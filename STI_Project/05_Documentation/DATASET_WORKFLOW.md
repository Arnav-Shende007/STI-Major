# Dataset Workflow Documentation

This document outlines the initial workflow and rules for preparing the dataset workspace for the STI Project.

## Dataset Processing Workflow

1. **First Target Dataset**: STIAtlas is the first dataset to be processed.
2. **Original Data Preservation**: All original downloaded files must be preserved in their raw state inside `01_STIAtlas/raw/`. They must never be modified or overwritten.
3. **Data Organization**: Processed and renamed copies of the images will eventually be placed into `01_STIAtlas/organized/`.
4. **Metadata Management**: Metadata associated with the STIAtlas dataset will eventually be stored in CSV files in `01_STIAtlas/metadata/`.
5. **Class Verification**: The exact STIAtlas class names must be verified from the source before any class-specific subfolders are created.
6. **Future Datasets**: DermNet and GISP will be handled later. No processing or operations should be performed inside `02_DermNet/` or `03_GISP/` at this stage.
