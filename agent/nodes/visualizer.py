from datetime import datetime, timedelta, timezone

import plotly.express as px
import plotly.graph_objects as go
from agent.state import ClinIQState


def _is_date_column_name(column_name: str) -> bool:
    """
    Identify columns that represent dates or timestamps based on their names.
    This prevents ordinary numeric columns from being mistaken for Unix dates.
    """
    name = column_name.lower()

    date_tokens = (
        "date",
        "datetime",
        "timestamp",
        "month_start",
        "year_month",
    )

    return any(token in name for token in date_tokens)


def _is_unix_timestamp(value) -> bool:
    """
    Return True for plausible Unix timestamps, including negative timestamps
    representing dates before 1970.
    """
    if not isinstance(value, (int, float)):
        return False

    return -2_208_988_800 <= float(value) <= 4_102_444_800


def _convert_unix_date_columns(sql_result: list) -> list:
    """
    Convert Unix timestamps to YYYY-MM-DD strings only for date-like columns.
    A copied result is returned so the original SQL output is not modified.
    """
    converted_rows = []

    for row in sql_result:
        converted_row = dict(row)

        for column, value in converted_row.items():
            if (
                _is_date_column_name(column)
                and _is_unix_timestamp(value)
            ):
                epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

                converted_row[column] = (
                    epoch + timedelta(seconds=int(value))
                ).strftime("%Y-%m-%d")

        converted_rows.append(converted_row)

    return converted_rows


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

        if (
            _is_date_column_name(col)
            and (
                _looks_like_date(str(val))
                or _is_unix_timestamp(val)
            )
        ):
            types[col] = "date"

        elif isinstance(val, (int, float)):
            types[col] = "numeric"

        elif isinstance(val, str) and _looks_like_date(val):
            types[col] = "date"

        else:
            types[col] = "categorical"

    numeric_cols = [
        column
        for column, column_type in types.items()
        if column_type == "numeric"
    ]

    categorical_cols = [
        column
        for column, column_type in types.items()
        if column_type == "categorical"
    ]

    date_cols = [
        column
        for column, column_type in types.items()
        if column_type == "date"
    ]

    if date_cols and numeric_cols:
        return "line"

    if (
        len(categorical_cols) == 1
        and len(numeric_cols) == 1
    ):
        return "bar"

    if len(numeric_cols) == 2:
        return "scatter"

    return "table"


def _looks_like_date(val: str) -> bool:
    return bool(len(val) >= 7 and val[:4].isdigit() and "-" in val)


def visualizer(state: ClinIQState) -> ClinIQState:
    original_sql_result = state.get("sql_result", [])
    sql_result = _convert_unix_date_columns(original_sql_result)

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