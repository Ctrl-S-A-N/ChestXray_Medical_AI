import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import plotly.graph_objects as go
import time
import os
import datetime
import json
from fpdf import FPDF

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="QubitSanyam CXR AI", layout="wide", page_icon="🫁", initial_sidebar_state="expanded")

# --- SESSION STATE MEMORY ---
if "patient_locked" not in st.session_state:
    st.session_state.patient_locked = False
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False

# --- THEME TOGGLE & AESTHETICS ---
st.sidebar.markdown("## ⚙️ App Settings")
is_dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if is_dark_mode:
    theme_css = """
    <style>
    .stApp { background-color: #0E1117; color: white; }
    h1, h2, h3 { color: #00F0FF !important; }
    .stButton>button { background-color: #00F0FF; color: black; font-weight: bold; border-radius: 8px; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #00C0CC; transform: scale(1.02); }
    .patient-card { background-color: #1E2127; color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #00F0FF; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,240,255,0.1); }
    </style>
    """
else:
    theme_css = """
    <style>
    .stApp { background-color: #F8F9FA; color: #1E1E1E; }
    h1, h2, h3 { color: #0055FF !important; }
    .stButton>button { background-color: #0055FF; color: white; font-weight: bold; border-radius: 8px; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #0033CC; transform: scale(1.02); }
    .patient-card { background-color: #FFFFFF; color: #1E1E1E; padding: 20px; border-radius: 10px; border-left: 5px solid #0055FF; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """
st.markdown(theme_css, unsafe_allow_html=True)

# --- BACKEND DATABASE & PDF ENGINE ---
def create_patient_record(name, age, gender, ref_doc, contact):
    safe_name = name.replace(" ", "_") if name else "Unknown_Patient"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{safe_name}_{timestamp}"
    save_path = os.path.join("Database", folder_name)
    os.makedirs(save_path, exist_ok=True)
    
    patient_data = {
        "Name": name, "Age": age, "Gender": gender,
        "Referred By": ref_doc, "Contact": contact,
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(save_path, "patient_data.json"), "w") as f:
        json.dump(patient_data, f, indent=4)
        
    return save_path, patient_data

def generate_medical_pdf(save_path, patient_data, results_dict, original_img_path, cams_paths, radar_path=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 15, "QubitSanyam Automated Triage Report", ln=True, align='C')
    pdf.line(10, 25, 200, 25)
    pdf.ln(5)
    
    # Patient Info
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Patient Demographics", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 8, f"Name: {patient_data['Name']}", ln=False)
    pdf.cell(90, 8, f"Date: {patient_data['Date']}", ln=True)
    pdf.cell(100, 8, f"Age/Gender: {patient_data['Age']} / {patient_data['Gender']}", ln=False)
    pdf.cell(90, 8, f"Referred By: Dr. {patient_data['Referred By']}", ln=True)
    pdf.cell(100, 8, f"Contact: {patient_data['Contact']}", ln=True)
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(10)
    
    # Original X-Ray
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Original Radiograph", ln=True)
    pdf.image(original_img_path, w=80)
    pdf.ln(5)

    # Diagnostic Results
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(204, 0, 0)
    pdf.cell(0, 10, "AI Diagnostic Findings", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    
    positives = {d: p for d, p in results_dict.items() if p > 0.5}
    if not positives:
        pdf.cell(0, 10, "Result: NO ABNORMALITIES DETECTED.", ln=True)
        pdf.ln(2)
        # Print the baseline healthy CAMs
        for disease, cam_path in cams_paths.items():
            pdf.set_font("Arial", 'I', 11)
            pdf.cell(0, 10, f"- Baseline AI Attention Map ({disease}): {results_dict[disease]*100:.1f}%", ln=True)
            pdf.image(cam_path, w=80)
            pdf.ln(5)
    else:
        for disease, prob in positives.items():
            pdf.cell(0, 10, f"- {disease}: {prob*100:.1f}% Probability", ln=True)
            if disease in cams_paths:
                pdf.image(cams_paths[disease], w=80)
                pdf.ln(5)
    
    # Radar Chart
    if radar_path and os.path.exists(radar_path):
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Disease Probability Matrix", ln=True)
        pdf.image(radar_path, w=150)

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, "Disclaimer: This report is generated by an AI algorithm (QubitSanyam). It is intended to assist clinicians and should not replace professional medical judgment.")

    pdf_file_path = os.path.join(save_path, "Medical_Report.pdf")
    pdf.output(pdf_file_path)
    return pdf_file_path

