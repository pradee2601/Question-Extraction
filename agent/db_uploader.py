# agent/db_uploader.py

import os
import json
import logging
import re
from pathlib import Path
from utils.collection_mapper import get_collection_name

logger = logging.getLogger(__name__)

def upload_to_db(questions: list) -> dict:
    """
    Upload questions to MongoDB, grouped into collections by exam_type.
    Database: goverment_qb
    Collection: slugified(exam_type)
    """
    if not questions:
        return {"success": True, "uploaded_count": 0}

    # Group questions by their slugified exam_type
    grouped_questions = {}
    for q in questions:
        exam_type = q.get("exam_type", "Unknown Exam")
        collection_name = get_collection_name(exam_type)
        if collection_name not in grouped_questions:
            grouped_questions[collection_name] = []
        
        # Clean the question (remove internal _id if it exists as a dict/oid)
        clean_q = {k: v for k, v in q.items() if k != "_id"}
        grouped_questions[collection_name].append(clean_q)

    # Database connection
    mongo_uri = os.environ.get("MONGODB_URI")
    
    if mongo_uri:
        try:
            from pymongo import MongoClient
            client = MongoClient(mongo_uri)
            db = client["goverment_qb"]
            
            total_uploaded = 0
            for coll_name, docs in grouped_questions.items():
                collection = db[coll_name]
                # Use insert_many for efficiency
                result = collection.insert_many(docs)
                total_uploaded += len(result.inserted_ids)
                logger.info(f"Uploaded {len(result.inserted_ids)} questions to collection: {coll_name}")
                
                # --- AUTO-SYNC WITH DASHBOARD ---
                try:
                    update_dashboard_metadata(db, coll_name, docs)
                except Exception as sync_err:
                    logger.warning(f"Dashboard metadata sync failed: {sync_err}")
            
            return {"success": True, "uploaded_count": total_uploaded}
        except ImportError:
            logger.error("pymongo not installed. Please run 'pip install pymongo'")
            return {"success": False, "uploaded_count": 0, "error": "pymongo not installed"}
        except Exception as e:
            logger.error(f"MongoDB upload failed: {e}")
            return {"success": False, "uploaded_count": 0, "error": str(e)}
    else:
        # FALLBACK: Local file simulation if no MONGODB_URI is provided
        logger.warning("MONGODB_URI not found in .env. Simulating upload locally.")
        output_base = Path("agent_output/local_db")
        output_base.mkdir(parents=True, exist_ok=True)
        
        total_saved = 0
        for coll_name, docs in grouped_questions.items():
            local_file = output_base / f"{coll_name}.json"
            existing = []
            if local_file.exists():
                with open(local_file, "r", encoding="utf-8") as f:
                    try:
                        existing = json.load(f)
                    except:
                        existing = []
            
            existing.extend(docs)
            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            total_saved += len(docs)
            
        return {"success": True, "uploaded_count": total_saved, "simulated": True}

def update_dashboard_metadata(db, collection_name, docs):
    """Updates the 'topics' collection with new counts and year ranges."""
    if not docs: return
    
    exam_name = docs[0].get("exam_type", collection_name.replace("_", " ").title())
    category = docs[0].get("department", docs[0].get("category", "General"))
    
    # Calculate stats from docs
    years = [str(d.get("year", "")) for d in docs if d.get("year")]
    if not years: return
    
    min_year = min(years)
    max_year = max(years)
    year_range = f"{min_year}-{max_year}" if min_year != max_year else min_year
    
    # Get current total count from collection
    total_q = db[collection_name].count_documents({})
    
    # Update or Insert into 'topics' collection
    topics = db["topics"]
    
    # Try to find existing entry
    existing = topics.find_one({"$or": [{"exam_name": exam_name}, {"collection_name": collection_name}]})
    
    if existing:
        topics.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "question_count": f"{total_q:,}",
                "year_range": year_range
            }}
        )
        logger.info(f"Updated dashboard metadata for {exam_name}")
    else:
        # Create new entry with sensible defaults
        new_topic = {
            "track_name": "Govt Exams Track", # Default
            "category": category,
            "exam_name": exam_name,
            "conducting_body": category,
            "level": docs[0].get("level", "National"),
            "eligibility": docs[0].get("eligibility", "Graduate"),
            "question_count": f"{total_q:,}",
            "year_range": year_range,
            "collection_name": collection_name, # Extra field for mapping
            "sub_topic": []
        }
        topics.insert_one(new_topic)
        logger.info(f"Created new dashboard entry for {exam_name}")
