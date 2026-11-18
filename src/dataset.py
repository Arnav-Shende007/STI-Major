"""
Dataset loading, preprocessing, metadata encoding, and splitting for STIAtlas clinical dataset.
"""

import os
import re
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
from sklearn.model_selection import train_test_split

CLASS_NAMES = [
    'Early_Syphilis',
    'Genital_Warts',
    'Herpes_Simplex',
    'Lichen_Sclerosus',
    'Molluscum_Contagiosum',
    'Tinea'
]

CLASS_DISPLAY_NAMES = {
    'Early_Syphilis': 'Early Syphilis',
    'Genital_Warts': 'Genital Warts (HPV)',
    'Herpes_Simplex': 'Herpes Simplex (HSV)',
    'Lichen_Sclerosus': 'Lichen Sclerosus',
    'Molluscum_Contagiosum': 'Molluscum Contagiosum',
    'Tinea': 'Tinea (Fungal)'
}

SITE_GROUPS = ['Genitals', 'Other Skin', 'Anus', 'Other']
GENDERS = ['Male', 'Female', 'Unknown']

TOP_ANATOMICAL_SITES = [
    'Vulva',
    'Penis',
    'Skin - general',
    'Anus',
    'Glans penis',
    'Buttock',
    'Scrotum',
    'Mouth',
    'Groin',
    'Cervix',
    'Vagina',
    'Other'
]


def clean_site_name(raw_site):
    if not isinstance(raw_site, str) or not raw_site.strip() or raw_site == 'nan':
        return 'Other'
    raw = raw_site.strip()
    for s in ['Vulva', 'Penis', 'Anus', 'Glans penis', 'Buttock', 'Scrotum', 'Mouth', 'Groin', 'Cervix', 'Vagina']:
        if s.lower() in raw.lower():
            return s
    if 'skin' in raw.lower():
        return 'Skin - general'
    return 'Other'


def encode_metadata(anatomical_site, site_group, gender):
    """
    Encodes clinical metadata into a fixed-length normalized vector (dim: 12 + 4 + 3 = 19).
    """
    clean_site = clean_site_name(anatomical_site)
    site_vec = [1.0 if clean_site == s else 0.0 for s in TOP_ANATOMICAL_SITES]
    if sum(site_vec) == 0:
        site_vec[-1] = 1.0

    sg = site_group if site_group in SITE_GROUPS else 'Other'
    sg_vec = [1.0 if sg == g else 0.0 for g in SITE_GROUPS]
    if sum(sg_vec) == 0:
        sg_vec[-1] = 1.0

    gen = gender if gender in GENDERS else 'Unknown'
    gen_vec = [1.0 if gen == g else 0.0 for g in GENDERS]
    if sum(gen_vec) == 0:
        gen_vec[-1] = 1.0

    full_vec = np.array(site_vec + sg_vec + gen_vec, dtype=np.float32)
    return full_vec


METADATA_DIM = len(TOP_ANATOMICAL_SITES) + len(SITE_GROUPS) + len(GENDERS)  # 12 + 4 + 3 = 19


def load_stiatlas_data(
    manifest_path='STI_Project/01_STIAtlas/metadata/stiatlas_manifest.csv',
    organized_dir='STI_Project/01_STIAtlas/organized'
):
    df_manifest = pd.read_csv(manifest_path)
    records = []

    for cls_name in CLASS_NAMES:
        cls_dir = os.path.join(organized_dir, cls_name)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_id = os.path.splitext(fname)[0]
                img_path = os.path.join(cls_dir, fname)
                match = df_manifest[df_manifest['image_id'] == img_id]

                if not match.empty:
                    row = match.iloc[0]
                    site = str(row.get('anatomical_site', 'Unknown'))
                    sg = str(row.get('site_group', 'Genitals'))
                    gender = str(row.get('patient_gender', 'Unknown'))
                    desc = str(row.get('description', ''))
                else:
                    site = 'Unknown'
                    sg = 'Genitals'
                    gender = 'Unknown'
                    desc = ''

                meta_vec = encode_metadata(site, sg, gender)

                records.append({
                    'image_id': img_id,
                    'file_path': img_path,
                    'disease_class': cls_name,
                    'class_idx': CLASS_NAMES.index(cls_name),
                    'anatomical_site': site,
                    'site_group': sg,
                    'gender': gender,
                    'description': desc,
                    'meta_vector': meta_vec
                })

    df_dataset = pd.DataFrame(records)
    return df_dataset


def get_train_test_split(df_dataset, test_size=0.20, random_state=42):
    """
    Stratified split ensuring representation of imbalanced minority classes.
    """
    train_df, test_df = train_test_split(
        df_dataset,
        test_size=test_size,
        stratify=df_dataset['class_idx'],
        random_state=random_state
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def compute_class_weights(df_train):
    """
    Compute balanced inverse class weights to handle severe class imbalance.
    """
    counts = df_train['class_idx'].value_counts().to_dict()
    total = len(df_train)
    num_classes = len(CLASS_NAMES)
    weights = np.zeros(num_classes, dtype=np.float32)
    for c in range(num_classes):
        cnt = counts.get(c, 1)
        weights[c] = total / (num_classes * cnt)
    return torch.tensor(weights, dtype=torch.float32)


# Image transforms
TRAIN_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.15, contrast=0.15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

EVAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class STIDataset(Dataset):
    def __init__(self, df, transform=EVAL_TRANSFORM):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['file_path']
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image_tensor = self.transform(image)
        else:
            image_tensor = transforms.ToTensor()(image)

        meta_tensor = torch.tensor(row['meta_vector'], dtype=torch.float32)
        label_tensor = torch.tensor(row['class_idx'], dtype=torch.long)

        return image_tensor, meta_tensor, label_tensor, row['image_id']

