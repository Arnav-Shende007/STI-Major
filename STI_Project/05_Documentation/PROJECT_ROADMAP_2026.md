# Project Roadmap & Team Work Allocation (2026)

## An Explainable Multimodal Framework for STI Lesion Classification and Antimicrobial-Resistance-Aware Treatment Recommendation

**BTech Research Project Roadmap — 2026**  
**Project Lead:** Atharva  
**Team Size:** 4 Members  
**Project Deadline:** December 25, 2026  

---

### Project Overview
This BTech research project aims to develop a clinical decision-support framework that combines skin and anogenital lesion images with available clinical information. The system investigates multimodal classification, provides visual and tabular explanations for model predictions, and links outputs to authoritative clinical treatment guidelines and antimicrobial-resistance surveillance context.

*Note: Research prototype for academic purposes; not intended to replace qualified medical professionals or provide autonomous diagnosis/prescription.*

---

## 1. Problem, Proposed Idea and Objectives

### Problem
Sexually transmitted infections (STIs) and related anogenital skin lesions can be difficult to distinguish visually due to overlapping clinical presentations. In real-world clinical settings, visual examination alone is often insufficient, and diagnostic decisions rely heavily on patient history, anatomical site, and clinical context. Furthermore, post-diagnostic management requires consulting clinical guidelines and monitoring regional antimicrobial-resistance patterns.

### Proposed Idea
Our project aims to develop an explainable multimodal framework that combines lesion images with available clinical information and provides interpretable predictions together with guideline-based treatment information and AMR context where applicable.

### Objectives
1. **Lesion Classification:** Develop a model for classification of the selected STI/skin lesion classes.
2. **Multimodal Investigation:** Investigate whether available clinical information can improve image-based classification.
3. **Model Interpretability:** Provide understandable explanations for model predictions.
4. **Treatment Guidance:** Connect predictions with authoritative treatment guidance.
5. **AMR Integration:** Incorporate antimicrobial-resistance information where it is relevant.

---

## 2. Current Project Status

### STIAtlas Dataset
The primary dataset is derived from the Melbourne Sexual Health Centre (MSHC) STIAtlas library.

| Disease Class | Discovered Count |
| :--- | :---: |
| **Early Syphilis** | 112 |
| **Genital Warts** | 86 |
| **Herpes Simplex** | 64 |
| **Lichen Sclerosus** | 35 |
| **Molluscum Contagiosum** | 12 |
| **Tinea** | 7 |
| **Total Discovered** | **316** |

**Collection & Review Summary:**
* 316 images collected and downloaded successfully (0 failures, 0 corrupted, 0 duplicate hashes).
* 2 microscopy/non-lesion images were excluded (`STIATLAS_039`, `STIATLAS_133`).
* 2 clinical images with unresolved anatomical site were retained (`STIATLAS_114`, `STIATLAS_263`).
* **Final organized clinical dataset: 314 images across 6 target classes.**
* *Current state: Preprocessing, augmentation, balancing and train/validation/test splitting are yet to be completed.*

### Other Data Sources
* **DermNet:** Investigated as a supplementary source but currently excluded because its official licensing terms do not permit AI/ML training/testing use without appropriate permission. Kaggle DermNet copies are also excluded.
* **CDC GISP / CARGOS:** Official CDC antimicrobial resistance surveillance data has been processed separately, containing 2,511 records related to *Neisseria gonorrhoeae* across four antimicrobials (Ceftriaxone, Cefixime, Azithromycin, and Ciprofloxacin).
* *Note: GISP/CARGOS is an independent AMR evidence source and is not used as a resistance label for the six STIAtlas image classes.*

---

## 3. Project Roadmap

| Dates (2026) | Phase | Goal & Deliverables |
| :--- | :--- | :--- |
| **Sep 5–15** | Literature Review | 20+ genuine research papers and initial research-gap analysis. |
| **Sep 16–25** | Research Gap + Architecture | Finalize problem definition, research objectives, and system design. |
| **Sep 26–Oct 10** | Dataset Preprocessing + Baseline | Clean dataset, leakage-free data split, and baseline model development. |
| **Oct 11–25** | Image Classification | Develop, fine-tune, and evaluate six-class image classification models. |
| **Oct 26–Nov 8** | Multimodal Module | Combine image and available clinical information; evaluate fusion. |
| **Nov 9–20** | Explainability | Implement and evaluate suitable visual and tabular XAI methods. |
| **Nov 21–Dec 5** | Treatment + AMR | Guideline-based treatment mapping and separate AMR evidence integration. |
| **Dec 6–12** | System Integration | Build end-to-end working research prototype. |
| **Dec 13–18** | Evaluation | Metrics, comparative analysis, ablation studies, and error analysis. |
| **Dec 19–22** | Paper + Documentation | Final research paper manuscript and project documentation. |
| **Dec 23–25** | Finalization | Presentation slides, demonstration, viva preparation, and submission. |

