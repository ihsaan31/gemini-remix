# # # # # import streamlit as st
# # # # # import os
# # # # # import shutil
# # # # # import glob
# # # # # import zipfile
# # # # # import io
# # # # # from src.with_image import remix_images  # Importing your function directly

# # # # # # =========================
# # # # # # SETUP
# # # # # # =========================
# # # # # st.set_page_config(page_title="Gemini Batch Remixer", layout="wide")

# # # # # # temporary folders to handle file passing
# # # # # TEMP_INPUT_DIR = "temp_streamlit_input"
# # # # # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # # # # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # # # # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # # # =========================
# # # # # # UI LAYOUT
# # # # # # =========================
# # # # # st.title("⚡ Gemini Batch Image Remixer")
# # # # # st.markdown("Upload multiple images. They will be processed **one by one** using your existing script.")

# # # # # # Sidebar configuration
# # # # # with st.sidebar:
# # # # #     st.header("Configuration")
    
# # # # #     # Allow API Key override, otherwise use env var inside your script
# # # # #     api_key_input = st.text_input("API Key (Optional override)", type="password")
# # # # #     if api_key_input:
# # # # #         os.environ["GEMINI_API_KEY"] = api_key_input
    
# # # # #     model_choice = st.selectbox(
# # # # #         "Model", 
# # # # #         ["gemini-3-pro-image-preview", "gemini-2.5-flash-image-preview"],
# # # # #         index=0
# # # # #     )

# # # # # # Main Inputs
# # # # # prompt = st.text_area(
# # # # #     "Prompt", 
# # # # #     value="Turn this image into a professional quality studio shoot with better lighting and depth of field.",
# # # # #     height=100
# # # # # )

# # # # # uploaded_files = st.file_uploader(
# # # # #     "Upload Images", 
# # # # #     type=["jpg", "jpeg", "png", "webp"], 
# # # # #     accept_multiple_files=True
# # # # # )

# # # # # run_btn = st.button("Start Processing", type="primary", disabled=not uploaded_files)

# # # # # # =========================
# # # # # # PROCESSING LOGIC
# # # # # # =========================
# # # # # if run_btn and uploaded_files:
# # # # #     st.divider()
# # # # #     progress_bar = st.progress(0)
# # # # #     status_area = st.empty()
# # # # #     results_container = st.container()

# # # # #     # Clear previous temp outputs to avoid confusion
# # # # #     if os.path.exists(TEMP_OUTPUT_DIR):
# # # # #         shutil.rmtree(TEMP_OUTPUT_DIR)
# # # # #     os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # #     total = len(uploaded_files)
# # # # #     all_generated_paths = [] # Keep track for the ZIP file later

# # # # #     for i, uploaded_file in enumerate(uploaded_files):
# # # # #         # 1. Update Status
# # # # #         status_area.info(f"Processing {i+1}/{total}: **{uploaded_file.name}**...")
        
# # # # #         # 2. Save Uploaded File to Disk
# # # # #         current_input_path = os.path.join(TEMP_INPUT_DIR, uploaded_file.name)
# # # # #         with open(current_input_path, "wb") as f:
# # # # #             f.write(uploaded_file.getbuffer())

# # # # #         # 3. Create a unique output subfolder
# # # # #         current_output_dir = os.path.join(TEMP_OUTPUT_DIR, f"result_{i}")
# # # # #         os.makedirs(current_output_dir, exist_ok=True)

# # # # #         try:
# # # # #             # 4. CALL YOUR IMPORTED FUNCTION
# # # # #             remix_images(
# # # # #                 image_paths=[current_input_path],
# # # # #                 prompt=prompt,
# # # # #                 MODEL_NAME=model_choice,
# # # # #                 output_dir=current_output_dir
# # # # #             )

# # # # #             # 5. Find the generated file
# # # # #             generated_files = glob.glob(os.path.join(current_output_dir, "*"))
            
# # # # #             # 6. Display Result
# # # # #             with results_container:
# # # # #                 col1, col2 = st.columns(2)
# # # # #                 with col1:
# # # # #                     st.image(uploaded_file, caption=f"Original: {uploaded_file.name}", use_container_width=True)
# # # # #                 with col2:
# # # # #                     if generated_files:
# # # # #                         gen_path = generated_files[0]
# # # # #                         all_generated_paths.append(gen_path)
                        
# # # # #                         st.image(gen_path, caption="Generated Result", use_container_width=True)
                        
# # # # #                         # --- INDIVIDUAL DOWNLOAD BUTTON ---
# # # # #                         with open(gen_path, "rb") as file:
# # # # #                             btn = st.download_button(
# # # # #                                 label="⬇️ Download Image",
# # # # #                                 data=file,
# # # # #                                 file_name=f"remixed_{uploaded_file.name}",
# # # # #                                 mime="image/png",
# # # # #                                 key=f"dl_btn_{i}" # Unique key is required inside loops
# # # # #                             )
# # # # #                     else:
# # # # #                         st.error("No output file was created.")
# # # # #                 st.divider()

# # # # #         except Exception as e:
# # # # #             st.error(f"Error processing {uploaded_file.name}: {e}")

# # # # #         # Update Progress
# # # # #         progress_bar.progress((i + 1) / total)

# # # # #     status_area.success("All images processed successfully!")

# # # # #     # =========================
# # # # #     # BULK DOWNLOAD (ZIP)
# # # # #     # =========================
# # # # #     if all_generated_paths:
# # # # #         # Create an in-memory zip file
# # # # #         zip_buffer = io.BytesIO()
# # # # #         with zipfile.ZipFile(zip_buffer, "w") as zf:
# # # # #             for file_path in all_generated_paths:
# # # # #                 # Add file to zip, arcname ensures it has a clean name inside the zip
# # # # #                 file_name = os.path.basename(file_path)
# # # # #                 zf.write(file_path, arcname=file_name)
        
# # # # #         # Reset pointer to beginning of buffer
# # # # #         zip_buffer.seek(0)

# # # # #         st.download_button(
# # # # #             label="📦 Download All Images (ZIP)",
# # # # #             data=zip_buffer,
# # # # #             file_name="all_remixed_images.zip",
# # # # #             mime="application/zip"
# # # # #         )
# # # # ####################################################################################################################################
# # # # # import streamlit as st
# # # # # import os
# # # # # import shutil
# # # # # import glob
# # # # # import zipfile
# # # # # import io
# # # # # from src.with_image import remix_images  # Importing your function directly

# # # # # # =========================
# # # # # # SETUP
# # # # # # =========================
# # # # # st.set_page_config(page_title="Gemini Remixer Pro", layout="wide")

# # # # # TEMP_INPUT_DIR = "temp_streamlit_input"
# # # # # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # # # # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # # # # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # # # Helper function to create ZIP
# # # # # def create_zip(paths):
# # # # #     zip_buffer = io.BytesIO()
# # # # #     with zipfile.ZipFile(zip_buffer, "w") as zf:
# # # # #         for file_path in paths:
# # # # #             zf.write(file_path, arcname=os.path.basename(file_path))
# # # # #     zip_buffer.seek(0)
# # # # #     return zip_buffer

# # # # # # =========================
# # # # # # SIDEBAR
# # # # # # =========================
# # # # # with st.sidebar:
# # # # #     st.header("Settings")
# # # # #     api_key_input = st.text_input("API Key (Optional override)", type="password")
# # # # #     if api_key_input:
# # # # #         os.environ["GEMINI_API_KEY"] = api_key_input
    
# # # # #     model_choice = st.selectbox(
# # # # #         "Model", 
# # # # #         ["gemini-3-pro-image-preview", "gemini-2.5-flash-image-preview"],
# # # # #         index=0
# # # # #     )

# # # # # # =========================
# # # # # # MAIN UI
# # # # # # =========================
# # # # # st.title("⚡ Gemini Image Remixer")

# # # # # tab1, tab2 = st.tabs(["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)"])

# # # # # # -------------------------
# # # # # # TAB 1: BATCH IMAGES
# # # # # # -------------------------
# # # # # with tab1:
# # # # #     st.markdown("Process many images using the **same** prompt.")
# # # # #     t1_prompt = st.text_area("Prompt", value="Studio lighting, professional photography", key="t1_p")
# # # # #     t1_files = st.file_uploader("Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="t1_f")
    
# # # # #     if st.button("Run Batch Process", type="primary", disabled=not t1_files):
# # # # #         all_paths = []
# # # # #         progress = st.progress(0)
        
# # # # #         for i, file in enumerate(t1_files):
# # # # #             in_path = os.path.join(TEMP_INPUT_DIR, file.name)
# # # # #             with open(in_path, "wb") as f:
# # # # #                 f.write(file.getbuffer())
            
# # # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
# # # # #             os.makedirs(out_dir, exist_ok=True)
            
# # # # #             remix_images(image_paths=[in_path], prompt=t1_prompt, MODEL_NAME=model_choice, output_dir=out_dir)
            
# # # # #             res = glob.glob(os.path.join(out_dir, "*"))
# # # # #             if res:
# # # # #                 all_paths.append(res[0])
# # # # #                 col_a, col_b = st.columns(2)
# # # # #                 col_a.image(file, caption="Original")
# # # # #                 col_b.image(res[0], caption=f"Result {i+1}")
# # # # #                 with col_b:
# # # # #                     with open(res[0], "rb") as f:
# # # # #                         st.download_button("Download", f, file_name=f"res_{i}.png", key=f"t1_dl_{i}")
            
# # # # #             progress.progress((i + 1) / len(t1_files))
        
# # # # #         if all_paths:
# # # # #             st.download_button("📦 Download All (ZIP)", create_zip(all_paths), "batch_results.zip")

# # # # # # -------------------------
# # # # # # TAB 2: MULTI-PROMPT
# # # # # # -------------------------
# # # # # with tab2:
# # # # #     st.markdown("Process **one image** using **multiple different prompts**.")
# # # # #     t2_file = st.file_uploader("Upload One Image", type=["jpg", "png", "jpeg"], key="t2_f")
# # # # #     t2_prompts_raw = st.text_area("Prompts (One per line)", value="Cyberpunk style\nOil painting style\nSketch drawing", height=150)
    
# # # # #     # Convert text area lines to a list of prompts
# # # # #     prompt_list = [p.strip() for p in t2_prompts_raw.split("\n") if p.strip()]

