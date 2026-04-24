# 🤖 Refining & Validation Agent — Complete Build Plan
### For Antigravity (Step-by-Step Instructions)

---

## 📌 Overview

This document describes how to build a **Refining & Validation Agent** that sits between the existing question extraction pipeline and the database. Its job is to:

1. **Analyze** each extracted JSON file for structural and data quality issues
2. **Normalize** all fields (year, exam_type, level, eligibility, etc.) to consistent values
3. **Fix** what it can automatically using an LLM
4. **Flag** what it cannot fix for human review
5. **Green-light** clean files and **auto-upload** them to the database

---

## 🗺️ Where This Agent Lives in the Pipeline

```
PDF Files
    ↓
[Existing Extractor] → exam_slug_year.json (docs/ folder)
    ↓
[Refining & Validation Agent]  ← YOU ARE BUILDING THIS
    ↓                ↓
Normalized JSON    Human Review Queue
    ↓
[Auto DB Upload]
    ↓
Database (MongoDB / Supabase / etc.)
```

---

## 📁 Required Folder Structure for the Agent

```
project-root/
├── docs/                          # Input: extracted JSONs from existing pipeline
│   ├── exim_bank_2024.json
│   ├── ippb_rrb_2017.json
│   └── ...
├── agent/
│   ├── refining_agent.py          # Main agent logic
│   ├── validators.py              # Field-level validation rules
│   ├── normalizer.py              # LLM + rule-based normalization
│   ├── db_uploader.py             # DB upload logic
│   ├── report_generator.py        # Human-readable validation report
│   └── config.py                  # Exam master data, field rules
├── agent_output/
│   ├── normalized/                # Cleaned, validated, ready-to-upload JSONs
│   ├── flagged/                   # JSONs that need human review
│   └── reports/                   # Per-file validation reports (.md or .json)
├── agent_status.json              # Live status file (for Streamlit monitor)
└── agent_history.json             # Tracks which files have been processed
```

---

## 🔍 Step 1 — Define the Required Schema (What a Valid Question Looks Like)

Before building anything, lock down the **master schema** every question object must satisfy.

### Required Fields (all must be present and non-empty)

| Field | Type | Example |
|---|---|---|
| `exam_type` | string | `"EXIM Bank Recruitment"` |
| `department` | string | `"EXIM Bank"` |
| `subject` | string | `"Professional Knowledge"` |
| `topic` | string | `"Banking"` |
| `subtopic` | string | `"Financial Inclusion"` |
| `difficulty` | enum | `"Easy"` / `"Medium"` / `"Hard"` |
| `question` | string | The full question text |
| `option` | object | `{"A": "...", "B": "...", "C": "...", "D": "..."}` |
| `answer` | enum | `"A"` / `"B"` / `"C"` / `"D"` |
| `explanation` | string | Explanation for the correct answer |
| `level` | enum | `"National"` / `"State"` / `"National Exam"` |
| `eligibility` | string | `"Graduate"` / `"12th/Graduate"` |
| `year` | string | 4-digit year string e.g. `"2024"` |
| `pdf_name` | string | Source PDF filename |

### Normalization Enums (canonical values only)

```python
# config.py

VALID_DIFFICULTY = ["Easy", "Medium", "Hard"]

VALID_LEVELS = ["National", "State", "National Exam"]

VALID_ANSWERS = ["A", "B", "C", "D"]

# Master exam registry — maps raw names → canonical name + department + year range
EXAM_MASTER = {
    "EXIM Bank Recruitment": {
        "department": "EXIM Bank",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2030)
    },
    "IBPS RRB Office Assistant (Clerk)": {
        "department": "IBPS",
        "level": "National Exam",
        "eligibility": "12th/Graduate",
        "valid_years": range(2010, 2030)
    },
    "IBPS PO": {
        "department": "IBPS",
        "level": "National Exam",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2030)
    },
    # Add all your exam types here...
}
```

> **Antigravity instruction:** Create `agent/config.py` with the above structures. This file is the single source of truth. All validation and normalization will refer to this file.

