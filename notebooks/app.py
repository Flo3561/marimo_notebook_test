import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="SQLite Explorer")


@app.cell
def _():
    import sqlite3
    import urllib.request

    import altair as alt
    import marimo as mo
    import pandas as pd

    return alt, mo, pd, sqlite3, urllib


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # SQLite Explorer

    Liest eine SQLite-Datenbank direkt im Browser (Pyodide/WASM), führt
    SQL-Queries aus und plottet das Resultat. Standardmässig wird
    `public/data.db` verwendet – du kannst aber auch eine eigene Datei hochladen.
    """)
    return


@app.cell
def _(mo):
    upload = mo.ui.file(
        filetypes=[".db", ".sqlite", ".sqlite3"],
        label="Eigene SQLite-Datei laden (optional)",
    )
    upload
    return (upload,)


@app.cell
def _(mo, upload, urllib):
    def load_db_bytes() -> tuple[bytes, str]:
        if upload.value:
            return upload.value[0].contents, upload.value[0].name
        # Lokal ist das ein Pfad, in WASM eine URL relativ zur Seite.
        location = mo.notebook_location() / "public" / "data.db"
        if str(location).startswith("http"):
            with urllib.request.urlopen(str(location)) as resp:
                return resp.read(), "public/data.db"
        return location.read_bytes(), "public/data.db"

    db_bytes, db_name = load_db_bytes()
    return db_bytes, db_name


@app.cell
def _(db_bytes, sqlite3):
    # In-Memory-DB aus den Bytes: funktioniert identisch lokal und im Browser.
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.deserialize(db_bytes)
    return (conn,)


@app.cell
def _(conn, db_name, mo, pd):
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    schemas = {
        t: pd.read_sql_query(f'PRAGMA table_info("{t}")', conn)[
            ["name", "type", "notnull", "pk"]
        ]
        for t in tables
    }
    mo.vstack(
        [
            mo.md(f"**Datenbank:** `{db_name}` – {len(tables)} Tabelle(n)"),
            mo.accordion({t: mo.ui.table(s, selection=None) for t, s in schemas.items()}),
        ]
    )
    return (tables,)


@app.cell
def _(mo, tables):
    if "sales" in tables:
        default_query = (
            "SELECT day, region, SUM(revenue) AS revenue\n"
            "FROM sales\n"
            "GROUP BY day, region\n"
            "ORDER BY day"
        )
    elif tables:
        default_query = f'SELECT * FROM "{tables[0]}" LIMIT 1000'
    else:
        default_query = "SELECT 1 AS x"

    query_form = mo.ui.code_editor(
        value=default_query, language="sql", min_height=120
    ).form(submit_button_label="Query ausführen")
    query_form
    return default_query, query_form


@app.cell
def _(conn, default_query, mo, pd, query_form):
    query = query_form.value or default_query
    try:
        df = pd.read_sql_query(query, conn)
        result_view = mo.ui.table(df, page_size=10, selection=None)
    except Exception as e:
        df = pd.DataFrame()
        result_view = mo.callout(mo.md(f"**Fehler:** `{e}`"), kind="danger")
    result_view
    return (df,)


@app.cell
def _(df, mo, pd):
    def parse_dates(frame: pd.DataFrame) -> pd.DataFrame:
        """Textspalten, die wie ISO-Daten aussehen, in datetime umwandeln."""
        out = frame.copy()
        for col in out.columns:
            if pd.api.types.is_string_dtype(out[col]) or out[col].dtype == object:
                sample = out[col].dropna().astype(str).head(20)
                if len(sample) and sample.str.match(r"^\d{4}-\d{2}-\d{2}").all():
                    out[col] = pd.to_datetime(out[col], errors="coerce")
        return out

    plot_df = parse_dates(df)
    columns = list(plot_df.columns)
    numeric = [c for c in columns if pd.api.types.is_numeric_dtype(plot_df[c])]

    chart_type = mo.ui.dropdown(
        ["line", "bar", "point", "area"], value="line", label="Diagramm"
    )
    x_col = mo.ui.dropdown(
        columns, value=columns[0] if columns else None, label="x"
    )
    y_col = mo.ui.dropdown(
        columns,
        value=(numeric[-1] if numeric else (columns[-1] if columns else None)),
        label="y",
    )
    color_col = mo.ui.dropdown(["—"] + columns, value="—", label="Farbe")

    mo.hstack([chart_type, x_col, y_col, color_col], justify="start")
    return chart_type, color_col, plot_df, x_col, y_col


@app.cell
def _(alt, chart_type, color_col, mo, plot_df, x_col, y_col):
    mo.stop(
        plot_df.empty or not x_col.value or not y_col.value,
        mo.md("_Keine Daten zum Plotten._"),
    )

    base = alt.Chart(plot_df)
    mark = {
        "line": base.mark_line(),
        "bar": base.mark_bar(),
        "point": base.mark_point(),
        "area": base.mark_area(opacity=0.7),
    }[chart_type.value]

    encoding = {
        "x": alt.X(x_col.value),
        "y": alt.Y(y_col.value),
        "tooltip": list(plot_df.columns),
    }
    if color_col.value != "—":
        encoding["color"] = alt.Color(color_col.value)

    chart = mo.ui.altair_chart(
        mark.encode(**encoding).properties(width="container", height=380)
    )
    chart
    return


if __name__ == "__main__":
    app.run()
