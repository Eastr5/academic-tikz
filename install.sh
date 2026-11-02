#!/usr/bin/env bash
set -euo pipefail

DEST="${HOME}/.claude/skills/academic-tikz"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== academic-tikz installer ==="
echo "Destination: ${DEST}"

mkdir -p "${DEST}"

# Root docs and metadata
cp "${SCRIPT_DIR}"/*.md "${DEST}/"
cp "${SCRIPT_DIR}/LICENSE" "${DEST}/LICENSE"
cp "${SCRIPT_DIR}/INSTALLATION.json" "${DEST}/INSTALLATION.json"

# Every asset directory is required: templates/ is the starting canvas,
# assets/ holds the publication preamble and the Method Draw editor.
for dir in references scripts templates assets agents tests; do
    mkdir -p "${DEST}/${dir}"
    cp -r "${SCRIPT_DIR}/${dir}/"* "${DEST}/${dir}/"
done

echo "Files installed: $(find "${DEST}" -type f | wc -l)"
echo ""

# Run env check if Python available
if command -v python3 &>/dev/null; then
    echo "=== Environment check ==="
    python3 "${DEST}/scripts/check-env.py" || true
elif command -v python &>/dev/null; then
    echo "=== Environment check ==="
    python "${DEST}/scripts/check-env.py" || true
else
    echo "Python not found — skipping environment check"
fi

echo ""
echo "Done. Restart Claude Code to use /academic-tikz"
