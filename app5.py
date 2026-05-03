import streamlit as st
import os
import glob
import zipfile
import io
import shutil
from src.with_image_v3 import remix_images

# =========================
# SETUP
# =========================
st.set_page_config(
    page_title="fal.ai Image Remixer Pro",
    layout="wide"
)

TEMP_INPUT_DIR = "temp_streamlit_input"
TEMP_OUTPUT_DIR = "temp_streamlit_output"

os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# =========================
# HELPERS
# =========================
def create_zip(paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in paths:
            zf.write(file_path, arcname=os.path.basename(file_path))
    zip_buffer.seek(0)
    return zip_buffer

def _get_fal_api_key_default() -> str:
    # Works both locally and on Streamlit Cloud.
    try:
        secret_val = st.secrets.get("FAL_KEY")
        if secret_val:
            return str(secret_val)
    except Exception:
        pass
    return os.environ.get("FAL_KEY", "")

# =========================
# SESSION STATE
# =========================
if "prompts" not in st.session_state:
    st.session_state.prompts = ["Cyberpunk style"]

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("Settings")

    if "fal_api_key" not in st.session_state:
        st.session_state.fal_api_key = _get_fal_api_key_default()

    st.session_state.fal_api_key = st.text_input(
        "fal.ai API Key (FAL_KEY)",
        type="password",
        value=st.session_state.fal_api_key
    )

    if not st.session_state.fal_api_key:
        st.warning(
            "Set a fal.ai key to run image generation. "
            "You can set it in this textbox, or via the FAL_KEY env var / Streamlit secret."
        )

    # Image generation models
    st.subheader("Image Models")
    image_model_choice = st.selectbox(
        "Model",
        [
            "openai/gpt-image-2/edit",
            "fal-ai/bytedance/seedream/v5/lite/edit",
            "fal-ai/nano-banana-2/edit",
        ],
        index=0,
        key="image_model"
    )

    st.divider()

    quality_choice = st.selectbox(
        "Quality",
        ["low", "medium", "high"],
        index=2,
        key="quality_choice"
    )

    aspect_ratio_choice = st.selectbox(
        "Aspect Ratio (Images)",
        ["auto", "1:1", "3:4", "4:3", "9:16", "16:9"],
        index=0
    )

# =========================
# MAIN UI
# =========================
st.title("⚡ fal.ai Image Remixer Pro")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📁 Batch Images (1 Prompt)",
        "📝 Multi-Prompt (1 Image)",
        "🖼️ Multi-Image Blend (1 Prompt)",
        "✍️ Text to Image",
    ]
)

# ==========================================================
# TAB 1 — BATCH IMAGES
# ==========================================================
with tab1:
    st.markdown("Process **multiple images** using the **same prompt**.")

    t1_prompt = st.text_area(
        "Prompt",
        value="Studio lighting, professional photography",
        key="t1_prompt_area"
    )

    t1_files = st.file_uploader(
        "Upload Images",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
        key="t1_files"
    )

    if st.button(
        "Run Batch Process",
        type="primary",
        disabled=(not t1_files) or (not st.session_state.fal_api_key),
        key="t1_run_btn"
    ):
        all_paths = []
        progress = st.progress(0)

        for i, file in enumerate(t1_files):
            in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
            with open(in_path, "wb") as f:
                f.write(file.getbuffer())

            out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
            shutil.rmtree(out_dir, ignore_errors=True)
            os.makedirs(out_dir, exist_ok=True)

            try:
                remix_images(
                    image_paths=[in_path],
                    prompt=t1_prompt,
                    MODEL_NAME=image_model_choice,
                    output_dir=out_dir,
                    api_key=st.session_state.fal_api_key,
                    aspect_ratio=aspect_ratio_choice,
                    quality=quality_choice
                )
            except Exception as e:
                st.error(f"Image {i + 1} failed: {e}")
                progress.progress((i + 1) / len(t1_files))
                continue

            results = sorted(glob.glob(os.path.join(out_dir, "*")))
            if results:
                result_path = results[0]
                all_paths.append(result_path)

                col_a, col_b = st.columns(2)
                col_a.image(file, caption="Original")
                col_b.image(result_path, caption=f"Result {i + 1}")

                with open(result_path, "rb") as f:
                    col_b.download_button(
                        "Download",
                        f,
                        file_name=f"batch_{i}.png",
                        key=f"t1_dl_{i}"
                    )

            progress.progress((i + 1) / len(t1_files))

        if all_paths:
            st.divider()
            st.download_button(
                "📦 Download All Results (ZIP)",
                create_zip(all_paths),
                "batch_results.zip",
                key="t1_zip_dl"
            )

