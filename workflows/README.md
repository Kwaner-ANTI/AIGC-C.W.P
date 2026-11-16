# Workflow source placement

The user's working ANIMA Aesthetic v1.1 UI workflow `C.A-VT1.json` is retained unchanged in `workflows/local/` on the user's computer. This directory is Git-ignored: the workflow and all positive/negative prompts are private by the user's explicit choice and are not included in public clones.

After `bash bootstrap.sh images-anima`, open the template's existing ComfyUI service and drag the original local JSON into the canvas. Retain its models, prompts, Steps/CFG control connections, Turbo switch, LoRA branch, and all original links. The script restores the four model dependencies; it does not upload or import a workflow. Back up the local JSON separately before moving computers or destroying an instance.

The original Vast.ai RTX 4090 instance generated an ANIMA image successfully according to the user. A fresh instance restored from this repository has not yet passed GPU inference. The user's original Vast PRO6000 full Ref2VA double-INT8 H3 workflow generated an MP4; the Power LoRA/8-step revision published below is a subsequent offline edit, NOT independently GPU validated. The ANIMA user's request to keep that workflow local remains unchanged; the H3 fictional prompt may be public per the user's later explicit instruction.


## Krea-2: user-customized public UI workflows (2026-11-16)

The user supplied and explicitly selected two ComfyUI UI JSONs to **replace the contents in place**, preserving their published filenames for the existing Vast provisioning and Workflows list:

- `workflows/vast/KREA2_T2I_INT8.json` ← `K2T_T2I_original3.json`: 23 nodes / 27 links; uses `krea2_turbo_int8_convrot`, `qwen3vl_4b_fp8_scaled`, Qwen Image VAE, `TextGenerate` prompt refinement, switchable model-only LoRA, `SaveImageAdvanced`. As saved, Shiiro Niji A LoRA `0-11xx-A-krea-2-base-epoch-10.safetensors` is selected with strength 0.8, the LoRA Boolean is **ON**, and the sampler is 15 steps / CFG 1 / Euler + simple. These are the **user's actual controls**, not claims of official or universally optimal settings. Restore the user's private LoRA TAR before running this saved ON configuration, or switch LoRA OFF.
- `workflows/vast/KREA2_I2I_CUSTOM.json` ← `K2-I2I-original.json`: 12 nodes / 12 links; 1056×1408 ImageScale, 8 steps / CFG 1 / Euler + simple / denoise 0.65, Qwen Image VAE. Saved `LoadImage` references **`GALEEE-12.png`** and a user-written creative prompt. The source PNG is **not** embedded or uploaded here; choose/upload the image again on a fresh GPU instance. This graph currently has no creative LoRA loader.

`workflows/vast/KREA2_STYLE_REFERENCE_OFFICIAL.json` is intentionally unchanged; it retains its dedicated style-reference LoRA and subgraph.

The repository is **public**: these two replacement JSONs include the user's saved prompts, output filename prefixes, and model settings by the user's explicit request. The images themselves and Civitai personal LoRA weights are not in Git. New Vast instances get the updated JSON names automatically from `scripts/vast_anima_provision.sh`; existing ComfyUI user-workflow files with the same names are deliberately preserved by that provisioning script and require manual import of the new JSON if a refresh is wanted. A successful GitHub update does not constitute a new GPU generation test.

## MiniMax H3: public 0.9 MP UI workflow (2026-11-15)

- `workflows/vast/h3_ref2va_double_int8_0.9_power_lora.json`: user's actual fictional prompt, reference image filenames, and H3 Ref2VA node layout are retained. No invented privacy/redaction requirement. The image files themselves are not embedded.
- Default switches OFF: full non-pruned `minimax_h3_ref2va_int8_convrot.safetensors` + INT8 Qwen3-VL, 20 steps, `res_multistep` / `beta`, 0.9 MP 16:9 (1280×736).
- A single rgthree **Power Lora Loader** handles separate creative and LightX2V LoRA rows. All rows default OFF. To try the LightX2V Ref2VA v1.1 8-step row, select ON on that row **and** ON on the Acceleration Boolean. The latter switches Euler/simple/8 and sigma shift 12/3. Both must be selected; the acceleration configuration is unverified on the user's GPU.
- Restore from the **existing** `bootstrap.sh`: `h3-int8-int8`, `h3-audio`, and optional `h3-lightx2v-ref2va8` (adds rgthree and the targeted LoRA). `scripts/vast_h3_lightx2v_provision.sh` wraps these for an optional Vast Template `PROVISIONING_SCRIPT`, using the public GitHub HTTPS source and no GitHub authentication. It does not run a second ComfyUI instance.
- Seed: `rgthree Seed` for quick random/fixed/last-queued use; repository's existing `comfyui_seed_finder` for filename to executed `/history` lookup. The graph retains native `RandomNoise` until rgthree Seed UI can be wired on a real ComfyUI session.
- Model weights (H3 and LoRA) and actual reference media are **not** stored in Git. These are downloaded or uploaded on each ephemeral instance. Keep secrets, tokens, SSH credentials and account/private user data out of public repository commits.

### Subsequent Vast rentals

With the appropriate Vast ComfyUI template (`/workspace/ComfyUI`, `/venv/main/bin/python`, verified for that rental), set Vast `PROVISIONING_SCRIPT` to:

`https://raw.githubusercontent.com/Kwaner-ANTI/AIGC-C.W.P/main/scripts/vast_h3_lightx2v_provision.sh`

After the template's bootstrap and node discovery, open the template-managed ComfyUI and load the UI JSON from `workflows/vast/`. Re-upload references from durable storage. The auto-provisioning path is published but has **not** yet been validated on a newly rented GPU; do not count it as a success until a real MP4 is generated.


Official UI templates to import and adapt (not replacements for your customized workflows):

- H3 Ref2VA https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json
- ANIMA https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_anima_base_v1.json
- MOSS SFT https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_moss_image_t2i.json
- MOSS multi-reference https://github.com/Chenkin-x/ComfyUI-Moss-Image-Edit/blob/main/workflows/moss_edit_multi_reference.json

Custom reference assets (pictures/videos) are NOT embedded in these manifests and must be imported separately from user-managed storage. UI JSON != API JSON.
