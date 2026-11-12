"""Fast focused offline tests of model restoration, never download real weights."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('restore', ROOT / 'scripts' / 'restore.py')
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)


class RestoreTests(TestCase):
    def test_first_restore_and_rerun_reuses_downloaded_links(self):
        with TemporaryDirectory() as td:
            base = Path(td)
            comfy = base / 'ComfyUI'
            (comfy / 'models').mkdir(parents=True)
            assets = base / 'assets'
            calls = []

            def fake_download(repo_id, filename, local_dir, **kw):
                calls.append(filename)
                target = Path(local_dir) / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'mock-model-file')
                return str(target)

            with mock.patch.object(restore, 'hf_hub_download', side_effect=fake_download):
                restore.restore_models('images-anima', ROOT, assets, comfy, sys.executable)
                restore.restore_models('images-anima', ROOT, assets, comfy, sys.executable)
            self.assertEqual(len(calls), 3)
            self.assertTrue((comfy / 'models/diffusion_models/anima-aesthetic-v1.1.safetensors').is_symlink())

    def test_existing_model_file_avoids_network_re_download(self):
        with TemporaryDirectory() as td:
            base = Path(td)
            comfy = base / 'ComfyUI'
            model = comfy / 'models/diffusion_models/anima-aesthetic-v1.1.safetensors'
            model.parent.mkdir(parents=True)
            model.write_bytes(b'user-provided-image-model')
            assets = base / 'assets'
            with mock.patch.object(restore, 'hf_hub_download') as download:
                def fake_download(repo_id, filename, local_dir, **kwargs):
                    destination = Path(local_dir) / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(b'mock')
                    return str(destination)
                download.side_effect = fake_download
                restore.restore_models('images-anima', ROOT, assets, comfy, sys.executable)
            self.assertEqual(download.call_count, 2)
            self.assertEqual(model.read_bytes(), b'user-provided-image-model')

    def test_vlm_download_is_full_repository_and_respects_selected_id(self):
        with TemporaryDirectory() as td:
            with mock.patch.dict('os.environ', {'AIW_VLM_REPO': 'Owner/ChosenModel', 'AIW_VLM_REVISION': 'v1'}):
                with mock.patch.object(restore, 'snapshot_download') as download:
                    restore.restore_vlm(Path(td))
                    self.assertEqual(download.call_args.kwargs['repo_id'], 'Owner/ChosenModel')
                    self.assertEqual(download.call_args.kwargs['revision'], 'v1')
                    self.assertNotIn('allow_patterns', download.call_args.kwargs)
