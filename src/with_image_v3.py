import mimetypes
import os
import time
import base64
import requests
import fal_client

# =========================
# DEFAULT MODEL
# =========================
DEFAULT_MODEL_NAME = "fal-ai/flux-2/klein/9b/base/edit/lora"

# =========================
# ASPECT RATIO MAPPING
# =========================
ASPECT_RATIO_MAP = {
    "1:1": {"width": 1024, "height": 1024},
    "4:3": {"width": 1024, "height": 768},
    "3:4": {"width": 768, "height": 1024},
    "16:9": {"width": 1280, "height": 720},
    "9:16": {"width": 720, "height": 1280},
}

GPT_IMAGE_2_EDIT_SIZE_MAP = {
    "1:1": "square_hd",
    "4:3": "landscape_4_3",
    "3:4": "portrait_4_3",
    "16:9": "landscape_16_9",
    "9:16": "portrait_16_9",
}

# =========================
# MAIN API LOGIC
# =========================
def remix_images(
    image_paths,
    prompt=None,
    MODEL_NAME=DEFAULT_MODEL_NAME,
    output_dir="output",
    api_key=None,
    aspect_ratio=None,
    quality="low",
):
    """
    Remix images using fal.ai's image editing models.
    """
    effective_api_key = api_key or os.environ.get("FAL_KEY")
    if not effective_api_key:
        raise ValueError("fal.ai API key not provided. Set FAL_KEY or pass api_key=...")

    client = fal_client.SyncClient(key=effective_api_key)

    os.makedirs(output_dir, exist_ok=True)

    if prompt is None:
        prompt = (
            "Turn this image into a professional quality studio shoot "
            "with better lighting and depth of field."
        )

    # Prepare image URLs (base64 data URIs)
    image_urls = []
    for path in image_paths:
        with open(path, "rb") as f:
            data = f.read()
        mime_type = _get_mime_type(path)
        b64 = base64.b64encode(data).decode("utf-8")
        image_urls.append(f"data:{mime_type};base64,{b64}")

    # Prepare arguments
    arguments = {
        "prompt": prompt,
        "image_urls": image_urls,
        "quality": quality,
    }

    image_size = _get_image_size(MODEL_NAME, aspect_ratio)
    if image_size:
        arguments["image_size"] = image_size

    try:
        print(f"Submitting request to {MODEL_NAME}...")
        handler = client.submit(
            MODEL_NAME,
            arguments=arguments,
        )

        result = handler.get()
        _process_fal_response(result, output_dir)

    except Exception as e:
        print(f"fal.ai request failed: {e}")
        raise

# =========================
# HELPERS
# =========================
def _process_fal_response(result, output_dir):
    if not result or "images" not in result or not result["images"]:
        print("No images returned from fal.ai.")
        return

    for i, img_info in enumerate(result["images"]):
        image_url = img_info["url"]
        
        # Determine extension from content_type if available, else .png
        content_type = img_info.get("content_type", "image/png")
        ext = mimetypes.guess_extension(content_type) or ".png"
        
        filename = os.path.join(
            output_dir,
            f"remixed_{int(time.time())}_{i}{ext}"
        )

        print(f"Downloading generated image to {filename}...")
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(filename, "wb") as f:
            f.write(response.content)

def _get_image_size(model_name, aspect_ratio):
    if not aspect_ratio:
        return None
    if aspect_ratio == "auto":
        return "auto"
    if model_name == "openai/gpt-image-2/edit":
        return GPT_IMAGE_2_EDIT_SIZE_MAP.get(aspect_ratio)
    return ASPECT_RATIO_MAP.get(aspect_ratio)

def _get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        # Fallback for common types if guess_type fails
        ext = os.path.splitext(path)[1].lower()
        if ext in [".jpg", ".jpeg"]: return "image/jpeg"
        if ext == ".png": return "image/png"
        if ext == ".webp": return "image/webp"
        raise ValueError(f"Cannot determine MIME type for {path}")
    return mime