# # # # #     if st.button("Run Multi-Prompt Process", type="primary", disabled=not t2_file or not prompt_list):
# # # # #         all_paths = []
        
# # # # #         # Save the single image
# # # # #         in_path = os.path.join(TEMP_INPUT_DIR, "single_source.png")
# # # # #         with open(in_path, "wb") as f:
# # # # #             f.write(t2_file.getbuffer())
            
# # # # #         progress = st.progress(0)
        
# # # # #         for i, p in enumerate(prompt_list):
# # # # #             st.write(f"Running Prompt {i+1}: *{p}*")
# # # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
# # # # #             os.makedirs(out_dir, exist_ok=True)
            
# # # # #             remix_images(image_paths=[in_path], prompt=p, MODEL_NAME=model_choice, output_dir=out_dir)
            
# # # # #             res = glob.glob(os.path.join(out_dir, "*"))
# # # # #             if res:
# # # # #                 all_paths.append(res[0])
# # # # #                 col_a, col_b = st.columns(2)
# # # # #                 col_a.image(t2_file, caption="Original Source")
# # # # #                 col_b.image(res[0], caption=f"Prompt: {p}")
# # # # #                 with col_b:
# # # # #                     with open(res[0], "rb") as f:
# # # # #                         st.download_button("Download", f, file_name=f"prompt_{i}.png", key=f"t2_dl_{i}")
            
# # # # #             progress.progress((i + 1) / len(prompt_list))

# # # # #         if all_paths:
# # # # #             st.divider()
# # # # #             st.download_button("📦 Download All Variations (ZIP)", create_zip(all_paths), "variations.zip")
# # # # ######################################################################################################################################
# # # # # import streamlit as st
# # # # # import os
# # # # # import glob
# # # # # import zipfile
# # # # # import io
# # # # # import shutil
# # # # # from src.with_image import remix_images

# # # # # # =========================
# # # # # # SETUP
# # # # # # =========================
# # # # # st.set_page_config(
# # # # #     page_title="Gemini Remixer Pro",
# # # # #     layout="wide"
# # # # # )

# # # # # TEMP_INPUT_DIR = "temp_streamlit_input"
# # # # # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # # # # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # # # # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # # # =========================
# # # # # # HELPERS
# # # # # # =========================
# # # # # def create_zip(paths):
# # # # #     zip_buffer = io.BytesIO()
# # # # #     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
# # # # #         for file_path in paths:
# # # # #             zf.write(file_path, arcname=os.path.basename(file_path))
# # # # #     zip_buffer.seek(0)
# # # # #     return zip_buffer

# # # # # # =========================
# # # # # # SESSION STATE
# # # # # # =========================
# # # # # if "prompts" not in st.session_state:
# # # # #     st.session_state.prompts = ["Cyberpunk style"]

# # # # # # =========================
# # # # # # SIDEBAR
# # # # # # =========================
# # # # # with st.sidebar:
# # # # #     st.header("Settings")

# # # # #     api_key_input = st.text_input(
# # # # #         "API Key (Optional override)",
# # # # #         type="password"
# # # # #     )
# # # # #     # if api_key_input:
# # # # #     #     os.environ["GEMINI_API_KEY"] = api_key_input

# # # # #     model_choice = st.selectbox(
# # # # #         "Model",
# # # # #         [
# # # # #             "gemini-3-pro-image-preview",
# # # # #             "gemini-2.5-flash-image"
# # # # #         ],
# # # # #         index=0
# # # # #     )

# # # # # # =========================
# # # # # # MAIN UI
# # # # # # =========================
# # # # # st.title("⚡ Gemini Image Remixer")

# # # # # tab1, tab2 = st.tabs(
# # # # #     ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)"]
# # # # # )

# # # # # # ==========================================================
# # # # # # TAB 1 — BATCH IMAGES
# # # # # # ==========================================================
# # # # # with tab1:
# # # # #     st.markdown("Process **multiple images** using the **same prompt**.")

# # # # #     t1_prompt = st.text_area(
# # # # #         "Prompt",
# # # # #         value="Studio lighting, professional photography"
# # # # #     )

# # # # #     t1_files = st.file_uploader(
# # # # #         "Upload Images",
# # # # #         type=["jpg", "png", "jpeg"],
# # # # #         accept_multiple_files=True
# # # # #     )

# # # # #     if st.button(
# # # # #         "Run Batch Process",
# # # # #         type="primary",
# # # # #         disabled=not t1_files
# # # # #     ):
# # # # #         all_paths = []
# # # # #         progress = st.progress(0)

# # # # #         for i, file in enumerate(t1_files):
# # # # #             in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
# # # # #             with open(in_path, "wb") as f:
# # # # #                 f.write(file.getbuffer())

# # # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
# # # # #             shutil.rmtree(out_dir, ignore_errors=True)
# # # # #             os.makedirs(out_dir, exist_ok=True)

# # # # #             remix_images(
# # # # #                 image_paths=[in_path],
# # # # #                 prompt=t1_prompt,
# # # # #                 MODEL_NAME=model_choice,
# # # # #                 output_dir=out_dir
# # # # #             )

# # # # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # # #             if results:
# # # # #                 result_path = results[0]
# # # # #                 all_paths.append(result_path)

# # # # #                 col_a, col_b = st.columns(2)
# # # # #                 col_a.image(file, caption="Original")
# # # # #                 col_b.image(result_path, caption=f"Result {i + 1}")

# # # # #                 with open(result_path, "rb") as f:
# # # # #                     col_b.download_button(
# # # # #                         "Download",
# # # # #                         f,
# # # # #                         file_name=f"batch_{i}.png",
# # # # #                         key=f"t1_dl_{i}"
# # # # #                     )

# # # # #             progress.progress((i + 1) / len(t1_files))

# # # # #         if all_paths:
# # # # #             st.divider()
# # # # #             st.download_button(
# # # # #                 "📦 Download All Results (ZIP)",
# # # # #                 create_zip(all_paths),
# # # # #                 "batch_results.zip"
# # # # #             )

# # # # # # ==========================================================
# # # # # # TAB 2 — MULTI PROMPT (FIXED)
# # # # # # ==========================================================
# # # # # with tab2:
# # # # #     st.markdown("Process **one image** using **multiple independent prompts**.")

# # # # #     t2_file = st.file_uploader(
# # # # #         "Upload One Image",
# # # # #         type=["jpg", "png", "jpeg"]
# # # # #     )

# # # # #     st.subheader("Prompts")

# # # # #     # Prompt inputs
# # # # #     for i, prompt in enumerate(st.session_state.prompts):
# # # # #         cols = st.columns([8, 1])
# # # # #         st.session_state.prompts[i] = cols[0].text_input(
# # # # #             f"Prompt {i + 1}",
# # # # #             value=prompt,
# # # # #             key=f"prompt_{i}"
# # # # #         )
# # # # #         if cols[1].button("❌", key=f"remove_{i}"):
# # # # #             st.session_state.prompts.pop(i)
# # # # #             st.rerun()

# # # # #     if st.button("➕ Add Prompt"):
# # # # #         st.session_state.prompts.append("")
# # # # #         st.rerun()

# # # # #     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

# # # # #     if st.button(
# # # # #         "Run Multi-Prompt Process",
# # # # #         type="primary",
# # # # #         disabled=not t2_file or not prompt_list
# # # # #     ):
# # # # #         all_paths = []
# # # # #         progress = st.progress(0)

# # # # #         # IMPORTANT: keep original bytes immutable
# # # # #         original_bytes = t2_file.getbuffer()

# # # # #         for i, prompt in enumerate(prompt_list):
# # # # #             st.write(f"Running Prompt {i + 1}: *{prompt}*")

# # # # #             # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
# # # # #             in_path = os.path.join(
# # # # #                 TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
# # # # #             )
# # # # #             with open(in_path, "wb") as f:
# # # # #                 f.write(original_bytes)

# # # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
# # # # #             shutil.rmtree(out_dir, ignore_errors=True)
# # # # #             os.makedirs(out_dir, exist_ok=True)

# # # # #             remix_images(
# # # # #                 image_paths=[in_path],
# # # # #                 prompt=prompt,
# # # # #                 MODEL_NAME=model_choice,
# # # # #                 output_dir=out_dir
# # # # #             )

# # # # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # # #             if results:
# # # # #                 result_path = results[0]
# # # # #                 all_paths.append(result_path)

# # # # #                 col_a, col_b = st.columns(2)
# # # # #                 col_a.image(t2_file, caption="Original")
# # # # #                 col_b.image(result_path, caption=prompt)

# # # # #                 with open(result_path, "rb") as f:
# # # # #                     col_b.download_button(
# # # # #                         "Download",
# # # # #                         f,
# # # # #                         file_name=f"prompt_{i}.png",
# # # # #                         key=f"t2_dl_{i}"
# # # # #                     )

# # # # #             progress.progress((i + 1) / len(prompt_list))

# # # # #         if all_paths:
# # # # #             st.divider()
# # # # #             st.download_button(
# # # # #                 "📦 Download All Variations (ZIP)",
# # # # #                 create_zip(all_paths),
# # # # #                 "variations.zip"
# # # # #             )
# # # # ###########################################################################
# # # # # import streamlit as st
# # # # # import os
# # # # # import glob
# # # # # import zipfile
# # # # # import io
# # # # # import shutil
# # # # # from src.with_image import remix_images

# # # # # # =========================
# # # # # # SETUP
# # # # # # =========================
# # # # # st.set_page_config(
# # # # #     page_title="Gemini Remixer Pro",
# # # # #     layout="wide"
# # # # # )

# # # # # TEMP_INPUT_DIR = "temp_streamlit_input"
# # # # # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # # # # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # # # # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # # # =========================
# # # # # # HELPERS
# # # # # # =========================
# # # # # def create_zip(paths):
# # # # #     zip_buffer = io.BytesIO()
# # # # #     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
# # # # #         for file_path in paths:
# # # # #             zf.write(file_path, arcname=os.path.basename(file_path))
# # # # #     zip_buffer.seek(0)
# # # # #     return zip_buffer

# # # # # # =========================
# # # # # # SESSION STATE
# # # # # # =========================
# # # # # if "prompts" not in st.session_state:
# # # # #     st.session_state.prompts = ["Cyberpunk style"]

