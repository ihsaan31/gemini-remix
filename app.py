# import streamlit as st
# import os
# import shutil
# import glob
# import zipfile
# import io
# from src.with_image import remix_images  # Importing your function directly

# # =========================
# # SETUP
# # =========================
# st.set_page_config(page_title="Gemini Batch Remixer", layout="wide")

# # temporary folders to handle file passing
# TEMP_INPUT_DIR = "temp_streamlit_input"
# TEMP_OUTPUT_DIR = "temp_streamlit_output"

# os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # =========================
# # UI LAYOUT
# # =========================
# st.title("⚡ Gemini Batch Image Remixer")
# st.markdown("Upload multiple images. They will be processed **one by one** using your existing script.")

# # Sidebar configuration
# with st.sidebar:
#     st.header("Configuration")
    
#     # Allow API Key override, otherwise use env var inside your script
#     api_key_input = st.text_input("API Key (Optional override)", type="password")
#     if api_key_input:
#         os.environ["GEMINI_API_KEY"] = api_key_input
    
#     model_choice = st.selectbox(
#         "Model", 
#         ["gemini-3-pro-image-preview", "gemini-2.5-flash-image-preview"],
#         index=0
#     )

# # Main Inputs
# prompt = st.text_area(
#     "Prompt", 
#     value="Turn this image into a professional quality studio shoot with better lighting and depth of field.",
#     height=100
# )

# uploaded_files = st.file_uploader(
#     "Upload Images", 
#     type=["jpg", "jpeg", "png", "webp"], 
#     accept_multiple_files=True
# )

# run_btn = st.button("Start Processing", type="primary", disabled=not uploaded_files)

# # =========================
# # PROCESSING LOGIC
# # =========================
# if run_btn and uploaded_files:
#     st.divider()
#     progress_bar = st.progress(0)
#     status_area = st.empty()
#     results_container = st.container()

#     # Clear previous temp outputs to avoid confusion
#     if os.path.exists(TEMP_OUTPUT_DIR):
#         shutil.rmtree(TEMP_OUTPUT_DIR)
#     os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

#     total = len(uploaded_files)
#     all_generated_paths = [] # Keep track for the ZIP file later

#     for i, uploaded_file in enumerate(uploaded_files):
#         # 1. Update Status
#         status_area.info(f"Processing {i+1}/{total}: **{uploaded_file.name}**...")
        
#         # 2. Save Uploaded File to Disk
#         current_input_path = os.path.join(TEMP_INPUT_DIR, uploaded_file.name)
#         with open(current_input_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         # 3. Create a unique output subfolder
#         current_output_dir = os.path.join(TEMP_OUTPUT_DIR, f"result_{i}")
#         os.makedirs(current_output_dir, exist_ok=True)

#         try:
#             # 4. CALL YOUR IMPORTED FUNCTION
#             remix_images(
#                 image_paths=[current_input_path],
#                 prompt=prompt,
#                 MODEL_NAME=model_choice,
#                 output_dir=current_output_dir
#             )

#             # 5. Find the generated file
#             generated_files = glob.glob(os.path.join(current_output_dir, "*"))
            
#             # 6. Display Result
#             with results_container:
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.image(uploaded_file, caption=f"Original: {uploaded_file.name}", use_container_width=True)
#                 with col2:
#                     if generated_files:
#                         gen_path = generated_files[0]
#                         all_generated_paths.append(gen_path)
                        
#                         st.image(gen_path, caption="Generated Result", use_container_width=True)
                        
#                         # --- INDIVIDUAL DOWNLOAD BUTTON ---
#                         with open(gen_path, "rb") as file:
#                             btn = st.download_button(
#                                 label="⬇️ Download Image",
#                                 data=file,
#                                 file_name=f"remixed_{uploaded_file.name}",
#                                 mime="image/png",
#                                 key=f"dl_btn_{i}" # Unique key is required inside loops
#                             )
#                     else:
#                         st.error("No output file was created.")
#                 st.divider()

#         except Exception as e:
#             st.error(f"Error processing {uploaded_file.name}: {e}")

#         # Update Progress
#         progress_bar.progress((i + 1) / total)

#     status_area.success("All images processed successfully!")

#     # =========================
#     # BULK DOWNLOAD (ZIP)
#     # =========================
#     if all_generated_paths:
#         # Create an in-memory zip file
#         zip_buffer = io.BytesIO()
#         with zipfile.ZipFile(zip_buffer, "w") as zf:
#             for file_path in all_generated_paths:
#                 # Add file to zip, arcname ensures it has a clean name inside the zip
#                 file_name = os.path.basename(file_path)
#                 zf.write(file_path, arcname=file_name)
        
