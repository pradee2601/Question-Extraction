"""
rag/exam_extractor.py
---------------------
Extracts MCQs from exam PDFs.

Two paper types supported
--------------------------
  simple  : flat list of standalone MCQs (UPSC GS, NEET, JEE, NDA ...)
  passage : reading-comprehension paper with passages + questions
            (UPSC CSAT, CLAT, ...)
            Passage text is embedded directly into each question's "question"
            field so that every question is a self-contained flat MCQ.

Pipeline (scanned PDFs)
-----------------------
  Scanned page -> PyMuPDF pixmap -> Tesseract OCR -> plain text ->
  Gemini (text-only) -> JSON

Output JSON schema matches the target MongoDB format:
  exam_type, department, subject, topic, subtopic, difficulty,
  question (with LaTeX formulas), option, answer, explanation,
  level, eligibility, year, pdf_name

Return value of extract_from_pdf()
------------------------------------
  {
    "type": "simple",
    "data": list[dict]   # always a flat MCQ list; passage text embedded in question field
  }
"""

import google.generativeai as genai
import fitz          # PyMuPDF
from PIL import Image
import pytesseract
import io
import json
import re
import os
import gc
import hashlib
import time as _time
from pathlib import Path

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# -- configure Tesseract -------------------------------------------------------
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD_PATH

# -- tuneable constants --------------------------------------------------------
OCR_DPI         = 250      # higher DPI -> better accuracy for old scans
MAX_TEXT_CHARS  = 60_000   # max chars per Gemini call (increased)
PAGES_PER_CHUNK = 1        # process 1 page at a time to prevent LLM laziness/truncation

# Keywords that indicate a reading-comprehension / passage-based paper
_PASSAGE_KEYWORDS = [
    "passage", "comprehension", "read the following", "based on the passage",
    "refer to the passage", "text given below", "following passage",
    "csat", "paper-ii", "paper ii",
]

# Field name mapping: old format -> new format
_FIELD_MAP = {
    "Exam Type":    "exam_type",
    "Department":   "department",
    "Subject":      "subject",
    "Topic":        "topic",
    "Subtopic":     "subtopic",
    "Explanation":  "explanation",
    "Eligibility":  "eligibility",
    "pdf name":     "pdf_name",
    "correct_answer": "answer",
    "question_text": "question",
}

# ---------- Invalid / placeholder values that must NEVER survive into output ---
_INVALID_VALUES = {
    "unknown", "not specified", "not available", "n/a", "na", "none",
    "null", "unspecified", "undefined", "tbd", "-", "--", "?", "",
    "not mentioned", "not found", "not given", "not provided",
}

def _is_invalid(value) -> bool:
    """Return True if value is None, empty, or a known placeholder string."""
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return value.strip().lower() in _INVALID_VALUES


def _extract_year_from_filename(pdf_name: str) -> str | None:
    """Try to extract a valid 4-digit year (1990-2030) from the PDF filename."""
    if not pdf_name:
        return None
    # Find all 4-digit numbers
    years = re.findall(r'\b(19[9]\d|20[0-3]\d)\b', pdf_name)
    if years:
        # Return the most plausible (usually the last year in the name)
        return years[-1]
    # Try patterns like "20-21" -> "2021", "19-20" -> "2020"
    short_years = re.findall(r'\b(\d{2})[-/](\d{2})\b', pdf_name)
    for y1, y2 in short_years:
        full = f"20{y2}" if int(y2) < 50 else f"19{y2}"
        if 1990 <= int(full) <= 2030:
            return full
    return None


