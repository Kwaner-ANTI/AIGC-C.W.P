#!/usr/bin/env bash
# Vast.ai ComfyUI image-template provisioning; reuse existing AIW restore profiles.
set -Eeuo pipefail

REPO='https://github.com/Kwaner-ANTI/AIGC-C.W.P.git'
ROOT='/workspace/AIGC-C.W.P'
export AIW_COMFY_DIR="${AIW_COMFY_DIR:-/workspace/ComfyUI}"
export AIW_PYTHON="${AIW_PYTHON:-/venv/main/bin/python}"
export AIW_ASSETS_ROOT="${AIW_ASSETS_ROOT:-/workspace/aiworkbench-assets}"
export HF_XET_HIGH_PERFORMANCE="${HF_XET_HIGH_PERFORMANCE:-1}"

if [[ ! -f "$ROOT/bootstrap.sh" ]]; then
  git clone --depth 1 "$REPO" "$ROOT"
else
  git -C "$ROOT" pull --ff-only
fi

# The template should already provide ComfyUI and its Python environment.
[[ -d "$AIW_COMFY_DIR/models" ]] || { echo "Missing ComfyUI models: $AIW_COMFY_DIR" >&2; exit 1; }
[[ -x "$AIW_PYTHON" ]] || { echo "Missing template Python: $AIW_PYTHON" >&2; exit 1; }

# Restore the small ComfyUI extension from the same public GitHub repository.
SEED_SRC="$ROOT/comfyui_seed_finder"
SEED_DST="$AIW_COMFY_DIR/custom_nodes/comfyui_seed_finder"
if [[ -f "$SEED_SRC/__init__.py" ]]; then
  mkdir -p "$AIW_COMFY_DIR/custom_nodes"
  if [[ ! -e "$SEED_DST" && ! -L "$SEED_DST" ]]; then
    ln -s "$SEED_SRC" "$SEED_DST"
    echo "[seed-finder] linked"
  else
    echo "[seed-finder] existing directory/link preserved"
  fi
fi

# Optional public, explicitly approved UI JSONs from workflows/vast/.
# Never publish private prompt, reference filenames, or private assets here.
WORKFLOW_SRC="$ROOT/workflows/vast"
WORKFLOW_DST="$AIW_COMFY_DIR/user/default/workflows"
if [[ -d "$WORKFLOW_SRC" ]]; then
  mkdir -p "$WORKFLOW_DST"
  for file in "$WORKFLOW_SRC"/*.json; do
    [[ -f "$file" ]] || continue
    if [[ ! -e "$WORKFLOW_DST/$(basename "$file")" ]]; then
      cp "$file" "$WORKFLOW_DST/"
      echo "[workflow] added $(basename "$file")"
    else
      echo "[workflow] existing workflow preserved: $(basename "$file")"
    fi
  done
fi

# Models/nodes: delegate to the existing bootstrap/manifest mechanism.
# Choose 'images-anima', 'images-anima-ref', or both via AIW_PROFILES.
read -r -a PROFILES <<< "${AIW_PROFILES:-images-anima images-anima-ref}"
for profile in "${PROFILES[@]}"; do
  case "$profile" in
    images-anima|images-anima-ref) ;;
    *) echo "Unsupported image profile: $profile" >&2; exit 2 ;;
  esac
  echo "[profile] $profile"
  bash "$ROOT/bootstrap.sh" "$profile"
done

echo '[done] Assets prepared. Reuse existing Supervisor/ComfyUI service; if new custom nodes were installed after startup, reload that one service when idle.'