---

## 🧱 Step 2 — Build the Validator (`validators.py`)

The validator checks every question object and returns a structured report of issues.

### Validator Logic

```python
# validators.py

from config import VALID_DIFFICULTY, VALID_LEVELS, VALID_ANSWERS, EXAM_MASTER
import re

def validate_question(q: dict, file_year: str, file_exam_type: str) -> dict:
    """
    Returns a report for a single question:
    {
        "valid": True/False,
        "issues": [ { "field": "year", "severity": "ERROR/WARNING", "message": "..." } ],
        "fixable": True/False
    }
    """
    issues = []

    # 1. Check all required fields exist and are non-empty
    required_fields = [
        "exam_type", "department", "subject", "topic", "subtopic",
        "difficulty", "question", "option", "answer",
        "explanation", "level", "eligibility", "year", "pdf_name"
    ]
    for field in required_fields:
        if field not in q or not q[field]:
            issues.append({
                "field": field,
                "severity": "ERROR",
                "message": f"Missing or empty required field: {field}"
            })

    # 2. Validate year
    year = q.get("year", "")
    if not re.match(r"^\d{4}$", str(year)):
        issues.append({
            "field": "year",
            "severity": "ERROR",
            "message": f"Invalid year format: '{year}'. Expected 4-digit string."
        })
    elif str(year) != str(file_year):
        issues.append({
            "field": "year",
            "severity": "WARNING",
            "message": f"Year mismatch: question has '{year}' but file is named '{file_year}'."
        })

    # 3. Validate exam_type consistency
    if q.get("exam_type") != file_exam_type:
        issues.append({
            "field": "exam_type",
            "severity": "WARNING",
            "message": f"exam_type '{q.get('exam_type')}' does not match file's exam type '{file_exam_type}'."
        })

    # 4. Validate exam_type is known
    if q.get("exam_type") not in EXAM_MASTER:
        issues.append({
            "field": "exam_type",
            "severity": "ERROR",
            "message": f"Unknown exam_type: '{q.get('exam_type')}'. Not in master registry."
        })

    # 5. Validate difficulty enum
    if q.get("difficulty") not in VALID_DIFFICULTY:
        issues.append({
            "field": "difficulty",
            "severity": "WARNING",
            "message": f"Invalid difficulty: '{q.get('difficulty')}'. Expected one of {VALID_DIFFICULTY}."
        })

    # 6. Validate answer key
    if q.get("answer") not in VALID_ANSWERS:
        issues.append({
            "field": "answer",
            "severity": "ERROR",
            "message": f"Invalid answer key: '{q.get('answer')}'. Must be A, B, C, or D."
        })

    # 7. Validate options structure
    option = q.get("option", {})
    if not isinstance(option, dict) or set(option.keys()) != {"A", "B", "C", "D"}:
        issues.append({
            "field": "option",
            "severity": "ERROR",
            "message": "Options must be a dict with exactly keys A, B, C, D."
        })

    # 8. Check options text is duplicated inside question text (a known extraction artifact)
    question_text = q.get("question", "")
    for key, val in option.items():
        if val and f"({key})" in question_text and val in question_text:
            issues.append({
                "field": "question",
                "severity": "WARNING",
                "message": f"Option text for '{key}' appears embedded in question body. May need cleaning."
            })

    # 9. Validate level
    if q.get("level") not in VALID_LEVELS:
        issues.append({
            "field": "level",
            "severity": "WARNING",
            "message": f"Non-standard level: '{q.get('level')}'. Expected one of {VALID_LEVELS}."
        })

    # Determine if all issues are auto-fixable
    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    fixable = error_count == 0  # Only warnings = can auto-fix

    return {
        "valid": len(issues) == 0,
        "fixable": fixable,
        "issues": issues
    }
```

> **Antigravity instruction:** Create `agent/validators.py` with the above code. Do not modify the existing extraction pipeline — this is a new standalone module.

---

## 🔧 Step 3 — Build the Normalizer (`normalizer.py`)

