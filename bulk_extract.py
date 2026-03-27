import os
import sys
import argparse
from pathlib import Path
from utils.logger import setup_logger
from rag.exam_extractor import ExamExtractor
from utils.question_store import detect_category, append_questions, append_passage_exam

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Bulk extract MCQs from a folder of PDFs without Streamlit timeouts.")
    parser.add_argument("folder", help="Path to the folder containing PDF files.")
    parser.add_argument("--mode", choices=["extract", "refine"], default="extract", help="Extraction mode (default: extract)")
    parser.add_argument("--fallback-category", default="upsc", 
                        choices=["upsc", "ssc", "banking", "insurance", "railway",
                                 "defense_nda", "defense_cds", "defense_afcat", "defense_other",
                                 "teaching", "judiciary", "psu", "healthcare", "technical",
                                 "central_police", "neet_ug", "neet_pg", "jee_main", "jee_advanced",
                                 "state_psc", "other"],
                        help="Category to use if exam acronym isn't detected in PDF name (default: upsc)")
    
    args = parser.parse_args()
    folder_path = Path(args.folder)

    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: Invalid folder path '{folder_path}'")
        sys.exit(1)

    pdfs = list(folder_path.rglob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in '{folder_path}'")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDFs in {folder_path}. Starting bulk extraction...")
    
    extractor = ExamExtractor()
    total_added = 0
    total_skipped = 0

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] Processing {pdf_path.name}...")
        
        try:
            with open(pdf_path, "rb") as fobj:
                result = extractor.extract_from_pdf(fobj, mode=args.mode)
            
            ptype = result.get("type", "simple")
            data = result.get("data", [])
            slug = detect_category(pdf_path.name) or args.fallback_category

            if ptype == "passage":
                if data:
                    was_new, msg = append_passage_exam(slug, data)
                    print(f"  -> {msg}")
                    if was_new:
                        total_added += len(data.get("questions", []))
                else:
                    print(f"  -> No questions found in passage mode.")
            else:
                if data:
                    added, skipped = append_questions(slug, data)
                    total_added += added
                    total_skipped += skipped
                    print(f"  -> Added {added} new MCQs, skipped {skipped} duplicates.")
                else:
                    print(f"  -> No MCQs found.")
        except Exception as e:
            print(f"  -> Error processing {pdf_path.name}: {e}")
            logger.error(f"Failed bulk extraction on {pdf_path}: {e}")

    print(f"\n=== BULK EXTRACTION COMPLETE ===")
    print(f"Total new questions saved: {total_added}")
    print(f"Total duplicates skipped:  {total_skipped}")

if __name__ == "__main__":
    main()