---

## 4. Team Responsibilities

| Role / Member | Key Responsibilities | Primary Ownership |
| :--- | :--- | :--- |
| **Member 1**<br>Dataset + ML | • Dataset cleaning and preprocessing<br>• Data splitting and leakage prevention<br>• Class imbalance handling<br>• Baseline and image classification models<br>• Vision evaluation metrics and error analysis | Image classification pipeline |
| **Member 2**<br>Multimodal AI | • Clinical metadata and text processing<br>• Feature representation and encoding<br>• Image + clinical information fusion<br>• Multimodal comparison experiments<br>• Ablation studies | Multimodal learning pipeline |
| **Member 3**<br>XAI + Interface | • Explainability methods (Grad-CAM / Grad-CAM++)<br>• Tabular SHAP/LIME where appropriate<br>• Explanation visualizations<br>• Prediction confidence display<br>• Prototype frontend/demo interface | Explainability & presentation layer |
| **Atharva**<br>Project Lead | • Literature review coordination<br>• Research-gap analysis and overall architecture<br>• CDC GISP / AMR integration<br>• WHO/CDC treatment guideline mapping<br>• System integration and project documentation<br>• Professor updates and final presentation coordination | Research direction, integration & AMR/treatment component |

---

## 5. Literature Review Plan

The literature review focuses on four core areas: (1) STI and dermatological lesion image classification, (2) Multimodal medical machine learning, (3) Explainable AI in clinical decision support, and (4) Antimicrobial resistance surveillance and treatment guidance.

| No. | Paper | Year | Area | Relevance to Project |
| :-: | :--- | :-: | :--- | :--- |
| **1** | Esteva et al. (*Nature*) | 2017 | Image Classification | Foundation for deep transfer learning in dermatological lesion diagnosis. |
| **2** | Mahbod et al. (*CMPB*) | 2020 | Image Classification | Multi-scale transfer learning strategies on medical image datasets. |
| **3** | Krammer et al. (*JEADV*) | 2022 | Image Classification | Label-efficient learning on dermatological lesions with limited data. |
| **4** | Hu et al. (*IEEE EMBC*) | 2022 | Image Classification | Feature representation and pooling methods on imbalanced lesion classes. |
| **5** | Shetty et al. (*Sci Rep*) | 2022 | Image Classification | Benchmark training and augmentation protocols for multi-class skin lesions. |
| **6** | Baltrušaitis et al. (*IEEE TPAMI*) | 2019 | Multimodal AI | Comprehensive taxonomy and formal foundations for multimodal fusion. |
| **7** | Zhang et al. (*PMLR / MLHC*) | 2022 | Multimodal AI | Contrastive representation learning from paired medical images and text. |
| **8** | Wang et al. (*EMNLP*) | 2022 | Multimodal AI | Cross-modal representation learning from medical images and clinical text. |
| **9** | Lyu et al. (*AMIA*) | 2022 | Multimodal AI | Fusing structured clinical patient data with unstructured clinical text notes. |
| **10** | Mi et al. (*CBM*) | 2022 | Multimodal AI | Multimodal medical fusion architecture incorporating explainability modules. |
| **11** | Selvaraju et al. (*IEEE ICCV*) | 2017 | Explainable AI | Visual explanations from deep networks via gradient-based localization (Grad-CAM). |
| **12** | Chattopadhyay et al. (*IEEE WACV*) | 2018 | Explainable AI | Grad-CAM++ for improved multi-instance and localized visual explanations. |
| **13** | Lundberg & Lee (*NeurIPS*) | 2017 | Explainable AI | Unified game-theoretic framework (SHAP) for interpreting feature contributions. |
| **14** | Abhishek et al. (*Sci Rep*) | 2021 | Clinical AI | Predicting clinical management decisions directly from lesion images. |
| **15** | Shafiq et al. (*Skin Res Technol*) | 2024 | Explainable AI | Vision Transformer with Grad-CAM [Retracted; studied for validation rigor]. |
| **16** | Soe et al. (*Commun Med*) | 2025 | STI Clinical AI | Evaluates deep learning on MSHC sexual health lesions; highlights clinical gaps. |
| **17** | Liu et al. (*Lancet Digit Health*) | 2025 | STI Review | Systematic review & meta-analysis of STI lesion AI; identifies critical integration gaps. |
| **18** | Martin et al. (*Ann NY Acad Sci*) | 2023 | AMR Surveillance | Machine learning models for *Neisseria gonorrhoeae* antimicrobial susceptibility. |
| **19** | Ha et al. (*Microbiol Spectr*) | 2023 | AMR Genomics | Machine learning for ceftriaxone resistance prediction in *N. gonorrhoeae*. |
| **20** | Tschandl et al. (*Sci Data*) | 2018 | Benchmark Dataset | HAM10000 dataset; benchmark standards for metadata curation and validation. |

