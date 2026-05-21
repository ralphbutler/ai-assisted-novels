#!/usr/bin/env bash
# Render SVG sources to PNG assets via headless Chrome.
# Re-run any time preview.svg or icon.svg changes.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"      # assets/
ROOT="$(cd "$DIR/.." && pwd)"             # repo root (favicon + apple-touch-icon live here)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

render() {
  local src="$1" out="$2" w="$3" h="$4"
  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --hide-scrollbars \
    --force-device-scale-factor=1 \
    --default-background-color=00000000 \
    --window-size="${w},${h}" \
    --screenshot="${DIR}/${out}" \
    "file://${DIR}/${src}" >/dev/null 2>&1
  echo "  assets/${out}  (${w}x${h})"
}

echo "Rendering:"
render preview.svg preview.png            1200 630
render icon.svg    icon-512.png            512  512

# Downscale the 512x512 master into the root-level icons (kept at root for client conventions).
sips -z 180 180 "${DIR}/icon-512.png" --out "${ROOT}/apple-touch-icon.png" >/dev/null
echo "  apple-touch-icon.png  (180x180)  [root]"
sips -z 64 64   "${DIR}/icon-512.png" --out "${ROOT}/favicon.png"          >/dev/null
echo "  favicon.png  (64x64)  [root]"

echo "Done."
