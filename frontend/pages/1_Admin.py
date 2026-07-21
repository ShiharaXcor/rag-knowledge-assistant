import streamlit as st
import sys
import json
from pathlib import Path

BACKEND_SRC = Path(__file__).resolve().parent.parent.parent / "backend" / "src"
sys.path.append(str(BACKEND_SRC))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.config import RAW_DATA_PATH
from ingestion.loader import load_all_documents
from ingestion.chunker import chunk_documents
from retrieval.vector_store import add_chunks_to_store, get_chroma_client, get_or_create_collection
from style_utils import get_custom_css

PERMISSIONS_FILE = RAW_DATA_PATH.parent / "doc_permissions.json"

st.set_page_config(page_title="Admin - Knowledge Base", layout="wide", page_icon="🔒")
st.markdown(get_custom_css(), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔒 Company Knowledge Assistant")
    st.caption("Admin Panel")

st.title("Knowledge Base Admin")
st.caption("Upload documents, assign access roles, and manage the vector index.")

# --- Load current permissions ---
def load_permissions():
    if PERMISSIONS_FILE.exists():
        with open(PERMISSIONS_FILE, "r") as f:
            return json.load(f)
    return {"default": ["employee", "hr", "leadership"]}

def save_permissions(perms):
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(perms, f, indent=2)

permissions = load_permissions()

col1, col2 = st.columns([1, 1])

# --- Upload section ---
with col1:
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "md"])
    allowed_roles = st.multiselect(
        "Who can access this document?",
        options=["employee", "hr", "leadership"],
        default=["employee", "hr", "leadership"],
    )

    if st.button("Upload & Index", type="primary", disabled=(uploaded_file is None)):
        RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
        save_path = RAW_DATA_PATH / uploaded_file.name

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        permissions[uploaded_file.name] = allowed_roles
        save_permissions(permissions)

        with st.spinner("Indexing document (embedding + storing)..."):
            docs = load_all_documents(str(RAW_DATA_PATH))
            docs = [d for d in docs if d["filename"] == uploaded_file.name]
            chunks = chunk_documents(docs)
            add_chunks_to_store(chunks)

        st.success(f"'{uploaded_file.name}' uploaded and indexed with access: {', '.join(allowed_roles)}")
        st.rerun()

# --- Current documents table ---
with col2:
    st.subheader("📚 Indexed Documents")

    client = get_chroma_client()
    collection = get_or_create_collection(client)
    data = collection.get()

    doc_chunk_counts = {}
    for meta in data["metadatas"]:
        source = meta["source"]
        doc_chunk_counts[source] = doc_chunk_counts.get(source, 0) + 1

    if not doc_chunk_counts:
        st.info("No documents indexed yet.")
    else:
        for filename, count in doc_chunk_counts.items():
            roles = permissions.get(filename, permissions.get("default", []))
            is_confidential = "employee" not in roles

            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{filename}**")
                c1.caption(f"{count} chunks · Access: {', '.join(roles)}")
                if is_confidential:
                    c2.markdown("🔒 Restricted")
                if c3.button("Delete", key=f"del_{filename}"):
                    ids_to_delete = [
                        data["ids"][i] for i in range(len(data["ids"]))
                        if data["metadatas"][i]["source"] == filename
                    ]
                    collection.delete(ids=ids_to_delete)
                    st.success(f"Deleted '{filename}' ({len(ids_to_delete)} chunks removed)")
                    st.rerun()
                st.divider()

st.markdown("---")
st.subheader("⚙️ Bulk Re-index")
st.caption("Re-process all files in the raw data folder from scratch (use if you've manually added files without uploading through this panel).")
if st.button("Re-index All Documents"):
    with st.spinner("Re-indexing all documents..."):
        docs = load_all_documents(str(RAW_DATA_PATH))
        chunks = chunk_documents(docs)
        add_chunks_to_store(chunks)
    st.success(f"Re-indexed {len(docs)} documents into {len(chunks)} chunks.")