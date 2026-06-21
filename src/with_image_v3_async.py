import asyncio
import mimetypes
import os
import time
import base64
import requests
import fal_client

DEFAULT_MODEL_NAME = "fal-ai/flux-2/klein/9b/base/edit/lora"

ASPECT_RATIO_MAP = {
    "1:1": {"width": 1024, "height": 1024},
    "4:3": {"width": 1024, "height": 768},
    "3:4": {"width": 768, "height": 1024},
    "16:9": {"width": 1280, "height": 720},
    "9:16": {"width": 720, "height": 1280},
}


async def remix_images_async(
    image_paths,
    prompt=None,
    MODEL_NAME=DEFAULT_MODEL_NAME,
    output_dir="output",
    api_key=None,
    aspect_ratio=None,
    quality="low",
):
    effective_api_key = api_key or os.environ.get("FAL_KEY")
    if not effective_api_key:
        raise ValueError("fal.ai API key not provided. Set FAL_KEY or pass api_key=...")

    client = fal_client.AsyncClient(key=effective_api_key)

    os.makedirs(output_dir, exist_ok=True)

    if prompt is None:
        prompt = (
            "Turn this image into a professional quality studio shoot "
            "with better lighting and depth of field."
        )
    prompt = _append_aspect_ratio_instruction(prompt, aspect_ratio)

    image_urls = []
    for path in image_paths:
        with open(path, "rb") as f:
            data = f.read()
        mime_type = _get_mime_type(path)
        b64 = base64.b64encode(data).decode("utf-8")
        image_urls.append(f"data:{mime_type};base64,{b64}")

    arguments = {
        "prompt": prompt,
        "image_urls": image_urls,
        "quality": quality,
    }

    if "openai" not in MODEL_NAME:
        if aspect_ratio == "auto":
            arguments["image_size"] = "auto"
        elif aspect_ratio and aspect_ratio in ASPECT_RATIO_MAP:
            arguments["image_size"] = ASPECT_RATIO_MAP[aspect_ratio]

    try:
        print(f"Submitting request to {MODEL_NAME}...")
        handler = await client.submit(
            MODEL_NAME,
            arguments=arguments,
        )

        result = await handler.get()
        await _process_fal_response_async(result, output_dir)

    except Exception as e:
        print(f"fal.ai request failed: {e}")
        raise


async def _process_fal_response_async(result, output_dir):
    if not result or "images" not in result or not result["images"]:
        print("No images returned from fal.ai.")
        return

    for i, img_info in enumerate(result["images"]):
        image_url = img_info["url"]

        content_type = img_info.get("content_type", "image/png")
        ext = mimetypes.guess_extension(content_type) or ".png"

        filename = os.path.join(
            output_dir,
            f"remixed_{int(time.time())}_{i}{ext}"
        )

        print(f"Downloading generated image to {filename}...")
        response = await asyncio.to_thread(requests.get, image_url)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)


def _append_aspect_ratio_instruction(prompt, aspect_ratio):
    if not aspect_ratio or aspect_ratio == "auto" or aspect_ratio not in ASPECT_RATIO_MAP:
        return prompt
    return f"{prompt} The final image must use a {aspect_ratio} aspect ratio."


def _get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        ext = os.path.splitext(path)[1].lower()
        if ext in [".jpg", ".jpeg"]: return "image/jpeg"
        if ext == ".png": return "image/png"
        if ext == ".webp": return "image/webp"
        raise ValueError(f"Cannot determine MIME type for {path}")
    return mime


def remix_images(
    image_paths,
    prompt=None,
    MODEL_NAME=DEFAULT_MODEL_NAME,
    output_dir="output",
    api_key=None,
    aspect_ratio=None,
    quality="low",
):
    return asyncio.run(remix_images_async(
        image_paths=image_paths,
        prompt=prompt,
        MODEL_NAME=MODEL_NAME,
        output_dir=output_dir,
        api_key=api_key,
        aspect_ratio=aspect_ratio,
        quality=quality,
    ))