# Keyword -> (exam_type, department, level, eligibility) for filename-based inference
_FILENAME_EXAM_MAP = [
    # Specific exams first (order matters - more specific first)
    (["jee", "advanced"],       ("JEE Advanced", "NTA", "National", "12th")),
    (["jee", "main"],           ("JEE Main", "NTA", "National", "12th")),
    (["neet", "pg"],            ("NEET PG", "NTA", "National", "MBBS/Medical")),
    (["neet", "ug"],            ("NEET UG", "NTA", "National", "12th")),
    (["neet"],                  ("NEET UG", "NTA", "National", "12th")),
    (["csat"],                  ("Civil Services Examination (CSE) - CSAT", "UPSC", "National", "Graduate")),
    (["upsc", "prelim"],        ("Civil Services Examination (CSE)", "UPSC", "National", "Graduate")),
    (["upsc", "main"],          ("Civil Services Examination (CSE)", "UPSC", "National", "Graduate")),
    (["upsc"],                  ("Civil Services Examination (CSE)", "UPSC", "National", "Graduate")),
    (["nda"],                   ("National Defence Academy (NDA) & NA", "UPSC", "National", "12th")),
    (["cds"],                   ("Combined Defence Services (CDS)", "UPSC", "National", "Graduate/12th")),
    (["afcat"],                 ("AFCAT", "Indian Air Force", "National", "Graduate/12th")),
    (["ssc", "cgl"],            ("SSC Combined Graduate Level (CGL)", "SSC", "National", "Graduate")),
    (["ssc", "chsl"],           ("SSC Combined Higher Secondary Level (CHSL)", "SSC", "National", "12th")),
    (["ssc", "mts"],            ("SSC Multi Tasking Staff (MTS)", "SSC", "National", "10th")),
    (["ssc", "gd"],             ("SSC GD Constable", "SSC", "National", "10th")),
    (["ssc", "cpo"],            ("SSC CPO (SI)", "SSC", "National", "Graduate")),
    (["ssc", "je"],             ("SSC Junior Engineer (JE)", "SSC", "National", "Diploma/Engineering")),
    (["ssc"],                   ("SSC", "SSC", "National", "Graduate")),
    (["ibps", "po"],            ("IBPS PO", "IBPS", "National", "Graduate")),
    (["ibps", "clerk"],         ("IBPS Clerk", "IBPS", "National", "Graduate")),
    (["ibps", "rrb"],           ("IBPS RRB Officer Scale I (PO)", "IBPS", "National", "Graduate")),
    (["ibps", "so"],            ("IBPS Specialist Officer (SO)", "IBPS", "National", "Graduate")),
    (["ibps"],                  ("IBPS", "IBPS", "National", "Graduate")),
    (["sbi", "po"],             ("SBI PO", "SBI", "National", "Graduate")),
    (["sbi", "clerk"],          ("SBI Clerk", "SBI", "National", "Graduate")),
    (["sbi"],                   ("SBI", "SBI", "National", "Graduate")),
    (["rbi", "grade"],          ("RBI Grade B", "RBI", "National", "Graduate")),
    (["rbi", "assistant"],      ("RBI Assistant", "RBI", "National", "Graduate")),
    (["rbi"],                   ("RBI", "RBI", "National", "Graduate")),
    (["rrb", "ntpc"],           ("RRB NTPC", "RRB", "National", "12th/Graduate")),
    (["rrb", "je"],             ("RRB JE", "RRB", "National", "Diploma/Engineering")),
    (["rrb", "group", "d"],     ("RRB Group D", "RRB", "National", "10th")),
    (["rrb", "alp"],            ("RRB ALP", "RRB", "National", "12th/Diploma")),
    (["rrb"],                   ("RRB", "RRB", "National", "12th/Graduate")),
    (["rpf"],                   ("RPF", "RPF", "National", "10th/12th")),
    (["railway"],               ("Railway", "RRB", "National", "12th/Graduate")),
    (["lic"],                   ("LIC AAO", "LIC", "National", "Graduate")),
    (["nabard"],                ("NABARD Grade A", "NABARD", "National", "Graduate")),
    (["ctet"],                  ("CTET", "CBSE", "National", "Graduate/12th")),
    (["ugc", "net"],            ("UGC NET", "UGC / NTA", "National", "Postgraduate")),
    (["kvs"],                   ("KVS Recruitment PRT/TGT/PGT", "KVS", "National", "Graduate/B.Ed")),
    (["ongc"],                  ("ONGC Graduate Trainee", "ONGC", "National", "Engineering/Graduate")),
    (["isro"],                  ("ISRO Scientist", "ISRO", "National", "Engineering/Science")),
    (["drdo"],                  ("DRDO Scientist", "DRDO", "National", "Engineering/Science")),
    (["bsf"],                   ("BSF Recruitment", "BSF", "National", "10th/12th/Graduate")),
    (["crpf"],                  ("CRPF Recruitment", "CRPF", "National", "10th/12th/Graduate")),
    (["cisf"],                  ("CISF Recruitment", "CISF", "National", "10th/12th/Graduate")),
    (["psc"],                   ("State PSC", "State PSC", "State", "Graduate")),
]

def _infer_metadata_from_filename(pdf_name: str) -> dict:
    """Infer exam metadata (exam_type, department, level, eligibility) from PDF filename."""
    if not pdf_name:
        return {}
    lower = pdf_name.lower()
    for keywords, (exam_type, department, level, eligibility) in _FILENAME_EXAM_MAP:
        if all(kw in lower for kw in keywords):
            return {
                "exam_type": exam_type,
                "department": department,
                "level": level,
                "eligibility": eligibility,
            }
    return {}


def _sanitize_question(q: dict, pdf_name: str) -> dict:
    """
    Post-process a single question dict to replace all invalid/placeholder
    values with proper inferred values from the PDF filename.
    """
    inferred = _infer_metadata_from_filename(pdf_name)
    year_from_file = _extract_year_from_filename(pdf_name)

    # --- Fix year field ---
    year_val = q.get("year")
    if _is_invalid(year_val):
        if year_from_file:
            q["year"] = year_from_file
        else:
            q["year"] = None   # JSON null — not the string "null"
    elif isinstance(year_val, str):
        # Clean up year if it has extra text like "2019 (approx)" -> "2019"
        year_match = re.search(r'\b(19[9]\d|20[0-3]\d)\b', year_val)
        if year_match:
            q["year"] = year_match.group(1)
        elif year_from_file:
            q["year"] = year_from_file
        else:
            q["year"] = None

    # --- Fix exam_type ---
    if _is_invalid(q.get("exam_type")) and inferred.get("exam_type"):
        q["exam_type"] = inferred["exam_type"]

    # --- Fix department ---
    if _is_invalid(q.get("department")) and inferred.get("department"):
        q["department"] = inferred["department"]

    # --- Fix level ---
    if _is_invalid(q.get("level")) and inferred.get("level"):
        q["level"] = inferred["level"]

    # --- Fix eligibility ---
    if _is_invalid(q.get("eligibility")) and inferred.get("eligibility"):
        q["eligibility"] = inferred["eligibility"]

    # --- Fix difficulty ---
    diff = q.get("difficulty")
    if _is_invalid(diff) or (isinstance(diff, str) and diff.strip().lower() not in ("easy", "medium", "hard")):
        q["difficulty"] = "Medium"  # safe default

    # Ensure pdf_name is always set
    if _is_invalid(q.get("pdf_name")):
        q["pdf_name"] = pdf_name

    # --- Validate exam_type against metadata map ---
    q = _validate_exam_type(q)

    # --- Add MongoDB _id ---
    if "_id" not in q:
        q["_id"] = {"$oid": _generate_object_id()}

    return q


# ---------- MongoDB ObjectId generation ----------------------------------------

def _generate_object_id() -> str:
    """Generate a unique 24-char hex string mimicking MongoDB ObjectId."""
    timestamp = int(_time.time())
    # 4 bytes timestamp + 5 bytes random + 3 bytes counter
    raw = timestamp.to_bytes(4, 'big') + os.urandom(8)
    return raw.hex()


# ---------- Exam metadata map validation --------------------------------------

_EXAM_METADATA_CACHE: list[dict] | None = None

def _load_exam_metadata_map() -> list[dict]:
    """Load exam_metadata_map.json (cached after first load)."""
    global _EXAM_METADATA_CACHE
    if _EXAM_METADATA_CACHE is not None:
        return _EXAM_METADATA_CACHE
    try:
        map_path = Path(__file__).resolve().parent.parent / "utils" / "exam_metadata_map.json"
        with open(map_path, "r", encoding="utf-8") as f:
            _EXAM_METADATA_CACHE = json.load(f)
        logger.info(f"Loaded {len(_EXAM_METADATA_CACHE)} entries from exam_metadata_map.json")
        return _EXAM_METADATA_CACHE
    except Exception as e:
        logger.error(f"Failed to load exam_metadata_map.json: {e}")
        _EXAM_METADATA_CACHE = []
        return []


def _validate_exam_type(q: dict) -> dict:
    """
    Cross-check the question's exam_type and department against the
    exam_metadata_map.json and fix/fill level + eligibility if found.
    """
    metadata = _load_exam_metadata_map()
    if not metadata:
        return q

    exam_type = (q.get("exam_type") or "").strip().lower()
    department = (q.get("department") or "").strip().lower()

    if not exam_type and not department:
        return q

    best_match = None
    best_score = 0

    for entry in metadata:
        entry_exam = (entry.get("Exam Type") or "").strip().lower()
        entry_dept = (entry.get("Department") or "").strip().lower()

        score = 0
        # Check exam_type matches entry's Exam Type or Department
        if exam_type:
            if exam_type in entry_exam or entry_exam in exam_type:
                score += 3
            if exam_type in entry_dept or entry_dept in exam_type:
                score += 5  # Department match is more specific

        # Check department matches
        if department:
            if department in entry_exam or entry_exam in department:
                score += 2
            if department in entry_dept or entry_dept in department:
                score += 4

        if score > best_score:
            best_score = score
            best_match = entry

    if best_match and best_score >= 3:
        # Fill level and eligibility from the map
        map_level = best_match.get("level")
        map_elig = best_match.get("Eligibility")

        if map_level and _is_invalid(q.get("level")):
            q["level"] = map_level
        if map_elig and _is_invalid(q.get("eligibility")):
            q["eligibility"] = map_elig

        logger.debug(
            f"Exam metadata matched: '{q.get('exam_type')}' → "
            f"map entry '{best_match.get('Department')}' (score={best_score})"
        )

    return q


