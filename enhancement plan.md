# Cost Optimization Report — Question Extraction

**Reduce Token Cost by 60–75% Without Losing Accuracy**

A surgical optimization plan for the Question-Extraction pipeline — targeting prompt bloat, redundant injection, and sequential bottlenecks.

---

## 📊 Current vs Target Metrics

| Metric | Value |
|--------|-------|
| Current Cost / Question | ₹0.028 (53,868 tokens for 41 Q's) |
| Prompt Overhead | ~850 tokens / call (dead weight) |
| Tokens / Question | 1,314 (vs ~400 optimal target) |
| Target Cost / Question | ₹0.007 (4× cheaper, same quality) |

---

## 01 — Root Cause Diagnosis

### Where Your 1,314 Tokens Per Question Are Going

- **~65% Prompt** – System Prompt (~850 tokens repeated every call)
- **~15% Mapping** – Exam Mapping Table (~200 tokens injected every call)
- **~20% Content** – Actual Page Content (~264 tokens — the only useful input)

### 🔴 Problem 1: Full ~200-line Prompt Repeated Every Page Call [Critical]

Your prompt (~850 tokens) is injected on every single API call. For a 100-page PDF, that's **85,000 tokens wasted purely on repeated instructions**. The LLM already received these rules on call #1 — but because you have no multi-turn conversation state, you keep resending everything. This is the single biggest cost driver.

### 🔴 Problem 2: Full Exam Mapping Table Injected Even After Filtering [High Impact]

Even though you filter the `exam_mapping_table` by filename, the filtered slice is still injected as raw text tokens into every call. For an exam with 5 relevant mappings, you're still burning ~200 tokens/call on structured data that changes zero times across the entire PDF run.

### 🟡 Problem 3: 1 Page → 1 API Call — Severe Underutilization [Medium Impact]

Each call processes only **~264 tokens of real content** (a single page) but ships ~850 tokens of overhead. Gemma-4 supports a 128K context window. You're using less than 1% of it productively per call. Batching 4–8 pages per call immediately cuts overhead by 4–8×.

### 🟡 Problem 4: Examples & Checklists Are Expensive Filler [Low-Medium Impact]

Your prompts contain `<VALID_EXAMPLE>`, `<INVALID_EXAMPLES>`, and `<PRE_OUTPUT_CHECKLIST>` sections totalling ~250–300 tokens. After the model has extracted questions successfully for 10+ pages, it does not need the example record repeated on page 11. These should be sent only on the first call.

---

## 02 — Optimization Strategies

### Priority 1: Multi-Page Batching
**↓ 75% overhead cost**

Send 4–6 pages per API call instead of 1. Your prompt overhead (~850 tokens) is amortized across 4–6× more content. Zero quality loss — the model handles multi-page context well.

- **Effort:** Easy to implement (~2 hrs work)

### Priority 2: Prompt Compression
**↓ 35% prompt tokens**

Strip verbose XML tag names, remove INVALID_EXAMPLES after call #1, compress the PRE_OUTPUT_CHECKLIST from 10 bullet points to 3 critical checks. Keep the HARD_FILTERS but trim prose.

- **Effort:** No code change (edit .txt files)

### Priority 3: Pre-bake Mapping as System Prompt
**↓ 200 tokens/call**

Extract the filtered exam mapping once before the page loop and store it as a string. Inject it only in the first call inside the system prompt, not user turn. Subsequent calls reference it via: *"Use the exam mapping from the system prompt."*

- **Effort:** Medium effort (exam_extractor.py)

### Priority 4: Slim Prompt After Page 1
**↓ 300 tokens/call**

On the first page, send the full prompt with examples and checklist. From page 2 onward, send a "slim" version (~500 tokens) that contains only HARD_FILTERS, OUTPUT_SCHEMA, and FINAL_INSTRUCTIONS — cutting the per-call prompt by ~40%.

- **Effort:** Medium effort (add slim_prompt.txt)

### Priority 5: Async Parallel Execution — Speed, Not Cost
**↑ 5–8× speed**

Wrap `call_llm` in `asyncio.gather()` to process batches of pages concurrently. Does not reduce token count but cuts a 100-page PDF from 15–20 min down to 2–4 min. Pair with Priority 1 (batching) for compound gains. Watch your RPM/TPM rate limits on the API provider.

- **Effort:** Needs rate-limit guard (exam_extractor.py)

---

## 03 — Before vs After — Numbers

Projections for a 100-page PDF yielding ~100 questions. Assumes 4-page batching + slim prompt after page 1.

| Metric | Current (Baseline) | After Priority 1+2 | After Priority 1+2+3+4 |
|--------|--------------------|--------------------|------------------------|
| API Calls (100 pages) | 100 calls | 25 calls | 25 calls |
| Prompt tokens / call | ~850 | ~850 (call 1) / ~550 (rest) | ~550 (call 1) / ~350 (rest) |
| Total prompt overhead | ~85,000 tokens | ~14,200 tokens | ~9,100 tokens |
| Content tokens (same) | ~26,400 | ~26,400 | ~26,400 |
| Total tokens | ~131,400 | ~55,000 | ~36,000 |
| Cost (₹) @ ₹0.0000208/tok | ₹2.73 | ₹1.14 | ₹0.75 |
| Cost per question | ₹0.0273 | ₹0.0114 | ₹0.0075 |
| Savings vs baseline | — | ~58% cheaper | ~72% cheaper |
| Quality impact | Baseline | None | None |

---

## 04 — Implementation — Code Changes

### Change 1 — Multi-Page Batching in `exam_extractor.py`

Replace the 1-page-per-call loop with a batch loop. The separator tells the LLM where each page boundary is.

```python
# ── ADD this constant to config.py ──────────────────────────────
PAGES_PER_BATCH = 4   # tune: 4–6 pages per call is the sweet spot

# ── REPLACE the page loop in extract_questions() ────────────────
# BEFORE (1 call per page):
for page_num, page_text in enumerate(pages):
    result = call_llm(prompt, page_text)

# AFTER (batch loop):
def _chunk_pages(pages: list[str], size: int) -> list[list[str]]:
    return [pages[i:i + size] for i in range(0, len(pages), size)]

batches = _chunk_pages(pages, PAGES_PER_BATCH)

for batch_idx, batch in enumerate(batches):
    # Join pages with a clear separator the LLM can use to track context
    batch_text = "\n\n--- PAGE BREAK ---\n\n".join(batch)
    
    # Use slim prompt from page 2+ (see Change 2)
    is_first = (batch_idx == 0)
    result = call_llm(batch_text, use_full_prompt=is_first)
```

### Change 2 — Two-Tier Prompt Strategy

Keep your full prompt for the first batch. Create a slim version (~350 tokens) for all subsequent batches. Add this to `exam_extractor.py`:

```python
# slim_prompt_suffix goes in a new file: prompts/slim_prompt.txt
# Or define inline. This is the minimal ~350-token version:

SLIM_PROMPT_TEMPLATE = """You are a strict JSON-only MCQ extraction engine.
Mode: {mode}. PDF: {pdf_name}.

REJECT: answer keys, direction headers, marking schemes, page artifacts.
EXTRACT: only English MCQ questions with stem + options + answer.

Rules (strict):
- answer: single UPPERCASE letter (A/B/C/D/E) for MCQ
- options: clean text, no "(a)" prefix
- explanation: mandatory, 1-2 sentences
- All math in LaTeX $...$
- No forbidden metadata values (Unknown, N/A, none, "")
- Embed full passage text in question field for RC questions

Exam context: {exam_mapping_summary}

Output ONLY a valid JSON array using this schema:
{"exam_type","department","subject","topic","subtopic","difficulty",
  "question","option":{"A","B","C","D"},"answer","explanation",
  "level","eligibility","year","pdf_name"}

--- CONTENT ---
{pdf_text}"""

def call_llm(self, page_text: str, use_full_prompt: bool = False) -> str:
    template = self.full_prompt if use_full_prompt else SLIM_PROMPT_TEMPLATE
    prompt = template.format(
        mode=self.mode,
        pdf_name=self.pdf_name,
        exam_mapping=self.filtered_mapping,     # full only on first call
        exam_mapping_summary=self.mapping_summary, # 1-line summary for slim
        pdf_text=page_text
    )
    # ... rest of your existing API call logic unchanged
```

### Change 3 — Compress Mapping Table to 1-Line Summary

Pre-compute a compact summary of the exam mapping once before the loop. Inject this (~30 tokens) instead of the full table (~200 tokens) in slim-prompt calls.

```python
def _build_mapping_summary(self, filtered_rows: list) -> str:
    """Build a compact 1-line mapping string for slim prompts."""
    if not filtered_rows:
        return "No specific exam mapping found — infer from PDF content."
    
    # Take only the first matched row (most specific match)
    row = filtered_rows[0]
    return (
        f"exam_type={row['exam_type']}, department={row['department']}, "
        f"level={row['level']}, eligibility={row['eligibility']}"
    )
    # Example output: "exam_type=RRB NTPC, department=RRB, level=National, eligibility=Graduate"
    # Cost: ~20 tokens vs ~200 for full table = 90% reduction on slim calls

# In your __init__ or at the start of extract_questions():
self.filtered_mapping = filter_exam_mapping(self.pdf_name)  # existing logic
self.mapping_summary = self._build_mapping_summary(self.filtered_mapping)
```

### Change 4 — Async Parallel Execution (Speed Boost)

Process batches concurrently. Add a semaphore to avoid hitting rate limits. Combine with batching for maximum effect.

```python
import asyncio
import aiohttp

MAX_CONCURRENT_CALLS = 4  # Tune based on your provider's RPM limit
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CALLS)

async def call_llm_async(self, batch_text: str, batch_idx: int) -> list:
    async with _semaphore:
        prompt = self._build_prompt(batch_text, use_full=(batch_idx==0))
        # Replace requests.post with aiohttp.ClientSession.post
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload) as resp:
                data = await resp.json()
                return self._parse_response(data)

async def extract_questions_async(self, pages: list[str]) -> list:
    batches = self._chunk_pages(pages, PAGES_PER_BATCH)
    tasks = [
        self.call_llm_async("\n\n--- PAGE BREAK ---\n\n".join(b), i)
        for i, b in enumerate(batches)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Flatten and deduplicate as before
    return self._deduplicate([q for batch in results for q in batch])
```

---

## 05 — Implementation Roadmap

### Phase 1 — Quick Wins – ~58% cost reduction
- [ ] Add `PAGES_PER_BATCH = 4` to `config.py`
- [ ] Replace the page loop in `exam_extractor.py` with the batch loop (Change 1 above)
- [ ] Join page texts with `--- PAGE BREAK ---` separator
- [ ] Add `--- PAGE BREAK ---` as a filter note in `HARD_FILTERS` so the LLM knows to treat it as a separator only, not a question
- [ ] Test on 2–3 PDFs and compare question count and quality vs. baseline

### Phase 2 — Slim Prompt  – +14% additional savings
- [ ] Create `prompts/slim_prompt.txt` with ~350-token compressed version (template above)
- [ ] Update `call_llm()` to accept a `use_full_prompt: bool` flag
- [ ] Build `_build_mapping_summary()` for compact exam context
- [ ] Run the first batch with the full prompt, all subsequent batches with slim

### Phase 3 — Async Speed – 5–8× speed increase
- [ ] Install `aiohttp` and replace `requests.post` with async equivalent
- [ ] Add semaphore-guarded `call_llm_async()`
- [ ] Run extraction with `asyncio.gather()` over all batches
- [ ] Update Streamlit to use `asyncio.run()` or `nest_asyncio` for the async call
- [ ] Monitor rate limits — add exponential backoff on 429 errors

---

## 06 — Additional Quality-Preserving Tricks

### Cross-Page Boundary Detection
**Quality Guard** – Add 200–300 chars of overlap between batches: append the last 2 lines of the previous batch to the start of the next. This catches questions split across page 4→5 boundary without adding many tokens.

### Skip Empty / Low-Content Pages
**Free Savings** – Before batching, filter out pages with fewer than 100 characters. Title pages, blank pages, and "Space for Rough Work" pages are currently burning full API calls. Pre-filter saves 5–15% calls for typical PDFs.

### Response Caching by Page Hash
**Re-run Savings** – Hash each page's text and cache the LLM response in a local storage (shelve or sqlite3). When the same PDF is reprocessed (e.g., in "refine" mode), cached pages skip the API call entirely. Near-zero cost for re-runs.

### Passage Prompt Trigger Optimization
**Quality + Cost** – Your `_is_passage_based()` check fires per page. When batching, check if ANY page in the batch contains passage keywords. If yes, use the passage prompt for the whole batch. Avoids prompt mismatch at boundaries.

---

## 📈 Summary of Gains

| Metric | Value |
| :--- | :--- |
| **Total Cost Reduction** | ~72% (after all 4 priority changes) |
| **New Cost / Question** | ₹0.007 (down from ₹0.028) |
| **Speed Improvement** | 5–8× (with async + batching) |
| **Priority 1+2 alone** | ~58% savings with 3 hrs of work |
