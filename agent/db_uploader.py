# agent/db_uploader.py

import os
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    """Convert 'Exam Name 2024' -> 'exam_name_2024'"""
    if not text:
        return "unknown_exam"
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

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
        collection_name = slugify(exam_type)
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
