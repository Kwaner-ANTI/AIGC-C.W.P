#!/usr/bin/env bash
# Restore two selected Civitai model versions to an existing Featurize image runtime.
# Does not modify H3 or start a second ComfyUI service.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export AIW_COMFY_DIR="${AIW_COMFY_DIR:-/home/featurize/ComfyUI-images}"
export AIW_PYTHON="${AIW_PYTHON:-/home/featurize/venvs/comfy-images/bin/python}"
export AIW_LORA_DIR="${AIW_LORA_DIR:-/home/featurize/work/AIWorkbench/models/loras}"
AIW_ASSETS_ROOT="${AIW_ASSETS_ROOT:-/home/featurize/aiworkbench-assets}"
if [[ ! -d "$AIW_COMFY_DIR/models" ]]; then
  echo "[error] not the image ComfyUI models dir: $AIW_COMFY_DIR/models" >&2
  exit 1
fi
echo "[1/3] Add Micro Details v2 Anima (28-block LoRA)"
bash "$ROOT/bootstrap.sh" images-civitai-loras --download anima-micro-v2
echo "[2/3] independent PVC Style Model Anima 2.9B (40-block checkpoint)"
filename="PVCStyleModelMovable_anima29B10.safetensors"
folder="${AIW_PVC_DIR:-$AIW_ASSETS_ROOT/civitai/pvc-anima29b}"
mkdir -p "$folder" "$AIW_COMFY_DIR/models/diffusion_models"
source_file="$folder/$filename"
target="$AIW_COMFY_DIR/models/diffusion_models/$filename"
if [[ -L "$source_file" && ! -f "$source_file" ]]; then
  echo "[error] broken source symlink: $source_file" >&2
  exit 1
fi
if [[ -e "$source_file" ]]; then
  [[ -s "$source_file" ]] || { echo "[error] empty existing checkpoint: $source_file" >&2; exit 1; }
  echo "[reuse] $source_file"
else
  part="$source_file.part"
  echo "[download] Civitai version 3402701 (~5.44 GB)"
  {
    printf 'url = "https://civitai.com/api/download/models/3402701"\n'
    if [[ -n "${CIVITAI_TOKEN:-}" ]]; then
      printf 'header = "Authorization: Bearer %s"\n' "$CIVITAI_TOKEN"
    fi
  } | curl --fail --location --retry 2 --continue-at - --output "$part" --config -
  [[ -s "$part" ]] || { echo "[error] empty PVC download" >&2; exit 1; }
  ln "$part" "$source_file"
  rm -f "$part"
  echo "[downloaded] $source_file"
fi
if [[ -L "$target" ]]; then
  [[ "$(readlink -f "$target")" == "$(readlink -f "$source_file")" ]] || {
    echo "[error] PVC checkpoint link belongs to a different file: $target" >&2; exit 1;
  }
elif [[ -e "$target" ]]; then
  echo "[reuse] $target"
else
  ln -s "$source_file" "$target"
  echo "[linked] $target"
fi
echo "[3/3] copy separate ComfyUI workflows without modifying existing originals"
saved="/home/featurize/work/AIWorkbench/workflows/anima-micro-pvc"
ui="$AIW_COMFY_DIR/user/default/workflows"
mkdir -p "$saved" "$ui"
for name in ANIMA_MICRO_BACKGROUND.json ANIMA_MICRO_CHARACTER.json ANIMA_BASE_REF_MICRO_CHARACTER.json PVC_ANIMA29B_BACKGROUND.json PVC_ANIMA29B_CHARACTER.json; do
  src="$ROOT/workflows/featurize/$name"
  [[ -f "$src" ]] || continue
  cp -n "$src" "$saved/$name"
  if [[ ! -e "$ui/$name" && ! -L "$ui/$name" ]]; then
    ln -s "$saved/$name" "$ui/$name"
  fi
done
echo "[complete] Requested assets installed without restarting or changing ComfyUI runtime."
echo "[workflows] $saved"
echo "[important] Micro Details is a 28-block LoRA. Do NOT place it on the PVC 40-block MODEL chain without proper remapping."
