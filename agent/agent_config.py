# agent/agent_config.py

VALID_DIFFICULTY = ["Easy", "Medium", "Hard"]

VALID_LEVELS = ["National", "State", "National Exam"]

VALID_ANSWERS = ["A", "B", "C", "D", "E"]

# Master exam registry — synced from Course-Explorer dashboard
EXAM_MASTER = {
    "AFCAT": {
        "department": "Indian Air Force",
        "level": "National",
        "eligibility": "Graduate/12th",
        "valid_years": range(2015, 2035)
    },
    "AIC Management Trainee (MTS)": {
        "department": "Agriculture Insurance Company",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "AIIMS Nursing / Paramedical Recruitment": {
        "department": "AIIMS / NTA",
        "level": "National",
        "eligibility": "Nursing/Paramedical",
        "valid_years": range(2010, 2035)
    },
    "ANM / GNM / Staff Nurse State Exams": {
        "department": "State Health Dept.",
        "level": "State",
        "eligibility": "Diploma/Nursing",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State PSC Combined Services": {
        "department": "State Public Service Commission (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State Police Constable Recruitment": {
        "department": "State Police Department (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Andhra Pradesh - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Andhra Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Apprenticeship Vacancies (Railways / PSUs / Industry)": {
        "department": "Apprenticeship Boards / PSUs",
        "level": "National/State",
        "eligibility": "ITI/Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Arrays": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Arunachal Pradesh - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State PSC Combined Services": {
        "department": "State Public Service Commission (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State Police Constable Recruitment": {
        "department": "State Police Department (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Arunachal Pradesh - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Arunachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State PSC Combined Services": {
        "department": "State Public Service Commission (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State Police Constable Recruitment": {
        "department": "State Police Department (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Assam - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Assam)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "BEL Recruitment": {
        "department": "BEL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "BEML Recruitment (Technical / Management) - Variant 1": {
        "department": "BEML",
        "level": "National",
        "eligibility": "Graduate/ITI",
        "valid_years": range(2010, 2035)
    },
    "BEML Recruitment (Technical / Management) - Variant 2": {
        "department": "BEML",
        "level": "National",
        "eligibility": "Graduate/ITI",
        "valid_years": range(2010, 2035)
    },
    "BEML Recruitment (Technical / Management) - Variant 3": {
        "department": "BEML",
        "level": "National",
        "eligibility": "Graduate/ITI",
        "valid_years": range(2010, 2035)
    },
    "BEML Recruitment (Technical / Management) - Variant 4": {
        "department": "BEML",
        "level": "National",
        "eligibility": "Graduate/ITI",
        "valid_years": range(2010, 2035)
    },
    "BEML Recruitment (Technical / Management) - Variant 5": {
        "department": "BEML",
        "level": "National",
        "eligibility": "Graduate/ITI",
        "valid_years": range(2010, 2035)
    },
    "BHEL Recruitment (Executive / Technician)": {
        "department": "BHEL",
        "level": "National",
        "eligibility": "Engineering/ITI",
        "valid_years": range(2010, 2035)
    },
    "BSF Recruitment (Constable / SI)": {
        "department": "BSF",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "BSNL / MTNL Technical Recruitment": {
        "department": "BSNL/MTNL",
        "level": "National/State",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Backend Development": {
        "department": "Domain-Based",
        "level": "National",
        "eligibility": "APIs & Server Logic",
        "valid_years": range(2015, 2035)
    },
    "Backtracking": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Bihar - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State PSC Combined Services": {
        "department": "State Public Service Commission (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State Police Constable Recruitment": {
        "department": "State Police Department (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Bihar - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Bihar)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Binary Search": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Binary Search Trees (BST)": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "CISF Recruitment (Assistants / SI)": {
        "department": "CISF",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "CPWD JE / AE": {
        "department": "CPWD",
        "level": "Central",
        "eligibility": "Diploma/Engineering",
        "valid_years": range(2010, 2035)
    },
    "CRPF Recruitment (Constable / SI)": {
        "department": "CRPF",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "CTET": {
        "department": "CBSE",
        "level": "National",
        "eligibility": "Graduate/12th",
        "valid_years": range(2010, 2035)
    },
    "Cantonment Board Recruitment (Clerk / Skilled Posts)": {
        "department": "Cantonment Boards",
        "level": "Local/National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Central Armed Police Forces (Assistant Commandant - CAPF AC)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "Central Government Medical College / Hospital Recruitment - Variant 1": {
        "department": "Central Medical Institutes",
        "level": "National",
        "eligibility": "Medical",
        "valid_years": range(2010, 2035)
    },
    "Central Government Medical College / Hospital Recruitment - Variant 2": {
        "department": "Central Medical Institutes",
        "level": "National",
        "eligibility": "Medical",
        "valid_years": range(2010, 2035)
    },
    "Central Government Medical College / Hospital Recruitment - Variant 3": {
        "department": "Central Medical Institutes",
        "level": "National",
        "eligibility": "Medical",
        "valid_years": range(2010, 2035)
    },
    "Central Government Medical College / Hospital Recruitment - Variant 4": {
        "department": "Central Medical Institutes",
        "level": "National",
        "eligibility": "Medical",
        "valid_years": range(2010, 2035)
    },
    "Central Government Medical College / Hospital Recruitment - Variant 5": {
        "department": "Central Medical Institutes",
        "level": "National",
        "eligibility": "Medical",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State PSC Combined Services": {
        "department": "State Public Service Commission (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State Police Constable Recruitment": {
        "department": "State Police Department (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Chhattisgarh - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Chhattisgarh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Civil Services Examination (CSE)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "Cloud & DevOps": {
        "department": "Domain-Based",
        "level": "National",
        "eligibility": "Infrastructure & CI/CD",
        "valid_years": range(2015, 2035)
    },
    "Coal India Recruitment": {
        "department": "Coal India",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "Coast Guard Navik / Yantrik": {
        "department": "Indian Coast Guard",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2015, 2035)
    },
    "Combined Defence Services (CDS)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate/12th",
        "valid_years": range(2015, 2035)
    },
    "Combined Geo-Scientist Examination": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "Combined Medical Services (CMS)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate (Medical)",
        "valid_years": range(2015, 2035)
    },
    "Core Programming": {
        "department": "Domain-Based",
        "level": "National",
        "eligibility": "Language Syntax & OOP",
        "valid_years": range(2015, 2035)
    },
    "DMRC (Delhi Metro) Technician / JE": {
        "department": "DMRC",
        "level": "Urban/State",
        "eligibility": "ITI/Diploma",
        "valid_years": range(2010, 2035)
    },
    "DRDO Scientist / Technician Recruitment": {
        "department": "DRDO",
        "level": "National",
        "eligibility": "Engineering/Science",
        "valid_years": range(2010, 2035)
    },
    "DSSSB Teaching Posts": {
        "department": "DSSSB",
        "level": "State/National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Databases": {
        "department": "Domain-Based",
        "level": "National",
        "eligibility": "SQL & Schema Design",
        "valid_years": range(2015, 2035)
    },
    "Debugging & Optimization": {
        "department": "Domain-Based",
        "level": "National",
        "eligibility": "Testing & Profiling",
        "valid_years": range(2015, 2035)
    },
    "District Judge Recruitment": {
        "department": "State High Courts",
        "level": "State",
        "eligibility": "Law Graduate",
        "valid_years": range(2010, 2035)
    },
    "Dynamic Programming": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "EPFO Enforcement Officer/Accounts Officer": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "ESIC Staff Nurse / Paramedical": {
        "department": "ESIC",
        "level": "National/State",
        "eligibility": "Nursing/Paramedical",
        "valid_years": range(2010, 2035)
    },
    "EXIM Bank Recruitment": {
        "department": "EXIM Bank",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Engineering Services Examination (ESE/IES)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Engineering Degree",
        "valid_years": range(2015, 2035)
    },
    "GAIL Executive Trainee Recruitment - Variant 1": {
        "department": "GAIL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "GAIL Executive Trainee Recruitment - Variant 2": {
        "department": "GAIL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "GAIL Executive Trainee Recruitment - Variant 3": {
        "department": "GAIL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "GAIL Executive Trainee Recruitment - Variant 4": {
        "department": "GAIL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "GAIL Executive Trainee Recruitment - Variant 5": {
        "department": "GAIL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "GIC Assistant Manager (AM)": {
        "department": "GIC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Goa - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State PSC Combined Services": {
        "department": "State Public Service Commission (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State Police Constable Recruitment": {
        "department": "State Police Department (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Goa - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Goa)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Graphs": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Greedy Algorithms": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Gujarat - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State PSC Combined Services": {
        "department": "State Public Service Commission (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State Police Constable Recruitment": {
        "department": "State Police Department (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Gujarat - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Gujarat)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "HAL Recruitment": {
        "department": "HAL",
        "level": "National",
        "eligibility": "Engineering/ITI",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State PSC Combined Services": {
        "department": "State Public Service Commission (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State Police Constable Recruitment": {
        "department": "State Police Department (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Haryana - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Haryana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Hashing": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Heap / Priority Queue": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "High Court Clerk / Junior Assistant": {
        "department": "State High Courts",
        "level": "State",
        "eligibility": "12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State PSC Combined Services": {
        "department": "State Public Service Commission (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State Police Constable Recruitment": {
        "department": "State Police Department (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Himachal Pradesh - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Himachal Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "IBPS Clerk": {
        "department": "IBPS",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2034)
    },
    "IBPS PO": {
        "department": "IBPS",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2034)
    },
    "IBPS RRB Office Assistant (Clerk)": {
        "department": "IBPS",
        "level": "National",
        "eligibility": "12th/Graduate",
        "valid_years": range(2015, 2034)
    },
    "IBPS RRB Officer Scale I (PO)": {
        "department": "IBPS",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2034)
    },
    "IBPS Specialist Officer (SO)": {
        "department": "IBPS",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "IOCL Recruitment (Executive / Technical)": {
        "department": "IOCL",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "IPPB / Regional Rural Bank (RBI-linked) Recruitment - Variant 1": {
        "department": "IPPB / RRBs",
        "level": "National/Regional",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "IPPB / Regional Rural Bank (RBI-linked) Recruitment - Variant 2": {
        "department": "IPPB / RRBs",
        "level": "National/Regional",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "IPPB / Regional Rural Bank (RBI-linked) Recruitment - Variant 3": {
        "department": "IPPB / RRBs",
        "level": "National/Regional",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "IPPB / Regional Rural Bank (RBI-linked) Recruitment - Variant 4": {
        "department": "IPPB / RRBs",
        "level": "National/Regional",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "IPPB / Regional Rural Bank (RBI-linked) Recruitment - Variant 5": {
        "department": "IPPB / RRBs",
        "level": "National/Regional",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "ISRO Scientist / Technical Recruitment": {
        "department": "ISRO",
        "level": "National",
        "eligibility": "Engineering/Science",
        "valid_years": range(2010, 2035)
    },
    "ITBP Recruitment": {
        "department": "ITBP",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "India Post GDS / Postman / Mail Guard Recruitment": {
        "department": "India Post",
        "level": "National",
        "eligibility": "10th/12th",
        "valid_years": range(2010, 2035)
    },
    "Indian Army Agniveer": {
        "department": "Indian Army",
        "level": "National",
        "eligibility": "10th/12th",
        "valid_years": range(2022, 2035)
    },
    "Indian Economic Service / Indian Statistical Service (IES/ISS)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Postgraduate",
        "valid_years": range(2015, 2035)
    },
    "Indian Forest Service (IFoS)": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "Indian Navy AA": {
        "department": "Indian Navy",
        "level": "National",
        "eligibility": "12th",
        "valid_years": range(2015, 2035)
    },
    "Indian Navy SSR": {
        "department": "Indian Navy",
        "level": "National",
        "eligibility": "12th",
        "valid_years": range(2010, 2035)
    },
    "JEE Advanced": {
        "department": "JEE",
        "level": "National",
        "eligibility": "Graduate (Science / Engineering background preferred)",
        "valid_years": range(2010, 2035)
    },
    "JEE Main": {
        "department": "JEE",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2036)
    },
    "Jharkhand - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State PSC Combined Services": {
        "department": "State Public Service Commission (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State Police Constable Recruitment": {
        "department": "State Police Department (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Jharkhand - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Jharkhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "KVS Recruitment PRT/TGT/PGT": {
        "department": "KVS",
        "level": "National",
        "eligibility": "Graduate/B.Ed",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State PSC Combined Services": {
        "department": "State Public Service Commission (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State Police Constable Recruitment": {
        "department": "State Police Department (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Karnataka - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Karnataka)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State PSC Combined Services": {
        "department": "State Public Service Commission (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State Police Constable Recruitment": {
        "department": "State Police Department (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Kerala - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Kerala)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "LIC AAO": {
        "department": "LIC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "LIC ADO": {
        "department": "LIC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Linked Lists": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Lower Judiciary (Judicial Magistrate)": {
        "department": "State Judiciary",
        "level": "State",
        "eligibility": "Law Graduate",
        "valid_years": range(2010, 2035)
    },
    "MRPL / ONGC / IOCL - Additional Specific Notices - Variant 1": {
        "department": "Various PSUs",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "MRPL / ONGC / IOCL - Additional Specific Notices - Variant 2": {
        "department": "Various PSUs",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "MRPL / ONGC / IOCL - Additional Specific Notices - Variant 3": {
        "department": "Various PSUs",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "MRPL / ONGC / IOCL - Additional Specific Notices - Variant 4": {
        "department": "Various PSUs",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "MRPL / ONGC / IOCL - Additional Specific Notices - Variant 5": {
        "department": "Various PSUs",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State PSC Combined Services": {
        "department": "State Public Service Commission (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State Police Constable Recruitment": {
        "department": "State Police Department (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Madhya Pradesh - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Madhya Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State PSC Combined Services": {
        "department": "State Public Service Commission (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State Police Constable Recruitment": {
        "department": "State Police Department (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Maharashtra - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Maharashtra)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State PSC Combined Services": {
        "department": "State Public Service Commission (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State Police Constable Recruitment": {
        "department": "State Police Department (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Manipur - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Manipur)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State PSC Combined Services": {
        "department": "State Public Service Commission (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State Police Constable Recruitment": {
        "department": "State Police Department (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Meghalaya - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Meghalaya)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Military Nursing Service (MNS)": {
        "department": "DGMS / Armed Forces",
        "level": "National",
        "eligibility": "Nursing Qualification",
        "valid_years": range(2015, 2035)
    },
    "Mizoram - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State PSC Combined Services": {
        "department": "State Public Service Commission (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State Police Constable Recruitment": {
        "department": "State Police Department (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Mizoram - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Mizoram)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Municipal Corporation / Urban Local Body Recruitments": {
        "department": "Municipal Corporations",
        "level": "Local/State",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "NABARD Grade A": {
        "department": "NABARD",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "NABARD Grade B": {
        "department": "NABARD",
        "level": "National",
        "eligibility": "Postgraduate",
        "valid_years": range(2010, 2035)
    },
    "NEET MDS": {
        "department": "NEET ",
        "level": "National",
        "eligibility": "12th Pass",
        "valid_years": range(2017, 2035)
    },
    "NEET PG": {
        "department": "NEET ",
        "level": "National",
        "eligibility": "Graduate / 12th (depending on academy)",
        "valid_years": range(2012, 2035)
    },
    "NEET SS": {
        "department": "NEET ",
        "level": "National",
        "eligibility": "Graduate (Medical – MBBS)",
        "valid_years": range(2017, 2035)
    },
    "NEET UG": {
        "department": "NEET ",
        "level": "National",
        "eligibility": "Engineering Degree",
        "valid_years": range(2010, 2036)
    },
    "NIACL AO": {
        "department": "New India Assurance",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "NIACL Assistant": {
        "department": "New India Assurance",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "NIC / MeitY Technical Hiring": {
        "department": "National Informatics Centre (NIC)",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "NPCIL Recruitment": {
        "department": "NPCIL",
        "level": "National",
        "eligibility": "Engineering/Science",
        "valid_years": range(2010, 2035)
    },
    "NTPC Executive Trainee": {
        "department": "NTPC",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "NVS Recruitment": {
        "department": "NVS",
        "level": "National",
        "eligibility": "Graduate/B.Ed",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State PSC Combined Services": {
        "department": "State Public Service Commission (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State Police Constable Recruitment": {
        "department": "State Police Department (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Nagaland - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Nagaland)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "National Cadet Corps (NCC) / Sports Authority recruitments - Variant 1": {
        "department": "SAI / NCC",
        "level": "National/State",
        "eligibility": "Varies",
        "valid_years": range(2010, 2035)
    },
    "National Cadet Corps (NCC) / Sports Authority recruitments - Variant 2": {
        "department": "SAI / NCC",
        "level": "National/State",
        "eligibility": "Varies",
        "valid_years": range(2010, 2035)
    },
    "National Cadet Corps (NCC) / Sports Authority recruitments - Variant 3": {
        "department": "SAI / NCC",
        "level": "National/State",
        "eligibility": "Varies",
        "valid_years": range(2010, 2035)
    },
    "National Cadet Corps (NCC) / Sports Authority recruitments - Variant 4": {
        "department": "SAI / NCC",
        "level": "National/State",
        "eligibility": "Varies",
        "valid_years": range(2010, 2035)
    },
    "National Defence Academy (NDA) & NA": {
        "department": "UPSC",
        "level": "National",
        "eligibility": "12th",
        "valid_years": range(2015, 2035)
    },
    "ONGC Graduate Trainee / GATE-based Recruitment": {
        "department": "ONGC",
        "level": "National",
        "eligibility": "Engineering/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State PSC Combined Services": {
        "department": "State Public Service Commission (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State Police Constable Recruitment": {
        "department": "State Police Department (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Odisha - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Odisha)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Pharmacist / Lab Technician Recruitment": {
        "department": "State/Central Boards",
        "level": "State/National",
        "eligibility": "Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Power Grid Recruitment": {
        "department": "Power Grid",
        "level": "National",
        "eligibility": "Graduate/Engineering",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State PSC Combined Services": {
        "department": "State Public Service Commission (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State Police Constable Recruitment": {
        "department": "State Police Department (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Punjab - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Punjab)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Queue / Deque": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "RBI Assistant": {
        "department": "RBI",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "RBI Grade B": {
        "department": "Reserve Bank of India (RBI)",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2012, 2035)
    },
    "RPF Constable": {
        "department": "Railway Protection Force (RPF)",
        "level": "National",
        "eligibility": "10th/12th",
        "valid_years": range(2015, 2035)
    },
    "RPF Sub-Inspector (SI)": {
        "department": "RPF",
        "level": "National",
        "eligibility": "12th/Graduate",
        "valid_years": range(2015, 2035)
    },
    "RRB ALP": {
        "department": "RRB",
        "level": "National",
        "eligibility": "12th/Diploma",
        "valid_years": range(2015, 2035)
    },
    "RRB Group D": {
        "department": "RRB",
        "level": "National",
        "eligibility": "10th",
        "valid_years": range(2015, 2035)
    },
    "RRB JE": {
        "department": "RRB",
        "level": "National",
        "eligibility": "Diploma/Engineering",
        "valid_years": range(2015, 2035)
    },
    "RRB NTPC": {
        "department": "Railway Recruitment Board (RRB)",
        "level": "National",
        "eligibility": "12th/Graduate",
        "valid_years": range(2015, 2035)
    },
    "RRB Technician": {
        "department": "RRB",
        "level": "National",
        "eligibility": "ITI/Diploma",
        "valid_years": range(2015, 2035)
    },
    "Railway Zone-specific Technician/Technical Assistant (Zone variant) - Variant 1": {
        "department": "Railway Zone",
        "level": "National",
        "eligibility": "Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Railway Zone-specific Technician/Technical Assistant (Zone variant) - Variant 2": {
        "department": "Railway Zone",
        "level": "National",
        "eligibility": "Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Railway Zone-specific Technician/Technical Assistant (Zone variant) - Variant 3": {
        "department": "Railway Zone",
        "level": "National",
        "eligibility": "Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Railway Zone-specific Technician/Technical Assistant (Zone variant) - Variant 4": {
        "department": "Railway Zone",
        "level": "National",
        "eligibility": "Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Railway Zone-specific Technician/Technical Assistant (Zone variant) - Variant 5": {
        "department": "Railway Zone",
        "level": "National",
        "eligibility": "Diploma/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State PSC Combined Services": {
        "department": "State Public Service Commission (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State Police Constable Recruitment": {
        "department": "State Police Department (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Rajasthan - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Rajasthan)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Recursion": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "SAIL Recruitment": {
        "department": "SAIL",
        "level": "National",
        "eligibility": "Graduate/ITI/Engineering",
        "valid_years": range(2010, 2035)
    },
    "SBI Clerk": {
        "department": "SBI",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2034)
    },
    "SBI PO": {
        "department": "State Bank of India (SBI)",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2034)
    },
    "SIDBI Grade A": {
        "department": "SIDBI",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "SSB / Assam Rifles Recruitment": {
        "department": "SSB / Assam Rifles",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2036)
    },
    "SSC CHSL DEO (Data Entry Operator)": {
        "department": "SSC",
        "level": "National",
        "eligibility": "12th",
        "valid_years": range(2015, 2035)
    },
    "SSC CPO (SI)": {
        "department": "SSC",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "SSC Combined Graduate Level (CGL)": {
        "department": "Staff Selection Commission (SSC)",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "SSC Combined Higher Secondary Level (CHSL)": {
        "department": "SSC",
        "level": "National",
        "eligibility": "12th",
        "valid_years": range(2015, 2035)
    },
    "SSC GD Constable": {
        "department": "SSC",
        "level": "National",
        "eligibility": "10th",
        "valid_years": range(2015, 2035)
    },
    "SSC Junior Engineer (JE)": {
        "department": "SSC",
        "level": "National",
        "eligibility": "Diploma/Engineering",
        "valid_years": range(2015, 2035)
    },
    "SSC Multi Tasking Staff (MTS)": {
        "department": "SSC",
        "level": "National",
        "eligibility": "10th",
        "valid_years": range(2015, 2035)
    },
    "SSC Selection Post (Phase-wise)": {
        "department": "SSC",
        "level": "National",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2015, 2035)
    },
    "SSC Stenographer Grade C & D": {
        "department": "SSC",
        "level": "National",
        "eligibility": "12th/10th",
        "valid_years": range(2015, 2035)
    },
    "Sikkim - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State PSC Combined Services": {
        "department": "State Public Service Commission (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State Police Constable Recruitment": {
        "department": "State Police Department (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Sikkim - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Sikkim)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Specialized Insurance Officer Exams (various) - Variant 1": {
        "department": "Insurance Companies",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Specialized Insurance Officer Exams (various) - Variant 2": {
        "department": "Insurance Companies",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Specialized Insurance Officer Exams (various) - Variant 3": {
        "department": "Insurance Companies",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Specialized Insurance Officer Exams (various) - Variant 4": {
        "department": "Insurance Companies",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Specialized Insurance Officer Exams (various) - Variant 5": {
        "department": "Insurance Companies",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Stack": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "State Cooperative Bank Recruitment (clerical / officer) - Variant 1": {
        "department": "State Cooperative Banks",
        "level": "State",
        "eligibility": "Graduate/12th",
        "valid_years": range(2010, 2035)
    },
    "State Cooperative Bank Recruitment (clerical / officer) - Variant 2": {
        "department": "State Cooperative Banks",
        "level": "State",
        "eligibility": "Graduate/12th",
        "valid_years": range(2010, 2035)
    },
    "State Cooperative Bank Recruitment (clerical / officer) - Variant 3": {
        "department": "State Cooperative Banks",
        "level": "State",
        "eligibility": "Graduate/12th",
        "valid_years": range(2010, 2035)
    },
    "State Cooperative Bank Recruitment (clerical / officer) - Variant 4": {
        "department": "State Cooperative Banks",
        "level": "State",
        "eligibility": "Graduate/12th",
        "valid_years": range(2010, 2035)
    },
    "State Cooperative Bank Recruitment (clerical / officer) - Variant 5": {
        "department": "State Cooperative Banks",
        "level": "State",
        "eligibility": "Graduate/12th",
        "valid_years": range(2010, 2035)
    },
    "State Fisheries / Agriculture Department Recruitment (All States)": {
        "department": "State Agriculture Dept.",
        "level": "State",
        "eligibility": "Graduate/Diploma",
        "valid_years": range(2010, 2035)
    },
    "State Forest Guard / Ranger Recruitment (All States)": {
        "department": "State Forest Dept.",
        "level": "State",
        "eligibility": "10th/12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "State Judicial Services (Civil Judge)": {
        "department": "State High Courts / PSC",
        "level": "State",
        "eligibility": "Law Graduate",
        "valid_years": range(2010, 2035)
    },
    "State Lecturer / Assistant Professor Recruitment (All States)": {
        "department": "State Higher Education Department",
        "level": "State",
        "eligibility": "Postgraduate / PhD",
        "valid_years": range(2010, 2035)
    },
    "State Medical Officer / Medical Officer (State Recruits)": {
        "department": "State Health Dept.",
        "level": "State",
        "eligibility": "MBBS/Medical",
        "valid_years": range(2010, 2035)
    },
    "State TET (All States Individual)": {
        "department": "State Education Boards",
        "level": "State",
        "eligibility": "12th/Graduate",
        "valid_years": range(2010, 2035)
    },
    "Strings": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Supreme Court / National Judicial Service Office - Junior Assistant - Variant 1": {
        "department": "Supreme Court / NJA",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Supreme Court / National Judicial Service Office - Junior Assistant - Variant 2": {
        "department": "Supreme Court / NJA",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Supreme Court / National Judicial Service Office - Junior Assistant - Variant 3": {
        "department": "Supreme Court / NJA",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Supreme Court / National Judicial Service Office - Junior Assistant - Variant 4": {
        "department": "Supreme Court / NJA",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Supreme Court / National Judicial Service Office - Junior Assistant - Variant 5": {
        "department": "Supreme Court / NJA",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "System Design": {
        "department": "Domain-Based",
        "level": "National",
        "eligibility": "Scalable Architecture",
        "valid_years": range(2015, 2035)
    },
    "Tamil Nadu - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State PSC Combined Services": {
        "department": "State Public Service Commission (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State Police Constable Recruitment": {
        "department": "State Police Department (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tamil Nadu - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Tamil Nadu)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State PSC Combined Services": {
        "department": "State Public Service Commission (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State Police Constable Recruitment": {
        "department": "State Police Department (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Telangana - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Telangana)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Territorial Army Officer": {
        "department": "Indian Army",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2015, 2035)
    },
    "Trees": {
        "department": "DSA — Data Structures & Algorithms",
        "level": "National",
        "eligibility": "NO Sub-Domain",
        "valid_years": range(2015, 2035)
    },
    "Tripura - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State PSC Combined Services": {
        "department": "State Public Service Commission (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State Police Constable Recruitment": {
        "department": "State Police Department (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Tripura - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Tripura)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "UGC NET": {
        "department": "UGC / NTA",
        "level": "National",
        "eligibility": "Postgraduate",
        "valid_years": range(2010, 2035)
    },
    "UIIC AO": {
        "department": "United India Insurance Company",
        "level": "National",
        "eligibility": "Graduate",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State PSC Combined Services": {
        "department": "State Public Service Commission (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State Police Constable Recruitment": {
        "department": "State Police Department (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttar Pradesh - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Uttar Pradesh)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State PSC Combined Services": {
        "department": "State Public Service Commission (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State Police Constable Recruitment": {
        "department": "State Police Department (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "Uttarakhand - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (Uttarakhand)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State Judiciary / Civil Judge Recruitment": {
        "department": "State High Court (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State PSC Assistant Engineer (AE/JE)": {
        "department": "State Public Service Commission (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State PSC Civil Services (State)": {
        "department": "State Public Service Commission (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State PSC Combined Services": {
        "department": "State Public Service Commission (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State PSC Group 2 / Group B Posts": {
        "department": "State Public Service Commission (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State PSC Police Services / SI": {
        "department": "State Public Service Commission / State Police (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State Police Constable Recruitment": {
        "department": "State Police Department (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
    "West Bengal - State TET (Teacher Eligibility Test)": {
        "department": "State Education Board (West Bengal)",
        "level": "State",
        "eligibility": "Varies (10th/12th/Graduate/Law/Engineering)",
        "valid_years": range(2010, 2035)
    },
}
