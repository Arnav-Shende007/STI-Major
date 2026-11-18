# Explainable Multimodal STI Decision Support & AMR-Aware Guidance System

**B.Tech Research Project — Technical Artifacts & Decision Support Dashboard**

An end-to-end multimodal clinical decision support system combining deep visual lesion feature extraction (**ResNet-18**), categorical clinical priors (**Anatomical Site & Demographics**), visual explainability (**Grad-CAM & Saliency Contour Segmentation**), and dynamic antimicrobial-resistance (**AMR**)-aware treatment ranking powered by 25 years of CDC GISP surveillance data (1999–2023).

---

## 🚀 Manual Steps to Run

### Step 1: Environment Setup & Python Dependencies
Ensure **Python 3.10+** is installed on your machine. Install the required backend dependencies:

```bash
pip install -r requirements.txt
```

---

### Step 2: Launch the System

You have two manual options to run the application:

#### Option A: Unified Full-Stack Server (Recommended — Single Command)
Flask serves both the compiled high-performance React dashboard and the backend API on a single port:

```bash
python backend_api.py
```

Once started, open your web browser and navigate to:
👉 **`http://localhost:8000`** *(or `http://127.0.0.1:8000`)*

---

#### Option B: Independent Development Mode (Hot Reload)
If you wish to make live modifications to the React code with instant hot-module replacement (HMR):

1. **Terminal 1 — Start the Python Backend API:**
   ```bash
   python backend_api.py
   ```

2. **Terminal 2 — Start the React Vite Development Server:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Once started, open your web browser and navigate to:
👉 **`http://localhost:3000`**

*(Note: If you modify the React frontend and wish to update the static build served by Flask in Option A, simply run `npm run build` inside the `frontend/` directory).*

---

## 🩺 System Capabilities & Architecture

| Module | Implementation | Description |
| :--- | :--- | :--- |
| **Visual Feature Extractor** | ResNet-18 (512-d) | Pre-trained on ImageNet, fine-tuned on clinical lesion imagery, outputting high-level morphological feature maps. |
| **Clinical Prior Embedding** | Categorical MLP (64-d) | One-hot vectorized patient context (19-d: Anatomical Location, Site Group, Gender) embedded into a 64-d representation. |
| **Multimodal Fusion Head** | Linear Concatenation (576-d) | Fuses visual (512-d) + clinical (64-d) vectors $\to$ Linear(576, 128) $\to$ ReLU $\to$ Dropout(0.3) $\to$ 6 disease classes. |
| **Visual Explainability (XAI)** | Grad-CAM + OpenCV Contours | Gradient-weighted class activation maps hooked to `layer4[1].conv2`, generating saliency heatmaps, bounding boxes, centroid coordinates, and field coverage %. |
| **Modality Attribution** | Gradient-based Sensitivity | Quantifies the relative contribution of visual image features vs anatomical site context vs patient demographics. |
| **Smart AMR Recommendation** | CDC GISP Engine (1999–2023) | Real-time mathematical scoring adjusting therapy suitability according to longitudinal resistance trends and contraindications. |

---

## 🔬 Mathematical Formulation: Longitudinal AMR Suitability

The smart recommendation engine dynamically calculates regimen suitability $S(d, t)$ for drug $d$ at surveillance year $t$:

$$\text{Suitability}(d, t) = \max\Big(0, \, \min\big(100, \, E_{\text{base}}(d) - \mathcal{P}_{\text{AMR}}(d, t) - P_{\text{contra}}\big)\Big)$$

Where:
- $E_{\text{base}}(d)$: Frontline clinical cure rate (%) from clinical trial baselines.
- $\mathcal{P}_{\text{AMR}}(d, t)$: Longitudinal resistance penalty computed as:
  $$\mathcal{P}_{\text{AMR}}(d, t) = \alpha \cdot R(d, t) + \beta \cdot \max(0, \Delta R_{5\text{yr}}(d, t))$$
  - $R(d, t)$: Point resistance percentage at year $t$.
  - $\Delta R_{5\text{yr}}(d, t) = R(d, t) - R(d, t-5)$: 5-year longitudinal resistance velocity.
  - $\alpha = 1.2$, $\beta = 0.8$: Trajectory weighting coefficients.