The normalizer has two layers:
1. **Rule-based fixes** — fast, deterministic, no LLM needed
2. **LLM-based fixes** — for ambiguous cases (wrong exam name, embedded options in question, missing subtopic)

### Rule-Based Normalization

```python
# normalizer.py

from config import EXAM_MASTER, VALID_DIFFICULTY, VALID_LEVELS
import re

def normalize_question(q: dict, file_year: str, file_exam_type: str) -> dict:
    """Apply all deterministic fixes to a question dict. Returns updated dict."""
    q = q.copy()

    # Fix 1: Normalize year from filename if missing or invalid
    if not re.match(r"^\d{4}$", str(q.get("year", ""))):
        q["year"] = str(file_year)

    # Fix 2: Sync year to filename year if mismatch (WARNING level)
    if str(q.get("year")) != str(file_year):
        q["year"] = str(file_year)

    # Fix 3: Normalize exam_type using master registry
    if q.get("exam_type") in EXAM_MASTER:
        master = EXAM_MASTER[q["exam_type"]]
        # Sync department, level, eligibility from master
        q["department"] = master["department"]
        q["level"] = master["level"]
        q["eligibility"] = master["eligibility"]
    elif q.get("exam_type") != file_exam_type:
        # Try to correct from filename
        q["exam_type"] = file_exam_type
        if file_exam_type in EXAM_MASTER:
            master = EXAM_MASTER[file_exam_type]
            q["department"] = master["department"]
            q["level"] = master["level"]
            q["eligibility"] = master["eligibility"]

    # Fix 4: Normalize difficulty casing
    diff = q.get("difficulty", "")
    for valid in VALID_DIFFICULTY:
        if diff.lower() == valid.lower():
            q["difficulty"] = valid
            break

    # Fix 5: Strip embedded options from question text
    # Pattern: "(A) option text" appearing in question body
    question_text = q.get("question", "")
    cleaned = re.sub(r'\n\s*\([A-D]\)\s*.+', '', question_text).strip()
    q["question"] = cleaned

    # Fix 6: Normalize answer key to uppercase
    if q.get("answer"):
        q["answer"] = str(q["answer"]).strip().upper()

    # Fix 7: Normalize level
    level = q.get("level", "")
    if "national exam" in level.lower():
        q["level"] = "National Exam"
    elif "national" in level.lower():
        q["level"] = "National"
    elif "state" in level.lower():
        q["level"] = "State"

    return q
```

### LLM-Based Normalization (for complex cases)

Use the Anthropic API to fix questions where:
- `exam_type` is unknown or garbled (not in master registry)
- `subtopic` is missing
- `explanation` is empty
- Question text is malformed

```python
# normalizer.py (continued)

import anthropic
import json

client = anthropic.Anthropic()

LLM_FIX_PROMPT = """
You are a data normalization agent for an Indian competitive exam question bank.

Here is a question object that failed validation:
{question_json}

Here are the validation issues found:
{issues}

Here is the master exam registry for reference:
{master_registry}

Your task:
1. Fix ONLY the fields listed in the issues above.
2. Do not change any field that is not listed in issues.
3. Return ONLY a valid JSON object (no explanation, no markdown).
4. If you cannot confidently fix a field, return it as null.

Return format:
{{
  "exam_type": "...",
  "department": "...",
  "year": "...",
  "subtopic": "...",
  ...only the fields you are fixing...
}}
"""

def llm_fix_question(q: dict, issues: list) -> dict:
    """Use LLM to fix fields that rule-based normalization could not handle."""
    prompt = LLM_FIX_PROMPT.format(
        question_json=json.dumps(q, indent=2),
        issues=json.dumps(issues, indent=2),
        master_registry=json.dumps(EXAM_MASTER, indent=2, default=str)
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        fixes = json.loads(response.content[0].text)
        q = q.copy()
        for field, value in fixes.items():
            if value is not None:
                q[field] = value
        return q
    except Exception:
        return q  # Return original if LLM output can't be parsed
```

> **Antigravity instruction:** Create `agent/normalizer.py`. The LLM is only called when rule-based fixes leave unresolved ERRORs. This keeps API cost low.

