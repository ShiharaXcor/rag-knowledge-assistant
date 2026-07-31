import streamlit as st
import requests
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from style_utils import get_custom_css

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Analytics", layout="wide", page_icon="🔒")
st.markdown(get_custom_css(), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔒 Company Knowledge Assistant")
    st.caption("Analytics Dashboard")

st.title("Analytics Dashboard")
st.caption("Usage patterns, knowledge gaps, and security events across all queries.")

try:
    response = requests.get(f"{API_URL}/analytics/logs", timeout=30)
    response.raise_for_status()
    logs = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Could not load analytics: {e}")
    logs = []

if not logs:
    st.info("No queries logged yet. Ask a few questions on the Chat page first.")
    st.stop()

df = pd.DataFrame(logs)
df["timestamp"] = pd.to_datetime(df["timestamp"])

total_queries = len(df)
allowed = len(df[df["status"] == "allowed"])
blocked = total_queries - allowed
block_rate = (blocked / total_queries * 100) if total_queries else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Queries", total_queries)
col2.metric("Allowed", allowed)
col3.metric("Blocked", blocked)
col4.metric("Block Rate", f"{block_rate:.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Queries by Role")
    role_counts = df["user_role"].value_counts()
    st.bar_chart(role_counts)

with col2:
    st.subheader("🔐 Security Events")
    security_df = df[df["status"] != "allowed"]
    if security_df.empty:
        st.success("No security events recorded — no blocked or flagged queries.")
    else:
        status_counts = security_df["status"].value_counts()
        st.bar_chart(status_counts)

st.markdown("---")

st.subheader("💬 Most Frequent Questions")
top_questions = df["query"].value_counts().head(10)
st.dataframe(top_questions.reset_index().rename(columns={"index": "Question", "query": "Count"}), use_container_width=True)

st.markdown("---")

st.subheader("🕳️ Potential Knowledge Gaps")
st.caption("Queries that were allowed but returned no source documents — may indicate missing content in the knowledge base.")
gaps_df = df[(df["status"] == "allowed") & (df["sources"].isin(["[]", "", None]))]
if gaps_df.empty:
    st.success("No knowledge gaps detected.")
else:
    st.dataframe(gaps_df[["timestamp", "user_role", "query"]], use_container_width=True)

st.markdown("---")

st.subheader("📋 Full Audit Log")
display_df = df[["timestamp", "user_role", "query", "status", "block_reason", "sources"]].copy()
display_df = display_df.sort_values("timestamp", ascending=False)
st.dataframe(display_df, use_container_width=True, height=400)