# # # # # # =========================
# # # # # # SIDEBAR
# # # # # # =========================
# # # # # with st.sidebar:
# # # # #     st.header("Settings")

# # # # #     if "api_key" not in st.session_state:
# # # # #         st.session_state.api_key = ""

# # # # #     st.session_state.api_key = st.text_input(
# # # # #         "API Key (Optional override)",
# # # # #         type="password",
# # # # #         value=st.session_state.api_key
# # # # #     )


# # # # #     model_choice = st.selectbox(
# # # # #         "Model",
# # # # #         [   
# # # # #             "gemini-3.1-flash-image-preview",
# # # # #             "gemini-3-pro-image-preview",
# # # # #             "gemini-2.5-flash-image",
            
# # # # #         ],
# # # # #         index=0
# # # # #     )

# # # # # # =========================
# # # # # # MAIN UI
# # # # # # =========================
# # # # # st.title("⚡ Gemini Image Remixer")

# # # # # tab1, tab2 = st.tabs(
# # # # #     ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)"]
# # # # # )

# # # # # # ==========================================================
# # # # # # TAB 1 — BATCH IMAGES
# # # # # # ==========================================================
# # # # # with tab1:
# # # # #     st.markdown("Process **multiple images** using the **same prompt**.")

# # # # #     t1_prompt = st.text_area(
# # # # #         "Prompt",
# # # # #         value="Studio lighting, professional photography"
# # # # #     )

# # # # #     t1_files = st.file_uploader(
# # # # #         "Upload Images",
# # # # #         type=["jpg", "png", "jpeg"],
# # # # #         accept_multiple_files=True
# # # # #     )

# # # # #     if st.button(
# # # # #         "Run Batch Process",
# # # # #         type="primary",
# # # # #         disabled=not t1_files
# # # # #     ):
# # # # #         all_paths = []
# # # # #         progress = st.progress(0)

# # # # #         for i, file in enumerate(t1_files):
# # # # #             in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
# # # # #             with open(in_path, "wb") as f:
# # # # #                 f.write(file.getbuffer())

# # # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
# # # # #             shutil.rmtree(out_dir, ignore_errors=True)
# # # # #             os.makedirs(out_dir, exist_ok=True)

# # # # #             remix_images(
# # # # #                 image_paths=[in_path],
# # # # #                 prompt=t1_prompt,
# # # # #                 MODEL_NAME=model_choice,
# # # # #                 output_dir=out_dir,
# # # # #                 api_key=st.session_state.api_key
# # # # #             )

# # # # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # # #             if results:
# # # # #                 result_path = results[0]
# # # # #                 all_paths.append(result_path)

# # # # #                 col_a, col_b = st.columns(2)
# # # # #                 col_a.image(file, caption="Original")
# # # # #                 col_b.image(result_path, caption=f"Result {i + 1}")

# # # # #                 with open(result_path, "rb") as f:
# # # # #                     col_b.download_button(
# # # # #                         "Download",
# # # # #                         f,
# # # # #                         file_name=f"batch_{i}.png",
# # # # #                         key=f"t1_dl_{i}"
# # # # #                     )

# # # # #             progress.progress((i + 1) / len(t1_files))

# # # # #         if all_paths:
# # # # #             st.divider()
# # # # #             st.download_button(
# # # # #                 "📦 Download All Results (ZIP)",
# # # # #                 create_zip(all_paths),
# # # # #                 "batch_results.zip"
# # # # #             )

# # # # # # ==========================================================
# # # # # # TAB 2 — MULTI PROMPT (FIXED)
# # # # # # ==========================================================
# # # # # with tab2:
# # # # #     st.markdown("Process **one image** using **multiple independent prompts**.")

# # # # #     t2_file = st.file_uploader(
# # # # #         "Upload One Image",
# # # # #         type=["jpg", "png", "jpeg"]
# # # # #     )

# # # # #     st.subheader("Prompts")

# # # # #     # Prompt inputs
# # # # #     for i, prompt in enumerate(st.session_state.prompts):
# # # # #         cols = st.columns([8, 1])
# # # # #         st.session_state.prompts[i] = cols[0].text_input(
# # # # #             f"Prompt {i + 1}",
# # # # #             value=prompt,
# # # # #             key=f"prompt_{i}"
# # # # #         )
# # # # #         if cols[1].button("❌", key=f"remove_{i}"):
# # # # #             st.session_state.prompts.pop(i)
# # # # #             st.rerun()

# # # # #     if st.button("➕ Add Prompt"):
# # # # #         st.session_state.prompts.append("")
# # # # #         st.rerun()

# # # # #     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

# # # # #     if st.button(
# # # # #         "Run Multi-Prompt Process",
# # # # #         type="primary",
# # # # #         disabled=not t2_file or not prompt_list
# # # # #     ):
# # # # #         all_paths = []
# # # # #         progress = st.progress(0)

# # # # #         # IMPORTANT: keep original bytes immutable
# # # # #         original_bytes = t2_file.getbuffer()

# # # # #         for i, prompt in enumerate(prompt_list):
# # # # #             st.write(f"Running Prompt {i + 1}: *{prompt}*")

# # # # #             # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
# # # # #             in_path = os.path.join(
# # # # #                 TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
# # # # #             )
# # # # #             with open(in_path, "wb") as f:
# # # # #                 f.write(original_bytes)

# # # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
# # # # #             shutil.rmtree(out_dir, ignore_errors=True)
# # # # #             os.makedirs(out_dir, exist_ok=True)

# # # # #             remix_images(
# # # # #                 image_paths=[in_path],
# # # # #                 prompt=prompt,
# # # # #                 MODEL_NAME=model_choice,
# # # # #                 output_dir=out_dir,
# # # # #                 api_key=st.session_state.api_key
# # # # #             )

# # # # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # # #             if results:
# # # # #                 result_path = results[0]
# # # # #                 all_paths.append(result_path)

# # # # #                 col_a, col_b = st.columns(2)
# # # # #                 col_a.image(t2_file, caption="Original")
# # # # #                 col_b.image(result_path, caption=prompt)

# # # # #                 with open(result_path, "rb") as f:
# # # # #                     col_b.download_button(
# # # # #                         "Download",
# # # # #                         f,
# # # # #                         file_name=f"prompt_{i}.png",
# # # # #                         key=f"t2_dl_{i}"
# # # # #                     )

# # # # #             progress.progress((i + 1) / len(prompt_list))

# # # # #         if all_paths:
# # # # #             st.divider()
# # # # #             st.download_button(
# # # # #                 "📦 Download All Variations (ZIP)",
# # # # #                 create_zip(all_paths),
# # # # #                 "variations.zip"
# # # # #             )


# # # # #####################################################################################################################
# # # # import streamlit as st
# # # # import os
# # # # import glob
# # # # import zipfile
# # # # import io
# # # # import shutil
# # # # from src.with_image import remix_images

# # # # # =========================
# # # # # SETUP
# # # # # =========================
# # # # st.set_page_config(
# # # #     page_title="Gemini Remixer Pro",
# # # #     layout="wide"
# # # # )

# # # # TEMP_INPUT_DIR = "temp_streamlit_input"
# # # # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # # # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # # # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # # =========================
# # # # # HELPERS
# # # # # =========================
# # # # def create_zip(paths):
# # # #     zip_buffer = io.BytesIO()
# # # #     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
# # # #         for file_path in paths:
# # # #             zf.write(file_path, arcname=os.path.basename(file_path))
# # # #     zip_buffer.seek(0)
# # # #     return zip_buffer

# # # # # =========================
# # # # # SESSION STATE
# # # # # =========================
# # # # if "prompts" not in st.session_state:
# # # #     st.session_state.prompts = ["Cyberpunk style"]

# # # # # =========================
# # # # # SIDEBAR
# # # # # =========================
# # # # with st.sidebar:
# # # #     st.header("Settings")

# # # #     if "api_key" not in st.session_state:
# # # #         st.session_state.api_key = ""

# # # #     st.session_state.api_key = st.text_input(
# # # #         "API Key (Optional override)",
# # # #         type="password",
# # # #         value=st.session_state.api_key
# # # #     )

# # # #     model_choice = st.selectbox(
# # # #         "Model",
# # # #         [
# # # #             "gemini-3.1-flash-image-preview",
# # # #             "gemini-3-pro-image-preview",
# # # #             "gemini-2.5-flash-image",

# # # #         ],
# # # #         index=0
# # # #     )

# # # # # =========================
# # # # # MAIN UI
# # # # # =========================
# # # # st.title("⚡ Gemini Image Remixer")

# # # # tab1, tab2, tab3 = st.tabs(
# # # #     ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)", "🖼️ Multi-Image Blend (1 Prompt)"]
# # # # )

# # # # # ==========================================================
# # # # # TAB 1 — BATCH IMAGES
# # # # # ==========================================================
# # # # with tab1:
# # # #     st.markdown("Process **multiple images** using the **same prompt**.")

# # # #     t1_prompt = st.text_area(
# # # #         "Prompt",
# # # #         value="Studio lighting, professional photography"
# # # #     )

# # # #     t1_files = st.file_uploader(
# # # #         "Upload Images",
# # # #         type=["jpg", "png", "jpeg"],
# # # #         accept_multiple_files=True
# # # #     )

# # # #     if st.button(
# # # #         "Run Batch Process",
# # # #         type="primary",
# # # #         disabled=not t1_files
# # # #     ):
# # # #         all_paths = []
# # # #         progress = st.progress(0)

# # # #         for i, file in enumerate(t1_files):
# # # #             in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
# # # #             with open(in_path, "wb") as f:
# # # #                 f.write(file.getbuffer())

# # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
# # # #             shutil.rmtree(out_dir, ignore_errors=True)
# # # #             os.makedirs(out_dir, exist_ok=True)

# # # #             remix_images(
# # # #                 image_paths=[in_path],
# # # #                 prompt=t1_prompt,
# # # #                 MODEL_NAME=model_choice,
# # # #                 output_dir=out_dir,
# # # #                 api_key=st.session_state.api_key
# # # #             )

# # # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # #             if results:
# # # #                 result_path = results[0]
# # # #                 all_paths.append(result_path)

# # # #                 col_a, col_b = st.columns(2)
# # # #                 col_a.image(file, caption="Original")
# # # #                 col_b.image(result_path, caption=f"Result {i + 1}")