---

## 🚦 Step 4 — Build the Main Agent Orchestrator (`refining_agent.py`)

This is the main runner. It processes each JSON file end-to-end.

### Agent Decision Tree Per File

```
Load JSON File
    ↓
Parse filename → extract exam_type_slug + year
    ↓
For each question in the file:
    ├── Run validator → get issues list
    ├── If no issues → mark CLEAN
    ├── If only WARNINGs → run rule-based normalizer → re-validate
    └── If ERRORs remain → run LLM normalizer → re-validate
            ├── If fixed → mark CLEAN
            └── If still ERROR → mark FLAGGED (send to human review)
    ↓
File-level decision:
    ├── All questions CLEAN → Green Light → Auto Upload to DB
    ├── <5% questions FLAGGED → Upload clean ones, log flagged ones
    └── >5% questions FLAGGED → Entire file goes to human review queue
```

### Agent Code

```python
# refining_agent.py

import json
import os
import re
from pathlib import Path
from datetime import datetime

from validators import validate_question
from normalizer import normalize_question, llm_fix_question
from db_uploader import upload_to_db
from report_generator import generate_report
from config import EXAM_MASTER

DOCS_FOLDER = Path("docs/")
NORMALIZED_FOLDER = Path("agent_output/normalized/")
FLAGGED_FOLDER = Path("agent_output/flagged/")
REPORTS_FOLDER = Path("agent_output/reports/")
HISTORY_FILE = Path("agent_history.json")
STATUS_FILE = Path("agent_status.json")

FLAG_THRESHOLD = 0.05  # If >5% questions flagged, whole file needs review

def parse_filename(filename: str) -> tuple[str, str]:
    """Extract exam_type_slug and year from filename like 'exim_bank_2024.json'"""
    stem = Path(filename).stem
    year_match = re.search(r'(\d{4})', stem)
    year = year_match.group(1) if year_match else "UNKNOWN"
    slug = stem.replace(f"_{year}", "").replace(year, "").strip("_")
    # Map slug back to canonical exam_type from master registry
    for exam_type in EXAM_MASTER:
        if exam_type.lower().replace(" ", "_") in slug.lower():
            return exam_type, year
    return slug, year

def process_file(json_path: Path):
    """Full pipeline for one JSON file."""
    update_status(f"Processing: {json_path.name}", 0)

    with open(json_path, "r") as f:
        questions = json.load(f)

    if not isinstance(questions, list):
        questions = [questions]

    file_exam_type, file_year = parse_filename(json_path.name)

    clean_questions = []
    flagged_questions = []
    report_entries = []

    for idx, q in enumerate(questions):
        update_status(f"Processing: {json_path.name}", round((idx / len(questions)) * 100))

        # Step 1: Validate
        result = validate_question(q, file_year, file_exam_type)

        if result["valid"]:
            clean_questions.append(q)
            report_entries.append({"index": idx, "status": "CLEAN", "issues": []})
            continue

        # Step 2: Apply rule-based normalization
        q_fixed = normalize_question(q, file_year, file_exam_type)
        result_after_rules = validate_question(q_fixed, file_year, file_exam_type)

        if result_after_rules["valid"]:
            clean_questions.append(q_fixed)
            report_entries.append({
                "index": idx, "status": "FIXED_BY_RULES",
                "original_issues": result["issues"]
            })
            continue

        # Step 3: Try LLM fix if ERRORs remain
        error_issues = [i for i in result_after_rules["issues"] if i["severity"] == "ERROR"]
        if error_issues:
            q_llm_fixed = llm_fix_question(q_fixed, error_issues)
            result_after_llm = validate_question(q_llm_fixed, file_year, file_exam_type)

            if result_after_llm["valid"]:
                clean_questions.append(q_llm_fixed)
                report_entries.append({
                    "index": idx, "status": "FIXED_BY_LLM",
                    "original_issues": result["issues"]
                })
                continue

            # LLM couldn't fix it either → FLAGGED
            flagged_questions.append({
                "question": q_llm_fixed,
                "remaining_issues": result_after_llm["issues"]
            })
            report_entries.append({
                "index": idx, "status": "FLAGGED",
                "remaining_issues": result_after_llm["issues"]
            })

    # File-level decision
    total = len(questions)
    flagged_ratio = len(flagged_questions) / total if total > 0 else 0

    if flagged_ratio > FLAG_THRESHOLD:
        # Whole file goes to human review
        save_flagged_file(json_path, questions, flagged_questions)
        status = "NEEDS_HUMAN_REVIEW"
    else:
        # Save clean + auto upload
        output_path = NORMALIZED_FOLDER / json_path.name
        save_normalized_file(output_path, clean_questions)

        if flagged_questions:
            save_flagged_file(json_path, [], flagged_questions)

        # Auto upload to DB
        upload_result = upload_to_db(clean_questions)
        status = "UPLOADED" if upload_result["success"] else "UPLOAD_FAILED"

    # Save report
    generate_report(json_path.name, report_entries, status, REPORTS_FOLDER)
    mark_as_processed(json_path.name)
    update_status(f"Done: {json_path.name} → {status}", 100)

def run_agent():
    """Scan docs/ folder and process all unprocessed JSON files."""
    NORMALIZED_FOLDER.mkdir(parents=True, exist_ok=True)
    FLAGGED_FOLDER.mkdir(parents=True, exist_ok=True)
    REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)

    processed = load_history()

    json_files = list(DOCS_FOLDER.glob("*.json"))
    pending = [f for f in json_files if f.name not in processed]

    print(f"Found {len(pending)} unprocessed files out of {len(json_files)} total.")

    for json_file in pending:
        try:
            process_file(json_file)
        except Exception as e:
            print(f"ERROR processing {json_file.name}: {e}")
            update_status(f"ERROR on {json_file.name}: {e}", -1)

def save_normalized_file(path: Path, questions: list):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    tmp.rename(path)

def save_flagged_file(original_path: Path, all_questions: list, flagged: list):
    output = FLAGGED_FOLDER / original_path.name
    with open(output, "w") as f:
        json.dump({
            "source_file": original_path.name,
            "flagged_at": datetime.now().isoformat(),
            "flagged_questions": flagged
        }, f, indent=2, ensure_ascii=False)

def load_history() -> set:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return set(json.load(f))
    return set()

def mark_as_processed(filename: str):
    history = load_history()
    history.add(filename)
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)

def update_status(message: str, progress: int):
    with open(STATUS_FILE, "w") as f:
        json.dump({
            "current_file": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }, f)

if __name__ == "__main__":
    run_agent()
```

