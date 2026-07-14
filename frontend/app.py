import html
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

from api_client import ask_mira, get_history, get_history_item


st.set_page_config(
    page_title="MIRA | Medical Intelligence and Reasoning Agent",
    page_icon="🩺",
    layout="wide",
)


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f7f3ee;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1380px;
    }

    .hero {
        padding: 2.4rem 2.7rem;
        border-radius: 32px;
        background:
            radial-gradient(circle at top right, rgba(191, 168, 119, 0.30), transparent 34%),
            linear-gradient(135deg, #1f2421 0%, #36312c 55%, #6f6254 100%);
        color: #fffaf2;
        margin-bottom: 1.5rem;
        box-shadow: 0 24px 55px rgba(31, 36, 33, 0.22);
        border: 1px solid rgba(255, 250, 242, 0.12);
    }

    .hero h1 {
        font-size: 4.1rem;
        line-height: 1;
        margin: 0.9rem 0 0.9rem 0;
        font-weight: 900;
        letter-spacing: -0.055em;
        color: #fffaf2;
    }

    .hero p {
        font-size: 1.16rem;
        line-height: 1.72;
        color: rgba(255, 250, 242, 0.82);
        max-width: 1050px;
        margin-bottom: 0;
    }

    .pill {
        display: inline-block;
        padding: 0.42rem 0.95rem;
        border: 1px solid rgba(255, 250, 242, 0.24);
        border-radius: 999px;
        margin-right: 0.55rem;
        margin-bottom: 0.55rem;
        font-size: 0.9rem;
        color: rgba(255, 250, 242, 0.92);
        background: rgba(255, 250, 242, 0.08);
        backdrop-filter: blur(8px);
    }

    .section-card {
        padding: 1.35rem 1.55rem;
        border: 1px solid #e4ddd2;
        border-radius: 24px;
        background: #fffaf2;
        box-shadow: 0 10px 28px rgba(79, 70, 61, 0.08);
        margin-bottom: 1.1rem;
    }

    .template-card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: #fbf7ef;
        border: 1px solid #e5dccf;
        min-height: 118px;
        margin-bottom: 0.8rem;
    }

    .template-card h4 {
        margin: 0 0 0.45rem 0;
        font-size: 1rem;
        color: #26231f;
    }

    .template-card p {
        margin: 0;
        font-size: 0.92rem;
        color: #6f665b;
        line-height: 1.45;
    }

    .answer-card {
        padding: 1.55rem 1.8rem;
        border-radius: 24px;
        background: #fffaf2;
        border-left: 7px solid #b8a06a;
        box-shadow: 0 14px 34px rgba(79, 70, 61, 0.10);
        margin-top: 1rem;
        margin-bottom: 1.1rem;
    }

    .small-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.10em;
        color: #8a7a64;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .friendly-box {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: #fffaf2;
        border: 1px solid #e5dccf;
        margin-bottom: 0.9rem;
    }

    .status-good {
        padding: 0.48rem 0.8rem;
        border-radius: 999px;
        background: #e8eee5;
        color: #3f5d45;
        font-weight: 800;
        display: inline-block;
    }

    .status-warn {
        padding: 0.48rem 0.8rem;
        border-radius: 999px;
        background: #f5ead2;
        color: #7a5a21;
        font-weight: 800;
        display: inline-block;
    }

    .status-neutral {
        padding: 0.48rem 0.8rem;
        border-radius: 999px;
        background: #ece7df;
        color: #51483f;
        font-weight: 800;
        display: inline-block;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.85rem;
        color: #26231f;
    }

    div[data-testid="stMetricLabel"] {
        color: #7c7063;
    }

    .footer-note {
        font-size: 0.9rem;
        color: #766b5e;
        line-height: 1.55;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid #d8cbb8;
        background: #fffaf2;
        color: #332f29;
    }

    .stButton > button:hover {
        border-color: #b8a06a;
        color: #1f2421;
        background: #f6efe2;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: #2f332f;
        color: #fffaf2;
        border: 1px solid #2f332f;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: #1f2421;
        color: #fffaf2;
        border: 1px solid #b8a06a;
    }

    textarea {
        border-radius: 18px !important;
        background: #fffaf2 !important;
        border: 1px solid #ddd2c3 !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 0.4rem;
    }

    button[data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.45rem 0.9rem;
        color: #5f554a;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: #eee5d6;
        color: #26231f;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def safe_text(value: Any) -> str:
    return html.escape(str(value or ""))


def normalize_payload(result: Dict[str, Any]) -> Dict[str, Any]:
    """Protect the UI from slightly different backend response shapes."""
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


def build_fallback_chart(sql_result: List[Dict[str, Any]], question: str) -> Optional[Any]:
    if not sql_result:
        return None

    df = make_dataframe(sql_result)

    if df.empty or len(df.columns) < 2:
        return None

    question_lower = question.lower()

    # Convert likely Unix timestamp columns into datetime columns.
    for col in df.columns:
        col_lower = col.lower()
        if any(word in col_lower for word in ["date", "month", "time", "start"]):
            if pd.api.types.is_numeric_dtype(df[col]):
                # Your encounter_month_start values are Unix seconds.
                df[col] = pd.to_datetime(df[col], unit="s", errors="coerce")
            else:
                df[col] = pd.to_datetime(df[col], errors="ignore")

    numeric_cols = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col])
    ]

    date_like_cols = [
        col for col in df.columns
        if any(word in col.lower() for word in ["date", "month", "year", "time", "start"])
    ]

    categorical_cols = [
        col for col in df.columns
        if col not in numeric_cols
    ]

    # Metric card
    if len(df) == 1 and len(numeric_cols) == 1:
        value = df[numeric_cols[0]].iloc[0]
        fig = px.bar(
            x=[numeric_cols[0].replace("_", " ").title()],
            y=[value],
            title=numeric_cols[0].replace("_", " ").title(),
            labels={"x": "", "y": "Value"},
        )
        return fig

    # Strong rule for encounter volume by month
    if "encounter" in question_lower and "month" in question_lower:
        x_col = date_like_cols[0] if date_like_cols else df.columns[0]
        y_col = "encounter_count" if "encounter_count" in df.columns else numeric_cols[-1]

        grouped = df.groupby(x_col, as_index=False)[y_col].sum()

        return px.line(
            grouped,
            x=x_col,
            y=y_col,
            markers=True,
            title="Monthly Encounter Volume",
            labels={
                x_col: "Month",
                y_col: "Encounter Count",
            },
        )

    # Trend/time series
    if date_like_cols and numeric_cols:
        x_col = date_like_cols[0]
        y_col = numeric_cols[-1]

        grouped = df.groupby(x_col, as_index=False)[y_col].sum()

        return px.line(
            grouped,
            x=x_col,
            y=y_col,
            markers=True,
            title=f"{y_col.replace('_', ' ').title()} Over Time",
        )

    # Category + number
    if categorical_cols and numeric_cols:
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]

        grouped = df.groupby(x_col, as_index=False)[y_col].sum().sort_values(
            y_col, ascending=False
        )

        return px.bar(
            grouped,
            x=x_col,
            y=y_col,
            title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
        )

    # Two numeric columns
    if len(numeric_cols) >= 2:
        return px.scatter(
            df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"{numeric_cols[1].replace('_', ' ').title()} vs {numeric_cols[0].replace('_', ' ').title()}",
        )

    return None