#         # Reset pointer to beginning of buffer
#         zip_buffer.seek(0)

#         st.download_button(
#             label="📦 Download All Images (ZIP)",
#             data=zip_buffer,
#             file_name="all_remixed_images.zip",
#             mime="application/zip"
#         )
####################################################################################################################################
# import streamlit as st
# import os
# import shutil
# import glob
# import zipfile
# import io
# from src.with_image import remix_images  # Importing your function directly

# # =========================
# # SETUP
# # =========================
# st.set_page_config(page_title="Gemini Remixer Pro", layout="wide")

# TEMP_INPUT_DIR = "temp_streamlit_input"
# TEMP_OUTPUT_DIR = "temp_streamlit_output"

# os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # Helper function to create ZIP
# def create_zip(paths):
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w") as zf:
#         for file_path in paths:
#             zf.write(file_path, arcname=os.path.basename(file_path))
#     zip_buffer.seek(0)
#     return zip_buffer

# # =========================
# # SIDEBAR
# # =========================
# with st.sidebar:
#     st.header("Settings")
#     api_key_input = st.text_input("API Key (Optional override)", type="password")
#     if api_key_input:
#         os.environ["GEMINI_API_KEY"] = api_key_input
    
#     model_choice = st.selectbox(
#         "Model", 
#         ["gemini-3-pro-image-preview", "gemini-2.5-flash-image-preview"],
#         index=0
#     )

# # =========================
# # MAIN UI
# # =========================
# st.title("⚡ Gemini Image Remixer")

# tab1, tab2 = st.tabs(["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)"])

# # -------------------------
# # TAB 1: BATCH IMAGES
# # -------------------------
# with tab1:
#     st.markdown("Process many images using the **same** prompt.")
#     t1_prompt = st.text_area("Prompt", value="Studio lighting, professional photography", key="t1_p")
#     t1_files = st.file_uploader("Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="t1_f")
    
#     if st.button("Run Batch Process", type="primary", disabled=not t1_files):
#         all_paths = []
#         progress = st.progress(0)
        
#         for i, file in enumerate(t1_files):
#             in_path = os.path.join(TEMP_INPUT_DIR, file.name)
#             with open(in_path, "wb") as f:
#                 f.write(file.getbuffer())
            
#             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
#             os.makedirs(out_dir, exist_ok=True)
            
#             remix_images(image_paths=[in_path], prompt=t1_prompt, MODEL_NAME=model_choice, output_dir=out_dir)
            
#             res = glob.glob(os.path.join(out_dir, "*"))
#             if res:
#                 all_paths.append(res[0])
#                 col_a, col_b = st.columns(2)
#                 col_a.image(file, caption="Original")
#                 col_b.image(res[0], caption=f"Result {i+1}")
#                 with col_b:
#                     with open(res[0], "rb") as f:
#                         st.download_button("Download", f, file_name=f"res_{i}.png", key=f"t1_dl_{i}")
            
#             progress.progress((i + 1) / len(t1_files))
        
#         if all_paths:
#             st.download_button("📦 Download All (ZIP)", create_zip(all_paths), "batch_results.zip")

# # -------------------------
# # TAB 2: MULTI-PROMPT
# # -------------------------
# with tab2:
#     st.markdown("Process **one image** using **multiple different prompts**.")
#     t2_file = st.file_uploader("Upload One Image", type=["jpg", "png", "jpeg"], key="t2_f")
#     t2_prompts_raw = st.text_area("Prompts (One per line)", value="Cyberpunk style\nOil painting style\nSketch drawing", height=150)
    
#     # Convert text area lines to a list of prompts
#     prompt_list = [p.strip() for p in t2_prompts_raw.split("\n") if p.strip()]

#     if st.button("Run Multi-Prompt Process", type="primary", disabled=not t2_file or not prompt_list):
#         all_paths = []
        
#         # Save the single image
#         in_path = os.path.join(TEMP_INPUT_DIR, "single_source.png")
#         with open(in_path, "wb") as f:
#             f.write(t2_file.getbuffer())
            
#         progress = st.progress(0)
        
#         for i, p in enumerate(prompt_list):
#             st.write(f"Running Prompt {i+1}: *{p}*")
#             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
#             os.makedirs(out_dir, exist_ok=True)
            
