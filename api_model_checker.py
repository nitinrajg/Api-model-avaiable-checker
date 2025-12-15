import streamlit as st
import requests
from datetime import datetime

# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(
    page_title="LLM Models Viewer",
    page_icon="🧠",
    layout="wide"
)

# --------------------------------------------------
# Some custom styling to make it look nicer
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top left, #111827, #020617);
        color: #e5e7eb;
    }
    h1, h2, h3 {
        color: #f9fafb;
        font-weight: 600;
    }
    .subtitle {
        color: #9ca3af;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    /* Input fields */
    .stTextInput input, .stSelectbox div {
        background-color: #020617 !important;
        border-radius: 10px;
    }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.4em;
        border: none;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af, #1d4ed8);
    }
    /* Tighten spacing in the table area */
    [data-testid="stHorizontalBlock"] {
        margin-top: 0.15rem !important;
        margin-bottom: 0.15rem !important;
    }
    hr {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
        border: none;
        height: 1px;
        background: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("## 🧠 LLM Models Viewer")
st.markdown(
    "<div class='subtitle'>Inspect available models from OpenAI, Gemini, or Groq using your API key.</div>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# Provider settings
# --------------------------------------------------
PROVIDERS = {
    "OpenAI": {
        "url": "https://api.openai.com/v1/models",
        "auth": "bearer"
    },
    "Groq": {
        "url": "https://api.groq.com/openai/v1/models",
        "auth": "bearer"
    },
    "Gemini": {
        "url": "https://generativelanguage.googleapis.com/v1/models",
        "auth": "query"
    },
    "Cerebras": {
        "url": "https://api.cerebras.ai/v1/models",
        "auth": "bearer"
    }
}


# --------------------------------------------------
# User inputs
# --------------------------------------------------
col1, col2 = st.columns([1, 2])
with col1:
    provider = st.selectbox("Provider", list(PROVIDERS.keys()))
with col2:
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="Paste your API key here"
    )

fetch = st.button("Fetch Models")

# --------------------------------------------------
# Small helper for dates
# --------------------------------------------------
def readable_time(ts):
    if not ts or ts <= 0:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts).strftime("%d %b %Y")
    except Exception:
        return "N/A"


# --------------------------------------------------
# Main logic when the button is pressed
# --------------------------------------------------
if fetch:
    if not api_key.strip():
        st.error("API key is required")
        st.stop()

    cfg = PROVIDERS[provider]

    headers = {}
    params = {}

    if cfg["auth"] == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
        url = cfg["url"]
    else:  # query param for Gemini
        params["key"] = api_key
        url = cfg["url"]

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:
        st.error(f"Request failed: {e}")
        st.stop()

    if response.status_code != 200:
        st.error(f"Error {response.status_code}")
        st.json(response.text)
        st.stop()

    data = response.json()
    models = data.get("data") or data.get("models") or []

    # Sort newest first
    models.sort(
    key=lambda m: m.get("created") if m.get("created") else -1,
    reverse=True
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.success(f"Showing {len(models)} models")

    # --------------------------------------------------
    # Table header
    # --------------------------------------------------
    h1, h2, h3, h4 = st.columns([1, 4, 3, 2])
    h1.markdown("**#**")
    h2.markdown("**Model**")
    h3.markdown("**Owner / Provider**")
    h4.markdown("**Created**")
    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------
    # Model rows
    # --------------------------------------------------
    for idx, model in enumerate(models, 1):
        c1, c2, c3, c4 = st.columns([1, 4, 3, 2])
        c1.write(idx)
        c2.code(model.get("id") or model.get("name", "unknown"))
        c3.write(model.get("owned_by", provider))
        c4.write(readable_time(model.get("created")))