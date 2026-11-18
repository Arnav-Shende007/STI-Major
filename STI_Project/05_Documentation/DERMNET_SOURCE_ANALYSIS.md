# DermNet NZ Dataset Source Analysis

This document provides a comprehensive research analysis of the DermNet NZ dataset, identifying relevant candidate images to supplement the STIAtlas clinical lesion-image dataset.

---

## 1. Source

* **Official Source URL**: [https://dermnetnz.org/](https://dermnetnz.org/)
* **Source Description**: DermNet NZ is a world-renowned, free online database of clinical dermatology information, developed and maintained by the **DermNet New Zealand Trust**.
* **Clinical Integrity**: Topics are authored and reviewed by registered dermatologists and medical professionals, ensuring high clinical diagnostic accuracy.

---

## 2. Relevant Disease Pages Discovered

We crawled and validated the following 11 topic and image gallery pages representing the six target disease classes:
1. **Lichen Sclerosus:**
   * `/images/lichen-sclerosus-images` (General gallery)
   * `/topics/penile-lichen-sclerosus-images` (Penile clinical presentations)
   * `/topics/vulval-lichen-sclerosus-images` (Vulval clinical presentations)
   * `/topics/extragenital-lichen-sclerosus-images` (Extragenital clinical presentations)
   * `/topics/perianal-lichen-sclerosus-images` (Perianal clinical presentations)
2. **Early Syphilis:**
   * `/topics/syphilis-images` (General syphilis presentations)
3. **Genital Warts:**
   * `/images/genital-wart-images` (Anogenital clinical presentations)
4. **Molluscum Contagiosum:**
   * `/topics/molluscum-contagiosum-images` (Molluscum lesions)
5. **Herpes Simplex:**
   * `/topics/herpes-simplex-images` (Oral/facial/body presentations)
   * `/topics/genital-herpes-images` (Anogenital presentations)
6. **Tinea:**
   * `/topics/tinea-corporis-images` (Body ringworm)
   * `/topics/tinea-pedis-images` (Athlete's foot)
   * `/images/tinea-capitis-images` (Scalp ringworm)

---

## 3. Discovered Candidate Counts

A total of **453 raw records** were crawled across the pages. After removing duplicates and filtering out non-early syphilis presentations, we compiled the following class-wise statistics:

| Disease Class | Discovered Unique Images | Clearly Relevant (Candidate) | Excluded Images | Duplicate Records | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Lichen Sclerosus** | 112 | 112 | 0 | 0 | Covers penile, vulval, extragenital, perianal types |
| **Early Syphilis** | 80 | 79 | 1 | 0 | Excludes tertiary and congenital syphilis records |
| **Genital Warts** | 29 | 29 | 0 | 0 | Anogenital condyloma presentations |
| **Molluscum Contagiosum** | 92 | 92 | 0 | 0 | Classical umbilicated papules |
| **Herpes Simplex** | 80 | 80 | 0 | 0 | Covers genital and zosteriform simplex herpes |
| **Tinea** | 60 | 60 | 0 | 0 | Covers pedis, capitis, and corporis varieties |
| **Total** | **453** | **451** | **2** | **0** | |

### Excluded Images Details:
The 2 excluded images under **Early Syphilis** are:
* Image from `/topics/syphilis-images` labeled as *"Tertiary syphilis"* (Late stage, not early syphilis).
* Image from `/topics/syphilis-images` labeled as *"Congenital syphilis"* (Infection from mother, different clinical entity).

---

## 4. Deduplication Findings

Our analysis identified **0 duplicate image listings** across the crawled pages:
* All 453 images are unique based on their source URL.
* Only one filename collision (`074.jpg`) exists across different CDN directories, which represents two different images. These are resolved by their unique URLs and will use unique local filenames if downloaded.

---

## 5. Metadata Availability

DermNet NZ provides the following fields programmatically:
* `image_asset_url`: Direct CDN/server link to the image.
* `description`: The caption/alt text accompanying the image, containing clinical diagnosis and occasionally anatomical details.
* `source_page_url`: The page where the image was found.
* `original_filename`: Derived from the CDN path.
* `patient_gender`: **Not available** (none of the pages feature gender fields).
* `anatomical_site` / `site_group`: Can be partially inferred from page context (e.g. `/topics/penile-lichen-sclerosus-images` implies `Penis` / `Genitals`) or description text, but is otherwise set to `NA` or requires manual confirmation.

---

## 6. Comparison & Supplementation Potential (DermNet vs STIAtlas)

DermNet NZ provides a strong candidate pool to supplement the currently organized STIAtlas dataset, especially for underrepresented classes:

| Class Name | STIAtlas Organized | Discovered DermNet Candidates | Supplementation Impact |
| :--- | :---: | :---: | :--- |
| **Lichen Sclerosus** | 35 | 112 | **Significant increase** (covers diverse skin/genital types) |
| **Early Syphilis** | 110 | 79 | Moderate increase |
| **Genital Warts** | 86 | 29 | Small/moderate increase |
| **Molluscum Contagiosum** | 12 | 92 | **Critical supplement** (+92 unique images) |
| **Herpes Simplex** | 64 | 80 | **Significant increase** |
| **Tinea** | 7 | 60 | **Critical supplement** (+60 unique images) |
| **Total** | **314** | **451** | **Double the dataset size** (from 314 to 765 total images) |

---

## 7. Licensing and Usage Considerations

> [!CAUTION]
> **FREE WATERMARKED DERMNET IMAGES ARE NOT APPROVED FOR AI/ML TRAINING OR TESTING UNDER THE CURRENT DERMNET IMAGE LICENCE.**

* **Copyright Ownership:** All images are copyrighted by the **DermNet New Zealand Trust** or individual contributing clinics/dermatologists.
* **Academic/Educational Policy:** DermNet allows the free use of **watermarked images** for non-commercial educational, teaching, and academic research purposes (including PowerPoint slides, academic papers, and journals). However, this free use license does **NOT** cover dataset creation, AI/ML training, validation, testing, or model building.
* **Redistribution Policy:** Redistribution of raw, unwatermarked images is strictly prohibited. Unwatermarked or high-quality images require purchasing a license from DermNet.

---

## 8. LICENSING BLOCKER

### Status: **BLOCKED**

The discovered DermNet NZ images **cannot be downloaded, copied, or utilized** in our project's dataset at this time. 

DermNet's official Image Licence explicitly restricts the use of their freely available watermarked images for AI/ML training or testing. This restriction applies to all model training, validation, and testing workflows, regardless of whether the models are intended for internal-only, academic, or commercial research. 

The discovered 451 candidate images may only be considered for our ML dataset **after appropriate permission/licensing for AI/ML use has been officially confirmed and secured** from the DermNet New Zealand Trust. 

Until such licensing is acquired, the dataset collection pipeline for DermNet remains fully halted.

---

## 9. Next Steps

1. **Keep Manifest Halted:** Keep the discovery manifest [`metadata/dermnet_manifest.csv`](file:///d:/STI_Project/02_DermNet/metadata/dermnet_manifest.csv) as-is for reference, but do **NOT** run any download processes.
2. **Contact DermNet NZ Trust (Optional):** If DermNet data remains essential for supplementing underrepresented classes (like Molluscum and Tinea), project leads must contact the DermNet New Zealand Trust to obtain a custom research license for AI/ML training.
3. **Focus on GISP:** Proceed to the next dataset phase (GISP) to evaluate and prepare antimicrobial-resistance metadata.
