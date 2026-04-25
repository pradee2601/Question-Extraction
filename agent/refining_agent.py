# agent/refining_agent.py

import json
import os
import re
import sys
from pathlib import Path

# Fix Windows encoding issues with emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
from datetime import datetime

from agent.validators import validate_question
from agent.normalizer import normalize_question, llm_fix_question
from agent.db_uploader import upload_to_db
from agent.report_generator import generate_report
from agent.agent_config import EXAM_MASTER
from utils.helpers import LLMTracker

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

DOCS_FOLDER = BASE_DIR / "docs"
NORMALIZED_FOLDER = BASE_DIR / "agent_output" / "normalized"
FLAGGED_FOLDER = BASE_DIR / "agent_output" / "flagged"
REPORTS_FOLDER = BASE_DIR / "agent_output" / "reports"
HISTORY_FILE = BASE_DIR / "agent_history.json"
STATUS_FILE = BASE_DIR / "agent_status.json"

FLAG_THRESHOLD = 0.05  # If >5% questions flagged, whole file needs review

def parse_filename(filename: str) -> tuple[str, str]:
    """Extract exam_type_slug and year from filename like 'exim_bank_2024.json'"""
    stem = Path(filename).stem
    year_match = re.search(r'(\d{4})', stem)
    year = year_match.group(1) if year_match else "UNKNOWN"
    slug = stem.replace(f"_{year}", "").replace(year, "").strip("_")
    
    # Map slug back to canonical exam_type from master registry
    for exam_type in EXAM_MASTER:
        # Check if slug is part of the exam name or vice versa
        clean_slug = slug.lower().replace("_", " ")
        clean_exam = exam_type.lower()
        if clean_slug in clean_exam or clean_exam in clean_slug:
            return exam_type, year
            
    return slug, year

def process_file(json_path: Path):
    """Full pipeline for one JSON file."""
    LLMTracker.reset()
    update_status(f"Processing: {json_path.name}", 0)

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            questions = json.load(f)
        except Exception as e:
            print(f"Failed to load JSON: {e}")
            return

    if not isinstance(questions, list):
        questions = [questions]

    file_exam_type, file_year = parse_filename(json_path.name)
    print(f"\n🚀 [TURBO-MODE] Refinement for: {json_path.name}")
    print(f"📋 Metadata Sync -> Exam: {file_exam_type} | Year: {file_year}")

    clean_questions = []
    purged_count = 0
    report_entries = []

    total_q = len(questions)
    for idx, q in enumerate(questions):
        # UI Status Update
        if total_q > 0:
            update_status(f"Cleaning: {json_path.name}", round((idx / total_q) * 100))
        
        # --- RULE 1: FORCE METADATA SYNC (Zero LLM) ---
        q["year"] = str(file_year)
        q["exam_type"] = file_exam_type
        
        # --- RULE 2: STRUCTURAL PURGE (Speed up) ---
        # If no question text or no options, DELETE instead of fixing
        options = q.get("option", q.get("options", {}))
        if not q.get("question") or not options or len(options) < 2:
            purged_count += 1
            continue

        # Step 1: Rapid Validation
        result = validate_question(q, file_year, file_exam_type)

        if result["valid"]:
            clean_questions.append(q)
            report_entries.append({"index": idx, "status": "CLEAN"})
            continue

        # Step 2: Apply fast rule-based normalization
        q_fixed = normalize_question(q, file_year, file_exam_type)
        result_after_rules = validate_question(q_fixed, file_year, file_exam_type)

        if result_after_rules["valid"]:
            clean_questions.append(q_fixed)
            report_entries.append({"index": idx, "status": "FIXED_BY_RULES"})
            continue

        # Step 3: LLM is a LAST RESORT (Fix malformed options, missing answers, etc.)
        # We call the AI if the question is invalid but seems to have enough content to be salvageable.
        has_error = any(issue["severity"] == "ERROR" for issue in result_after_rules["issues"])
        
        if has_error and len(q_fixed.get("question", "")) > 30:
            print(f"  ✨ Saving high-quality question {idx + 1} with LLM...")
            q_llm_fixed = llm_fix_question(q_fixed, result_after_rules["issues"])
            if validate_question(q_llm_fixed, file_year, file_exam_type)["valid"]:
                clean_questions.append(q_llm_fixed)
                report_entries.append({"index": idx, "status": "FIXED_BY_LLM"})
                continue

        # If still invalid after all this, we skip it to maintain speed and quality
        purged_count += 1
        report_entries.append({
            "index": idx, 
            "status": "FLAGGED", 
            "remaining_issues": validate_question(q_fixed, file_year, file_exam_type)["issues"]
        })

    # Final file-level processing
    total = len(questions)
    
    # Save clean + auto upload
    output_path = NORMALIZED_FOLDER / json_path.name
    save_normalized_file(output_path, clean_questions)

    # Auto upload to DB
    upload_result = upload_to_db(clean_questions)
    status = "UPLOADED" if upload_result["success"] else "UPLOAD_FAILED"

    # Save report
    generate_report(json_path.name, report_entries, status, REPORTS_FOLDER, LLMTracker.get_report())
    mark_as_processed(json_path.name)
    
    print(f"✅ Finished: {json_path.name} | Result: {status}")
    print(f"   - Kept: {len(clean_questions)} | Purged: {purged_count}")
    
    update_status(f"Done: {json_path.name} → {status}", 100)

def run_agent():
    """Scan docs/ folder and process all unprocessed JSON files."""
    NORMALIZED_FOLDER.mkdir(parents=True, exist_ok=True)
    FLAGGED_FOLDER.mkdir(parents=True, exist_ok=True)
    REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)

    processed = load_history()

    if not DOCS_FOLDER.exists():
        print(f"Docs folder not found: {DOCS_FOLDER}")
        return

    json_files = list(DOCS_FOLDER.glob("*.json"))
    # Exclude status and history files if they were in docs (they shouldn't be)
    pending = [f for f in json_files if f.name not in processed and f.name not in ("automation_status.json",)]

    print(f"Found {len(pending)} unprocessed files out of {len(json_files)} total.")

    for json_file in pending:
        try:
            process_file(json_file)
        except Exception as e:
            print(f"ERROR processing {json_file.name}: {e}")
            update_status(f"ERROR on {json_file.name}: {e}", -1)

def save_normalized_file(path: Path, questions: list):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    if path.exists():
        path.unlink()
    tmp.rename(path)

def save_flagged_file(original_path: Path, all_questions: list, flagged: list):
    output = FLAGGED_FOLDER / original_path.name
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "source_file": original_path.name,
            "flagged_at": datetime.now().isoformat(),
            "flagged_questions": flagged
        }, f, indent=2, ensure_ascii=False)

def load_history() -> set:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def mark_as_processed(filename: str):
    history = load_history()
    history.add(filename)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history), f)

def update_status(message: str, progress: int):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "current_file": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }, f)

if __name__ == "__main__":
    run_agent()
