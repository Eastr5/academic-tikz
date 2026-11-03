#!/usr/bin/env bash
# academic-tikz: local dependency install
# Installs into the same interpreter that runs the skill scripts (no venv),
# matching scripts/check-env.py so the packages are actually importable.

set -e

echo "=== academic-tikz setup ==="

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python

if ! "$PYTHON" -m pip install -q pymupdf pdfplumber Pillow numpy; then
    echo "ERROR: pip install failed." >&2
    echo "  PEP 668 systems (Ubuntu 24.04+/Debian 12/Homebrew): use a venv and run scripts with it:" >&2
    echo "    python3 -m venv .venv && .venv/bin/pip install pymupdf pdfplumber Pillow numpy" >&2
    echo "    (or pass --break-system-packages if you accept modifying the system environment)" >&2
    exit 1
fi
"$PYTHON" -c 'import sys; print("Dependencies installed into", sys.executable)'
echo "Optional, only for references/figure-diff.py: pip install opencv-python scikit-image"

echo ""
echo "Only LaTeX needs manual install:"
echo "  macOS: brew install --cask mactex-no-gui"
echo "  Linux: sudo apt install texlive-latex-recommended"
echo "  Windows: winget install MiKTeX.MiKTeX"
