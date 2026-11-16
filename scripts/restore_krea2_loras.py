#!/usr/bin/env python3
"""Restore explicitly selected Civitai LoRAs or a private TAR.

This runs in the user's ComfyUI environment, never starts ComfyUI, and never
puts paid weights or API tokens into the public GitHub repository.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path



def load_assets(repo_root):
    """Reuse the existing per-model manifest format across model families."""
    assets = {}
    for manifest in sorted((repo_root / "manifests").glob("*-civitai-loras.json")):
        entries = json.loads(manifest.read_text(encoding="utf-8"))["assets"]
        for name, item in entries.items():
            if name in assets:
                raise ValueError(f"Duplicate LoRA name {name!r} in {manifest}; use a distinct name")
            assets[name] = item
    return assets


def link_saved_loras(assets, folder, comfy_folder):
    """Expose persistent LoRAs to ComfyUI without copying the large files."""
    if folder.resolve() == comfy_folder.resolve():
        return
    comfy_folder.mkdir(parents=True, exist_ok=True)
    for name, item in assets.items():
        source = folder / item["filename"]
        if not source.is_file():
            continue
        target = comfy_folder / item["filename"]
        if target.is_symlink():
            if target.is_file() and target.resolve() == source.resolve():
                continue
            raise FileExistsError(f"Conflicting or broken ComfyUI LoRA link: {target}")
        if target.exists():
            if target.is_file():
                print(f"[reuse] ComfyUI has its own file: {target}", flush=True)
                continue
            raise FileExistsError(f"Conflicting ComfyUI LoRA path: {target}")
        target.symlink_to(source.resolve())
        print(f"[linked] {target} -> {source}", flush=True)


def existing_file(path):
    if path.is_symlink() and not path.is_file():
        raise RuntimeError(f"Broken LoRA link, not replacing: {path}")
    if path.exists():
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Conflicting or empty LoRA path, not replacing: {path}")
        print(f"[reuse] {path}", flush=True)
        return True
    return False


def install_stream(source, dest):
    """Publish a complete file without overwriting an existing file/link."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, prefix=".aiw_lora_", delete=False) as out:
        staged = Path(out.name)
        try:
            shutil.copyfileobj(source, out)
        except BaseException:
            staged.unlink(missing_ok=True)
            raise
    try:
        if staged.stat().st_size == 0:
            raise ValueError(f"Empty archive member for {dest.name}")
        os.link(staged, dest)
    finally:
        staged.unlink(missing_ok=True)
    print(f"[restored] {dest}", flush=True)


def restore_archive(archive, assets, folder):
    archive = Path(archive).expanduser()
    if not archive.is_file():
        raise FileNotFoundError(f"Personal LoRA archive not found: {archive}")
    with tarfile.open(archive, "r:*") as bundle:
        for item in assets.values():
            filename = item["filename"]
            dest = folder / filename
            if existing_file(dest):
                continue
            member = next((m for m in bundle.getmembers() if m.name in (filename, f"./{filename}")), None)
            if member is None:
                print(f"[archive] not included: {filename}", flush=True)
                continue
            if not member.isfile():
                raise ValueError(f"Not a regular file in archive: {member.name}")
            stream = bundle.extractfile(member)
            if stream is None:
                raise ValueError(f"Cannot read archive member: {member.name}")
            with stream:
                install_stream(stream, dest)


def download_selected(names, assets, folder):
    token = os.environ.get("CIVITAI_TOKEN", "")
    failed = []
    for name in names:
        item = assets[name]
        dest = folder / item["filename"]
        if existing_file(dest):
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        partial = Path(f"{dest}.part")
        # Give curl credentials via stdin, not CLI arguments, shell history, or URL.
        config = f'url = "https://civitai.com/api/download/models/{item["version_id"]}"\n'
        if token:
            config += f'header = {json.dumps("Authorization: Bearer " + token)}\n'
        cmd = ["curl", "--fail", "--location", "--http1.1", "--connect-timeout", "30", "--retry", "4", "--retry-all-errors", "--retry-delay", "3", "--continue-at", "-", "--output", str(partial), "--config", "-"]
        print(f"[download] {name} (Civitai version {item['version_id']})", flush=True)
        result = subprocess.run(cmd, input=config, text=True, check=False)
        if result.returncode:
            print(f"[download-error] {name}: curl exit {result.returncode}; 35 = TLS/connection error, 22 = HTTP error (inspect HTTP response and access)", file=sys.stderr)
            failed.append(name)
            continue
        if not partial.is_file() or partial.stat().st_size == 0:
            print(f"[unavailable] {name}: downloaded file is empty", file=sys.stderr)
            failed.append(name)
            continue
        # Link, rather than replace, to preserve any concurrently created LoRA.
        try:
            os.link(partial, dest)
            print(f"[downloaded] {dest}", flush=True)
        except FileExistsError:
            print(f"[reuse] existing destination retained: {dest}", flush=True)
        finally:
            partial.unlink(missing_ok=True)
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("--archive", default=os.environ.get("AIW_LORA_ARCHIVE", ""), help="Local KREA2_personal_loras.tar path")
    parser.add_argument("--download", default=os.environ.get("AIW_CIVITAI_LORAS", ""), help="Explicit comma-separated names, e.g. mrpopo,shiiro")
    parser.add_argument("--list", action="store_true", help="List recorded model versions without downloading")
    args = parser.parse_args()
    assets = load_assets(args.repo_root)
    if args.list:
        for name, item in assets.items():
            print(f"{name}: {item['filename']} (Civitai version {item['version_id']})")
        return 0
    selected = [n.strip() for n in args.download.split(",") if n.strip()]
    unknown = [n for n in selected if n not in assets]
    if unknown:
        parser.error(f"unknown models: {', '.join(unknown)}; available: {', '.join(assets)}")
    if not args.archive and not selected:
        parser.error("provide AIW_LORA_ARCHIVE or explicitly select AIW_CIVITAI_LORAS")
    comfy_folder = Path(os.environ.get("AIW_COMFY_DIR", "/workspace/ComfyUI")).expanduser() / "models" / "loras"
    if not comfy_folder.parent.is_dir():
        raise FileNotFoundError(f"ComfyUI models directory missing: {comfy_folder.parent}; set AIW_COMFY_DIR")
    folder = Path(os.environ.get("AIW_LORA_DIR", str(comfy_folder))).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    if args.archive:
        restore_archive(args.archive, assets, folder)
    failures = download_selected(selected, assets, folder) if selected else []
    link_saved_loras(assets, folder, comfy_folder)
    if failures:
        print(f"[failed] Not restored: {', '.join(failures)}; no success claimed", file=sys.stderr)
        return 1
    print("[complete] Selected Civitai LoRAs restored; choose compatible files in ComfyUI")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
