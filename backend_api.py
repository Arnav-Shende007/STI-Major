"""
Flask Backend for the Modern React Multimodal Decision-Support System
"""

import os
import io
import base64
import json
import numpy as np
import pandas as pd
from PIL import Image
import torch
import cv2
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

from src.dataset import (
    encode_metadata,
    EVAL_TRANSFORM,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
    TOP_ANATOMICAL_SITES,
    GENDERS,
    SITE_GROUPS
)
from src.models import MultimodalFusionModel
from src.explainability import GradCAM, LesionSegmenter, MultimodalModalityExplainer
from src.treatment_amr import TREATMENT_GUIDELINES, CDCGISPService

dist_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
app = Flask(__name__, static_folder=dist_folder, static_url_path="")
CORS(app)

device = torch.device('cpu')
model = MultimodalFusionModel(meta_dim=19, num_classes=6, pretrained=False).to(device)
weights_path = 'saved_models/multimodal_best.pth'
if os.path.exists(weights_path):
    model.load_state_dict(torch.load(weights_path, map_location=device))
model.eval()

gradcam = GradCAM(model)
gisp_service = CDCGISPService()

# Benchmark Clinical Cases (Strictly Balanced Across All 6 Disease Classes)
CLEAN_PRESET_CASES = {
    "case_1": {
        "id": "case_1",
        "title": "Primary Syphilitic Chancre (Perioral)",
        "image_path": "STI_Project/01_STIAtlas/organized/Early_Syphilis/STIATLAS_171.jpg",
        "clean_site": "Oral Mucosa / Lip (Perioral)",
        "site_group": "Other Skin",
        "gender": "Male",
        "symptoms": "Indurated, clean-based solitary painless ulcer on the inner upper lip for 12 days",
        "actual_class": "Early_Syphilis",
        "clinical_note": "Classic primary syphilitic chancre presenting on oral mucosal epithelium."
    },
    "case_2": {
        "id": "case_2",
        "title": "Mucosal Papilloma (HPV / Condyloma)",
        "image_path": "STI_Project/01_STIAtlas/organized/Genital_Warts/STIATLAS_054.jpg",
        "clean_site": "Oral Mucosa / Lip (Perioral)",
        "site_group": "Other Skin",
        "gender": "Male",
        "symptoms": "Painless, flesh-colored exophytic verrucous papules in the oral cavity",
        "actual_class": "Genital_Warts",
        "clinical_note": "Focal oral condylomatous papilloma caused by mucosal HPV genotypes."
    },
    "case_3": {
        "id": "case_3",
        "title": "Herpes Simplex Vesicular Lesion (Cutaneous)",
        "image_path": "STI_Project/01_STIAtlas/organized/Herpes_Simplex/STIATLAS_020.jpg",
        "clean_site": "Cutaneous Skin - General (Trunk & Limbs)",
        "site_group": "Other Skin",
        "gender": "Male",
        "symptoms": "Recurrent stinging cluster of small erythematous fluid-filled vesicles and erosions",
        "actual_class": "Herpes_Simplex",
        "clinical_note": "Cutaneous manifestation of HSV with localized crusted vesicular activity."
    },
    "case_4": {
        "id": "case_4",
        "title": "Lichen Sclerosus Atrophic Plaque",
        "image_path": "STI_Project/01_STIAtlas/organized/Lichen_Sclerosus/STIATLAS_103.jpg",
        "clean_site": "Cutaneous Skin - General (Trunk & Limbs)",
        "site_group": "Other Skin",
        "gender": "Male",
        "symptoms": "Porcelain-white atrophic sclerotic plaque with epidermal thinning and focal purpura",
        "actual_class": "Lichen_Sclerosus",
        "clinical_note": "Chronic inflammatory dermatosis showing parchment-like ivory sclerosis."
    },
    "case_5": {
        "id": "case_5",
        "title": "Molluscum Umbilicated Papule",
        "image_path": "STI_Project/01_STIAtlas/organized/Molluscum_Contagiosum/STIATLAS_053.jpg",
        "clean_site": "Cutaneous Skin - General (Trunk & Limbs)",
        "site_group": "Other Skin",
        "gender": "Male",
        "symptoms": "Firm, dome-shaped pearly papules with characteristic central dell / umbilication",
        "actual_class": "Molluscum_Contagiosum",
        "clinical_note": "Benign epidermal poxvirus infection displaying discrete umbilicated papules."
    },
    "case_6": {
        "id": "case_6",
        "title": "Tinea Corporis / Dermatophytosis",
        "image_path": "STI_Project/01_STIAtlas/organized/Tinea/STIATLAS_059.jpg",
        "clean_site": "Flexural Fold / Inguinal (Upper Thigh)",
        "site_group": "Other Skin",
        "gender": "Male",
        "symptoms": "Pruritic annular erythematous scaly plaque with active raised border and central clearing",
        "actual_class": "Tinea",
        "clinical_note": "Superficial dermatophytosis exhibiting typical advancing annular margin."
    }
}