def status_badge(intent: str, validation_status: str) -> str:
    if intent == "document_query":
        return '<span class="status-neutral">Clinical document answer</span>'

    if intent == "hybrid":
        return '<span class="status-neutral">Hybrid SQL + RAG response</span>'

    if validation_status == "valid":
        return '<span class="status-good">Validated SQL result</span>'

    if validation_status in ["suspect", "out_of_range"]:
        return '<span class="status-warn">Review recommended</span>'

    return '<span class="status-neutral">Generated response</span>'


def explain_for_user(intent: str, validation_status: str) -> None:
    st.markdown("### How to read this result")

    if intent == "data_query":
        st.success("MIRA answered this using structured patient data.")
        st.write(
            "The system translated your question into SQL, ran it against the synthetic clinical warehouse, "
            "validated the result, and summarized the output in plain English."
        )
    elif intent == "document_query":
        st.info("MIRA answered this using clinical policy or guideline documents.")
        st.write(
            "The system searched the clinical document knowledge base, retrieved relevant passages, "
            "and generated an answer grounded in those sources."
        )
    elif intent == "hybrid":
        st.info("MIRA used both patient data and clinical document context.")
        st.write(
            "The system analyzed structured synthetic patient data and combined the result with relevant "
            "clinical guideline or policy information."
        )
    else:
        st.write("MIRA generated a response based on the detected question type.")

    if validation_status == "valid":
        st.success("Validation status: valid. The output passed the system checks.")
    elif validation_status in ["suspect", "out_of_range"]:
        st.warning(
            "Validation status: warning. The system returned an answer, but the validator flagged a value "
            "for review. This can happen with synthetic clinical data."
        )
    elif validation_status in ["not_applicable", ""]:
        st.info("Validation was not applicable because this response was not primarily SQL-based.")


