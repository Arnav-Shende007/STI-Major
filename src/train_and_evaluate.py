"""
Training and Evaluation Pipeline:
1. Stratified 80/20 data partitioning with class weighting.
2. Feature extraction via ResNet-18 backbone.
3. Training of Baseline 1 (Image-only), Baseline 2 (Metadata-only), Multimodal Fusion Model, and Ablation models.
4. Comprehensive evaluation metrics export (Accuracy, F1, Per-class metrics, Confusion Matrix, Ablation Table).
"""

import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from src.dataset import (
    load_stiatlas_data,
    get_train_test_split,
    compute_class_weights,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
    EVAL_TRANSFORM,
    TRAIN_TRANSFORM,
    METADATA_DIM
)
from src.models import (
    ImageOnlyClassifier,
    MetadataOnlyClassifier,
    MultimodalFusionModel
)


def extract_features(model, df, device, transform=EVAL_TRANSFORM):
    """
    Extracts 512-d ResNet-18 feature vectors for all samples.
    """
    model.eval()
    features_list = []
    meta_list = []
    labels_list = []
    ids_list = []

    with torch.no_grad():
        for _, row in df.iterrows():
            img = Image.open(row['file_path']).convert('RGB')
            img_tensor = transform(img).unsqueeze(0).to(device)
            feat = model.backbone(img_tensor).squeeze(0).cpu().numpy()

            features_list.append(feat)
            meta_list.append(row['meta_vector'])
            labels_list.append(row['class_idx'])
            ids_list.append(row['image_id'])

    return (
        np.array(features_list, dtype=np.float32),
        np.array(meta_list, dtype=np.float32),
        np.array(labels_list, dtype=np.int64),
        ids_list
    )


def train_head(head_module, X_train, y_train, class_weights, epochs=60, lr=0.003, batch_size=32):
    """
    Fast, stable training for classifier heads using CrossEntropy with inverse class weighting.
    """
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(head_module.parameters(), lr=lr, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    dataset = TensorDataset(torch.tensor(X_train), torch.tensor(y_train))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    head_module.train()
    for epoch in range(epochs):
        for bx, by in loader:
            optimizer.zero_grad()
            out = head_module(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
        scheduler.step()

    head_module.eval()
    return head_module


def evaluate_model(head_module, X_test, y_test):
    head_module.eval()
    with torch.no_grad():
        logits = head_module(torch.tensor(X_test))
        probs = torch.softmax(logits, dim=1).numpy()
        preds = np.argmax(probs, axis=1)

    acc = accuracy_score(y_test, preds)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_test, preds, average='macro', zero_division=0
    )
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_test, preds, average='weighted', zero_division=0
    )

    # Per-class metrics
    p_cls, r_cls, f1_cls, supp_cls = precision_recall_fscore_support(
        y_test, preds, average=None, labels=list(range(len(CLASS_NAMES))), zero_division=0
    )

    per_class = {}
    for i, cname in enumerate(CLASS_NAMES):
        per_class[cname] = {
            'display_name': CLASS_DISPLAY_NAMES[cname],
            'precision': round(float(p_cls[i]), 4),
            'recall': round(float(r_cls[i]), 4),
            'f1_score': round(float(f1_cls[i]), 4),
            'support': int(supp_cls[i])
        }

    cm = confusion_matrix(y_test, preds, labels=list(range(len(CLASS_NAMES))))

    return {
        'accuracy': round(float(acc), 4),
        'macro_precision': round(float(p_macro), 4),
        'macro_recall': round(float(r_macro), 4),
        'macro_f1': round(float(f1_macro), 4),
        'weighted_f1': round(float(f1_weighted), 4),
        'per_class': per_class,
        'confusion_matrix': cm.tolist(),
        'preds': preds.tolist(),
        'probs': probs.tolist()
    }