> **Antigravity instruction:** Create `agent/refining_agent.py` as the main entry point. This is what users run — or what gets triggered automatically after each extraction batch.

---

## 📤 Step 5 — Build the DB Uploader (`db_uploader.py`)

Replace the content inside this file with your actual database connection. Templates for MongoDB and Supabase are provided.

```python
# db_uploader.py

import os
import json

# ---- CHOOSE YOUR DATABASE ----
# Uncomment the one you use:

# Option A: MongoDB
# from pymongo import MongoClient
# client = MongoClient(os.environ["MONGODB_URI"])
# db = client["question_bank"]
# collection = db["questions"]

# Option B: Supabase (PostgreSQL)
# from supabase import create_client
# supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def upload_to_db(questions: list) -> dict:
    """
    Upload a list of validated, normalized question objects to the database.
    Returns {"success": True/False, "uploaded_count": N, "error": "..."}
    """
    if not questions:
        return {"success": True, "uploaded_count": 0}

    try:
        # --- MongoDB ---
        # Remove _id from questions to let MongoDB generate new ones
        # (avoids duplicate key errors if re-uploading)
        clean = [{k: v for k, v in q.items() if k != "_id"} for q in questions]
        result = collection.insert_many(clean)
        return {"success": True, "uploaded_count": len(result.inserted_ids)}

        # --- Supabase ---
        # clean = [{k: v for k, v in q.items() if k != "_id"} for q in questions]
        # response = supabase.table("questions").insert(clean).execute()
        # return {"success": True, "uploaded_count": len(response.data)}

    except Exception as e:
        return {"success": False, "uploaded_count": 0, "error": str(e)}
```

