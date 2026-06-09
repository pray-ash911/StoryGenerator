# models/model_loader.py

import os
import torch
import streamlit as st
from diffusers import AutoPipelineForText2Image, DDIMScheduler
from transformers import CLIPVisionModelWithProjection

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


def get_pipeline():
    """
    Returns the pipeline from st.session_state.
    Loads it once on first call, reuses forever after.
    Storing in session_state guarantees survival across Streamlit reruns.
    Module-level variables can reset on rerun — session_state never does.
    """

    if "sdxl_pipeline" not in st.session_state:
        print("Loading SDXL + IP-Adapter... (first time only)")

        image_encoder = CLIPVisionModelWithProjection.from_pretrained(
            "h94/IP-Adapter",
            subfolder="models/image_encoder",
            torch_dtype=torch.float16,
        )

        pipeline = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            image_encoder=image_encoder,
            variant="fp16",
        )

        pipeline.scheduler = DDIMScheduler.from_config(
            pipeline.scheduler.config
        )

        pipeline.enable_model_cpu_offload()

        pipeline.load_ip_adapter(
            "h94/IP-Adapter",
            subfolder="sdxl_models",
            weight_name=[
                "ip-adapter-plus_sdxl_vit-h.safetensors",
                "ip-adapter-plus-face_sdxl_vit-h.safetensors",
            ]
        )
        pipeline.set_ip_adapter_scale([0.7, 0.3])

        pipeline.enable_vae_slicing()
        pipeline.enable_vae_tiling()

        # Store in session_state — survives all reruns
        st.session_state.sdxl_pipeline = pipeline
        print("SDXL + IP-Adapter ready. Stored in session_state.")

    return st.session_state.sdxl_pipeline