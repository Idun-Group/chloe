"""
Chloé Streamlit Frontend
Main entry point for the multi-page Streamlit app.
"""

import streamlit as st

st.set_page_config(
    page_title="Chloé - LinkedIn Lead Analyzer",
    page_icon="🔍",
    layout="wide",
)

st.title("Chloé - LinkedIn Lead Analyzer")
st.markdown("""
Welcome to Chloé, an AI-powered LinkedIn lead analysis tool.

### Pages

- **Config**: Configure your prompts and company context
- **Analyze**: Analyze LinkedIn profiles and generate insights

### Getting Started

1. Go to the **Config** page to customize your company context and prompts (optional)
2. Go to the **Analyze** page to enter a LinkedIn URL and get AI-powered insights

Make sure the backend is running at `localhost:8000`.
""")