# # # #                 with open(result_path, "rb") as f:
# # # #                     col_b.download_button(
# # # #                         "Download",
# # # #                         f,
# # # #                         file_name=f"batch_{i}.png",
# # # #                         key=f"t1_dl_{i}"
# # # #                     )

# # # #             progress.progress((i + 1) / len(t1_files))

# # # #         if all_paths:
# # # #             st.divider()
# # # #             st.download_button(
# # # #                 "📦 Download All Results (ZIP)",
# # # #                 create_zip(all_paths),
# # # #                 "batch_results.zip"
# # # #             )

# # # # # ==========================================================
# # # # # TAB 2 — MULTI PROMPT (FIXED)
# # # # # ==========================================================
# # # # with tab2:
# # # #     st.markdown("Process **one image** using **multiple independent prompts**.")

# # # #     t2_file = st.file_uploader(
# # # #         "Upload One Image",
# # # #         type=["jpg", "png", "jpeg"]
# # # #     )

# # # #     st.subheader("Prompts")

# # # #     # Prompt inputs
# # # #     for i, prompt in enumerate(st.session_state.prompts):
# # # #         cols = st.columns([8, 1])
# # # #         st.session_state.prompts[i] = cols[0].text_input(
# # # #             f"Prompt {i + 1}",
# # # #             value=prompt,
# # # #             key=f"prompt_{i}"
# # # #         )
# # # #         if cols[1].button("❌", key=f"remove_{i}"):
# # # #             st.session_state.prompts.pop(i)
# # # #             st.rerun()

# # # #     if st.button("➕ Add Prompt"):
# # # #         st.session_state.prompts.append("")
# # # #         st.rerun()

# # # #     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

# # # #     if st.button(
# # # #         "Run Multi-Prompt Process",
# # # #         type="primary",
# # # #         disabled=not t2_file or not prompt_list
# # # #     ):
# # # #         all_paths = []
# # # #         progress = st.progress(0)

# # # #         # IMPORTANT: keep original bytes immutable
# # # #         original_bytes = t2_file.getbuffer()

# # # #         for i, prompt in enumerate(prompt_list):
# # # #             st.write(f"Running Prompt {i + 1}: *{prompt}*")

# # # #             # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
# # # #             in_path = os.path.join(
# # # #                 TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
# # # #             )
# # # #             with open(in_path, "wb") as f:
# # # #                 f.write(original_bytes)

# # # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
# # # #             shutil.rmtree(out_dir, ignore_errors=True)
# # # #             os.makedirs(out_dir, exist_ok=True)

# # # #             remix_images(
# # # #                 image_paths=[in_path],
# # # #                 prompt=prompt,
# # # #                 MODEL_NAME=model_choice,
# # # #                 output_dir=out_dir,
# # # #                 api_key=st.session_state.api_key
# # # #             )

# # # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # #             if results:
# # # #                 result_path = results[0]
# # # #                 all_paths.append(result_path)

# # # #                 col_a, col_b = st.columns(2)
# # # #                 col_a.image(t2_file, caption="Original")
# # # #                 col_b.image(result_path, caption=prompt)

# # # #                 with open(result_path, "rb") as f:
# # # #                     col_b.download_button(
# # # #                         "Download",
# # # #                         f,
# # # #                         file_name=f"prompt_{i}.png",
# # # #                         key=f"t2_dl_{i}"
# # # #                     )

# # # #             progress.progress((i + 1) / len(prompt_list))

# # # #         if all_paths:
# # # #             st.divider()
# # # #             st.download_button(
# # # #                 "📦 Download All Variations (ZIP)",
# # # #                 create_zip(all_paths),
# # # #                 "variations.zip"
# # # #             )

# # # # # ==========================================================
# # # # # TAB 3 — MULTI-IMAGE BLEND (NEW)
# # # # # ==========================================================
# # # # with tab3:
# # # #     st.markdown("Process **multiple reference images** together into a **single result**.")

# # # #     t3_prompt = st.text_area(
# # # #         "Prompt",
# # # #         value="Combine the subjects of these images in a natural way, producing a new image.",
# # # #         key="t3_prompt_area"
# # # #     )

# # # #     t3_files = st.file_uploader(
# # # #         "Upload Reference Images (Max 5 recommended)",
# # # #         type=["jpg", "png", "jpeg"],
# # # #         accept_multiple_files=True,
# # # #         key="t3_files"
# # # #     )

# # # #     if st.button(
# # # #         "Run Multi-Image Blend",
# # # #         type="primary",
# # # #         disabled=not t3_files,
# # # #         key="t3_run_btn"
# # # #     ):
# # # #         progress = st.progress(0)
        
# # # #         in_paths = []
# # # #         for i, file in enumerate(t3_files):
# # # #             in_path = os.path.join(TEMP_INPUT_DIR, f"blend_input_{i}.png")
# # # #             with open(in_path, "wb") as f:
# # # #                 f.write(file.getbuffer())
# # # #             in_paths.append(in_path)

# # # #         out_dir = os.path.join(TEMP_OUTPUT_DIR, "blend_output")
# # # #         shutil.rmtree(out_dir, ignore_errors=True)
# # # #         os.makedirs(out_dir, exist_ok=True)

# # # #         st.write(f"Running blend process using {len(in_paths)} images...")

# # # #         remix_images(
# # # #             image_paths=in_paths,
# # # #             prompt=t3_prompt,
# # # #             MODEL_NAME=model_choice,
# # # #             output_dir=out_dir,
# # # #             api_key=st.session_state.api_key
# # # #         )

# # # #         results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # # #         if results:
# # # #             result_path = results[0]

# # # #             st.subheader("Input Reference Images")
# # # #             cols = st.columns(len(t3_files))
# # # #             for idx, col in enumerate(cols):
# # # #                 col.image(t3_files[idx], caption=f"Ref {idx+1}")

# # # #             st.subheader("Blended Result")
# # # #             st.image(result_path, use_container_width=True)

# # # #             with open(result_path, "rb") as f:
# # # #                 st.download_button(
# # # #                     "⬇️ Download Blended Image",
# # # #                     f,
# # # #                     file_name="blended_result.png",
# # # #                     key="t3_dl_btn"
# # # #                 )

# # # #         progress.progress(1.0)


# # # #####################################################################################################################
# # # import streamlit as st
# # # import os
# # # import glob
# # # import zipfile
# # # import io
# # # import shutil
# # # from src.with_image import remix_images

# # # # =========================
# # # # SETUP
# # # # =========================
# # # st.set_page_config(
# # #     page_title="Gemini Remixer Pro",
# # #     layout="wide"
# # # )

# # # TEMP_INPUT_DIR = "temp_streamlit_input"
# # # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # # =========================
# # # # HELPERS
# # # # =========================
# # # def create_zip(paths):
# # #     zip_buffer = io.BytesIO()
# # #     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
# # #         for file_path in paths:
# # #             zf.write(file_path, arcname=os.path.basename(file_path))
# # #     zip_buffer.seek(0)
# # #     return zip_buffer

# # # # =========================
# # # # SESSION STATE
# # # # =========================
# # # if "prompts" not in st.session_state:
# # #     st.session_state.prompts = ["Cyberpunk style"]

# # # # =========================
# # # # SIDEBAR
# # # # =========================
# # # with st.sidebar:
# # #     st.header("Settings")

# # #     if "api_key" not in st.session_state:
# # #         st.session_state.api_key = ""

# # #     st.session_state.api_key = st.text_input(
# # #         "API Key (Optional override)",
# # #         type="password",
# # #         value=st.session_state.api_key
# # #     )

# # #     model_choice = st.selectbox(
# # #         "Model",
# # #         [
# # #             "gemini-3.1-flash-image-preview",
# # #             "gemini-3-pro-image-preview",
# # #             "gemini-2.5-flash-image",

# # #         ],
# # #         index=0
# # #     )

# # # # =========================
# # # # MAIN UI
# # # # =========================
# # # st.title("⚡ Gemini Image Remixer")

# # # tab1, tab2, tab3, tab4 = st.tabs(
# # #     ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)", "🖼️ Multi-Image Blend (1 Prompt)", "✍️ Text to Image"]
# # # )

# # # # ==========================================================
# # # # TAB 1 — BATCH IMAGES
# # # # ==========================================================
# # # with tab1:
# # #     st.markdown("Process **multiple images** using the **same prompt**.")

# # #     t1_prompt = st.text_area(
# # #         "Prompt",
# # #         value="Studio lighting, professional photography"
# # #     )

# # #     t1_files = st.file_uploader(
# # #         "Upload Images",
# # #         type=["jpg", "png", "jpeg"],
# # #         accept_multiple_files=True
# # #     )

# # #     if st.button(
# # #         "Run Batch Process",
# # #         type="primary",
# # #         disabled=not t1_files
# # #     ):
# # #         all_paths = []
# # #         progress = st.progress(0)

# # #         for i, file in enumerate(t1_files):
# # #             in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
# # #             with open(in_path, "wb") as f:
# # #                 f.write(file.getbuffer())

# # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
# # #             shutil.rmtree(out_dir, ignore_errors=True)
# # #             os.makedirs(out_dir, exist_ok=True)

# # #             remix_images(
# # #                 image_paths=[in_path],
# # #                 prompt=t1_prompt,
# # #                 MODEL_NAME=model_choice,
# # #                 output_dir=out_dir,
# # #                 api_key=st.session_state.api_key
# # #             )

# # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # #             if results:
# # #                 result_path = results[0]
# # #                 all_paths.append(result_path)

# # #                 col_a, col_b = st.columns(2)
# # #                 col_a.image(file, caption="Original")
# # #                 col_b.image(result_path, caption=f"Result {i + 1}")

# # #                 with open(result_path, "rb") as f:
# # #                     col_b.download_button(
# # #                         "Download",
# # #                         f,
# # #                         file_name=f"batch_{i}.png",
# # #                         key=f"t1_dl_{i}"
# # #                     )

# # #             progress.progress((i + 1) / len(t1_files))

# # #         if all_paths:
# # #             st.divider()
# # #             st.download_button(
# # #                 "📦 Download All Results (ZIP)",
# # #                 create_zip(all_paths),
# # #                 "batch_results.zip"
# # #             )

# # # # ==========================================================
# # # # TAB 2 — MULTI PROMPT (FIXED)
# # # # ==========================================================
# # # with tab2:
# # #     st.markdown("Process **one image** using **multiple independent prompts**.")