# ==========================================================
# TAB 2 — MULTI PROMPT
# ==========================================================
with tab2:
    st.markdown("Process **one image** using **multiple independent prompts**.")

    t2_file = st.file_uploader(
        "Upload One Image",
        type=["jpg", "png", "jpeg"],
        key="t2_file"
    )

    st.subheader("Prompts")

    # Prompt inputs
    for i, prompt in enumerate(st.session_state.prompts):
        cols = st.columns([8, 1])
        st.session_state.prompts[i] = cols[0].text_input(
            f"Prompt {i + 1}",
            value=prompt,
            key=f"prompt_{i}"
        )
        if cols[1].button("❌", key=f"remove_{i}"):
            st.session_state.prompts.pop(i)
            st.rerun()

    if st.button("➕ Add Prompt", key="add_prompt_btn"):
        st.session_state.prompts.append("")
        st.rerun()

    prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

    if st.button(
        "Run Multi-Prompt Process",
        type="primary",
        disabled=(not t2_file) or (not prompt_list) or (not st.session_state.fal_api_key),
        key="t2_run_btn"
    ):
        all_paths = []
        progress = st.progress(0)

        # IMPORTANT: keep original bytes immutable
        original_bytes = t2_file.getbuffer()

        for i, prompt in enumerate(prompt_list):
            st.write(f"Running Prompt {i + 1}: *{prompt}*")

            # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
            in_path = os.path.join(
                TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
            )
            with open(in_path, "wb") as f:
                f.write(original_bytes)

            out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
            shutil.rmtree(out_dir, ignore_errors=True)
            os.makedirs(out_dir, exist_ok=True)

            try:
                remix_images(
                    image_paths=[in_path],
                    prompt=prompt,
                    MODEL_NAME=image_model_choice,
                    output_dir=out_dir,
                    api_key=st.session_state.fal_api_key,
                    aspect_ratio=aspect_ratio_choice,
                    quality=quality_choice
                )
            except Exception as e:
                st.error(f"Prompt {i + 1} failed: {e}")
                progress.progress((i + 1) / len(prompt_list))
                continue

            results = sorted(glob.glob(os.path.join(out_dir, "*")))
            if results:
                result_path = results[0]
                all_paths.append(result_path)

                col_a, col_b = st.columns(2)
                col_a.image(t2_file, caption="Original")
                col_b.image(result_path, caption=prompt)

                with open(result_path, "rb") as f:
                    col_b.download_button(
                        "Download",
                        f,
                        file_name=f"prompt_{i}.png",
                        key=f"t2_dl_{i}"
                    )

            progress.progress((i + 1) / len(prompt_list))

        if all_paths:
            st.divider()
            st.download_button(
                "📦 Download All Variations (ZIP)",
                create_zip(all_paths),
                "variations.zip",
                key="t2_zip_dl"
            )

