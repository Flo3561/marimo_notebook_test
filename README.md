# marimo SQLite Explorer

Ein marimo-Notebook, das eine SQLite-Datenbank liest, SQL-Queries ausführt und die
Resultate mit Altair plottet. Es läuft komplett im Browser (WASM/Pyodide) und wird
über GitHub Pages veröffentlicht.

## Lokal

```bash
uv sync
uv run python scripts/create_sample_db.py   # Beispiel-DB erzeugen (optional)
uv run marimo edit notebooks/app.py          # bearbeiten
uv run marimo run notebooks/app.py           # als App starten
```

## Eigene Datenbank

Lege deine Datei als `notebooks/public/data.db` ab. Alles in `notebooks/public/`
wird beim Export mitkopiert und im Browser per HTTP geladen.
Alternativ kann man im Notebook eine `.db`-Datei hochladen (bleibt lokal im Browser).

## WASM-Export testen

```bash
uv run marimo export html-wasm notebooks/app.py -o dist --mode run
python -m http.server --directory dist
```

## GitHub Pages

1. Repo auf GitHub pushen (Branch `main`).
2. Unter *Settings → Pages → Source* **GitHub Actions** wählen.
3. Der Workflow [.github/workflows/deploy.yml](.github/workflows/deploy.yml) exportiert und deployt bei jedem Push.

Hinweis: Die Datenbank ist auf GitHub Pages öffentlich abrufbar – keine sensiblen Daten verwenden.
