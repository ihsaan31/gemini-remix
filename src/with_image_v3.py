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
):
    """
    Remix images using fal.ai's image editing models.
    """
    if not api_key:
        api_key = os.getenv("FAL_KEY")
    
    # Set the environment variable for fal_client if provided manually
    if api_key:
        os.environ["FAL_KEY"] = api_key
    elif not os.getenv("FAL_KEY"):
        raise ValueError("fal.ai API key not provided. Set FAL_KEY or pass api_key=...")

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
    }

    # Handle aspect ratio / image size
    if aspect_ratio and aspect_ratio in ASPECT_RATIO_MAP:
        arguments["image_size"] = ASPECT_RATIO_MAP[aspect_ratio]
    elif aspect_ratio:
        # If it's a custom ratio or formatted differently, we could try to parse it
        # but for now we follow the app.py options.
        pass

    try:
        print(f"Submitting request to {MODEL_NAME}...")
        handler = fal_client.submit(
            MODEL_NAME,
            arguments=arguments,
        )
        
        result = handler.get()
        _process_fal_response(result, output_dir, aspect_ratio)

    except Exception as e:
        print(f"fal.ai request failed: {e}")
        raise

# =========================
# HELPERS
# =========================
def _process_fal_response(result, output_dir, aspect_ratio=None):
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

        # ✅ Optional strict aspect ratio enforcement (if Pillow is available)
        if aspect_ratio:
            _enforce_aspect_ratio(filename, aspect_ratio)

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

def _enforce_aspect_ratio(image_path, aspect_ratio):
    """
    Force image to desired aspect ratio via center crop.
    Requires Pillow (pip install pillow)
    """
    try:
        from PIL import Image
    except ImportError:
        return

    try:
        img = Image.open(image_path)
        width, height = img.size

        # Simple parse "W:H"
        try:
            target_w, target_h = map(int, aspect_ratio.split(":"))
        except ValueError:
            return

        target_ratio = target_w / target_h
        current_ratio = width / height

        if abs(current_ratio - target_ratio) < 0.01:
            return  # already close enough

        if current_ratio > target_ratio:
            # too wide → crop width
            new_width = int(height * target_ratio)
            offset = (width - new_width) // 2
            crop_box = (offset, 0, offset + new_width, height)
        else:
            # too tall → crop height
            new_height = int(width / target_ratio)
            offset = (height - new_height) // 2
            crop_box = (0, offset, width, offset + new_height)

        cropped = img.crop(crop_box)
        cropped.save(image_path)
    except Exception as e:
        print(f"Aspect ratio enforcement failed: {e}")