#             remix_images(image_paths=[in_path], prompt=p, MODEL_NAME=model_choice, output_dir=out_dir)
            
#             res = glob.glob(os.path.join(out_dir, "*"))
#             if res:
#                 all_paths.append(res[0])
#                 col_a, col_b = st.columns(2)
#                 col_a.image(t2_file, caption="Original Source")
#                 col_b.image(res[0], caption=f"Prompt: {p}")
#                 with col_b:
#                     with open(res[0], "rb") as f:
#                         st.download_button("Download", f, file_name=f"prompt_{i}.png", key=f"t2_dl_{i}")
            
#             progress.progress((i + 1) / len(prompt_list))

#         if all_paths:
#             st.divider()
#             st.download_button("📦 Download All Variations (ZIP)", create_zip(all_paths), "variations.zip")
######################################################################################################################################
# import streamlit as st
# import os
# import glob
# import zipfile
# import io
# import shutil
# from src.with_image import remix_images

# # =========================
# # SETUP
# # =========================
# st.set_page_config(
#     page_title="Gemini Remixer Pro",
#     layout="wide"
# )

# TEMP_INPUT_DIR = "temp_streamlit_input"
# TEMP_OUTPUT_DIR = "temp_streamlit_output"

# os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # =========================
# # HELPERS
# # =========================
# def create_zip(paths):
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
#         for file_path in paths:
#             zf.write(file_path, arcname=os.path.basename(file_path))
#     zip_buffer.seek(0)
#     return zip_buffer

# # =========================
# # SESSION STATE
# # =========================
# if "prompts" not in st.session_state:
#     st.session_state.prompts = ["Cyberpunk style"]

# # =========================
# # SIDEBAR
# # =========================
# with st.sidebar:
#     st.header("Settings")

#     api_key_input = st.text_input(
#         "API Key (Optional override)",
#         type="password"
#     )
#     # if api_key_input:
#     #     os.environ["GEMINI_API_KEY"] = api_key_input

#     model_choice = st.selectbox(
#         "Model",
#         [
#             "gemini-3-pro-image-preview",
#             "gemini-2.5-flash-image"
#         ],
#         index=0
#     )

# # =========================
# # MAIN UI
# # =========================
# st.title("⚡ Gemini Image Remixer")

# tab1, tab2 = st.tabs(
#     ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)"]
# )

# # ==========================================================
# # TAB 1 — BATCH IMAGES
# # ==========================================================
# with tab1:
#     st.markdown("Process **multiple images** using the **same prompt**.")

#     t1_prompt = st.text_area(
#         "Prompt",
#         value="Studio lighting, professional photography"
#     )

#     t1_files = st.file_uploader(
#         "Upload Images",
#         type=["jpg", "png", "jpeg"],
#         accept_multiple_files=True
#     )

#     if st.button(
#         "Run Batch Process",
#         type="primary",
#         disabled=not t1_files
#     ):
#         all_paths = []
#         progress = st.progress(0)

#         for i, file in enumerate(t1_files):
#             in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
#             with open(in_path, "wb") as f:
#                 f.write(file.getbuffer())

#             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
#             shutil.rmtree(out_dir, ignore_errors=True)
#             os.makedirs(out_dir, exist_ok=True)

#             remix_images(
#                 image_paths=[in_path],
#                 prompt=t1_prompt,
#                 MODEL_NAME=model_choice,
#                 output_dir=out_dir
#             )

#             results = sorted(glob.glob(os.path.join(out_dir, "*")))
#             if results:
#                 result_path = results[0]
#                 all_paths.append(result_path)

#                 col_a, col_b = st.columns(2)
#                 col_a.image(file, caption="Original")
#                 col_b.image(result_path, caption=f"Result {i + 1}")

#                 with open(result_path, "rb") as f:
#                     col_b.download_button(
#                         "Download",
#                         f,
#                         file_name=f"batch_{i}.png",
#                         key=f"t1_dl_{i}"
#                     )

#             progress.progress((i + 1) / len(t1_files))

#         if all_paths:
#             st.divider()
#             st.download_button(
#                 "📦 Download All Results (ZIP)",
#                 create_zip(all_paths),
#                 "batch_results.zip"
#             )

# # ==========================================================
# # TAB 2 — MULTI PROMPT (FIXED)
# # ==========================================================
# with tab2:
#     st.markdown("Process **one image** using **multiple independent prompts**.")