# # #     t2_file = st.file_uploader(
# # #         "Upload One Image",
# # #         type=["jpg", "png", "jpeg"]
# # #     )

# # #     st.subheader("Prompts")

# # #     # Prompt inputs
# # #     for i, prompt in enumerate(st.session_state.prompts):
# # #         cols = st.columns([8, 1])
# # #         st.session_state.prompts[i] = cols[0].text_input(
# # #             f"Prompt {i + 1}",
# # #             value=prompt,
# # #             key=f"prompt_{i}"
# # #         )
# # #         if cols[1].button("❌", key=f"remove_{i}"):
# # #             st.session_state.prompts.pop(i)
# # #             st.rerun()

# # #     if st.button("➕ Add Prompt"):
# # #         st.session_state.prompts.append("")
# # #         st.rerun()

# # #     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

# # #     if st.button(
# # #         "Run Multi-Prompt Process",
# # #         type="primary",
# # #         disabled=not t2_file or not prompt_list
# # #     ):
# # #         all_paths = []
# # #         progress = st.progress(0)

# # #         # IMPORTANT: keep original bytes immutable
# # #         original_bytes = t2_file.getbuffer()

# # #         for i, prompt in enumerate(prompt_list):
# # #             st.write(f"Running Prompt {i + 1}: *{prompt}*")

# # #             # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
# # #             in_path = os.path.join(
# # #                 TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
# # #             )
# # #             with open(in_path, "wb") as f:
# # #                 f.write(original_bytes)

# # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
# # #             shutil.rmtree(out_dir, ignore_errors=True)
# # #             os.makedirs(out_dir, exist_ok=True)

# # #             remix_images(
# # #                 image_paths=[in_path],
# # #                 prompt=prompt,
# # #                 MODEL_NAME=model_choice,
# # #                 output_dir=out_dir,
# # #                 api_key=st.session_state.api_key
# # #             )

# # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # #             if results:
# # #                 result_path = results[0]
# # #                 all_paths.append(result_path)

# # #                 col_a, col_b = st.columns(2)
# # #                 col_a.image(t2_file, caption="Original")
# # #                 col_b.image(result_path, caption=prompt)

# # #                 with open(result_path, "rb") as f:
# # #                     col_b.download_button(
# # #                         "Download",
# # #                         f,
# # #                         file_name=f"prompt_{i}.png",
# # #                         key=f"t2_dl_{i}"
# # #                     )

# # #             progress.progress((i + 1) / len(prompt_list))

# # #         if all_paths:
# # #             st.divider()
# # #             st.download_button(
# # #                 "📦 Download All Variations (ZIP)",
# # #                 create_zip(all_paths),
# # #                 "variations.zip"
# # #             )

# # # # ==========================================================
# # # # TAB 3 — MULTI-IMAGE BLEND (NEW)
# # # # ==========================================================
# # # with tab3:
# # #     st.markdown("Process **multiple reference images** together into a **single result**.")

# # #     t3_prompt = st.text_area(
# # #         "Prompt",
# # #         value="Combine the subjects of these images in a natural way, producing a new image.",
# # #         key="t3_prompt_area"
# # #     )

# # #     t3_files = st.file_uploader(
# # #         "Upload Reference Images (Max 5 recommended)",
# # #         type=["jpg", "png", "jpeg"],
# # #         accept_multiple_files=True,
# # #         key="t3_files"
# # #     )

# # #     if st.button(
# # #         "Run Multi-Image Blend",
# # #         type="primary",
# # #         disabled=not t3_files,
# # #         key="t3_run_btn"
# # #     ):
# # #         progress = st.progress(0)
        
# # #         in_paths = []
# # #         for i, file in enumerate(t3_files):
# # #             in_path = os.path.join(TEMP_INPUT_DIR, f"blend_input_{i}.png")
# # #             with open(in_path, "wb") as f:
# # #                 f.write(file.getbuffer())
# # #             in_paths.append(in_path)

# # #         out_dir = os.path.join(TEMP_OUTPUT_DIR, "blend_output")
# # #         shutil.rmtree(out_dir, ignore_errors=True)
# # #         os.makedirs(out_dir, exist_ok=True)

# # #         st.write(f"Running blend process using {len(in_paths)} images...")

# # #         remix_images(
# # #             image_paths=in_paths,
# # #             prompt=t3_prompt,
# # #             MODEL_NAME=model_choice,
# # #             output_dir=out_dir,
# # #             api_key=st.session_state.api_key
# # #         )

# # #         results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # #         if results:
# # #             result_path = results[0]

# # #             st.subheader("Input Reference Images")
# # #             cols = st.columns(len(t3_files))
# # #             for idx, col in enumerate(cols):
# # #                 col.image(t3_files[idx], caption=f"Ref {idx+1}")

# # #             st.subheader("Blended Result")
# # #             st.image(result_path, use_container_width=True)

# # #             with open(result_path, "rb") as f:
# # #                 st.download_button(
# # #                     "⬇️ Download Blended Image",
# # #                     f,
# # #                     file_name="blended_result.png",
# # #                     key="t3_dl_btn"
# # #                 )

# # #         progress.progress(1.0)

# # # # ==========================================================
# # # # TAB 4 — TEXT TO IMAGE (NEW)
# # # # ==========================================================
# # # with tab4:
# # #     st.markdown("Generate **new images** from text prompts (no reference images).")

# # #     t4_prompt = st.text_area(
# # #         "Prompt",
# # #         value="A futuristic city with flying cars at sunset, studio lighting, hyperrealistic",
# # #         key="t4_prompt_area"
# # #     )

# # #     t4_count = st.number_input("Number of Images to Generate", min_value=1, max_value=10, value=1, step=1, key="t4_count")

# # #     if st.button(
# # #         "Run Text-to-Image",
# # #         type="primary",
# # #         key="t4_run_btn"
# # #     ):
# # #         progress = st.progress(0)
# # #         all_paths = []
        
# # #         for i in range(t4_count):
# # #             st.write(f"Generating image {i + 1} of {t4_count}...")

# # #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"text_to_image_{i}")
# # #             shutil.rmtree(out_dir, ignore_errors=True)
# # #             os.makedirs(out_dir, exist_ok=True)

# # #             remix_images(
# # #                 image_paths=[],
# # #                 prompt=t4_prompt,
# # #                 MODEL_NAME=model_choice,
# # #                 output_dir=out_dir,
# # #                 api_key=st.session_state.api_key
# # #             )

# # #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# # #             if results:
# # #                 result_path = results[0]
# # #                 all_paths.append(result_path)

# # #                 st.image(result_path, caption=f"Generated Image {i + 1}")

# # #                 with open(result_path, "rb") as f:
# # #                     st.download_button(
# # #                         "⬇️ Download Image",
# # #                         f,
# # #                         file_name=f"generated_{i}.png",
# # #                         key=f"t4_dl_btn_{i}"
# # #                     )

# # #             progress.progress((i + 1) / t4_count)

# # #         if all_paths and len(all_paths) > 1:
# # #             st.divider()
# # #             st.download_button(
# # #                 "📦 Download All Results (ZIP)",
# # #                 create_zip(all_paths),
# # #                 "generated_results.zip",
# # #                 key="t4_zip_dl"
# # #             )

# # #####################################################################################################################
# # import streamlit as st
# # import os
# # import glob
# # import zipfile
# # import io
# # import shutil
# # from src.with_image import remix_images

# # # =========================
# # # SETUP
# # # =========================
# # st.set_page_config(
# #     page_title="Gemini Remixer Pro",
# #     layout="wide"
# # )

# # TEMP_INPUT_DIR = "temp_streamlit_input"
# # TEMP_OUTPUT_DIR = "temp_streamlit_output"

# # os.makedirs(TEMP_INPUT_DIR, exist_ok=True)
# # os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

# # # =========================
# # # HELPERS
# # # =========================
# # def create_zip(paths):
# #     zip_buffer = io.BytesIO()
# #     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
# #         for file_path in paths:
# #             zf.write(file_path, arcname=os.path.basename(file_path))
# #     zip_buffer.seek(0)
# #     return zip_buffer

# # # =========================
# # # SESSION STATE
# # # =========================
# # if "prompts" not in st.session_state:
# #     st.session_state.prompts = ["Cyberpunk style"]

# # # =========================
# # # SIDEBAR
# # # =========================
# # with st.sidebar:
# #     st.header("Settings")

# #     if "api_key" not in st.session_state:
# #         st.session_state.api_key = ""

# #     st.session_state.api_key = st.text_input(
# #         "API Key (Optional override)",
# #         type="password",
# #         value=st.session_state.api_key
# #     )

# #     model_choice = st.selectbox(
# #         "Model",
# #         [
# #             "gemini-3.1-flash-image-preview",
# #             "gemini-3-pro-image-preview",
# #             "gemini-2.5-flash-image",

# #         ],
# #         index=0
# #     )

# #     aspect_ratio_choice = st.selectbox(
# #         "Aspect Ratio",
# #         ["1:1", "3:4", "4:3", "9:16", "16:9"],
# #         index=0
# #     )

# # # =========================
# # # MAIN UI
# # # =========================
# # st.title("⚡ Gemini Image Remixer")

# # tab1, tab2, tab3, tab4 = st.tabs(
# #     ["📁 Batch Images (1 Prompt)", "📝 Multi-Prompt (1 Image)", "🖼️ Multi-Image Blend (1 Prompt)", "✍️ Text to Image"]
# # )

# # # ==========================================================
# # # TAB 1 — BATCH IMAGES
# # # ==========================================================
# # with tab1:
# #     st.markdown("Process **multiple images** using the **same prompt**.")

# #     t1_prompt = st.text_area(
# #         "Prompt",
# #         value="Studio lighting, professional photography"
# #     )

# #     t1_files = st.file_uploader(
# #         "Upload Images",
# #         type=["jpg", "png", "jpeg"],
# #         accept_multiple_files=True
# #     )

# #     if st.button(
# #         "Run Batch Process",
# #         type="primary",
# #         disabled=not t1_files
# #     ):
# #         all_paths = []
# #         progress = st.progress(0)

# #         for i, file in enumerate(t1_files):
# #             in_path = os.path.join(TEMP_INPUT_DIR, f"batch_input_{i}.png")
# #             with open(in_path, "wb") as f:
# #                 f.write(file.getbuffer())

