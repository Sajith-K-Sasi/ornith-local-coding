#!/usr/bin/env bash
# One-command launch: check dependencies, then serve Ornith locally.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v llama-server >/dev/null 2>&1; then
  echo "llama.cpp not found. Install it first:  brew install llama.cpp" >&2
  exit 1
fi

QUANT="${ORNITH_QUANT:-Q4_K_M}"
echo "Ornith local coding — quant=${QUANT}"
echo "First run downloads the weights from Hugging Face (~5 GB for Q4_K_M)."
echo "Endpoint: http://127.0.0.1:${ORNITH_PORT:-8080}/v1"
echo "Apple Silicon tip (bigger models): sudo sysctl iogpu.wired_limit_mb=21000"
echo

exec "${DIR}/start_ornith.sh"
