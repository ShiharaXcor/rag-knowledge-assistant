import streamlit as st
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from style_utils import get_custom_css

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Admin - Knowledge Base", layout="wide", page_icon="🔒")
st.markdown(get_custom_css(), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔒 Company Knowledge Assistant")
    st.caption("Admin Panel")

st.title("Knowledge Base Admin")
st.caption("Upload documents, assign access roles, and manage the vector index.")

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
        with st.spinner("Uploading and indexing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"allowed_roles": ",".join(allowed_roles)}
                response = requests.post(f"{API_URL}/documents/upload", files=files, data=data, timeout=120)
                response.raise_for_status()
                result = response.json()
                st.success(f"'{result['filename']}' uploaded and indexed ({result['chunks_indexed']} chunks). Access: {', '.join(result['allowed_roles'])}")
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Upload failed: {e}")

# --- Current documents table ---
with col2:
    st.subheader("📚 Indexed Documents")

    try:
        response = requests.get(f"{API_URL}/documents", timeout=30)
        response.raise_for_status()
        documents = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not load documents: {e}")
        documents = []

    if not documents:
        st.info("No documents indexed yet.")
    else:
        for doc in documents:
            filename = doc["filename"]
            count = doc["chunk_count"]
            roles = doc["allowed_roles"]
            is_confidential = "employee" not in roles

            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{filename}**")
                c1.caption(f"{count} chunks · Access: {', '.join(roles)}")
                if is_confidential:
                    c2.markdown("🔒 Restricted")
                if c3.button("Delete", key=f"del_{filename}"):
                    try:
                        del_response = requests.delete(f"{API_URL}/documents/{filename}", timeout=30)
                        del_response.raise_for_status()
                        del_result = del_response.json()
                        st.success(f"Deleted '{filename}' ({del_result['chunks_deleted']} chunks removed)")
                        st.rerun()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Delete failed: {e}")
                st.divider()