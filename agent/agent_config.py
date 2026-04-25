# agent/agent_config.py

VALID_DIFFICULTY = ["Easy", "Medium", "Hard"]

VALID_LEVELS = ["National", "State", "National Exam"]

VALID_ANSWERS = ["A", "B", "C", "D", "E"]

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
        "valid_years": range(2010, 2035)
    },
    "IBPS PO": {
        "department": "IBPS",
        "level": "National Exam",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "IPPB RRB": {
        "department": "IPPB",
        "level": "National Exam",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "NABARD Grade A": {
        "department": "NABARD",
        "level": "National Exam",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "NABARD Grade B": {
        "department": "NABARD",
        "level": "National Exam",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    # Add all your exam types here...
}
