# agent/validators.py

from agent.agent_config import VALID_DIFFICULTY, VALID_LEVELS, VALID_ANSWERS, EXAM_MASTER
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
    elif str(year) != str(file_year) and file_year != "UNKNOWN":
        issues.append({
            "field": "year",
            "severity": "WARNING",
            "message": f"Year mismatch: question has '{year}' but file is named '{file_year}'."
        })

    # 3. Validate exam_type consistency
    if q.get("exam_type") != file_exam_type and file_exam_type != "UNKNOWN":
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
    valid_keys_4 = {"A", "B", "C", "D"}
    valid_keys_5 = {"A", "B", "C", "D", "E"}
    
    if not isinstance(option, dict) or set(option.keys()) not in [valid_keys_4, valid_keys_5]:
        issues.append({
            "field": "option",
            "severity": "ERROR",
            "message": "Options must be a dict with exactly keys {A,B,C,D} or {A,B,C,D,E}."
        })

    # 8. Check options text is duplicated inside question text (a known extraction artifact)
    question_text = q.get("question", "")
    for key, val in option.items():
        if isinstance(val, str) and val and f"({key})" in question_text and val in question_text:
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
