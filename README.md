# 🇫🇷 Chloé

Assistant IA de prospection LinkedIn.

---

## Fonctionnalités

- Analyse de profils LinkedIn
- Génération d'insights IA (profil, interactions, outreach)
- Support multi-LLM (OpenAI, Gemini)
- Interface Streamlit
- Prompts personnalisables

---

## Setup

### 1. Prérequis

- Python 3.11+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv)

### 2. Installation

```bash
git clone <repo>
cd chloe-api
cp .env.example .env
```

Remplissez le fichier `.env` avec vos clés API.

### 3. Lancement

```bash
make serve   # API sur localhost:8001
make ui      # Streamlit sur localhost:8501
```

---

## Commandes

| Commande | Description |
|----------|-------------|
| `make serve` | Lance l'API |
| `make ui` | Lance Streamlit |
| `make sync` | Synchronise les dépendances |

---

## Configuration

Voir `.env.example` pour les variables disponibles.

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | `openai` ou `gemini` |
| `LLM_MODEL_NAME` | Ex: `gpt-4o`, `gemini-2.0-flash` |
| `COMPANY_NAME` | Nom de votre entreprise |

---

## Support

contact@idun-group.com
