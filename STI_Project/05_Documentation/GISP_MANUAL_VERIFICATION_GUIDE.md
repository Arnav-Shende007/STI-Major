# CDC GISP / CARGOS Manual Verification Guide

This document lists the items that require manual review and verification in the 2023 CDC GISP profiles dataset. These items represent values that are not present in standard sections, are ambiguous, or failed to parse programmatically with high confidence.

## Table of Contents
1. [Overview](#1-overview)
2. [Verification Items Checklist](#2-verification-items-checklist)
3. [Manual Verification Instructions](#3-manual-verification-instructions)

---

## 1. Overview
Surveillance profiles from the CDC are published as PDF reports. While the programmatic parser extracted site-specific trends with 100% success for all 30 clinics, some items (such as Ciprofloxacin 5-year periods in Table 1) are mathematically or structurally missing from the source document.

---

## 2. Verification Items Checklist

The following is a list of items to inspect:

| PDF Document | Page Number | Table/Section | Sentinel Site | Year/Period | Drug | Extracted Value | Review Task / What to Verify |
| :--- | :---: | :--- | :--- | :---: | :--- | :---: | :--- |
| **National (251952)** | 12 | Table 1D | National | 1999-2023 | Ciprofloxacin | *(blank)* | Verify if Ciprofloxacin 5-year periods MIC parameters are available in the report. |

---

## 3. Manual Verification Instructions

### Item 1: Ciprofloxacin 5-Year Periods (National Profile)
* **PDF Report**: *Sexually Transmitted Disease Surveillance 2023: Enhanced Gonococcal Isolate Surveillance Project Profiles* (Stacks ID: [251952](https://stacks.cdc.gov/view/cdc/251952))
* **Page to Inspect**: Page 12
* **Row/Column to Inspect**: Look for **Table 1D** or any other sub-table under Table 1.
* **Instructions**:
  1. Open the National Profile PDF (`cdc_251952.pdf`).
  2. Scroll to Page 12.
  3. Notice that Table 1 only has sub-tables **1A (Cefixime)**, **1B (Ceftriaxone)**, and **1C (Azithromycin)**. There is **no Table 1D for Ciprofloxacin**.
  4. Confirm that Ciprofloxacin 5-year period MIC parameters are indeed omitted from the Table 1 index.
  5. Keep the Ciprofloxacin 5-year rows in the final CSV as blank/empty to represent this absence, with a note: `"Ciprofloxacin 5-year parameters omitted in Table 1 index."`
