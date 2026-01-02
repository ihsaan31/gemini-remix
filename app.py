# import streamlit as st
# import os
# import shutil
# import glob
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

#     for i, uploaded_file in enumerate(uploaded_files):
#         # 1. Update Status
#         status_area.info(f"Processing {i+1}/{total}: **{uploaded_file.name}**...")
        
#         # 2. Save Uploaded File to Disk (Your function needs a path)
#         # We create a specific subfolder for input to avoid name collisions
#         current_input_path = os.path.join(TEMP_INPUT_DIR, uploaded_file.name)
#         with open(current_input_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         # 3. Create a unique output subfolder for this specific image
#         # This ensures we know exactly which output image belongs to this input
#         current_output_dir = os.path.join(TEMP_OUTPUT_DIR, f"result_{i}")
#         os.makedirs(current_output_dir, exist_ok=True)

#         try:
#             # 4. CALL YOUR IMPORTED FUNCTION
#             # We pass the list of 1 image path to execute them synchronously
#             remix_images(
#                 image_paths=[current_input_path],
#                 prompt=prompt,
#                 MODEL_NAME=model_choice,
#                 output_dir=current_output_dir
#             )

#             # 5. Find the generated file in that specific output folder
#             generated_files = glob.glob(os.path.join(current_output_dir, "*"))
            
#             # 6. Display Result
#             with results_container:
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.image(uploaded_file, caption=f"Original: {uploaded_file.name}", use_container_width=True)
#                 with col2:
#                     if generated_files:
#                         st.image(generated_files[0], caption="Generated Result", use_container_width=True)
#                     else:
#                         st.error("No output file was created.")
#                 st.divider()

#         except Exception as e:
#             st.error(f"Error processing {uploaded_file.name}: {e}")

#         # Update Progress
#         progress_bar.progress((i + 1) / total)

#     status_area.success("All images processed successfully!")

#     # Optional: Cleanup input temp files after run
#     # shutil.rmtree(TEMP_INPUT_DIR)

import streamlit as st
import os
import shutil
import glob
import zipfile
import io
from src.with_image import remix_images  # Importing your function directly

# =========================
# SETUP
# =========================
st.set_page_config(page_title="Gemini Batch Remixer", layout="wide")

# temporary folders to handle file passing
TEMP_INPUT_DIR = "temp_streamlit_input"
TEMP_OUTPUT_DIR = "temp_streamlit_output"

os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# =========================
# UI LAYOUT
# =========================
st.title("⚡ Gemini Batch Image Remixer")
st.markdown("Upload multiple images. They will be processed **one by one** using your existing script.")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Allow API Key override, otherwise use env var inside your script
    api_key_input = st.text_input("API Key (Optional override)", type="password")
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
    
    model_choice = st.selectbox(
        "Model", 
        ["gemini-3-pro-image-preview", "gemini-2.5-flash-image-preview"],
        index=0
    )

# Main Inputs
prompt = st.text_area(
    "Prompt", 
    value="Turn this image into a professional quality studio shoot with better lighting and depth of field.",
    height=100
)

uploaded_files = st.file_uploader(
    "Upload Images", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

run_btn = st.button("Start Processing", type="primary", disabled=not uploaded_files)

# =========================
# PROCESSING LOGIC
# =========================
if run_btn and uploaded_files:
    st.divider()
    progress_bar = st.progress(0)
    status_area = st.empty()
    results_container = st.container()

    # Clear previous temp outputs to avoid confusion
    if os.path.exists(TEMP_OUTPUT_DIR):
        shutil.rmtree(TEMP_OUTPUT_DIR)
    os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

    total = len(uploaded_files)
    all_generated_paths = [] # Keep track for the ZIP file later

    for i, uploaded_file in enumerate(uploaded_files):
        # 1. Update Status
        status_area.info(f"Processing {i+1}/{total}: **{uploaded_file.name}**...")
        
        # 2. Save Uploaded File to Disk
        current_input_path = os.path.join(TEMP_INPUT_DIR, uploaded_file.name)
        with open(current_input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 3. Create a unique output subfolder
        current_output_dir = os.path.join(TEMP_OUTPUT_DIR, f"result_{i}")
        os.makedirs(current_output_dir, exist_ok=True)

        try:
            # 4. CALL YOUR IMPORTED FUNCTION
            remix_images(
                image_paths=[current_input_path],
                prompt=prompt,
                MODEL_NAME=model_choice,
                output_dir=current_output_dir
            )

            # 5. Find the generated file
            generated_files = glob.glob(os.path.join(current_output_dir, "*"))
            
            # 6. Display Result
            with results_container:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(uploaded_file, caption=f"Original: {uploaded_file.name}", use_container_width=True)
                with col2:
                    if generated_files:
                        gen_path = generated_files[0]
                        all_generated_paths.append(gen_path)
                        
                        st.image(gen_path, caption="Generated Result", use_container_width=True)
                        
                        # --- INDIVIDUAL DOWNLOAD BUTTON ---
                        with open(gen_path, "rb") as file:
                            btn = st.download_button(
                                label="⬇️ Download Image",
                                data=file,
                                file_name=f"remixed_{uploaded_file.name}",
                                mime="image/png",
                                key=f"dl_btn_{i}" # Unique key is required inside loops
                            )
                    else:
                        st.error("No output file was created.")
                st.divider()

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

        # Update Progress
        progress_bar.progress((i + 1) / total)

    status_area.success("All images processed successfully!")

    # =========================
    # BULK DOWNLOAD (ZIP)
    # =========================
    if all_generated_paths:
        # Create an in-memory zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for file_path in all_generated_paths:
                # Add file to zip, arcname ensures it has a clean name inside the zip
                file_name = os.path.basename(file_path)
                zf.write(file_path, arcname=file_name)
        
        # Reset pointer to beginning of buffer
        zip_buffer.seek(0)

        st.download_button(
            label="📦 Download All Images (ZIP)",
            data=zip_buffer,
            file_name="all_remixed_images.zip",
            mime="application/zip"
        )