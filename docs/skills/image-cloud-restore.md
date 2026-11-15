---
name: image-cloud-restore
description: Reuse Featurize ANIMA/MOSS image environments, eliminate duplicate model downloads, and restore selected ANIMA/MOSS/FLUX.2 profiles on Vast.ai.
---

# Image cloud restore — Featurize to Vast.ai

## Real Featurize RTX 4090 observations (2026-11-15)

User completed basic FLUX.2 Dev workflow testing and provided the actual folder listings, sizes and resolved ANIMA symlink paths. The subsequent deletion, new personal-image creation and Vast FLUX.2 generation have **not** been confirmed.

| Featurize path | Observed size | Content |
|---|---:|---|
| `/home/featurize/image-models` | 29G | Old ANIMA 9.2G (Base v1.0 and Aesthetic v1.1) + MOSS 20G |
| `/home/featurize/aiworkbench-assets` | 59G before cleanup | FLUX.2 53G + duplicate ANIMA 5.3G + Turbo LoRA 143M |
| `/home/featurize/ComfyUI-images` | 368M | Image ComfyUI |
| `/home/featurize/venvs/comfy-images` | 6.3G | Image Python environment |
| `/environment` | 8.2G | Base environment; do not blindly remove |
| Image estimate / quota | 113.9GB / 111GB available | Image accounting cannot be equated directly to `du` |

The user successfully repointed three ComfyUI ANIMA links to these existing old files:

```text
/home/featurize/image-models/anima/split_files/diffusion_models/anima-aesthetic-v1.1.safetensors
/home/featurize/image-models/anima/split_files/text_encoders/qwen_3_06b_base.safetensors
/home/featurize/image-models/anima/split_files/vae/qwen_image_vae.safetensors
```

These `readlink -f` outputs establish only correct link destinations, **not** a newly successful Aesthetic generation or completed deletion. After a real Aesthetic generation, the possible duplicate-removal target is `/home/featurize/aiworkbench-assets/repos/circlestone-labs__Anima` (5.3G), **not** old `image-models/anima`, MOSS, FLUX.2, or the separate `Anima-Official-LoRAs` Turbo LoRA.

The existing `scripts/restore.py` intentionally refuses a symlink that points outside its own expected asset location. Therefore do not rerun `images-anima` without resolving the Featurize pre-existing link layout; do not remove this safety behavior. Never copy absolute Featurize links into a Vast image.

`/home/featurize/work/AIWorkbench/AIGC-C.W.P/manifests/images-flux2-dev.json` existed in Featurize persistent work (837 bytes). Work output contained ~951MB images, including an `anima_ref_adapter/` output folder. This folder **is not** the ANIMA Reference Adapter model weight. Save actual workflows, selected outputs and references to long-lived storage before returning an instance. Cloud personal-image size only becomes confirmed after platform image creation and next-instance recovery.

## Vast.ai workflow

Use the existing public repository `Kwaner-ANTI/AIGC-C.W.P`, **one** `bootstrap.sh` / `scripts/restore.py`, and a suitable image ComfyUI template. Do not provision H3/vLLM into this image environment.

From the **Vast instance Linux terminal** (only when actual template paths agree):

```bash
cd /workspace
if [ -d AIGC-C.W.P/.git ]; then git -C AIGC-C.W.P pull --ff-only; else git clone --depth 1 https://github.com/Kwaner-ANTI/AIGC-C.W.P.git; fi
cd AIGC-C.W.P
export AIW_COMFY_DIR=/workspace/ComfyUI
export AIW_PYTHON=/venv/main/bin/python
export AIW_ASSETS_ROOT=/workspace/aiworkbench-assets
export HF_XET_HIGH_PERFORMANCE=1
bash bootstrap.sh images-flux2-dev
# Only when needed: bash bootstrap.sh images-anima
# Only when needed: bash bootstrap.sh images-anima-ref
# Only when needed: bash bootstrap.sh images-moss-edit
```

The FLUX.2 profile downloads `flux2_dev_fp8mixed.safetensors` (~35.5GB), `mistral_3_small_flux2_fp8.safetensors` (~18GB), and `flux2-vae.safetensors` (~0.34GB) from `Comfy-Org/flux2-dev`. RTX4090 24GB needs CPU offload, adequate host RAM (64GB+ preferred 96GB+) and enough temporary disk. FLUX.2 VAE is distinct from MOSS `flux2-vae_small.safetensors`; ANIMA uses Qwen/VAE.

For automatic startup, edit **Vast website > Templates > Environment Variables** (not a Linux shell command):

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Kwaner-ANTI/AIGC-C.W.P/main/scripts/vast_anima_provision.sh
AIW_PROFILES=images-flux2-dev images-anima
```

The existing script filename remains for compatibility, but it now accepts ANIMA, MOSS and FLUX.2 profiles. Choose only needed profiles; omit ANIMA when only FLUX.2 is needed. A Vast Template is provisioning instructions, **not** a GPU disk snapshot. Reuse one template-managed ComfyUI process/Supervisor, not another launcher, and don't run concurrent startup downloads.

Existing Workbench SSH Host / ComfyUI Runtime is separate from Vast provisioning. Previously observed Vast SSH HTTP422 and Workbench-owned tunnel failure are not yet verified fixed. Actual Vast port and template paths must be checked against the rented instance; historical 18188 ComfyUI / 8080 Jupyter are not universal defaults. Use personal UI workflows/references, run a real FLUX.2 PNG, then associate it with Workbench Project/Shot/Prompt/Review and save before Destroy. Do not claim Vast FLUX.2 PASS before that real run.

## Scope / safety

No new hash/SHA-256 verification, frozen baselines, generic scanners, separate download managers, second ComfyUI launchers, or Workbench History duplicate. Do not remove existing SSH/known-hosts, credentials separation, model conflict safety, context/Raw/History/lineage protections. Keep tokens and SSH private keys out of public repo or template. Follow respective model licenses.
