# Wasabi sync
This is a project to handle multiple REAPER projects.

you can find reaper api documentation in ./REAPER API docs.html. You should just use lua api; no reascript no python.

you should use uv as a package manager and runner (e.g. uv run, uv add and so on)

be sure to structure the python project in a modular fashion, respect PEPs and standard project structure. Pay close attention to structure modules well. When in doubt break down a module to avoid monolitic structure

## Usage

```bash
uv run wasabi-sync
```

A terminal UI with two tabs:

- **Export projects** — scans the configured *projects* directory; each
  project folder unfolds into its audio entries (expects 5). Tick a
  project to select all its entries, or tick entries individually.
- **Generate LIVE** — scans the configured *exports* directory, runs a
  validation check per project, and shows the result next to each row.

### Keys

| Key | Action |
| --- | --- |
| `F1` / `F2` | switch tab |
| `ctrl+s` | open settings (source directories + REAPER executable) |
| `ctrl+q` | quit |
| `enter` | expand/collapse a project |
| `space` | check/uncheck the row under the cursor |
| `a` | check all / clear all |
| click a row | toggle its checkbox (checking a project unfolds + ticks its entries) |

Settings are stored in JSON in the platform config directory
(`~/.config/wasabi-sync/settings.json` on Linux, `%APPDATA%` on Windows,
`~/Library/Application Support` on macOS).

The UI uses a flat theme that adopts your terminal's palette (native ANSI
colors). Set `TEXTUAL_THEME=ansi-light` if you use a light terminal, or
`TEXTUAL_THEME=textual-dark` for Textual's bundled dark palette.

## Packaging

- **zipapp** (needs Python 3.14 on the target machine):

  ```bash
  bash scripts/build_pyz   # -> dist/wasabi-sync.pyz
  python3 dist/wasabi-sync.pyz          # Linux/macOS
  py dist/wasabi-sync.pyz               # Windows
  ```

- **standalone executable** (no Python needed; build on each target OS,
  PyInstaller cannot cross-compile):

  ```bash
  uv run pyinstaller packaging/wasabi-sync.spec --noconfirm
  # -> dist/wasabi-sync (Linux/macOS) or dist/wasabi-sync.exe (Windows)
  ```

## Development

```bash
uv run pytest        # tests (headless Textual pilot + unit tests)
uv run ruff check .  # lint
uv run ruff format . # format
```

