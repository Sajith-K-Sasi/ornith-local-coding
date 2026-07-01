#!/usr/bin/env bash
# Reproduce the Ornith benchmarks: speed (llama-bench) + quality (harness).
#
# NOTE: speed loads the model itself; quality talks to a *running* server.
# On limited RAM, run them separately — don't llama-bench while the server
# already holds the model in memory.
#
# Usage: ./run_bench.sh <path-to-gguf> [label] [base_url]
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${1:?usage: run_bench.sh <path-to-gguf> [label] [base_url]}"
LABEL="${2:-model}"
BASE="${3:-http://127.0.0.1:8080/v1}"
OUT="${DIR}/results"; mkdir -p "$OUT"

echo "== SPEED (llama-bench) =="
llama-bench -m "$MODEL" -ngl 99 -fa 1 -p 512,2048 -n 128 | tee "$OUT/${LABEL}_speed.txt"

echo
echo "== QUALITY (harness) — requires the model served at $BASE =="
python3 "$DIR/harness.py" --base-url "$BASE" --model ornith --label "$LABEL" --out "$OUT/${LABEL}_quality.json"