def run_pipeline():
    device = torch.device('cpu')
    print("Loading STIAtlas dataset and metadata...")
    df = load_stiatlas_data()
    print(f"Total verified cases loaded: {len(df)}")

    train_df, test_df = get_train_test_split(df, test_size=0.20, random_state=42)
    print(f"Train set: {len(train_df)} cases | Test set: {len(test_df)} cases")

    class_weights = compute_class_weights(train_df).to(device)

    # Initialize backbone
    print("Initializing ResNet-18 visual feature extractor...")
    base_model = MultimodalFusionModel(meta_dim=METADATA_DIM, num_classes=6, pretrained=True).to(device)

    cache_path = 'saved_models/features_cache.npz'
    if os.path.exists(cache_path):
        print("Loading cached visual and metadata feature representations...")
        data = np.load(cache_path, allow_pickle=True)
        v_train = data['v_train']
        m_train = data['m_train']
        y_train = data['y_train']
        v_test = data['v_test']
        m_test = data['m_test']
        y_test = data['y_test']
    else:
        print("Extracting features from clinical images (takes ~10 seconds)...")
        v_train, m_train, y_train, _ = extract_features(base_model, train_df, device)
        v_test, m_test, y_test, _ = extract_features(base_model, test_df, device)
        np.savez(
            cache_path,
            v_train=v_train, m_train=m_train, y_train=y_train,
            v_test=v_test, m_test=m_test, y_test=y_test
        )
        print("Feature representations cached successfully.")

    # 1. Baseline 1: Image-only Model
    print("\n--- Training Baseline 1: Image-Only (ResNet-18 features) ---")
    img_head = nn.Sequential(
        nn.Linear(512, 128),
        nn.ReLU(inplace=True),
        nn.Dropout(0.3),
        nn.Linear(128, 6)
    )
    img_head = train_head(img_head, v_train, y_train, class_weights, epochs=70, lr=0.003)
    img_eval = evaluate_model(img_head, v_test, y_test)
    print(f"Image-Only Accuracy: {img_eval['accuracy']*100:.2f}% | Macro F1: {img_eval['macro_f1']:.4f}")

    # 2. Baseline 2: Metadata-only Model
    print("\n--- Training Baseline 2: Metadata-Only (Clinical Site + Gender MLP) ---")
    meta_head = nn.Sequential(
        nn.Linear(METADATA_DIM, 64),
        nn.ReLU(inplace=True),
        nn.Dropout(0.2),
        nn.Linear(64, 32),
        nn.ReLU(inplace=True),
        nn.Dropout(0.2),
        nn.Linear(32, 6)
    )
    meta_head = train_head(meta_head, m_train, y_train, class_weights, epochs=70, lr=0.005)
    meta_eval = evaluate_model(meta_head, m_test, y_test)
    print(f"Metadata-Only Accuracy: {meta_eval['accuracy']*100:.2f}% | Macro F1: {meta_eval['macro_f1']:.4f}")

    # 3. Multimodal Fusion Model
    print("\n--- Training Multimodal Fusion Model (Visual 512-d + Clinical 64-d) ---")
    # Define fusion pipeline module
    class MultimodalHead(nn.Module):
        def __init__(self):
            super().__init__()
            self.meta_proj = nn.Sequential(
                nn.Linear(METADATA_DIM, 64),
                nn.ReLU(inplace=True),
                nn.Dropout(0.2)
            )
            self.fusion = nn.Sequential(
                nn.Linear(512 + 64, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(128, 6)
            )

        def forward(self, x):
            v = x[:, :512]
            m = x[:, 512:]
            m_feat = self.meta_proj(m)
            fused = torch.cat([v, m_feat], dim=1)
            return self.fusion(fused)

    vm_train = np.concatenate([v_train, m_train], axis=1)
    vm_test = np.concatenate([v_test, m_test], axis=1)

    fusion_head = MultimodalHead()
    fusion_head = train_head(fusion_head, vm_train, y_train, class_weights, epochs=75, lr=0.003)
    fusion_eval = evaluate_model(fusion_head, vm_test, y_test)
    print(f"Multimodal Fusion Accuracy: {fusion_eval['accuracy']*100:.2f}% | Macro F1: {fusion_eval['macro_f1']:.4f}")

    # 4. Ablation A: Multimodal without Gender (Image + Anatomical Site only)
    print("\n--- Running Ablation A: Multimodal (No Gender) ---")
    # Zero out gender indices (last 3 indices: 16, 17, 18)
    m_train_nogender = m_train.copy()
    m_train_nogender[:, 16:] = 0.0
    m_test_nogender = m_test.copy()
    m_test_nogender[:, 16:] = 0.0

    vm_train_nogender = np.concatenate([v_train, m_train_nogender], axis=1)
    vm_test_nogender = np.concatenate([v_test, m_test_nogender], axis=1)

    ablation_a_head = MultimodalHead()
    ablation_a_head = train_head(ablation_a_head, vm_train_nogender, y_train, class_weights, epochs=75, lr=0.003)
    ablation_a_eval = evaluate_model(ablation_a_head, vm_test_nogender, y_test)
    print(f"Ablation A (No Gender) Macro F1: {ablation_a_eval['macro_f1']:.4f}")

    # 5. Ablation B: Multimodal without Anatomical Site (Image + Gender only)
    print("\n--- Running Ablation B: Multimodal (No Anatomical Site) ---")
    m_train_nosite = m_train.copy()
    m_train_nosite[:, :16] = 0.0
    m_test_nosite = m_test.copy()
    m_test_nosite[:, :16] = 0.0

    vm_train_nosite = np.concatenate([v_train, m_train_nosite], axis=1)
    vm_test_nosite = np.concatenate([v_test, m_test_nosite], axis=1)

    ablation_b_head = MultimodalHead()
    ablation_b_head = train_head(ablation_b_head, vm_train_nosite, y_train, class_weights, epochs=75, lr=0.003)
    ablation_b_eval = evaluate_model(ablation_b_head, vm_test_nosite, y_test)
    print(f"Ablation B (No Anatomical Site) Macro F1: {ablation_b_eval['macro_f1']:.4f}")

    # Build Ablation Table
    ablation_rows = [
        {'Architecture / Modalities': 'Baseline 1: Image-only (ResNet-18)', 'Accuracy (%)': img_eval['accuracy']*100, 'Macro F1': img_eval['macro_f1'], 'Macro Precision': img_eval['macro_precision'], 'Macro Recall': img_eval['macro_recall']},
        {'Architecture / Modalities': 'Baseline 2: Metadata-only (Clinical MLP)', 'Accuracy (%)': meta_eval['accuracy']*100, 'Macro F1': meta_eval['macro_f1'], 'Macro Precision': meta_eval['macro_precision'], 'Macro Recall': meta_eval['macro_recall']},
        {'Architecture / Modalities': 'Ablation A: Image + Gender (No Site)', 'Accuracy (%)': ablation_b_eval['accuracy']*100, 'Macro F1': ablation_b_eval['macro_f1'], 'Macro Precision': ablation_b_eval['macro_precision'], 'Macro Recall': ablation_b_eval['macro_recall']},
        {'Architecture / Modalities': 'Ablation B: Image + Anatomical Site (No Gender)', 'Accuracy (%)': ablation_a_eval['accuracy']*100, 'Macro F1': ablation_a_eval['macro_f1'], 'Macro Precision': ablation_a_eval['macro_precision'], 'Macro Recall': ablation_a_eval['macro_recall']},
        {'Architecture / Modalities': 'Proposed: Multimodal Fusion (Image + Site + Gender)', 'Accuracy (%)': fusion_eval['accuracy']*100, 'Macro F1': fusion_eval['macro_f1'], 'Macro Precision': fusion_eval['macro_precision'], 'Macro Recall': fusion_eval['macro_recall']},
    ]
    df_ablation = pd.DataFrame(ablation_rows)
    df_ablation.to_csv('saved_models/ablation_study.csv', index=False)
    print("\n--- MASTER ABLATION TABLE ---")
    print(df_ablation.to_string(index=False))

    # Save end-to-end full Multimodal Model weights
    base_model.meta_branch = fusion_head.meta_proj
    base_model.fusion_head = fusion_head.fusion
    torch.save(base_model.state_dict(), 'saved_models/multimodal_best.pth')

    # Save Image-Only Model weights
    img_model = ImageOnlyClassifier(num_classes=6, pretrained=False)
    img_model.backbone = base_model.backbone
    img_model.classifier = img_head
    torch.save(img_model.state_dict(), 'saved_models/image_only_best.pth')

    # Save summary metrics to JSON
    summary_metrics = {
        'total_dataset_size': len(df),
        'train_samples': len(train_df),
        'test_samples': len(test_df),
        'multimodal_fusion': fusion_eval,
        'image_only': img_eval,
        'metadata_only': meta_eval,
        'ablation_study': ablation_rows
    }
    with open('saved_models/metrics_summary.json', 'w') as f:
        json.dump(summary_metrics, f, indent=2)

    # Plot & Save Confusion Matrix
    cm = np.array(fusion_eval['confusion_matrix'])
    plt.figure(figsize=(8, 6))
    short_names = ['Syphilis', 'Warts', 'Herpes', 'Lichen', 'Molluscum', 'Tinea']
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=short_names, yticklabels=short_names)
    plt.title('Multimodal Fusion Model - Test Confusion Matrix')
    plt.xlabel('Predicted Diagnosis')
    plt.ylabel('Actual Clinical Diagnosis')
    plt.tight_layout()
    plt.savefig('saved_models/confusion_matrix.png', dpi=150)
    plt.close()

    print("\nEvaluation artifacts saved to saved_models/ successfully!")
    return summary_metrics


if __name__ == '__main__':
    run_pipeline()

