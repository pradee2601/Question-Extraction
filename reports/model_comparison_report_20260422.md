# 📊 Model Comparison Report: Local Llama vs. OpenRouter (Google API)

This report compares two extraction runs for the same PDF document (`RRB-PO-Pre-Memory-Based-2020-1.pdf`) using different model backends.

## 🚀 Performance Metrics

| Metric | Local Llama (2026-04-21) | OpenRouter (Google API) (2026-04-11) | Winner |
| :--- | :--- | :--- | :--- |
| **Total Questions** | 41 | **43** | OpenRouter (Slightly) |
| **Total Time Taken** | 265s (4m 25s) | **260s** | OpenRouter |
| **Extraction Speed** | **202.7 tokens/sec** | 190.0 tokens/sec | Local Llama |
| **Avg Time per Call** | 20.44s | **20.01s** | Neutral |
| **Total Tokens** | 53,868 | 49,417 | - |

---

## 💎 Question Quality Check

### 1. Metadata Accuracy
*   **Local Llama:** Correctly categorized subjects (e.g., *Quantitative Aptitude*, *Reasoning Ability*) and specific topics (e.g., *Number System*, *Floor and Flat Based Puzzle*).
*   **OpenRouter:** Frequently failed to identify subjects and topics, defaulting to **"Unknown"** or using generic "General Awareness" even for logical reasoning questions.

### 2. Mathematical Formatting
*   **Local Llama:** Utilizes **LaTeX** (e.g., `$2$`, `$2145673$`). Critical for high-quality exam platforms.
*   **OpenRouter:** Used plain text numbers and symbols, making the content look less professional.

### 3. Explanation Depth (Logic)
*   **Local Llama:** Provides **step-by-step reasoning**. For the first number manipulation question, it showed the exact digit-by-digit transformation.
*   **OpenRouter:** Provided **tautological or shallow explanations**. Example: *"The information provided in the question is true regarding H."* It failed to explain *why*.

### 4. Handling Constraints
*   **Local Llama:** Better at recognizing when info is insufficient. It admitted to *"Insufficient information provided in the text"* rather than hallucinating.
*   **OpenRouter:** Attempted to provide answers/explanations even when the logic was circular.

---

## 🏆 Final Verdict

**Local Llama** is the clear winner for this task. While the speed is comparable, the depth of categorization and the professional formatting (LaTeX) make it far more suitable for a production-grade question extraction pipeline than the current OpenRouter configuration.