SITE_MAPPING = {
    "Oral Mucosa / Lip (Perioral)": ("Mouth", "Other Skin"),
    "Cutaneous Skin - General (Trunk & Limbs)": ("Skin - general", "Other Skin"),
    "Upper Body / Torso (Chest & Back)": ("Skin - general", "Other Skin"),
    "Flexural Fold / Inguinal (Upper Thigh)": ("Groin", "Other Skin"),
    "Mucocutaneous Transition Zone": ("Glans penis", "Genitals"),
    "Perianal Mucocutaneous Zone": ("Anus", "Anus"),
    "General Dermal Region": ("Other", "Other Skin")
}

def pil_to_base64(pil_image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()

def numpy_to_base64(np_image):
    pil_img = Image.fromarray(np_image)
    return pil_to_base64(pil_img)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "operational",
        "framework": "PyTorch 2.14 + ResNet-18 Multimodal",
        "verified_cohort_size": 314
    })

@app.route("/api/cases", methods=["GET"])
def get_cases():
    cases_list = []
    for k, v in CLEAN_PRESET_CASES.items():
        img = Image.open(v["image_path"]).convert("RGB")
        cases_list.append({
            "id": v["id"],
            "title": v["title"],
            "clean_site": v["clean_site"],
            "gender": v["gender"],
            "symptoms": v["symptoms"],
            "actual_class": v["actual_class"],
            "clinical_note": v["clinical_note"],
            "image_thumb": pil_to_base64(img.resize((180, 135)))
        })
    return jsonify(cases_list)

