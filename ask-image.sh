#!/usr/bin/env bash
# Ask Ornith about an image — local vision, nothing uploaded anywhere.
#
# Requires the server running WITH vision enabled:
#   ORNITH_MMPROJ=/path/to/ornith-mmproj-f16.gguf ./run-ornith.sh
#
# Usage:
#   ./ask-image.sh screenshot.png "What's the bug in this stack trace?"
#   ./ask-image.sh ui.png "What looks visually off here?"
#   ./ask-image.sh diagram.jpg            # defaults to a describe prompt
set -euo pipefail

IMG="${1:?usage: ask-image.sh <image-path> \"your question\"}"
Q="${2:-Describe this image. If it contains code or a UI, explain what it shows.}"
BASE="${ORNITH_BASE:-http://127.0.0.1:8080/v1}"

[ -f "$IMG" ] || { echo "no such image: $IMG" >&2; exit 1; }

case "${IMG##*.}" in
  png|PNG)            MIME=image/png ;;
  jpg|jpeg|JPG|JPEG)  MIME=image/jpeg ;;
  webp|WEBP)          MIME=image/webp ;;
  gif|GIF)            MIME=image/gif ;;
  *)                  MIME=image/png ;;
esac
B64=$(base64 < "$IMG" | tr -d '\n')

python3 - "$BASE" "$Q" "$MIME" "$B64" <<'PY'
import sys, json, urllib.request
base, q, mime, b64 = sys.argv[1:5]
body = json.dumps({
    "model": "ornith",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": q},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ]}],
    "temperature": 0.6, "top_k": 20, "top_p": 0.95, "max_tokens": 2048,
}).encode()
req = urllib.request.Request(base.rstrip("/") + "/chat/completions",
                             data=body, headers={"Content-Type": "application/json"})
try:
    d = json.load(urllib.request.urlopen(req, timeout=600))
except urllib.error.URLError as e:
    sys.exit(f"request failed: {e}\nIs the server running with vision enabled? "
             f"(ORNITH_MMPROJ=... ./run-ornith.sh)")
msg = d["choices"][0]["message"]
reasoning = (msg.get("reasoning_content") or "").strip()
if reasoning:
    print("── reasoning ──\n" + reasoning + "\n")
print("── answer ──\n" + (msg.get("content") or "").strip())
PY
