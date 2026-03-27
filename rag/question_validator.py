"""
rag/question_validator.py
--------------------------
Post-extraction quality assurance for exam MCQs.

The PDFs being extracted are REAL government exam papers downloaded from
official / coaching sources.  OCR + LLM extraction can introduce errors:
  - wrong answer key
  - jumbled / missing options
  - incorrect year / exam_type
  - garbled question text (OCR artefacts)

This module cross-checks every extracted question against the web and
FIXES any errors it finds, so students get correct data to study from.

Pipeline
--------
  1. Serper API   → search Google for the exact question + answer key
  2. Firecrawl API → scrape the top matching page (trusted exam sites first)
  3. Gemini LLM    → compare extracted JSON vs scraped content → produce
                     corrected JSON with every wrong field fixed

Usage
-----
    from rag.question_validator import QuestionValidator
    validator = QuestionValidator()
    fixed_questions = validator.validate_batch(questions)
"""

import json
import re
import time
import os
import traceback
import requests
import google.generativeai as genai
from pathlib import Path

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── API endpoints ─────────────────────────────────────────────────────────────
SERPER_ENDPOINT    = "https://google.serper.dev/search"
FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v1/scrape"

# Rate-limit delays (seconds)
_SERPER_DELAY  = 1.0
_CRAWL_DELAY   = 2.0
_GEMINI_DELAY  = 1.5


# ── Exam metadata map cache ───────────────────────────────────────────────────

_EXAM_META_CACHE: list[dict] | None = None

def _load_exam_metadata_map() -> list[dict]:
    """Load and cache exam_metadata_map.json for exam_type validation."""
    global _EXAM_META_CACHE
    if _EXAM_META_CACHE is not None:
        return _EXAM_META_CACHE
    try:
        map_path = Path(__file__).resolve().parent.parent / "utils" / "exam_metadata_map.json"
        with open(map_path, "r", encoding="utf-8") as f:
            _EXAM_META_CACHE = json.load(f)
        logger.info(f"Validator loaded {len(_EXAM_META_CACHE)} entries from exam_metadata_map.json")
        return _EXAM_META_CACHE
    except Exception as e:
        logger.error(f"Failed to load exam_metadata_map.json: {e}")
        _EXAM_META_CACHE = []
        return []


def _get_exam_types_summary() -> str:
    """Build a compact summary of all exam types for LLM prompt context."""
    meta = _load_exam_metadata_map()
    if not meta:
        return "(exam metadata map not available)"
    
    # Deduplicate: collect unique (Exam Type, Department) pairs
    seen = set()
    lines = []
    for entry in meta:
        et = entry.get("Exam Type", "")
        dept = entry.get("Department", "")
        key = f"{et}|{dept}"
        if key not in seen:
            seen.add(key)
            lines.append(f"- {et} → {dept} (level: {entry.get('level','')}, elig: {entry.get('Eligibility','')})")
    # Limit to 120 lines to avoid overwhelming context
    if len(lines) > 120:
        lines = lines[:120] + [f"... and {len(lines)-120} more entries"]
    return "\n".join(lines)


def _generate_object_id() -> str:
    """Generate a unique 24-char hex string mimicking MongoDB ObjectId."""
    timestamp = int(time.time())
    raw = timestamp.to_bytes(4, 'big') + os.urandom(8)
    return raw.hex()