def render_key_numbers(sql_result: List[Dict[str, Any]]) -> None:
    df = make_dataframe(sql_result)

    if df.empty:
        st.info("No structured rows were returned.")
        return

    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    if len(df) == 1 and numeric_cols:
        cols = st.columns(min(len(numeric_cols), 4))
        for idx, col in enumerate(numeric_cols[:4]):
            cols[idx].metric(col.replace("_", " ").title(), f"{df[col].iloc[0]:,.2f}")
    else:
        st.dataframe(df, use_container_width=True)


# -----------------------------
# Session state
# -----------------------------
if "question" not in st.session_state:
    st.session_state.question = ""

if "result" not in st.session_state:
    st.session_state.result = None


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🩺 MIRA")
    st.caption("Medical Intelligence and Reasoning Agent")

    st.divider()

    st.markdown("### Recent Queries")
    try:
        history = get_history(limit=10)
    except Exception:
        history = []

    if history:
        for item in history:
            label = f"{item['id']} · {item.get('question', '')[:38]}"
            if st.button(label, key=f"history_{item['id']}", use_container_width=True):
                try:
                    st.session_state.result = normalize_payload(get_history_item(item["id"]))
                    st.session_state.question = st.session_state.result.get("question", "")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not load history item: {exc}")
    else:
        st.caption("No recent queries yet.")

    st.divider()
    st.caption("Synthetic Synthea patient data only. Not for clinical use.")


# -----------------------------
# Hero / Landing
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <div>
            <span class="pill">Text-to-SQL</span>
            <span class="pill">Clinical RAG</span>
            <span class="pill">LangGraph Agent</span>
            <span class="pill">MCP Tools</span>
            <span class="pill">MLflow Evaluation</span>
        </div>
        <h2>MIRA - Medical Intelligence and Reasoning Agent</h2>
        <p>
            A clinical intelligence demo that lets users ask healthcare analytics and policy
            questions in plain English. MIRA routes each question to structured synthetic patient
            data, clinical documents, or both — then returns a transparent answer with SQL evidence,
            source context, validation status, and traceability.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Guided templates
# -----------------------------
st.markdown("## What would you like to ask?")

template_tabs = st.tabs(
    [
        "Population",
        "Encounters",
        "Chronic Conditions",
        "Labs & A1c",
        "Policies & Guidelines",
        "Hybrid Questions",
    ]
)

