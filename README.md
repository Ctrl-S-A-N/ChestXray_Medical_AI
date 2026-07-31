# 🫁 QubitSanyam Medical AI: Automated X-Ray Triage System

An enterprise-grade, full-stack Deep Learning application designed to perform automated triage and clinical decision support on Chest Radiographs. Featuring a sleek **Skeuomorphic Console Design**, **2-Page System Architecture**, **Supabase Cloud Synchronization**, and **Render 1-Click Deployment**, this system analyzes NIH Chest X-Ray data to detect 14 distinct pulmonary pathologies and generates interpretable Explainable AI (XAI) visualizations.

![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Cloud](https://img.shields.io/badge/Supabase-Cloud%20Database-emerald)
![Deployment](https://img.shields.io/badge/Render-Live%20Deployment-purple)

---

## 🎨 Design & Navigation Architecture

### 1. Skeuomorphic Medical Console
- **Tactile 3D Controls:** Dual-shadowed hardware cards, inset input fields, embossed typography, and raised metallic action buttons.
- **Hardware Status LEDs:** Glowing radial-gradient LED indicators (Cyan, Green, Amber, Red) providing instant visual status.
- **Adaptive Dark & Light Themes:** Custom dual-shadow palettes optimized for both Dark (`#12151b`) and Light (`#e6ecf5`) clinical lighting.

### 2. 2-Page App Layout
- 🏠 **Home Overview Page:** 
  - Comprehensive explanation of system capabilities and medical triage mission.
  - Interactive breakdown of the 6-layer system architecture (Pre-processing, CNN Ensemble, Multi-Label Probability Fusion, Grad-CAM XAI, Risk-First Triage, Cloud Database & PDF Engine).
  - NIH ChestX-ray14 dataset metrics and model specifications.
- 🩺 **Automated Triage & Detection Page:** 
  - Patient intake form with demographic locking and protocol selection.
  - Radiograph upload & multi-disease neural network inference.
  - Grad-CAM heatmap visualizations & Plotly radar probability matrix.
  - Risk-first clinical triage (Code Red ER / Code Yellow Pulmonologist / Code Green GP) with location-aware Google Maps deep-linking.
  - Printable PDF report generation and Doctor's Lounge Admin View (Passkey protected).

---

## 🏗️ Multi-Layered System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        QubitSanyam Medical AI                          │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Layer 1: Input Pre-processing & Normalization (224x224 RGB Tensors)   │
 └──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Layer 2: Multi-Backbone Deep Neural Network Ensemble                │
 └──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Layer 3: Multi-Label Probability Fusion & Matrix Radar System        │
 └──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Layer 4: Explainable AI (Grad-CAM Spatial Heatmap Localization)       │
 └──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Layer 5: Risk-First Clinical Triage & Google Maps Emergency Routing │
 └──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Layer 6: Cloud Synchronization (Supabase) & PDF Report Generation    │
 └──────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

* **Skeuomorphic User Interface:** Tactile 3D controls, inset panels, glowing status LEDs, and adaptive dark/light themes.
* **Multi-Model Ensemble Engine:** Combines deep neural network architectures trained on 112,120 anonymized chest radiographs from 30,805 unique patients.
* **Explainable AI (Grad-CAM):** Generates region-of-interest spatial heatmaps so clinicians can visually verify diagnostic findings.
* **Dual Diagnostic Modes:** Run a lightning-fast single disease scan or execute the full 14-disease panel scan.
* **Risk-First Clinical Triage:** Prioritizes critical emergency conditions (Pneumothorax, Cardiomegaly, Mass, Hernia) over simple probability max scores, routing patients to emergency care via Google Maps.
* **Supabase Cloud Sync:** Automatically uploads patient records, X-Ray images, and medical report PDFs to Supabase cloud storage & database.
* **Enterprise Reporting System:** Automatically compiles demographics, probability matrix, XAI maps, and referral links into downloadable PDF reports.
* **Doctor's Lounge Admin View:** Secure passkey-protected admin section for viewing and exporting patient records.

---

## 📋 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Ctrl-S-A-N/QubitSanyam_Medical_AI.git
cd QubitSanyam_Medical_AI
```

### 2. Environment Setup
Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Load Model Weights
Create a folder named `models` in the root directory and place the 14 trained `.h5` model files inside:
```
QubitSanyam_Medical_AI/
│
├── models/
│   ├── QubitSanyam_Pneumonia.h5
│   ├── QubitSanyam_Cardiomegaly.h5
│   └── ... (12 others)
```

### 4. Launch the Applications
Run the Clinical Triage Console:
```bash
streamlit run app.py
```

Run the Engineering Metrics Dashboard:
```bash
streamlit run metrics_app.py
```

---

## 🌐 Deployment Options

### ☁️ 1-Click Render Deployment (`render.yaml`)
This repository includes a `render.yaml` blueprint configured for instant deployment on Render:
1. Go to [Render Dashboard](https://dashboard.render.com/select-repo?type=web).
2. Connect repository **`Ctrl-S-A-N/QubitSanyam_Medical_AI`**.
3. Render auto-detects `render.yaml` and launches your Streamlit web service automatically.

### 🐳 Docker Deployment
```bash
# Build Docker image
docker build -t qubitsanyam-ai .

# Run container
docker run -p 8501:8501 qubitsanyam-ai
```
Access at `http://localhost:8501`.

---

## 📂 Output & Cloud Data Architecture

When a scan is executed, records are persisted both locally and to Supabase Cloud:

```text
Database/
  └── John_Doe_20260302_143000/
      ├── patient_data.json       # Demographic & diagnostic metadata
      ├── original_xray.png       # Uploaded radiograph
      ├── cam_Pneumonia.png       # Grad-CAM heatmap localization
      ├── radar_chart.png         # Plotly probability matrix
      └── Medical_Report.pdf      # Printable clinical report
```

---

**Developed by Sanyam | Batch of 2023-2027**