---

## 6. Research Gap & Proposed System

### Research Gap
Existing research has explored STI/skin-lesion image classification, multimodal medical AI, explainability, clinical management, and antimicrobial-resistance surveillance as separate domains. However, these components are rarely integrated into a cohesive workflow. 

Our project investigates a decision-support framework that connects:
* Lesion image evidence
* Available clinical information (anatomical site, gender, clinical text)
* Visual and tabular explainability
* Guideline-based treatment information
* Antimicrobial-resistance surveillance context where applicable

*Note: The exact research gap will be refined during the literature review phase. The framework is proposed as an investigational prototype and is not claimed to be inherently superior prior to experimental validation.*

### Conceptual System Architecture

```
Lesion Image + Available Clinical Information
                     ↓
Image Model + Clinical Information Processing
                     ↓
             Multimodal Fusion
                     ↓
                 Prediction
                     ↓
                Explanation
                     ↓
   Guideline-Based Treatment Information
                     ↓
       AMR Context Where Applicable
                     ↓
           Decision-Support Output
```

---

## 7. Implementation & Evaluation Plan

### Implementation Steps
1. **Dataset Preprocessing:** Cleaning, verification, and reproducible standardization.
2. **Data Splitting:** Stratified, leakage-free train/validation/test partitions.
3. **Baseline Model:** Non-pretrained baseline CNN to establish initial benchmark.
4. **Image Classification Experiments:** Transfer learning and class-imbalance exploration.
5. **Clinical Metadata/Text Processing:** Feature encoding for tabular site/gender and text.
6. **Multimodal Fusion:** Cross-modal fusion combining visual and clinical representations.
7. **Explainability Layer:** Grad-CAM/Grad-CAM++ heatmaps and tabular SHAP attributions.
8. **Treatment Engine:** Deterministic mapping to published WHO/CDC guidelines.
9. **AMR Module:** Longitudinal surveillance querying for *N. gonorrhoeae* (CDC GISP).
10. **Prototype Interface:** Unified dashboard for interactive clinical exploration.

### Evaluation Metrics & Comparisons
* **Performance Metrics:** Accuracy, Precision, Recall, F1-score, Macro F1, Per-class metrics, Confusion matrix, and ROC-AUC where appropriate.
* **Comparative Studies:** Image-only vs. Metadata/Text-only vs. Multimodal model.
* **Ablation Studies:** Quantifying the performance impact of individual modalities.
* **Error Analysis:** Categorizing failure cases across lesion types and anatomical sites.

---

## 8. Treatment, AMR & Development Approach

### Guideline-Based Treatment
Treatment information will be mapped deterministically from authoritative clinical sources such as the World Health Organization (WHO) and the Centers for Disease Control and Prevention (CDC) STI Treatment Guidelines. The system presents guideline-based therapeutic references rather than autonomously prescribing medication.

### Antimicrobial Resistance (AMR)
AMR information is handled as a separate evidence component, specifically for *Neisseria gonorrhoeae* using official CDC GISP / CARGOS surveillance data (2,511 records). GISP data is not used as a training label for the six STIAtlas image classes. Missing surveillance values are strictly preserved.

### Incremental Development Approach
Development follows an iterative, version-controlled engineering cycle:
$$\text{Implement} \longrightarrow \text{Test} \longrightarrow \text{Review} \longrightarrow \text{Commit} \longrightarrow \text{Push} \longrightarrow \text{Document}$$

All progress is committed in meaningful, verifiable milestones rather than as a single monolithic release.

---

## 9. Expected Deliverables & Limitations

### Expected Deliverables
1. Clean and reproducible dataset preprocessing and splitting pipeline.
2. Trained six-class image classification model.
3. Multimodal fusion model combining image and clinical information.
4. Visual (Grad-CAM/Grad-CAM++) and tabular (SHAP) explainability modules.
5. Guideline-based treatment reference engine.
6. CDC GISP / CARGOS antimicrobial resistance surveillance component.
7. Interactive demonstration dashboard.
8. Final BTech research paper, technical documentation, and presentation deck.

### Main Project Limitations
* **Small Dataset Size:** The primary image dataset is limited to 314 clinical photographs.
* **Class Imbalance:** Significant disparity between majority classes (Syphilis: 110) and minority classes (Tinea: 7).
* **Sparse Metadata:** Clinical descriptions and metadata are concise and partially missing across records.
* **Licensing Restrictions:** Supplementary repositories (such as DermNet) remain excluded due to licensing constraints.
* **AMR Scope:** Surveillance data is biologically specific to *N. gonorrhoeae* and does not cover the six visual skin lesion classes.
* **Lack of In-Vivo Validation:** The system is an academic research prototype and has not undergone clinical trials.

### Concluding Note
This project is an academic research prototype. Results should be interpreted as experimental and must not be used as a substitute for professional medical diagnosis, clinical judgment, or treatment.
