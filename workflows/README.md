# Workflow source placement

The user's working ANIMA Aesthetic v1.1 UI workflow `C.A-VT1.json` is retained unchanged in `workflows/local/` on the user's computer. This directory is Git-ignored: the workflow and all positive/negative prompts are private by the user's explicit choice and are not included in public clones.

After `bash bootstrap.sh images-anima`, open the template's existing ComfyUI service and drag the original local JSON into the canvas. Retain its models, prompts, Steps/CFG control connections, Turbo switch, LoRA branch, and all original links. The script restores the four model dependencies; it does not upload or import a workflow. Back up the local JSON separately before moving computers or destroying an instance.

The original Vast.ai RTX 4090 instance generated an image successfully according to the user. A fresh instance restored from this repository has not yet passed GPU inference. H3 and MOSS user-customized workflow JSON files have not been supplied here.

Official UI templates to import and adapt (not replacements for your customized workflows):

- H3 Ref2VA https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json
- ANIMA https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_anima_base_v1.json
- MOSS SFT https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_moss_image_t2i.json
- MOSS multi-reference https://github.com/Chenkin-x/ComfyUI-Moss-Image-Edit/blob/main/workflows/moss_edit_multi_reference.json

Custom reference assets (pictures/videos) are NOT embedded in these manifests and must be imported separately from user-managed storage. UI JSON != API JSON.
