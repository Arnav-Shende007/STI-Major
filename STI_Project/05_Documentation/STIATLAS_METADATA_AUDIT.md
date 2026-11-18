# STIAtlas Dataset Metadata Audit Report

This report documents the completeness, consistency, and structural integrity of the downloaded STIAtlas metadata manifest, referencing 316 unique verified target assets.

---

## 1. Metadata Completeness

| Metric | Field | Present Count | Missing / NA Count | Completeness |
| :--- | :---: | :---: | :---: | :---: |
| **Total Records** | - | 316 | 0 | 100.0% |
| **Disease Class** | `disease_class` | 316 | 0 | 100.0% |
| **Anatomical Site** | `anatomical_site` | 312 | 4 | 98.7% |
| **Site Group** | `site_group` | 312 | 4 | 98.7% |
| **Patient Gender** | `patient_gender` | 281 | 35 | 88.9% |
| **Description** | `description` | 141 | 175 | 44.6% |
| **Review Status** | `review_status` | 316 | 0 | 100.0% |

---

## 2. Data Consistency Validation

* **Unique IDs:** Checked. Total unique `image_id` count is 316/316. Duplicate IDs found: 0
* **Image File Existence:** Checked. Mapped local files exist on disk for all records. Missing files: 0
* **Disease Class Integrity:** Checked. All records belong to the six target classes. Invalid classes: 0
* **SHA-256 Hash Integrity:** Checked. All records have valid 64-character hexadecimal hashes. Invalid hashes: 0
* **Duplicate Hashes:** Checked. Duplicate content hashes found: 0
* **Source URL Integrity:** Checked. All records have a valid source page URL on `stiatlas.org`. Missing source URLs: 0


---

## 3. Anatomical-Site Mapping Validation

All site values are grouped into the three standard classes from the 2025 paper: `Genitals`, `Anus`, and `Other Skin`.
* **Invalid or Unmapped Groups:** 0

---

## 4. Class Distribution & Imbalance Analysis

Below is the class-by-class count and percentage breakdown for the 316 downloaded target images:

| Class Name | Count | Percentage | Status |
| :--- | :---: | :---: | :--- |
| **Lichen Sclerosus** | 35 | 11.1% | Sufficient |
| **Early Syphilis** | 112 | 35.4% | Sufficient |
| **Genital Warts** | 86 | 27.2% | Sufficient |
| **Molluscum Contagiosum** | 12 | 3.8% | Underrepresented |
| **Herpes Simplex** | 64 | 20.3% | Sufficient |
| **Tinea** | 7 | 2.2% | Underrepresented |
| **Total** | **316** | **100.0%** | |

---

## 5. Review Status Distribution

We classified the dataset records into three clinical categories based on manual and automated reviews:

* **`verified_lesion`:** Clinical photographs of skin/mucosal lesions suitable for ML training (312 images).
* **`microscopy_non_lesion`:** Microscopic darkfield photographs showing *Treponema pallidum* spirochetes (bacteria) rather than skin lesions (2 images).
* **`unresolved_anatomical_site`:** Clinical photographs of skin lesions where no anatomical location tag was provided by stiatlas.org (2 images).

---

## 6. Recommended Naming Convention for Organization

We compared the following four filename strategies for organizing copies of the raw assets into category subfolders:

* **Approach A (`STIATLAS_<ID>.jpg`):** Keep the raw ID (e.g., `STIATLAS_001.jpg`).
* **Approach B (`STIATLAS_<Class>_<ID>.jpg`):** Include class prefix (e.g., `STIATLAS_Early_Syphilis_001.jpg`).
* **Approach C (`STIATLAS_<Class>_<SiteGroup>_<ID>.jpg`):** Include class and anatomical group (e.g., `STIATLAS_Early_Syphilis_Genitals_001.jpg`).
* **Approach D (`STIATLAS_<Class>_<Gender>_<Site>_<ID>.jpg`):** Include class, gender, and exact site.

### Selected Convention: **Approach A (`STIATLAS_<ID>.jpg`)**
* **Rationale:** Since the organized images will live inside disease-specific subfolders (e.g., `organized/Early_Syphilis/`), embedding the class and site name in the filename is redundant and results in excessively long, fragile filenames. Keeping the name as `STIATLAS_<ID>.jpg` is clean, robust, prevents file path length issues, and maintains a direct 1-to-1 link with the `image_id` key in the manifest metadata.

---

## 7. Records Requiring Manual Human Review

| Image ID | Filename | Review Status | Action Taken / Reason | Source URL |
| :--- | :--- | :--- | :--- | :--- |
| STIATLAS_039 | Positive_dark_ground_microscopy_(01).jpg | `microscopy_non_lesion` | Microscopy view (non-lesion) | [Link](https://stiatlas.org/SearchAtlas.aspx?pageidx=15) |
| STIATLAS_114 | Secondary_syphilis-widespread_rash_(06)_2-4.jpg | `unresolved_anatomical_site` | Unresolved anatomical site tag in source database | [Link](https://stiatlas.org/SearchAtlas.aspx?pageidx=37) |
| STIATLAS_133 | Treponema_pallidum-darkground_microscopy.jpg | `microscopy_non_lesion` | Microscopy view (non-lesion) | [Link](https://stiatlas.org/SearchAtlas.aspx?pageidx=40) |
| STIATLAS_263 | Secondary syphilis 36.jpg | `unresolved_anatomical_site` | Unresolved anatomical site tag in source database | [Link](https://stiatlas.org/SearchAtlas.aspx?pageidx=72) |
