"""
Explainability Layer:
1. Grad-CAM (Visual XAI heatmap generation)
2. Lesion Segmentation & Localization (Contour extraction, Area %, Bounding Box)
3. Multimodal Modality Attribution (Visual vs Clinical Context contribution)
"""

import numpy as np
import cv2
import torch
import torch.nn.functional as F
from PIL import Image


class GradCAM:
    """
    Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization.
    Hooks into ResNet-18 layer4 conv layer.
    """
    def __init__(self, model, target_layer=None):
        self.model = model
        self.model.eval()
        self.target_layer = target_layer or model.get_last_conv_layer()

        self.gradients = None
        self.activations = None

        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate(self, img_tensor, meta_tensor=None, target_class=None):
        """
        img_tensor: (1, 3, 224, 224)
        meta_tensor: (1, 19) or None
        """
        self.model.zero_grad()

        if meta_tensor is not None:
            logits = self.model(img_tensor, meta_tensor)
        else:
            logits = self.model(img_tensor)

        probs = F.softmax(logits, dim=1)

        if target_class is None:
            target_class = torch.argmax(probs, dim=1).item()

        score = logits[0, target_class]
        score.backward(retain_graph=True)

        gradients = self.gradients[0]  # (C, H, W)
        activations = self.activations[0]  # (C, H, W)

        # Global average pooling of gradients = alpha weights
        weights = torch.mean(gradients, dim=(1, 2), keepdim=True)  # (C, 1, 1)

        # Weighted combination
        cam = torch.sum(weights * activations, dim=0).cpu().numpy()  # (H, W)

        # ReLU on CAM (positive attributions only)
        cam = np.maximum(cam, 0)

        # Normalize to [0, 1]
        if np.max(cam) > 0:
            cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam) + 1e-8)
        else:
            cam = np.zeros_like(cam)

        cam_resized = cv2.resize(cam, (224, 224))
        return cam_resized, target_class, probs[0].detach().cpu().numpy()


class LesionSegmenter:
    """
    Segments lesion boundaries from Grad-CAM activation + color saliency.
    Computes lesion area coverage, bounding box, and visual contour overlay.
    """
    @staticmethod
    def segment_lesion(cam_map, original_pil_img, threshold=0.35):
        """
        cam_map: (224, 224) float [0, 1]
        original_pil_img: PIL Image of any resolution
        """
        orig_w, orig_h = original_pil_img.size
        orig_np = np.array(original_pil_img)

        # Resize CAM to match original image dimensions
        cam_full = cv2.resize(cam_map, (orig_w, orig_h))

        # Binary threshold for high-attention lesion core
        binary_mask = (cam_full >= threshold).astype(np.uint8) * 255

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create overlay
        overlay = orig_np.copy()
        total_pixels = orig_w * orig_h
        lesion_pixels = np.sum(binary_mask > 0)
        coverage_pct = (lesion_pixels / total_pixels) * 100.0

        bbox = None
        centroid = None
        if contours:
            largest_c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_c)
            bbox = (int(x), int(y), int(w), int(h))

            # Centroid
            M = cv2.moments(largest_c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroid = (cx, cy)

            # Draw smooth contours in emerald green
            cv2.drawContours(overlay, [largest_c], -1, (0, 255, 128), 3)

            # Draw subtle semi-transparent tinted mask over lesion area
            color_mask = np.zeros_like(orig_np)
            color_mask[binary_mask > 0] = [0, 230, 130]
            overlay = cv2.addWeighted(overlay, 0.85, color_mask, 0.15, 0)

        # Create Heatmap Overlay Image
        heatmap_color = cv2.applyColorMap(np.uint8(255 * cam_full), cv2.COLORMAP_JET)
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
        blended_heatmap = cv2.addWeighted(orig_np, 0.55, heatmap_color, 0.45, 0)

        return {
            'binary_mask': binary_mask,
            'contour_overlay': overlay,
            'blended_heatmap': blended_heatmap,
            'coverage_pct': round(coverage_pct, 2),
            'bbox': bbox,
            'centroid': centroid,
            'contours_count': len(contours)
        }


class MultimodalModalityExplainer:
    """
    Computes modality attribution scores (Visual Features % vs Anatomical Site % vs Gender %).
    Uses gradient sensitivity across multimodal branches.
    """
    @staticmethod
    def explain(model, img_tensor, meta_tensor, target_class=None):
        model.eval()
        img_tensor = img_tensor.clone().requires_grad_(True)
        meta_tensor = meta_tensor.clone().requires_grad_(True)

        logits, v_feat, m_feat = model(img_tensor, meta_tensor, return_features=True)
        if target_class is None:
            target_class = torch.argmax(logits, dim=1).item()

        score = logits[0, target_class]
        grads = torch.autograd.grad(score, [v_feat, meta_tensor], retain_graph=True)

        v_grad_norm = torch.norm(grads[0]).item()
        m_grad = grads[1][0]  # (19,)

        # Split metadata into Anatomical Site (first 16) vs Gender (last 3)
        site_grad_norm = torch.norm(m_grad[:16]).item()
        gender_grad_norm = torch.norm(m_grad[16:]).item()

        total = v_grad_norm + site_grad_norm + gender_grad_norm + 1e-8
        v_pct = round((v_grad_norm / total) * 100, 1)
        s_pct = round((site_grad_norm / total) * 100, 1)
        g_pct = round((gender_grad_norm / total) * 100, 1)

        # Ensure sum to 100
        remainder = 100.0 - (v_pct + s_pct + g_pct)
        v_pct = round(v_pct + remainder, 1)

        return {
            'visual_pct': v_pct,
            'site_pct': s_pct,
            'gender_pct': g_pct,
            'target_class': target_class
        }

