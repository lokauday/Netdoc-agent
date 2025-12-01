import streamlit as st
from auth import login_required

def ai_docs_page():
    login_required()

    st.title("🤖 AI Documentation Engine")

    data = st.session_state.get("ai_docs")
    if not data:
        st.warning("Generate AI docs from the Upload page first.")
        return

    st.subheader("📌 Summary")
    st.write(data.get("summary"))

    st.subheader("📘 Section Explanations")
    st.write(data.get("explanation"))

    st.subheader("🏆 Best Practices")
    st.write(data.get("best_practices"))

    st.subheader("🛠 Recommendations")
    st.write(data.get("recommendations"))