templates = {
    "Population": [
        (
            "Patient count",
            "How many patients are in the dataset?",
            "Get the total number of synthetic patients.",
        ),
        (
            "Age profile",
            "What is the age distribution of patients?",
            "Understand the overall demographic spread.",
        ),
        (
            "Gender breakdown",
            "Show the patient count by gender.",
            "Review basic population composition.",
        ),
    ],
    "Encounters": [
        (
            "Monthly volume",
            "Show encounter volume by month.",
            "Visualize encounter trends over time.",
        ),
        (
            "Encounter class",
            "Show encounter count by encounter class.",
            "Compare inpatient, outpatient, emergency, and other visit types.",
        ),
        (
            "Average length",
            "What is the average encounter duration by encounter class?",
            "Review utilization by encounter type.",
        ),
    ],
    "Chronic Conditions": [
        (
            "Diabetes count",
            "How many diabetic patients are there?",
            "Find the size of the diabetic cohort.",
        ),
        (
            "Common conditions",
            "What are the five most common conditions?",
            "Identify high-prevalence conditions.",
        ),
        (
            "Heart failure",
            "How many patients have heart failure?",
            "Review a high-risk chronic disease group.",
        ),
    ],
    "Labs & A1c": [
        (
            "A1c summary",
            "Summarize A1c values for diabetic patients.",
            "Understand glycemic control in the diabetic cohort.",
        ),
        (
            "Elevated A1c",
            "How many diabetic patients have elevated A1c values?",
            "Identify patients above clinical thresholds.",
        ),
        (
            "A1c chart",
            "Show the distribution of A1c values.",
            "Visualize lab result spread.",
        ),
    ],
    "Policies & Guidelines": [
        (
            "Readmission policy",
            "What does the hospital readmission policy say about heart failure?",
            "Retrieve internal policy guidance.",
        ),
        (
            "ADA guidance",
            "What are the ADA recommendations for A1c management?",
            "Retrieve diabetes guideline context.",
        ),
        (
            "Medication reconciliation",
            "What does the medication reconciliation protocol require?",
            "Review clinical workflow policy.",
        ),
    ],
    "Hybrid Questions": [
        (
            "Diabetes + guideline",
            "How many diabetic patients have elevated A1c values, and what do the guidelines recommend?",
            "Combine patient data with clinical guideline context.",
        ),
        (
            "A1c interpretation",
            "For diabetic patients, summarize the A1c data and explain the relevant guideline context.",
            "Analyze data and explain what it means clinically.",
        ),
        (
            "Heart failure + readmission",
            "How many patients have heart failure, and what does the readmission policy recommend?",
            "Combine cohort analytics with hospital policy.",
        ),
    ],
}

