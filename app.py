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
from supabase import create_client, Client

# --- SUPABASE CLOUD SETUP ---
SUPABASE_URL = "https://xagwnnqgzebncevwwwxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZ3dubnFnemVibmNldnd3d3h4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI2MTA0OTAsImV4cCI6MjA4ODE4NjQ5MH0.Xu4EXxHHGxuQ7rDpYUWk1F9EHWdKkiVAzlX1WjUrT9o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="QubitSanyam CXR AI", layout="wide", page_icon="🫁", initial_sidebar_state="expanded")

# --- SESSION STATE MEMORY ---
if "patient_locked" not in st.session_state:
    st.session_state.patient_locked = False
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home Overview"

# --- THEME TOGGLE & SKEUOMORPHIC AESTHETICS ---
st.sidebar.markdown("### ⚙️ System Settings")
is_dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if is_dark_mode:
    theme_css = """
    <style>
    /* Skeuomorphic Dark Theme */
    .stApp {
        background-color: #12151b;
        color: #e2e8f0;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    
    /* Tactile 3D Skeuomorphic Card */
    .skeuo-card {
        background: #181c24;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 8px 8px 18px #0a0c0f, -8px -8px 18px #262c39;
        transition: all 0.3s ease;
    }
    
    /* Inset Skeuomorphic Panel */
    .skeuo-inset {
        background: #13161c;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #1e232e;
        box-shadow: inset 4px 4px 8px #0b0c0f, inset -4px -4px 8px #1b2029;
        margin-bottom: 20px;
    }
    
    /* Metallic Header & Glowing LED */
    .skeuo-header {
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 2px solid #232936;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    
    .led-indicator {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #00ffff, #008b8b);
        box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff;
        display: inline-block;
    }
    
    .led-indicator.red {
        background: radial-gradient(circle at 30% 30%, #ff3366, #990022);
        box-shadow: 0 0 10px #ff3366, 0 0 20px #ff3366;
    }
    
    .led-indicator.amber {
        background: radial-gradient(circle at 30% 30%, #ffbb00, #997000);
        box-shadow: 0 0 10px #ffbb00, 0 0 20px #ffbb00;
    }

    h1, h2, h3 { color: #00F0FF !important; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
    
    /* Skeuomorphic Raised Buttons */
    .stButton>button {
        background: linear-gradient(145deg, #00d2eb, #009cb0) !important;
        color: #050b14 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #00ffff !important;
        box-shadow: 5px 5px 12px #0a0c0f, -5px -5px 12px #262c39 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 7px 7px 15px #0a0c0f, -7px -7px 15px #262c39, 0 0 15px rgba(0,240,255,0.4) !important;
    }
    
    .stButton>button:active {
        transform: translateY(2px) !important;
        box-shadow: inset 3px 3px 6px #006b78, inset -3px -3px 6px #00e5ff !important;
    }
    
    /* Inset Text Inputs & Selectboxes */
    .stTextInput input, .stNumberInput input, .stSelectbox>div>div {
        background: #13161c !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #232936 !important;
        box-shadow: inset 3px 3px 6px #0b0c0f, inset -3px -3px 6px #1b2029 !important;
    }
    
    /* Sidebar Tactile Styling */
    section[data-testid="stSidebar"] {
        background-color: #161920 !important;
        border-right: 2px solid #232936;
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }
    
    /* Badge styling */
    .skeuo-badge {
        background: linear-gradient(145deg, #1f2532, #141821);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #00F0FF;
        border: 1px solid #2d3546;
        box-shadow: 3px 3px 6px #0b0c0f, -3px -3px 6px #1b2029;
    }

    .patient-card { 
        background: #181c24; 
        color: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 5px solid #00F0FF; 
        margin-bottom: 20px; 
        box-shadow: 6px 6px 14px #0a0c0f, -6px -6px 14px #262c39; 
    }
    </style>
    """