> **Antigravity instruction:** Create `agent/db_uploader.py`. Ask the user which database they use (MongoDB or Supabase) and fill in the connection string from environment variables. Never hardcode credentials.

---

## 📊 Step 6 — Build the Report Generator (`report_generator.py`)

After processing each file, the agent saves a human-readable Markdown report.

```python
# report_generator.py

from pathlib import Path
from datetime import datetime
import json

def generate_report(filename: str, entries: list, final_status: str, reports_folder: Path):
    """Generate a Markdown validation report for a processed JSON file."""

    clean = [e for e in entries if e["status"] in ("CLEAN", "FIXED_BY_RULES", "FIXED_BY_LLM")]
    flagged = [e for e in entries if e["status"] == "FLAGGED"]

    report_lines = [
        f"# Validation Report: `{filename}`",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Final Status:** `{final_status}`",
        "",
        "## Summary",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Total Questions | {len(entries)} |",
        f"| ✅ Clean (no changes) | {sum(1 for e in entries if e['status'] == 'CLEAN')} |",
        f"| 🔧 Fixed by Rules | {sum(1 for e in entries if e['status'] == 'FIXED_BY_RULES')} |",
        f"| 🤖 Fixed by LLM | {sum(1 for e in entries if e['status'] == 'FIXED_BY_LLM')} |",
        f"| 🚨 Flagged (needs review) | {len(flagged)} |",
        "",
    ]

    if flagged:
        report_lines += ["## 🚨 Flagged Questions", ""]
        for entry in flagged:
            report_lines.append(f"### Question #{entry['index'] + 1}")
            for issue in entry.get("remaining_issues", []):
                report_lines.append(
                    f"- **{issue['severity']}** | Field: `{issue['field']}` — {issue['message']}"
                )
            report_lines.append("")

    report_path = reports_folder / filename.replace(".json", "_report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    print(f"Report saved: {report_path}")
```

> **Antigravity instruction:** Create `agent/report_generator.py`. Reports are saved in `agent_output/reports/` and can be viewed in the Streamlit monitor tab.

---

## 🖥️ Step 7 — Add Agent Tab to Streamlit App (`app.py`)

Add a new tab called **"🔍 Validation Agent"** to the existing Streamlit app. It should show:

```python
# In app.py — add this to the existing tabs list

with tab_agent:
    st.header("🔍 Refining & Validation Agent")

    # --- Run Agent ---
    if st.button("▶️ Run Agent Now"):
        import subprocess
        subprocess.Popen(["python", "agent/refining_agent.py"])
        st.success("Agent started! Monitor progress below.")

    # --- Live Status ---
    import json, time
    from pathlib import Path

    status_file = Path("agent_status.json")
    if status_file.exists():
        with open(status_file) as f:
            status = json.load(f)
        st.metric("Current File", status.get("current_file", "Idle"))
        st.progress(max(0, status.get("progress", 0)) / 100)
        st.caption(f"Last updated: {status.get('timestamp', '')}")

    # --- Output Summary ---
    st.subheader("📁 Processed Files")
    norm_folder = Path("agent_output/normalized/")
    flag_folder = Path("agent_output/flagged/")

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Normalized: {len(list(norm_folder.glob('*.json')))} files")
    with col2:
        st.warning(f"🚨 Flagged: {len(list(flag_folder.glob('*.json')))} files")

    # --- Show Reports ---
    report_folder = Path("agent_output/reports/")
    reports = list(report_folder.glob("*_report.md"))
    if reports:
        selected = st.selectbox("View report:", [r.name for r in reports])
        with open(report_folder / selected) as f:
            st.markdown(f.read())
```

> **Antigravity instruction:** In `app.py`, add `"🔍 Validation Agent"` to the existing `st.tabs(...)` call, and paste the tab code above inside that tab's `with` block.

