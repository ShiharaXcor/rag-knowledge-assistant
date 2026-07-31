import streamlit as st
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from style_utils import get_custom_css

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Company Knowledge Assistant", layout="wide", page_icon="🔒")
st.markdown(get_custom_css(), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔒 Company Knowledge Assistant")
    st.markdown("---")
    st.markdown("**Viewing as:**")
    user_role = st.selectbox("Role", options=["employee", "hr", "leadership"], label_visibility="collapsed")
    st.markdown(f'<span class="role-badge">{user_role.upper()}</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("This role switcher demonstrates role-based access control, enforced server-side via the FastAPI backend.")
    st.markdown("---")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("Company Knowledge Assistant")
st.caption("Ask about company policies, onboarding, security practices, or engineering standards.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            strip_class = "access-strip blocked" if msg.get("blocked") else "access-strip"
            sources_str = ", ".join(msg["sources"])
            st.markdown(f'<div class="{strip_class}">📄 Sources: {sources_str}</div>', unsafe_allow_html=True)

user_query = st.chat_input("Ask a question...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]

            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"query": user_query, "user_role": user_role, "chat_history": history},
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.RequestException as e:
                result = {"answer": f"Error connecting to backend: {e}", "sources": [], "blocked": False}

        st.write(result["answer"])

        if result["sources"]:
            strip_class = "access-strip blocked" if result.get("blocked") else "access-strip"
            sources_str = ", ".join(result["sources"])
            st.markdown(f'<div class="{strip_class}">📄 Sources: {sources_str}</div>', unsafe_allow_html=True)
        elif result.get("blocked"):
            st.markdown('<div class="access-strip blocked">🚫 Request blocked by security filter</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
        "blocked": result.get("blocked", False),
    })