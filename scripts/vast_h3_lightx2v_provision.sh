#!/usr/bin/env bash
# Vast.ai existing ComfyUI image startup restoration; does not start another ComfyUI.
# Requires this script to be published in the public GitHub repo before using its Raw URL.
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
# Original H3, both INT8, with native audio. Models reused when present.
bash bootstrap.sh h3-int8-int8
bash bootstrap.sh h3-audio
# Additional LightX2V 8-step LoRA + rgthree Power LoRA/Seed nodes.
bash bootstrap.sh h3-lightx2v-ref2va8
# The repository already provides ComfyUI's Seed Finder. No independent backend.
if [[ ! -e "$AIW_COMFY_DIR/custom_nodes/aiw_seed_finder" ]]; then
  cp -a "$REPO_DIR/comfyui_seed_finder" "$AIW_COMFY_DIR/custom_nodes/aiw_seed_finder"
fi
echo "[provision] H3 base, optional LightX2V weight and nodes restored. Use template-managed ComfyUI and load workflows/vast/h3_ref2va_double_int8_0.9_power_lora.json."
echo "[provision] Fresh instance / new extensions need the EXISTING ComfyUI service to restart when idle; no second server was launched."
