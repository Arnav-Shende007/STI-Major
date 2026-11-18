# STIAtlas Dataset Manual Review Report

This document reports the clinical audit and manual verification results for specific anomalous or metadata-deficient records in the STIAtlas dataset.

---

## 1. Summary of Reviewed Records

| Image ID | Original Filename | Disease Class | Review Status | Action Taken | Current Site Group |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **STIATLAS_039** | `Positive_dark_ground_microscopy_(01).jpg` | Early Syphilis | `microscopy_non_lesion` | Retained raw image; marked for exclusion from lesion-image ML training subset. | `NA` |
| **STIATLAS_133** | `Treponema_pallidum-darkground_microscopy.jpg` | Early Syphilis | `microscopy_non_lesion` | Retained raw image; marked for exclusion from lesion-image ML training subset. | `NA` |
| **STIATLAS_114** | `Secondary_syphilis-widespread_rash_(06)_2-4.jpg` | Early Syphilis | `unresolved_anatomical_site` | Verified source page; no explicit anatomical site tag exists. Left as `NA`. | `NA` |
| **STIATLAS_263** | `Secondary syphilis 36.jpg` | Early Syphilis | `unresolved_anatomical_site` | Verified source page; no explicit anatomical site tag exists. Left as `NA`. | `NA` |

---

## 2. Detailed Verification Log

### 1. STIATLAS_039 & STIATLAS_133
* **Verification Status:** **Exclusion Candidate**.
* **Clinical Context:** These two assets are darkfield microscopic photographs of *Treponema pallidum* spirochetes (the causative agent of syphilis) rather than clinical photographs of skin or mucosal lesions.
* **Metadata Resolution:** As these do not depict skin lesions on a patient's body, their `anatomical_site` is correctly set as `NA`. They are flagged with `review_status = microscopy_non_lesion` to facilitate filtering and exclusion from any downstream skin-lesion classification models.

### 2. STIATLAS_114
* **Verification Status:** **Unresolved Site Metadata**.
* **Clinical Context:** This is a clinical photograph of a widespread secondary syphilis rash.
* **Metadata Resolution:** A thorough audit of the original stiatlas.org database records confirms that **no explicit anatomical site label** exists for this record (the structured `Sites:` field is empty). To prevent visual bias or incorrect assumptions, the `anatomical_site` and `site_group` fields are left as `NA`, and the record is flagged with `review_status = unresolved_anatomical_site`.

### 3. STIATLAS_263
* **Verification Status:** **Unresolved Site Metadata**.
* **Clinical Context:** This is a clinical photograph depicting secondary syphilis alopecia on a hair-bearing region (scalp).
* **Metadata Resolution:** A review of the original database entry on stiatlas.org confirms that **no explicit anatomical site label** is provided by the source. The `anatomical_site` and `site_group` fields are left as `NA`, and the record is flagged with `review_status = unresolved_anatomical_site`.

---

## 3. Exclusion Recommendations for ML Modeling

When preparing the dataset for training classification models, it is strongly recommended to apply the following filter:

```python
# Recommended dataset filtering logic
lesion_dataset = full_dataset[full_dataset['review_status'] == 'verified_lesion']
```

This filter will exclude the microscopic images (`STIATLAS_039` and `STIATLAS_133`) while retaining the clinical photographs with unresolved sites (`STIATLAS_114` and `STIATLAS_263`) if required, or allowing they be treated separately due to their missing anatomical mappings.