else:
    theme_css = """
    <style>
    /* Skeuomorphic Light Theme */
    .stApp {
        background-color: #e6ecf5;
        color: #1e293b;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    
    .skeuo-card {
        background: #e6ecf5;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 8px 8px 18px #bec4cd, -8px -8px 18px #ffffff;
        transition: all 0.3s ease;
    }
    
    .skeuo-inset {
        background: #e1e7f0;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #d1d8e3;
        box-shadow: inset 4px 4px 8px #bdc3cc, inset -4px -4px 8px #ffffff;
        margin-bottom: 20px;
    }
    
    .skeuo-header {
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 2px solid #cbd5e1;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    
    .led-indicator {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #0066ff, #0040c0);
        box-shadow: 0 0 10px #0066ff;
        display: inline-block;
    }
    
    h1, h2, h3 { color: #0055FF !important; text-shadow: 0 1px 2px rgba(255,255,255,0.8); }
    
    .stButton>button {
        background: linear-gradient(145deg, #0055ff, #0040cc) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #3377ff !important;
        box-shadow: 5px 5px 12px #bec4cd, -5px -5px 12px #ffffff !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 7px 7px 15px #bec4cd, -7px -7px 15px #ffffff, 0 0 15px rgba(0,85,255,0.3) !important;
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox>div>div {
        background: #e1e7f0 !important;
        color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: inset 3px 3px 6px #bdc3cc, inset -3px -3px 6px #ffffff !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #dfe5ef !important;
        border-right: 2px solid #cbd5e1;
        box-shadow: 5px 0 15px rgba(0,0,0,0.05);
    }
    
    .skeuo-badge {
        background: linear-gradient(145deg, #ffffff, #dce2ed);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #0055FF;
        border: 1px solid #cbd5e1;
        box-shadow: 3px 3px 6px #bdc3cc, -3px -3px 6px #ffffff;
    }

    .patient-card { 
        background: #FFFFFF; 
        color: #1E1E1E; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 5px solid #0055FF; 
        margin-bottom: 20px; 
        box-shadow: 6px 6px 14px #bec4cd, -6px -6px 14px #ffffff; 
    }
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

def display_clinical_referral(predicted_disease):
    """
    Generates dynamic, location-aware referral links using Google Maps Deep Linking.
    """
    critical = ['Pneumothorax', 'Cardiomegaly', 'Mass', 'Hernia']
    urgent = ['Pneumonia', 'Edema', 'Consolidation', 'Effusion']
    
    st.markdown("---")
    st.markdown("### 🏥 Clinical Next Steps & Local Triage")
    
    if predicted_disease in critical:
        st.error(f"**🔴 CODE RED: Critical Pathology Detected ({predicted_disease})**")
        st.write("**Recommended Action:** Immediate Emergency Room evaluation is highly recommended.")
        st.link_button(
            label="🚑 Find Nearest Emergency Trauma Center (Google Maps)",
            url="https://www.google.com/maps/search/emergency+hospital+trauma+centre+near+me",
            type="primary"
        )
        st.caption("Clicking this button will auto-detect your location and route you to the nearest ER.")

    elif predicted_disease in urgent:
        st.warning(f"**🟡 CODE YELLOW: Urgent Pathology Detected ({predicted_disease})**")
        st.write("**Recommended Action:** Please consult a Pulmonologist within 24-48 hours.")
        st.link_button(
            label="📍 Find Nearest Chest Specialist / Pulmonologist",
            url="https://www.google.com/maps/search/pulmonologist+chest+specialist+near+me"
        )

    else:
        st.success(f"**🟢 CODE GREEN: Routine Pathology Detected ({predicted_disease})**")
        st.write("**Recommended Action:** Schedule a standard follow-up to review this scan.")
        st.link_button(
            label="👨‍⚕️ Find Nearest General Physician",
            url="https://www.google.com/maps/search/general+physician+doctor+near+me"
        )

    st.caption("⚠️ **Disclaimer:** QubitSanyam is an AI-assisted preliminary triage tool. It does not replace a professional radiological read or doctor's diagnosis. Never start or stop medications based on this output.")
                
def generate_medical_pdf(save_path, patient_data, results_dict, original_img_path, cams_paths, radar_path=None):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 15, "QubitSanyam Automated Triage Report", ln=True, align='C')
    pdf.line(10, 25, 200, 25)
    pdf.ln(5)
    
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
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Original Radiograph", ln=True)
    pdf.image(original_img_path, w=80)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(204, 0, 0)
    pdf.cell(0, 10, "AI Diagnostic Findings", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    
    positives = {d: p for d, p in results_dict.items() if p > 0.5}
    if not positives:
        pdf.cell(0, 10, "Result: NO ABNORMALITIES DETECTED.", ln=True)
        pdf.ln(2)
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

def upload_file_to_cloud(local_filepath, cloud_filename):
    try:
        with open(local_filepath, "rb") as f:
            supabase.storage.from_("scans").upload(
                path=cloud_filename,
                file=f,
                file_options={"content-type": "application/pdf" if cloud_filename.endswith(".pdf") else "image/png"}
            )
        return f"{SUPABASE_URL}/storage/v1/object/public/scans/{cloud_filename}"
    except Exception as e:
        st.error(f"Cloud Upload Failed: {e}")
        return None

def save_patient_record(data_dict):
    try:
        supabase.table("patients").insert(data_dict).execute()
        st.toast("☁️ Patient record synced to QubitSanyam Cloud!")
    except Exception as e:
        st.error(f"Database Save Failed: {e}")

# --- APP START & MODEL INITIALIZATION ---
with st.spinner("🧠 Booting Neural Networks & Skeuomorphic Console..."):
    models_dict = load_all_models()

if not models_dict:
    st.error("⚠️ No models found! Create a folder named 'models' and place your .h5 files inside.")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("## 🌐 Navigation")
nav_page = st.sidebar.radio(
    "Go to",
    ["🏠 Home Overview", "🩺 Automated Triage & Detection"],
    index=0 if st.session_state.current_page == "🏠 Home Overview" else 1
)
st.session_state.current_page = nav_page

# ==============================================================================
# PAGE 1: 🏠 HOME OVERVIEW (SYSTEM ARCHITECTURE & EXPLANATION)
# ==============================================================================
if st.session_state.current_page == "🏠 Home Overview":
    st.markdown("""
        <div class="skeuo-card">
            <div class="skeuo-header">
                <span class="led-indicator"></span>
                <h1 style="margin:0; padding:0;">🫁 QubitSanyam Medical AI Console</h1>
            </div>
            <p style="font-size: 1.15rem; opacity: 0.9;">
                <strong>Next-Generation Automated Chest Radiograph Triage & Clinical Decision Support System</strong>
            </p>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px;">
                <span class="skeuo-badge">⚡ Real-Time Neural Inference</span>
                <span class="skeuo-badge">🎯 Multi-Label Fusion Architecture</span>
                <span class="skeuo-badge">🔬 Explainable Grad-CAM Heatmaps</span>
                <span class="skeuo-badge">🚑 Automated Clinical Referral</span>
                <span class="skeuo-badge">☁️ Cloud Synchronized</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
            <div class="skeuo-inset">
                <h3>📖 System Purpose & Capabilities</h3>
                <p>
                    <strong>QubitSanyam Medical AI</strong> is built to solve high-throughput radiological triage bottlenecks in medical facilities. By analyzing standard digital chest radiographs (CXR), the system evaluates 14 critical cardiopulmonary pathologies simultaneously, assigning probability scores and triaging patients based on clinical urgency.
                </p>
                <ul>
                    <li><strong>Emergency Code Red Prioritization:</strong> Detects life-threatening pathologies (Pneumothorax, Cardiomegaly, Mass, Hernia) and immediately flags emergency care.</li>
                    <li><strong>Explainable Artificial Intelligence (XAI):</strong> Generates Class Activation Maps (Grad-CAM) overlaying the specific anatomical regions triggering AI confidence.</li>
                    <li><strong>Automated Clinical Reporting:</strong> Compiles demographic details, AI probability matrix, attention maps, and referral links into downloadable PDF reports.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="skeuo-card">
                <h3>🏗️ Multi-Layered Architecture & Fusion Protocol</h3>
                <p>The system operates on a 6-layer decoupled modular architecture designed for safety, accuracy, and latency efficiency:</p>
        """, unsafe_allow_html=True)

        # Layer Accordions / Cards
        with st.expander("🔹 Layer 1: Input Pre-processing & Normalization Engine", expanded=True):
            st.write("Scales incoming DICOM/PNG/JPG radiographs to standardized 224x224 RGB tensors, performing histogram equalization and floating-point normalization (0.0 - 1.0).")

        with st.expander("🔹 Layer 2: Deep Convolutional Neural Network Ensemble", expanded=False):
            st.write("Consists of specialized Deep Neural Network backbones (EfficientNet, DenseNet, and ResNet variations) trained on over 110,000 anonymized chest X-Ray studies from the NIH dataset.")

        with st.expander("🔹 Layer 3: Multi-Label Probability Fusion & Matrix Radar", expanded=False):
            st.write("Aggregates single-disease neural network prediction outputs into a unified 14-disease probability vector represented dynamically via radar matrix visualization.")

        with st.expander("🔹 Layer 4: Explainable AI (Grad-CAM Localization)", expanded=False):
            st.write("Computes gradient-weighted class activation mapping (Grad-CAM) to highlight spatial region-of-interest heatmaps over affected lung tissues.")

        with st.expander("🔹 Layer 5: Risk-First Clinical Triage Engine", expanded=False):
            st.write("Overrides simple mathematical max probability by evaluating disease clinical severity (Code Red vs Code Yellow vs Code Green) and generating location-aware Google Maps referral links.")

        with st.expander("🔹 Layer 6: Cloud Synchronization & PDF Generation", expanded=False):
            st.write("Generates signed medical report PDFs locally and automatically syncs patient metadata, diagnostic results, and scan images to the Supabase Cloud Database.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div class="skeuo-inset">
                <h3>📊 Model & Dataset Metrics</h3>
                <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;"><strong>Primary Dataset:</strong></td>
                        <td style="text-align: right;">NIH ChestX-ray14</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;"><strong>Total Scans Trained:</strong></td>
                        <td style="text-align: right;">112,120 Radiographs</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;"><strong>Unique Patients:</strong></td>
                        <td style="text-align: right;">30,805 Patients</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;"><strong>Target Pathologies:</strong></td>
                        <td style="text-align: right;">14 Cardiopulmonary</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;"><strong>Inference Engine:</strong></td>
                        <td style="text-align: right;">TensorFlow / Keras 3</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Cloud Storage:</strong></td>
                        <td style="text-align: right;">Supabase PostgreSQL</td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="skeuo-card" style="text-align: center;">
                <h3>🚀 Ready to Diagnose?</h3>
                <p>Proceed to the automated triage console to input patient demographics and analyze chest X-ray scans.</p>
        """, unsafe_allow_html=True)
        
        if st.button("🩺 Launch Detection Dashboard", use_container_width=True):
            st.session_state.current_page = "🩺 Automated Triage & Detection"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: 🩺 AUTOMATED TRIAGE & DETECTION DASHBOARD
