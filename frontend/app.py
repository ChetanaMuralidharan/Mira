import html
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

from api_client import ask_mira, get_history, get_history_item


st.set_page_config(
    page_title="MIRA | Clinical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Theme and application styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --page: #f4f7fa;
        --surface: #ffffff;
        --surface-soft: #f8fbfd;
        --surface-blue: #edf6fa;
        --border: #dbe5eb;
        --border-strong: #c9d8e1;
        --navy: #173b57;
        --navy-deep: #102b40;
        --blue: #2878a5;
        --teal: #16828b;
        --teal-soft: #e9f7f6;
        --text: #1f2f3a;
        --muted: #667985;
        --success: #26876f;
        --warning: #b77822;
        --danger: #bd5a5a;
        --shadow: 0 8px 24px rgba(29, 61, 80, 0.07);
    }

    .stApp {
        background: var(--page);
        color: var(--text);
    }

    /* Reserve space for Streamlit's fixed toolbar so it never covers page content. */
    header[data-testid="stHeader"] {
        height: 3.25rem;
        background: rgba(255, 255, 255, 0.96);
        border-bottom: 1px solid var(--border);
        backdrop-filter: blur(10px);
        z-index: 999;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 4.35rem;
        padding-bottom: 2.5rem;
        padding-left: 1.55rem;
        padding-right: 1.55rem;
    }

    /* Keep every Streamlit column row aligned and separated vertically. */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    div[data-testid="column"] {
        min-width: 0;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 3.8rem;
    }

    .brand-shell {
        display: flex;
        gap: 0.8rem;
        align-items: center;
        padding: 0.3rem 0 0.9rem 0;
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        display: grid;
        place-items: center;
        border-radius: 13px;
        color: white;
        font-size: 1.25rem;
        background: linear-gradient(145deg, var(--blue), var(--teal));
        box-shadow: 0 8px 18px rgba(40, 120, 165, 0.2);
    }

    .brand-title {
        color: var(--navy-deep);
        font-size: 1.18rem;
        line-height: 1.1;
        font-weight: 850;
        margin: 0;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.77rem;
        margin-top: 0.2rem;
    }

    .sidebar-label {
        margin-top: 0.6rem;
        margin-bottom: 0.35rem;
        color: #81919b;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .sidebar-status {
        border: 1px solid var(--border);
        background: var(--surface-soft);
        border-radius: 15px;
        padding: 0.9rem;
        margin-top: 0.75rem;
    }

    .sidebar-status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #49606f;
        font-size: 0.81rem;
        padding: 0.3rem 0;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        display: inline-block;
        margin-right: 0.45rem;
        background: var(--success);
        box-shadow: 0 0 0 4px rgba(38, 135, 111, 0.10);
    }

    .demo-note {
        margin-top: 0.85rem;
        padding: 0.9rem;
        border: 1px solid #cfe1ea;
        background: var(--surface-blue);
        border-radius: 15px;
        color: #4e6877;
        font-size: 0.78rem;
        line-height: 1.48;
    }

    .app-header {
        background: linear-gradient(120deg, #ffffff 0%, #f7fbfd 100%);
        border: 1px solid var(--border);
        border-radius: 20px;
        box-shadow: var(--shadow);
        padding: 1.2rem 1.35rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }

    .header-kicker {
        color: var(--teal);
        font-size: 0.71rem;
        font-weight: 850;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .header-title {
        margin: 0;
        color: var(--navy-deep);
        font-size: 1.72rem;
        line-height: 1.1;
        font-weight: 850;
        letter-spacing: -0.025em;
    }

    .header-copy {
        color: var(--muted);
        margin-top: 0.35rem;
        margin-bottom: 0;
        font-size: 0.92rem;
    }

    .system-pill {
        white-space: nowrap;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border: 1px solid #cde5dc;
        color: #276e5d;
        background: #f1faf7;
        border-radius: 999px;
        padding: 0.55rem 0.82rem;
        font-size: 0.8rem;
        font-weight: 800;
    }

    .metric-card {
        min-height: 112px;
        height: 100%;
        box-sizing: border-box;
        margin-bottom: 0.15rem;
        border-radius: 17px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-top: 3px solid var(--blue);
        padding: 0.9rem 1rem;
        box-shadow: 0 4px 16px rgba(29, 61, 80, 0.045);
    }

    .metric-card.teal { border-top-color: var(--teal); }
    .metric-card.navy { border-top-color: var(--navy); }
    .metric-card.green { border-top-color: var(--success); }

    .metric-label {
        color: #7b8d98;
        font-size: 0.69rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
    }

    .metric-value {
        margin-top: 0.42rem;
        color: var(--navy-deep);
        font-size: 1.5rem;
        line-height: 1.05;
        font-weight: 850;
    }

    .metric-detail {
        color: var(--muted);
        font-size: 0.76rem;
        margin-top: 0.35rem;
    }

    .workspace-card,
    .content-card {
        box-sizing: border-box;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: var(--shadow);
        padding: 1.05rem 1.15rem;
        margin-bottom: 1rem;
    }

    .section-eyebrow {
        color: var(--teal);
        font-size: 0.69rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 850;
        margin-bottom: 0.25rem;
    }

    .section-title {
        color: var(--navy-deep);
        font-size: 1.15rem;
        font-weight: 820;
        margin: 0;
    }

    .section-copy {
        color: var(--muted);
        font-size: 0.84rem;
        margin-top: 0.3rem;
        margin-bottom: 0.75rem;
    }

    .prompt-card {
        min-height: 126px;
        height: 100%;
        box-sizing: border-box;
        margin-bottom: 0.45rem;
        border: 1px solid var(--border);
        background: var(--surface-soft);
        border-radius: 16px;
        padding: 0.85rem 0.9rem;
        transition: all 0.15s ease;
    }

    .prompt-card:hover {
        border-color: #b7ceda;
        background: #f4fafd;
        transform: translateY(-1px);
    }

    .prompt-icon {
        width: 31px;
        height: 31px;
        border-radius: 10px;
        display: grid;
        place-items: center;
        background: #e8f3f8;
        color: var(--blue);
        font-size: 0.95rem;
        margin-bottom: 0.55rem;
    }

    .prompt-title {
        color: var(--navy-deep);
        font-size: 0.91rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .prompt-description {
        color: var(--muted);
        font-size: 0.77rem;
        line-height: 1.42;
    }

    .answer-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 5px solid var(--teal);
        border-radius: 18px;
        box-shadow: var(--shadow);
        padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
    }

    .answer-title {
        color: var(--navy-deep);
        font-size: 1.18rem;
        font-weight: 850;
        margin: 0.1rem 0 0.5rem 0;
    }

    .answer-copy {
        color: #314753;
        font-size: 0.96rem;
        line-height: 1.7;
        margin-bottom: 0.75rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.48rem;
        margin-top: 0.65rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--surface-soft);
        color: #4d6573;
        padding: 0.36rem 0.65rem;
        font-size: 0.72rem;
        font-weight: 800;
    }

    .chip.good {
        background: #eef9f5;
        border-color: #cce8dc;
        color: #2e735f;
    }

    .chip.warn {
        background: #fff8ec;
        border-color: #ead9b6;
        color: #906422;
    }

    .detail-box {
        background: var(--surface-soft);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        margin-bottom: 0.7rem;
    }

    .detail-label {
        color: #82929c;
        font-size: 0.67rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 850;
    }

    .detail-value {
        color: var(--navy-deep);
        font-size: 0.9rem;
        font-weight: 780;
        margin-top: 0.28rem;
    }

    .empty-state {
        border: 1px dashed #cbd9e1;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.58);
        padding: 1.2rem;
        color: var(--muted);
        font-size: 0.88rem;
        text-align: center;
    }

    .footer-note {
        color: #788a95;
        font-size: 0.76rem;
        line-height: 1.5;
    }

    .stButton > button {
        border-radius: 11px;
        font-weight: 750;
        border: 1px solid var(--border-strong);
        background: #ffffff;
        color: var(--navy-deep);
        min-height: 2.45rem;
    }

    .stButton > button:hover {
        border-color: #96b6c8;
        background: #f1f7fa;
        color: var(--navy-deep);
    }

    div[data-testid="stButton"] button[kind="primary"] {
        color: white;
        background: linear-gradient(135deg, var(--navy) 0%, var(--teal) 100%);
        border: none;
        box-shadow: 0 7px 16px rgba(23, 59, 87, 0.18);
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        color: white;
        background: linear-gradient(135deg, #102f47 0%, #12747c 100%);
    }

    textarea {
        border-radius: 14px !important;
        background: #fbfdfe !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text) !important;
    }

    textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(40, 120, 165, 0.10) !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 0.25rem;
        border-bottom: 1px solid var(--border);
    }

    button[data-baseweb="tab"] {
        color: #667a87;
        padding: 0.55rem 0.75rem;
        font-size: 0.82rem;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--navy-deep);
        font-weight: 800;
        border-bottom-color: var(--teal);
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 13px;
        overflow: hidden;
    }

    div[data-testid="stMetric"] {
        background: var(--surface-soft);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.75rem;
    }

    div[data-testid="stMetricValue"] {
        color: var(--navy-deep);
        font-size: 1.32rem;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    .stExpander {
        border-color: var(--border) !important;
        border-radius: 13px !important;
        overflow: hidden;
    }

    @media (max-width: 900px) {
        .block-container {
            padding-top: 4rem;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }
        .app-header {
            align-items: flex-start;
            flex-direction: column;
        }
        .header-title { font-size: 1.42rem; }
        .metric-card,
        .prompt-card { min-height: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def safe_text(value: Any) -> str:
    return html.escape(str(value or ""))


def normalize_payload(result: Dict[str, Any]) -> Dict[str, Any]:
    """Protect the UI from slight backend response-shape differences."""
    return {
        "question": result.get("question", ""),
        "answer": result.get("answer") or result.get("final_explanation", ""),
        "intent": result.get("intent", ""),
        "data_sources_needed": result.get("data_sources_needed", []),
        "generated_sql": result.get("generated_sql", ""),
        "sql_result": result.get("sql_result", []) or [],
        "validation_status": result.get("validation_status", ""),
        "validation_notes": result.get("validation_notes", ""),
        "chart_type": result.get("chart_type", "none"),
        "chart_spec": result.get("chart_spec"),
        "rag_chunks": result.get("rag_chunks", []) or [],
        "suggested_followup": result.get("suggested_followup", ""),
        "mlflow_run_id": result.get("mlflow_run_id", ""),
        "tool_calls_log": result.get("tool_calls_log", []) or [],
        "total_latency_ms": result.get("total_latency_ms", ""),
    }


def make_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="ignore")
        df[col] = converted

    return df


def style_chart(fig: Any) -> Any:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Arial, sans-serif", color="#304652"),
        title=dict(font=dict(size=17, color="#173b57"), x=0.01),
        margin=dict(l=28, r=22, t=56, b=28),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#ffffff", font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor="#dbe5eb", tickfont=dict(color="#667985"))
    fig.update_yaxes(gridcolor="#edf2f5", zeroline=False, tickfont=dict(color="#667985"))
    return fig


def build_fallback_chart(sql_result: List[Dict[str, Any]], question: str) -> Optional[Any]:
    if not sql_result:
        return None

    df = make_dataframe(sql_result)
    if df.empty or len(df.columns) < 2:
        return None

    question_lower = question.lower()

    for col in df.columns:
        col_lower = col.lower()
        if any(word in col_lower for word in ["date", "month", "time", "start"]):
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], unit="s", errors="coerce")
            else:
                df[col] = pd.to_datetime(df[col], errors="ignore")

    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    date_like_cols = [
        col
        for col in df.columns
        if any(word in col.lower() for word in ["date", "month", "year", "time", "start"])
    ]
    categorical_cols = [col for col in df.columns if col not in numeric_cols]

    if len(df) == 1 and len(numeric_cols) == 1:
        value = df[numeric_cols[0]].iloc[0]
        fig = px.bar(
            x=[numeric_cols[0].replace("_", " ").title()],
            y=[value],
            title=numeric_cols[0].replace("_", " ").title(),
            labels={"x": "", "y": "Value"},
        )
        return style_chart(fig)

    if "encounter" in question_lower and "month" in question_lower:
        x_col = date_like_cols[0] if date_like_cols else df.columns[0]
        y_col = "encounter_count" if "encounter_count" in df.columns else numeric_cols[-1]
        grouped = df.groupby(x_col, as_index=False)[y_col].sum()
        fig = px.line(
            grouped,
            x=x_col,
            y=y_col,
            markers=True,
            title="Monthly Encounter Volume",
            labels={x_col: "Month", y_col: "Encounter Count"},
        )
        return style_chart(fig)

    if date_like_cols and numeric_cols:
        x_col = date_like_cols[0]
        y_col = numeric_cols[-1]
        grouped = df.groupby(x_col, as_index=False)[y_col].sum()
        fig = px.line(
            grouped,
            x=x_col,
            y=y_col,
            markers=True,
            title=f"{y_col.replace('_', ' ').title()} Over Time",
        )
        return style_chart(fig)

    if categorical_cols and numeric_cols:
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        grouped = (
            df.groupby(x_col, as_index=False)[y_col]
            .sum()
            .sort_values(y_col, ascending=False)
        )
        fig = px.bar(
            grouped,
            x=x_col,
            y=y_col,
            title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
        )
        return style_chart(fig)

    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=(
                f"{numeric_cols[1].replace('_', ' ').title()} vs "
                f"{numeric_cols[0].replace('_', ' ').title()}"
            ),
        )
        return style_chart(fig)

    return None


