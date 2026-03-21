#!/usr/bin/env bash
# Guardrail: validates PyO3 pyclass quality patterns
# Checks: from_py_object on Clone types, docstrings before pyclass
set -euo pipefail

# Extract file path from stdin JSON
FILE=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)

# Only check .rs files in src/
if [[ -z "$FILE" ]] || [[ "$FILE" != *.rs ]] || [[ "$FILE" != */src/* ]]; then
    exit 0
fi

# Skip if file doesn't exist (deleted)
[[ -f "$FILE" ]] || exit 0

VIOLATIONS=""

# Check 1: pyclass with Clone must have from_py_object
while IFS= read -r line; do
    lineno=$(echo "$line" | cut -d: -f1)
    has_from_py=$(echo "$line" | grep -c 'from_py_object' || true)
    # Scan up to 3 lines after #[pyclass for #[derive(Clone)]
    has_clone=0
    for offset in 1 2 3; do
        checkline=$((lineno + offset))
        if sed -n "${checkline}p" "$FILE" | grep -q 'derive.*Clone'; then
            has_clone=1
            break
        fi
        # Stop scanning if we hit a non-attribute line
        if ! sed -n "${checkline}p" "$FILE" | grep -q '^\s*#\['; then
            break
        fi
    done
    if [ "$has_clone" -gt 0 ] && [ "$has_from_py" -eq 0 ]; then
        VIOLATIONS="${VIOLATIONS}Line ${lineno}: #[pyclass] with Clone but missing from_py_object\n"
    fi
done < <(grep -n '#\[pyclass' "$FILE" || true)

# Check 2: pyclass must have /// docstring above
while IFS= read -r line; do
    lineno=$(echo "$line" | cut -d: -f1)
    prevline=$((lineno - 1))
    if [ "$prevline" -lt 1 ]; then
        VIOLATIONS="${VIOLATIONS}Line ${lineno}: #[pyclass] missing /// docstring (at top of file)\n"
        continue
    fi
    prev_content=$(sed -n "${prevline}p" "$FILE" | sed 's/^[[:space:]]*//')
    # Accept /// docstring or // section comment as valid predecessors
    if [[ ! "$prev_content" == ///* ]] && [[ ! "$prev_content" == //* ]]; then
        VIOLATIONS="${VIOLATIONS}Line ${lineno}: #[pyclass] missing /// docstring (found: '${prev_content}')\n"
    fi
done < <(grep -n '#\[pyclass' "$FILE" || true)

if [ -n "$VIOLATIONS" ]; then
    echo -e "{\"decision\": \"block\", \"reason\": \"GUARDRAIL VIOLATION in ${FILE}:\n${VIOLATIONS}\"}"
    exit 0
fi
