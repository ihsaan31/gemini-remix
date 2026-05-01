import mimetypes
import os
import time
import random
import base64

from openai import OpenAI, AuthenticationError, PermissionDeniedError

# =========================
# DEFAULT MODEL
# =========================
DEFAULT_MODEL_NAME = "bytedance-seed/seedream-4.5"

class PermanentOpenRouterError(RuntimeError):
    """Non-retryable errors (auth/permission/model-access) that require user action."""

# =========================
# RETRY HELPER
# =========================
def with_retry(fn, max_retries=5, base_delay=1.0, max_delay=30.0):
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as e:
            # Permanent failures: retrying just wastes time and hides the real issue.
            if isinstance(e, (AuthenticationError, PermissionDeniedError, PermanentOpenRouterError)):
                raise
            if attempt == max_retries:
                raise

            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay += random.uniform(0, delay * 0.2)
            time.sleep(delay)

def _format_openrouter_auth_error(model_name: str, *, is_permission_denied: bool) -> str:
    code = "403" if is_permission_denied else "401"
    reason = "permission denied" if is_permission_denied else "authentication failed"
    return (
        f"OpenRouter request failed ({code} {reason}). "
        f"Model: {model_name!r}. "
        "Make sure you provided a valid OpenRouter API key (OPENROUTER_API_KEY), "
        "and that your OpenRouter account has access/credits for this model."
    )

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
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OpenRouter API key not provided. Set OPENROUTER_API_KEY or pass api_key=...")

    os.makedirs(output_dir, exist_ok=True)

    if prompt is None:
        prompt = (
            "Turn this image into a professional quality studio shoot "
            "with better lighting and depth of field."
        )

    # ✅ Inject aspect ratio into prompt (since OpenRouter has no native support for many models)
    if aspect_ratio:
        prompt += f" The final image must have an aspect ratio of {aspect_ratio}."

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = _build_messages(image_paths, prompt)

    # Determine modalities based on model
    # According to user snippets:
    # openai/gpt-5.4-image-2 -> ["image", "text"]
    # google/gemini-3.1-flash-image-preview -> ["image", "text"]
    # bytedance-seed/seedream-4.5 -> ["image"]
    
    modalities = ["image"]
    if "gpt-5.4" in MODEL_NAME or "gemini-3.1-flash" in MODEL_NAME:
        modalities = ["image", "text"]

    def run():
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                extra_body={"modalities": modalities},
            )
        except AuthenticationError:
            raise PermanentOpenRouterError(
                _format_openrouter_auth_error(MODEL_NAME, is_permission_denied=False)
            ) from None
        except PermissionDeniedError:
            raise PermanentOpenRouterError(
                _format_openrouter_auth_error(MODEL_NAME, is_permission_denied=True)
            ) from None

        _process_openrouter_response(response, output_dir, aspect_ratio)

    with_retry(run)

# =========================
# HELPERS
# =========================
def _build_messages(image_paths, prompt):
    content = []

    # Add images as base64 data URLs
    for path in image_paths:
        with open(path, "rb") as f:
            data = f.read()

        mime_type = _get_mime_type(path)
        b64 = base64.b64encode(data).decode("utf-8")

        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{b64}"
            }
        })

    # Add prompt
    content.append({
        "type": "text",
        "text": prompt
    })

    return [{
        "role": "user",
        "content": content
    }]

def _process_openrouter_response(response, output_dir, aspect_ratio=None):
    file_index = 0
    message = response.choices[0].message

    if not hasattr(message, "images") or not message.images:
        print("No images returned.")
        return

    for image in message.images:
        # Some models return dict, some might return objects depending on library version
        if isinstance(image, dict):
            image_url = image["image_url"]["url"]
        else:
            image_url = image.image_url.url

        if not image_url.startswith("data:"):
            # If it's a direct URL instead of base64 (less common for modalities)
            # handle it here if needed, but for now we expect base64 as per snippets
            continue

        header, b64_data = image_url.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]

        ext = mimetypes.guess_extension(mime_type) or ".png"
        filename = os.path.join(
            output_dir,
            f"remixed_{int(time.time())}_{file_index}{ext}"
        )

        _save_binary_file(filename, base64.b64decode(b64_data))

        # ✅ Optional strict aspect ratio enforcement
        if aspect_ratio:
            _enforce_aspect_ratio(filename, aspect_ratio)

        file_index += 1

def _save_binary_file(path, data):
    with open(path, "wb") as f:
        f.write(data)

def _get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
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
        print("Pillow not installed, skipping aspect ratio enforcement.")
        return

    try:
        img = Image.open(image_path)
        width, height = img.size

        target_w, target_h = map(int, aspect_ratio.split(":"))
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
