#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE="${1:-}"
if [[ -z "$PROFILE" ]]; then
  echo 'Usage: bash bootstrap.sh images-krea2-turbo | images-krea2-personal-loras [--archive PATH] [--download mrpopo,shiiro] | images-anima | images-anima-ref | images-moss | images-moss-edit | images-flux2-dev | h3-int8-int8 | h3-int8-bf16 | h3-audio | h3-controlnet-int8 | h3-controlnet-bf16 | vlm' >&2
  exit 2
fi

PYTHON="${AIW_PYTHON:-python3}"
# Private Civitai/community LoRAs are optional and use only the Python stdlib.
# Do not install huggingface_hub or download paid models for an archive restore.
if [[ "$PROFILE" == "images-krea2-personal-loras" ]]; then
  exec "$PYTHON" "$ROOT/scripts/restore_krea2_loras.py" "$ROOT" "${@:2}"
fi
if ! "$PYTHON" -c 'import huggingface_hub' >/dev/null 2>&1; then
  echo '[bootstrap] huggingface_hub missing; installing in configured Python environment' >&2
  "$PYTHON" -m pip install 'huggingface_hub[hf_xet]'
fi
exec "$PYTHON" "$ROOT/scripts/restore.py" "$PROFILE" "$ROOT"
