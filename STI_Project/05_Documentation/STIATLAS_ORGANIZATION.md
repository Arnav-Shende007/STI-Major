# STIAtlas Organized Dataset Report

This report documents the dataset organization process, summarizing the distribution of clinical photos copied into class-specific folders, and the clinical exclusions applied.

---

## 1. Dataset Overview

* **Original Raw Dataset (Immutable):** Preserved untouched in [`01_STIAtlas/raw/`](file:///d:/STI_Project/01_STIAtlas/raw) (316 images).
* **Organized Dataset Directory:** [`01_STIAtlas/organized/`](file:///d:/STI_Project/01_STIAtlas/organized).
* **Total Assets Processed:** 316
* **Images Successfully Organized:** 314
* **Microscopy Exclusions:** 2
* **Unresolved Site Images Included:** 2

---

## 2. Organized Disease Class Counts

Below is the distribution of the 314 clinical photos copied into class subfolders:

| Disease Class Folder | Discovered Raw Count | Organized Count | Excluded Microscopy | Status |
| :--- | :---: | :---: | :---: | :--- |
| **`Early_Syphilis/`** | 112 | 110 | 2 | Verified clinical photos organized |
| **`Genital_Warts/`** | 86 | 86 | 0 | Verified clinical photos organized |
| **`Herpes_Simplex/`** | 64 | 64 | 0 | Verified clinical photos organized |
| **`Lichen_Sclerosus/`** | 35 | 35 | 0 | Verified clinical photos organized |
| **`Molluscum_Contagiosum/`** | 12 | 12 | 0 | Verified clinical photos organized |
| **`Tinea/`** | 7 | 7 | 0 | Verified clinical photos organized |
| **Total** | **316** | **314** | **2** | |

---

## 3. Clinical Exclusions (Microscopy Images)

The following two records were classified as `microscopy_non_lesion` and were **excluded** from the organized lesion dataset:
1. **`STIATLAS_039`** (`Positive_dark_ground_microscopy_(01).jpg`) — Darkfield microscopy showing *Treponema pallidum* bacteria.
2. **`STIATLAS_133`** (`Treponema_pallidum-darkground_microscopy.jpg`) — Darkfield microscopy showing *Treponema pallidum* bacteria.

*Note: These images remain unmodified in [`01_STIAtlas/raw/`](file:///d:/STI_Project/01_STIAtlas/raw) and are logged in [`metadata/stiatlas_organization_report.csv`](file:///d:/STI_Project/01_STIAtlas/metadata/stiatlas_organization_report.csv).*

---

## 4. Unresolved Anatomical-Site Clinical Photos

The following two clinical photographs had no explicit anatomical location tags in the source database, but are **included** in the organized folders:
1. **`STIATLAS_114`** — Placed in `Early_Syphilis/` (widespread secondary syphilis rash). Mapped site is `NA`.
2. **`STIATLAS_263`** — Placed in `Early_Syphilis/` (alopecia of scalp). Mapped site is `NA`.

---

## 5. Dataset Validation Summary

* **Raw Integrity:** Confirmed. The raw directory was untouched; no files were moved, renamed, or deleted.
* **Organized Copies Existence:** Confirmed. All 314 organized files exist on disk in their respective folders.
* **Manifest Mapping Match:** Confirmed. Every organized file correlates with exactly one record in the manifest and has a corresponding raw source file.
* **Folder Correctness:** Confirmed. Every organized file is placed in the folder matching its verified disease class.
* **Redundancy/Duplicate Check:** Confirmed. No duplicate files or redundant assets were created.
* **Validation Status:** PASSED
