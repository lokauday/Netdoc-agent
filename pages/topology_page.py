import streamlit as st
from auth_engine import current_user
from utils.parser import parse_config
from main import generate_topology_mermaid


def topology_page():
    user = current_user()
    if not user:
        st.warning("You must be logged in.")
        st.stop()

    st.title("🌐 Topology Builder")

    config = st.text_area("Paste configuration", height=300)

    if st.button("Generate Topology"):
        parsed = parse_config(config)
        topo = generate_topology_mermaid(parsed["raw"])

        st.subheader("Topology Diagram")
        st.markdown(f"```mermaid\n{topo}\n```")
