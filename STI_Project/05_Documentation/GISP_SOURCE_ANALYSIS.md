# CDC GISP / CARGOS Dataset Source Analysis

This document provides a comprehensive research analysis of the Centers for Disease Control and Prevention (CDC) **Gonococcal Isolate Surveillance Project (GISP)** and its successor **Combatting Antimicrobial Resistant Gonorrhea and Other STIs (CARGOS)**. It establishes the scientific scope, temporal/geographic ranges, and clinical integrations of antimicrobial susceptibility data for our multimodal treatment recommendation system.

---

## 1. What is GISP?

The **Gonococcal Isolate Surveillance Project (GISP)** is a sentinel surveillance system established by the CDC in **1986**. 
* **Primary Objective**: To monitor trends in antimicrobial susceptibility of *Neisseria gonorrhoeae* (the bacterium causing gonorrhea) in the United States.
* **Clinical Significance**: GISP provides the scientific, evidence-based foundation for selecting recommended gonococcal therapies, directly informing the CDC’s Sexually Transmitted Infections (STI) Treatment Guidelines.
* **Pathogen Covered**: Exclusively **`Neisseria gonorrhoeae`**. It does **NOT** monitor or collect data on any other bacterial, viral, or fungal STI pathogens.

---

## 2. Official CDC Sources