@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    req = request.json or {}
    case_id = req.get("case_id", "case_1")
    image_base64 = req.get("image_base64")
    case = CLEAN_PRESET_CASES.get(case_id, CLEAN_PRESET_CASES["case_1"])
    clean_site = req.get("clean_site") or case.get("clean_site", "Oral Mucosa / Lip (Perioral)")
    gender = req.get("gender") or case.get("gender", "Male")
    surveillance_year = int(req.get("surveillance_year", 2023))
    penicillin_allergic = bool(req.get("penicillin_allergic", False))
    is_pregnant = bool(req.get("is_pregnant", False))

    # 1. Resolve image
    if image_base64 and len(image_base64) > 100:
        header, encoded = image_base64.split(",", 1) if "," in image_base64 else ("", image_base64)
        img_bytes = base64.b64decode(encoded)
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    else:
        pil_img = Image.open(case["image_path"]).convert("RGB")

    # 2. Resolve metadata
    internal_site, internal_sg = SITE_MAPPING.get(clean_site, ("Mouth", "Other Skin"))
    meta_vec = encode_metadata(internal_site, internal_sg, gender)
    meta_tensor = torch.tensor(meta_vec, dtype=torch.float32).unsqueeze(0)
    img_tensor = EVAL_TRANSFORM(pil_img).unsqueeze(0)

    # 3. Model inference + Grad-CAM
    cam_map, pred_class_idx, probs = gradcam.generate(img_tensor, meta_tensor)
    pred_class = CLASS_NAMES[pred_class_idx]
    display_name = CLASS_DISPLAY_NAMES[pred_class]
    confidence = float(probs[pred_class_idx] * 100.0)

    # 4. Saliency segmentation
    seg_res = LesionSegmenter.segment_lesion(cam_map, pil_img)

    # 5. Modality attribution
    attr = MultimodalModalityExplainer.explain(model, img_tensor, meta_tensor, pred_class_idx)

    # 6. Smart AMR recommendation calculation
    recommendations = gisp_service.calculate_smart_recommendations(
        pred_class,
        surveillance_year=surveillance_year,
        penicillin_allergic=penicillin_allergic,
        is_pregnant=is_pregnant
    )

    # Differential probabilities
    differential = []
    for c_idx, c_name in enumerate(CLASS_NAMES):
        differential.append({
            "class_name": c_name,
            "display_name": CLASS_DISPLAY_NAMES[c_name],
            "probability": round(float(probs[c_idx] * 100.0), 2)
        })
    differential.sort(key=lambda x: x["probability"], reverse=True)

    guidelines = TREATMENT_GUIDELINES.get(pred_class, {})

    return jsonify({
        "predicted_class": pred_class,
        "display_name": display_name,
        "icd10": guidelines.get("icd10", ""),
        "pathogen": guidelines.get("pathogen", ""),
        "confidence": round(confidence, 1),
        "differential": differential,
        "original_image_base64": pil_to_base64(pil_img),
        "heatmap_base64": numpy_to_base64(seg_res["blended_heatmap"]),
        "contour_base64": numpy_to_base64(seg_res["contour_overlay"]),
        "coverage_pct": seg_res["coverage_pct"],
        "centroid": seg_res["centroid"],
        "modality_attribution": attr,
        "recommendations": recommendations,
        "guidelines": guidelines
    })

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    ablation_rows = []
    if os.path.exists("saved_models/ablation_study.csv"):
        df = pd.read_csv("saved_models/ablation_study.csv")
        ablation_rows = df.to_dict(orient="records")

    summary_metrics = {}
    if os.path.exists("saved_models/metrics_summary.json"):
        with open("saved_models/metrics_summary.json", "r") as f:
            summary_metrics = json.load(f)

    cm_b64 = None
    if os.path.exists("saved_models/confusion_matrix.png"):
        try:
            with open("saved_models/confusion_matrix.png", "rb") as f:
                cm_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode()
        except Exception:
            pass

    return jsonify({
        "ablation_study": ablation_rows,
        "metrics_summary": summary_metrics,
        "confusion_matrix_base64": cm_b64
    })

@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():
    req = request.json or {}
    condition = req.get("condition", "Early_Syphilis")
    year = int(req.get("year", 2023))
    pen = bool(req.get("penicillin_allergic", False))
    preg = bool(req.get("is_pregnant", False))
    recs = gisp_service.calculate_smart_recommendations(
        condition,
        surveillance_year=year,
        penicillin_allergic=pen,
        is_pregnant=preg
    )
    return jsonify(recs)

@app.route("/api/amr-trends", methods=["GET"])
def get_amr_trends():
    df_multi = gisp_service.get_multi_drug_trends()
    if df_multi.empty:
        return jsonify([])
    return jsonify(df_multi.to_dict(orient="records"))

@app.route("/api/cohort-stats", methods=["GET"])
def get_cohort_stats():
    return jsonify({
        "total_verified": 314,
        "classes": [
            {"name": "Early Syphilis", "count": 110},
            {"name": "Genital Warts", "count": 86},
            {"name": "Herpes Simplex", "count": 64},
            {"name": "Lichen Sclerosus", "count": 35},
            {"name": "Molluscum Contagiosum", "count": 12},
            {"name": "Tinea", "count": 7}
        ],
        "sites": [
            {"region": "Mucocutaneous Genital Region", "count": 220},
            {"region": "Extragenital / General Skin / Oral", "count": 60},
            {"region": "Perianal Zone", "count": 32}
        ]
    })

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    if os.path.exists(os.path.join(app.static_folder, "index.html")):
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"status": "Backend running. Build frontend with 'npm run build' inside frontend directory."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
