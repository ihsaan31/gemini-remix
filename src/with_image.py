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
# import mimetypes
# import os
# import time
# import random

# from google import genai
# from google.genai import types
# from google.api_core.exceptions import ServerError

# # =========================
# # DEFAULT MODEL
# # =========================
# DEFAULT_MODEL_NAME = "gemini-3-pro-image-preview"

# # =========================
# # RETRY HELPER
# # =========================
# def with_retry(fn, max_retries=5, base_delay=1.0, max_delay=30.0):
#     for attempt in range(1, max_retries + 1):
#         try:
#             return fn()
#         except ServerError:
#             if attempt == max_retries:
#                 raise

#             delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
#             delay += random.uniform(0, delay * 0.2)
#             time.sleep(delay)

# # =========================
# # MAIN API LOGIC
# # =========================
# def remix_images(
#     image_paths,
#     prompt=None,
#     MODEL_NAME=DEFAULT_MODEL_NAME,
#     output_dir="output",
#     api_key=None,
#     aspect_ratio=None,
# ):
#     if not api_key:
#         raise ValueError("API key not provided.")

#     os.makedirs(output_dir, exist_ok=True)

#     if prompt is None:
#         prompt = (
#             "Turn this image into a professional quality studio shoot "
#             "with better lighting and depth of field."
#         )

#     client = genai.Client(api_key=api_key)

#     contents = _load_image_parts(image_paths)
#     contents.append(types.Part.from_text(text=prompt))

#     generate_config_kwargs = {
#         "response_modalities": ["IMAGE", "TEXT"]
#     }
#     if aspect_ratio:
#         generate_config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)

#     config = types.GenerateContentConfig(**generate_config_kwargs)

#     def run_stream():
#         stream = client.models.generate_content_stream(
#             model=MODEL_NAME,
#             contents=contents,
#             config=config,
#         )
#         _process_api_stream_response(stream, output_dir)

#     with_retry(run_stream)

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

# def _save_binary_file(path, data):
#     with open(path, "wb") as f:
#         f.write(data)

# def _get_mime_type(path):
#     mime, _ = mimetypes.guess_type(path)
#     if not mime:
#         raise ValueError(f"Cannot determine MIME type for {path}")
#     return mime
####################################################################################################################################################



import mimetypes
import os
import time
import random
import base64

from openai import OpenAI

# =========================
# DEFAULT MODEL
# =========================
DEFAULT_MODEL_NAME = "bytedance-seed/seedream-4.5"

# =========================
# RETRY HELPER
# =========================
def with_retry(fn, max_retries=5, base_delay=1.0, max_delay=30.0):
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as e:
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
    aspect_ratio=None,
):
    if not api_key:
        raise ValueError("API key not provided.")

    os.makedirs(output_dir, exist_ok=True)

    if prompt is None:
        prompt = (
            "Turn this image into a professional quality studio shoot "
            "with better lighting and depth of field."
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = _build_messages(image_paths, prompt)

    def run():
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            extra_body={"modalities": ["image"]},
        )

        _process_openrouter_response(response, output_dir)

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

def _process_openrouter_response(response, output_dir):
    file_index = 0
    message = response.choices[0].message

    if not hasattr(message, "images") or not message.images:
        print("No images returned.")
        return

    for image in message.images:
        image_url = image["image_url"]["url"]

        # Extract base64 from data URL
        if image_url.startswith("data:"):
            header, b64_data = image_url.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]

            ext = mimetypes.guess_extension(mime_type) or ".png"
            filename = os.path.join(
                output_dir,
                f"remixed_{int(time.time())}_{file_index}{ext}"
            )

            _save_binary_file(filename, base64.b64decode(b64_data))
            file_index += 1

def _save_binary_file(path, data):
    with open(path, "wb") as f:
        f.write(data)

def _get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        raise ValueError(f"Cannot determine MIME type for {path}")
    return mime