for tab, category in zip(template_tabs, templates.keys()):
    with tab:
        cols = st.columns(3)
        for idx, (title, question, description) in enumerate(templates[category]):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="template-card">
                        <h4>{safe_text(title)}</h4>
                        <p>{safe_text(description)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Use this question", key=f"{category}_{idx}", use_container_width=True):
                    st.session_state.question = question
                    st.rerun()


# -----------------------------
# Ask box
# -----------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### Ask your own question")

question = st.text_area(
    "Ask a clinical analytics or policy question",
    value=st.session_state.question,
    placeholder="Example: Show encounter volume by month.",
    height=105,
    label_visibility="collapsed",
)

col_ask, col_clear, col_space = st.columns([1.2, 1.2, 5])

with col_ask:
    run_clicked = st.button("Ask MIRA", type="primary", use_container_width=True)

with col_clear:
    clear_clicked = st.button("Clear", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if clear_clicked:
    st.session_state.question = ""
    st.session_state.result = None
    st.rerun()

if run_clicked and question.strip():
    st.session_state.question = question.strip()
    with st.spinner("MIRA is analyzing the question, selecting tools, and generating a transparent answer..."):
        try:
            st.session_state.result = normalize_payload(ask_mira(question.strip()))
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            st.session_state.result = None


# -----------------------------
# Results
# -----------------------------
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

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="small-label">MIRA Clinical Summary</div>
            <h2>What MIRA found</h2>
            <p style="font-size:1.08rem; line-height:1.8;">
                {safe_text(answer_text)}
            </p>
            <br/>
            {status_badge(intent, validation_status)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(5)
    metric_cols[0].metric("Question Type", intent.replace("_", " ").title())
    metric_cols[1].metric("Validation", validation_status.replace("_", " ").title())
    metric_cols[2].metric("Chart", chart_type.replace("_", " ").title())
    metric_cols[3].metric("Latency", f"{latency} ms" if latency else "")
    metric_cols[4].metric("MLflow Run", mlflow_run_id[:8] if mlflow_run_id else "")

    tab_summary, tab_visuals, tab_explain, tab_sql, tab_sources, tab_trace = st.tabs(
        [
            "Summary",
            "Visuals",
            "Plain-English Explanation",
            "SQL Evidence",
            "Clinical Sources",
            "Technical Trace",
        ]
    )

    with tab_summary:
        st.markdown("### Direct answer")
        st.write(answer_text)

        if result.get("suggested_followup"):
            st.info(f"Suggested follow-up: {result['suggested_followup']}")

        if sql_result:
            st.markdown("### Key returned data")
            render_key_numbers(sql_result)

    with tab_visuals:
        st.markdown("### Visualization")

        chart_spec = result.get("chart_spec")
        chart_rendered = False

        if chart_spec and chart_type not in (None, "", "none"):
            try:
                fig = pio.from_json(pio.to_json(chart_spec))
                st.plotly_chart(fig, use_container_width=True)
                chart_rendered = True
            except Exception:
                chart_rendered = False

        if not chart_rendered:
            fallback_fig = build_fallback_chart(sql_result, result.get("question", st.session_state.question))
            if fallback_fig:
                st.plotly_chart(fallback_fig, use_container_width=True)
            elif sql_result:
                st.info("No chart was generated for this query, but the structured result is shown below.")
                st.dataframe(make_dataframe(sql_result), use_container_width=True)
            else:
                st.info("No structured data was returned for visualization.")

    with tab_explain:
        explain_for_user(intent, validation_status)

        st.markdown("### Why this matters")
        if intent == "data_query":
            st.write(
                "This type of result helps clinical operations teams quickly inspect patient populations, "
                "encounter trends, condition prevalence, and lab patterns without manually writing SQL."
            )
        elif intent == "document_query":
            st.write(
                "This type of result helps users find relevant clinical policy or guideline information "
                "without manually searching through documents."
            )
        elif intent == "hybrid":
            st.write(
                "Hybrid answers are useful when a user needs both the measured patient-data result and "
                "the clinical guideline or policy context needed to interpret it."
            )

        st.markdown(
            """
            <div class="footer-note">
            MIRA uses synthetic patient data generated by Synthea. It is a portfolio/demo system and
            should not be used for real clinical decisions.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_sql:
        st.markdown("### SQL Evidence")

        if generated_sql:
            st.code(generated_sql, language="sql")
        else:
            st.info("No SQL was generated for this response.")

        if sql_result:
            st.markdown("### SQL Result")
            st.dataframe(make_dataframe(sql_result), use_container_width=True)

    with tab_sources:
        st.markdown("### Retrieved Clinical Sources")

        if rag_chunks:
            for idx, chunk in enumerate(rag_chunks, start=1):
                doc_name = chunk.get("document_name", "Unknown document")
                doc_type = chunk.get("document_type", "document")
                score = chunk.get("relevance_score", "")

                with st.expander(f"Source {idx}: {doc_name}"):
                    st.caption(f"Type: {doc_type} | Score: {score}")
                    st.write(chunk.get("chunk_text", ""))
        else:
            st.info("No clinical document chunks were retrieved for this response.")

    with tab_trace:
        st.markdown("### Execution Path")

        trace = result.get("tool_calls_log", [])

        if trace:
            steps = [item.get("node", "unknown") for item in trace]
            st.success(" → ".join(steps))
            st.json(trace)
        else:
            st.info("No technical trace was returned.")

        if mlflow_run_id:
            st.markdown("### MLflow Tracking")
            st.write(f"Run ID: `{mlflow_run_id}`")
            st.markdown("[Open MLflow](http://localhost:5000)")
else:
    st.markdown(
        """
        <div class="friendly-box">
            <b>Tip:</b> Choose a question template above or type your own clinical analytics question.
            For the best portfolio screenshot, use a hybrid question such as:
            <i>“How many diabetic patients have elevated A1c values, and what do the guidelines recommend?”</i>
        </div>
        """,
        unsafe_allow_html=True,
    )