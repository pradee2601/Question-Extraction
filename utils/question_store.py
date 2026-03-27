"""
utils/question_store.py
------------------------
Manages per-exam-category JSON question banks stored inside docs/.

Two document schemas are supported:

  simple  : docs/<slug>.json  →  JSON array of MCQ objects
  passage : docs/<slug>.json  →  JSON array containing a mix of:
              - standalone MCQ objects  (same schema as simple)
              - passage exam objects    {"type":"passage_exam", "exam":..., "passages":[], "questions":[]}

Duplicate detection
  - simple MCQs:   based on "question" text (exact, case-insensitive)
  - passage exams: based on ("exam" + "date") pair
"""

import json
import os
import re
import gc
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

# -- Exam category definitions -------------------------------------------------
EXAM_CATEGORIES: dict[str, dict] = {
    "upsc": {
        "label":    "UPSC",
        "file":     "upsc.json",
        "keywords": ["upsc", "ias", "ips", "civil services", "civil service",
                     "prelims", "mains", "capf", "csat", "ifos", "indian forest",
                     "ese", "ies", "cds", "nda", "cms", "geo-scientist",
                     "epfo", "combined medical"],
    },
    "ssc": {
        "label":    "SSC",
        "file":     "ssc.json",
        "keywords": ["ssc", "staff selection", "cgl", "chsl", "mts",
                     "gd constable", "ssc je", "cpo", "stenographer",
                     "selection post", "deo"],
    },
    "banking": {
        "label":    "Banking (IBPS, SBI, RBI)",
        "file":     "banking.json",
        "keywords": ["ibps", "sbi", "banking", "bank", "po",
                     "clerk", "nabard", "rbi", "sebi", "sidbi", "exim",
                     "ippb", "regional rural bank"],
    },
    "insurance": {
        "label":    "Insurance (LIC, GIC, NIACL)",
        "file":     "insurance.json",
        "keywords": ["lic", "insurance", "niacl", "uiic", "gic",
                     "aic", "ado", "aao"],
    },
    "railway": {
        "label":    "Railway (RRB, RPF)",
        "file":     "railway.json",
        "keywords": ["railway", "rrb", "alp", "ntpc", "loco pilot",
                     "group d", "je railway", "sse railway", "indian railway",
                     "rpf", "technician railway", "constable railway"],
    },
    "defense_nda": {
        "label":    "Defence - NDA",
        "file":     "defense_nda.json",
        "keywords": ["nda", "national defence academy"],
    },
    "defense_cds": {
        "label":    "Defence - CDS",
        "file":     "defense_cds.json",
        "keywords": ["cds", "combined defence services"],
    },
    "defense_afcat": {
        "label":    "Defence - AFCAT",
        "file":     "defense_afcat.json",
        "keywords": ["afcat", "air force common admission"],
    },
    "defense_other": {
        "label":    "Defence - Other",
        "file":     "defense_other.json",
        "keywords": ["defense", "defence", "army", "navy", "air force",
                     "military", "coast guard", "agniveer",
                     "territorial army", "mns"],
    },
    "teaching": {
        "label":    "Teaching (CTET, UGC NET, KVS)",
        "file":     "teaching.json",
        "keywords": ["ctet", "ugc net", "kvs", "nvs", "dsssb",
                     "tet", "teacher", "prt", "tgt", "pgt", "b.ed"],
    },
    "judiciary": {
        "label":    "Judiciary",
        "file":     "judiciary.json",
        "keywords": ["judiciary", "civil judge", "district judge",
                     "high court", "judicial", "magistrate", "law"],
    },
    "psu": {
        "label":    "PSU (ONGC, IOCL, BHEL, etc.)",
        "file":     "psu.json",
        "keywords": ["ongc", "iocl", "bhel", "sail", "ntpc", "bel",
                     "drdo", "isro", "hal", "coal india", "power grid",
                     "npcil", "gail", "beml", "mrpl", "gate"],
    },
    "healthcare": {
        "label":    "Healthcare (AIIMS, ESIC)",
        "file":     "healthcare.json",
        "keywords": ["aiims", "esic", "nurse", "paramedical",
                     "medical officer", "anm", "gnm", "pharmacist",
                     "lab technician", "staff nurse"],
    },
    "technical": {
        "label":    "Technical (CPWD, DMRC, BSNL)",
        "file":     "technical.json",
        "keywords": ["cpwd", "dmrc", "delhi metro", "bsnl", "mtnl",
                     "nic", "meity"],
    },
    "central_police": {
        "label":    "Central Police (BSF, CRPF, CISF)",
        "file":     "central_police.json",
        "keywords": ["bsf", "crpf", "cisf", "itbp", "ssb",
                     "assam rifles", "central police"],
    },
    "neet_ug": {
        "label":    "NEET UG",
        "file":     "neet_ug.json",
        "keywords": ["neet ug", "neet-ug", "mbbs", "bds", "neet"],
    },
    "neet_pg": {
        "label":    "NEET PG",
        "file":     "neet_pg.json",
        "keywords": ["neet pg", "neet-pg", "neet ss", "neet-ss"],
    },
    "jee_main": {
        "label":    "JEE Main",
        "file":     "jee_main.json",
        "keywords": ["jee main", "jee-main", "aieee"],
    },
    "jee_advanced": {
        "label":    "JEE Advanced",
        "file":     "jee_advanced.json",
        "keywords": ["jee advanced", "jee-advanced", "iit jee", "iit-jee"],
    },
    "state_psc": {
        "label":    "State PSC / State Exams",
        "file":     "state_psc.json",
        "keywords": ["state psc", "state civil", "psc", "state police",
                     "state tet", "state judiciary"],
    },
    "other": {
        "label":    "Other (India Post, Cantonment, etc.)",
        "file":     "other.json",
        "keywords": ["india post", "cantonment", "apprenticeship",
                     "municipal", "cooperative bank", "supreme court",
                     "ncc", "sports authority"],
    },
}