The primary CDC resources identified for GISP/CARGOS surveillance data include:
1. **Official GISP Profiles Portal**: [https://www.cdc.gov/sti-statistics/gisp-profiles/](https://www.cdc.gov/sti-statistics/gisp-profiles/) (Host for national/site-specific profile summaries).
2. **CDC Stacks Repository**: [https://stacks.cdc.gov/](https://stacks.cdc.gov/) (The official digital archive hosting historical and recent annual PDF profiles).
3. **CARGOS Surveillance Details**: [Combatting Antimicrobial Resistant Gonorrhea and Other STIs (CARGOS) Project](https://www.cdc.gov/sti-statistics/gisp-profiles/) (The successor program launched on August 1, 2024, to broaden surveillance capabilities).

---

## 3. Exact 2023 CDC Stacks Publications Mapping

The 2023 surveillance data is split across two official PDF publications in the CDC Stacks repository:

### A. National Profile Report
* **Exact PDF Title:** *Sexually Transmitted Disease Surveillance 2023: Enhanced Gonococcal Isolate Surveillance Project Profiles*
* **Official CDC Stacks URL:** [https://stacks.cdc.gov/view/cdc/251952](https://stacks.cdc.gov/view/cdc/251952)
* **Direct PDF URL:** [Download PDF (251952)](https://stacks.cdc.gov/view/cdc/251952/cdc_251952_DS1.pdf)
* **Publication Date:** August 2025 (Metadata indexed on April 14, 2025)
* **Page Count:** 24 pages
* **Table 1 (National Trends) Location:** Located on **Page 12**
  * **Table Title:** *"Table 1: Antimicrobial Minimum Inhibitory Concentration Parameters by 5-Year Periods in the Gonococcal Isolate Surveillance Project (GISP), 1999–2023"*
  * **Table Mappings (Antibiotics of Interest):**
    * **Table 1A (Page 12):** **Cefixime** (Elevated MIC $\ge 0.25\ \mu\text{g/mL}$ percentages)
    * **Table 1B (Page 13):** **Ceftriaxone** (Elevated MIC $\ge 0.125\ \mu\text{g/mL}$ percentages)
    * **Table 1C (Page 14):** **Azithromycin** (Resistance $\ge 2.0\ \mu\text{g/mL}$ percentages)
    * **Table 1D (Page 15):** **Ciprofloxacin** (Resistance $\ge 1.0\ \mu\text{g/mL}$ percentages)

### B. Site-Specific Profiles Report
* **Exact PDF Title:** *Sexually Transmitted Disease Surveillance 2023: Enhanced Gonococcal Isolate Surveillance Project (GISP) Site-Specific Profiles*
* **Official CDC Stacks URL:** [https://stacks.cdc.gov/view/cdc/251953](https://stacks.cdc.gov/view/cdc/251953)
* **Direct PDF URL:** [Download PDF (251953)](https://stacks.cdc.gov/view/cdc/251953/cdc_251953_DS1.pdf)
* **Publication Date:** August 2025
* **Page Count:** 155 pages
* **Site Profiles Location:** Interspersed from **Page 6 to Page 154** (each participating sentinel clinic has a dedicated one-page summary).
  * **Table Mapping:** The individual clinic tables (usually titled *"Table 1: Antimicrobial Susceptibility of Neisseria gonorrhoeae Isolates..."*) contain the annual percentages of isolates with resistance or elevated MICs for the target drugs.

---

## 4. Fields to Manually Transcribe

For the eventual resistance dataset, the following fields must be manually transcribed from the mapped tables:
1. `year` (Integer) — e.g. 2019 to 2023
2. `geography` (String) — e.g. "National" (from report 251952) or the sentinel clinic city name like "Atlanta" (from report 251953)
3. `pathogen` (String) — Fixed as "Neisseria gonorrhoeae"
4. `antimicrobial` (String) — "Ceftriaxone", "Cefixime", "Azithromycin", or "Ciprofloxacin"
5. `mic_threshold_ug_ml` (Float) — 0.125 (Ceftriaxone), 0.25 (Cefixime), 2.0 (Azithromycin), or 1.0 (Ciprofloxacin)
6. `resistance_measure` (String) — "Elevated MIC" or "Resistance"
7. `resistance_percent` (Float) — The percentage value recorded in the table column
8. `sample_count` (Integer) — The number of tested isolates representing the cohort denominator

---

## 5. Temporal Range & Transition to CARGOS

* **Historical Range**: 1986 – 2023.
* **Most Recent Data**: 
  * **2023 GISP Profiles**: Published in **August 2025** as part of the *Sexually Transmitted Disease Surveillance 2023* release.
  * **2024 GISP/CARGOS Profiles**: Currently being transitionally reported in CDC Stacks.
* **CARGOS Transition Status**: On **August 1, 2024**, GISP and eGISP (Enhanced GISP) were officially integrated into the **CARGOS** project. CARGOS continues the core surveillance of *N. gonorrhoeae* susceptibility while augmenting rapid outbreak responses and preparedness for other drug-resistant STIs.

---

## 6. Monitored Drugs & MIC Resistance Thresholds

GISP tracks antimicrobial susceptibility by measuring the **Minimum Inhibitory Concentration (MIC)**—the lowest concentration of an antibiotic that prevents visible bacterial growth. Because the Clinical & Laboratory Standards Institute (CLSI) does not define resistance breakpoints for all agents, CDC uses specific "Elevated MIC" and "Resistance" thresholds for public health tracking:

| Antimicrobial Agent | Monitoring Status | MIC Interpretive Threshold | Classification |
| :--- | :---: | :---: | :--- |
| **Ceftriaxone** | Active | $\ge 0.125\ \mu\text{g/mL}$ | Elevated MIC (Alert Level) |
| **Cefixime** | Active | $\ge 0.25\ \mu\text{g/mL}$ | Elevated MIC (Alert Level) |
| **Azithromycin** | Active | $\ge 2.0\ \mu\text{g/mL}$ | Resistance (CLSI criteria) |
| **Ciprofloxacin** | Active | $\ge 1.0\ \mu\text{g/mL}$ | Resistance (CLSI criteria) |
| **Penicillin** | Active | $\ge 2.0\ \mu\text{g/mL}$ or $\beta$-lactamase positive | Resistance (CLSI criteria) |
| **Tetracycline** | Active | $\ge 2.0\ \mu\text{g/mL}$ | Resistance (CLSI criteria) |
| **Gentamicin** | Active | No established breakpoints | Monitored (MIC distribution only) |

---

## 7. Geographic Resolution (National vs. Sentinel Sites)

The CDC provides geographic trends at two distinct resolutions:
1. **National Trends**: Aggregated statistics across all testing centers representing overall US gonococcal susceptibility.
2. **Site-Specific Profiles**: Granular data from individual sentinel clinics (e.g., Atlanta, San Francisco, Seattle) participating in the monthly isolate sampling network. 
* *Note: Geography is defined by the sentinel clinic site name (city/region); there is no arbitrary "region" grouping in the CDC source.*

---

## 8. Scientific Alignment with our 6-Class Vision Dataset

### CRITICAL SCIENTIFIC CONSTRAINT:
Our project includes a **6-class STIAtlas image dataset** representing visible skin lesions, and a **multimodal treatment recommendation engine**. 

Because **GISP is strictly limited to *Neisseria gonorrhoeae***, it has the following alignment with the six classes:

1. **Lichen Sclerosus (Autoimmune/Inflammatory)**: **NO** GISP data available. Treated with topical steroids.
2. **Early Syphilis (*Treponema pallidum* - Bacterial)**: **NO** GISP data available. (Syphilis resistance, such as azithromycin resistance, is tracked via separate studies, not GISP).
3. **Genital Warts (HPV - Viral)**: **NO** GISP data available. Treated with local ablation.
4. **Molluscum Contagiosum (MCV - Viral)**: **NO** GISP data available. Treated with local ablation.
5. **Herpes Simplex (HSV - Viral)**: **NO** GISP data available. Treated with systemic antivirals (Acyclovir).
6. **Tinea (Dermatophytes - Fungal)**: **NO** GISP data available. Treated with topical/systemic antifungals.

### Conclusion on Treatment Connection:
* **Gonorrhea Treatment Branch Only**: GISP can **exclusively** support the Gonorrhea treatment recommendation branch of our system (e.g. if the multimodal framework takes clinical symptoms or test results for Gonorrhea as a non-visual STI input).
* **No Visual Disease Overlap**: None of the 6 visual skin lesion classes from STIAtlas can map to GISP data.
* **Separation of Evidence Sources**: For our 6 visual STI classes, the treatment engine must utilize separate clinical guidelines (such as WHO or CDC STI Treatment Guidelines) rather than GISP surveillance data.

---

## 9. Proposed Resistance Dataset Schema

We propose the following clean database schema for the eventual GISP resistance table in `03_GISP/`:

* `year` (Integer) — Temporal key (e.g. 2023)
* `geography` (String) — Clinic site name or "National"
* `pathogen` (String) — Fixed as "Neisseria gonorrhoeae"
* `antimicrobial` (String) — e.g. "Ceftriaxone"
* `mic_threshold_ug_ml` (Float) — e.g. 0.125
* `resistance_measure` (String) — "Resistance" or "Elevated MIC"
* `resistance_percent` (Float) — e.g. 1.2 (percentage of isolates exceeding threshold)
* `sample_count` (Integer) — Number of isolates tested (cohort size)
* `source` (String) — "CDC GISP" or "CDC CARGOS"
* `source_url` (String) — Link to the specific CDC Stacks report/profile

---

## 10. Licensing and Data Use

* **Licensing**: CDC data and surveillance reports are works of the United States Government and reside in the **Public Domain**.
* **Usage Permissions**: The tables, data, and profiles may be freely copied, analyzed, and integrated into our machine-learning dataset and recommendations without licensing costs, provided proper citation is given to the CDC.

---

## 11. Automated vs. Manual Work

### AUTOMATABLE:
* **Pipeline Database Population**: Writing scripts to parse standard CSV/JSON tables if they are published.
* **Calculations & Validation**: Computing means, site comparisons, and checking for duplicates.

### MANUAL REVIEW REQUIRED (Licensing & Parsing Blocker):
* **No Raw Spreadsheets**: The CDC publishes GISP national and site-specific profiles **exclusively as PDF reports** (e.g. in CDC Stacks) rather than raw CSVs/Excels.
* **Visual Verification / PDF Extraction**: Reading and validating resistance percentages requires opening the annual PDF report (e.g., *Sexually Transmitted Disease Surveillance 2023: Enhanced Gonococcal Isolate Surveillance Project Profiles*) and manually verifying the numbers in the data tables to prevent PDF parsing errors.
* **Manual Data Entry Needed**: A clinical researcher must open:
  1. The latest [CDC Stacks PDF for the 2023 GISP Profiles](https://stacks.cdc.gov/).
  2. Locate **Table 1** (National Trends) and **Site Tables** (for site-specific trends).
  3. Extract ceftriaxone, cefixime, and azithromycin resistance percentages and log them into the proposed schema.

---

## 12. Recommended Next Step

1. **Obtain Approval**: Wait for user approval of this source analysis, the proposed data schema, and the clinical alignment findings.
2. **Execute Manual Extraction Plan**: Once approved, create the final CSV dataset (`03_GISP/metadata/gisp_resistance_data.csv`) by manually entering the verified national trends for the target drugs (Ceftriaxone, Cefixime, Azithromycin, Ciprofloxacin) for recent years (2018–2023) using the CDC PDF tables.