def status_chip(intent: str, validation_status: str) -> str:
    if intent == "document_query":
        return '<span class="chip">Clinical document response</span>'
    if intent == "hybrid":
        return '<span class="chip">Hybrid SQL + RAG</span>'
    if validation_status == "valid":
        return '<span class="chip good">Validated result</span>'
    if validation_status in ["suspect", "out_of_range"]:
        return '<span class="chip warn">Review recommended</span>'
    return '<span class="chip">Generated response</span>'


def render_key_numbers(sql_result: List[Dict[str, Any]]) -> None:
    df = make_dataframe(sql_result)
    if df.empty:
        st.info("No structured rows were returned.")
        return

    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    if len(df) == 1 and numeric_cols:
        cols = st.columns(min(len(numeric_cols), 4))
        for idx, col in enumerate(numeric_cols[:4]):
            value = df[col].iloc[0]
            if isinstance(value, (int, float)):
                rendered = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
            else:
                rendered = str(value)
            cols[idx].metric(col.replace("_", " ").title(), rendered)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <div class="header-kicker">Clinical intelligence workspace</div>
                <h1 class="header-title">{safe_text(title)}</h1>
                <p class="header-copy">{safe_text(subtitle)}</p>
            </div>
            <div class="system-pill"><span class="status-dot"></span>System operational</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, detail: str, variant: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card {variant}">
            <div class="metric-label">{safe_text(label)}</div>
            <div class="metric-value">{safe_text(value)}</div>
            <div class="metric-detail">{safe_text(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_prompt_card(icon: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="prompt-card">
            <div class="prompt-icon">{safe_text(icon)}</div>
            <div class="prompt-title">{safe_text(title)}</div>
            <div class="prompt-description">{safe_text(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "question" not in st.session_state:
    st.session_state.question = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "page" not in st.session_state:
    st.session_state.page = "Ask MIRA"


# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-shell">
            <div class="brand-mark">✦</div>
            <div>
                <div class="brand-title">MIRA</div>
                <div class="brand-subtitle">Medical Intelligence & Reasoning Agent</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)
    selected_page = st.radio(
        "Navigation",
        ["Overview", "Ask MIRA", "Query History", "Evaluation", "About"],
        index=["Overview", "Ask MIRA", "Query History", "Evaluation", "About"].index(
            st.session_state.page
        ),
        label_visibility="collapsed",
    )
    st.session_state.page = selected_page

    st.markdown('<div class="sidebar-label">System status</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sidebar-status">
            <div class="sidebar-status-row"><span><span class="status-dot"></span>Clinical warehouse</span><b>Ready</b></div>
            <div class="sidebar-status-row"><span><span class="status-dot"></span>Knowledge base</span><b>Indexed</b></div>
            <div class="sidebar-status-row"><span><span class="status-dot"></span>Agent services</span><b>Online</b></div>
        </div>
        <div class="demo-note">
            <b>Demo environment</b><br/>
            Uses synthetic Synthea patient data. MIRA is a portfolio system and is not intended for clinical decision-making.
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Shared template library
# -----------------------------------------------------------------------------
templates = [
    ("👥", "Population summary", "How many patients are in the dataset?", "Inspect the size of the synthetic patient population."),
    ("📈", "Encounter trends", "Show encounter volume by month.", "Visualize utilization patterns over time."),
    ("🫀", "Chronic conditions", "What are the five most common conditions?", "Identify the highest-prevalence diagnoses."),
    ("🧪", "Laboratory analysis", "Summarize A1c values for diabetic patients.", "Review glycemic-control measurements."),
    ("📚", "Clinical policies", "What does the medication reconciliation protocol require?", "Search clinical policies and care protocols."),
    ("🧠", "Hybrid reasoning", "How many diabetic patients have elevated A1c values, and what do the guidelines recommend?", "Combine patient analytics with clinical guidance."),
]


# -----------------------------------------------------------------------------
# Overview page
# -----------------------------------------------------------------------------
if selected_page == "Overview":
    render_header(
        "MIRA Clinical Intelligence",
        "A transparent agentic system for healthcare analytics, clinical document retrieval, and hybrid reasoning.",
    )

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric_card("SQL accuracy", "100%", "25 of 25 benchmark questions", "navy")
    with metric_cols[1]:
        render_metric_card("Clinical RAG", "100%", "15 of 15 benchmark questions", "teal")
    with metric_cols[2]:
        render_metric_card("Hybrid reasoning", "100%", "7 of 7 benchmark questions", "green")
    with metric_cols[3]:
        render_metric_card("Benchmark", "48 / 50", "96% overall accuracy", "")

    left, right = st.columns([1.55, 1])
    with left:
        st.markdown(
            """
            <div class="content-card">
                <div class="section-eyebrow">System capabilities</div>
                <h3 class="section-title">One interface, three reasoning paths</h3>
                <p class="section-copy">MIRA automatically selects structured data, clinical documents, or both based on the user's question.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cap_cols = st.columns(3)
        capabilities = [
            ("Text-to-SQL", "Natural-language questions are translated into validated SQL over curated dbt marts."),
            ("Clinical RAG", "Relevant policy, protocol, and guideline passages are retrieved from pgvector."),
            ("Hybrid Agent", "LangGraph coordinates SQL and retrieval tools before synthesizing a grounded answer."),
        ]
        for idx, (title, description) in enumerate(capabilities):
            with cap_cols[idx]:
                render_prompt_card("✓", title, description)

    with right:
        st.markdown(
            """
            <div class="content-card">
                <div class="section-eyebrow">Architecture</div>
                <h3 class="section-title">Production-oriented foundations</h3>
                <p class="section-copy">The project combines modern data engineering, analytics engineering, agentic AI, observability, and API delivery.</p>
                <div class="detail-box"><div class="detail-label">Data platform</div><div class="detail-value">Delta Lake · DuckDB · dbt · Great Expectations</div></div>
                <div class="detail-box"><div class="detail-label">Agent layer</div><div class="detail-value">LangGraph · Groq · MCP tool servers</div></div>
                <div class="detail-box"><div class="detail-label">Retrieval</div><div class="detail-value">Sentence Transformers · PostgreSQL · pgvector</div></div>
                <div class="detail-box"><div class="detail-label">Delivery & tracing</div><div class="detail-value">FastAPI · Streamlit · Plotly · MLflow</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="content-card">
            <div class="section-eyebrow">Start exploring</div>
            <h3 class="section-title">Suggested clinical intelligence questions</h3>
            <p class="section-copy">Select a prompt below to open it in the Ask MIRA workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    prompt_cols = st.columns(3)
    for idx, (icon, title, question, description) in enumerate(templates):
        with prompt_cols[idx % 3]:
            render_prompt_card(icon, title, description)
            if st.button("Use prompt", key=f"overview_prompt_{idx}", use_container_width=True):
                st.session_state.question = question
                st.session_state.page = "Ask MIRA"
                st.rerun()


# -----------------------------------------------------------------------------
# Ask MIRA page
# -----------------------------------------------------------------------------
elif selected_page == "Ask MIRA":
    render_header(
        "Ask MIRA",
        "Query structured synthetic patient data, search clinical knowledge, or combine both in one transparent workflow.",
    )

    st.markdown(
        """
        <div class="workspace-card">
            <div class="section-eyebrow">Clinical query workspace</div>
            <h3 class="section-title">What would you like to investigate?</h3>
            <p class="section-copy">Ask a healthcare analytics, clinical policy, or hybrid reasoning question in plain English.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Ask a clinical analytics or policy question",
        value=st.session_state.question,
        placeholder="Example: How many diabetic patients have elevated A1c values, and what do the guidelines recommend?",
        height=116,
        label_visibility="collapsed",
    )

    action_cols = st.columns([1.25, 1, 5.6])
    with action_cols[0]:
        run_clicked = st.button("Run analysis", type="primary", use_container_width=True)
    with action_cols[1]:
        clear_clicked = st.button("Clear", use_container_width=True)

    if clear_clicked:
        st.session_state.question = ""
        st.session_state.result = None
        st.rerun()

    if run_clicked:
        if not question.strip():
            st.warning("Enter a question before running the analysis.")
        else:
            st.session_state.question = question.strip()
            with st.spinner("MIRA is selecting tools, executing the workflow, and validating the response..."):
                try:
                    st.session_state.result = normalize_payload(ask_mira(question.strip()))
                except Exception as exc:
                    st.error(f"Request failed: {exc}")
                    st.session_state.result = None

    with st.expander("Browse suggested questions", expanded=st.session_state.result is None):
        prompt_cols = st.columns(3)
        for idx, (icon, title, prompt_question, description) in enumerate(templates):
            with prompt_cols[idx % 3]:
                render_prompt_card(icon, title, description)
                if st.button("Use this question", key=f"ask_prompt_{idx}", use_container_width=True):
                    st.session_state.question = prompt_question
                    st.rerun()

    result = st.session_state.result
    if result:
        intent = result.get("intent", "")
        validation_status = result.get("validation_status", "")
        chart_type = result.get("chart_type", "none")
        latency = result.get("total_latency_ms", "")
        mlflow_run_id = result.get("mlflow_run_id", "")
        answer_text = result.get("answer", "")
        sql_result = result.get("sql_result", [])
        rag_chunks = result.get("rag_chunks", [])
        generated_sql = result.get("generated_sql", "")
        source_count = len(rag_chunks)

        chips = [
            status_chip(intent, validation_status),
            f'<span class="chip">Route: {safe_text(intent.replace("_", " ").title() or "Unknown")}</span>',
            f'<span class="chip">Chart: {safe_text(chart_type.replace("_", " ").title())}</span>',
        ]
        if latency:
            chips.append(f'<span class="chip">Latency: {safe_text(latency)} ms</span>')
        if source_count:
            chips.append(f'<span class="chip">Sources: {source_count}</span>')

        st.markdown(
            f"""
            <div class="answer-card">
                <div class="section-eyebrow">MIRA clinical summary</div>
                <div class="answer-title">What MIRA found</div>
                <div class="answer-copy">{safe_text(answer_text)}</div>
                <div class="chip-row">{''.join(chips)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        primary_col, detail_col = st.columns([2.15, 0.85])
        with primary_col:
            st.markdown(
                """
                <div class="content-card">
                    <div class="section-eyebrow">Data output</div>
                    <h3 class="section-title">Visualization and returned data</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            chart_spec = result.get("chart_spec")
            chart_rendered = False
            if chart_spec and chart_type not in (None, "", "none"):
                try:
                    fig = pio.from_json(pio.to_json(chart_spec))
                    st.plotly_chart(style_chart(fig), use_container_width=True)
                    chart_rendered = True
                except Exception:
                    chart_rendered = False

            if not chart_rendered:
                fallback_fig = build_fallback_chart(sql_result, result.get("question", question))
                if fallback_fig:
                    st.plotly_chart(fallback_fig, use_container_width=True)
                elif sql_result:
                    render_key_numbers(sql_result)
                else:
                    st.info("This response did not return structured data for visualization.")

        with detail_col:
            st.markdown(
                f"""
                <div class="content-card">
                    <div class="section-eyebrow">Execution details</div>
                    <h3 class="section-title">Workflow status</h3>
                    <div class="detail-box"><div class="detail-label">Route</div><div class="detail-value">{safe_text(intent.replace('_', ' ').title() or 'Not available')}</div></div>
                    <div class="detail-box"><div class="detail-label">Validation</div><div class="detail-value">{safe_text(validation_status.replace('_', ' ').title() or 'Not applicable')}</div></div>
                    <div class="detail-box"><div class="detail-label">Clinical sources</div><div class="detail-value">{source_count}</div></div>
                    <div class="detail-box"><div class="detail-label">Latency</div><div class="detail-value">{safe_text(str(latency) + ' ms' if latency else 'Not available')}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if result.get("suggested_followup"):
                st.info(f"Suggested follow-up: {result['suggested_followup']}")

        tab_data, tab_sql, tab_sources, tab_trace = st.tabs(
            ["Returned Data", "SQL Evidence", "Clinical Sources", "Execution Trace"]
        )

        with tab_data:
            if sql_result:
                render_key_numbers(sql_result)
            else:
                st.info("No structured rows were returned for this response.")

        with tab_sql:
            if generated_sql:
                st.code(generated_sql, language="sql")
                if sql_result:
                    st.dataframe(make_dataframe(sql_result), use_container_width=True, hide_index=True)
            else:
                st.info("No SQL was required for this response.")

        with tab_sources:
            if rag_chunks:
                for idx, chunk in enumerate(rag_chunks, start=1):
                    doc_name = chunk.get("document_name", "Unknown document")
                    doc_type = chunk.get("document_type", "document")
                    score = chunk.get("relevance_score", "")
                    with st.expander(f"Source {idx}: {doc_name}"):
                        st.caption(f"Type: {doc_type} | Relevance: {score}")
                        st.write(chunk.get("chunk_text", ""))
            else:
                st.info("No clinical document passages were retrieved for this response.")

        with tab_trace:
            trace = result.get("tool_calls_log", [])
            if trace:
                steps = [item.get("node", "unknown") for item in trace]
                st.success(" → ".join(steps))
                st.json(trace)
            else:
                st.info("No execution trace was returned.")

            if mlflow_run_id:
                st.markdown(f"**MLflow run:** `{mlflow_run_id}`")
                st.markdown("[Open MLflow](http://localhost:5000)")
    else:
        st.markdown(
            """
            <div class="empty-state">
                Your answer, visualization, SQL evidence, source context, and execution trace will appear here after you run a question.
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# Query history page
# -----------------------------------------------------------------------------
elif selected_page == "Query History":
    render_header(
        "Query History",
        "Reopen previous MIRA analyses and review their questions, routes, and generated responses.",
    )

    try:
        history = get_history(limit=30)
    except Exception as exc:
        history = []
        st.error(f"Could not load query history: {exc}")

    if not history:
        st.markdown('<div class="empty-state">No saved MIRA queries are available yet.</div>', unsafe_allow_html=True)
    else:
        for item in history:
            question_text = item.get("question", "Untitled query")
            item_id = item.get("id")
            cols = st.columns([5, 1.15])
            with cols[0]:
                st.markdown(
                    f"""
                    <div class="content-card">
                        <div class="section-eyebrow">Saved analysis</div>
                        <div class="section-title">{safe_text(question_text)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with cols[1]:
                if st.button("Open", key=f"history_open_{item_id}", use_container_width=True):
                    try:
                        st.session_state.result = normalize_payload(get_history_item(item_id))
                        st.session_state.question = st.session_state.result.get("question", "")
                        st.session_state.page = "Ask MIRA"
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not load this query: {exc}")


# -----------------------------------------------------------------------------
# Evaluation page
# -----------------------------------------------------------------------------
elif selected_page == "Evaluation":
    render_header(
        "Evaluation",
        "Benchmark performance across structured querying, clinical retrieval, hybrid reasoning, and visualization.",
    )

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric_card("Overall accuracy", "96%", "48 of 50 questions", "navy")
    with metric_cols[1]:
        render_metric_card("SQL", "100%", "25 of 25", "teal")
    with metric_cols[2]:
        render_metric_card("RAG", "100%", "15 of 15", "green")
    with metric_cols[3]:
        render_metric_card("Hybrid", "100%", "7 of 7", "")

    st.markdown(
        """
        <div class="content-card">
            <div class="section-eyebrow">Evaluation summary</div>
            <h3 class="section-title">Core reasoning achieved 47 / 47 correct responses</h3>
            <p class="section-copy">
                MIRA completed every SQL, clinical RAG, and hybrid reasoning benchmark correctly. The two remaining benchmark misses were isolated to visualization-output comparison and chart-selection behavior rather than SQL execution, retrieval quality, or answer synthesis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    eval_df = pd.DataFrame(
        {
            "Capability": ["Text-to-SQL", "Clinical RAG", "Hybrid Reasoning", "Visualization"],
            "Correct": [25, 15, 7, 1],
            "Total": [25, 15, 7, 3],
            "Accuracy": [100.0, 100.0, 100.0, 33.33],
        }
    )
    fig = px.bar(
        eval_df,
        x="Capability",
        y="Accuracy",
        text="Accuracy",
        range_y=[0, 110],
        title="Benchmark Accuracy by Capability",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(style_chart(fig), use_container_width=True)
    st.caption("Evaluation uses the 50-question benchmark stored in the evaluation module.")


# -----------------------------------------------------------------------------
# About page
# -----------------------------------------------------------------------------
else:
    render_header(
        "About MIRA",
        "A personal engineering project exploring transparent clinical analytics over structured and unstructured healthcare data.",
    )

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown(
            """
            <div class="content-card">
                <div class="section-eyebrow">Project purpose</div>
                <h3 class="section-title">Clinical intelligence with evidence and traceability</h3>
                <p class="section-copy">
                    MIRA lets users ask questions in plain English and automatically routes them to structured synthetic patient data, clinical documents, or a hybrid workflow. Every response can include generated SQL, returned rows, source passages, validation status, and an execution trace.
                </p>
                <div class="detail-box"><div class="detail-label">Structured analytics</div><div class="detail-value">Text-to-SQL over curated healthcare marts and metrics models</div></div>
                <div class="detail-box"><div class="detail-label">Clinical knowledge</div><div class="detail-value">Retrieval-augmented generation over policies, protocols, and guidelines</div></div>
                <div class="detail-box"><div class="detail-label">Agent orchestration</div><div class="detail-value">LangGraph state machine with MCP database and vector tools</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="content-card">
                <div class="section-eyebrow">Technology stack</div>
                <h3 class="section-title">End-to-end implementation</h3>
                <div class="detail-box"><div class="detail-label">Data engineering</div><div class="detail-value">Synthea · Delta Lake · Parquet · PyArrow · Airflow</div></div>
                <div class="detail-box"><div class="detail-label">Analytics engineering</div><div class="detail-value">DuckDB · dbt Core · Great Expectations</div></div>
                <div class="detail-box"><div class="detail-label">AI and retrieval</div><div class="detail-value">LangGraph · Groq · Sentence Transformers · pgvector</div></div>
                <div class="detail-box"><div class="detail-label">Application and observability</div><div class="detail-value">FastAPI · Streamlit · Plotly · MLflow · Docker</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="content-card">
            <div class="section-eyebrow">Responsible use</div>
            <h3 class="section-title">Synthetic-data demonstration only</h3>
            <p class="section-copy">
                MIRA uses synthetic Synthea patient records and curated demonstration documents. It is not a medical device, does not provide clinical advice, and must not be used for real patient care or clinical decision-making.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )