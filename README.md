# Nano Banana Python - Image Mixer

This project demonstrates how to remix 1 to 5 images using Google Generative AI.

## Streamlit App (OpenRouter)

The included Streamlit app (`app.py`) uses OpenRouter for image remixing / text-to-image.

### Setup

Set an OpenRouter API key:

```bash
export OPENROUTER_API_KEY="YOUR_OPENROUTER_KEY"
```

If you deploy on Streamlit Cloud, set `OPENROUTER_API_KEY` in the app's Secrets.

### Run

```bash
streamlit run app.py
```

Notes:

- If you see `PermissionDenied` / `403`, it usually means your OpenRouter key is missing/invalid, or your account does not have access or credits for the selected model.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd nano-banana-python
    ```

2.  **Install dependencies using `uv`:**

    ```bash
    uv sync
    ```

3.  **Set your Google Gemini API Key:**
    Ensure you have your `GEMINI_API_KEY` or `GOOGLE_API_KEY` set as an environment variable.

    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    # OR
    export GOOGLE_API_KEY="YOUR_API_KEY"
    ```

## Usage

Run the `mix_images.py` script with 1 to 5 input images and an optional prompt. The remixed image(s) will be saved in the `output` directory (or a custom directory if specified).

-   If one image is provided without a prompt, the default prompt will be to "Turn this image into a professional quality studio shoot with better lighting and depth of field.".
-   If multiple images are provided without a prompt, the default prompt will be to "Combine these images in a way that makes sense.".
-   If a prompt is explicitly provided, it will always be used.

### Example 1: Improve a single image (default prompt)

```bash
uv run python src/mix_images.py -i images/man.jpeg
```

### Example 2: Combine two images (default prompt)

```bash
uv run python src/mix_images.py -i images/man.jpeg -i images/cap.jpeg
```

### Example 3: Combine multiple images with a custom prompt

```bash
uv run python src/mix_images.py -i images/man.jpeg -i images/cap.jpeg -i images/soda.jpeg --prompt "Create a product advertisement with the man, cap, and soda."
```

### Example 4: Specify Output Directory

```bash
uv run python src/mix_images.py -i images/man.jpeg -i images/cap.jpeg --prompt "Remix these two images." --output-dir my_custom_output
```
