# Kaggle DermNet Datasets Comparative Analysis Report

This report evaluates two Kaggle datasets compiled from DermNet NZ, investigating their folder/class structures, class availability, image counts, splits, and licensing concerns to determine their suitability for our 6-class STI lesion classification project.

---

## 1. Comparative Analysis Matrix

| Feature | Dataset A: Shubham Goel (`shubhamgoel27/dermnet`) | Dataset B: Thomas Rademaker (`thomasrademaker/dermnetnz-100-cleaned`) |
| :--- | :--- | :--- |
| **Kaggle URL** | [shubhamgoel27/dermnet](https://www.kaggle.com/datasets/shubhamgoel27/dermnet) | [thomasrademaker/dermnetnz-100-cleaned](https://www.kaggle.com/datasets/thomasrademaker/dermnetnz-100-cleaned) |
| **Total Images** | ~19,559 images | ~600 images |
| **Total Classes** | 23 clinical groups (super-classes) | 8 ISIC 2019 categories |
| **Class Structure** | Broad clinical disease categories | Specific cancer and benign tumor groups |
| **Train/Test Split** | Pre-split: `train/` (~15,557) and `test/` (~4,002) | Flat structure (no pre-split) |
| **Metadata File** | None (inferred from folder/filename slugs) | None (inferred from folder/filename slugs) |
| **Source Provenance** | Scraped from DermNet NZ | Scraped from DermNet NZ (cleaned of non-lesion artifacts) |
| **Watermarks Present** | Yes (contains "DermNet NZ" watermarks) | Yes (contains "DermNet NZ" watermarks) |
| **License on Kaggle** | CC0: Public Domain | CC BY 4.0 |
| **Legal/Copyright Owner** | **DermNet New Zealand Trust** | **DermNet New Zealand Trust** |

---

## 2. Target Class Availability & Image Counts

Our project focuses on exactly six target classes: **Lichen Sclerosus**, **Early Syphilis**, **Genital Warts**, **Molluscum Contagiosum**, **Herpes Simplex**, and **Tinea**.

### Dataset A: Shubham Goel (`shubhamgoel27/dermnet`)
None of our 6 target classes are represented as independent classes/folders. Instead, they are nested inside broad category folders. To extract them, we would have to search the filenames (which retain DermNet topic slugs like `herpes-simplex-1.jpg`) and filter them:
* **Tinea**: Nested under `Tinea Ringworm Candidiasis and other Fungal Infections` (approx. 60 usable images).
* **Herpes Simplex**: Nested under `Herpes HPV and other STDs Photos` (approx. 80 usable images).
* **Molluscum Contagiosum**: Nested under `Warts Molluscum and other Viral Infections` (approx. 92 usable images).
* **Genital Warts**: Nested under `Warts Molluscum and other Viral Infections` or `Herpes HPV and other STDs Photos` (approx. 29 usable images).
* **Lichen Sclerosus**: Nested under `Psoriasis Lichen Planus and related diseases` (approx. 112 usable images).
* **Early Syphilis**: Nested under `Herpes HPV and other STDs Photos` (approx. 79 usable images).

> [!NOTE]
> Out of the 19,559 images in this dataset, only about **450 images** (~2.3% of the total dataset) correspond to our 6 target classes. The remaining 97.7% are completely irrelevant (e.g. Acne, Eczema, Hair Loss, Psoriasis, Melanoma).

### Dataset B: Thomas Rademaker (`thomasrademaker/dermnetnz-100-cleaned`)
**Zero (0) target classes are available.** 
This dataset is organized strictly by **ISIC 2019 categories** (`akiec`, `bcc`, `bkl`, `df`, `mel`, `nv`, `scc`, `vasc`) for skin cancer and benign tumor classification. It contains no clinical photographs for STIs, fungal, or viral lesions.

---

## 3. Licensing and Legal Constraints

> [!CAUTION]
> **BOTH KAGGLE DATASETS ARE STRICTLY BLOCKED FOR USE IN OUR PROJECT DUE TO COPYRIGHT VIOLATIONS.**

* **No Uploader Ownership:** Neither Kaggle uploader owns the copyright to the images in their datasets. Both scraped the images directly from DermNet NZ without authorization.
* **Copyright Owner:** The **DermNet New Zealand Trust** holds copyright ownership of all images.
* **Licensing Blocker:** The official **DermNet Image Licence** explicitly prohibits utilizing their freely available watermarked images for dataset creation or AI/ML training, validation, and testing. 
* **CC0/CC-BY Invalidity:** The CC0 and CC-BY labels applied by the Kaggle uploaders are legally invalid because they had no copyright authority to distribute the scraped assets under those terms.
* **Consequence:** Downloading, copying, or integrating either dataset into our project would violate international copyright law and DermNet's terms of service.

---

## 4. Teammate Proposal Evaluation & Recommendations

### Which dataset is better for our project?
**Shubham Goel's dataset** is the only one that could theoretically be useful, as it contains images matching some of our target classes. **Thomas Rademaker's dataset is completely irrelevant** to our project.

### Should we use it alongside STIAtlas?
**No.** We must not use either dataset alongside STIAtlas due to the licensing blocker. The raw organized `01_STIAtlas/organized/` dataset remains our only verified, legally compliant image dataset.

### Should we merge the datasets first and split later?
**No. We recommend rejecting the teammate's proposal to merge and split these datasets.** 
1. **Legal Block**: Merging these Kaggle datasets with STIAtlas violates project licensing policies.
2. **Structural Flaw**: Even if licensing were resolved, merging first and splitting later at the database level is not recommended. Shubham Goel's dataset contains 97.7% irrelevant images, and we would need to programmatically filter and extract only our 6 target classes first.
3. **Data Leakage Risk**: A random train/test split on a merged dataset without clinical deduplication could lead to data leakage if identical patients exist in both sources.

---

## 5. Next Steps

1. **Reject Kaggle Datasets:** Finalize the decision to exclude both Kaggle datasets from the machine-learning pipeline.
2. **Maintain STIAtlas Independence:** Continue to treat [`01_STIAtlas/organized/`](file:///d:/STI_Project/01_STIAtlas/organized) as the sole, immutable image training subset (314 verified clinical photos).
3. **Request Licensing (Optional):** If supplementary images are absolutely required, project leads should contact the **DermNet New Zealand Trust** to acquire a formal research license.