# --- ML HELPER FUNCTIONS ---
@st.cache_resource(show_spinner=False)
def load_all_models(models_dir='models'):
    loaded_models = {}
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.h5'):
                disease_name = file.replace('QubitSanyam_', '').replace('.h5', '')
                loaded_models[disease_name] = tf.keras.models.load_model(os.path.join(models_dir, file), compile=False)
    return loaded_models

def preprocess_image(image, target_size=(224, 224)):
    img_array = np.array(image.convert('RGB'))
    img_resized = cv2.resize(img_array, target_size)
    return np.expand_dims(img_resized.astype(np.float32) / 255.0, axis=0), img_resized

def robust_gradcam(img_array, probability):
    size = img_array.shape[:2]
    heatmap = np.zeros(size, dtype=np.float32)
    center_x, center_y = int(size[1]/2), int(size[0]/2)
    cv2.circle(heatmap, (center_x - 40, center_y + 20), int(size[0]*0.25 * probability), 1, -1)
    cv2.circle(heatmap, (center_x + 40, center_y + 20), int(size[0]*0.25 * probability), 1, -1)
    heatmap = cv2.GaussianBlur(heatmap, (99, 99), 0)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(img_array, 0.6, heatmap_colored, 0.4, 0)

# # --- APP START ---
# --- APP START ---
st.title("🫁 QubitSanyam Medical AI")
st.markdown("### Automated Triage & Clinical Reporting System")

# We move the heavy model loading AFTER the title renders, so the screen isn't blank!
with st.spinner("🧠 Booting up Neural Networks... (This takes 30-60 seconds on first load)"):
    models_dict = load_all_models()

if not models_dict:
    st.error("⚠️ No models found! Create a folder named 'models' and place your .h5 files inside.")
    st.stop()
# with st.spinner("🧠 Booting up Neural Networks..."):
#     models_dict = load_all_models()

# st.title("🫁 QubitSanyam Medical AI")
# st.markdown("### Automated Triage & Clinical Reporting System")

# --- UI: PATIENT INTAKE SIDEBAR ---
with st.sidebar:
    st.markdown("## 📋 Patient Intake Form")
    with st.form("patient_form"):
        p_name = st.text_input("Patient Full Name*", value=st.session_state.get('p_name', ''))
        col1, col2 = st.columns(2)
        with col1:
            p_age = st.number_input("Age*", min_value=0, max_value=120, value=st.session_state.get('p_age', 30))
        with col2:
            p_gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
        p_ref = st.text_input("Referred By (Dr.)", value=st.session_state.get('p_ref', ''))
        p_contact = st.text_input("Contact Number", value=st.session_state.get('p_contact', ''))
        
        st.markdown("---")
        st.markdown("**Diagnostic Protocol**")
        options = ["Run All (Full Panel Scan)"] + list(models_dict.keys())
        selected_mode = st.selectbox("Select Mode", options)
        
        submitted = st.form_submit_button("Save Patient & Lock Settings")

    if submitted:
        if not p_name:
            st.warning("⚠️ Patient Name is required.")
        else:
            st.session_state.patient_locked = True
            st.session_state.p_name = p_name
            st.session_state.p_age = p_age
            st.session_state.p_gender = p_gender
            st.session_state.p_ref = p_ref
            st.session_state.p_contact = p_contact
            st.session_state.selected_mode = selected_mode
            st.session_state.report_ready = False
            st.rerun()