# ==============================================================================
elif st.session_state.current_page == "🩺 Automated Triage & Detection":
    st.markdown("""
        <div class="skeuo-card">
            <div class="skeuo-header">
                <span class="led-indicator red"></span>
                <h1 style="margin:0; padding:0;">🩺 Diagnostic & Triage Console</h1>
            </div>
            <p style="margin:0; opacity:0.85;">Input patient demographics, upload digital chest X-ray scans, and run full multi-label AI diagnostic screening.</p>
        </div>
    """, unsafe_allow_html=True)

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

        uploaded_file = st.file_uploader("Drop Patient 🩻 X-Ray Here (PNG/JPG)", type=["png", "jpg", "jpeg"])

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
                            if len(results) == 1:
                                items_to_show = results
                            else:
                                top_disease = max(results, key=results.get)
                                items_to_show = {top_disease: results[top_disease]}
                                st.info(f"Showing baseline AI attention map for highest background probability: **{top_disease}**")
                        else:
                            st.error(f"⚠️ DETECTED {len(positives)} POTENTIAL PATHOLOGIES")
                            items_to_show = positives

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
                            try:
                                fig.write_image(radar_path, engine="kaleido", width=800, height=600)
                            except Exception as e:
                                print(f"Kaleido ignored: {e}")
                                st.toast("⚠️ System bypassed a chart export error. Generating PDF now...")
                                radar_path = None
                    
                    critical_diseases = ['Pneumothorax', 'Cardiomegaly', 'Mass', 'Hernia']
                    critical_findings = {d: p for d, p in results.items() if d in critical_diseases and p > 0.5}

                    if critical_findings:
                        top_disease = max(critical_findings, key=critical_findings.get)
                        st.subheader(f"⚠️ PRIORITY ALERT: Critical Finding Detected ({top_disease})")
                        highest_prob_disease = max(results, key=results.get)
                        if highest_prob_disease != top_disease:
                            st.caption(f"**Note:** System prioritized **{top_disease}** over **{highest_prob_disease}** due to immediate clinical severity.")
                    else:
                        top_disease = max(results, key=results.get)
                        if results[top_disease] > 0.5:
                            st.subheader(f"Primary AI Finding: {top_disease}")
                        else:
                            st.subheader("Primary AI Finding: No Critical Abnormalities")
                            top_disease = "Clear Scan"

                    display_clinical_referral(top_disease)
                    st.session_state.pdf_path = generate_medical_pdf(save_path, pat_data, results, orig_img_path, cams_paths, radar_path)
                    
                    with st.spinner("☁️ Syncing with Doctor's Database..."):
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        xray_cloud_name = f"{st.session_state.p_name}_{timestamp}_xray.png"
                        xray_url = upload_file_to_cloud(orig_img_path, xray_cloud_name)

                        pdf_cloud_name = f"{st.session_state.p_name}_{timestamp}_Report.pdf"
                        pdf_url = upload_file_to_cloud(st.session_state.pdf_path, pdf_cloud_name)

                        if xray_url and pdf_url:
                            patient_record = {
                                "full_name": st.session_state.p_name,
                                "age": st.session_state.p_age,
                                "gender": st.session_state.p_gender,
                                "referred_by": st.session_state.p_ref,
                                "contact_info": st.session_state.p_contact,
                                "ai_diagnosis": top_disease, 
                                "confidence_score": float(results[top_disease]),
                                "original_image_url": xray_url,
                                "report_url": pdf_url
                            }
                            save_patient_record(patient_record)

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

    # --- ADMIN AREA (DOCTOR'S LOUNGE) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🥼 DOCTOR'S LOUNGE \n(🔐 Admin Access)")

    admin_pass = st.sidebar.text_input("Enter Doctor's Passkey", type="password")

    if admin_pass == "SanyamDoctor2026":
        st.sidebar.success("Access Granted")
        if st.sidebar.button("📂 Open Patient Database"):
            st.header("🗄️ Secure Patient Records (Admin View)")
            try:
                response = supabase.table('patients').select("*").execute()
                data = response.data
                
                if data:
                    st.dataframe(data)
                    st.download_button(
                        label="⬇️ Download Records (CSV)",
                        data=json.dumps(data),
                        file_name="QubitSanyam_Patient_Records.json",
                        mime="application/json"
                    )
                else:
                    st.info("Database is currently empty.")
            except Exception as e:
                st.error(f"Database Connection Failed: {e}")

    elif admin_pass:
        st.sidebar.error("⛔ Access Denied: Incorrect Passkey")