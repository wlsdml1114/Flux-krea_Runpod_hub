import shutil
import tempfile
import unittest
from pathlib import Path

from download_models import copy_model_file


class CopyModelFileTest(unittest.TestCase):
    def test_snapshot_symlink_is_copied_as_independent_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cache = root / "hub" / "models--repo"
            blob = cache / "blobs" / "model-sha"
            snapshot_file = (
                cache / "snapshots" / "revision" / "split_files" / "vae" / "ae.safetensors"
            )
            destination = root / "ComfyUI" / "models" / "vae" / "ae.safetensors"
            payload = b"fake VAE model bytes"

            blob.parent.mkdir(parents=True)
            blob.write_bytes(payload)
            snapshot_file.parent.mkdir(parents=True)
            snapshot_file.symlink_to(Path("../../../../blobs/model-sha"))

            copy_model_file(snapshot_file, destination)

            self.assertFalse(destination.is_symlink())
            self.assertEqual(destination.read_bytes(), payload)

            # The copied destination must survive removal of the HF cache tree.
            shutil.rmtree(cache)
            self.assertEqual(destination.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
