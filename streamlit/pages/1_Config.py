"""
Configuration page for customizing prompts and company context.
"""

import streamlit as st

st.set_page_config(
    page_title="Config - Chloé",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Configuration")
st.markdown("Customize your company context and prompt templates.")

# Initialize session state
if "company_context" not in st.session_state:
    st.session_state.company_context = """# Your Company Context

Describe your company here. Include:
- Company name and description
- Products/services offered
- Target audience
- Value proposition
- Key differentiators

This context will be used by the AI to generate relevant insights and outreach messages.
"""

if "profile_prompt" not in st.session_state:
    st.session_state.profile_prompt = ""

if "interactions_prompt" not in st.session_state:
    st.session_state.interactions_prompt = ""

if "outreach_prompt" not in st.session_state:
    st.session_state.outreach_prompt = ""

# Company Context
st.header("Company Context")
st.markdown("This replaces the default company context used in all prompts.")
company_context = st.text_area(
    "Company Context",
    value=st.session_state.company_context,
    height=300,
    key="company_context_input",
)
st.session_state.company_context = company_context

# Custom Prompts
st.header("Custom Prompts (Optional)")
st.markdown("Leave empty to use default prompts. Use placeholders like `{le_wagon_context}`, `{full_name}`, etc.")

with st.expander("Profile Insight Prompt"):
    st.markdown("""
    **Available placeholders:**
    `{le_wagon_context}`, `{insights_languages}`, `{date_now}`, `{full_name}`, `{headline}`,
    `{current_title}`, `{current_company}`, `{location}`, `{languages}`,
    `{experiences_summary}`, `{educations_summary}`, `{certifications_summary}`
    """)
    profile_prompt = st.text_area(
        "Profile Insight Prompt",
        value=st.session_state.profile_prompt,
        height=200,
        key="profile_prompt_input",
        label_visibility="collapsed",
    )
    st.session_state.profile_prompt = profile_prompt

with st.expander("Interactions Insight Prompt"):
    st.markdown("""
    **Available placeholders:**
    `{le_wagon_context}`, `{insights_languages}`, `{date_now}`, `{full_name}`,
    `{current_title}`, `{current_company}`, `{posts_count}`, `{posts_summary}`,
    `{reactions_count}`, `{reactions_summary}`
    """)
    interactions_prompt = st.text_area(
        "Interactions Insight Prompt",
        value=st.session_state.interactions_prompt,
        height=200,
        key="interactions_prompt_input",
        label_visibility="collapsed",
    )
    st.session_state.interactions_prompt = interactions_prompt

with st.expander("Outreach Messages Prompt"):
    st.markdown("""
    **Available placeholders:**
    `{le_wagon_context}`, `{date_now}`, `{full_name}`, `{first_name}`,
    `{current_title}`, `{current_company}`, `{languages}`, `{outreach_messages_languages}`,
    `{profile_insight_summary}`, `{interactions_insight_summary}`, `{recent_posts_for_comments}`
    """)
    outreach_prompt = st.text_area(
        "Outreach Messages Prompt",
        value=st.session_state.outreach_prompt,
        height=200,
        key="outreach_prompt_input",
        label_visibility="collapsed",
    )
    st.session_state.outreach_prompt = outreach_prompt

# Save indicator
st.success("Configuration is automatically saved in session state.")