# #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"batch_{i}")
# #             shutil.rmtree(out_dir, ignore_errors=True)
# #             os.makedirs(out_dir, exist_ok=True)

# #             remix_images(
# #                 image_paths=[in_path],
# #                 prompt=t1_prompt,
# #                 MODEL_NAME=model_choice,
# #                 output_dir=out_dir,
# #                 api_key=st.session_state.api_key,
# #                 aspect_ratio=aspect_ratio_choice
# #             )

# #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# #             if results:
# #                 result_path = results[0]
# #                 all_paths.append(result_path)

# #                 col_a, col_b = st.columns(2)
# #                 col_a.image(file, caption="Original")
# #                 col_b.image(result_path, caption=f"Result {i + 1}")

# #                 with open(result_path, "rb") as f:
# #                     col_b.download_button(
# #                         "Download",
# #                         f,
# #                         file_name=f"batch_{i}.png",
# #                         key=f"t1_dl_{i}"
# #                     )

# #             progress.progress((i + 1) / len(t1_files))

# #         if all_paths:
# #             st.divider()
# #             st.download_button(
# #                 "📦 Download All Results (ZIP)",
# #                 create_zip(all_paths),
# #                 "batch_results.zip"
# #             )

# # # ==========================================================
# # # TAB 2 — MULTI PROMPT (FIXED)
# # # ==========================================================
# # with tab2:
# #     st.markdown("Process **one image** using **multiple independent prompts**.")

# #     t2_file = st.file_uploader(
# #         "Upload One Image",
# #         type=["jpg", "png", "jpeg"]
# #     )

# #     st.subheader("Prompts")

# #     # Prompt inputs
# #     for i, prompt in enumerate(st.session_state.prompts):
# #         cols = st.columns([8, 1])
# #         st.session_state.prompts[i] = cols[0].text_input(
# #             f"Prompt {i + 1}",
# #             value=prompt,
# #             key=f"prompt_{i}"
# #         )
# #         if cols[1].button("❌", key=f"remove_{i}"):
# #             st.session_state.prompts.pop(i)
# #             st.rerun()

# #     if st.button("➕ Add Prompt"):
# #         st.session_state.prompts.append("")
# #         st.rerun()

# #     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

# #     if st.button(
# #         "Run Multi-Prompt Process",
# #         type="primary",
# #         disabled=not t2_file or not prompt_list
# #     ):
# #         all_paths = []
# #         progress = st.progress(0)

# #         # IMPORTANT: keep original bytes immutable
# #         original_bytes = t2_file.getbuffer()

# #         for i, prompt in enumerate(prompt_list):
# #             st.write(f"Running Prompt {i + 1}: *{prompt}*")

# #             # UNIQUE INPUT FILE PER PROMPT (CRITICAL FIX)
# #             in_path = os.path.join(
# #                 TEMP_INPUT_DIR, f"single_source_prompt_{i}.png"
# #             )
# #             with open(in_path, "wb") as f:
# #                 f.write(original_bytes)

# #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"prompt_{i}")
# #             shutil.rmtree(out_dir, ignore_errors=True)
# #             os.makedirs(out_dir, exist_ok=True)

# #             remix_images(
# #                 image_paths=[in_path],
# #                 prompt=prompt,
# #                 MODEL_NAME=model_choice,
# #                 output_dir=out_dir,
# #                 api_key=st.session_state.api_key,
# #                 aspect_ratio=aspect_ratio_choice
# #             )

# #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# #             if results:
# #                 result_path = results[0]
# #                 all_paths.append(result_path)

# #                 col_a, col_b = st.columns(2)
# #                 col_a.image(t2_file, caption="Original")
# #                 col_b.image(result_path, caption=prompt)

# #                 with open(result_path, "rb") as f:
# #                     col_b.download_button(
# #                         "Download",
# #                         f,
# #                         file_name=f"prompt_{i}.png",
# #                         key=f"t2_dl_{i}"
# #                     )

# #             progress.progress((i + 1) / len(prompt_list))

# #         if all_paths:
# #             st.divider()
# #             st.download_button(
# #                 "📦 Download All Variations (ZIP)",
# #                 create_zip(all_paths),
# #                 "variations.zip"
# #             )

# # # ==========================================================
# # # TAB 3 — MULTI-IMAGE BLEND (NEW)
# # # ==========================================================
# # with tab3:
# #     st.markdown("Process **multiple reference images** together into a **single result**.")

# #     t3_prompt = st.text_area(
# #         "Prompt",
# #         value="Combine the subjects of these images in a natural way, producing a new image.",
# #         key="t3_prompt_area"
# #     )

# #     t3_files = st.file_uploader(
# #         "Upload Reference Images (Max 5 recommended)",
# #         type=["jpg", "png", "jpeg"],
# #         accept_multiple_files=True,
# #         key="t3_files"
# #     )

# #     if st.button(
# #         "Run Multi-Image Blend",
# #         type="primary",
# #         disabled=not t3_files,
# #         key="t3_run_btn"
# #     ):
# #         progress = st.progress(0)
        
# #         in_paths = []
# #         for i, file in enumerate(t3_files):
# #             in_path = os.path.join(TEMP_INPUT_DIR, f"blend_input_{i}.png")
# #             with open(in_path, "wb") as f:
# #                 f.write(file.getbuffer())
# #             in_paths.append(in_path)

# #         out_dir = os.path.join(TEMP_OUTPUT_DIR, "blend_output")
# #         shutil.rmtree(out_dir, ignore_errors=True)
# #         os.makedirs(out_dir, exist_ok=True)

# #         st.write(f"Running blend process using {len(in_paths)} images...")

# #         remix_images(
# #             image_paths=in_paths,
# #             prompt=t3_prompt,
# #             MODEL_NAME=model_choice,
# #             output_dir=out_dir,
# #             api_key=st.session_state.api_key,
# #             aspect_ratio=aspect_ratio_choice
# #         )

# #         results = sorted(glob.glob(os.path.join(out_dir, "*")))
# #         if results:
# #             result_path = results[0]

# #             st.subheader("Input Reference Images")
# #             cols = st.columns(len(t3_files))
# #             for idx, col in enumerate(cols):
# #                 col.image(t3_files[idx], caption=f"Ref {idx+1}")

# #             st.subheader("Blended Result")
# #             st.image(result_path, use_container_width=True)

# #             with open(result_path, "rb") as f:
# #                 st.download_button(
# #                     "⬇️ Download Blended Image",
# #                     f,
# #                     file_name="blended_result.png",
# #                     key="t3_dl_btn"
# #                 )

# #         progress.progress(1.0)

# # # ==========================================================
# # # TAB 4 — TEXT TO IMAGE (NEW)
# # # ==========================================================
# # with tab4:
# #     st.markdown("Generate **new images** from text prompts (no reference images).")

# #     t4_prompt = st.text_area(
# #         "Prompt",
# #         value="A futuristic city with flying cars at sunset, studio lighting, hyperrealistic",
# #         key="t4_prompt_area"
# #     )

# #     t4_count = st.number_input("Number of Images to Generate", min_value=1, max_value=10, value=1, step=1, key="t4_count")

# #     if st.button(
# #         "Run Text-to-Image",
# #         type="primary",
# #         key="t4_run_btn"
# #     ):
# #         progress = st.progress(0)
# #         all_paths = []
        
# #         for i in range(t4_count):
# #             st.write(f"Generating image {i + 1} of {t4_count}...")

# #             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"text_to_image_{i}")
# #             shutil.rmtree(out_dir, ignore_errors=True)
# #             os.makedirs(out_dir, exist_ok=True)

# #             remix_images(
# #                 image_paths=[],
# #                 prompt=t4_prompt,
# #                 MODEL_NAME=model_choice,
# #                 output_dir=out_dir,
# #                 api_key=st.session_state.api_key,
# #                 aspect_ratio=aspect_ratio_choice
# #             )

# #             results = sorted(glob.glob(os.path.join(out_dir, "*")))
# #             if results:
# #                 result_path = results[0]
# #                 all_paths.append(result_path)

# #                 st.image(result_path, caption=f"Generated Image {i + 1}")

# #                 with open(result_path, "rb") as f:
# #                     st.download_button(
# #                         "⬇️ Download Image",
# #                         f,
# #                         file_name=f"generated_{i}.png",
# #                         key=f"t4_dl_btn_{i}"
# #                     )

# #             progress.progress((i + 1) / t4_count)

# #         if all_paths and len(all_paths) > 1:
# #             st.divider()
# #             st.download_button(
# #                 "📦 Download All Results (ZIP)",
# #                 create_zip(all_paths),
# #                 "generated_results.zip",
# #                 key="t4_zip_dl"
# #             )
# ##################################################################################################################################################################################################################
# import streamlit as st
# import os
# import glob
# import zipfile
# import io
# import shutil
# import time
# from google import genai
# from src.with_image import remix_images

# # =========================
# # SETUP
# # =========================
# st.set_page_config(
#     page_title="Gemini Remixer Pro + Video",
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


# def generate_video(
#     prompt,
#     model_name,
#     api_key,
#     output_dir,
#     image_path=None,
#     progress_callback=None,
# ):
#     """
#     Generate a video using Veo models via the Google GenAI API.
#     Supports both text-to-video and image-to-video modes.
#     """
#     os.makedirs(output_dir, exist_ok=True)

#     client = genai.Client(api_key=api_key)

#     # Build kwargs for generate_videos
#     generate_kwargs = {
#         "model": model_name,
#         "prompt": prompt,
#     }

#     # Add image if provided (image-to-video mode)
#     if image_path:
#         from google.genai import types
#         with open(image_path, "rb") as f:
#             image_data = f.read()

#         # Determine MIME type
#         import mimetypes
#         mime_type, _ = mimetypes.guess_type(image_path)
#         if not mime_type:
#             mime_type = "image/png"

#         image_part = types.Part.from_image(
#             data=image_data,
#             mime_type=mime_type,
#         )
#         generate_kwargs["image"] = image_part

#     # Call the video generation API
#     operation = client.models.generate_videos(**generate_kwargs)

