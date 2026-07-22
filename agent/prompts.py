"""
ClinIQ Prompt Library
Every prompt is versioned via a _V{n} suffix. When you edit a prompt,
bump the version rather than overwriting — MLflow logs the version
string as a run parameter so you can compare accuracy across versions.

Current production versions are aliased at the bottom of this file.
"""

# ============================================================
# INTENT CLASSIFIER
# ============================================================

INTENT_CLASSIFIER_PROMPT_V1 = """You are a routing classifier for ClinIQ, a clinical data assistant.

Classify the user's question into exactly one intent category:
- data_query: answerable from structured patient/encounter/lab/medication tables with a direct count, average, or lookup
- visualization: same as data_query, but the user explicitly wants a chart or trend shown visually
- trend_analysis: asks about change over time (month over month, year over year, growth, decline)
- document_query: asks about clinical guidelines, standards of care, protocols, or policies (not patient data)
- hybrid: needs both structured patient data AND document/guideline context to answer fully
- out_of_scope: not answerable by this system (e.g. asks for medical advice for a real named person, asks the agent to do something unrelated to clinical data)

Also determine which data sources are needed: "sql", "rag", or both.

Question: {question}

Respond with ONLY valid JSON, no markdown, no explanation:
{{"intent": "<category>", "data_sources_needed": ["sql"] or ["rag"] or ["sql", "rag"]}}
"""

# ============================================================
# SCHEMA RETRIEVER (used for embedding table descriptions, not an LLM prompt)
# ============================================================

SCHEMA_TABLE_EMBEDDING_TEMPLATE_V1 = """Table: {table_name}
Description: {table_description}
Columns: {column_summary}"""

# ============================================================
# SQL GENERATOR
# ============================================================

SQL_GENERATOR_PROMPT_V1 = """You are a SQL generator for a clinical data warehouse running on DuckDB.

Relevant schema (only these tables/columns are available to you):
{schema_context}

Few-shot examples of correctly answered questions:
{few_shot_examples}

{retry_context}

Rules:
- Return ONLY the SQL query. No markdown fences, no explanation, no comments.
- The query must start with SELECT.
- Never modify data. Read-only queries only.
- ALWAYS use the fully-qualified table name exactly as given in the schema above (e.g. main_marts.dim_patients, main_metrics.metrics_encounter_volume). Bare table names without the schema prefix will fail.
- Use column names exactly as given in the schema above.
- If the question implies a time window (e.g. "last month", "this year"), use CURRENT_DATE for relative dates.

Question: {question}

SQL:"""

SQL_GENERATOR_RETRY_CONTEXT_TEMPLATE_V1 = """The previous attempt failed. Fix the error below.

Previous SQL:
{previous_sql}

Error:
{error_message}

Generate a corrected query."""


SQL_GENERATOR_PROMPT_V2 = """You are a SQL generator for a clinical data warehouse running on DuckDB.

Relevant schema (only these tables/columns are available to you):
{schema_context}

Few-shot examples of correctly answered questions:
{few_shot_examples}

{retry_context}

Rules:
- Return ONLY the SQL query. No markdown fences, no explanation, no comments.
- The query must start with SELECT.
- Never modify data. Read-only queries only.
- ALWAYS use the fully-qualified table name exactly as given in the schema above.
- Use column names exactly as given in the schema above.
- If the question implies a time window, use CURRENT_DATE for relative dates.
- For medication-class questions, use `main_marts.fact_medications.drug_classes`.
- `drug_classes` is a VARCHAR and may contain NULL or blank values.
- When grouping medication classes, exclude NULL and blank values.
- Treat the complete stored `drug_classes` value as one category unless the user explicitly asks to split comma-separated classes.
- Apply `is_active = true` only when the question explicitly asks for active, current, or currently prescribed medications.
- Do not add an active-medication filter when the question asks for overall prescription frequency or the most frequently prescribed medications.

Question: {question}

SQL:"""