# ==========================================================
# TAB 3 — MULTI-IMAGE BLEND
# ==========================================================
with tab3:
    st.markdown("Process **multiple reference images** together into a **single result**.")

    t3_prompt = st.text_area(
        "Prompt",
        value="Combine the subjects of these images in a natural way, producing a new image.",
        key="t3_prompt_area"
    )

    t3_files = st.file_uploader(
        "Upload Reference Images (Max 5 recommended)",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
        key="t3_files_uploader"
    )

    if st.button(
        "Run Multi-Image Blend",
        type="primary",
        disabled=(not t3_files) or (not st.session_state.fal_api_key),
        key="t3_run_btn"
    ):
        progress = st.progress(0)

        in_paths = []
        for i, file in enumerate(t3_files):
            in_path = os.path.join(TEMP_INPUT_DIR, f"blend_input_{i}.png")
            with open(in_path, "wb") as f:
                f.write(file.getbuffer())
            in_paths.append(in_path)

        out_dir = os.path.join(TEMP_OUTPUT_DIR, "blend_output")
        shutil.rmtree(out_dir, ignore_errors=True)
        os.makedirs(out_dir, exist_ok=True)

        st.write(f"Running blend process using {len(in_paths)} images...")

        try:
            remix_images(
                image_paths=in_paths,
                prompt=t3_prompt,
                MODEL_NAME=image_model_choice,
                output_dir=out_dir,
                api_key=st.session_state.fal_api_key,
                aspect_ratio=aspect_ratio_choice,
                quality=quality_choice
            )
        except Exception as e:
            st.error(f"Blend failed: {e}")
            st.stop()

        results = sorted(glob.glob(os.path.join(out_dir, "*")))
        if results:
            result_path = results[0]

            st.subheader("Input Reference Images")
            cols = st.columns(len(t3_files))
            for idx, col in enumerate(cols):
                col.image(t3_files[idx], caption=f"Ref {idx+1}")

            st.subheader("Blended Result")
            st.image(result_path, use_container_width=True)

            with open(result_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Blended Image",
                    f,
                    file_name="blended_result.png",
                    key="t3_dl_btn"
                )

        progress.progress(1.0)

# ==========================================================
# TAB 4 — TEXT TO IMAGE
# ==========================================================
with tab4:
    st.markdown("Generate **new images** from text prompts (no reference images).")

    t4_prompt = st.text_area(
        "Prompt",
        value="A futuristic city with flying cars at sunset, studio lighting, hyperrealistic",
        key="t4_prompt_area"
    )

    t4_count = st.number_input(
        "Number of Images to Generate",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        key="t4_count"
    )

    if st.button(
        "Run Text-to-Image",
        type="primary",
        disabled=not st.session_state.fal_api_key,
        key="t4_run_btn"
    ):
        progress = st.progress(0)
        all_paths = []

        for i in range(t4_count):
            st.write(f"Generating image {i + 1} of {t4_count}...")

            out_dir = os.path.join(TEMP_OUTPUT_DIR, f"text_to_image_{i}")
            shutil.rmtree(out_dir, ignore_errors=True)
            os.makedirs(out_dir, exist_ok=True)

            try:
                remix_images(
                    image_paths=[],
                    prompt=t4_prompt,
                    MODEL_NAME=image_model_choice,
                    output_dir=out_dir,
                    api_key=st.session_state.fal_api_key,
                    aspect_ratio=aspect_ratio_choice,
                    quality=quality_choice
                )
            except Exception as e:
                st.error(f"Generation {i + 1} failed: {e}")
                progress.progress((i + 1) / t4_count)
                continue

            results = sorted(glob.glob(os.path.join(out_dir, "*")))
            if results:
                result_path = results[0]
                all_paths.append(result_path)

                st.image(result_path, caption=f"Generated Image {i + 1}")

                with open(result_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Image",
                        f,
                        file_name=f"generated_{i}.png",
                        key=f"t4_dl_btn_{i}"
                    )

            progress.progress((i + 1) / t4_count)

        if all_paths and len(all_paths) > 1:
            st.divider()
            st.download_button(
                "📦 Download All Results (ZIP)",
                create_zip(all_paths),
                "generated_results.zip",
                key="t4_zip_dl"
            )