def _normalize_fields(q: dict) -> dict:
    """Normalize field names from old/mixed format to the target lowercase format."""
    normalized = {}
    for key, value in q.items():
        new_key = _FIELD_MAP.get(key, key)
        normalized[new_key] = value

    # Ensure 'option' key exists (some responses may use 'options')
    if "options" in normalized and "option" not in normalized:
        normalized["option"] = normalized.pop("options")

    return normalized


class ExamExtractor:
    """
    Extracts and optionally refines questions directly from an uploaded exam PDF.

    Modes
    -----
    extract : Preserve original wording; only fill missing answers/explanations.
    refine  : Improve grammar/clarity while keeping meaning and correct answer.

    Output includes LaTeX formatting for all mathematical formulas, chemical
    equations, and scientific notation.
    """

    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing.")

        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        import google.generativeai.types as genai_types
        self.generation_config = genai_types.GenerationConfig(max_output_tokens=8192)
        self.model = genai.GenerativeModel(
            Config.GENERATION_MODEL,
            safety_settings=self.safety_settings,
            generation_config=self.generation_config,
        )

        prompts_dir = os.path.join(Config.BASE_DIR, "prompts")

        # Standard standalone-MCQ prompt
        mcq_path = os.path.join(prompts_dir, "exam_extraction_prompt.txt")
        try:
            with open(mcq_path, "r", encoding="utf-8") as f:
                self.mcq_prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"MCQ extraction prompt not found at {mcq_path}")
            raise

        # Passage-based comprehension prompt
        passage_path = os.path.join(prompts_dir, "passage_extraction_prompt.txt")
        try:
            with open(passage_path, "r", encoding="utf-8") as f:
                self.passage_prompt_template = f.read()
        except FileNotFoundError:
            logger.warning(
                f"Passage prompt not found at {passage_path}. Using MCQ prompt as fallback."
            )
            self.passage_prompt_template = self.mcq_prompt_template

        # Exam metadata mapping table
        mapping_path = os.path.join(prompts_dir, "exam_mapping_table.txt")
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.exam_mapping_text = f.read()
        except FileNotFoundError:
            logger.warning(f"Exam mapping table not found at {mapping_path}. Metadata mapping will be empty.")
            self.exam_mapping_text = ""

        # Backward-compat alias
        self.prompt_template = self.mcq_prompt_template

    # ------------------------------------------------------------------
    # Step 1 - PDF -> per-page OCR text
    # ------------------------------------------------------------------

    def _has_embedded_images(self, page) -> bool:
        """Return True if the PDF page contains any embedded image objects."""
        try:
            return len(page.get_images(full=True)) > 0
        except Exception:
            return False

    def _is_real_content(self, text: str) -> bool:
        """
        Return True if text looks like actual exam content.
        Relaxed to allow all types of questions, not just MCQs.
        """
        # If it has a decent amount of text, or question marks, treat it as content.
        if len(text) > 100 or "?" in text:
            return True
        return False

    def _ocr_page(self, page) -> str:
        """Render page as image and OCR it with Tesseract (English only)."""
        try:
            pix = page.get_pixmap(dpi=OCR_DPI)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_config = r"--oem 3 --psm 6 -l eng"
            text = pytesseract.image_to_string(img, config=ocr_config)
            # Free memory immediately
            del img
            del pix
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR failed for page: {e}")
            return ""

    def _extract_pages_text(self, raw_bytes: bytes) -> list[dict]:
        """
        Extract per-page text. For pages with embedded images or thin native
        text, run Tesseract OCR.
        Returns list of {"page": int, "text": str, "source": str}.
        """
        pages = []
        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            total = len(doc)
            logger.info(f"PDF opened: {total} page(s)")

            for i in range(total):
                page        = doc.load_page(i)
                native_text = page.get_text("text").strip()
                has_images  = self._has_embedded_images(page)

                if self._is_real_content(native_text) and not has_images:
                    text, source = native_text, "native"
                else:
                    ocr_text = self._ocr_page(page)
                    if has_images and not ocr_text and native_text:
                        text, source = native_text, "native-fallback"
                    elif ocr_text and len(ocr_text) > len(native_text):
                        text, source = ocr_text, "ocr"
                    elif native_text:
                        text, source = native_text, "native"
                    else:
                        text, source = ocr_text, "ocr"

                if text and len(text.strip()) > 10:
                    pages.append({"page": i + 1, "text": text, "source": source})
                    logger.info(
                        f"  Page {i+1}/{total} [{source}|imgs={has_images}]: {len(text)} chars"
                    )
                else:
                    logger.warning(f"  Page {i+1}/{total}: no usable text")

            doc.close()
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise
        return pages

    # ------------------------------------------------------------------
    # Step 2 - Detect paper type
    # ------------------------------------------------------------------

    def _is_passage_based(self, pages: list[dict]) -> bool:
        """
        Return True if the OCR text strongly suggests a passage-based paper.
        Checks the first ~8 pages for passage keywords.
        """
        sample = " ".join(p["text"].lower() for p in pages[:8])
        for kw in _PASSAGE_KEYWORDS:
            if kw in sample:
                logger.info(f"Passage-based paper detected (keyword: '{kw}')")
                return True
        return False

    # ------------------------------------------------------------------
    # Step 3 - Gemini calls
    # ------------------------------------------------------------------

    def _build_prompt(self, mode: str, text_block: str, passage_mode: bool, pdf_name: str) -> str:
        """Fill prompt template placeholders."""
        template = self.passage_prompt_template if passage_mode else self.mcq_prompt_template
        if len(text_block) > MAX_TEXT_CHARS:
            text_block = (
                text_block[:MAX_TEXT_CHARS]
                + "\n\n[... content truncated - process questions found so far ...]"
            )
        prompt = template.replace("{mode}", mode)
        prompt = prompt.replace("{pdf_name}", pdf_name)
        prompt = prompt.replace("{exam_mapping}", self.exam_mapping_text)
        return prompt.replace("{pdf_text}", text_block)

    def _raw_gemini_call(self, prompt: str, label: str) -> str:
        """Call Gemini and return raw text. Handles finish_reason=4 gracefully with exponential backoff for rate limits."""
        import time
        max_retries = 5
        base_delay = 10

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if not response.candidates:
                    logger.warning(f"[{label}] No candidates returned.")
                    return ""
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, "finish_reason", None)
                if finish_reason == 4:
                    logger.warning(f"[{label}] RECITATION block - retrying with rephrased prompt ...")
                    return self._rephrased_call(prompt, label)
                if finish_reason == 2: # MAX_TOKENS
                    logger.warning(f"[{label}] Exceeded max output tokens.")
                if not candidate.content or not candidate.content.parts:
                    logger.warning(f"[{label}] Empty content parts.")
                    return ""
                return "".join(
                    part.text for part in candidate.content.parts if hasattr(part, "text")
                )
            except Exception as e:
                err = str(e)
                if "finish_reason" in err and "4" in err:
                    logger.warning(f"[{label}] RECITATION exception - retrying rephrased ...")
                    return self._rephrased_call(prompt, label)
                if "429" in err or "quota" in err.lower() or "too many requests" in err.lower() or "ResourceExhausted" in err:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"[{label}] Rate limit/Quota. Retrying in {delay}s ({attempt+1}/{max_retries})...")
                        time.sleep(delay)
                        continue
                logger.error(f"[{label}] Gemini call failed: {e}")
                return ""
        return ""

    def _rephrased_call(self, original_prompt: str, label: str) -> str:
        """Retry with line-labelled content to avoid recitation detection."""
        # Extract the pdf_text section from the prompt
        parts = original_prompt.split("--- OCR TEXT TO PROCESS ---")
        if len(parts) < 2:
            parts = original_prompt.split("{pdf_text}")
        ocr_text = parts[-1].strip() if len(parts) > 1 else original_prompt

        labelled = "\n".join(
            f"[LINE {idx+1}] {line}"
            for idx, line in enumerate(ocr_text.splitlines())
            if line.strip()
        )
        rephrased = (
            "You are a data formatter. The following lines were captured by an "
            "OCR scanner from a printed exam paper. Parse them to extract all "
            "questions (including MCQs, Fill-in-the-blanks, Descriptive, etc.) "
            "and return valid JSON only. Use LaTeX notation ($...$) for any "
            "mathematical formulas, chemical equations, or scientific notation:\n\n"
            + labelled[:MAX_TEXT_CHARS]
        )
        try:
            resp = self.model.generate_content(rephrased)
            if not resp.candidates:
                return ""
            cand = resp.candidates[0]
            if not cand.content or not cand.content.parts:
                return ""
            return "".join(
                part.text for part in cand.content.parts if hasattr(part, "text")
            )
        except Exception as e:
            logger.error(f"[{label}] Rephrased call also failed: {e}")
            return ""

    def _call_gemini(
        self, mode: str, text_block: str, chunk_label: str, passage_mode: bool, pdf_name: str = "unknown.pdf"
    ) -> str:
        """Build prompt and call Gemini, returning raw text."""
        prompt = self._build_prompt(mode, text_block, passage_mode, pdf_name)
        logger.info(f"Gemini call [{chunk_label}]: {len(prompt):,} chars prompt")
        return self._raw_gemini_call(prompt, chunk_label)

    # ------------------------------------------------------------------
    # Step 4 - Parse response (both schemas)
    # ------------------------------------------------------------------

    def _clean_raw(self, raw: str) -> str:
        """Strip markdown fences and whitespace."""
        text = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r"^```\s*",     "", text, flags=re.MULTILINE)
        text = re.sub(r",?\s*```$",   "", text, flags=re.MULTILINE)
        return text.strip()

    def _fix_backslashes(self, text: str) -> str:
        """Fix backslashes that break JSON parsing.
        
        In JSON, these are the ONLY valid escape sequences:
          \\\"  \\\\  \\/  \\b  \\f  \\n  \\r  \\t  \\uXXXX
        
        But LaTeX commands like \\frac start with \\f (form feed),
        \\begin starts with \\b (backspace), \\nabla starts with \\n (newline).
        We must double-escape ALL backslashes, then un-double the ones that
        are clearly valid JSON escapes (followed by exactly the right pattern).
        
        Strategy: replace every \\ that is NOT a valid COMPLETE JSON escape.
        A valid JSON escape is \\ followed by exactly one of: \" \\\\ / b f n r t
        OR \\ followed by u and 4 hex digits.
        But \\b alone (backspace) vs \\begin (LaTeX) — if followed by more
        letters, it's LaTeX, not JSON backspace.
        """
        # Match backslash followed by anything.
        # We keep it only if it's a valid JSON escape that is NOT also a LaTeX command.
        # Valid terminal JSON escapes: \", \\, \/, and single-char \b \f \n \r \t
        # that are NOT followed by letters (which would make them LaTeX).
        # \uXXXX is valid if followed by exactly 4 hex digits.
        def _replacer(m: re.Match) -> str:
            after = m.group(1)
            # \\ \" \/ — always valid JSON
            if after in ('"', '\\', '/'):
                return m.group(0)
            # \uXXXX — unicode escape
            if after == 'u':
                # Check if followed by 4 hex digits in the original text
                pos = m.end()
                remaining = text[pos:pos+4]
                if re.fullmatch(r'[0-9a-fA-F]{4}', remaining):
                    return m.group(0)
            # \b \f \n \r \t — valid ONLY if NOT followed by a letter
            # (otherwise it's a LaTeX command like \frac, \beta, \nabla, etc.)
            if after in ('b', 'f', 'n', 'r', 't'):
                pos = m.end()
                if pos < len(text) and text[pos].isalpha():
                    # It's LaTeX (e.g. \frac, \begin, \nabla) — double-escape
                    return '\\\\' + after
                else:
                    # It's a genuine JSON escape (e.g. \n at end of line)
                    return m.group(0)
            # Everything else (\p, \s, \i, \l, \c, \a, \d, etc.) — double-escape
            return '\\\\' + after

        return re.sub(r'\\(.)', _replacer, text)

    def _salvage_objects(self, text: str) -> list[dict]:
        """Extract fully formed JSON objects from a truncated or messy string."""
        results = []
        depth = 0
        start = -1
        in_string = False
        escape = False
        for i, c in enumerate(text):
            if c == '"' and not escape:
                in_string = not in_string
            if in_string:
                escape = (c == '\\' and not escape)
                continue
            if c == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif c == '}':
                if depth > 0:
                    depth -= 1
                    if depth == 0:
                        try:
                            obj_str = self._fix_backslashes(text[start:i+1])
                            obj = json.loads(obj_str, strict=False)
                            if isinstance(obj, dict) and ("question" in obj or "question_text" in obj):
                                results.append(_normalize_fields(obj))
                        except Exception:
                            pass
        return results

    def _parse_response_simple(self, raw: str) -> list[dict]:
        """
        Parse a flat MCQ array response.
        Handles several Gemini response shapes:
          - Plain array:                [{ ... }, ...]
          - Object-wrapped:             { "questions": [...] }
          - Object with known key:      { "mcqs": [...] }
          - Single object (1 question): { "question": "..." }

        All results are normalized to lowercase field names.
        """
        if not raw:
            return []
        text = self._clean_raw(raw)

        # --- Try plain array first ---
        arr_start = text.find("[")
        arr_end   = text.rfind("]")
        obj_start = text.find("{")

        # If there's an object BEFORE the first array, it might be a wrapper
        if obj_start != -1 and (arr_start == -1 or obj_start < arr_start):
            # Try to parse the whole thing as an object
            obj_end = text.rfind("}")
            if obj_end != -1:
                try:
                    obj_text = self._fix_backslashes(text[obj_start:obj_end + 1])
                    data = json.loads(obj_text, strict=False)
                    if isinstance(data, dict):
                        # Check common wrapper keys
                        for key in ("questions", "mcqs", "items", "data", "results"):
                            if key in data and isinstance(data[key], list):
                                logger.info(f"Unwrapped '{key}' from object response.")
                                return [_normalize_fields(q) for q in data[key]]
                        # Object with no list values - treat as single MCQ
                        if "question" in data or "question_text" in data:
                            return [_normalize_fields(data)]
                except Exception:
                    pass  # fall through to array search

        # --- Plain array extraction ---
        if arr_start == -1 or arr_end == -1:
            logger.warning("No JSON array found in response.")
            # Last resort: log snippet for debugging
            logger.debug(f"Response snippet: {text[:300]}")
            return []
        text = self._fix_backslashes(text[arr_start:arr_end + 1])
        try:
            data = json.loads(text, strict=False)
            if isinstance(data, list):
                return [_normalize_fields(q) for q in data if isinstance(q, dict)]
            if isinstance(data, dict):
                return [_normalize_fields(data)]
        except json.JSONDecodeError as e:
            logger.warning(f"json.loads failed: {e} - trying ast fallback ...")
            try:
                import ast
                fb = text.replace("null","None").replace("true","True").replace("false","False")
                data = ast.literal_eval(fb)
                if isinstance(data, list):
                    return [_normalize_fields(q) for q in data if isinstance(q, dict)]
                if isinstance(data, dict):
                    return [_normalize_fields(data)]
            except Exception as fe:
                logger.error(f"ast fallback failed: {fe}")
                
        # --- Final Fallback: Salvage fully-formed JSON objects from truncated strings ---
        logger.info("Attempting to salvage fully completed JSON objects from truncated output...")
        salvaged = self._salvage_objects(text)
        if salvaged:
            logger.info(f"Successfully salvaged {len(salvaged)} question(s).")
            return salvaged
            
        return []

    def _parse_response_passage(self, raw: str) -> dict | None:
        """Parse a passage-based exam object response."""
        if not raw:
            return None
        text = self._clean_raw(raw)
        # Find outermost JSON object
        start = text.find("{")
        end   = text.rfind("}")
        if start == -1 or end == -1:
            logger.warning("No JSON object found in passage response.")
            return None
        text = self._fix_backslashes(text[start:end + 1])
        try:
            data = json.loads(text, strict=False)
            if isinstance(data, dict) and "questions" in data:
                return data
            logger.warning("Parsed JSON does not look like passage schema.")
        except json.JSONDecodeError as e:
            logger.warning(f"Passage JSON parse failed: {e}")
        return None

    # ------------------------------------------------------------------
    # Merge helpers for passage-based chunks
    # ------------------------------------------------------------------

    def _merge_passage_results(self, chunks: list[dict]) -> dict:
        """
        Merge multiple chunk results (for long passage PDFs) into one object.
        Deduplicates passages by passage_id and questions by question_number.
        """
        merged: dict = {
            "exam":            "",
            "date":            None,
            "total_questions": 0,
            "passages":        [],
            "questions":       [],
        }
        seen_passage_ids:  set[str] = set()
        seen_q_numbers:    set[int] = set()

        for chunk in chunks:
            if not merged["exam"] and chunk.get("exam"):
                merged["exam"] = chunk["exam"]
            if not merged["date"] and chunk.get("date"):
                merged["date"] = chunk["date"]
            if chunk.get("total_questions", 0) > merged["total_questions"]:
                merged["total_questions"] = chunk["total_questions"]

            for p in chunk.get("passages", []):
                pid = p.get("passage_id", "")
                if pid and pid not in seen_passage_ids:
                    merged["passages"].append(p)
                    seen_passage_ids.add(pid)

            for q in chunk.get("questions", []):
                qnum = q.get("question_number")
                if qnum is not None and qnum not in seen_q_numbers:
                    merged["questions"].append(q)
                    seen_q_numbers.add(qnum)
                elif qnum is None:
                    merged["questions"].append(q)   # no number - keep all

        # Sort questions by number
        merged["questions"].sort(key=lambda q: q.get("question_number") or 0)
        return merged

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def extract_from_pdf(self, file_stream, mode: str = "extract") -> dict:
        """
        Full pipeline: PDF -> OCR -> Gemini -> structured result.

        After processing, extracted page data is freed from memory to
        keep RAM usage low on slower machines.

        Returns
        -------
        {
          "type": "simple" | "passage",
          "data": list[dict] | dict
        }
        """
        if mode not in ("extract", "refine"):
            raise ValueError(f"Invalid mode '{mode}'. Choose 'extract' or 'refine'.")

        pdf_name = os.path.basename(getattr(file_stream, 'name', 'unknown.pdf'))
        logger.info(f"=== PDF extraction started | mode={mode} | file={pdf_name} ===")

        raw_bytes = file_stream.read()
        pages     = self._extract_pages_text(raw_bytes)

        # Free the raw PDF bytes immediately after page extraction
        del raw_bytes
        gc.collect()

        if not pages:
            logger.warning("No text could be extracted from the PDF.")
            return {"type": "simple", "data": []}

        passage_mode = self._is_passage_based(pages)
        logger.info(
            f"Total pages: {len(pages)} | "
            f"Paper type: {'PASSAGE-BASED' if passage_mode else 'SIMPLE MCQ'}"
        )

        total_chunks = (len(pages) + PAGES_PER_CHUNK - 1) // PAGES_PER_CHUNK

        if passage_mode:
            # -- Passage-based: flat MCQ list with passage embedded in question field --
            all_results: list[dict] = []

            for chunk_idx in range(0, len(pages), PAGES_PER_CHUNK):
                chunk_pages = pages[chunk_idx : chunk_idx + PAGES_PER_CHUNK]
                chunk_num   = chunk_idx // PAGES_PER_CHUNK + 1
                page_nums   = [p["page"] for p in chunk_pages]
                text_block  = "\n\n".join(
                    f"--- Page {p['page']} ---\n{p['text']}" for p in chunk_pages
                )
                label  = f"chunk {chunk_num}/{total_chunks}, pages {page_nums}"
                logger.info(f"Processing {label} ({len(text_block):,} chars)")

                raw     = self._call_gemini(mode, text_block, label, passage_mode=True, pdf_name=pdf_name)
                results = self._parse_response_simple(raw)
                logger.info(f"  >> {len(results)} question(s) in {label}")
                all_results.extend(results)

                # Free chunk data after processing
                del text_block, raw, results
                gc.collect()

            # Free pages data
            del pages
            gc.collect()

            # Deduplicate by question text and sanitize
            seen:   set[str]  = set()
            unique: list[dict] = []
            for q in all_results:
                q = _sanitize_question(q, pdf_name)
                key = (q.get("question") or q.get("question_text", "")).strip().lower()
                if key and key not in seen:
                    seen.add(key)
                    unique.append(q)

            # Free all_results
            del all_results
            gc.collect()

            logger.info(
                f"=== Done (passage-as-flat): {len(unique)} unique questions ==="
            )
            return {"type": "simple", "data": unique}

        else:
            # -- Simple MCQ: flat list ----------------------------------------
            all_results: list[dict] = []

            for chunk_idx in range(0, len(pages), PAGES_PER_CHUNK):
                chunk_pages = pages[chunk_idx : chunk_idx + PAGES_PER_CHUNK]
                chunk_num   = chunk_idx // PAGES_PER_CHUNK + 1
                page_nums   = [p["page"] for p in chunk_pages]
                text_block  = "\n\n".join(
                    f"--- Page {p['page']} ---\n{p['text']}" for p in chunk_pages
                )
                label  = f"chunk {chunk_num}/{total_chunks}, pages {page_nums}"
                logger.info(f"Processing {label} ({len(text_block):,} chars)")

                raw     = self._call_gemini(mode, text_block, label, passage_mode=False, pdf_name=pdf_name)
                results = self._parse_response_simple(raw)
                logger.info(f"  >> {len(results)} question(s) in {label}")
                all_results.extend(results)

                # Free chunk data after processing
                del text_block, raw, results
                gc.collect()

            # Free pages data
            del pages
            gc.collect()

            # Deduplicate and sanitize
            seen:   set[str]  = set()
            unique: list[dict] = []
            for q in all_results:
                q = _sanitize_question(q, pdf_name)
                key = q.get("question", "").strip().lower()
                if key and key not in seen:
                    seen.add(key)
                    unique.append(q)

            # Free all_results
            del all_results
            gc.collect()

            logger.info(
                f"=== Done: {len(unique)} unique questions ==="
            )
            return {"type": "simple", "data": unique}
