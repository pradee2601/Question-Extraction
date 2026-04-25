import re

def get_collection_name(exam_type: str) -> str:
    """
    Maps an exam_type/department to a MongoDB collection name.
    Matches the logic in Course-Explorer/server.js:mapToCollection.
    """
    if not exam_type:
        return "topics"
        
    d = exam_type.lower()
    
    # Exact/Specific matches for UPSC sub-exams
    if any(k in d for k in ["medical services", "combined medical services", "cms"]):
        return "upsc_cms"
    if any(k in d for k in ["civil services examination", "upsc cse"]) or d == "cse":
        return "upsc_cse"
    if any(k in d for k in ["combined geo-scientist", "cgse"]):
        return "combined_geo_scientist"
    if any(k in d for k in ["epfo enforcement officer", "epfo ao"]):
        return "epfo_enforcement_officer"
    if any(k in d for k in ["economic service", "statistical service", "ies/iss"]):
        return "upsc_ies"
    if any(k in d for k in ["engineering services", "ese", "ies"]):
        return "upsc_ese"
    if any(k in d for k in ["indian forest service", "ifos"]):
        return "upsc_ifos"
    if any(k in d for k in ["combined defence services", "cds"]):
        return "upsc_cds"
    if any(k in d for k in ["national defence academy", "nda"]):
        return "upsc_nda"
    if "central armed police forces" in d and "assistant commandant" in d:
        return "upsc_capf_ac"
    if any(k in d for k in ["upsc capf", "capf"]):
        return "upsc_capf_ac"
        
    # General UPSC fallback
    if any(k in d for k in ["upsc", "civil services", "cse", "forest service", "ifos", "defence service", "cds", "defence academy", "nda", "economic service", "epfo", "central armed police forces", "geo-scientist"]):
        return "upsc"
        
    # Precise Banking Matches
    if any(k in d for k in ["office assistant", "rrb clerk", "rrb po", "officer scale i"]):
        if any(k in d for k in ["clerk", "assistant"]):
            return "ibps_rrb_clerk"
        if any(k in d for k in ["po", "scale i"]):
            return "ibps_rrb_po"
            
    if any(k in d for k in ["specialist officer", "so"]):
        return "ibps_so"
    if "sbi clerk" in d:
        return "sbi_clerk"
    if "sbi po" in d:
        return "sbi_po"
    if "ibps clerk" in d:
        return "ibps_clerk"
    if "ibps po" in d:
        return "ibps_po"
    if "rbi grade b" in d:
        return "rbi_grade_b"
    if "rbi assistant" in d:
        return "rbi_assistant"
    if "nabard grade a" in d:
        return "nabard_grade_a"
    if "nabard grade b" in d:
        return "nabard_grade_b"
    if "sidbi grade a" in d:
        return "sidbi_grade_a"
    if "exim bank recruitment" in d:
        return "exim_bank_recruitment"
    if "ippb" in d and ("regional rural bank" in d or "rbi-linked" in d):
        return "ippb_rbi_linked"
        
    if any(k in d for k in ["bank", "sbi", "ibps", "rbi"]):
        return "bank_exams"
        
    # Railways
    if any(k in d for k in ["railway", "rrb", "ntpc", "group d", "alp", "rpf"]):
        return "railways"
        
    # Medical
    if "neet mds" in d: return "neet_mds"
    if "neet ss" in d: return "neet_ss"
    if "neet pg" in d: return "neet_pg"
    if "neet" in d: return "neet_ug"
    
    # Defence
    if any(k in d for k in ["afcat", "defence_afcad", "afcad"]):
        return "defence_afcad"
    if "agniveer" in d: return "indian_army_agniveer"
    if any(k in d for k in ["navy ssr", "navy aa"]):
        return "indian_navy_ssr"
    if "coast guard" in d: return "coast_guard"
    if "territorial army" in d: return "territorial_army_officer"
    if any(k in d for k in ["defence", "army", "navy", "air force", "military"]):
        return "defence"
        
    # JEE
    if "jee advance" in d: return "jee_advance"
    if "jee" in d: return "jee_main"
    
    # Tech / Programming fallback
    tech_words = [
        "arrays", "strings", "hashing", "linked lists", "stack", "queue", "binary search", 
        "trees", "graphs", "recursion", "backtracking", "dynamic programming", "greedy", 
        "heap", "priority queue", "ai", "machine learning", "web dev", "software engineering", 
        "operating systems", "database", "dsa", "c++", "java", "python", "javascript",
        "programming", "core-programming", "domain-based", "development", "backend", 
        "frontend", "system design", "cloud", "devops", "debugging", "optimization", "coding"
    ]
    if any(w in d for w in tech_words) or "data structure" in d or "algorithm" in d:
        return "coding_problems"

    # --- SSC Exams ---
    if any(k in d for k in ["ssc cgl", "ssc chsl", "ssc mts", "ssc cpo", "ssc gd", "ssc stenographer", "ssc je"]):
        return "ssc"
    if "ssc" in d:
        return "ssc"

    # --- State PSC & State Exams (Comprehensive) ---
    states = [
        "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat", 
        "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh", 
        "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab", 
        "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", 
        "uttarakhand", "west bengal", "delhi", "jammu", "kashmir", "ladakh", "puducherry"
    ]
    if any(state in d for state in states):
        if any(k in d for k in ["psc", "public service commission", "civil services", "combined services", "state services"]):
            return "state_psc_state_exams"
        if any(k in d for k in ["police", "constable", "sub inspector", "si", "jail warder"]):
            return "central_police"
        if any(k in d for k in ["judiciary", "civil judge", "district judge"]):
            return "judiciary"
        if any(k in d for k in ["tet", "teacher eligibility test", "teaching"]):
            return "teaching"
        if any(k in d for k in ["assistant engineer", "ae", "je", "junior engineer"]):
            return "technical"
        # Fallback for any state exam not specifically caught
        return "state_generic"

    # --- Insurance Exams ---
    if any(k in d for k in ["lic ", "gic ", "niacl", "nicl", "uiic", "oicl", "irda"]):
        return "insurance"
        
    # --- Teaching Exams (General) ---
    if any(k in d for k in ["ctet", "kvs", "nvs", "dsssb", "ugc net", "csir net", "set exam"]):
        return "teaching"
        
    # --- PSU Exams ---
    psus = ["ntpc", "ongc", "sail", "bhel", "gail", "hpcl", "bpcl", "iocl", "hal", "bel", "coal india"]
    if any(psu in d for psu in psus) or "psu" in d:
        return "psu"
        
    # --- Healthcare ---
    if any(k in d for k in ["nurse", "nursing", "anm", "gnm", "pharmacist", "lab technician", "medical officer"]):
        return "healthcare"

    # --- Default slugification if no match ---
    slug = re.sub(r'[^a-z0-9]+', '_', d).strip('_')
    return slug or "topics"
