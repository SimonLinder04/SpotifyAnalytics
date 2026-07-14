# Repository Guidelines

## Project Structure & Module Organization

`SpotifyAnalyticsApplicaton.py` is the command-line entry point. Application code lives in `spotify_analytics/`: `menu.py` owns prompts and actions, `client.py` handles Spotify API requests, `auth.py` implements PKCE login, `display.py` renders results, and `settings.py` persists display preferences. `Pokemon.py` provides the padded-data printer. Root `settings.json` stores the selected view and item limit. VS Code settings are under `.vscode/`. There is currently no `tests/` directory or asset bundle.

Keep new API operations in `client.py`, authentication concerns in `auth.py`, and user-facing menu behavior in `menu.py`. Avoid adding logic to the top-level launcher.

## Build, Test, and Development Commands

Use Python 3.13 from PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe SpotifyAnalyticsApplicaton.py
.\.venv\Scripts\python.exe -m compileall SpotifyAnalyticsApplicaton.py spotify_analytics
```

The first command creates an isolated environment, the second installs `requests`, the third starts the CLI, and the fourth performs a syntax/import compilation check. VS Code users can run the configured launch profile with `F5`.

## Coding Style & Naming Conventions

Follow standard Python conventions: four-space indentation, `snake_case` for functions and variables, `PascalCase` for classes, and `UPPER_CASE` for constants. Use lowercase module names for new files. Keep functions focused and add type hints when introducing non-obvious data structures. No formatter or linter is configured, so preserve the existing style and keep imports grouped as standard library, third-party, then local modules.

## Testing Guidelines

No automated tests or coverage requirement currently exist. Add tests under `tests/` using names such as `test_client.py` and methods beginning with `test_`. Prefer mocked HTTP responses; tests must not require live Spotify credentials. Run future tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Commit & Pull Request Guidelines

Git history is small and uses brief descriptive messages. Use concise, imperative subjects such as `Add playlist pagination`. Pull requests should explain behavior changes, list verification commands, link relevant issues, and include terminal output when CLI presentation changes.

## Security & Configuration

Never commit `.env`, `.spotify_token.json`, OAuth codes, access tokens, or `.venv/`. Register `http://127.0.0.1:8888/callback` in the Spotify developer dashboard and keep the Client ID in `.env`.
