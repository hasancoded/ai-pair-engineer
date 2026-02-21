"""
app.py
Streamlit entry point for the AI Pair Engineer.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from groq import AuthenticationError, RateLimitError

from analyzer import (
    AnalysisOptions,
    GROQ_MODELS,
    DEFAULT_MODEL,
    SUPPORTED_LANGUAGES,
    run_analysis,
)

load_dotenv()


def _resolve_api_key() -> str:
    """
    Resolve the Groq API key using environment-appropriate sources.

    Priority order:
      1. st.secrets["GROQ_API_KEY"]  — Streamlit Cloud (secrets manager)
      2. GROQ_API_KEY env variable    — local .env file via python-dotenv
      3. Empty string                 — user must supply key in the sidebar
    """
    try:
        return st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    except Exception:
        return os.getenv("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Pair Engineer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — refined, dark editorial aesthetic
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Syne:wght@400;600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

    :root {
        --bg-primary:    #0d0f12;
        --bg-secondary:  #13161b;
        --bg-tertiary:   #1a1e26;
        --border:        #252932;
        --accent:        #4fffb0;
        --accent-dim:    #1a3d2e;
        --text-primary:  #e8eaf0;
        --text-secondary:#8891a4;
        --text-muted:    #4a5264;
        --danger:        #ff4f6e;
        --warning:       #f5a623;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'DM Mono', monospace;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * {
        font-family: 'DM Mono', monospace;
    }

    /* Hide Streamlit footer — toolbar is suppressed via .streamlit/config.toml */
    #MainMenu { display: none; }
    footer { display: none; }


    /* Sidebar collapse/expand toggle — fix icon rendering as raw ligature text */
    [data-testid="collapsedControl"] span,
    button[kind="header"] span,
    [data-testid="stSidebarCollapseButton"] span {
        font-family: 'Material Symbols Rounded', sans-serif !important;
        font-size: 1.25rem !important;
        font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
        color: var(--text-muted) !important;
        transition: color 0.15s ease;
    }
    [data-testid="collapsedControl"]:hover span,
    button[kind="header"]:hover span,
    [data-testid="stSidebarCollapseButton"]:hover span {
        color: var(--text-secondary) !important;
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Syne', sans-serif;
        letter-spacing: -0.02em;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent);
        color: #000;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border: none;
        border-radius: 2px;
        padding: 0.65rem 1.5rem;
        transition: opacity 0.15s ease;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Download button */
    .stDownloadButton > button {
        background-color: transparent;
        color: var(--accent);
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
        border: 1px solid var(--accent);
        border-radius: 2px;
        transition: background-color 0.15s ease;
    }
    .stDownloadButton > button:hover {
        background-color: var(--accent-dim);
    }

    /* Text areas & inputs */
    textarea, .stTextInput input {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 2px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.82rem !important;
        line-height: 1.65 !important;
    }
    textarea:focus, .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-dim) !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 2px !important;
        color: var(--text-primary) !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.82rem !important;
    }

    /* Checkboxes */
    [data-testid="stCheckbox"] label {
        font-size: 0.82rem;
        color: var(--text-secondary);
    }

    /* Alerts */
    [data-testid="stAlert"] {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 2px;
        font-size: 0.82rem;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }

    /* Markdown analysis output */
    [data-testid="stMarkdownContainer"] pre {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border);
        border-radius: 2px;
        padding: 1rem 1.25rem;
        overflow-x: auto;
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
        line-height: 1.65;
    }
    [data-testid="stMarkdownContainer"] code {
        background-color: var(--bg-tertiary);
        color: var(--accent);
        padding: 0.1rem 0.35rem;
        border-radius: 2px;
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
    }
    [data-testid="stMarkdownContainer"] pre code {
        background: none;
        color: var(--text-primary);
        padding: 0;
    }
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Syne', sans-serif;
        color: var(--text-primary);
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.35rem;
        margin-top: 1.75rem;
    }
    [data-testid="stMarkdownContainer"] p {
        line-height: 1.75;
        color: var(--text-secondary);
    }
    [data-testid="stMarkdownContainer"] strong {
        color: var(--text-primary);
    }
    [data-testid="stMarkdownContainer"] blockquote {
        border-left: 3px solid var(--accent);
        padding-left: 1rem;
        color: var(--text-muted);
        margin-left: 0;
    }

    /* Spinner */
    [data-testid="stSpinner"] p {
        color: var(--text-muted) !important;
        font-size: 0.8rem;
    }

    /* Sidebar section label */
    .sidebar-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        background-color: var(--accent-dim);
        color: var(--accent);
        font-size: 0.68rem;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.15rem 0.55rem;
        border-radius: 2px;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        "<p style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;"
        "letter-spacing:-0.02em;color:#e8eaf0;margin-bottom:0'>AI Pair Engineer</p>"
        "<p style='font-size:0.72rem;color:#4a5264;margin-top:0.2rem;margin-bottom:1.5rem'>"
        "Powered by Groq + Llama</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-label'>Authentication</div>", unsafe_allow_html=True)
    env_key = _resolve_api_key()
    api_key = st.text_input(
        "Groq API Key",
        value=env_key,
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
        help="Your Groq API key. Obtain one free at console.groq.com",
    )
    if not api_key:
        st.caption("Obtain a free key at [console.groq.com](https://console.groq.com)")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-label'>Model</div>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "Model",
        options=list(GROQ_MODELS.keys()),
        format_func=lambda k: GROQ_MODELS[k],
        index=list(GROQ_MODELS.keys()).index(DEFAULT_MODEL),
        label_visibility="collapsed",
    )

    st.markdown("<div class='sidebar-label' style='margin-top:1rem'>Language</div>", unsafe_allow_html=True)
    selected_language = st.selectbox(
        "Language",
        options=SUPPORTED_LANGUAGES,
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-label'>Analysis Modules</div>", unsafe_allow_html=True)
    opt_design   = st.checkbox("Design Flaw Detection",    value=True)
    opt_refactor = st.checkbox("Refactoring Suggestions",  value=True)
    opt_tests    = st.checkbox("Unit Test Proposals",      value=True)
    opt_solid    = st.checkbox("SOLID Principles Audit",   value=False)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.7rem;color:#4a5264;line-height:1.6'>"
        "API keys are used only for the duration of your session and are never stored or logged.</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    "<h1 style='margin-bottom:0.1rem'>AI Pair Engineer"
    "<span class='status-badge'>Beta</span></h1>"
    "<p style='color:#8891a4;font-size:0.85rem;margin-top:0.2rem'>"
    "Paste your code. Receive architectural analysis, refactoring proposals, and unit tests.</p>",
    unsafe_allow_html=True,
)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown(
        "<p style='font-family:Syne,sans-serif;font-weight:700;font-size:0.8rem;"
        "letter-spacing:0.08em;text-transform:uppercase;color:#8891a4;margin-bottom:0.4rem'>"
        "Code Input</p>",
        unsafe_allow_html=True,
    )
    code_input = st.text_area(
        label="Code Input",
        height=460,
        placeholder=f"# Paste your {selected_language} code here...",
        label_visibility="collapsed",
    )
    analyze_clicked = st.button("Run Analysis", use_container_width=True)

# ---------------------------------------------------------------------------
# Analysis execution
# ---------------------------------------------------------------------------

with right_col:
    st.markdown(
        "<p style='font-family:Syne,sans-serif;font-weight:700;font-size:0.8rem;"
        "letter-spacing:0.08em;text-transform:uppercase;color:#8891a4;margin-bottom:0.4rem'>"
        "Analysis Output</p>",
        unsafe_allow_html=True,
    )

    if analyze_clicked:
        # --- Input validation ---
        if not api_key:
            st.error("A Groq API key is required. Enter it in the sidebar.")
        elif not code_input.strip():
            st.warning("No code provided. Paste a code snippet in the input panel.")
        elif not any([opt_design, opt_refactor, opt_tests, opt_solid]):
            st.warning("Select at least one analysis module in the sidebar.")
        else:
            options = AnalysisOptions(
                detect_design_flaws=opt_design,
                suggest_refactoring=opt_refactor,
                propose_tests=opt_tests,
                audit_solid=opt_solid,
                language=selected_language,
                model=selected_model,
            )

            try:
                with st.spinner("Analysing..."):
                    result = run_analysis(code_input, api_key, options)

                st.markdown(result)
                st.markdown("<hr>", unsafe_allow_html=True)
                st.download_button(
                    label="Download Report (.md)",
                    data=result,
                    file_name="pair_engineer_review.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            except AuthenticationError:
                st.error(
                    "Authentication failed. Verify your Groq API key is correct and active."
                )
            except RateLimitError:
                st.error(
                    "Rate limit reached. Wait a moment and try again, or switch to a faster model."
                )
            except Exception as exc:
                st.error(f"An unexpected error occurred: {exc}")

    else:
        st.markdown(
            "<div style='border:1px solid #252932;border-radius:2px;padding:1.5rem 2rem;"
            "color:#4a5264;font-size:0.82rem;line-height:1.9;margin-top:0.1rem'>"
            "Select your analysis modules in the sidebar, paste your code on the left, "
            "then click <strong style='color:#8891a4'>Run Analysis</strong>.<br><br>"
            "Available modules:<br>"
            "— Design Flaw Detection<br>"
            "— Refactoring Suggestions<br>"
            "— Unit Test Proposals<br>"
            "— SOLID Principles Audit"
            "</div>",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size:0.7rem;color:#4a5264;text-align:center'>"
    "AI Pair Engineer — Groq API + Streamlit — For demonstration purposes</p>",
    unsafe_allow_html=True,
)