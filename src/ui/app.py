"""
Streamlit UI for Social Support Application Demo, with stable session_state handling.
"""

import os
import json
import base64
import requests
import streamlit as st
from src.core.agent_orchestrator import AgentOrchestrator

CONNECT_TIMEOUT = float(os.getenv("CHATBOT_CONNECT_TIMEOUT", 5))
READ_TIMEOUT    = float(os.getenv("CHATBOT_READ_TIMEOUT", 120))

# ────────────────────────────────────────────────────────────────────────────────
# Initialize session_state defaults so 'documents' always exists
# ────────────────────────────────────────────────────────────────────────────────
if "documents" not in st.session_state:
    st.session_state.documents = []

# ────────────────────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Social Support AI Demo", layout="centered")
st.title("Social Support Application Demo")

# ────────────────────────────────────────────────────────────────────────────────
# Application Form
# ────────────────────────────────────────────────────────────────────────────────
with st.form("application_form"):
    applicant_id = st.text_input("Applicant ID", max_chars=50)
    income       = st.number_input("Monthly Income", min_value=0.0, step=0.01, format="%.2f")
    family_size  = st.number_input("Family Size", min_value=1, step=1)
    docs         = st.file_uploader("Upload Documents (PDF/Image)", accept_multiple_files=True)
    submitted    = st.form_submit_button("Submit Application")

if submitted:
    if not applicant_id:
        st.error("Please enter an Applicant ID.")
    else:
        # Build and store documents in session_state
        st.session_state.documents = []
        for f in docs or []:
            raw  = f.read()
            mime = f.type or "application/octet-stream"
            b64  = base64.b64encode(raw).decode("utf-8")
            st.session_state.documents.append(f"data:{mime};base64,{b64}")

        # Now safe to reference session_state.documents
        payload = {
            "applicant_id": applicant_id,
            "income":       income,
            "family_size":  family_size,
            "documents":    st.session_state.documents,
        }

        api_url = os.environ["API_URL"].rstrip("/")
        try:
            resp = requests.post(
                f"{api_url}/application/",
                json=payload,
                timeout=(10, 120)
            )
            resp.raise_for_status()
            data = resp.json()

            st.subheader("Decision Results")
            st.write(f"**Application ID:** {data['application_id']}")
            st.write(f"**Eligibility:** {data['eligibility']}")
            st.write(f"**Recommendation:** {data['recommendation']}")
            st.write(f"**Final Decision:** {data['final_decision']}")
        except Exception as e:
            st.error(f"Submission error: {e}")

st.markdown("---")

# ────────────────────────────────────────────────────────────────────────────────
# Chat with GenAI Bot (single JSON response)
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("Chat with GenAI Bot")
chat_input = st.text_input("You:")

if st.button("Send Chat"):
    if not chat_input:
        st.error("Please enter a message to send.")
    else:
        api_url = os.getenv("API_URL", "http://localhost:8001").rstrip("/")
        payload = {
            "user_id": applicant_id or "anonymous",
            "messages": [chat_input],
            "context": {},
        }

        try:
            # NOTE: no stream=True— we now expect a single JSON payload
            resp = requests.post(
                f"{api_url}/chatbot/",
                json=payload,
                stream=True,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            )
            resp.raise_for_status()
            data = resp.json()

            # Display each response in the array
            for msg in data.get("responses", []):
                st.write(f"Bot: {msg}")

        except Exception as e:
            st.error(f"Chatbot error: {e}")