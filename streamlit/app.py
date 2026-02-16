"""
Chloé - Assistant IA de Prospection LinkedIn
"""

import streamlit as st
import requests
import time
import threading

st.set_page_config(
    page_title="Chloé - Prospection IA",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background-color: #0f0f1a;
    }
    section[data-testid="stSidebar"] {
        background-color: #16162a;
        border-right: 1px solid #2a2a4a;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input {
        background-color: #1e1e3a !important;
        border: 1px solid #3a3a5a !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0 2.5rem 0;
    }
    .main-header h1 {
        font-size: 3.5rem;
        color: #fff;
        margin-bottom: 0.5rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    .main-header .subtitle {
        color: #5865F2;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .main-header .description {
        color: #999;
        font-size: 1rem;
        max-width: 550px;
        margin: 0 auto 1.5rem;
        line-height: 1.6;
    }
    .main-header .powered-by {
        display: inline-flex;
        align-items: center;
        gap: 1rem;
        background-color: #16162a;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        border: 1px solid #2a2a4a;
        font-size: 0.85rem;
        color: #888;
    }
    .main-header .powered-by a {
        color: #5865F2;
        text-decoration: none;
        font-weight: 600;
    }
    .main-header .powered-by a:hover {
        text-decoration: underline;
    }
    .stTextArea > div > div > textarea {
        background-color: #1e1e3a !important;
        border: 1px solid #3a3a5a !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
    }
    .stTextInput > div > div > input {
        background-color: #1e1e3a !important;
        border: 1px solid #3a3a5a !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background-color: #5865F2;
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: #4752C4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #16162a;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        color: #888;
        padding: 12px 24px;
        font-size: 1rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #5865F2;
        color: white;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1.5rem 0;
    }
    .stExpander {
        background-color: #16162a;
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .stExpander > div > div > div > div {
        color: #e2e8f0;
    }
    .loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
    }
    .loader {
        width: 50px;
        height: 50px;
        border: 4px solid #2a2a4a;
        border-top-color: #5865F2;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    .loader-text {
        color: #888;
        font-size: 1rem;
        margin-top: 1rem;
    }
    .section-title {
        color: #5865F2;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 1.5rem 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .result-card {
        background-color: #16162a;
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .result-label {
        color: #5865F2;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .result-value {
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.6;
    }
    .lead-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 8px;
    }
    .lead-title {
        color: #e2e8f0;
        font-size: 1.1rem;
        margin-bottom: 12px;
    }
    .lead-meta {
        color: #888;
        font-size: 0.9rem;
    }
    .tag {
        display: inline-block;
        background-color: #2a2a4a;
        border: 1px solid #3a3a5a;
        color: #e2e8f0;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 4px 4px 4px 0;
    }
    .insight-section {
        background-color: #16162a;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 4px solid #5865F2;
    }
    .message-box {
        background-color: #1e1e3a;
        border: 1px solid #3a3a5a;
        border-radius: 12px;
        padding: 16px;
        color: #e2e8f0;
        line-height: 1.7;
        white-space: pre-wrap;
    }
    [data-testid="stJson"] {
        max-height: 500px;
        overflow-y: auto;
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.85rem;
        border-top: 1px solid #2a2a4a;
        margin-top: 2rem;
    }
    .footer a {
        color: #5865F2;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
</style>
""",
    unsafe_allow_html=True,
)

DEFAULT_CONTEXT = """# Contexte de l'entreprise

Nom: [Nom de l'entreprise]
Description: [Ce que fait votre entreprise]
Site: [https://votreentreprise.com]

## Produits & Services

[Vos principales offres]

## Clients cibles

[Profil client idéal]

## Proposition de valeur

[Ce qui vous rend unique]

## Arguments de vente

1. [Premier argument]
2. [Deuxième argument]
3. [Troisième argument]
"""

if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "company_context" not in st.session_state:
    st.session_state.company_context = DEFAULT_CONTEXT
if "results" not in st.session_state:
    st.session_state.results = None

API_URL = "http://localhost:8001/agent/invoke"

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    st.caption("Nom de votre entreprise pour personnaliser les messages")
    company_name = st.text_input(
        "Nom entreprise",
        value=st.session_state.company_name,
        placeholder="Votre entreprise",
        label_visibility="collapsed",
    )
    st.session_state.company_name = company_name

    st.markdown("---")

    st.caption("Nombre de posts LinkedIn à analyser")
    posts_limit = st.number_input("Posts", 1, 50, 10, label_visibility="collapsed")

    st.caption("Nombre de réactions LinkedIn à analyser")
    reactions_limit = st.number_input(
        "Réactions", 1, 50, 10, label_visibility="collapsed"
    )

    st.caption("Langue des insights générés")
    language = st.selectbox(
        "Langue",
        ["French", "English", "Spanish", "German"],
        label_visibility="collapsed",
    )

st.markdown(
    """
<div class="main-header">
    <h1>🎯 Chloé</h1>
    <p class="subtitle">Assistant IA de Prospection LinkedIn</p>
    <p class="description">
        Analysez un profil LinkedIn et obtenez des insights détaillés sur le lead,
        ses centres d'intérêt, et des messages de prospection personnalisés.
    </p>
    <div class="powered-by">
        <span>Powered by <a href="https://github.com/Idun-Group/idun-agent-platform" target="_blank">Idun Agent Platform</a> ⭐</span>
        <span>·</span>
        <span>By <a href="https://www.idun-group.com/" target="_blank">Idun Group</a></span>
        <span>·</span>
        <span>📧 contact@idun-group.com</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.caption("URL du profil LinkedIn à analyser")
col1, col2 = st.columns([5, 1])
with col1:
    linkedin_url = st.text_input(
        "URL LinkedIn",
        value="https://www.linkedin.com/in/geoffrey-harrazi9/",
        placeholder="https://www.linkedin.com/in/prenom-nom/",
        label_visibility="collapsed",
    )
with col2:
    analyze_btn = st.button("🚀 Analyser", disabled=not linkedin_url, use_container_width=True)

if "context_expanded" not in st.session_state:
    st.session_state.context_expanded = True

st.caption(
    "Décrivez votre entreprise, vos produits, vos clients cibles et votre proposition de valeur. Plus le contexte est riche, plus les messages seront pertinents."
)
with st.expander("📝 Contexte Entreprise", expanded=st.session_state.context_expanded):
    company_context = st.text_area(
        "Contexte",
        value=st.session_state.company_context,
        height=350,
        label_visibility="collapsed",
    )
    st.session_state.company_context = company_context

if analyze_btn:
    loader_placeholder = st.empty()

    payload = {
        "linkedin_url": linkedin_url,
        "posts_limit": posts_limit,
        "reactions_limit": reactions_limit,
        "insights_languages": language,
        "get_profile_insight": True,
        "get_interactions_insight": True,
        "get_outreach_messages": True,
        "get_raw_data": False,
    }

    if st.session_state.company_name.strip():
        payload["company_name"] = st.session_state.company_name
    if st.session_state.company_context.strip():
        payload["custom_company_context"] = st.session_state.company_context

    result_container = {"result": None, "error": None, "done": False}

    def make_request():
        try:
            response = requests.post(API_URL, json=payload, timeout=300)
            response.raise_for_status()
            result_container["result"] = response.json()
        except requests.exceptions.ConnectionError:
            result_container["error"] = "Impossible de se connecter à l'API."
        except requests.exceptions.Timeout:
            result_container["error"] = "Timeout."
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            result_container["done"] = True

    thread = threading.Thread(target=make_request)
    thread.start()

    while not result_container["done"]:
        loader_placeholder.markdown(
            """
        <div class='loader-container'>
            <div class='loader'></div>
            <div class='loader-text'>Analyse en cours...</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        time.sleep(0.5)

    loader_placeholder.empty()

    if result_container["error"]:
        st.error(f"❌ {result_container['error']}")
    else:
        st.session_state.results = result_container["result"]
        st.session_state.context_expanded = False
        st.rerun()

if st.session_state.results:
    result = st.session_state.results
    st.markdown(
        "<hr style='border: none; border-top: 1px solid #2a2a4a; margin: 2rem 0;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='color: #fff; font-size: 1.5rem; margin-bottom: 1rem;'>Résultats de l'analyse</h2>",
        unsafe_allow_html=True,
    )

    insights = result.get("insights", {})
    profile_insight = insights.get("profile_insight") or result.get("profile_insight")
    interactions_insight = insights.get("interactions_insight") or result.get(
        "interactions_insight"
    )
    outreach_messages = insights.get("outreach_messages") or result.get(
        "outreach_messages"
    )

    tabs = st.tabs(
        ["👤 Lead", "📊 Profil", "💬 Interactions", "📧 Outreach", "📄 JSON"]
    )

    with tabs[0]:
        lead = result.get("lead", {})
        if lead:
            st.markdown(
                f"<div class='lead-name'>{lead.get('full_name', 'N/A')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='lead-title'><strong>{lead.get('current_title', '')}</strong> @ {lead.get('current_company', '')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='lead-meta'>📍 {lead.get('location', 'N/A')} · 🌐 {lead.get('languages', 'N/A')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color: #94a3b8; margin-top: 12px; font-style: italic;'>{lead.get('headline', '')}</div>",
                unsafe_allow_html=True,
            )

    with tabs[1]:
        if profile_insight:
            st.markdown(
                f"""
            <div class='insight-section'>
                <div class='result-label'>Résumé</div>
                <div class='result-value'>{profile_insight.get("summary", "N/A")}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""
                <div class='insight-section'>
                    <div class='result-label'>Expérience</div>
                    <div class='result-value'>{profile_insight.get("work_experience_summary", "N/A")}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""
                <div class='insight-section'>
                    <div class='result-label'>Formation</div>
                    <div class='result-value'>{profile_insight.get("education_summary", "N/A")}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            if profile_insight.get("topics_of_interest"):
                st.markdown(
                    "<div class='result-label' style='margin-top: 16px;'>Sujets d'intérêt</div>",
                    unsafe_allow_html=True,
                )
                tags_html = "".join(
                    [
                        f"<span class='tag'>{topic}</span>"
                        for topic in profile_insight["topics_of_interest"]
                    ]
                )
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

            if profile_insight.get("keywords"):
                st.markdown(
                    "<div class='result-label' style='margin-top: 16px;'>Mots-clés</div>",
                    unsafe_allow_html=True,
                )
                tags_html = "".join(
                    [
                        f"<span class='tag'>{kw}</span>"
                        for kw in profile_insight["keywords"]
                    ]
                )
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
        else:
            st.info("Non généré")

    with tabs[2]:
        if interactions_insight:
            st.markdown(
                f"""
            <div class='insight-section'>
                <div class='result-label'>Résumé</div>
                <div class='result-value'>{interactions_insight.get("summary", "N/A")}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
            <div class='insight-section'>
                <div class='result-label'>Style d'engagement</div>
                <div class='result-value'>{interactions_insight.get("engagement_style", "N/A")}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                if interactions_insight.get("pain_points"):
                    st.markdown(
                        "<div class='result-label'>Points de douleur</div>",
                        unsafe_allow_html=True,
                    )
                    for point in interactions_insight["pain_points"]:
                        st.markdown(
                            f"<div style='color: #fca5a5; padding: 8px 0;'>• {point}</div>",
                            unsafe_allow_html=True,
                        )

            with col2:
                if interactions_insight.get("approach_angles"):
                    st.markdown(
                        "<div class='result-label'>Angles d'approche</div>",
                        unsafe_allow_html=True,
                    )
                    for angle in interactions_insight["approach_angles"]:
                        st.markdown(
                            f"<div style='color: #86efac; padding: 8px 0;'>• {angle}</div>",
                            unsafe_allow_html=True,
                        )
        else:
            st.info("Non généré")

    with tabs[3]:
        if outreach_messages:
            st.markdown(
                f"""
            <div class='insight-section'>
                <div class='result-label'>Stratégie</div>
                <div class='result-value'>{outreach_messages.get("summary", "N/A")}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if outreach_messages.get("linkedin_messages"):
                linkedin_messages = outreach_messages["linkedin_messages"]
                st.markdown(
                    "<div class='result-label' style='margin: 20px 0 12px 0;'>Messages LinkedIn</div>",
                    unsafe_allow_html=True,
                )

                with st.expander("💬 Message initial", expanded=True):
                    st.markdown(
                        f"<div class='message-box'>{linkedin_messages.get('initial', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
                with st.expander("💬 Relance J+3"):
                    st.markdown(
                        f"<div class='message-box'>{linkedin_messages.get('follow_up_day3', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
                with st.expander("💬 Relance J+7"):
                    st.markdown(
                        f"<div class='message-box'>{linkedin_messages.get('follow_up_day7', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )

            if outreach_messages.get("emails") and outreach_messages["emails"].get(
                "initial"
            ):
                st.markdown(
                    "<div class='result-label' style='margin: 20px 0 12px 0;'>Email</div>",
                    unsafe_allow_html=True,
                )
                with st.expander("📧 Email initial", expanded=True):
                    email = outreach_messages["emails"]["initial"]
                    st.markdown(
                        f"<div style='color: #667eea; font-weight: 600; margin-bottom: 8px;'>Objet: {email.get('subject', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div class='message-box'>{email.get('body_text', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Non généré")

    with tabs[4]:
        st.json(result)
