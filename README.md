```markdown
# 🫁 QubitSanyam Medical AI: Automated X-Ray Triage System

An enterprise-grade, full-stack Deep Learning application designed to perform automated triage and clinical reporting on Chest Radiographs. Built using a custom Triple-Ensemble architecture, this system analyzes NIH Chest X-Ray data to detect 14 distinct pulmonary pathologies and generates interpretable Explainable AI (XAI) visualizations.

![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16.1-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

---

## 🏗️ System Architecture & Workflow

flowdiagrams/NIH_chestxrays.drawio (2).png


### 1. High-Level Data Pipeline

flowdiagrams/NIH (1).jpg


### 2. Triple-Ensemble AI Architecture

flowdiagrams/NIH (4).jpg


---

## ✨ Key Features
* **Triple-Ensemble Engine:** Combines the textural pattern recognition of **VGG-19**, the spatial depth analysis of **ResNet-50**, and the multi-scale feature extraction of **Inception-V3**.
* **Explainable AI (Grad-CAM):** Generates baseline and localized heatmaps so clinicians can visually verify exactly where the AI is detecting pathological features.
* **Dual Diagnostic Modes:** Run a lightning-fast "Single Specialist" scan or execute the heavy "Full Panel (14-Disease)" triage protocol.
* **Enterprise Reporting System:** Automatically bundles patient demographics, clinical probability matrices, and visual XAI mappings into a downloadable, professional PDF.
* **Local Database Archiving:** Secures all patient runs, generated charts, and JSON data locally in a timestamped `Database/` architecture.
* **Dedicated Analytics Dashboard:** A standalone interactive metrics application powered by Scikit-Learn and Plotly to monitor system efficacy.

---

## 🧗‍♂️ Technical Hurdles & Engineering Solutions

Building this system required overcoming significant hardware and dependency challenges:

1. **The I/O Hardware Crash:** Initial attempts to locally duplicate and sort the 42GB+ NIH dataset resulted in a localized SSD failure. **Solution:** Completely rewrote the pipeline for cloud execution, building an "In-Memory Data Pipeline" on Kaggle to stream data directly to GPU RAM, bypassing disk writes entirely.
2. **Keras 3 vs TensorFlow 2.15 Silo:** Kaggle's backend stealth-updated to Keras 3, causing fatal deserialization errors (`batch_shape`, `DTypePolicy`) when loading `.h5` files locally. **Solution:** Executed a "nuclear sweep" of local dependencies, perfectly mirroring Kaggle's environment with a highly specific `tensorflow==2.16.1` and `numpy==1.26.4` stack.
3. **The Kaleido Windows Bug:** Background PDF graph generation caused Streamlit to silently deadlock due to a known Windows serialization bug in `kaleido`. **Solution:** Engineered a graceful fallback/muzzle using `try/except` blocks, allowing the system to skip the broken chart export while still successfully compiling the rest of the patient PDF.

---

## 📋 Prerequisites
Before you begin, ensure you have the following installed:
* **Python 3.11+**
* **Git**
* **Docker** (Optional, for containerized deployment)

---

## 🚀 Installation & Local Deployment

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/QubitSanyam_Medical_AI.git](https://github.com/yourusername/QubitSanyam_Medical_AI.git)
cd QubitSanyam_Medical_AI

```

### 2. Environment Setup

*Strict versioning is required to maintain Keras 3 compatibility with the pre-trained weights.*

```bash
pip install tensorflow==2.16.1 numpy==1.26.4 opencv-python==4.9.0.80 streamlit plotly fpdf scikit-learn pandas
```

*Note: If generating PDFs on Windows, install the stable Kaleido version: `pip install kaleido==0.1.0.post1*`

### 3. Load the Models

Create a folder named `models` in the root directory and place the 14 trained `.h5` model files inside.

```
QubitSanyam_Medical_AI/
│
├── models/
│   ├── QubitSanyam_Pneumonia.h5
│   ├── QubitSanyam_Cardiomegaly.h5
│   └── ... (12 others)

```

### 🐳 Docker Deployment (Recommended)
You can run the entire clinical triage system inside an isolated Docker container. 

1. **Build the Image:**
   ```bash
   docker build -t qubitsanyam-ai .

  

2. **Run the Container:**

```bash
docker run -p 8501:8501 qubitsanyam-ai

```

3. Open your browser and navigate to `http://localhost:8501`.


```markdown

## 📂 Output Data Architecture
When a scan is executed, the system automatically generates a local database architecture to store patient records securely:

```text
Database/
  └── John_Doe_20260302_143000/
      ├── patient_data.json       # Raw demographic data
      ├── original_xray.png       # Uploaded scan
      ├── cam_Pneumonia.png       # Generated Grad-CAM heatmaps
      ├── radar_chart.png         # Plotly probability matrix
      └── Medical_Report.pdf      # Final printable clinical report

```

   
### 4. Launch the Applications

**To run the Clinical Triage System:**

```bash
streamlit run app.py

```

**To view the Engineering Metrics Dashboard:**

```bash
streamlit run metrics_app.py

```

---

**Developed by Sanyam | Batch of 2023-2027**

