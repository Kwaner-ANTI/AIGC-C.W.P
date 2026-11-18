#!/usr/bin/env bash
# Vast H3 Ref2VA RTX5090: Pruned INT8 DiT + NVFP4-AWQ text + LightX2V v1.1 8-step.
# Reuse the template-managed ComfyUI service; do not start another one.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
export AIW_COMFY_DIR="${AIW_COMFY_DIR:-$WORKSPACE/ComfyUI}"
export AIW_PYTHON="${AIW_PYTHON:-/venv/main/bin/python}"
export AIW_ASSETS_ROOT="${AIW_ASSETS_ROOT:-$WORKSPACE/aiworkbench-assets}"
export HF_XET_HIGH_PERFORMANCE=1

REPO_DIR="$WORKSPACE/AIGC-C.W.P"
if [[ -d "$REPO_DIR/.git" ]]; then
  git -C "$REPO_DIR" pull --ff-only
else
  git clone --depth 1 https://github.com/Kwaner-ANTI/AIGC-C.W.P.git "$REPO_DIR"
fi
cd "$REPO_DIR"

bash bootstrap.sh h3-ref2va-pruned-int8-nvfp4
bash bootstrap.sh h3-audio
bash bootstrap.sh h3-lightx2v-ref2va8

# Keep the existing Seed Finder; no separate service.
if [[ ! -e "$AIW_COMFY_DIR/custom_nodes/aiw_seed_finder" ]]; then
  cp -a "$REPO_DIR/comfyui_seed_finder" "$AIW_COMFY_DIR/custom_nodes/aiw_seed_finder"
fi

WORKFLOW="h3_ref2va_pruned_int8_nvfp4_lightx2v8.json"
WORKFLOW_SRC="$REPO_DIR/workflows/vast/$WORKFLOW"
WORKFLOW_DIR="$AIW_COMFY_DIR/user/default/workflows"
if [[ -d "$AIW_COMFY_DIR/user/default" ]]; then
  mkdir -p "$WORKFLOW_DIR"
  if [[ ! -e "$WORKFLOW_DIR/$WORKFLOW" ]]; then
    cp "$WORKFLOW_SRC" "$WORKFLOW_DIR/$WORKFLOW"
    echo "[workflow] copied: $WORKFLOW_DIR/$WORKFLOW"
  else
    echo "[workflow] existing user copy preserved: $WORKFLOW_DIR/$WORKFLOW"
  fi
else
  echo "[workflow] import manually from: $WORKFLOW_SRC"
fi

echo "[provision] Pruned Ref2VA INT8 + Qwen3-VL NVFP4-AWQ + LightX2V Ref2VA v1.1 restored."
echo "[provision] Use the template-managed ComfyUI, replace reference images and Prompt, and Queue a short MP4."
echo "[provision] LightX2V row ON + acceleration ON; inspect Pruned LoRA mismatch warnings during the real run."
echo "[provision] Fresh custom nodes may require restart of the EXISTING service when idle; no GPU PASS is claimed."
