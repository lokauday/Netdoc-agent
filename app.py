import os
import json
import streamlit as st
from openai import OpenAI
from utils.parser import parse_config

# ----------- LOAD API KEY -----------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ----------- PAGE CONFIG -----------
st.set_page_config(page_title="NetDoc AI", layout="wide")

# ----------- LOGO -----------
st.image("https://i.imgur.com/NU9cu5S.png", width=180)

# ----------- TITLE -----------
st.title("⚡ NetDoc AI — Autonomous Network Documentation Engine")
st.write("Upload Cisco configs → AI generates documentation, auditing & exports.")

# ----------- FILE UPLOAD -----------
uploaded_files = st.file_uploader(
    "Upload one or more config files",
    type=["txt", "cfg", "log"],
    accept_multiple_files=True
)

# ----------- MAIN TABS -----------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📄 Overview", "🛡 Security Audit", "🗺 Topology", "📤 Export"]
)

# ⭕ TAB 1 — Overview -----------------------------------------
with tab1:
    st.subheader("📄 Overview Documentation")

    if uploaded_files and st.button("Generate Report"):
        combined = ""

        for f in uploaded_files:
            combined += f"\n\n# FILE: {f.name}\n"
            combined += f.read().decode("utf-8")

        with st.spinner("Processing configs..."):
            result = parse_config(combined)

        st.session_state["report"] = result
        st.session_state["report_markdown"] = json.dumps(result, indent=2)

        st.success("Report generated successfully!")
        st.json(result)

    else:
        st.info("Upload configs & click **Generate Report** to begin.")


# ⭕ TAB 2 — Security Audit -----------------------------------
with tab2:
    st.subheader("🛡 Security Audit (Coming in Step C-5)")

    if "report" in st.session_state:
        st.success("Security audit will be generated in the next step.")
    else:
        st.info("Generate a report first.")


# ⭕ TAB 3 — Topology -----------------------------------------
with tab3:
    st.subheader("🗺 AI Topology Diagram (Coming in Step C-6)")

    if "report" in st.session_state:
        st.success("Topology generation will be added in the next step.")
    else:
        st.info("Generate a report first.")


# ⭕ TAB 4 — Export -------------------------------------------
with tab4:
    st.subheader("📤 Export Options")

    if "report_markdown" in st.session_state:
        st.success("PDF, DOCX, HTML export will be added in Step C-7.")
    else:
        st.info("Generate a report first.")