#     # Poll for completion
#     poll_count = 0
#     max_polls = 120  # Max ~20 minutes at 10s intervals
#     while not operation.done:
#         if progress_callback:
#             progress_callback(poll_count)
#         time.sleep(10)
#         operation = client.operations.get(operation)
#         poll_count += 1
#         if poll_count >= max_polls:
#             raise TimeoutError("Video generation timed out after ~20 minutes")

#     # Check for errors
#     if operation.error:
#         raise RuntimeError(f"Video generation failed: {operation.error}")

#     # Extract and save the video
#     if not operation.response or not operation.response.generated_videos:
#         raise RuntimeError("No video was generated")

#     generated_video = operation.response.generated_videos[0]

#     # Download and save
#     client.files.download(file=generated_video.video)
#     timestamp = int(time.time())
#     filename = os.path.join(output_dir, f"generated_video_{timestamp}.mp4")
#     generated_video.video.save(filename)

#     return filename

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

#     if "api_key" not in st.session_state:
#         st.session_state.api_key = ""

#     st.session_state.api_key = st.text_input(
#         "API Key (Optional override)",
#         type="password",
#         value=st.session_state.api_key
#     )

#     # Image generation models
#     st.subheader("Image Models")
#     image_model_choice = st.selectbox(
#         "Model",
#         [
#             "gemini-3.1-flash-image-preview",
#             "gemini-3-pro-image-preview",
#             "gemini-2.5-flash-image",
#         ],
#         index=0,
#         key="image_model"
#     )

#     st.divider()

#     # Video generation models
#     st.subheader("Video Models")
#     video_model_choice = st.selectbox(
#         "Model",
#         [
#             "veo-3.1-generate-preview",
#             "veo-3.1-fast-generate-preview",
#             "veo-3.1-lite-generate-preview",
#             "veo-3.0-generate-001",
#             "veo-3.0-fast-generate-001",
#         ],
#         index=0,
#         key="video_model"
#     )

#     aspect_ratio_choice = st.selectbox(
#         "Aspect Ratio (Images)",
#         ["1:1", "3:4", "4:3", "9:16", "16:9"],
#         index=0
#     )

# # =========================
# # MAIN UI
# # =========================
# st.title("⚡ Gemini Image & Video Remixer")

# tab1, tab2, tab3, tab4, tab5 = st.tabs(
#     [
#         "📁 Batch Images (1 Prompt)",
#         "📝 Multi-Prompt (1 Image)",
#         "🖼️ Multi-Image Blend (1 Prompt)",
#         "✍️ Text to Image",
#         "🎬 Video Generation"
#     ]
# )

# # ==========================================================
# # TAB 1 — BATCH IMAGES
# # ==========================================================
# with tab1:
#     st.markdown("Process **multiple images** using the **same prompt**.")

#     t1_prompt = st.text_area(
#         "Prompt",
#         value="Studio lighting, professional photography",
#         key="t1_prompt_area"
#     )

#     t1_files = st.file_uploader(
#         "Upload Images",
#         type=["jpg", "png", "jpeg"],
#         accept_multiple_files=True,
#         key="t1_files"
#     )

#     if st.button(
#         "Run Batch Process",
#         type="primary",
#         disabled=not t1_files,
#         key="t1_run_btn"
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
#                 MODEL_NAME=image_model_choice,
#                 output_dir=out_dir,
#                 api_key=st.session_state.api_key,
#                 aspect_ratio=aspect_ratio_choice
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
#                 "batch_results.zip",
#                 key="t1_zip_dl"
#             )

# # ==========================================================
# # TAB 2 — MULTI PROMPT
# # ==========================================================
# with tab2:
#     st.markdown("Process **one image** using **multiple independent prompts**.")

#     t2_file = st.file_uploader(
#         "Upload One Image",
#         type=["jpg", "png", "jpeg"],
#         key="t2_file"
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

#     if st.button("➕ Add Prompt", key="add_prompt_btn"):
#         st.session_state.prompts.append("")
#         st.rerun()

#     prompt_list = [p.strip() for p in st.session_state.prompts if p.strip()]

#     if st.button(
#         "Run Multi-Prompt Process",
#         type="primary",
#         disabled=not t2_file or not prompt_list,
#         key="t2_run_btn"
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
#                 MODEL_NAME=image_model_choice,
#                 output_dir=out_dir,
#                 api_key=st.session_state.api_key,
#                 aspect_ratio=aspect_ratio_choice
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
#                 "variations.zip",
#                 key="t2_zip_dl"
#             )

# # ==========================================================
# # TAB 3 — MULTI-IMAGE BLEND
# # ==========================================================
# with tab3:
#     st.markdown("Process **multiple reference images** together into a **single result**.")

#     t3_prompt = st.text_area(
#         "Prompt",
#         value="Combine the subjects of these images in a natural way, producing a new image.",
#         key="t3_prompt_area"
#     )

#     t3_files = st.file_uploader(
#         "Upload Reference Images (Max 5 recommended)",
#         type=["jpg", "png", "jpeg"],
#         accept_multiple_files=True,
#         key="t3_files_uploader"
#     )

#     if st.button(
#         "Run Multi-Image Blend",
#         type="primary",
#         disabled=not t3_files,
#         key="t3_run_btn"
#     ):
#         progress = st.progress(0)

#         in_paths = []
#         for i, file in enumerate(t3_files):
#             in_path = os.path.join(TEMP_INPUT_DIR, f"blend_input_{i}.png")
#             with open(in_path, "wb") as f:
#                 f.write(file.getbuffer())
#             in_paths.append(in_path)

#         out_dir = os.path.join(TEMP_OUTPUT_DIR, "blend_output")
#         shutil.rmtree(out_dir, ignore_errors=True)
#         os.makedirs(out_dir, exist_ok=True)

#         st.write(f"Running blend process using {len(in_paths)} images...")

#         remix_images(
#             image_paths=in_paths,
#             prompt=t3_prompt,
#             MODEL_NAME=image_model_choice,
#             output_dir=out_dir,
#             api_key=st.session_state.api_key,
#             aspect_ratio=aspect_ratio_choice
#         )

#         results = sorted(glob.glob(os.path.join(out_dir, "*")))
#         if results:
#             result_path = results[0]

#             st.subheader("Input Reference Images")
#             cols = st.columns(len(t3_files))
#             for idx, col in enumerate(cols):
#                 col.image(t3_files[idx], caption=f"Ref {idx+1}")

#             st.subheader("Blended Result")
#             st.image(result_path, use_container_width=True)

#             with open(result_path, "rb") as f:
#                 st.download_button(
#                     "⬇️ Download Blended Image",
#                     f,
#                     file_name="blended_result.png",
#                     key="t3_dl_btn"
#                 )

#         progress.progress(1.0)

# # ==========================================================
# # TAB 4 — TEXT TO IMAGE
# # ==========================================================
# with tab4:
#     st.markdown("Generate **new images** from text prompts (no reference images).")

#     t4_prompt = st.text_area(
#         "Prompt",
#         value="A futuristic city with flying cars at sunset, studio lighting, hyperrealistic",
#         key="t4_prompt_area"
#     )

#     t4_count = st.number_input(
#         "Number of Images to Generate",
#         min_value=1,
#         max_value=10,
#         value=1,
#         step=1,
#         key="t4_count"
#     )

#     if st.button(
#         "Run Text-to-Image",
#         type="primary",
#         key="t4_run_btn"
#     ):
#         progress = st.progress(0)
#         all_paths = []

#         for i in range(t4_count):
#             st.write(f"Generating image {i + 1} of {t4_count}...")

#             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"text_to_image_{i}")
#             shutil.rmtree(out_dir, ignore_errors=True)
#             os.makedirs(out_dir, exist_ok=True)

#             remix_images(
#                 image_paths=[],
#                 prompt=t4_prompt,
#                 MODEL_NAME=image_model_choice,
#                 output_dir=out_dir,
#                 api_key=st.session_state.api_key,
#                 aspect_ratio=aspect_ratio_choice
#             )

#             results = sorted(glob.glob(os.path.join(out_dir, "*")))
#             if results:
#                 result_path = results[0]
#                 all_paths.append(result_path)

#                 st.image(result_path, caption=f"Generated Image {i + 1}")

#                 with open(result_path, "rb") as f:
#                     st.download_button(
#                         "⬇️ Download Image",
#                         f,
#                         file_name=f"generated_{i}.png",
#                         key=f"t4_dl_btn_{i}"
#                     )

#             progress.progress((i + 1) / t4_count)

#         if all_paths and len(all_paths) > 1:
#             st.divider()
#             st.download_button(
#                 "📦 Download All Results (ZIP)",
#                 create_zip(all_paths),
#                 "generated_results.zip",
#                 key="t4_zip_dl"
#             )

# # ==========================================================
# # TAB 5 — VIDEO GENERATION (NEW)
# # ==========================================================
# with tab5:
#     st.markdown("Generate **videos** using Veo models from text prompts and optionally reference images.")

#     # Mode selector
#     video_mode = st.radio(
#         "Generation Mode",
#         ["Text-to-Video", "Image-to-Video"],
#         horizontal=True,
#         key="video_mode"
#     )

#     t5_prompt = st.text_area(
#         "Prompt",
#         value="A cat sitting on a windowsill watching rain fall, cinematic lighting",
#         key="t5_prompt_area"
#     )

#     t5_video_file = None
#     if video_mode == "Image-to-Video":
#         t5_video_file = st.file_uploader(
#             "Upload Reference Image",
#             type=["jpg", "png", "jpeg", "webp"],
#             key="t5_file"
#         )

#     t5_count = st.number_input(
#         "Number of Videos to Generate",
#         min_value=1,
#         max_value=5,
#         value=1,
#         step=1,
#         key="t5_count"
#     )

#     st.info(f"Selected Model: **{video_model_choice}**")

#     if st.button(
#         "Run Video Generation",
#         type="primary",
#         disabled=(video_mode == "Image-to-Video" and not t5_video_file),
#         key="t5_run_btn"
#     ):
#         if not st.session_state.api_key:
#             st.error("API key is required for video generation. Please set it in the sidebar.")
#             st.stop()

#         progress = st.progress(0)
#         status_text = st.empty()
#         all_paths = []

#         for i in range(t5_count):
#             status_text.write(f"Generating video {i + 1} of {t5_count}...")

#             out_dir = os.path.join(TEMP_OUTPUT_DIR, f"video_gen_{i}")
#             shutil.rmtree(out_dir, ignore_errors=True)
#             os.makedirs(out_dir, exist_ok=True)

