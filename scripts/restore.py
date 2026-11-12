#!/usr/bin/env python3
"""Restore only the selected AI Workbench workload assets.

ComfyUI/vLLM process lifecycle remains owned by the existing Workbench Runtime
(or the provider's already configured service manager). No duplicate launcher.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

from huggingface_hub import hf_hub_download, snapshot_download


def within_relative(text):
    p = Path(text)
    if p.is_absolute() or not p.parts or '..' in p.parts:
        raise ValueError(f'Invalid relative model path: {text!r}')
    return p


def node_install(item, comfy, python):
    name = item['name']
    repo = item['url']
    folder = comfy / 'custom_nodes' / name
    if not folder.exists():
        folder.parent.mkdir(parents=True, exist_ok=True)
        print(f'[nodes] installing {name}', flush=True)
        subprocess.run(['git', 'clone', '--depth', '1', repo, str(folder)], check=True)
        req = folder / 'requirements.txt'
        if req.is_file():
            subprocess.run([python, '-m', 'pip', 'install', '-r', str(req)], check=True)
    else:
        print(f'[nodes] present, preserved: {folder}', flush=True)


def restore_models(profile, repo_root, asset_root, comfy, python):
    manifest_path = repo_root / 'manifests' / f'{profile}.json'
    if not manifest_path.is_file():
        raise ValueError(f'Unknown workload profile: {profile}')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not (comfy / 'models').is_dir():
        raise RuntimeError(f'ComfyUI models folder not found: {comfy}/models; set AIW_COMFY_DIR')
    from huggingface_hub import __version__
    print(f'[restore] {profile}; huggingface_hub={__version__}; comfy={comfy}', flush=True)
    for item in manifest.get('nodes', []):
        node_install(item, comfy, python)
    for item in manifest['models']:
        repo = item['repo']
        revision = item.get('revision')
        source = within_relative(item['source'])
        target = within_relative(item['target'])
        dest = comfy / 'models' / target
        # An image/template may already ship the selected model. Reusing a present
        # regular file avoids wasting GPU time downloading it again. Trust the
        # operator's existing file name here; no new checksum/scanner is added.
        if dest.is_file() and not dest.is_symlink():
            print(f'[reuse] pre-existing model file: {dest}', flush=True)
            continue
        remote_local_dir = asset_root / 'repos' / repo.replace('/', '__')
        downloaded_location = remote_local_dir / source
        if dest.is_symlink():
            if dest.exists() and dest.resolve() == downloaded_location.resolve():
                print(f'[reuse] linked model: {dest}', flush=True)
                continue
            raise FileExistsError(f'Conflicting or broken model link: {dest}; resolve it before retrying')
        if dest.exists():
            raise FileExistsError(f'Conflicting model path: {dest}')
        remote_local_dir.mkdir(parents=True, exist_ok=True)
        print(f'[model] {repo} : {source}', flush=True)
        params = {'repo_id': repo, 'filename': str(source), 'local_dir': str(remote_local_dir)}
        if revision:
            params['revision'] = revision
        downloaded = Path(hf_hub_download(**params)).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(downloaded)
        print(f'[ready] {dest}', flush=True)
    print(f'[complete] {profile}: required downloads linked; start or reuse your existing Runtime', flush=True)


def restore_vlm(asset_root):
    repo = os.environ.get('AIW_VLM_REPO', '').strip()
    if not repo or '/' not in repo:
        raise ValueError('Set AIW_VLM_REPO=OWNER/MODEL for the specific model selected in Workbench Model Registry')
    revision = os.environ.get('AIW_VLM_REVISION', '').strip() or None
    target = asset_root / 'vlm' / repo.replace('/', '__')
    target.mkdir(parents=True, exist_ok=True)
    print(f'[vlm] downloading selected repository {repo} to {target}', flush=True)
    kwargs = {'repo_id': repo, 'local_dir': str(target)}
    if revision:
        kwargs['revision'] = revision
    snapshot_download(**kwargs)
    print(f'[complete] model files: {target}\nConfigure existing Workbench vLLM workload separately; no server was started.', flush=True)


def main():
    profile, root = sys.argv[1], Path(sys.argv[2])
    asset_root = Path(os.environ.get('AIW_ASSETS_ROOT', '/workspace/aiworkbench-assets')).expanduser()
    comfy = Path(os.environ.get('AIW_COMFY_DIR', '/workspace/ComfyUI')).expanduser()
    python = os.environ.get('AIW_PYTHON', sys.executable)
    asset_root.mkdir(parents=True, exist_ok=True)
    if profile == 'vlm':
        restore_vlm(asset_root)
    else:
        restore_models(profile, root, asset_root, comfy, python)


if __name__ == '__main__':
    main()