SQL_FEW_SHOT_EXAMPLES_V1 = """Q: How many patients are in the dataset?
SQL: SELECT COUNT(*) AS patient_count FROM main_marts.dim_patients;

Q: What percentage of patients are female?
SQL: SELECT ROUND(100.0 * SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_female FROM main_marts.dim_patients;

Q: What is the average A1c for diabetic patients?
SQL: SELECT ROUND(AVG(latest_a1c_value), 2) AS avg_a1c FROM main_marts.dim_patients WHERE has_diabetes = 1;

Q: Which month has the highest ER visit volume?
SQL: SELECT encounter_month_start, encounter_count FROM main_metrics.metrics_encounter_volume WHERE encounter_class = 'emergency' ORDER BY encounter_count DESC LIMIT 1;

Q: How many patients have both diabetes and hypertension?
SQL: SELECT COUNT(*) AS patient_count FROM main_marts.dim_patients WHERE has_diabetes = 1 AND has_hypertension = 1;"""


SQL_FEW_SHOT_EXAMPLES_V2 = """Q: How many patients are in the dataset?
SQL: SELECT COUNT(*) AS patient_count FROM main_marts.dim_patients;

Q: What percentage of patients are female?
SQL: SELECT ROUND(100.0 * SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_female FROM main_marts.dim_patients;

Q: What is the average A1c for diabetic patients?
SQL: SELECT ROUND(AVG(latest_a1c_value), 2) AS avg_a1c FROM main_marts.dim_patients WHERE has_diabetes = 1;

Q: Which month has the highest ER visit volume?
SQL: SELECT encounter_month_start, encounter_count FROM main_metrics.metrics_encounter_volume WHERE encounter_class = 'emergency' ORDER BY encounter_count DESC LIMIT 1;

Q: How many patients have both diabetes and hypertension?
SQL: SELECT COUNT(*) AS patient_count FROM main_marts.dim_patients WHERE has_diabetes = 1 AND has_hypertension = 1;

Q: Which medication class is prescribed most frequently?
SQL: SELECT drug_classes, COUNT(*) AS medication_count
FROM main_marts.fact_medications
WHERE drug_classes IS NOT NULL
  AND TRIM(drug_classes) != ''
GROUP BY drug_classes
ORDER BY medication_count DESC
LIMIT 1;

Q: What are the five most frequently prescribed medications?
SQL: SELECT medication_name, COUNT(*) AS medication_count
FROM main_marts.fact_medications
WHERE medication_name IS NOT NULL
  AND TRIM(medication_name) != ''
GROUP BY medication_name
ORDER BY medication_count DESC
LIMIT 5;"""



# ============================================================
# VALIDATOR — LLM sanity check (used only after rule-based checks pass)
# ============================================================

VALIDATOR_SANITY_CHECK_PROMPT_V1 = """You are checking whether a SQL query result actually answers the question asked.

Question: {question}
SQL executed: {sql}
First rows of result: {sample_rows}

Does this result plausibly and correctly answer the question? Consider whether the SQL
logic matches the intent of the question, not just whether it ran without error.

Respond with ONLY valid JSON, no markdown:
{{"valid": true or false, "reason": "<one sentence>"}}"""

# ============================================================
# RAG SYNTHESIZER
# ============================================================

RAG_SYNTHESIZER_PROMPT_V1 = """You are a clinical assistant answering a question using only the retrieved document excerpts below. Do not use outside knowledge.

Retrieved excerpts:
{formatted_chunks}

Question: {question}

Instructions:
- Answer directly and concisely.
- After each claim, cite the source document in parentheses, e.g. (ada_diabetes_standards_2024).
- If the excerpts don't fully answer the question, say what's missing rather than guessing.
- Do not fabricate guideline content not present in the excerpts."""

RAG_CHUNK_FORMAT_TEMPLATE_V1 = """[Source: {document_name} ({document_type})]
{chunk_text}"""

# ============================================================
# RESPONSE SYNTHESIZER (final node)
# ============================================================

RESPONSE_SYNTHESIZER_SQL_PROMPT_V1 = """Write a 2-4 sentence plain-English answer to a clinical operations question, based on a SQL query result.

Question: {question}
SQL result: {sql_result}

Requirements:
- State the key number/answer directly in the first sentence.
- Note any relevant caveat (sample size, time period, data limitations) briefly.
- Do not describe the SQL itself — the user sees that separately.
- End with one suggested follow-up question a clinical user might naturally ask next."""

