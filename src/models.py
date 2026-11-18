"""
PyTorch Neural Network Architectures for:
1. Image-only Baseline (ResNet-18)
2. Metadata-only Baseline (MLP)
3. Multimodal Fusion Model (ResNet-18 + Clinical Embedding + Fusion Head)
"""

import torch
import torch.nn as nn
from torchvision import models


class ImageOnlyClassifier(nn.Module):
    """
    Image-only Baseline: Pretrained ResNet-18 backbone fine-tuned for 6 STI classes.
    """
    def __init__(self, num_classes=6, pretrained=True):
        super().__init__()
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        in_features = self.backbone.fc.in_features  # 512
        self.backbone.fc = nn.Identity()

        self.classifier = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        features = self.backbone(x)
        logits = self.classifier(features)
        return logits

    def get_last_conv_layer(self):
        return self.backbone.layer4[1].conv2


class MetadataOnlyClassifier(nn.Module):
    """
    Metadata-only Baseline: MLP that classifies based purely on clinical context (site, gender).
    """
    def __init__(self, meta_dim=19, num_classes=6):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(meta_dim, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes)
        )

    def forward(self, meta):
        return self.net(meta)


class MultimodalFusionModel(nn.Module):
    """
    Multimodal Fusion Architecture:
    Combines ResNet-18 visual feature representation (512-d) with
    clinical metadata embedding (64-d) into a fused multimodal decision vector (576-d).
    """
    def __init__(self, meta_dim=19, num_classes=6, pretrained=True):
        super().__init__()
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        self.visual_dim = self.backbone.fc.in_features  # 512
        self.backbone.fc = nn.Identity()

        # Clinical metadata branch
        self.meta_branch = nn.Sequential(
            nn.Linear(meta_dim, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2)
        )

        # Multimodal fusion & classification head
        fused_dim = self.visual_dim + 64  # 512 + 64 = 576
        self.fusion_head = nn.Sequential(
            nn.Linear(fused_dim, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, img, meta, return_features=False):
        # 1. Visual representation
        visual_feats = self.backbone(img)  # (batch, 512)

        # 2. Clinical metadata representation
        meta_feats = self.meta_branch(meta)  # (batch, 64)

        # 3. Cross-modal concatenation
        fused = torch.cat([visual_feats, meta_feats], dim=1)  # (batch, 576)

        # 4. Final classification
        logits = self.fusion_head(fused)

        if return_features:
            return logits, visual_feats, meta_feats
        return logits

    def get_last_conv_layer(self):
        return self.backbone.layer4[1].conv2

