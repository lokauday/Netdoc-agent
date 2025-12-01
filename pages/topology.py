import streamlit as st
from auth import login_required
from topology_engine import generate_topology_mermaid

def topology_page():
    login_required()
    st.title("🌐 Network Topology")

    if "parsed" not in st.session_state:
        st.error("Upload a config first.")
        return

    parsed = st.session_state.parsed
    topology = generate_topology_mermaid(parsed)
    st.session_state.topology = topology

    st.markdown(f"""
    ```mermaid
    {topology}
    ```
    """)