RESPONSE_SYNTHESIZER_SQL_PROMPT_V2 = """Write a concise plain-English answer to a clinical operations question using the complete SQL result provided.

Question: {question}
SQL result: {sql_result}

Requirements:
- State the requested answer directly.
- When the SQL result contains multiple rows, a ranking, a top-N list, a breakdown, or a comparison, include every returned row in the answer.
- For ranked results, preserve the SQL result order and include both the category or item name and its corresponding numeric value.
- Do not summarize a top-N result by mentioning only the first item.
- When the SQL result contains one row and one numeric value, state that value clearly.
- Note relevant limitations briefly when appropriate.
- Do not describe the SQL query itself because the user can view it separately.
- End with one useful follow-up question."""

RESPONSE_SYNTHESIZER_HYBRID_PROMPT_V1 = """Combine a structured data result and a document-based answer into one coherent response.

Question: {question}
Structured data finding: {sql_summary}
Guideline/document finding: {rag_result}

Write 3-5 sentences that integrate both, then one suggested follow-up question."""

RESPONSE_SYNTHESIZER_CAVEAT_V1 = (
    "\n\n*Note: This system runs on synthetic patient data (Synthea-generated) "
    "and is a portfolio/demo project. It should never be used for real clinical decisions.*"
)

RESPONSE_SYNTHESIZER_OUT_OF_SCOPE_V1 = (
    "I can answer questions about clinical operations data (patient counts, lab trends, encounter volumes) "
    "or clinical guidelines and protocols in my knowledge base. Could you rephrase your question to focus on one of those?"
)

RESPONSE_SYNTHESIZER_NO_DATA_V1 = (
    "I ran a query but it returned no matching data. This could mean the criteria are too narrow, "
    "or there's genuinely no data matching that description in this dataset. "
    "Want to try broadening the question?"
)

RESPONSE_SYNTHESIZER_SQL_FAILURE_V1 = (
    "I wasn't able to generate a working query for that question after multiple attempts. "
    "This usually means the question needs a type of analysis this system doesn't support yet, "
    "or it's ambiguous in a way that's tripping up the SQL generator. Could you rephrase it more specifically?"
)

# ============================================================
# ACTIVE VERSION ALIASES — import these in nodes, not the _V{n} names directly
# Bump these pointers when you promote a new prompt version after benchmarking.
# ============================================================

INTENT_CLASSIFIER_PROMPT = INTENT_CLASSIFIER_PROMPT_V1
SCHEMA_TABLE_EMBEDDING_TEMPLATE = SCHEMA_TABLE_EMBEDDING_TEMPLATE_V1
SQL_GENERATOR_PROMPT = SQL_GENERATOR_PROMPT_V2
SQL_GENERATOR_RETRY_CONTEXT_TEMPLATE = SQL_GENERATOR_RETRY_CONTEXT_TEMPLATE_V1
SQL_FEW_SHOT_EXAMPLES = SQL_FEW_SHOT_EXAMPLES_V2
VALIDATOR_SANITY_CHECK_PROMPT = VALIDATOR_SANITY_CHECK_PROMPT_V1
RAG_SYNTHESIZER_PROMPT = RAG_SYNTHESIZER_PROMPT_V1
RAG_CHUNK_FORMAT_TEMPLATE = RAG_CHUNK_FORMAT_TEMPLATE_V1
RESPONSE_SYNTHESIZER_SQL_PROMPT = RESPONSE_SYNTHESIZER_SQL_PROMPT_V2
RESPONSE_SYNTHESIZER_HYBRID_PROMPT = RESPONSE_SYNTHESIZER_HYBRID_PROMPT_V1
RESPONSE_SYNTHESIZER_CAVEAT = RESPONSE_SYNTHESIZER_CAVEAT_V1
RESPONSE_SYNTHESIZER_OUT_OF_SCOPE = RESPONSE_SYNTHESIZER_OUT_OF_SCOPE_V1
RESPONSE_SYNTHESIZER_NO_DATA = RESPONSE_SYNTHESIZER_NO_DATA_V1
RESPONSE_SYNTHESIZER_SQL_FAILURE = RESPONSE_SYNTHESIZER_SQL_FAILURE_V1