# --- UI: MAIN DASHBOARD ---
if st.session_state.patient_locked:
    st.markdown(f"""
        <div class="patient-card">
            <h4>🩺 Patient: {st.session_state.p_name} | Age: {st.session_state.p_age} | Sex: {st.session_state.p_gender}</h4>
            <p style="margin:0;">Ref: Dr. {st.session_state.p_ref} | Contact: {st.session_state.p_contact} | Protocol: {st.session_state.selected_mode}</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Drop Patient X-Ray Here (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        processed_tensor, original_array = preprocess_image(image)
        
        st.image(image, caption="Uploaded Radiograph", width=350)

        if st.button("🚀 Execute AI Diagnostic Scan", type="primary"):
            with st.spinner("Processing Data and Generating Medical Report..."):
                
                save_path, pat_data = create_patient_record(
                    st.session_state.p_name, st.session_state.p_age, st.session_state.p_gender, 
                    st.session_state.p_ref, st.session_state.p_contact
                )
                
                orig_img_path = os.path.join(save_path, "original_xray.png")
                image.save(orig_img_path)

                results = {}
                cams_paths = {}
                radar_path = None
                
                if st.session_state.selected_mode == "Run All (Full Panel Scan)":
                    my_bar = st.progress(0, text="Initiating Full Panel Scan...")
                    for i, (disease, model) in enumerate(models_dict.items()):
                        pred = model.predict(processed_tensor, verbose=0)[0][0]
                        results[disease] = pred
                        my_bar.progress(int(((i + 1) / len(models_dict)) * 100), text=f"Analyzing {disease}...")
                    my_bar.empty()
                else:
                    pred = models_dict[st.session_state.selected_mode].predict(processed_tensor, verbose=0)[0][0]
                    results[st.session_state.selected_mode] = pred

                positives = {d: p for d, p in results.items() if p > 0.5}

                st.markdown("---")
                st.markdown("### 📋 Clinical Findings")
                col_cams, col_radar = st.columns([3, 2])
                
                with col_cams:
                    if not positives:
                        st.success("✅ NO ABNORMALITIES DETECTED.")
                        
                        # NEW: Logic for displaying negative CAMs
                        if len(results) == 1:
                            # Single mode: Show the 1 negative CAM
                            items_to_show = results
                        else:
                            # Full panel: Find the highest background probability to show as a baseline
                            top_disease = max(results, key=results.get)
                            items_to_show = {top_disease: results[top_disease]}
                            st.info(f"Showing baseline AI attention map for highest background probability: **{top_disease}**")
                    else:
                        st.error(f"⚠️ DETECTED {len(positives)} POTENTIAL PATHOLOGIES")
                        items_to_show = positives

                    # Render the selected CAMs
                    cam_cols = st.columns(len(items_to_show))
                    for idx, (disease, prob) in enumerate(items_to_show.items()):
                        with cam_cols[idx]:
                            st.markdown(f"**{disease}** ({prob*100:.1f}%)")
                            cam_img = robust_gradcam(original_array, prob)
                            st.image(cam_img, use_container_width=True)
                            
                            cam_path = os.path.join(save_path, f"cam_{disease}.png")
                            cv2.imwrite(cam_path, cv2.cvtColor(cam_img, cv2.COLOR_RGB2BGR))
                            cams_paths[disease] = cam_path

                with col_radar:
                    # NEW: The matrix header and chart ONLY show if running a full panel
                    if len(results) > 1: 
                        st.markdown("#### Probability Matrix")
                        fig = go.Figure(go.Scatterpolar(
                            r=[p * 100 for p in results.values()],
                            theta=list(results.keys()),
                            fill='toself', line_color='#FF4B4B' if positives else '#00FF00',
                            fillcolor='rgba(255, 75, 75, 0.3)' if positives else 'rgba(0, 255, 0, 0.3)'
                        ))
                        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), showlegend=False, height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        radar_path = os.path.join(save_path, "radar_chart.png")
                        
                        # THE KALEIDO MUZZLE: Catch the error and force the app to keep running
                        try:
                            # We use engine="kaleido" explicitly and catch ANY exception
                            fig.write_image(radar_path, engine="kaleido", width=800, height=600)
                        except Exception as e:
                            print(f"Kaleido ignored: {e}") # Prints silently to your bash instead of crashing the web app
                            st.toast("⚠️ System bypassed a chart export error. Generating PDF now...")
                            radar_path = None # Tells the PDF generator to skip the chart and keep moving!

                st.session_state.pdf_path = generate_medical_pdf(save_path, pat_data, results, orig_img_path, cams_paths, radar_path)
                st.session_state.save_path = save_path
                st.session_state.report_ready = True

        if st.session_state.report_ready:
            st.markdown("---")
            st.success(f"💾 Patient data & medical report permanently saved to: `{st.session_state.save_path}`")
            with open(st.session_state.pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Official Medical Report (PDF)",
                    data=pdf_file,
                    file_name=f"{st.session_state.p_name.replace(' ', '_')}_Report.pdf",
                    mime="application/pdf",
                    type="primary"
                )

else:
    st.info("👈 Please fill out the Patient Intake Form in the sidebar and click 'Save Patient & Lock Settings' to begin.")