from config import Config
from utils.logger import setup_logger
from utils.helpers import call_llm
import json
import os

logger = setup_logger(__name__)

class Generator:
    def __init__(self):
        if not (Config.API_KEY or Config.GOOGLE_API_KEY):
             raise ValueError("No API key found (API_KEY or GOOGLE_API_KEY).")
             
        # Load prompt template
        prompt_path = os.path.join(Config.BASE_DIR, "prompts", "mcq_generation_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found at {prompt_path}")
            self.prompt_template = "{context} {n} {subject} {difficulty}" # Fallback
            
    def generate_mcqs(self, context_questions, topic, difficulty, num_questions, exam_type="JEE"):
        """
        Generate MCQs based on context.
        """
        # Format context
        context_str = ""
        for i, q in enumerate(context_questions):
            # Extract question text and answer
            q_text = q.get('question_text', '') or q.get('question', '')
            ans = q.get('correct_answer', '')
            context_str += f"Example {i+1}: {q_text}\nAnswer: {ans}\n\n"
            
        # Fill prompt
        # Fill prompt using replace to avoid issues with literal braces in JSON example
        prompt = self.prompt_template.replace("{context}", context_str)
        prompt = prompt.replace("{n}", str(num_questions))
        prompt = prompt.replace("{exam}", str(exam_type))
        prompt = prompt.replace("{subject}", str(topic))
        prompt = prompt.replace("{difficulty}", str(difficulty))
        
        try:
            logger.info("Sending generation request to Mistral/Llama...")
            text = call_llm(prompt)
            
            if not text:
                logger.error("Empty response from LLM")
                return []

            import re
            
            # Clean markdown code blocks
            text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r',?\s*```$', '', text, flags=re.MULTILINE) # Handle potential trailing comma before backticks
            text = text.strip()
            
            # Find JSON array
            start = text.find('[')
            end = text.rfind(']')
            
            if start != -1 and end != -1:
                text = text[start:end+1]
                
            # Attempt to fix invalid escape sequences (common with LaTeX)
            text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
            
            try:
                data = json.loads(text, strict=False)
            except json.JSONDecodeError as e:
                logger.warning(f"json.loads failed: {e}. Attempting fallback parser...")
                # Fallback: Sometimes the model generates raw Python strings instead of strict JSON
                import ast
                try:
                    # Clean up common issues before ast.literal_eval
                    # Replace JSON literal booleans/nulls to python ones if present (though mostly string values here)
                    text_fallback = text.replace('null', 'None').replace('true', 'True').replace('false', 'False')
                    data = ast.literal_eval(text_fallback)
                    if not isinstance(data, list):
                        data = [data] if isinstance(data, dict) else []
                    logger.info("Fallback parser (ast.literal_eval) succeeded.")
                except Exception as eval_e:
                    safe_text = text.encode('ascii', 'backslashreplace').decode('ascii')
                    logger.error(f"Fallback parsing also failed: {eval_e}. Raw text: {safe_text}")
                    return []
                    
            return data
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return []
