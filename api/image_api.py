# api/image_api.py

import io
import torch
import streamlit as st
from PIL import Image
from models.model_loader import get_pipeline


# Image generation settings
IMAGE_HEIGHT = 1024
IMAGE_WIDTH = 1024
INFERENCE_STEPS = 9       # Results in 8 actual DiT forwards
GUIDANCE_SCALE = 0.0      # Must remain 0.0 for Turbo

NEGATIVE_PROMPT = (
    "ugly, deformed, disfigured, poor quality, low quality, "
    "blurry, watermark, signature, text, "
    "realistic photo, photorealistic, nsfw, violence, "
    "extra limbs, bad anatomy, "
    "repetitive background, same location"
)


# Convert PIL image to bytes for storage/download
def _pil_to_bytes(pil_image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


# Convert bytes back into a PIL image
def _bytes_to_pil(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


# Generate the first image and create a locked seed
def generate_first_image(prompt: str) -> tuple[bytes, int]:
    """
    Page 1:
    Generates the initial image and seed.
    No reference image is used because Z-Image-Turbo
    does not support IP-Adapter.
    """
    pipe = get_pipeline()

    seed = torch.randint(0, 2**32, (1,)).item()
    generator = torch.Generator("cuda").manual_seed(seed)

    try:
        result = pipe(
            prompt=prompt,
            height=IMAGE_HEIGHT,
            width=IMAGE_WIDTH,
            num_inference_steps=INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            generator=generator,
        )

        return _pil_to_bytes(result.images[0]), seed

    except RuntimeError as e:
        if "out of memory" in str(e):
            st.error("GPU out of memory. Check nvidia-smi.")
        else:
            st.error(f"Generation failed: {str(e)}")

        return None, None


# Generate later pages while maintaining character consistency
def generate_with_consistency(
    prompt: str,
    reference_image_bytes: bytes,  # Unused: Z-Image has no IP-Adapter
    locked_seed: int,
    character_name: str,
    page_index: int,
) -> tuple[bytes, int]:
    """
    Pages 2+:

    Consistency is achieved through:
    - Repeating character details in prompts
    - Deterministic seed progression

    Seed pattern:
    Page 1 -> locked_seed
    Page 2 -> locked_seed + 1000
    Page 3 -> locked_seed + 2000
    """

    pipe = get_pipeline()

    consistency_prefix = (
        f"{character_name} — same appearance as always. "
        f"New scene, completely different background. "
    )

    full_prompt = consistency_prefix + prompt

    page_seed = locked_seed + (page_index * 1000)
    generator = torch.Generator("cuda").manual_seed(page_seed)

    try:
        result = pipe(
            prompt=full_prompt,
            height=IMAGE_HEIGHT,
            width=IMAGE_WIDTH,
            num_inference_steps=INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            generator=generator,
        )

        return _pil_to_bytes(result.images[0]), page_seed

    except RuntimeError as e:
        if "out of memory" in str(e):
            st.error("GPU out of memory.")
        else:
            st.error(f"Generation failed: {str(e)}")

        return None, None