---

## ⚙️ Step 8 — Auto-Trigger After Extraction

To make this fully automatic, call the agent at the end of every extraction batch in `automate_batch_extractor.py`:

```python
# At the end of automate_batch_extractor.py, after batch processing completes:

import subprocess

def trigger_validation_agent():
    """Kick off the refining and validation agent after extraction."""
    print("🔍 Starting Refining & Validation Agent...")
    subprocess.Popen(["python", "agent/refining_agent.py"])

# Call this at the end of your batch_process() function:
# trigger_validation_agent()
```

> **Antigravity instruction:** In `automate_batch_extractor.py`, import and call `trigger_validation_agent()` at the very end of the batch processing function, after all PDFs in the batch are done.

---

## 🔐 Step 9 — Environment Variables

Add these to your `.env` file:

```env
# Database
MONGODB_URI=mongodb+srv://your_user:your_pass@cluster.mongodb.net/question_bank
# OR
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key

# Anthropic (already set if you use Gemini, add this for LLM normalization)
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 📦 Step 10 — Dependencies to Install

```bash
pip install anthropic pymongo python-dotenv
# OR for Supabase:
pip install anthropic supabase python-dotenv
```

Add to `requirements.txt`:
```
anthropic>=0.20.0
pymongo>=4.6.0
python-dotenv>=1.0.0
```

---

## ✅ Complete Checklist for Antigravity

- [ ] Create `agent/config.py` — master schema, exam registry, valid enum values
- [ ] Create `agent/validators.py` — field-level validation with severity levels
- [ ] Create `agent/normalizer.py` — rule-based + LLM-based normalization
- [ ] Create `agent/db_uploader.py` — database upload with env var credentials
- [ ] Create `agent/report_generator.py` — per-file Markdown validation reports
- [ ] Create `agent/refining_agent.py` — main orchestrator with decision tree
- [ ] Create `agent_output/normalized/`, `agent_output/flagged/`, `agent_output/reports/` folders
- [ ] Update `app.py` — add "🔍 Validation Agent" tab with live status and reports
- [ ] Update `automate_batch_extractor.py` — auto-trigger agent after each batch
- [ ] Update `.env` — add DB credentials and Anthropic API key
- [ ] Update `requirements.txt` — add new dependencies
- [ ] Test with `exim_bank_recruitment_2024.json` and `ippb_rrb_2017.json` as sample inputs

---

## 🧪 How to Test the Agent

```bash
# 1. Copy sample JSONs to docs/ folder
cp exim_bank_recruitment_2024.json docs/
cp ippb_rrb_2017.json docs/

# 2. Run the agent
python agent/refining_agent.py

# 3. Check output
ls agent_output/normalized/   # Should contain cleaned JSONs
ls agent_output/flagged/      # Should be empty if files are clean
ls agent_output/reports/      # Should contain *_report.md files
cat agent_output/reports/exim_bank_recruitment_2024_report.md
```

---

## 📐 Agent Logic Summary Diagram

```
JSON File (docs/)
      │
      ▼
Parse filename → file_exam_type, file_year
      │
      ▼
For each question:
  ┌───────────────────────────────────────┐
  │  Validate → issues[]                 │
  │                                       │
  │  No issues? ──────────────→ CLEAN ✅  │
  │                                       │
  │  Only WARNINGs?                       │
  │    → Rule-based normalize             │
  │    → Re-validate                      │
  │    → Fixed? ──────────────→ CLEAN ✅  │
  │                                       │
  │  ERRORs remain?                       │
  │    → LLM normalize                    │
  │    → Re-validate                      │
  │    → Fixed? ──────────────→ CLEAN ✅  │
  │    → Still errors? ───────→ FLAGGED 🚨│
  └───────────────────────────────────────┘
      │
      ▼
  flagged_ratio = flagged / total
      │
  ≤5%? ──→ Save normalized → Auto Upload DB → Report
  >5%? ──→ Entire file to human review queue → Report
```

---

*End of Build Plan — All steps are ready for implementation in Antigravity.*
