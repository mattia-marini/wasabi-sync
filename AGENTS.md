# AGENTS.md

## Project

wasabi-sync — a Textual TUI wrapping REAPER for multi-project synchronisation.
Two tabs: **Export projects** (pick projects + their 5 audio entries and export)
and **Generate LIVE** (validate exported projects and build a live set).

Stack: Python >= 3.14, uv, src layout (PEP 621), Textual 8.2.x, platformdirs.
Runtime deps are pure-Python by design so the app ships as a zipapp.

## Commands

- Run the app: `uv run wasabi-sync`
- Tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Build zipapp: `bash scripts/build_pyz` -> `dist/wasabi-sync.pyz`
  (run with `python3 dist/wasabi-sync.pyz`; Windows: `py wasabi-sync.pyz`)
- Build executable (per-OS, no cross-compile):
  `uv run pyinstaller packaging/wasabi-sync.spec --noconfirm` -> `dist/wasabi-sync`

## Architecture

- `wasabi_sync.models` — pure dataclasses (`Project`, `Entry`, `Selection` helpers); no I/O, no UI.
- `wasabi_sync.settings` — `Settings` dataclass + JSON `SettingsStore` (config dir via platformdirs, atomic writes).
- `wasabi_sync.logging_setup` — rotating file log in the config dir; never logs to the terminal (the TUI owns it).
- `wasabi_sync.core` — pure logic, unit-tested, no textual imports:
  - `audio.py` — audio-extension registry.
  - `discovery.py` — folder scanning: `scan_projects` (LIVE tab: a project = a folder with >= 1 audio file) and `scan_rpp_projects` (Export tab: a project = a folder with a `.rpp`, entries = tracks that send directly to master).
  - `validation.py` — `ValidationRule` protocol + registry (LIVE tab); step-2 rules plug in here.
  - `actions/` — `Action` protocol + `ExportAction` (unmutes master-sending tracks) + stub `LiveAction`.
- `wasabi_sync.reaper` — REAPER interop: `rpp.py` (parse/edit `.rpp` track metadata), `runner.py` (locate the binary), `api.py` (future Lua facade). Lua-only, no ReaScript-Python (see `REAPER API docs.html`).
- `wasabi_sync.ui` — Textual layer:
  - `widgets/checkbox_tree.py` — tri-state (unicode glyph) checkbox tree shared by both tabs.
  - `project_view.py` — shared tab behaviour (toolbar, tree, status, submit worker).
  - `export_view.py` / `live_view.py` — the two tabs.
  - `settings_screen.py` + `browser.py` — settings modal + directory-picker modal.
  - `main_screen.py` — F1/F2 tab switching; `app.py` — ctrl+s opens settings.

## Conventions

- No runtime deps beyond `textual` + `platformdirs` (zipapp must stay pure-Python).
- No `.tcss` files — CSS lives in inline `DEFAULT_CSS` (widgets) / `CSS` (app-level theme) so zipapp/PyInstaller never chase data files.
  App-level overrides go in `App.CSS`, not `App.DEFAULT_CSS`: `DEFAULT_CSS` is treated as widget-level and loses specificity to built-in widget styles (e.g. `Button:ansi.-style-default`).
- Theme is `ansi-dark` by default, so the UI adopts the terminal's own palette; override with the `TEXTUAL_THEME` env var (e.g. `ansi-light`).
- Blocking work runs in `@work` threads; update the UI via `app.call_from_thread` (or `app.notify`, which is thread-safe).
- `push_screen` returns an awaitable and must be awaited. `screen.dismiss(result)` is fire-and-forget by design.
- In tests, `pilot.click`/`app.query_one` only see the default screen; query modal screens via `app.screen`.

## Step-2 hooks (pending spec)

- `core/actions/export_action.py` — currently unmutes master-sending tracks (step 1); the export pipeline extends this.
- `core/actions/live_action.py` — replace stub with the LIVE generation pipeline.
- `core/validation.py` — real validation rules for exported projects.
- `reaper/api.py` — Lua script generation + REAPER invocation (mechanism TBD; `REAPER API docs.html` is the reference).
