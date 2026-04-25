import os
import sys
import json
import time
import argparse
import re
from pathlib import Path
from rag.exam_extractor import ExamExtractor
from utils.question_store import (
    detect_category, append_questions_to_file, append_passage_exam_to_file, 
    EXAM_CATEGORIES, SLUG_ORDER, DOCS_DIR
)

import subprocess
from config import Config
from utils.logger import setup_logger
from utils.helpers import LLMTracker

logger = setup_logger(__name__)

def extract_year(text: str) -> int:
    """Extract a 4-digit year from text, default to 9999 if not found."""
    match = re.search(r'\b(19[9]\d|20[0-3]\d)\b', text)
    return int(match.group(1)) if match else 9999

def slugify(text: str) -> str:
    """Create a URL/file-friendly version of a string."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def get_job_batch(folder: Path, processed_files: dict, batch_size: int = 5) -> list[Path]:
    """Get the next batch of 5 unprocessed PDFs from the folder."""
    all_pdfs = sorted(list(folder.glob("*.pdf")))
    batch = []
    for pdf in all_pdfs:
        file_key = f"{pdf.name}_{pdf.stat().st_size}"
        if file_key not in processed_files:
            batch.append(pdf)
            if len(batch) >= batch_size:
                break
    return batch

def process_folder_structure(root_path: str, mode: str = "extract", fallback_category: str = "other"):
    """
    Implements the requested flow:
    1. Identify if root is a single exam or multi-exam folder.
    2. Process exams one by one.
    3. Inside each exam, process year subfolders one by one.
    4. Save to exam-specific JSON files (e.g. 'ibps_po_2025.json').
    """
    root = Path(root_path)
    if not root.exists() or not root.is_dir():
        logger.error(f"Invalid root path: {root_path}")
        return

    # 1. Broad scan of subfolders to determine hierarchy
    subfolders = [d for d in root.iterdir() if d.is_dir()]
    
    # Check if root contains year folders directly (Single Exam)
    is_single_exam = any(extract_year(d.name) != 9999 for d in subfolders)
    
    exam_tasks = [] # List of (exam_folder, [year_folders])
    
    if is_single_exam:
        subfolders.sort(key=lambda d: extract_year(d.name))
        exam_tasks.append((root, subfolders))
    else:
        # Each subfolder is treated as an exam
        for exam_folder in sorted(subfolders):
            years = [d for d in exam_folder.iterdir() if d.is_dir()]
            if years:
                years.sort(key=lambda d: extract_year(d.name))
                exam_tasks.append((exam_folder, years))
            elif list(exam_folder.glob("*.pdf")):
                # No subfolders but has PDFs directly
                exam_tasks.append((exam_folder, [exam_folder]))

    if not exam_tasks:
        logger.warning(f"No processable folders found in {root_path}")
        return

    extractor = ExamExtractor()
    history_path = root / "extraction_history.json"
    global_status_path = DOCS_DIR / "automation_status.json"

    # Flatten task list for status reporting
    flat_folders = []
    for _, years in exam_tasks:
        flat_folders.extend(years)
    
    def get_display_name(f):
        if not f or not hasattr(f, "relative_to"): return str(f or "---")
        try: return str(f.relative_to(root))
        except: return f.name

    def update_global_status(current_folder, current_pdf, newly_processed, total_q, all_folders, processed_h):
        # Allow passing strings directly for simple status messages
        folder_name = current_folder.name if hasattr(current_folder, 'name') else str(current_folder or "---")
        pdf_name = current_pdf.name if hasattr(current_pdf, 'name') else str(current_pdf or "Scanning...")
        
        try:
            status = {
                "root": str(root),
                "current_folder": get_display_name(current_folder),
                "current_pdf": pdf_name,
                "processed_count": newly_processed,
                "questions_added": total_q,
                "llm_stats": LLMTracker.get_report(),
                "folders": [
                    {
                        "name": get_display_name(f),
                        "status": "pending"
                    } for f in all_folders
                ],
                "last_update": time.ctime()
            }
            # Refine folder status: if all PDFs in folder are in history, it's done
            for folder_stat in status["folders"]:
                # Try to find the folder path by name
                f_path = root / folder_stat["name"]
                if not f_path.exists(): continue
                
                all_f_pdfs = list(f_path.glob("*.pdf"))
                if not all_f_pdfs: 
                    folder_stat["status"] = "no_pdfs"
                    continue
                done_in_f = sum(1 for p in all_f_pdfs if f"{p.name}_{p.stat().st_size}" in processed_h)
                if done_in_f == len(all_f_pdfs) and len(all_f_pdfs) > 0:
                    folder_stat["status"] = "done"
                elif done_in_f > 0:
                    folder_stat["status"] = f"processing ({done_in_f}/{len(all_f_pdfs)})"

            # Use atomic write for status and history to prevent corruption
            import tempfile
            tf = tempfile.NamedTemporaryFile('w', dir=global_status_path.parent, delete=False, encoding='utf-8')
            try:
                json.dump(status, tf, indent=2)
                tf.flush()
                if hasattr(os, 'fsync'): 
                    try: os.fsync(tf.fileno())
                    except: pass
                tf.close()
                os.replace(tf.name, global_status_path)
            except Exception as j_err:
                tf.close()
                if os.path.exists(tf.name): os.remove(tf.name)
                raise j_err

        except Exception as e:
            logger.error(f"Failed to update global status: {e}")

    # Load history
    processed_files = {}
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                processed_files = json.load(f)
        except Exception:
            processed_files = {}

    newly_processed = 0
    total_questions = 0

    # Process tasks
    for exam_folder, year_folders in exam_tasks:
        # Base slug from exam folder (e.g. 'IBPS PO' -> 'ibps_po')
        base_slug = slugify(exam_folder.name) or fallback_category
        
        logger.info(f"📁 Processing Exam: {exam_folder.name} (Slug: {base_slug})")

        for folder in year_folders:
            year = extract_year(folder.name)
            year_suffix = f"_{year}" if year != 9999 else ""
            target_filename = f"{base_slug}{year_suffix}.json"
            
            logger.info(f"   📂 Year Folder: {folder.name} -> Target: {target_filename}")
            
            while True:
                # 2. Get next batch of PDFs
                batch = get_job_batch(folder, processed_files, batch_size=5)
                if not batch:
                    logger.info(f"   ✅ Folder {folder.name} completed.")
                    break

                logger.info(f"   🚀 Starting batch of {len(batch)} PDFs in {folder.name}...")
                
                update_global_status(folder, None, newly_processed, total_questions, flat_folders, processed_files)
            
                for pdf_path in batch:
                    file_key = f"{pdf_path.name}_{pdf_path.stat().st_size}"
                    logger.info(f"  📥 Extracting: {pdf_path.name}")
                    update_global_status(folder, pdf_path, newly_processed, total_questions, flat_folders, processed_files)
                    
                    try:
                        with open(pdf_path, "rb") as fobj:
                            result = extractor.extract_from_pdf(fobj, mode=mode)
                        
                        p_type = result.get("type", "simple")
                        data = result.get("data", [])
                        
                        if data:
                            if p_type == "passage":
                                was_new, msg = append_passage_exam_to_file(target_filename, data)
                                logger.info(f"    ✅ {msg}")
                                if was_new: total_questions += len(data.get("questions", []))
                            else:
                                added, skipped = append_questions_to_file(target_filename, data)
                                logger.info(f"    ✅ Added {added}, skipped {skipped}")
                                total_questions += added
                        
                        # Update history
                        processed_files[file_key] = {
                            "status": "success",
                            "target": target_filename,
                            "time": time.ctime()
                        }
                        # Save history frequently
                        with open(history_path, "w", encoding="utf-8") as f:
                            json.dump(processed_files, f, indent=2)
                        
                        newly_processed += 1
                        update_global_status(folder, pdf_path, newly_processed, total_questions, flat_folders, processed_files)
                            
                    except Exception as e:
                        logger.error(f"    ❌ Error: {e}")
                        processed_files[file_key] = {"status": "error", "error": str(e), "time": time.ctime()}
                
                logger.info(f"   Rescanning {folder.name} for more files...")
                time.sleep(1) # Brief pause

    logger.info(f"\n✨ DONE! Total new questions in bank: {total_questions}")
    # Final cleanup update for UI
    update_global_status(None, "✅ All tasks completed!", newly_processed, total_questions, flat_folders, processed_files)
    
    # Step 5: Trigger the Refining & Validation Agent
    trigger_validation_agent()

def trigger_validation_agent():
    """Kick off the refining and validation agent after extraction."""
    logger.info("🔍 Starting Refining & Validation Agent...")
    try:
        agent_script = os.path.join(Config.BASE_DIR, "agent", "refining_agent.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = Config.BASE_DIR
        subprocess.Popen(["python", agent_script], env=env)
    except Exception as e:
        logger.error(f"Failed to trigger validation agent: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Year-by-year batch PDF extractor.")
    parser.add_argument("folder", help="Path to main folder (e.g. 'Downloads/JEE Main')")
    parser.add_argument("--mode", choices=["extract", "refine"], default="extract")
    parser.add_argument("--fallback", default="other")
    
    args = parser.parse_args()
    process_folder_structure(args.folder, mode=args.mode, fallback_category=args.fallback)