SLUG_ORDER = [
    "upsc", "ssc", "banking", "insurance", "railway",
    "defense_nda", "defense_cds", "defense_afcat", "defense_other",
    "teaching", "judiciary", "psu", "healthcare", "technical",
    "central_police", "neet_pg", "neet_ug", "jee_main", "jee_advanced",
    "state_psc", "other",
]
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


# -- Helpers -------------------------------------------------------------------

def _ensure_docs_dir() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def _file_path(slug: str) -> Path:
    return DOCS_DIR / EXAM_CATEGORIES[slug]["file"]


def detect_category(exam_name: str) -> str | None:
    """Infer category slug from exam name. Returns None if undetermined."""
    if not exam_name or not isinstance(exam_name, str):
        return None
    lower = exam_name.lower()
    for slug in SLUG_ORDER:
        for kw in EXAM_CATEGORIES[slug]["keywords"]:
            if kw in lower:
                return slug
    return None


def _normalize_question_text(text: str) -> str:
    """Normalize question text for duplicate comparison - strips whitespace,
    removes question numbers, and lowercases."""
    if not text:
        return ""
    text = text.strip().lower()
    # Remove leading question numbers like "Q1.", "1.", "Q.1", etc.
    text = re.sub(r'^q?\.?\s*\d+[\.\)\:]?\s*', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text


# -- Read / Write --------------------------------------------------------------

def _load_raw_file(filename: str) -> list:
    """Load from a specific file in docs/."""
    _ensure_docs_dir()
    fpath = DOCS_DIR / filename
    if not fpath.exists():
        return []
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        logger.error(f"Failed to load {fpath}: {e}")
        return []


def _save_raw_file(filename: str, records: list) -> None:
    _ensure_docs_dir()
    fpath = DOCS_DIR / filename
    temp_fpath = DOCS_DIR / f"{filename}.tmp"
    try:
        with open(temp_fpath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        temp_fpath.replace(fpath) # Atomic replacement
        logger.info(f"Saved {len(records)} record(s) to {fpath}")
    except Exception as e:
        logger.error(f"Failed to save {fpath}: {e}")
        if temp_fpath.exists():
            temp_fpath.unlink() # Cleanup on error
        raise


def _load_raw(slug: str) -> list:
    """Load the raw JSON array from disk. Returns [] if missing or corrupt."""
    return _load_raw_file(EXAM_CATEGORIES[slug]["file"])


def _save_raw(slug: str, records: list) -> None:
    _save_raw_file(EXAM_CATEGORIES[slug]["file"], records)


def load_questions(slug: str) -> list[dict]:
    """
    Return all SIMPLE MCQ dicts for the slug.
    Passage exam objects are excluded from this list
    (use load_all_records for the full picture).
    """
    return [r for r in _load_raw(slug) if r.get("type") != "passage_exam"]


def load_all_records(slug: str) -> list:
    """Return every record (both MCQs and passage exam objects) for the slug."""
    return _load_raw(slug)


def load_passage_exams(slug: str) -> list[dict]:
    """Return only passage-exam objects for the slug."""
    return [r for r in _load_raw(slug) if r.get("type") == "passage_exam"]


def save_questions(slug: str, questions: list[dict]) -> None:
    """Overwrite the simple-MCQ list (non-passage records) for a slug."""
    existing = _load_raw(slug)
    passage_records = [r for r in existing if r.get("type") == "passage_exam"]
    _save_raw(slug, passage_records + questions)


def append_questions(slug: str, new_questions: list[dict]) -> tuple[int, int]:
    """
    Append simple MCQs, skipping exact duplicates.
    Uses normalized comparison for better dedup.
    Returns (added, skipped).
    """
    existing_mcqs = load_questions(slug)
    existing_texts: set[str] = {
        _normalize_question_text(q.get("question", "")) for q in existing_mcqs
    }
    added = skipped = 0
    for q in new_questions:
        q_text = _normalize_question_text(q.get("question", ""))
        if not q_text:
            skipped += 1
            continue
        if q_text in existing_texts:
            skipped += 1
        else:
            existing_mcqs.append(q)
            existing_texts.add(q_text)
            added += 1

    save_questions(slug, existing_mcqs)

    # Free memory after save
    del existing_mcqs
    del existing_texts
    gc.collect()

    return added, skipped


def append_questions_to_file(filename: str, new_questions: list[dict]) -> tuple[int, int]:
    """Append questions to a specific file with deduplication."""
    existing = _load_raw_file(filename)
    existing_texts = {
        _normalize_question_text(q.get("question", "")) for q in existing 
        if q.get("type") != "passage_exam"
    }
    added = skipped = 0
    for q in new_questions:
        q_text = _normalize_question_text(q.get("question", ""))
        if not q_text or q_text in existing_texts:
            skipped += 1
        else:
            existing.append(q)
            existing_texts.add(q_text)
            added += 1
    _save_raw_file(filename, existing)
    return added, skipped


def append_passage_exam_to_file(filename: str, exam_obj: dict) -> tuple[bool, str]:
    """Append passage exam to a specific file with deduplication."""
    records = _load_raw_file(filename)
    exam_key = (
        str(exam_obj.get("exam_type") or exam_obj.get("exam") or "").strip().lower(),
        str(exam_obj.get("year") or exam_obj.get("date") or "").strip().lower()
    )
    for r in records:
        if r.get("type") == "passage_exam":
            ek = (
                str(r.get("exam_type") or r.get("exam") or "").strip().lower(),
                str(r.get("year") or r.get("date") or "").strip().lower()
            )
            if ek == exam_key:
                return False, f"Duplicate passage exam already in {filename}"
                
    tagged = dict(exam_obj)
    tagged["type"] = "passage_exam"
    records.append(tagged)
    _save_raw_file(filename, records)
    return True, f"Saved to {filename}"


def append_passage_exam(slug: str, exam_obj: dict) -> tuple[bool, str]:
    return append_passage_exam_to_file(EXAM_CATEGORIES[slug]["file"], exam_obj)


# -- Counts -------------------------------------------------------------------

def question_count(slug: str) -> int:
    """Count of simple MCQs for a slug."""
    return len(load_questions(slug))


def passage_exam_count(slug: str) -> int:
    """Count of passage-exam objects for a slug."""
    return len(load_passage_exams(slug))


def all_counts() -> dict[str, dict]:
    """Return {slug: {"mcq": int, "passage_exams": int}} for every category."""
    return {
        slug: {
            "mcq":           question_count(slug),
            "passage_exams": passage_exam_count(slug),
        }
        for slug in SLUG_ORDER
    }
