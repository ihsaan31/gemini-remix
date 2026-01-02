import mimetypes
import os
import time
from google import genai
from google.genai import types
from IPython.display import display, Image as IPImage
import mimetypes
import os
import time

MODEL_NAME = "gemini-2.5-flash-image-preview"

def no_images(
    image_paths=None,
    prompt=None,
    output_dir="/mnt/c/work/nano-banana-python-main/output",
):
    """
    Generate images from text only OR remix 1–5 images using Gemini Flash Image.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    os.makedirs(output_dir, exist_ok=True)

    # Default prompt logic
    if not prompt:
        if image_paths:
            prompt = "Enhance and remix the provided image with studio-quality lighting."
        else:
            prompt = "Generate a high-quality studio background image."

    client = genai.Client(api_key=api_key)

    contents = []

    # Load images only if provided
    if image_paths:
        if not isinstance(image_paths, (list, tuple)):
            raise ValueError("image_paths must be a list of file paths.")
        contents.extend(_load_image_parts(image_paths))

    # Add text prompt
    contents.append(types.Part.from_text(text=prompt))

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"]
    )

    num_images = len(image_paths) if image_paths else 0
    print(f"Remixing {num_images} image(s)")
    print(f"Prompt: {prompt}")

    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=contents,
        config=config,
    )

    _process_api_stream_response(stream, output_dir)


# =========================
# HELPERS
# =========================

def _load_image_parts(image_paths):
    parts = []

    for path in image_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")

        with open(path, "rb") as f:
            data = f.read()

        mime_type = _get_mime_type(path)

        parts.append(
            types.Part(
                inline_data=types.Blob(
                    data=data,
                    mime_type=mime_type,
                )
            )
        )

    return parts


def _process_api_stream_response(stream, output_dir):
    file_index = 0

    for chunk in stream:
        if not chunk.candidates:
            continue

        content = chunk.candidates[0].content
        if not content or not content.parts:
            continue

        for part in content.parts:
            # Save images
            if part.inline_data and part.inline_data.data:
                timestamp = int(time.time())
                ext = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
                filename = os.path.join(
                    output_dir,
                    f"generated_{timestamp}_{file_index}{ext}"
                )

                _save_binary_file(filename, part.inline_data.data)
                file_index += 1

            # Print text output (if any)
            elif part.text:
                print(part.text)


def _save_binary_file(path, data):
    with open(path, "wb") as f:
        f.write(data)
    print(f"Saved: {path}")


def _get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        raise ValueError(f"Cannot determine MIME type for {path}")
    return mime