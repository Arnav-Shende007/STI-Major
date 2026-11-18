# STIAtlas Source Analysis

This document provides a comprehensive research analysis of the STIAtlas dataset, referencing the official online source and the related publication *"Radiomics analysis for the early diagnosis of common sexually transmitted infections and skin lesions"* (PLOS Digital Health, 2025).

---

## 1. Source

* **Official Source URL**: [https://stiatlas.org/](https://stiatlas.org/)
* **Source Description**: The STI Atlas is a free, open-access, online clinical image library developed and maintained by the **Melbourne Sexual Health Centre (MSHC)**, a service of Alfred Health in Melbourne, Australia.
* **Clinical Integrity**: All diagnoses in the atlas are confirmed using gold-standard clinical methods, including serological and molecular (PCR) testing.

---

## 2. Dataset Size & Discrepancy

* **Total Images on Live Website**: The active website hosts exactly **660 unique clinical images** across all conditions.
* **Research Dataset Subset**: The 2025 PLOS Digital Health paper reports the analysis of a curated subset of **597 images** belonging to the six target classes.
* **Currently Accessible Mapped Images**: Out of the 660 unique images currently accessible on the website, only **316 images** map to the six target classes. The other 344 belong to non-target classes (e.g., Scabies, Chlamydia, Lichen planus, Herpes zoster).
* **Important Limitation**: The original 597-image research dataset **cannot currently be reproduced completely** from the public website alone. 

> [!WARNING]
> We must NOT duplicate, synthesize, or invent missing records to reach 597. We also must NOT download unrelated conditions to inflate counts. We will collect only the 316 currently accessible verified records.
> Possible explanations for the missing 281 target images include:
> 1. MSHC pruning or removing older/lower-quality images from the public library since the paper was prepared (between 2024 and 2026).
> 2. The paper's authors utilizing a private or non-public database subset from MSHC that was never fully uploaded to the public website despite the paper's data availability statement.

---

## 3. Classes & Counts Comparison

Below is the comparison between the live public crawl counts and the reported counts in the 2025 paper:

| Class/Condition Name | Category | Discovered Count | Published Text Count | Published Table Count | Discrepancy (vs Table) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Lichen Sclerosus** | Skin Lesion (Non-STI) | 35 | 145 | 145 | -110 |
| **Early Syphilis** | STI | 112 | 143 | 143 | -31 |
| **Genital Warts** | STI | 86 | 127 | 121 | -35 |
| **Molluscum Contagiosum** | STI | 12 | 66 | 66 | -54 |
| **Herpes Simplex** | STI | 64 | 128 | 61 | +3 |
| **Tinea** | Skin Lesion (Non-STI) | 7 | 61 | 61 | -54 |
| **Total** | | **316** | **670** | **597** | **-281** |

*Note: The published paper contains internal inconsistencies, stating "597 images" in the abstract/methods but summing to 670 in the introductory text sentences (e.g., listing 128 herpes cases and 127 warts cases). The detailed table breakdown (S1 Table) sums to 597.*

---

## 4. Anatomical Sites & Grouping

Images are categorized by the anatomical location of the lesion. 

### Source Anatomical Labels
The STIAtlas website classifies images under the following specific site tags:
* `Anus`, `Buttock`, `Cervix`, `Eye`, `Glans penis`, `Groin`, `Mouth`, `Penis`, `Pubis`, `Scrotum`, `Skin - general`, `Thigh`, `Urethra`, `Urethral meatus`, `Vagina`, `Vulva`.

### Grouped Anatomical Sites (`site_group`)
For machine-learning modeling, these original locations are mapped to three primary sites without overwriting the original site labels:
1. **Genitals**: Includes external/internal genitalia (penis, scrotum, vulva, perineum, vagina, cervix, glans penis, urethra, urethral meatus, etc.).
2. **Anus**: Specifically denotes the perianal region.
3. **Other Skin**: Covers all other regions (groin, pubis, buttock, thigh, mouth, eye, general skin, etc.).

---

## 5. Disease Grade / Severity

* **Grade/Severity Status**: **Unavailable**.
* **Detail**: There is no disease grading, severity rating, or clinical staging (e.g., mild, moderate, severe) provided by the source. We must not attempt to invent or visually infer severity metrics.

---

## 6. Download/Collection Method

* **No Bulk Download/API**: The website does not offer a bulk archive (like a zip file) or a public API.
* **Scraper Pipeline**: Programmatic collection is executed using our Python script [`collect_stiatlas.py`](file:///d:/STI_Project/01_STIAtlas/collect_stiatlas.py) utilizing `requests` and `BeautifulSoup` within the session context.
* **Crawl Logic**: The script initializes the ASP.NET session state via a dummy GET followed by a search query POST, then paginates page-by-page from index 1 to 83.

---

## 7. Metadata Field Structure

The metadata manifest is saved under [`metadata/stiatlas_manifest.csv`](file:///d:/STI_Project/01_STIAtlas/metadata/stiatlas_manifest.csv) and contains:
* `image_id`: Unique identifier (e.g., `STIATLAS_001`).
* `source`: `"STIAtlas"` for all records.
* `disease_class`: Mapped diagnosis name (one of the six classes).
* `source_page_url`: The URL of the page containing the image.
* `image_asset_url`: Direct high-resolution image file link.
* `anatomical_site`: Exact original site label provided by the source.
* `site_group`: Grouped anatomical site (`Genitals`, `Anus`, `Other Skin`).
* `patient_gender`: `Male`, `Female`, or `Unspecified`.
* `description`: Clinical description accompanying the image.
* `original_filename`: Filename from URL.
* `local_filename`: Local path where downloaded.
* `sha256`: SHA-256 file hash.
* `file_extension`: Extracted file extension.
* `file_size`: Downloaded file size in bytes.
* `collection_status`: Status of collection (`pending`, `collected`, `failed`).
* `download_timestamp`: Download time in UTC.

---

## 8. Licensing and Usage

* **Usage Terms**: Royalty-free for **educational, teaching, and academic research purposes**.
* **Redistribution Restriction**: The website states: *"Please do not redistribute these images. If you wish to share them with your colleagues, please point them to this website."*
* **Modification Restriction**: Images must not be altered, other than for necessary resizing.
* **Commercial Restrictions**: Commercial use of the images is prohibited.

---

## 9. Collection Risks & Mitigation

1. **Redistribution Policy**: The restriction on redistributing images means that we must not upload the raw clinical images to a public repository (such as GitHub).
2. **Web Page Structure Changes**: If the HTML structure of `stiatlas.org` changes, scraping scripts will break.
3. **Session Dependencies**: ASP.NET requires active session tracking; directly fetching paginated URLs returns HTTP 500. This is mitigated by session tracking in our Python crawler.
4. **Data Discrepancy**: Since only 316 of 597 images are currently discoverable on the live site, models trained on this data will represent a smaller dataset. This is documented in [`metadata/stiatlas_collection_summary.csv`](file:///d:/STI_Project/01_STIAtlas/metadata/stiatlas_collection_summary.csv).
