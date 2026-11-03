#!/usr/bin/env bash
# compile.sh — build a standalone .tex into a cropped PDF.
# usage: bash compile.sh figure.tex
set -euo pipefail
src="${1:?usage: compile.sh figure.tex}"
dir="$(cd "$(dirname "$src")" && pwd)"
base="$(basename "${src%.tex}")"

# xelatex is the default (CJK/Unicode safe); override with TIKZ_ENGINE=pdflatex|lualatex.
engine="${TIKZ_ENGINE:-xelatex}"
if ! command -v "$engine" >/dev/null 2>&1; then
  echo "WARN: $engine not found on PATH — falling back to pdflatex" >&2
  engine="pdflatex"
fi
cd "$dir"
if command -v latexmk >/dev/null 2>&1; then
  # -halt-on-error so failures surface immediately; latexmk handles reruns.
  latexmk -"$engine" -no-shell-escape -interaction=nonstopmode -halt-on-error "$base.tex" >/dev/null
  latexmk -c "$base.tex" >/dev/null 2>&1 || true   # clean aux, keep the PDF
else
  # no latexmk (e.g. BasicTeX): run twice so references/labels settle.
  "$engine" -no-shell-escape -interaction=nonstopmode -halt-on-error "$base.tex" >/dev/null
  "$engine" -no-shell-escape -interaction=nonstopmode -halt-on-error "$base.tex" >/dev/null
  rm -f "$base.aux" "$base.log" "$base.out" "$base.fls" "$base.fdb_latexmk" 2>/dev/null || true
fi
echo "$dir/$base.pdf"
