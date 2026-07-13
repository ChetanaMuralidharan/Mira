import plotly.express as px
import plotly.graph_objects as go
from agent.state import ClinIQState


def _infer_chart_type(sql_result: list) -> str:
    if not sql_result:
        return "none"

    row = sql_result[0]
    columns = list(row.keys())
    n_cols = len(columns)

    if len(sql_result) == 1 and n_cols == 1:
        value = next(iter(row.values()))
        if isinstance(value, (int, float)):
            return "metric_card"
        return "table"
    if n_cols > 5:
        return "table"

    types = {}
    for col in columns:
        val = row[col]
        if isinstance(val, (int, float)):
            types[col] = "numeric"
        elif isinstance(val, str) and _looks_like_date(val):
            types[col] = "date"
        else:
            types[col] = "categorical"

    numeric_cols = [c for c, t in types.items() if t == "numeric"]
    categorical_cols = [c for c, t in types.items() if t == "categorical"]
    date_cols = [c for c, t in types.items() if t == "date"]

    if date_cols and numeric_cols:
        return "line"
    if categorical_cols and numeric_cols and len(categorical_cols) == 1 and len(numeric_cols) == 1:
        return "bar"
    if len(numeric_cols) == 2:
        return "scatter"
    return "table"


def _looks_like_date(val: str) -> bool:
    return bool(len(val) >= 7 and val[:4].isdigit() and "-" in val)


def visualizer(state: ClinIQState) -> ClinIQState:
    sql_result = state.get("sql_result", [])
    chart_type = _infer_chart_type(sql_result)
    state["chart_type"] = chart_type

    if chart_type == "none" or not sql_result:
        state["chart_spec"] = None
        return state

    columns = list(sql_result[0].keys())

    try:
        if chart_type == "bar":
            cat_col = next(c for c in columns if isinstance(sql_result[0][c], str))
            num_col = next(c for c in columns if isinstance(sql_result[0][c], (int, float)))
            fig = px.bar(sql_result, x=cat_col, y=num_col)
        elif chart_type == "line":
            date_col = next(c for c in columns if _looks_like_date(str(sql_result[0][c])))
            num_col = next(c for c in columns if isinstance(sql_result[0][c], (int, float)))
            fig = px.line(sql_result, x=date_col, y=num_col)
        elif chart_type == "scatter":
            num_cols = [c for c in columns if isinstance(sql_result[0][c], (int, float))]
            fig = px.scatter(sql_result, x=num_cols[0], y=num_cols[1])
        elif chart_type == "metric_card":
            value = list(sql_result[0].values())[0]
            fig = go.Figure(go.Indicator(mode="number", value=value))
        else:  # table
            fig = go.Figure(go.Table(
                header=dict(values=columns),
                cells=dict(values=[[row[c] for row in sql_result] for c in columns]),
            ))

        state["chart_spec"] = fig.to_dict()
    except (StopIteration, IndexError, KeyError, ValueError):
        state["chart_type"] = "table"
        fig = go.Figure(go.Table(
            header=dict(values=columns),
            cells=dict(values=[[row[c] for row in sql_result] for c in columns]),
        ))
        state["chart_spec"] = fig.to_dict()

    return state