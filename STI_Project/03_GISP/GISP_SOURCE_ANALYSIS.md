# GISP Source Analysis

This directory contains the metadata and documentation for the Centers for Disease Control and Prevention (CDC) **Gonococcal Isolate Surveillance Project (GISP)** and the **Combatting Antimicrobial Resistant Gonorrhea and Other STIs (CARGOS)** project.

Refer to the primary documentation file:
[`05_Documentation/GISP_SOURCE_ANALYSIS.md`](file:///d:/STI_Project/05_Documentation/GISP_SOURCE_ANALYSIS.md) for the complete scientific and clinical analysis.

## Key Findings

1. **Pathogen Constraint**: GISP monitors only *Neisseria gonorrhoeae*.
2. **Visual Overlap**: None of the 6 classes in the `STIAtlas` visual dataset (Lichen Sclerosus, Early Syphilis, Genital Warts, Molluscum, Herpes Simplex, Tinea) have antimicrobial resistance tracked by GISP.
3. **Treatment recommendation branching**: GISP resistance data can only support a Gonorrhea-specific treatment branch. The 6 visual STI classes will require separate clinical guideline references.
4. **Data format**: Data is published as PDF reports on CDC Stacks. Reclaiming this data requires manual PDF inspection and table extraction.
5. **Licensing**: Public Domain (US Government Work).

## Proposed Schema

The database schema is defined in [`metadata/gisp_data_dictionary.csv`](file:///d:/STI_Project/03_GISP/metadata/gisp_data_dictionary.csv).
The source links are managed in [`metadata/gisp_source_manifest.csv`](file:///d:/STI_Project/03_GISP/metadata/gisp_source_manifest.csv).
