from datasets import load_dataset
from config import Config
import logging
from utils.logger import setup_logger

logger = setup_logger(__name__)

from huggingface_hub import snapshot_download
from datasets import Dataset, load_dataset
import pandas as pd
import glob
import os

def load_data(split="train"):
    """
    Load the JEE/NEET benchmark dataset manually to bypass script restrictions.
    """
    try:
        logger.info(f"Attempting to load {Config.DATASET_NAME} via snapshot download...")
        
        # Download repo content ignoring the script
        local_dir = os.path.join(Config.RAW_DATA_DIR, "jee_neet_snapshot")
        snapshot_download(repo_id=Config.DATASET_NAME, repo_type="dataset", local_dir=local_dir, 
                          allow_patterns=["data/*", "images/*", "*.json", "*.parquet", "*.arrow", "*.csv", "*.png", "*.jpg", "*.jpeg", "*.jsonl"],
                          ignore_patterns=["results/*"]) 

        # Try loading parquet files from data/ directory
        data_pattern = os.path.join(local_dir, "data", "*.parquet")
        files = glob.glob(data_pattern)
        
        if not files:
             # Try recursive
             data_pattern = os.path.join(local_dir, "**", "*.parquet")
             files = glob.glob(data_pattern, recursive=True)

        if files:
            logger.info(f"Found parquet files: {len(files)}")
            dataset = load_dataset("parquet", data_files=files, split=split)
            logger.info(f"Dataset features: {dataset.features}")
            logger.info(f"Loaded {len(dataset)} examples")
            return dataset
            
        # Check for metadata.jsonl (common in image datasets)
        jsonl_files = glob.glob(os.path.join(local_dir, "**", "metadata.jsonl"), recursive=True)
        if jsonl_files:
            jsonl_path = jsonl_files[0]
            logger.info(f"Found metadata.jsonl at {jsonl_path}")
            
            import json
            from datasets import Features, Value, Image as ImageFeature
            
            data = []
            base_path = os.path.dirname(jsonl_path)
            
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        row = json.loads(line)
                        # Fix correct_answer type mismatch
                        ans = row.get('correct_answer')
                        if isinstance(ans, list):
                            row['correct_answer'] = str(ans[0]) if ans else "" 
                        else:
                            row['correct_answer'] = str(ans) if ans is not None else ""
                            
                        # Handle image path
                        # 'file_name' is standard for ImageFolder metadata, but this dataset uses 'image_path'
                        image_file = row.get('file_name') or row.get('image') or row.get('image_path')
                        
                        if image_file and isinstance(image_file, str):
                             # Potential paths to check
                             possible_paths = [
                                 os.path.join(base_path, image_file), # ./images/xxx.png
                                 os.path.join(base_path, 'data', image_file), # ./data/images/xxx.png
                                 os.path.join(os.path.dirname(base_path), image_file), # ../images/xxx.png (sibling to data)
                                 os.path.join(Config.RAW_DATA_DIR, "jee_neet_snapshot", image_file) # Absolute root of snapshot
                             ]
                             
                             found = False
                             for p in possible_paths:
                                 # Resolve .. and .
                                 p = os.path.abspath(p)
                                 if os.path.exists(p):
                                     row['image'] = p
                                     found = True
                                     break
                                     
                             if not found:
                                 row['image'] = None # Image missing
                        
                        data.append(row)
                    except Exception as e:
                        logger.warning(f"Skipping bad row: {e}")
            
            if data:
                # Create dataset
                ds = Dataset.from_list(data)
                # Cast image column
                if 'image' in ds.column_names:
                     try:
                        ds = ds.cast_column("image", ImageFeature())
                     except Exception as cast_err:
                        logger.warning(f"Could not cast image column: {cast_err}. Images might be paths.")
                
                logger.info(f"Loaded {len(ds)} examples manuel parsed JSONL")
                return ds

        # Fallback to generic imagefolder if no JSONL or manual parsing failed
        if os.path.exists(os.path.join(local_dir, "data")):
             logger.info("Trying generic imagefolder as fallback...")
             dataset = load_dataset("imagefolder", data_dir=os.path.join(local_dir, "data"), split=split)
             return dataset

        logger.error("No recognizable data files found in snapshot.")
        return None

    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return None
