# 🇫🇷 Chloé - Analyseur de Leads LinkedIn

> Transformez vos profils LinkedIn en opportunités commerciales grâce à l'IA.

---

## ✨ Fonctionnalités

| | |
|---|---|
| 🔍 | Analyse complète de profils LinkedIn |
| 🤖 | Insights IA : profil, interactions, messages de prospection |
| 🔄 | Multi-LLM : OpenAI ou Gemini au choix |
| 🎨 | Interface Streamlit intuitive |
| 🌍 | Support multilingue |

---

## 📋 Prérequis

- Python 3.11+
- PostgreSQL
- Clé API OpenAI ou Gemini
- `idun-agent-engine`

---

## 🚀 Installation

```bash
git clone <repository-url>
cd chloe-api

pip install -r requirements.txt
pip install idun-agent-engine
```

---

## ⚙️ Configuration

Créez un fichier `.env` à la racine :

```bash
# Base de données
POSTGRESQL_URI=postgresql://user:password@localhost:5432/chloe

# LLM (openai ou gemini)
LLM_PROVIDER=gemini
LLM_MODEL_NAME=gemini-2.0-flash
LLM_TEMPERATURE=0.0

# Clés API
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
APIFY_API_TOKEN=...
```

> 💡 **Tip:** Pour OpenAI, utilisez `gpt-4o` ou `gpt-4o-mini`. Pour Gemini, `gemini-2.0-flash` ou `gemini-2.5-pro`.

---

## 🏃 Lancement

### Serveur API

```bash
idun agent serve --source=file --path=app/agent/config.yaml
```

> 💡 **Tip:** La documentation Swagger est disponible sur `http://localhost:8000/docs`

### Interface Streamlit

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

---

## 🎯 Utilisation

1. **Lancez le serveur API** et **Streamlit**
2. Ouvrez `http://localhost:8501`
3. *(Optionnel)* Allez dans **Config** pour personnaliser le contexte entreprise
4. Allez dans **Analyze**, collez une URL LinkedIn, cliquez sur **Analyze**
5. Explorez les insights générés !

> 💡 **Tip:** Plus vous fournissez de contexte sur votre entreprise dans Config, plus les messages de prospection seront pertinents.

---

## 📧 Support

Des questions ? contact@idun-group.com

---

<p align="center">
  <strong>Chloé</strong> — Insights commerciaux intelligents
</p>