# Trusted exam portals — results from these are preferred
_TRUSTED_DOMAINS = [
    # Official
    "upsc.gov.in", "ssc.nic.in", "ibps.in", "rrbcdg.gov.in",
    "nta.ac.in", "jeemain.nta.nic.in", "neet.nta.nic.in",
    # Top coaching / answer-key sites
    "testbook.com", "adda247.com", "oliveboard.in",
    "gradeup.co", "byjus.com", "unacademy.com",
    "collegedunia.com", "embibe.com", "selfstudys.com",
    "cracku.in", "careerlauncher.com", "safalta.com",
    "examveda.com", "indiabix.com", "gktoday.in",
    "jagranjosh.com", "sarkarresult.com", "sarkariexam.com",
    "wifistudy.com", "studyiq.com", "toppr.com", "vedantu.com",
    "learncbse.in", "doubtnut.com", "allen.ac.in",
    "physicswallah.live", "mathongo.com", "jeeneetprep.com",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_search_query(q: dict) -> str:
    """
    Build an optimised Google query to find this exact question
    on an answer-key / coaching site.
    """
    question_text = q.get("question") or q.get("question_text", "")
    # Strip LaTeX markers
    question_text = re.sub(r'\$+', '', question_text)
    # If passage-based, take only the actual question (after last double newline)
    parts = question_text.split("\n\n")
    if len(parts) > 1:
        question_text = parts[-1]
    # Clean and truncate
    question_text = re.sub(r'\s+', ' ', question_text).strip()[:180]

    exam  = q.get("exam_type", "") or ""
    year  = q.get("year", "") or ""
    subj  = q.get("subject", "") or ""

    terms = []
    if exam:
        terms.append(exam)
    if year:
        terms.append(str(year))
    if subj:
        terms.append(subj)
    terms.append(f'"{question_text[:120]}"')   # exact match for core text
    terms.append("answer key OR solution")

    return " ".join(terms)


def _build_fallback_query(q: dict) -> str:
    """Shorter, broader query if the first search returned nothing."""
    question_text = q.get("question") or q.get("question_text", "")
    question_text = re.sub(r'\$+', '', question_text)
    parts = question_text.split("\n\n")
    if len(parts) > 1:
        question_text = parts[-1]
    question_text = re.sub(r'\s+', ' ', question_text).strip()[:100]

    return f'{question_text} correct answer'


class QuestionValidator:
    """
    Cross-checks extracted questions against the web and FIXES errors.
    Focus: data-quality for students preparing for government exams.
    """

    def __init__(self):
        self.serper_key    = Config.SERPER_API
        self.firecrawl_key = Config.FIRECRAWL_API

        if not self.serper_key:
            raise ValueError("SERPER_API key is missing from .env")
        if not self.firecrawl_key:
            raise ValueError("FIRECRAWL_API key is missing from .env")

        # Gemini for cross-checking
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.GENERATION_MODEL)
        else:
            self.model = None

    # ══════════════════════════════════════════════════════════════════════
    #  STEP 1 — Serper web search
    # ══════════════════════════════════════════════════════════════════════

    def _search_serper(self, query: str, num_results: int = 8) -> list[dict]:
        """Search Google via Serper API. Returns [{title, link, snippet}, …]."""
        try:
            resp = requests.post(
                SERPER_ENDPOINT,
                json={"q": query, "num": num_results, "gl": "in", "hl": "en"},
                headers={
                    "X-API-KEY": self.serper_key,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            results = [
                {
                    "title":   item.get("title", ""),
                    "link":    item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
                for item in data.get("organic", [])
            ]
            logger.info(f"Serper: {len(results)} results for: {query[:80]}…")
            return results

        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []

    def _pick_best_urls(self, results: list[dict], max_urls: int = 2) -> list[str]:
        """
        Pick up to `max_urls` best URLs from search results.
        Trusted domains come first; then first remaining result.
        """
        if not results:
            return []

        picked: list[str] = []
        seen: set[str] = set()

        # Pass 1: trusted domains
        for r in results:
            link = r.get("link", "")
            if link in seen:
                continue
            for domain in _TRUSTED_DOMAINS:
                if domain in link:
                    picked.append(link)
                    seen.add(link)
                    break
            if len(picked) >= max_urls:
                break

        # Pass 2: fill remaining slots
        for r in results:
            if len(picked) >= max_urls:
                break
            link = r.get("link", "")
            if link and link not in seen:
                picked.append(link)
                seen.add(link)

        return picked

    # ══════════════════════════════════════════════════════════════════════
    #  STEP 2 — Firecrawl web scraping
    # ══════════════════════════════════════════════════════════════════════

    def _scrape_firecrawl(self, url: str) -> str:
        """Scrape a URL via Firecrawl. Returns markdown text."""
        try:
            resp = requests.post(
                FIRECRAWL_ENDPOINT,
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                    "timeout": 30000,
                },
                headers={
                    "Authorization": f"Bearer {self.firecrawl_key}",
                    "Content-Type": "application/json",
                },
                timeout=45,
            )
            resp.raise_for_status()
            data = resp.json()

            content = ""
            if data.get("success") and data.get("data"):
                content = (
                    data["data"].get("markdown", "")
                    or data["data"].get("content", "")
                )

            # Truncate to fit LLM context
            if len(content) > 10_000:
                content = content[:10_000] + "\n\n[…truncated…]"

            logger.info(f"Firecrawl: {len(content)} chars from {url}")
            return content

        except Exception as e:
            logger.error(f"Firecrawl failed for {url}: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════════════
    #  STEP 3 — Gemini LLM cross-check & correction
    # ══════════════════════════════════════════════════════════════════════

    def _llm_cross_check(
        self,
        question: dict,
        web_content: str,
        source_url: str,
    ) -> dict:
        """
        Use Gemini to compare extracted question vs web source.
        The LLM is instructed to FIX every wrong field and return
        the corrected values.
        """
        if not self.model or not web_content:
            return {
                "status": "unverified",
                "corrections": {},
                "notes": "No web content available for cross-check.",
            }

        question_json = json.dumps(question, indent=2, ensure_ascii=False)

        prompt = f"""You are an expert exam-data quality engineer. Students will study from this data to prepare for government exams, so EVERY FIELD MUST BE CORRECT.

EXTRACTED QUESTION (from OCR + LLM — may contain errors):
{question_json}

WEB SOURCE (scraped from {source_url}):
{web_content[:8000]}

YOUR JOB — compare the extracted question against the web source and FIX every error:

KNOWN VALID EXAM TYPES (from our exam_metadata_map.json):
{_get_exam_types_summary()}

CHECK-LIST:
1. ANSWER — Does the web source confirm the correct answer?
   • If the extracted answer is WRONG, provide the correct answer.
   • This is the MOST IMPORTANT check — a wrong answer key ruins student preparation.
2. OPTIONS — Are options A/B/C/D exactly matching?
   • Fix any OCR-garbled option text.
   • CRITICAL: If any option is missing or poorly extracted, search the web source for the options and CORRECT them.
   • Compare the extracted question, answer, and options with the web source. If the web source has a DIFFERENT correct question text, answer, or options, REPLACE the extracted ones with the web source's data.
3. QUESTION TEXT — Is the question text accurate?
   • Fix OCR artefacts (garbled words, merged text, wrong symbols).
   • Do NOT rephrase; only fix extraction errors.
4. YEAR — Does the web source confirm which year this question appeared? (Report this in `notes` but do NOT change the extracted year).
5. EXPLANATION — If the web source has a better explanation, provide it.

RESPONSE (strict JSON — NO markdown fences, NO extra text):
{{
  "status": "verified | corrected | unverified",
  "is_real_exam_question": true/false,
  "answer_verified": true/false,
  "answer_from_source": "the correct answer letter or value from web source (e.g. 'B' or the answer text)",
  "corrections": {{
    // Include ONLY fields that need fixing. Examples:
    // "answer": "C",
    // "question": "fixed question text",
    // "option": {{"A": "fixed A", "C": "fixed C"}},
    // "explanation": "better explanation from web"
    // Leave as empty object {{}} if everything is already correct
  }},
  "notes": "Provide a verification summary. Explain exactly which source was used to verify. If not verified, explain why (e.g., 'question not found in web', 'found in web but options do not match', etc.). Specify if this confirms the question is a real government exam question and which year."
}}

RULES:
- If the extracted data is already correct → status = "verified", corrections = {{}}
- If you fixed anything → status = "corrected", corrections = {{...the fixed fields...}}
- If you cannot determine from the web content → status = "unverified"
- NEVER guess — only correct if the web source clearly provides the right data
- The "answer_from_source" field should ALWAYS contain the answer you found in the web content (even if same as extracted)

Return ONLY the JSON object."""

        try:
            response = self.model.generate_content(prompt)
            if not response.candidates:
                return {
                    "status": "unverified",
                    "corrections": {},
                    "notes": "Gemini returned no response.",
                }

            raw = response.candidates[0].content.parts[0].text
            # Strip markdown fences
            raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE | re.IGNORECASE)
            raw = re.sub(r',?\s*```\s*$', '', raw, flags=re.MULTILINE)
            raw = raw.strip()

            result = json.loads(raw, strict=False)
            return {
                "status":               result.get("status", "unverified"),
                "is_real_exam_question": result.get("is_real_exam_question", False),
                "answer_verified":       result.get("answer_verified", False),
                "answer_from_source":    result.get("answer_from_source", ""),
                "corrections":           result.get("corrections", {}),
                "notes":                 result.get("notes", ""),
            }

        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            return {"status": "unverified", "corrections": {}, "notes": f"LLM JSON parse error: {e}"}
        except Exception as e:
            logger.error(f"LLM cross-check failed: {e}")
            return {"status": "unverified", "corrections": {}, "notes": f"LLM error: {str(e)[:120]}"}

    # ══════════════════════════════════════════════════════════════════════
    #  MAIN — validate + fix a single question
    # ══════════════════════════════════════════════════════════════════════

    def validate_question(self, question: dict) -> dict:
        """
        Full pipeline for one question:
          search → pick best pages → scrape → LLM cross-check → apply fixes.
        Returns the question dict with corrections applied and validation metadata.
        """
        q = dict(question)   # work on a copy

        # ── Web Search ────────────────────────────────────────────────
        search_query = _build_search_query(q)
        time.sleep(_SERPER_DELAY)
        search_results = self._search_serper(search_query)

        # Fallback: broader query if exact match returned nothing
        if not search_results:
            fallback_query = _build_fallback_query(q)
            time.sleep(_SERPER_DELAY)
            search_results = self._search_serper(fallback_query)

        if not search_results:
            q["validation_status"]  = "unverified"
            q["validation_source"]  = None
            q["validation_notes"]   = "No web results found for this question."
            q["search_results"]     = []
            q["is_real_exam_question"] = False
            q["answer_verified"]    = False
            return q

        # Save top results for transparency
        q["search_results"] = [
            {"title": r["title"], "link": r["link"], "snippet": r["snippet"]}
            for r in search_results[:3]
        ]

        # ── Pick best URLs & scrape ────────────────────────────────────
        best_urls = self._pick_best_urls(search_results, max_urls=2)
        scraped_content = ""
        used_url = best_urls[0] if best_urls else ""

        for url in best_urls:
            time.sleep(_CRAWL_DELAY)
            content = self._scrape_firecrawl(url)
            if content and len(content) > 200:
                scraped_content = content
                used_url = url
                break

        # If all scraping failed, fall back to search snippets
        if not scraped_content:
            snippet_text = "\n".join(
                f"Source: {r['title']} ({r['link']})\n{r['snippet']}"
                for r in search_results[:5]
            )
            if snippet_text:
                scraped_content = snippet_text
                used_url = best_urls[0] if best_urls else search_results[0].get("link", "")

        # ── LLM cross-check ───────────────────────────────────────────
        if scraped_content:
            time.sleep(_GEMINI_DELAY)
            validation = self._llm_cross_check(q, scraped_content, used_url)
        else:
            validation = {
                "status": "unverified",
                "corrections": {},
                "notes": "Could not scrape any source page.",
            }

        # ── Apply corrections ─────────────────────────────────────────
        corrections = validation.get("corrections", {})
        fields_fixed = []

        if corrections:
            for field, new_value in corrections.items():
                if not new_value:     # skip null / empty corrections
                    continue
                if field == "option" and isinstance(new_value, dict):
                    existing = q.get("option", {})
                    if isinstance(existing, dict):
                        for opt_key, opt_val in new_value.items():
                            if opt_val and opt_val != existing.get(opt_key):
                                existing[opt_key] = opt_val
                                fields_fixed.append(f"option.{opt_key}")
                        q["option"] = existing
                elif field in ("answer", "question", "explanation", "subject", "topic",
                               "subtopic", "difficulty", "level", "eligibility"):
                    old_val = q.get(field)
                    if str(new_value).strip() and new_value != old_val:
                        q[field] = new_value
                        fields_fixed.append(field)

        # ── Write validation metadata ─────────────────────────────────
        q["validation_status"]     = validation.get("status", "unverified")
        q["validation_source"]     = used_url
        q["validation_notes"]      = validation.get("notes", "")
        q["is_real_exam_question"] = validation.get("is_real_exam_question", False)
        q["answer_verified"]       = validation.get("answer_verified", False)
        q["answer_from_source"]    = validation.get("answer_from_source", "")

        if fields_fixed:
            q["fields_corrected"] = fields_fixed
            q["validation_notes"] = (
                q.get("validation_notes", "")
                + f" | Fixed: {', '.join(fields_fixed)}"
            )
            logger.info(f"  ✔ Corrected fields: {fields_fixed}")

        # Ensure MongoDB _id
        if "_id" not in q:
            q["_id"] = {"$oid": _generate_object_id()}

        return q

    # ══════════════════════════════════════════════════════════════════════
    #  BATCH — validate a full extraction batch
    # ══════════════════════════════════════════════════════════════════════

    def validate_batch(
        self,
        questions: list[dict],
        progress_callback=None,
    ) -> list[dict]:
        """
        Validate + fix a list of extracted questions.

        Parameters
        ----------
        questions : list[dict]
            Extracted MCQ dicts.
        progress_callback : callable, optional
            Called with (current_index, total, validated_question) after each.

        Returns
        -------
        list[dict]
            Questions with corrections applied and validation metadata.
        """
        total     = len(questions)
        validated = []

        for i, q in enumerate(questions):
            try:
                logger.info(f"Validating question {i+1}/{total}…")
                result = self.validate_question(q)
                validated.append(result)

                if progress_callback:
                    progress_callback(i, total, result)

            except Exception as e:
                logger.error(f"Validation failed for Q{i+1}: {e}\n{traceback.format_exc()}")
                q_copy = dict(q)
                q_copy["validation_status"]  = "error"
                q_copy["validation_source"]  = None
                q_copy["validation_notes"]   = f"Error: {str(e)[:200]}"
                q_copy["is_real_exam_question"] = False
                q_copy["answer_verified"]    = False
                validated.append(q_copy)

        # ── Summary ──────────────────────────────────────────────────
        n_verified   = sum(1 for q in validated if q.get("validation_status") == "verified")
        n_corrected  = sum(1 for q in validated if q.get("validation_status") == "corrected")
        n_unverified = sum(1 for q in validated if q.get("validation_status") == "unverified")
        n_errors     = sum(1 for q in validated if q.get("validation_status") == "error")

        total_fixes  = sum(
            len(q.get("fields_corrected", [])) for q in validated
        )

        logger.info(
            f"=== Validation done: {n_verified} verified, {n_corrected} corrected "
            f"({total_fixes} fields fixed), {n_unverified} unverified, "
            f"{n_errors} errors — out of {total} questions ==="
        )

        return validated
