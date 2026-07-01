#!/usr/bin/env bash
# Serve Ornith-1.0-9B on llama.cpp as a local OpenAI-compatible coding endpoint.
# Tuned for Apple Silicon / 24 GB unified memory (e.g. a fanless MacBook Air).
#
# Env overrides:
#   ORNITH_QUANT   quant tag (default Q4_K_M — the sweet spot on 24 GB; see bench/)
#   ORNITH_PORT    port (default 8080)
#   ORNITH_CTX     context length (default 131072; 65536 uses less RAM)
#   ORNITH_MMPROJ  path to the vision encoder gguf to enable image understanding
set -euo pipefail

QUANT="${ORNITH_QUANT:-Q4_K_M}"
PORT="${ORNITH_PORT:-8080}"
CTX="${ORNITH_CTX:-131072}"
MMPROJ="${ORNITH_MMPROJ:-}"

args=(
  -hf "deepreinforce-ai/Ornith-1.0-9B-GGUF:${QUANT}"
  -a ornith
  --host 127.0.0.1 --port "${PORT}"
  -np 1
  -c "${CTX}" -n 16384
  --jinja
  --reasoning-format deepseek        # split <think> into reasoning_content
  -ngl 99 -fa on                     # full GPU offload + flash attention
  --temp 0.6 --top-k 20 --top-p 0.95 --min-p 0   # Ornith's recommended sampling
  --no-context-shift
  --mlock
)

# Vision (image understanding) is optional: provide an mmproj encoder to enable it.
if [[ -n "${MMPROJ}" && -f "${MMPROJ}" ]]; then
  args+=(--mmproj "${MMPROJ}")
  echo "vision: ENABLED (${MMPROJ})"
else
  echo "vision: disabled — set ORNITH_MMPROJ=/path/to/ornith-mmproj-f16.gguf to enable"
fi

echo "serving Ornith ${QUANT} at http://127.0.0.1:${PORT}/v1  (ctx ${CTX})"
exec llama-server "${args[@]}"
