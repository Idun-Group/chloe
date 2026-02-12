"""
Analysis page for LinkedIn profile analysis.
"""

import streamlit as st
import requests

st.set_page_config(
    page_title="Analyze - Chloé",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Analyze LinkedIn Profile")

API_URL = "http://localhost:8001/agent/invoke"

# Input section
st.header("Input")

linkedin_url = st.text_input(
    "LinkedIn URL",
    placeholder="https://www.linkedin.com/in/firstname-lastname/",
)

col1, col2 = st.columns(2)

with col1:
    posts_limit = st.slider("Posts Limit", min_value=1, max_value=100, value=10)

with col2:
    reactions_limit = st.slider("Reactions Limit", min_value=1, max_value=100, value=10)

language = st.selectbox(
    "Insights Language",
    options=[
        "English",
        "French",
        "Spanish",
        "German",
        "Italian",
        "Portuguese",
        "Dutch",
        "Polish",
        "Russian",
        "Chinese",
        "Japanese",
        "Korean",
        "Arabic",
    ],
    index=1,  # French as default
)

st.subheader("Insights to Generate")
col1, col2, col3 = st.columns(3)

with col1:
    get_profile_insight = st.checkbox("Profile Insight", value=True)

with col2:
    get_interactions_insight = st.checkbox("Interactions Insight", value=True)

with col3:
    get_outreach_messages = st.checkbox("Outreach Messages", value=True)

get_raw_data = st.checkbox("Include Raw Data", value=False)

# Analyze button
if st.button("Analyze", type="primary", disabled=not linkedin_url):
    with st.spinner("Analyzing LinkedIn profile..."):
        payload = {
            "linkedin_url": linkedin_url,
            "posts_limit": posts_limit,
            "reactions_limit": reactions_limit,
            "insights_languages": language,
            "get_profile_insight": get_profile_insight,
            "get_interactions_insight": get_interactions_insight,
            "get_outreach_messages": get_outreach_messages,
            "get_raw_data": get_raw_data,
        }

        # Add custom prompts from session state if configured
        if (
            st.session_state.get("company_context")
            and st.session_state.company_context.strip()
        ):
            payload["custom_company_context"] = st.session_state.company_context

        if (
            st.session_state.get("profile_prompt")
            and st.session_state.profile_prompt.strip()
        ):
            payload["custom_profile_prompt"] = st.session_state.profile_prompt

        if (
            st.session_state.get("interactions_prompt")
            and st.session_state.interactions_prompt.strip()
        ):
            payload["custom_interactions_prompt"] = st.session_state.interactions_prompt

        if (
            st.session_state.get("outreach_prompt")
            and st.session_state.outreach_prompt.strip()
        ):
            payload["custom_outreach_prompt"] = st.session_state.outreach_prompt

        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            st.success("Analysis complete!")

            # Display results in tabs
            tabs = st.tabs(
                [
                    "Lead Info",
                    "Profile Insight",
                    "Interactions Insight",
                    "Outreach Messages",
                    "Raw Response",
                ]
            )

            with tabs[0]:
                st.subheader("Lead Information")
                lead = result.get("lead", {})
                if lead:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Name:** {lead.get('full_name', 'N/A')}")
                        st.markdown(f"**Title:** {lead.get('current_title', 'N/A')}")
                        st.markdown(
                            f"**Company:** {lead.get('current_company', 'N/A')}"
                        )
                    with col2:
                        st.markdown(f"**Location:** {lead.get('location', 'N/A')}")
                        st.markdown(f"**Languages:** {lead.get('languages', 'N/A')}")
                        st.markdown(f"**Headline:** {lead.get('headline', 'N/A')}")

            with tabs[1]:
                st.subheader("Profile Insight")
                insights = result.get("insights", {})
                profile_insight = insights.get("profile_insight")
                if profile_insight:
                    st.markdown(f"**Summary:** {profile_insight.get('summary', 'N/A')}")
                    st.markdown(
                        f"**Work Experience:** {profile_insight.get('work_experience_summary', 'N/A')}"
                    )
                    st.markdown(
                        f"**Education:** {profile_insight.get('education_summary', 'N/A')}"
                    )

                    if profile_insight.get("topics_of_interest"):
                        st.markdown("**Topics of Interest:**")
                        for topic in profile_insight["topics_of_interest"]:
                            st.markdown(f"- {topic}")

                    if profile_insight.get("keywords"):
                        st.markdown(
                            f"**Keywords:** {', '.join(profile_insight['keywords'])}"
                        )

                    st.markdown(
                        f"**Confidence:** {profile_insight.get('confidence', 'N/A')}"
                    )
                else:
                    st.info("Profile insight not generated or not requested.")

            with tabs[2]:
                st.subheader("Interactions Insight")
                interactions_insight = insights.get("interactions_insight")
                if interactions_insight:
                    st.markdown(
                        f"**Summary:** {interactions_insight.get('summary', 'N/A')}"
                    )
                    st.markdown(
                        f"**Engagement Style:** {interactions_insight.get('engagement_style', 'N/A')}"
                    )

                    if interactions_insight.get("pain_points"):
                        st.markdown("**Pain Points:**")
                        for point in interactions_insight["pain_points"]:
                            st.markdown(f"- {point}")

                    if interactions_insight.get("approach_angles"):
                        st.markdown("**Approach Angles:**")
                        for angle in interactions_insight["approach_angles"]:
                            st.markdown(f"- {angle}")

                    st.markdown(
                        f"**Confidence:** {interactions_insight.get('confidence', 'N/A')}"
                    )
                else:
                    st.info("Interactions insight not generated or not requested.")

            with tabs[3]:
                st.subheader("Outreach Messages")
                outreach = insights.get("outreach_messages")
                if outreach:
                    st.markdown(f"**Summary:** {outreach.get('summary', 'N/A')}")
                    st.markdown(f"**Language:** {outreach.get('languages', 'N/A')}")

                    if outreach.get("post_comments"):
                        st.markdown("**Post Comments:**")
                        for comment in outreach["post_comments"]:
                            with st.expander(
                                f"Comment for {comment.get('post_id', 'Unknown')}"
                            ):
                                st.markdown(comment.get("comment", "N/A"))
                                if comment.get("post_url"):
                                    st.markdown(f"[View Post]({comment['post_url']})")

                    if outreach.get("linkedin_messages"):
                        st.markdown("**LinkedIn Messages:**")
                        messages = outreach["linkedin_messages"]
                        with st.expander("Initial Message"):
                            st.markdown(messages.get("initial", "N/A"))
                        with st.expander("Follow-up Day 3"):
                            st.markdown(messages.get("follow_up_day3", "N/A"))
                        with st.expander("Follow-up Day 7"):
                            st.markdown(messages.get("follow_up_day7", "N/A"))

                    if outreach.get("emails"):
                        st.markdown("**Emails:**")
                        emails = outreach["emails"]
                        if emails.get("initial"):
                            with st.expander("Initial Email"):
                                st.markdown(
                                    f"**Subject:** {emails['initial'].get('subject', 'N/A')}"
                                )
                                st.markdown(emails["initial"].get("body_text", "N/A"))

                    st.markdown(f"**Confidence:** {outreach.get('confidence', 'N/A')}")
                else:
                    st.info("Outreach messages not generated or not requested.")

            with tabs[4]:
                st.subheader("Raw Response")
                st.json(result)

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the API. Make sure the backend is running at localhost:8000"
            )
        except requests.exceptions.Timeout:
            st.error("Request timed out. The analysis is taking too long.")
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