- $P_{\text{contra}}$: Severe contraindication deduction ($100\%$ penalty triggered by confirmed drug allergy or pregnancy risks).

---

## 📊 Master Ablation Study (Held-Out Test Cohort)

Evaluation across held-out stratified test cases (63 patients) demonstrating cross-modal synergy:

| Architecture / Modality Configuration | Test Accuracy (%) | Macro F1 | Macro Precision | Macro Recall | Relative Gain |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Baseline 1: Image-only (ResNet-18) | 36.51% | 0.2945 | 0.3020 | 0.2905 | Benchmark |
| Baseline 2: Metadata-only (Clinical MLP) | 25.40% | 0.2036 | 0.2259 | 0.3487 | -11.11% |
| Ablation A: Image + Gender (No Site) | 42.86% | 0.3666 | 0.4422 | 0.3540 | +6.35% |
| Ablation B: Image + Anatomical Site (No Gender) | 44.44% | 0.3557 | 0.3681 | 0.3498 | +7.93% |
| **Proposed: Multimodal Fusion (Image + Site + Gender)** | **46.03%** | **0.3844** | **0.4615** | **0.3634** | **+9.52%** |

---

## 📁 Repository Structure

```
Review 3/
├── backend_api.py             # Flask REST API + Static Frontend Server (Single-port runner)
├── requirements.txt           # Python dependencies
├── README.md                  # System documentation & manual run steps
├── frontend/                  # Modern React 19 + Vite Web Application
│   ├── src/
│   │   ├── App.jsx            # Main React Dashboard (Diagnosis, Benchmarks, AMR, Cohort)
│   │   ├── index.css          # Dark medical glassmorphic CSS theme
│   │   └── main.jsx           # React DOM root entrypoint
│   ├── dist/                  # Production-compiled single-bundle static assets
│   ├── package.json           # Node.js project manifest & scripts
│   └── vite.config.js         # Vite bundler configuration
├── src/
│   ├── dataset.py             # Dataset loader, 19-d metadata encoding, stratified split, class weights
│   ├── models.py              # PyTorch ResNet-18 visual extractor, Clinical MLP, and Fusion head
│   ├── explainability.py      # Grad-CAM, OpenCV contour segmentation, Modality Attribution
│   ├── treatment_amr.py       # CDC 2021/2026 guidelines & CDC GISP longitudinal calculation service
│   └── train_and_evaluate.py  # Model training, test evaluation, ablation tables, metrics export
├── saved_models/
│   ├── multimodal_best.pth    # Trained PyTorch weights for proposed fusion network
│   ├── image_only_best.pth    # Trained baseline weights
│   ├── features_cache.npz     # Cached 512-d ResNet-18 visual vectors
│   ├── ablation_study.csv     # Master ablation study table
│   ├── metrics_summary.json   # Precision, recall, F1, and confusion matrix data
│   └── confusion_matrix.png   # 6-class multimodal test confusion matrix
└── STI_Project/
    ├── 01_STIAtlas/           # 314 verified clinical photographs and manifest
    └── 03_GISP/               # 2,511 longitudinal CDC GISP resistance records (1999–2023)
```

---

## 🛡️ Academic & Presentation Standards

- **Clean Anatomical Terminology:** All anatomical locations and preset clinical benchmarks use discreet, non-explicit terminology suitable for academic reviews (*e.g., Oral Mucosa / Lip, Cutaneous Skin, Upper Body / Torso, Flexural Fold, Mucocutaneous Transition Zone*).
- **Strict Quality Control:** 316 downloaded images $\to$ 2 non-lesion microscopy slides excluded $\to$ 314 verified clinical cases across 6 target disease classes with zero duplicate image hashes.
