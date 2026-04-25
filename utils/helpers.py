from config import Config
import logging
from utils.logger import setup_logger

logger = setup_logger(__name__)

import google.generativeai as genai
from huggingface_hub import snapshot_download
from datasets import Dataset, load_dataset
import pandas as pd
import glob
import os
import time
import requests

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

def _is_invalid(value) -> bool:
    # Helper for sanitization if needed here
    return False

class LLMTracker:
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_time = 0
    call_count = 0
    total_questions = 0
    
    # Cost constants (Indian Rupees)
    COST_PER_QUESTION = 0.028
    COST_PER_TOKEN = 0.0000208

    @classmethod
    def update(cls, p_tokens, c_tokens, wall_time):
        cls.prompt_tokens += p_tokens
        cls.completion_tokens += c_tokens
        cls.total_tokens += (p_tokens + c_tokens)
        cls.total_time += wall_time
        cls.call_count += 1

    @classmethod
    def update_questions(cls, count):
        cls.total_questions += count

    @classmethod
    def reset(cls):
        cls.total_tokens = 0
        cls.prompt_tokens = 0
        cls.completion_tokens = 0
        cls.total_time = 0
        cls.call_count = 0
        cls.total_questions = 0

    @classmethod
    def get_report(cls):
        cost_tokens = cls.total_tokens * cls.COST_PER_TOKEN
        cost_questions = cls.total_questions * cls.COST_PER_QUESTION
        
        return {
            "total_calls": cls.call_count,
            "total_tokens": cls.total_tokens,
            "total_questions": cls.total_questions,
            "prompt_tokens": cls.prompt_tokens,
            "completion_tokens": cls.completion_tokens,
            "total_time_seconds": round(cls.total_time, 2),
            "avg_time_per_call": round(cls.total_time / cls.call_count, 2) if cls.call_count > 0 else 0,
            "cost_by_tokens": round(cost_tokens, 4),
            "cost_by_questions": round(cost_questions, 4),
            "effective_cost_per_question": round(cost_tokens / cls.total_questions, 4) if cls.total_questions else 0
        }

def call_llm(prompt: str) -> str:
    """
    Calls the Google Generative AI (Gemma/Gemini) service or fallback API with the given prompt.
    Returns the text content of the response and tracks metrics.
    """
    model_name = Config.GENERATION_MODEL
    
    # 1. Try using Google Generative AI SDK if it's a Google/Gemma model 
    # AND we have a valid-looking Google API Key (starts with AIza)
    g_key = Config.GOOGLE_API_KEY
    if (model_name.startswith("google/") or model_name.startswith("models/")) and g_key and g_key.startswith("AIza"):
        try:
            genai.configure(api_key=g_key)
            # Remove "google/" prefix if present for AI Studio compatibility
            api_model_name = model_name.replace("google/", "models/") if model_name.startswith("google/") else model_name
            
            model = genai.GenerativeModel(api_model_name)
            
            start_time = time.time()
            response = model.generate_content(prompt)
            end_time = time.time()
            wall_time = end_time - start_time
            
            text = response.text
            
            # Track usage
            usage = getattr(response, 'usage_metadata', None)
            p_tokens = usage.prompt_token_count if usage else 0
            c_tokens = usage.candidates_token_count if usage else 0
            LLMTracker.update(p_tokens, c_tokens, wall_time)
            
            return text
        except Exception as e:
            logger.warning(f"Google Generative AI SDK failed (model: {model_name}): {e}. Trying fallback API...")
            # Continue to custom API fallback instead of returning empty

    # 2. Fallback to custom OpenAI-compatible API (Mistral/Llama/etc)
    url = Config.API_URL
    api_key = Config.API_KEY

    if not api_key:
        logger.error("API_KEY is missing from .env for custom endpoint")
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        end_time = time.time()
        wall_time = end_time - start_time

        response.raise_for_status()
        data = response.json()
        
        # Track usage if available
        usage = data.get("usage", {})
        p_tokens = usage.get("prompt_tokens", 0)
        c_tokens = usage.get("completion_tokens", 0)
        LLMTracker.update(p_tokens, c_tokens, wall_time)

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            logger.warning(f"Unexpected API response format: {data}")
            return ""
    except Exception as e:
        logger.error(f"Custom LLM API call failed: {e}")
        return ""