#             image_path_for_call = None
#             if video_mode == "Image-to-Video" and t5_video_file:
#                 image_path_for_call = os.path.join(TEMP_INPUT_DIR, f"video_ref_{i}.png")
#                 with open(image_path_for_call, "wb") as f:
#                     f.write(t5_video_file.getbuffer())

#             # Define a progress callback for polling
#             def poll_progress(poll_count):
#                 # Update status with polling count
#                 status_text.write(f"Generating video {i + 1} of {t5_count}... (poll #{poll_count}, ~{poll_count * 10}s elapsed)")

#             try:
#                 result_path = generate_video(
#                     prompt=t5_prompt,
#                     model_name=video_model_choice,
#                     api_key=st.session_state.api_key,
#                     output_dir=out_dir,
#                     image_path=image_path_for_call,
#                     progress_callback=poll_progress,
#                 )

#                 all_paths.append(result_path)

#                 st.video(result_path)

#                 with open(result_path, "rb") as f:
#                     st.download_button(
#                         "⬇️ Download Video",
#                         f,
#                         file_name=f"generated_video_{i}.mp4",
#                         key=f"t5_dl_btn_{i}"
#                     )

#             except Exception as e:
#                 st.error(f"Video {i + 1} failed: {e}")

#             # Update overall progress
#             progress.progress((i + 1) / t5_count)

#         status_text.success("Video generation complete!")

#         if all_paths and len(all_paths) > 1:
#             st.divider()
#             st.download_button(
#                 "📦 Download All Videos (ZIP)",
#                 create_zip(all_paths),
#                 "generated_videos.zip",
#                 key="t5_zip_dl"
#             )

###########################################################################################################################################################
import streamlit as st
import os
import glob
import zipfile
import io
import shutil
import time
from google import genai
from google.genai import types
from src.with_image import remix_images

# =========================
# SETUP
# =========================
st.set_page_config(
    page_title="Gemini Remixer Pro + Video",
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


def generate_video(
    prompt,
    model_name,
    api_key,
    output_dir,
    image_path=None,
    duration_seconds=8,
    video_aspect_ratio="16:9",
    progress_callback=None,
):
    """
    Generate a video using Veo models via the Google GenAI API.
    Supports both text-to-video and image-to-video modes.
    """
    os.makedirs(output_dir, exist_ok=True)

    client = genai.Client(api_key=api_key)

    # Build config for generate_videos
    video_config = types.GenerateVideosConfig(
        aspect_ratio=video_aspect_ratio,
        duration_seconds=duration_seconds,
    )

    # Build kwargs for generate_videos
    generate_kwargs = {
        "model": model_name,
        "prompt": prompt,
        "config": video_config,
    }

    # Add image if provided (image-to-video mode)
    if image_path:
        with open(image_path, "rb") as f:
            image_data = f.read()

        # Determine MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"

        image_part = types.Part.from_image(
            data=image_data,
            mime_type=mime_type,
        )
        generate_kwargs["image"] = image_part

    # Call the video generation API
    operation = client.models.generate_videos(**generate_kwargs)

    # Poll for completion
    poll_count = 0
    max_polls = 120  # Max ~20 minutes at 10s intervals
    while not operation.done:
        if progress_callback:
            progress_callback(poll_count)
        time.sleep(10)
        operation = client.operations.get(operation)
        poll_count += 1
        if poll_count >= max_polls:
            raise TimeoutError("Video generation timed out after ~20 minutes")

    # Check for errors
    if operation.error:
        raise RuntimeError(f"Video generation failed: {operation.error}")

    # Extract and save the video
    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError("No video was generated")

    generated_video = operation.response.generated_videos[0]

    # Download and save
    client.files.download(file=generated_video.video)
    timestamp = int(time.time())
    filename = os.path.join(output_dir, f"generated_video_{timestamp}.mp4")
    generated_video.video.save(filename)

    return filename

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

    # Image generation models
    st.subheader("Image Models")
    image_model_choice = st.selectbox(
        "Model",
        [
            "bytedance-seed/seedream-4.5",
        ],
        index=0,
        key="image_model"
    )

    st.divider()

    # Video generation models
    st.subheader("Video Models")
    video_model_choice = st.selectbox(
        "Model",
        [
            "veo-3.1-generate-preview",
            "veo-3.1-fast-generate-preview",
            "veo-3.1-lite-generate-preview",
            "veo-3.0-generate-001",
            "veo-3.0-fast-generate-001",
        ],
        index=0,
        key="video_model"
    )

    aspect_ratio_choice = st.selectbox(
        "Aspect Ratio (Images)",
        ["1:1", "3:4", "4:3", "9:16", "16:9"],
        index=0
    )

# =========================
# MAIN UI
# =========================
st.title("⚡ Gemini Image & Video Remixer")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📁 Batch Images (1 Prompt)",
        "📝 Multi-Prompt (1 Image)",
        "🖼️ Multi-Image Blend (1 Prompt)",
        "✍️ Text to Image",
        "🎬 Video Generation"
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
        disabled=not t1_files,
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

            remix_images(
                image_paths=[in_path],
                prompt=t1_prompt,
                MODEL_NAME=image_model_choice,
                output_dir=out_dir,
                api_key=st.session_state.api_key,
                aspect_ratio=aspect_ratio_choice
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
        disabled=not t2_file or not prompt_list,
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

            remix_images(
                image_paths=[in_path],
                prompt=prompt,
                MODEL_NAME=image_model_choice,
                output_dir=out_dir,
                api_key=st.session_state.api_key,
                aspect_ratio=aspect_ratio_choice
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
        disabled=not t3_files,
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

        remix_images(
            image_paths=in_paths,
            prompt=t3_prompt,
            MODEL_NAME=image_model_choice,
            output_dir=out_dir,
            api_key=st.session_state.api_key,
            aspect_ratio=aspect_ratio_choice
        )

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
        key="t4_run_btn"
    ):
        progress = st.progress(0)
        all_paths = []

        for i in range(t4_count):
            st.write(f"Generating image {i + 1} of {t4_count}...")

            out_dir = os.path.join(TEMP_OUTPUT_DIR, f"text_to_image_{i}")
            shutil.rmtree(out_dir, ignore_errors=True)
            os.makedirs(out_dir, exist_ok=True)

            remix_images(
                image_paths=[],
                prompt=t4_prompt,
                MODEL_NAME=image_model_choice,
                output_dir=out_dir,
                api_key=st.session_state.api_key,
                aspect_ratio=aspect_ratio_choice
            )

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

# ==========================================================
# TAB 5 — VIDEO GENERATION (NEW)
# ==========================================================
with tab5:
    st.markdown("Generate **videos** using Veo models from text prompts and optionally reference images.")

    # Mode selector
    video_mode = st.radio(
        "Generation Mode",
        ["Text-to-Video", "Image-to-Video"],
        horizontal=True,
        key="video_mode"
    )

    t5_prompt = st.text_area(
        "Prompt",
        value="A cat sitting on a windowsill watching rain fall, cinematic lighting",
        key="t5_prompt_area"
    )

    t5_video_file = None
    if video_mode == "Image-to-Video":
        t5_video_file = st.file_uploader(
            "Upload Reference Image",
            type=["jpg", "png", "jpeg", "webp"],
            key="t5_file"
        )

    t5_count = st.number_input(
        "Number of Videos to Generate",
        min_value=1,
        max_value=5,
        value=1,
        step=1,
        key="t5_count"
    )

    # Video configuration options
    col_dur, col_ar = st.columns(2)
    with col_dur:
        t5_duration = st.selectbox(
            "Duration",
            [4, 5, 6, 7, 8],
            index=4,  # Default to 8s
            format_func=lambda x: f"{x}s",
            key="t5_duration"
        )
    with col_ar:
        t5_video_ar = st.selectbox(
            "Aspect Ratio",
            ["16:9", "9:16", "1:1"],
            index=0,
            key="t5_video_ar"
        )

    st.info(f"Selected Model: **{video_model_choice}** | Duration: **{t5_duration}s** | Ratio: **{t5_video_ar}**")

    if st.button(
        "Run Video Generation",
        type="primary",
        disabled=(video_mode == "Image-to-Video" and not t5_video_file),
        key="t5_run_btn"
    ):
        if not st.session_state.api_key:
            st.error("API key is required for video generation. Please set it in the sidebar.")
            st.stop()

        progress = st.progress(0)
        status_text = st.empty()
        all_paths = []

        for i in range(t5_count):
            status_text.write(f"Generating video {i + 1} of {t5_count}...")

            out_dir = os.path.join(TEMP_OUTPUT_DIR, f"video_gen_{i}")
            shutil.rmtree(out_dir, ignore_errors=True)
            os.makedirs(out_dir, exist_ok=True)

            image_path_for_call = None
            if video_mode == "Image-to-Video" and t5_video_file:
                image_path_for_call = os.path.join(TEMP_INPUT_DIR, f"video_ref_{i}.png")
                with open(image_path_for_call, "wb") as f:
                    f.write(t5_video_file.getbuffer())

            # Define a progress callback for polling
            def poll_progress(poll_count):
                # Update status with polling count
                status_text.write(f"Generating video {i + 1} of {t5_count}... (poll #{poll_count}, ~{poll_count * 10}s elapsed)")

            try:
                result_path = generate_video(
                    prompt=t5_prompt,
                    model_name=video_model_choice,
                    api_key=st.session_state.api_key,
                    output_dir=out_dir,
                    image_path=image_path_for_call,
                    duration_seconds=t5_duration,
                    video_aspect_ratio=t5_video_ar,
                    progress_callback=poll_progress,
                )

                all_paths.append(result_path)

                st.video(result_path)

                with open(result_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Video",
                        f,
                        file_name=f"generated_video_{i}.mp4",
                        key=f"t5_dl_btn_{i}"
                    )

            except Exception as e:
                st.error(f"Video {i + 1} failed: {e}")

            # Update overall progress
            progress.progress((i + 1) / t5_count)

        status_text.success("Video generation complete!")

        if all_paths and len(all_paths) > 1:
            st.divider()
            st.download_button(
                "📦 Download All Videos (ZIP)",
                create_zip(all_paths),
                "generated_videos.zip",
                key="t5_zip_dl"
            )
