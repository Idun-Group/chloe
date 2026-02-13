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
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] .stTextArea > div > div > textarea {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
        min-height: 500px !important;
    }
    section[data-testid="stSidebar"] .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    .main-header h1 {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        color: #a0aec0;
        font-size: 1.1rem;
    }
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #fff !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        color: #a0aec0;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stExpander {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    .loading-text {
        text-align: center;
        color: #667eea;
        font-size: 1.3rem;
        padding: 2rem;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .stNumberInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #fff !important;
    }
    .sidebar-title {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .sidebar-hint {
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 1rem;
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

[Profil client idéal - secteurs, postes, problèmes résolus]

## Proposition de valeur

[Ce qui vous rend unique]

## Style de communication

[Ton de votre marque]

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

# Sidebar - Company Context
with st.sidebar:
    st.markdown(
        "<p class='sidebar-title'>📝 Contexte Entreprise</p>", unsafe_allow_html=True
    )

    company_name = st.text_input(
        "Nom",
        value=st.session_state.company_name,
        placeholder="Votre entreprise",
    )
    st.session_state.company_name = company_name

    st.markdown(
        "<p class='sidebar-hint'>Décrivez votre entreprise pour personnaliser les insights et messages de prospection.</p>",
        unsafe_allow_html=True,
    )

    company_context = st.text_area(
        "Contexte",
        value=st.session_state.company_context,
        height=600,
        label_visibility="collapsed",
    )
    st.session_state.company_context = company_context

# Main content
st.markdown(
    """
<div class="main-header">
    <h1>🎯 Chloé</h1>
    <p>Assistant IA de Prospection LinkedIn</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### 🔍 Analyser un profil")

linkedin_url = st.text_input(
    "URL LinkedIn",
    placeholder="https://www.linkedin.com/in/prenom-nom/",
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    posts_limit = st.number_input("Posts", 1, 50, 10)
with col2:
    reactions_limit = st.number_input("Réactions", 1, 50, 10)
with col3:
    language = st.selectbox("Langue", ["French", "English", "Spanish", "German"])
with col4:
    get_profile = st.checkbox("Profil", value=True)
    get_interactions = st.checkbox("Interactions", value=True)
with col5:
    get_outreach = st.checkbox("Outreach", value=True)

st.markdown("")

if st.button("🚀 Analyser", disabled=not linkedin_url, use_container_width=True):
    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    steps = [
        "🔄 Connexion à LinkedIn...",
        "📊 Récupération du profil...",
        "📝 Analyse des posts...",
        "🔍 Analyse des réactions...",
        "🧠 Génération des insights IA...",
        "✨ Finalisation...",
    ]

    progress_bar = progress_placeholder.progress(0)

    payload = {
        "linkedin_url": linkedin_url,
        "posts_limit": posts_limit,
        "reactions_limit": reactions_limit,
        "insights_languages": language,
        "get_profile_insight": get_profile,
        "get_interactions_insight": get_interactions,
        "get_outreach_messages": get_outreach,
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
            result_container["error"] = (
                "Impossible de se connecter à l'API. Vérifiez que le backend tourne."
            )
        except requests.exceptions.Timeout:
            result_container["error"] = "Timeout - L'analyse prend trop de temps."
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            result_container["done"] = True

    thread = threading.Thread(target=make_request)
    thread.start()

    step_idx = 0
    progress = 0
    while not result_container["done"]:
        status_placeholder.markdown(
            f"<p class='loading-text'>{steps[step_idx % len(steps)]}</p>",
            unsafe_allow_html=True,
        )
        progress = min(progress + 1, 90)
        progress_bar.progress(progress)
        step_idx += 1
        time.sleep(2)

    progress_bar.progress(100)
    time.sleep(0.3)
    progress_placeholder.empty()
    status_placeholder.empty()

    if result_container["error"]:
        st.error(f"❌ {result_container['error']}")
    else:
        st.session_state.results = result_container["result"]
        st.success("✅ Analyse terminée!")
        st.rerun()

if st.session_state.results:
    result = st.session_state.results
    st.markdown("---")

    tabs = st.tabs(
        ["👤 Lead", "📊 Profil", "💬 Interactions", "📧 Outreach", "📄 JSON"]
    )

    with tabs[0]:
        lead = result.get("lead", {})
        if lead:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nom:** {lead.get('full_name', 'N/A')}")
                st.markdown(f"**Titre:** {lead.get('current_title', 'N/A')}")
                st.markdown(f"**Entreprise:** {lead.get('current_company', 'N/A')}")
            with col2:
                st.markdown(f"**Localisation:** {lead.get('location', 'N/A')}")
                st.markdown(f"**Langues:** {lead.get('languages', 'N/A')}")
            st.markdown(f"**Headline:** {lead.get('headline', 'N/A')}")

    with tabs[1]:
        insights = result.get("insights", {})
        pi = insights.get("profile_insight")
        if pi:
            st.markdown(f"**Résumé:** {pi.get('summary', 'N/A')}")
            st.markdown(f"**Expérience:** {pi.get('work_experience_summary', 'N/A')}")
            st.markdown(f"**Formation:** {pi.get('education_summary', 'N/A')}")
            if pi.get("topics_of_interest"):
                st.markdown(
                    "**Sujets d'intérêt:** " + ", ".join(pi["topics_of_interest"])
                )
            if pi.get("keywords"):
                st.markdown("**Mots-clés:** " + ", ".join(pi["keywords"]))
            st.markdown(f"**Confiance:** {pi.get('confidence', 'N/A')}")
        else:
            st.info("Non généré")

    with tabs[2]:
        ii = insights.get("interactions_insight")
        if ii:
            st.markdown(f"**Résumé:** {ii.get('summary', 'N/A')}")
            st.markdown(f"**Style:** {ii.get('engagement_style', 'N/A')}")
            if ii.get("pain_points"):
                st.markdown("**Points de douleur:**")
                for p in ii["pain_points"]:
                    st.markdown(f"• {p}")
            if ii.get("approach_angles"):
                st.markdown("**Angles d'approche:**")
                for a in ii["approach_angles"]:
                    st.markdown(f"• {a}")
            st.markdown(f"**Confiance:** {ii.get('confidence', 'N/A')}")
        else:
            st.info("Non généré")

    with tabs[3]:
        om = insights.get("outreach_messages")
        if om:
            st.markdown(f"**Résumé:** {om.get('summary', 'N/A')}")
            if om.get("linkedin_messages"):
                msgs = om["linkedin_messages"]
                with st.expander("💬 Message initial"):
                    st.markdown(msgs.get("initial", "N/A"))
                with st.expander("💬 Relance J+3"):
                    st.markdown(msgs.get("follow_up_day3", "N/A"))
                with st.expander("💬 Relance J+7"):
                    st.markdown(msgs.get("follow_up_day7", "N/A"))
            if om.get("emails"):
                emails = om["emails"]
                if emails.get("initial"):
                    with st.expander("📧 Email initial"):
                        st.markdown(
                            f"**Objet:** {emails['initial'].get('subject', 'N/A')}"
                        )
                        st.markdown(emails["initial"].get("body_text", "N/A"))
            st.markdown(f"**Confiance:** {om.get('confidence', 'N/A')}")
        else:
            st.info("Non généré")

    with tabs[4]:
        st.json(result)

    if st.button("🔄 Nouvelle analyse"):
        st.session_state.results = None
        st.rerun()
