import sys
import asyncio

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import streamlit as st
import os
import json
import time
import subprocess
import psutil

from config import Config
from utils.logger import setup_logger
from utils.helpers import load_data
from rag.ocr import extract_text_from_image, clean_text
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import Generator
from rag.pdf_processor import process_pdf, chunk_text
from rag.exam_extractor import ExamExtractor
from rag.question_validator import QuestionValidator
from utils.question_store import (
    EXAM_CATEGORIES, SLUG_ORDER,
    append_questions, load_questions, all_counts, detect_category,
    append_passage_exam, load_passage_exams,
)

# Setup logger
logger = setup_logger()

st.set_page_config(page_title="JEE/NEET MCQ Generator", layout="wide", page_icon="📚")

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .question-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
    }
    /* Folder picker widget */
    .folder-drop-zone {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #1e1e2e;
        border: 1.5px solid #3a3a5c;
        border-radius: 8px;
        padding: 18px 20px;
        margin: 6px 0 10px 0;
        min-height: 72px;
        gap: 16px;
    }
    .folder-drop-zone .fdz-left {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;
    }
    .folder-drop-zone .fdz-icon {
        font-size: 2rem;
        color: #aaa;
    }
    .folder-drop-zone .fdz-text { color: #e0e0e0; font-size: 1rem; font-weight: 500; }
    .folder-drop-zone .fdz-sub  { color: #888; font-size: 0.78rem; margin-top: 2px; }
    .folder-browse-btn {
        background: #2c2c3e !important;
        color: #e0e0e0 !important;
        border: 1px solid #555 !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
        font-size: 0.9rem !important;
        cursor: pointer;
        white-space: nowrap;
    }
    .folder-browse-btn:hover { background: #3c3c5e !important; }
    .folder-selected-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: #1a3a1a; border: 1px solid #2d6a2d;
        border-radius: 6px; padding: 8px 14px;
        color: #7dda7d; font-size: 0.88rem; margin: 4px 0 8px 0;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)


def _check_api_key() -> bool:
    """
    Quick validation of the GOOGLE_API_KEY.
    Shows a clear error banner and returns False if the key is missing,
    obviously wrong, or suspended (403 CONSUMER_SUSPENDED).
    """
    key = Config.GOOGLE_API_KEY
    if not key or len(key) < 20:
        st.error(
            "## ⚠️ Google API Key Missing\n\n"
            "No `GOOGLE_API_KEY` found in your `.env` file.\n\n"
            "**Steps to fix:**\n"
            "1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and create a new key\n"
            "2. Open `.env` and set: `GOOGLE_API_KEY=your_new_key_here`\n"
            "3. Restart the app"
        )
        return False

    # Test the key with a minimal call
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel(Config.GENERATION_MODEL)
        model.generate_content("Say OK", generation_config={"max_output_tokens": 5})
        return True
    except Exception as e:
        err_str = str(e)
        if "CONSUMER_SUSPENDED" in err_str or "suspended" in err_str.lower():
            st.error(
                "## 🚫 Google API Key Suspended\n\n"
                "Your API key has been **suspended** by Google. This usually happens when:\n"
                "- The free-tier quota was exceeded\n"
                "- The key was flagged for unusual activity\n\n"
                "**Steps to fix:**\n"
                "1. Go to [Google AI Studio](https://aistudio.google.com/apikey) → create a **new** API key\n"
                "2. Open your `.env` file and replace the old key:\n"
                "   ```\n"
                "   GOOGLE_API_KEY=your_new_key_here\n"
                "   ```\n"
                "3. Save `.env` and restart the app with `streamlit run app.py`"
            )
        elif "403" in err_str or "401" in err_str:
            st.error(
                f"## ❌ API Key Invalid (403/401)\n\n"
                f"The key in `.env` was rejected by Google.\n\n"
                f"Get a new key at [Google AI Studio](https://aistudio.google.com/apikey) and update `.env`.\n\n"
                f"Raw error: `{err_str[:200]}`"
            )
        else:
            st.warning(
                f"⚠️ Could not verify API key: `{err_str[:200]}`\n\n"
                "The app will continue but may fail during generation."
            )
            return True   # Non-auth error — let it proceed
        return False


def ingest_data():
    """
    Ingest data from HuggingFace, process images, embed, and store.
    """
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        status_text.text("Loading dataset...")
        dataset = load_data(split="train")
        if not dataset:
            st.error("Failed to load dataset.")
            return

        # Initialize components
        embedder = Embedder()
        vector_store = VectorStore()
        
        # For demonstration, limit to 50 items to save time/API costs
        # In production this would be an offline batch job
        subset_size = min(50, len(dataset))
        data_subset = dataset.select(range(subset_size))
        
        embeddings = []
        metadatas = []
        
        status_text.text(f"Processing {subset_size} images with OCR and Embedding...")
        
        for i, item in enumerate(data_subset):
            try:
                # Reja1/jee-neet-benchmark structure
                image = item.get('image')
                question_id = item.get('question_id', str(i))
                subject = item.get('subject', 'General')
                
                # OCR
                ocr_text = ""
                if image:
                    try:
                        # Handle path string (custom loader)
                        if isinstance(image, str):
                            if os.path.exists(image):
                                from PIL import Image
                                image = Image.open(image)
                            else:
                                logger.warning(f"Image path not found: {image}")
                                continue
                                
                        if hasattr(image, 'mode') and image.mode != 'RGB':
                            image = image.convert('RGB')
                        ocr_text = extract_text_from_image(image)
                        ocr_text = clean_text(ocr_text)
                    except Exception as e:
                        logger.warning(f"OCR failed for item {i}: {e}")
                
                if not ocr_text:
                    if i < 5: # Log first few failures just to see
                        logger.warning(f"Item {i} skipped: OCR text is empty.")
                    continue
                    
                # Embed
                emb = embedder.get_embedding(ocr_text)
                if emb:
                    embeddings.append(emb)
                    metadatas.append({
                        "id": str(question_id),
                        "question_text": ocr_text,
                        "subject": subject,
                        "correct_answer": item.get('correct_answer', 'Unknown')
                    })
            except Exception as e:
                logger.error(f"Error processing item {i}: {e}")
                
            progress_bar.progress((i + 1) / subset_size)
        
        if embeddings:
            vector_store.add_embeddings(embeddings, metadatas)
            vector_store.save_index()
            status_text.text("Ingestion Complete!")
            st.success(f"Successfully processed and indexed {len(embeddings)} questions.")
        else:
            st.warning("No valid data processed.")
            
    except Exception as e:
        st.error(f"An error occurred during ingestion: {e}")
        logger.error(f"Ingestion fatal error: {e}")

def process_uploaded_pdfs(uploaded_files):
    """
    Process manually uploaded PDFs, chunk them, embed, and store in the Vector Store.
    """
    if not uploaded_files:
        st.warning("Please upload some PDFs first.")
        return
        
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        embedder = Embedder()
        vector_store = VectorStore()
        
        embeddings = []
        metadatas = []
        
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing '{uploaded_file.name}' ({i+1}/{total_files})...")
            
            # Extract text (with OCR fallback for scanned PDFs)
            extracted_text = process_pdf(uploaded_file)
            
            if not extracted_text:
                logger.warning(f"No text extracted from {uploaded_file.name}")
                continue
                
            # Chunk the extracted text
            chunks = chunk_text(extracted_text, chunk_size=800, overlap=100)
            
            status_text.text(f"Embedding {len(chunks)} chunks from '{uploaded_file.name}'...")
            
            for j, chunk in enumerate(chunks):
                if chunk.strip():
                     emb = embedder.get_embedding(chunk)
                     if emb:
                         embeddings.append(emb)
                         metadatas.append({
                             "id": f"pdf_{uploaded_file.name}_chunk_{j}",
                             "question_text": chunk, # Treated as context in the prompt
                             "subject": "Extracted PDF Context",
                             "correct_answer": "Refer to Document" # Default placeholder
                         })
                         
            progress_bar.progress((i + 1) / total_files)
            
        if embeddings:
            vector_store.add_embeddings(embeddings, metadatas)
            vector_store.save_index()
            status_text.text("PDF Processing Complete!")
            st.success(f"Successfully processed {total_files} PDFs into {len(embeddings)} knowledge chunks.")
        else:
            status_text.text("No extractable text found.")
            st.warning("Could not extract any meaningful text/images from the uploaded PDFs.")
            
    except Exception as e:
         st.error(f"An error occurred while processing PDFs: {e}")
         logger.error(f"PDF processing error: {e}")

def _render_mcq_list(mcqs: list, key_prefix: str = ""):
    """Render a flat list of simple MCQ dicts (supports new lowercase + old field names)."""
    for i, mcq in enumerate(mcqs):
        with st.container():
            qtext = mcq.get('question') or mcq.get('question_text', '')
            # Separate heading from question text so complex LaTeX renders properly
            st.markdown(f"**Q{i+1}:**")
            st.markdown(qtext)

            exam_type  = mcq.get('exam_type') or mcq.get('Exam Type') or mcq.get('exam', 'N/A')
            department = mcq.get('department') or mcq.get('Department', 'N/A')
            year       = mcq.get('year', 'N/A')
            subject    = mcq.get('subject') or mcq.get('Subject', 'N/A')
            topic      = mcq.get('topic') or mcq.get('Topic', 'N/A')
            subtopic   = mcq.get('subtopic') or mcq.get('Subtopic', 'N/A')
            difficulty = mcq.get('difficulty', 'N/A')

            st.caption(
                f"**Exam:** {exam_type} | **Dept:** {department} | **Year:** {year} | **Subject:** {subject} "
                f"| **Topic:** {topic} | **Subtopic:** {subtopic} | **Difficulty:** {difficulty}"
            )

            # ── Validation badge ──────────────────────────────────────
            v_status = mcq.get('validation_status')
            if v_status:
                _render_validation_badge(mcq)

            cols = st.columns(2)
            options = mcq.get('option') or mcq.get('options', {})
            if isinstance(options, dict) and len(options) > 0:
                for idx, (opt, text) in enumerate(options.items()):
                    # Use st.markdown instead of st.info so LaTeX renders
                    cols[idx % 2].markdown(
                        f"> **{opt.upper()}:** {text}"
                    )
            else:
                st.info("💡 **Numerical / Subjective Question (No Options)**")

            with st.expander("Show Answer & Explanation"):
                ans = mcq.get('answer') or mcq.get('correct_answer', 'N/A')
                # Use st.markdown instead of st.success so LaTeX in answer renders
                st.markdown(f"✅ **Correct Answer:** {str(ans).upper()}")
                expl = mcq.get('explanation') or mcq.get('Explanation', 'N/A')
                if expl and expl != 'N/A':
                    st.markdown(f"**Explanation:** {expl}")

            st.markdown("---")


def _render_validation_badge(mcq: dict):
    """Render a coloured validation badge with source URL for a validated question."""
    status = mcq.get('validation_status', 'unverified')
    source = mcq.get('validation_source', '')
    notes  = mcq.get('validation_notes', '')
    is_real = mcq.get('is_real_exam_question', False)
    ans_ok  = mcq.get('answer_verified', False)
    ans_src = mcq.get('answer_from_source', '')
    fixed   = mcq.get('fields_corrected', [])

    # Status colours
    status_config = {
        'verified':   ('\u2705 Verified',           '#1a3a1a', '#2d6a2d', '#7dda7d'),
        'corrected':  ('\U0001f527 Corrected & Fixed',  '#3a3a1a', '#6a6a2d', '#dada7d'),
        'unverified': ('\u26a0\ufe0f Unverified',          '#3a2a1a', '#6a4a2d', '#da9a7d'),
        'error':      ('\u274c Validation Error',     '#3a1a1a', '#6a2d2d', '#da7d7d'),
    }
    label, bg, border, color = status_config.get(status, status_config['unverified'])

    # Build badge HTML
    badge_parts = [f"<strong>{label}</strong>"]
    if is_real:
        badge_parts.append("\U0001f4cb Real Exam Q")
    if ans_ok:
        badge_parts.append("\u2705 Answer OK")
    if ans_src:
        badge_parts.append(f"\U0001f4dd Source Answer: <strong>{ans_src}</strong>")

    badge_text = " &nbsp;|&nbsp; ".join(badge_parts)

    st.markdown(
        f"<div style='display:inline-flex;align-items:center;gap:8px;"
        f"background:{bg};border:1px solid {border};border-radius:6px;"
        f"padding:6px 12px;color:{color};font-size:0.85rem;margin:4px 0 8px 0;'>"
        f"{badge_text}</div>",
        unsafe_allow_html=True,
    )

    if source:
        st.markdown(
            f"&nbsp;&nbsp;\U0001f517 **Source:** [{source[:80]}{'...' if len(source) > 80 else ''}]({source})",
        )

    if fixed:
        st.caption(f"\U0001f527 **Fields fixed:** {', '.join(fixed)}")

    if notes:
        st.caption(f"\U0001f4dd {notes}")

    # Show search results in an expander
    search_results = mcq.get('search_results', [])
    if search_results:
        with st.expander("\U0001f50d Web Search Results"):
            for sr in search_results:
                st.markdown(
                    f"- **[{sr.get('title', 'Link')}]({sr.get('link', '#')})** \u2014 "
                    f"{sr.get('snippet', '')[:150]}"
                )

def _render_passage_exam(exam_obj: dict, inside_expander: bool = False):
    """
    Render a passage-based exam object (CSAT-style).

    Parameters
    ----------
    inside_expander : bool
        When True, questions are rendered as plain containers (no expanders),
        because Streamlit forbids nesting expanders inside expanders.
    """
    # Build passage lookup
    passage_map: dict[str, dict] = {
        p["passage_id"]: p
        for p in exam_obj.get("passages", [])
        if "passage_id" in p
    }

    questions = exam_obj.get("questions", [])
    if not questions:
        st.info("No questions found in this exam object.")
        return

    # Group questions by passage_ref
    from collections import defaultdict
    groups: dict[str | None, list] = defaultdict(list)
    for q in questions:
        groups[q.get("passage_ref")].append(q)

    q_counter = 0
    for passage_ref, qs in groups.items():
        if passage_ref and passage_ref in passage_map:
            p = passage_map[passage_ref]
            st.markdown(
                f"<div style='background:#1a2a3a;border-left:4px solid #4a9eff;"
                f"padding:12px 16px;border-radius:6px;margin-bottom:12px;'>"
                f"<b style='color:#4a9eff'>{p.get('title','Passage')}</b>"
                f"<span style='color:#888;font-size:0.8em;margin-left:10px'>{p.get('section','')}</span>"
                f"<p style='color:#ddd;margin-top:8px;font-size:0.92em;white-space:pre-wrap;'>{p.get('text','')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        elif passage_ref is None and qs:
            st.markdown("##### Standalone Questions")

        for q in qs:
            q_counter += 1
            qnum  = q.get("question_number") or q_counter
            qtext = q.get("question_text", "")

            statements  = q.get("statements")
            instruction = q.get("instruction", "")
            options     = q.get("options", {})
            ans         = q.get("correct_answer", "N/A")
            expl        = q.get("explanation", "")

            stmt_html = ""
            if statements:
                stmt_html = "<ol style='margin:6px 0 2px 18px;color:#ccc;font-size:0.92em;'>" + \
                    "".join(f"<li>{s}</li>" for s in statements) + "</ol>"

            label = f"Q{qnum}: {qtext[:120]}{'...' if len(qtext) > 120 else ''}"

            def _render_q_body():
                """Inner render shared by both expander and container modes."""
                st.markdown(f"**{qtext}**")
                if stmt_html:
                    st.markdown(stmt_html, unsafe_allow_html=True)
                if instruction:
                    st.caption(f"_{instruction}_")
                if isinstance(options, dict):
                    cols = st.columns(2)
                    for idx2, (opt, otext) in enumerate(options.items()):
                        cols[idx2 % 2].info(f"**({opt.upper()})** {otext}")
                st.success(f"**Answer:** ({str(ans).upper()})")
                if expl:
                    st.write(f"**Explanation:** {expl}")

            if inside_expander:
                # Streamlit forbids nested expanders — use a styled container
                st.markdown(
                    f"<div style='border:1px solid #333;border-radius:6px;"
                    f"padding:10px 14px;margin:4px 0;background:#16161e;'>"
                    f"<b style='color:#ccc'>{label}</b></div>",
                    unsafe_allow_html=True,
                )
                with st.container():
                    _render_q_body()
                st.markdown("<hr style='border-color:#222;margin:4px 0'>",
                            unsafe_allow_html=True)
            else:
                with st.expander(label):
                    _render_q_body()

        st.markdown("---")


def _run_extraction(
    pdf_sources,          # list of (name, file-like) tuples
    extraction_mode: str,
    selected_slug: str,
) -> dict:
    """
    Run ExamExtractor over a list of (filename, file-like) sources.
    Saves results into the Question Bank.
    Returns {"simple": [MCQ, ...], "passage": [exam_obj, ...]}.
    """
    extractor   = ExamExtractor()
    all_simple:  list[dict] = []
    all_passage: list[dict] = []
    file_results: list[str] = []

    progress = st.progress(0, text="Starting...")
    total    = len(pdf_sources)

    for idx, (fname, fobj) in enumerate(pdf_sources):
        progress.progress(idx / total, text=f"Processing {fname} ({idx+1}/{total})...")
        try:
            result = extractor.extract_from_pdf(fobj, mode=extraction_mode)
            ptype  = result.get("type", "simple")
            data   = result.get("data", [])

            if ptype == "passage":
                q_count = len(data.get("questions", []))
                p_count = len(data.get("passages", []))
                if q_count > 0:
                    all_passage.append(data)
                    file_results.append(
                        f"✅ **{fname}** (passage-based) — "
                        f"{p_count} passage(s), {q_count} question(s)"
                    )
                else:
                    file_results.append(f"⚠️ **{fname}** — no questions found")
            else:
                if data:
                    all_simple.extend(data)
                    file_results.append(
                        f"✅ **{fname}** — {len(data)} MCQ(s) extracted"
                    )
                else:
                    file_results.append(f"⚠️ **{fname}** — no MCQs found")
        except Exception as e:
            file_results.append(f"❌ **{fname}** — error: {e}")
            logger.error(f"Extraction error for {fname}: {e}")

    progress.progress(1.0, text="Done!")

    save_summary: list[str] = []
    total_added = total_skipped = 0

    # -- Save simple MCQs -------------------------------------------------
    if all_simple:
        grouped: dict[str, list] = {}
        for q in all_simple:
            # Use the manually selected slug exclusively (no auto-detect override)
            slug = selected_slug
            grouped.setdefault(slug, []).append(q)
        for slug, qs in grouped.items():
            added, skipped = append_questions(slug, qs)
            total_added   += added
            total_skipped += skipped
            save_summary.append(
                f"**{EXAM_CATEGORIES[slug]['label']}** (MCQ): "
                f"{added} added, {skipped} duplicate(s) skipped"
            )

    # -- Save passage exams -----------------------------------------------
    if all_passage:
        for exam_obj in all_passage:
            # Use the manually selected slug exclusively (no auto-detect override)
            slug = selected_slug
            was_new, msg = append_passage_exam(slug, exam_obj)
            status = "✅" if was_new else "⚠️"
            save_summary.append(f"{status} {msg}")
            if was_new:
                total_added += len(exam_obj.get("questions", []))

    # -- UI feedback ------------------------------------------------------
    any_data = all_simple or all_passage
    if any_data:
        st.success(
            f"Extracted from **{total}** file(s). "
            + (f"**{len(all_simple)}** standalone MCQ(s). " if all_simple else "")
            + (f"**{len(all_passage)}** passage exam(s). " if all_passage else "")
            + f"Saved **{total_added}** new item(s) ({total_skipped} duplicate(s) skipped)."
        )
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("Per-file results"):
                for r in file_results:
                    st.markdown(f"- {r}")
        with col_b:
            with st.expander("Save breakdown by category"):
                for line in save_summary:
                    st.markdown(f"- {line}")
    else:
        st.error("No content could be extracted from any of the uploaded files.")
        for r in file_results:
            st.markdown(f"- {r}")

    return {"simple": all_simple, "passage": all_passage}


def _open_folder_dialog() -> str:
    """
    Open a native OS folder-picker dialog using tkinter.
    Returns the selected folder path as a string, or '' if cancelled.
    """
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()                      # hide the empty root window
    root.wm_attributes('-topmost', True) # dialog floats on top of browser
    selected = filedialog.askdirectory(title="Select folder containing PDFs")
    root.destroy()
    return selected or ""


def _folder_picker_widget() -> str:
    """
    Renders a styled folder-picker that visually matches Streamlit's file
    uploader widget (dark card + Browse button). Returns the chosen folder path.
    """
    current_path = st.session_state.get("_folder_path", "")

    # ── Styled drop-zone card ─────────────────────────────────────────────
    if current_path:
        icon   = "📂"
        title  = "Folder selected"
        sub    = current_path
    else:
        icon   = "🖥️"
        title  = "Select a folder"
        sub    = "Click &ldquo;Browse folder&rdquo; to open a folder on this computer"

    browse_label = "📂 &nbsp;Change folder" if current_path else "📂 &nbsp;Browse folder"

    st.markdown(
        f"""
        <div class="folder-drop-zone">
          <div class="fdz-left">
            <span class="fdz-icon">{icon}</span>
            <div>
              <div class="fdz-text">{title}</div>
              <div class="fdz-sub">{sub}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Streamlit button triggers the tkinter dialog
    if st.button(browse_label.replace("&nbsp;", " "), key="_btn_browse_folder"):
        chosen = _open_folder_dialog()
        if chosen:
            st.session_state["_folder_path"] = chosen
            st.rerun()

    return st.session_state.get("_folder_path", "")


def main():
    st.title("📚 JEE/NEET MCQ Generator with RAG")
    st.markdown("Generate high-quality practice questions based on real exam patterns.")

    # ── API key health check ───────────────────────────────────────────────
    if not st.session_state.get("_api_key_ok"):
        with st.spinner("🔑 Verifying Google API key …"):
            ok = _check_api_key()
        if not ok:
            st.stop()   # halt rendering — show only the error above
        st.session_state["_api_key_ok"] = True

    # ------------------------------------------------------------------ Sidebar
    st.sidebar.title("⚙️ Configuration")

    st.sidebar.subheader("Knowledge Base")
    if st.sidebar.button("Update Knowledge Base (Ingest Data)"):
        ingest_data()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Upload Custom PDFs (RAG)")
    st.sidebar.caption("Upload PDFs to enrich the knowledge base for MCQ generation.")
    uploaded_pdfs = st.sidebar.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="rag_pdf_uploader",
    )
    if st.sidebar.button("Process Uploaded PDFs"):
        process_uploaded_pdfs(uploaded_pdfs)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Generator Settings")

    custom_exam = st.sidebar.toggle("Custom Exam")
    if custom_exam:
        exam_type = st.sidebar.text_input("Enter Custom Exam Name", placeholder="e.g., CUET")
    else:
        exam_type = st.sidebar.selectbox("Select Exam", ["JEE Main", "JEE Advanced", "NEET"])

    custom_subject = st.sidebar.toggle("Custom Subject")
    if custom_subject:
        subject = st.sidebar.text_input("Enter Custom Subject Name", placeholder="e.g., Computer Science")
    else:
        subject = st.sidebar.selectbox("Select Subject", ["Physics", "Chemistry", "Mathematics", "Biology"])

    difficulty    = st.sidebar.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
    num_questions = st.sidebar.slider("Number of Questions", 1, 10, 3)

    # -------------------------------------------------------------- Main tabs
    tab_generate, tab_extract, tab_bank, tab_monitor = st.tabs(
        ["🤖 Generate MCQs (RAG)", "📥 Extract from Exam PDF", "🗄️ Question Bank", "📊 Automation Monitor"]
    )

    # ============================= TAB 1 – RAG Generator ====================
    with tab_generate:
        if st.button("🚀 Generate MCQs", key="btn_generate"):
            st.session_state['mcqs'] = None
            try:
                retriever = Retriever()
                generator = Generator()

                with st.spinner("🔍 Retrieving similar questions from Knowledge Base..."):
                    query   = f"{subject} question {difficulty} {exam_type}"
                    context = retriever.retrieve(query, k=3)

                if not context:
                    st.warning("No similar questions found. Please update the knowledge base first.")
                else:
                    with st.expander("🔍 View Retrieved Context (RAG Source)"):
                        for i, ctx_item in enumerate(context):
                            st.markdown(f"**Context {i+1}**")
                            st.info(ctx_item.get('question_text', 'No text'))
                            st.caption(f"Answer: {ctx_item.get('correct_answer')}")

                    with st.spinner("🤖 Generating new MCQs with Gemini..."):
                        mcqs = generator.generate_mcqs(
                            context, subject, difficulty, num_questions, exam_type
                        )
                        if mcqs:
                            st.session_state['mcqs'] = mcqs
                        else:
                            st.error("Failed to generate MCQs. Check logs.")
            except Exception as e:
                st.error(f"Error: {e}")

        if st.session_state.get('mcqs'):
            st.markdown("### 📝 Generated Questions")
            _render_mcq_list(st.session_state['mcqs'], key_prefix="gen")
            mcq_json = json.dumps(st.session_state['mcqs'], indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=mcq_json,
                file_name="generated_mcqs.json",
                mime="application/json",
                key="download_gen",
            )

    # ============================= TAB 2 – Exam PDF Extractor ===============
    with tab_extract:
        st.markdown(
            "Extract MCQs from exam PDFs. Upload **individual files** or point to a "
            "**local folder** and all PDFs inside will be processed automatically. "
            "Results are saved to the Question Bank."
        )

        # ── Shared settings row ───────────────────────────────────────────────
        cfg_col1, cfg_col2 = st.columns([2, 1])

        with cfg_col1:
            category_options = {
                slug: EXAM_CATEGORIES[slug]["label"] for slug in SLUG_ORDER
            }
            selected_slug = st.selectbox(
                "💾 Default Save Category",
                options=list(category_options.keys()),
                format_func=lambda s: category_options[s],
                help=(
                    "Fallback category when the exam name in the PDF cannot be "
                    "auto-detected. Auto-detection runs first."
                ),
                key="sel_category",
            )

        with cfg_col2:
            extraction_mode = st.radio(
                "Extraction Mode",
                options=["extract", "refine"],
                index=0,
                format_func=lambda m: "📋 Extract (original)" if m == "extract" else "✏️ Refine (polished)",
                help=(
                    "Extract – keep original wording, only fill missing answers/explanations.\n"
                    "Refine – improve grammar & clarity while preserving the correct answer."
                ),
            )

        # ── Validation toggle ────────────────────────────────────────────
        val_col1, val_col2 = st.columns([1, 2])
        with val_col1:
            enable_validation = st.checkbox(
                "🔍 Validate with Web Search",
                value=False,
                key="enable_validation",
                help=(
                    "After extraction, each question is searched on Google (Serper API), "
                    "the best matching page is scraped (Firecrawl API), and the extracted "
                    "data is cross-checked for correctness using Gemini. "
                    "This verifies exam type, year, options, and answer against real sources."
                ),
            )
        with val_col2:
            if enable_validation:
                st.info(
                    "🔍 Validation is **ON**. Each question will be verified against web sources. "
                    "This adds ~5-8 sec per question."
                )

        st.markdown("---")

        # ── Input-mode selector ───────────────────────────────────────────────
        input_mode = st.radio(
            "Input Source",
            options=["files", "folder"],
            format_func=lambda m: "📄 Upload Files" if m == "files" else "📁 Select Folder (local path)",
            horizontal=True,
            key="input_mode",
        )

        pdf_sources: list[tuple] = []   # (filename, file-like)
        ready = False

        # ── Mode A: file uploader ────────────────────────────────────────────
        if input_mode == "files":
            uploaded_files = st.file_uploader(
                "📄 Upload PDF file(s)",
                type=["pdf"],
                accept_multiple_files=True,
                key="exam_pdf_uploader",
                help="You can select multiple PDF files at once using Ctrl+Click or Shift+Click.",
            )
            if uploaded_files:
                pdf_sources = [(f.name, f) for f in uploaded_files]
                st.caption(
                    f"📄 **{len(uploaded_files)}** file(s) selected: "
                    + ", ".join(f.name for f in uploaded_files[:5])
                    + (" …" if len(uploaded_files) > 5 else "")
                )
                ready = True

        # ── Mode B: folder picker ───────────────────────────────────────────
        else:
            include_subfolders = st.checkbox(
                "Include sub-folders (recursive)",
                value=True,
                key="include_subfolders",
            )

            folder_path_str = _folder_picker_widget()

            if folder_path_str:
                import pathlib
                folder_path = pathlib.Path(folder_path_str.strip())

                if not folder_path.exists() or not folder_path.is_dir():
                    st.error(f"❌ Invalid folder path: `{folder_path}`")
                    st.session_state["_folder_path"] = ""
                else:
                    pattern = "**/*.pdf" if include_subfolders else "*.pdf"
                    found_pdfs = sorted(folder_path.glob(pattern))
                    if not found_pdfs:
                        st.warning(f"⚠️ No PDF files found in `{folder_path}`.")
                    else:
                        st.markdown(
                            f'<div class="folder-selected-badge">📚 '
                            f'<strong>{len(found_pdfs)}</strong> PDF file(s) found'
                            + (" (including sub-folders)" if include_subfolders else "")
                            + '</div>',
                            unsafe_allow_html=True,
                        )
                        with st.expander(f"📄 View {len(found_pdfs)} file(s)"):
                            for p in found_pdfs:
                                st.markdown(f"- `{p.relative_to(folder_path)}`")
                        pdf_sources = [(p.name, open(p, "rb")) for p in found_pdfs]
                        ready = True

        # ── Extract & Save button ───────────────────────────────────────────
        st.markdown("")
        if st.button(
            "⚙️ Extract & Save MCQs",
            key="btn_extract",
            disabled=not ready,
            type="primary",
        ):
            st.session_state['extracted_result'] = None
            st.session_state['validated_result'] = None
            extracted = _run_extraction(pdf_sources, extraction_mode, selected_slug)
            any_data = extracted.get("simple") or extracted.get("passage")
            if any_data:
                st.session_state['extracted_result'] = extracted

                # ── Auto-validate if toggle is on ────────────────────
                if enable_validation and extracted.get("simple"):
                    st.markdown("---")
                    st.markdown("### 🔍 Validating Questions Against Web Sources...")
                    try:
                        validator = QuestionValidator()
                        val_progress = st.progress(0, text="Starting validation...")
                        val_status = st.empty()

                        def _val_callback(idx, total, q):
                            pct = (idx + 1) / total
                            v = q.get('validation_status', '?')
                            val_progress.progress(pct, text=f"Validating {idx+1}/{total} — {v}")
                            val_status.caption(
                                f"Q{idx+1}: {q.get('question','')[:80]}... → **{v}**"
                            )

                        validated_qs = validator.validate_batch(
                            extracted["simple"],
                            progress_callback=_val_callback,
                        )
                        val_progress.progress(1.0, text="Validation complete!")

                        # Counts
                        n_ver = sum(1 for q in validated_qs if q.get('validation_status') == 'verified')
                        n_cor = sum(1 for q in validated_qs if q.get('validation_status') == 'corrected')
                        n_unv = sum(1 for q in validated_qs if q.get('validation_status') == 'unverified')
                        n_err = sum(1 for q in validated_qs if q.get('validation_status') == 'error')

                        st.success(
                            f"**Validation Complete:** "
                            f"✅ {n_ver} verified, 🔧 {n_cor} corrected, "
                            f"⚠️ {n_unv} unverified, ❌ {n_err} errors"
                        )

                        # Replace simple MCQs with validated versions
                        extracted["simple"] = validated_qs
                        st.session_state['extracted_result'] = extracted
                        st.session_state['validated_result'] = validated_qs
                        
                        try:
                            val_out_dir = os.path.join("e:\\", "govtexam", "docs", "valitedquestionsfolder")
                            os.makedirs(val_out_dir, exist_ok=True)
                            val_out_file = os.path.join(val_out_dir, f"validated_{int(time.time())}.json")
                            with open(val_out_file, "w", encoding="utf-8") as f:
                                json.dump(validated_qs, f, indent=2, ensure_ascii=False)
                        except Exception as file_exp:
                            logger.error(f"Failed to write validated MCQs to folder: {file_exp}")

                        try:
                            from utils.question_store import update_questions_by_id
                            # Default to updating the current selected category 
                            update_questions_by_id(selected_slug, validated_qs)
                        except Exception as store_exp:
                            logger.error(f"Failed to update validated MCQs in question store: {store_exp}")

                    except Exception as e:
                        st.error(f"Validation failed: {e}")
                        logger.error(f"Validation error: {e}")

            # Close any open file handles from folder mode
            if input_mode == "folder":
                for _, fobj in pdf_sources:
                    try:
                        fobj.close()
                    except Exception:
                        pass

        # ── Manual Validate button (for previously extracted but unvalidated questions) ──
        result = st.session_state.get('extracted_result')
        if result and result.get("simple") and not st.session_state.get('validated_result'):
            if st.button("🔍 Validate Extracted Questions Now", key="btn_validate_manual"):
                st.markdown("### 🔍 Validating Questions Against Web Sources...")
                try:
                    validator = QuestionValidator()
                    val_progress = st.progress(0, text="Starting validation...")

                    def _val_cb(idx, total, q):
                        val_progress.progress(
                            (idx + 1) / total,
                            text=f"Validating {idx+1}/{total} — {q.get('validation_status', '?')}"
                        )

                    validated_qs = validator.validate_batch(
                        result["simple"], progress_callback=_val_cb
                    )
                    val_progress.progress(1.0, text="Validation complete!")

                    n_ver = sum(1 for q in validated_qs if q.get('validation_status') == 'verified')
                    n_cor = sum(1 for q in validated_qs if q.get('validation_status') == 'corrected')
                    n_unv = sum(1 for q in validated_qs if q.get('validation_status') == 'unverified')

                    st.success(
                        f"✅ {n_ver} verified, 🔧 {n_cor} corrected, ⚠️ {n_unv} unverified"
                    )

                    result["simple"] = validated_qs
                    st.session_state['extracted_result'] = result
                    st.session_state['validated_result'] = validated_qs
                    
                    try:
                        val_out_dir = os.path.join("e:\\", "govtexam", "docs", "valitedquestionsfolder")
                        os.makedirs(val_out_dir, exist_ok=True)
                        val_out_file = os.path.join(val_out_dir, f"validated_{int(time.time())}.json")
                        with open(val_out_file, "w", encoding="utf-8") as f:
                            json.dump(validated_qs, f, indent=2, ensure_ascii=False)
                    except Exception as file_exp:
                        logger.error(f"Failed to write validated MCQs to folder: {file_exp}")
                        
                    try:
                        from utils.question_store import update_questions_by_id
                        # Try to get the slug from the UI state
                        slug_to_update = st.session_state.get('browse_slug', selected_slug)
                        update_questions_by_id(slug_to_update, validated_qs)
                    except Exception as store_exp:
                        logger.error(f"Failed to update validated MCQs in question store: {store_exp}")
                        
                    st.rerun()

                except Exception as e:
                    st.error(f"Validation failed: {e}")

        # ── Preview ───────────────────────────────────────────────────────
        if result:
            simple_mcqs   = result.get("simple", [])
            passage_exams = result.get("passage", [])

            total_qs = len(simple_mcqs) + sum(
                len(e.get("questions", [])) for e in passage_exams
            )
            st.markdown(f"### Preview - {total_qs} Extracted Question(s)")

            # Validation summary if available
            if st.session_state.get('validated_result'):
                v_qs = st.session_state['validated_result']
                n_ver = sum(1 for q in v_qs if q.get('validation_status') == 'verified')
                n_cor = sum(1 for q in v_qs if q.get('validation_status') == 'corrected')
                n_unv = sum(1 for q in v_qs if q.get('validation_status') == 'unverified')
                n_real = sum(1 for q in v_qs if q.get('is_real_exam_question'))
                n_ans = sum(1 for q in v_qs if q.get('answer_verified'))

                sum_cols = st.columns(6)
                sum_cols[0].metric("✅ Verified", n_ver)
                sum_cols[1].metric("🔧 Corrected", n_cor)
                sum_cols[2].metric("⚠️ Unverified", n_unv)
                sum_cols[3].metric("📋 Real Exam", n_real)
                sum_cols[4].metric("✅ Answer OK", n_ans)
                n_fixes = sum(len(q.get('fields_corrected', [])) for q in v_qs)
                sum_cols[5].metric("🔧 Fields Fixed", n_fixes)

            if simple_mcqs:
                st.markdown(f"#### Standalone MCQs ({len(simple_mcqs)})")
                _render_mcq_list(simple_mcqs, key_prefix="ext")

                # Download buttons
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    ext_json = json.dumps(simple_mcqs, indent=2, ensure_ascii=False)
                    st.download_button(
                        label=f"⬇️ Download MCQs ({len(simple_mcqs)}) JSON",
                        data=ext_json,
                        file_name="extracted_mcqs.json",
                        mime="application/json",
                        key="download_ext_simple",
                    )
                with dl_col2:

                    # Download validated version in MongoDB-ready format

                    if st.session_state.get('validated_result'):

                        _TARGET_FIELDS = [

                            "_id", "exam_type", "department", "subject",

                            "topic", "subtopic", "difficulty", "question",

                            "option", "answer", "explanation", "level",

                            "eligibility", "year", "pdf_name",

                        ]

                        clean_qs = []

                        for q in simple_mcqs:

                            ordered = {}

                            for f in _TARGET_FIELDS:

                                if f in q:

                                    ordered[f] = q[f]

                            if q.get("validation_source"):

                                ordered["validation_source"] = q["validation_source"]

                            if q.get("validation_status"):

                                ordered["validation_status"] = q["validation_status"]

                            clean_qs.append(ordered)

                        val_json = json.dumps(clean_qs, indent=2, ensure_ascii=False)

                        st.download_button(

                            label=f"⬇️ Download Validated MCQs JSON",

                            data=val_json,

                            file_name="validated_mcqs.json",

                            mime="application/json",

                            key="download_validated",

                        )


            for i, exam_obj in enumerate(passage_exams):
                exam_name = exam_obj.get("exam", f"Exam {i+1}")
                exam_date = exam_obj.get("date", "")
                st.markdown(
                    f"#### Passage Exam: {exam_name}"
                    + (f" ({exam_date})" if exam_date else "")
                )
                _render_passage_exam(exam_obj)
                ext_json = json.dumps(exam_obj, indent=2, ensure_ascii=False)
                st.download_button(
                    label=f"Download '{exam_name}' JSON",
                    data=ext_json,
                    file_name=f"passage_exam_{i+1}.json",
                    mime="application/json",
                    key=f"download_ext_passage_{i}",
                )

    # ============================= TAB 3 – Question Bank =====================
    with tab_bank:
        st.markdown(
            "Browse, search, and download the questions stored in each exam "
            "category file inside `docs/`."
        )

        # ── Category summary cards ─────────────────────────────────────────
        counts = all_counts()
        card_cols = st.columns(3)
        for i, slug in enumerate(SLUG_ORDER):
            label    = EXAM_CATEGORIES[slug]["label"]
            fname    = EXAM_CATEGORIES[slug]["file"]
            slug_cnt = counts[slug]
            mcq_n    = slug_cnt.get("mcq", 0)
            pex_n    = slug_cnt.get("passage_exams", 0)
            delta    = f"{mcq_n} MCQs" + (f" + {pex_n} exams" if pex_n else "")
            with card_cols[i % 3]:
                st.metric(label=f"{label}", value=f"{mcq_n + pex_n}", delta=delta)

        st.markdown("---")

        # ── Drill-down: pick a category to browse ─────────────────────────
        browse_slug = st.selectbox(
            "📂 Browse Category",
            options=SLUG_ORDER,
            format_func=lambda s: EXAM_CATEGORIES[s]["label"],
            key="browse_slug",
        )

        bank_qs = load_questions(browse_slug)
        cat_label = EXAM_CATEGORIES[browse_slug]["label"]
        cat_file  = EXAM_CATEGORIES[browse_slug]["file"]

        if not bank_qs:
            st.info(
                f"No questions saved yet for **{cat_label}**.  \n"
                f"Upload a PDF in the *Extract from Exam PDF* tab to populate it."
            )
        else:
            # Search / filter
            search_term = st.text_input(
                "🔍 Search questions",
                placeholder="Type keywords …",
                key="bank_search",
            )
            if search_term:
                filtered = [
                    q for q in bank_qs
                    if search_term.lower() in q.get("question", "").lower()
                    or search_term.lower() in q.get("topic", "").lower()
                    or search_term.lower() in q.get("subtopic", "").lower()
                ]
            else:
                filtered = bank_qs

            st.markdown(
                f"### {cat_label}  -  {len(filtered)} / {len(bank_qs)} MCQ(s)"
            )
            _render_mcq_list(filtered, key_prefix=f"bank_{browse_slug}")

            bank_json = json.dumps(bank_qs, indent=2, ensure_ascii=False)
            st.download_button(
                label=f"Download {cat_label} MCQs ({len(bank_qs)})",
                data=bank_json,
                file_name=cat_file,
                mime="application/json",
                key=f"download_bank_{browse_slug}",
            )

        # -- Passage exams browser ----------------------------------------
        passage_exams = load_passage_exams(browse_slug)
        if passage_exams:
            st.markdown(f"---\n### Passage-Based Exams ({len(passage_exams)}):")
            for i, exam_obj in enumerate(passage_exams):
                exam_name = exam_obj.get("exam", f"Exam {i+1}")
                exam_date = exam_obj.get("date", "")
                q_count   = len(exam_obj.get("questions", []))
                p_count   = len(exam_obj.get("passages", []))
                with st.expander(
                    f"{exam_name}" + (f" ({exam_date})" if exam_date else "")
                    + f"  -  {p_count} passages, {q_count} questions"
                ):
                    _render_passage_exam(exam_obj, inside_expander=True)
                    exam_json = json.dumps(exam_obj, indent=2, ensure_ascii=False)
                    st.download_button(
                        label=f"Download '{exam_name}' JSON",
                        data=exam_json,
                        file_name=f"{exam_name.replace(' ','_')[:40]}.json",
                        mime="application/json",
                        key=f"dl_pex_{browse_slug}_{i}",
                    )

            # ── Danger zone: clear category ────────────────────────────────
            with st.expander("⚠️ Danger Zone"):
                st.warning(
                    f"This will permanently delete all **{len(bank_qs)}** questions "
                    f"from **{cat_label}** (`docs/{cat_file}`)."
                )
                if st.button(
                    f"🗑️ Clear {cat_label} Bank",
                    key=f"clear_{browse_slug}",
                ):
                    from utils.question_store import save_questions
                    save_questions(browse_slug, [])
                    st.success(f"✅ {cat_label} question bank cleared.")
                    st.rerun()

    # ============================= TAB 4 – Automation Monitor =================
    with tab_monitor:
        st.markdown("### 🤖 Automation Controls")
        
        # --- Control Form ---
        with st.expander("⚙️ Set Up Automation", expanded=not os.path.exists(os.path.join("docs", "automation_status.json"))):
            auto_path = st.text_input("Folder to Watch:", value=st.session_state.get('auto_path', ""), placeholder="C:\\Users\\...\\JEE Main")
            auto_fallback = st.selectbox("Fallback Category:", options=SLUG_ORDER, index=SLUG_ORDER.index("jee_main") if "jee_main" in SLUG_ORDER else 0)
            
            c1, c2 = st.columns(2)
            
            # Use a file to track PID so it survives refresh
            pid_file = os.path.join("docs", "automation_pid.txt")
            is_running = False
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, "r") as f:
                        old_pid = int(f.read().strip())
                    # Check if process is actually alive
                    if psutil.pid_exists(old_pid):
                        is_running = True
                except Exception:
                    pass

            if c1.button("🚀 Start Automation", disabled=is_running, type="primary"):
                if not auto_path or not os.path.isdir(auto_path):
                    st.error("Invalid folder path!")
                else:
                    cmd = [sys.executable, "-u", "automate_batch_extractor.py", auto_path, "--fallback", auto_fallback]
                    proc = subprocess.Popen(
                        cmd, 
                        stdout=None,
                        stderr=None
                    )
                    with open(pid_file, "w") as f:
                        f.write(str(proc.pid))
                    st.success(f"Started automation (PID: {proc.pid})")
                    st.session_state['auto_path'] = auto_path
                    st.rerun()

            if c2.button("🛑 Stop Automation", disabled=not is_running):
                try:
                    with open(pid_file, "r") as f:
                        pid_to_kill = int(f.read().strip())
                    parent = psutil.Process(pid_to_kill)
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                    os.remove(pid_file)
                    if os.path.exists(os.path.join("docs", "automation_status.json")):
                        os.remove(os.path.join("docs", "automation_status.json"))
                    st.warning("Automation stopped.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to stop: {e}")

        st.markdown("---")
        st.markdown("### 📊 Live Progress")

        status_file = os.path.join("docs", "automation_status.json")
        if not os.path.exists(status_file):
            st.info("No automation process currently reporting status. Run `python automate_batch_extractor.py \"FOLDER_PATH\"` to start.")
        else:
            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    status = json.load(f)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📁 Current Folder", status.get("current_folder", "N/A"))
                col2.metric("📄 Current PDF", (status.get("current_pdf") or "Scanning...")[:20] + "...")
                col3.metric("✅ PDFs Processed", status.get("processed_count", 0))
                col4.metric("📝 Questions Saved", status.get("questions_added", 0))

                st.markdown("---")
                
                folders = status.get("folders", [])
                if folders:
                    st.markdown("#### 📂 Processing Queue")
                    for f in folders:
                        name = f.get("name")
                        stat = f.get("status", "pending")
                        icon = "⏳" if stat == "pending" else "⚙️" if "processing" in stat else "✅"
                        color = "gray" if stat == "pending" else "orange" if "processing" in stat else "green"
                        
                        st.markdown(
                            f"""<div style="padding:10px; border-radius:5px; border-left: 5px solid {color}; background:#262730; margin-bottom:5px;">
                                {icon} <b>{name}</b> — <small>{stat.upper()}</small>
                            </div>""", 
                            unsafe_allow_html=True
                        )
                
                st.caption(f"Last updated: {status.get('last_update', 'Unknown')}")
                
                with st.expander("📜 Show Live Tracking Logs (Terminal Output)", expanded=False):
                    try:
                        if os.path.exists(Config.LOG_FILE):
                            with open(Config.LOG_FILE, "r", encoding="utf-8", errors="replace") as lf:
                                lines = lf.readlines()
                                recent_logs = "".join(lines[-35:])
                                st.code(recent_logs, language="text")
                        else:
                            st.info("No logs generated yet.")
                    except Exception as err:
                        st.error(f"Cannot load logs: {err}")
                
                if st.button("🔄 Refresh Status", key="btn_refresh_status_auto"):
                    st.rerun()

                # Auto-refresh if active or recently updated
                is_active = is_running or (time.time() - os.path.getmtime(status_file) < 30)
                if is_active:
                    time.sleep(3)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading status: {e}")


if __name__ == "__main__":
    main()
