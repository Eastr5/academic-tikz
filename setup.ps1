# academic-tikz: local dependency install (Windows)
# Installs into the same interpreter that runs the skill scripts (no venv),
# matching scripts/check-env.py so the packages are actually importable.

$ErrorActionPreference = "Stop"

Write-Host "=== academic-tikz setup ==="

& python -m pip install -q pymupdf pdfplumber Pillow numpy
& python -c "import sys; print('Dependencies installed into', sys.executable)"
Write-Host "Optional, only for references/figure-diff.py: pip install opencv-python scikit-image"

Write-Host ""
Write-Host "Only LaTeX needs manual install:"
Write-Host "  winget install MiKTeX.MiKTeX"
Write-Host "  or https://miktex.org/download"