#     t2_file = st.file_uploader(
#         "Upload One Image",
#         type=["jpg", "png", "jpeg"]
#     )

#     st.subheader("Prompts")

#     # Prompt inputs
#     for i, prompt in enumerate(st.session_state.prompts):
#         cols = st.columns([8, 1])
#         st.session_state.prompts[i] = cols[0].text_input(
#             f"Prompt {i + 1}",
#             value=prompt,
#             key=f"prompt_{i}"
#         )
#         if cols[1].button("❌", key=f"remove_{i}"):
#             st.session_state.prompts.pop(i)
#             st.rerun()

#     if st.button("➕ Add Prompt"):
#         st.session_state.prompts.append("")
#         st.rerun()

#     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

#     if st.button(
#         "Run Multi-Prompt Process",
#         type="primary",
#         disabled=not t2_file or not prompt_list
#     ):
#         all_paths = []
#         progress = st.progress(0)

#         # IMPORTANT: keep original bytes immutable
#         original_bytes = t2_file.getbuffer()

#         for i, prompt in enumerate(prompt_list):
#             st.write(f"Running Prompt {i + 1}: *{prompt}*")

#             # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
#             in_path = os.path.join(
#                 TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
#             )
#             with open(in_path, "wb") as f:
#                 f.write(original_bytes)

#             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
#             shutil.rmtree(out_dir, ignore_errors=True)
#             os.makedirs(out_dir, exist_ok=True)

#             remix_images(
#                 image_paths=[in_path],
#                 prompt=prompt,
#                 MODEL_NAME=model_choice,
#                 output_dir=out_dir
#             )

#             results = sorted(glob.glob(os.path.join(out_dir, "*")))
#             if results:
#                 result_path = results[0]
#                 all_paths.append(result_path)

#                 col_a, col_b = st.columns(2)
#                 col_a.image(t2_file, caption="Original")
#                 col_b.image(result_path, caption=prompt)

#                 with open(result_path, "rb") as f:
#                     col_b.download_button(
#                         "Download",
#                         f,
#                         file_name=f"prompt_{i}.png",
#                         key=f"t2_dl_{i}"
#                     )

#             progress.progress((i + 1) / len(prompt_list))

#         if all_paths:
#             st.divider()
#             st.download_button(
#                 "📦 Download All Variations (ZIP)",
#                 create_zip(all_paths),
#                 "variations.zip"
#             )
###########################################################################
import streamlit as st
import os
import glob
import zipfile
import io
import shutil
from src.with_image import remix_images

# =========================
# SETUP
# =========================
st.set_page_config(
    page_title="Gemini Remixer Pro",
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

    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

    st.session_state.api_key = st.text_input(
        "API Key (Optional override)",
        type="password",
        value=st.session_state.api_key
    )


    model_choice = st.selectbox(
        "Model",
        [
            "gemini-3-pro-image-preview",
            "gemini-2.5-flash-image"
        ],
        index=0
    )

# =========================
# MAIN UI
# =========================
st.title("⚡ Gemini Image Remixer")

tab1, tab2 = st.tabs(
    ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)"]
)

# ==========================================================
# TAB 1 — BATCH IMAGES
# ==========================================================
with tab1:
    st.markdown("Process **multiple images** using the **same prompt**.")

    t1_prompt = st.text_area(
        "Prompt",
        value="Studio lighting, professional photography"
    )

    t1_files = st.file_uploader(
        "Upload Images",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

    if st.button(
        "Run Batch Process",
        type="primary",
        disabled=not t1_files
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

            remix_images(
                image_paths=[in_path],
                prompt=t1_prompt,
                MODEL_NAME=model_choice,
                output_dir=out_dir,
                api_key=st.session_state.api_key
            )

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
                "batch_results.zip"
            )

# ==========================================================
# TAB 2 — MULTI PROMPT (FIXED)
# ==========================================================
with tab2:
    st.markdown("Process **one image** using **multiple independent prompts**.")

    t2_file = st.file_uploader(
        "Upload One Image",
        type=["jpg", "png", "jpeg"]
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

    if st.button("➕ Add Prompt"):
        st.session_state.prompts.append("")
        st.rerun()

    prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

    if st.button(
        "Run Multi-Prompt Process",
        type="primary",
        disabled=not t2_file or not prompt_list
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

            remix_images(
                image_paths=[in_path],
                prompt=prompt,
                MODEL_NAME=model_choice,
                output_dir=out_dir,
                api_key=st.session_state.api_key
            )

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
                "variations.zip"
            )

