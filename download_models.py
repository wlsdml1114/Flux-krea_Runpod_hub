import os
import shutil

downloads = [
    ("Comfy-Org/z_image_turbo", "split_files/diffusion_models/z_image_turbo_bf16.safetensors", "/ComfyUI/models/unet/z_image_turbo_bf16.safetensors"),
    ("Comfy-Org/z_image_turbo", "split_files/text_encoders/qwen_3_4b.safetensors", "/ComfyUI/models/clip/qwen_3_4b.safetensors"),
    ("Comfy-Org/z_image_turbo", "split_files/vae/ae.safetensors", "/ComfyUI/models/vae/ae.safetensors"),
    ("alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union", "Z-Image-Turbo-Fun-Controlnet-Union.safetensors", "/ComfyUI/models/model_patches/Z-Image-Turbo-Fun-Controlnet-Union.safetensors")
]


def copy_model_file(cached_file, destination):
    """Copy the model bytes out of the Hugging Face snapshot cache."""
    resolved_file = os.path.realpath(cached_file)
    if not os.path.isfile(resolved_file):
        raise FileNotFoundError(f"Cached model file not found: {cached_file}")

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    if os.path.lexists(destination):
        os.remove(destination)

    # hf_hub_download returns a snapshot symlink. Copy its resolved target so
    # the baked image does not retain a link into the temporary HF cache.
    shutil.copy2(resolved_file, destination)
    if os.path.islink(destination) or not os.path.isfile(destination):
        raise RuntimeError(f"Model destination is not a regular file: {destination}")


def download_models():
    from huggingface_hub import hf_hub_download

    print("Starting model downloads...")
    for repo, filename, destination in downloads:
        print(f"Downloading {filename} from {repo}...")
        cached_file = hf_hub_download(repo_id=repo, filename=filename)
        copy_model_file(cached_file, destination)
        print(f"Copied model bytes to {destination}")

    print("All models downloaded successfully!")


if __name__ == "__main__":
    download_models()
