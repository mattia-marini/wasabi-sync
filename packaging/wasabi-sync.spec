# PyInstaller spec for the wasabi-sync executable.
#
# Build on the target OS (PyInstaller does not cross-compile):
#   uv run pyinstaller packaging/wasabi-sync.spec --noconfirm
#
# The result is a single-console-binary in dist/ that runs the TUI with
# no Python installation required.

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("textual.widgets")

a = Analysis(
    ["entry_point.py"],
    pathex=["../src"],
    hiddenimports=hiddenimports,
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="wasabi-sync",
    console=True,
)
