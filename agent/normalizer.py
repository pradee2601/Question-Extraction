# agent/normalizer.py

import re
import json
from agent.agent_config import EXAM_MASTER, VALID_DIFFICULTY, VALID_LEVELS
from utils.helpers import call_llm

def normalize_question(q: dict, file_year: str, file_exam_type: str) -> dict:
    """Apply all deterministic fixes to a question dict. Returns updated dict."""
    q = q.copy()

    # Fix 1: Normalize year from filename if missing or invalid
    if not re.match(r"^\d{4}$", str(q.get("year", ""))):
        if file_year and file_year != "UNKNOWN":
            q["year"] = str(file_year)

    # Fix 2: Sync year to filename year if mismatch (WARNING level)
    if str(q.get("year")) != str(file_year) and file_year != "UNKNOWN":
        q["year"] = str(file_year)

    # Fix 3: Normalize exam_type using master registry
    if q.get("exam_type") in EXAM_MASTER:
        master = EXAM_MASTER[q["exam_type"]]
        # Sync department, level, eligibility from master
        q["department"] = master["department"]
        q["level"] = master["level"]
        q["eligibility"] = master["eligibility"]
    elif file_exam_type in EXAM_MASTER:
        # Try to correct from filename if current exam_type is invalid
        q["exam_type"] = file_exam_type
        master = EXAM_MASTER[file_exam_type]
        q["department"] = master["department"]
        q["level"] = master["level"]
        q["eligibility"] = master["eligibility"]

    # Fix 4: Normalize difficulty casing
    diff = q.get("difficulty", "")
    if isinstance(diff, str):
        for valid in VALID_DIFFICULTY:
            if diff.lower() == valid.lower():
                q["difficulty"] = valid
                break

    # Fix 5: Strip embedded options from question text
    # Pattern: "(A) option text" appearing in question body
    question_text = q.get("question", "")
    if isinstance(question_text, str):
        cleaned = re.sub(r'\n\s*\([A-D]\)\s*.+', '', question_text).strip()
        q["question"] = cleaned

    # Fix 6: Normalize answer key to uppercase
    if q.get("answer"):
        q["answer"] = str(q["answer"]).strip().upper()

    # Fix 7: Normalize level
    level = q.get("level", "")
    if isinstance(level, str):
        if "national exam" in level.lower():
            q["level"] = "National Exam"
        elif "national" in level.lower():
            q["level"] = "National"
        elif "state" in level.lower():
            q["level"] = "State"

    return q

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

def extract_json(text: str) -> dict:
    """Extract the first JSON object found in the text."""
    if not text:
        return None
    
    text = text.strip()
    
    # Try direct parse first (cleanest case)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Look for the first { and match it with its corresponding }
    # This handles "Extra data" errors where text follows the JSON
    start = text.find("{")
    if start == -1:
        return None
        
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                json_str = text[start:i+1]
                try:
                    return json.loads(json_str)
                except:
                    # If it fails, maybe there's another { later? 
                    # For now, return None and let it fall through
                    return None
    return None

def llm_fix_question(q: dict, issues: list) -> dict:
    """Call LLM to fix specific structural or content issues."""
    prompt = f"""
    You are a Question Bank Auditor. Fix the following JSON question based on these issues:
    {json.dumps(issues, indent=2)}
    
    Original Question:
    {json.dumps(q, indent=2)}
    
    Return ONLY the corrected JSON object. No conversation.
    """
    
    response = call_llm(prompt)
    fixed_q = extract_json(response)
    
    if isinstance(fixed_q, dict):
        # Ensure ID and critical metadata are preserved
        if "_id" in q: fixed_q["_id"] = q["_id"]
        return fixed_q
    
    if isinstance(fixed_q, list) and len(fixed_q) > 0:
        # LLM returned an array, take first item
        f_q = fixed_q[0]
        if isinstance(f_q, dict):
            if "_id" in q: f_q["_id"] = q["_id"]
            return f_q
    
    print(f"⚠️ LLM Fix failed for a question. Returning original.")
    return q
