# import mimetypes
# import os
# import time
# import random
# from pathlib import Path

# from google import genai
# from google.genai import types
# from google.api_core.exceptions import ServerError

# # =========================
# # CONFIG
# # =========================


# #MODEL_NAME = "gemini-2.5-flash-image-preview"
# MODEL_NAME = "gemini-3-pro-image-preview"


# # =========================
# # RETRY HELPER
# # =========================

# def with_retry(fn, max_retries=5, base_delay=1.0, max_delay=30.0):
#     """
#     Retry wrapper with exponential backoff + jitter.
#     Retries only ServerError (5xx).
#     """
#     for attempt in range(1, max_retries + 1):
#         try:
#             return fn()
#         except ServerError as e:
#             if attempt == max_retries:
#                 print("[retry] Max retries reached. Raising error.")
#                 raise

#             delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
#             delay += random.uniform(0, delay * 0.2)

#             print(
#                 f"[retry] Attempt {attempt}/{max_retries} failed "
#                 f"(ServerError). Retrying in {delay:.1f}s..."
#             )
#             time.sleep(delay)


# # =========================
# # MAIN API LOGIC
# # =========================

# def remix_images(
#     image_paths,
#     prompt=None,
#     MODEL_NAME=MODEL_NAME,
#     output_dir="output",
    
# ):
#     """
#     Remix 1–5 images using Gemini Flash Image (Nano Banana).
#     """

#     api_key = os.environ.get("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY environment variable not set.")

#     os.makedirs(output_dir, exist_ok=True)

#     # Default prompt logic
#     if prompt is None:
#         if len(image_paths) == 1:
#             prompt = (
#                 "Turn this image into a professional quality studio shoot "
#                 "with better lighting and depth of field."
#             )
#         else:
#             prompt = (
#                 "Combine the subjects of these images in a natural way, "
#                 "producing a new image."
#             )

#     client = genai.Client(api_key=api_key)

#     contents = _load_image_parts(image_paths)
#     contents.append(types.Part.from_text(text=prompt))

#     config = types.GenerateContentConfig(
#         response_modalities=["IMAGE", "TEXT"]
#     )

#     print(f"\nRemixing {len(image_paths)} image(s)")
#     print(f"Prompt: {prompt}")

#     # ---- STREAM CALL (RETRIED) ----
#     def run_stream():
#         stream = client.models.generate_content_stream(
#             model=MODEL_NAME,
#             contents=contents,
#             config=config,
#         )
#         _process_api_stream_response(stream, output_dir)

#     with_retry(run_stream, max_retries=5)


# # =========================
# # HELPERS
# # =========================

# def _load_image_parts(image_paths):
#     parts = []
#     for path in image_paths:
#         with open(path, "rb") as f:
#             data = f.read()

#         mime_type = _get_mime_type(path)
#         parts.append(
#             types.Part(
#                 inline_data=types.Blob(
#                     data=data,
#                     mime_type=mime_type
#                 )
#             )
#         )
#     return parts


# def _process_api_stream_response(stream, output_dir):
#     file_index = 0

#     for chunk in stream:
#         if not chunk.candidates:
#             continue

#         content = chunk.candidates[0].content
#         if not content or not content.parts:
#             continue

#         for part in content.parts:
#             if part.inline_data and part.inline_data.data:
#                 timestamp = int(time.time())
#                 ext = (
#                     mimetypes.guess_extension(part.inline_data.mime_type)
#                     or ".png"
#                 )
#                 filename = os.path.join(
#                     output_dir,
#                     f"remixed_{timestamp}_{file_index}{ext}"
#                 )
#                 _save_binary_file(filename, part.inline_data.data)
#                 file_index += 1

#             elif part.text:
#                 print(part.text)


# def _save_binary_file(path, data):
#     with open(path, "wb") as f:
#         f.write(data)
#     print(f"Saved: {path}")


# def _get_mime_type(path):
#     mime, _ = mimetypes.guess_type(path)
#     if not mime:
#         raise ValueError(f"Cannot determine MIME type for {path}")
#     return mime

#########################################################################
import mimetypes
import os
import time
import random

from google import genai
from google.genai import types
from google.api_core.exceptions import ServerError

# =========================
# DEFAULT MODEL
# =========================
DEFAULT_MODEL_NAME = "gemini-3-pro-image-preview"

# =========================
# RETRY HELPER
# =========================
def with_retry(fn, max_retries=5, base_delay=1.0, max_delay=30.0):
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except ServerError:
            if attempt == max_retries:
                raise

            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay += random.uniform(0, delay * 0.2)
            time.sleep(delay)

# =========================
# MAIN API LOGIC
# =========================
def remix_images(
    image_paths,
    prompt=None,
    MODEL_NAME=DEFAULT_MODEL_NAME,
    output_dir="output",
    api_key=None,
):
    if not api_key:
        raise ValueError("API key not provided.")

    os.makedirs(output_dir, exist_ok=True)

    if prompt is None:
        prompt = (
            "Turn this image into a professional quality studio shoot "
            "with better lighting and depth of field."
        )

    client = genai.Client(api_key=api_key)

    contents = _load_image_parts(image_paths)
    contents.append(types.Part.from_text(text=prompt))

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"]
    )

    def run_stream():
        stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )
        _process_api_stream_response(stream, output_dir)

    with_retry(run_stream)

# =========================
# HELPERS
# =========================
def _load_image_parts(image_paths):
    parts = []
    for path in image_paths:
        with open(path, "rb") as f:
            data = f.read()

        mime_type = _get_mime_type(path)
        parts.append(
            types.Part(
                inline_data=types.Blob(
                    data=data,
                    mime_type=mime_type
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
            if part.inline_data and part.inline_data.data:
                timestamp = int(time.time())
                ext = (
                    mimetypes.guess_extension(part.inline_data.mime_type)
                    or ".png"
                )
                filename = os.path.join(
                    output_dir,
                    f"remixed_{timestamp}_{file_index}{ext}"
                )
                _save_binary_file(filename, part.inline_data.data)
                file_index += 1

def _save_binary_file(path, data):
    with open(path, "wb") as f:
        f.write(data)

def _get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        raise ValueError(f"Cannot determine MIME type for {path}")
    return mime

