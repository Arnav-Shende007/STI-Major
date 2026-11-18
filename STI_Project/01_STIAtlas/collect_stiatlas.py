import os
import sys
import re
import csv
import time
import hashlib
import argparse
import collections
import io
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, quote
from PIL import Image

# Base URL for STIAtlas
URL_BASE = "https://stiatlas.org/SearchAtlas.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 6 Target Classes
TARGET_CLASSES = [
    "Lichen Sclerosus",
    "Early Syphilis",
    "Genital Warts",
    "Molluscum Contagiosum",
    "Herpes Simplex",
    "Tinea"
]

def map_to_class(stis, others):
    """
    Maps raw categories to one of the 6 target classes.
    Uses exact matches based on known truncated labels from the site.
    """
    stis = stis.strip()
    others = others.strip()
    
    # 1. Lichen Sclerosus (website truncates to Lichen sclerosu)
    if others == "Lichen sclerosu":
        return "Lichen Sclerosus"
    # 2. Tinea (website truncates to Tine)
    if others == "Tine":
        return "Tinea"
    # 3. Molluscum Contagiosum
    if stis == "Molluscum contagiosum":
        return "Molluscum Contagiosum"
    # 4. Herpes Simplex
    if stis in ["Herpes simplex", "Herpes simplex , HIV"]:
        return "Herpes Simplex"
    # 5. Early Syphilis (includes primary and secondary syphilis)
    if any(s in stis for s in ["Primary syphilis", "Secondary syphilis"]):
        return "Early Syphilis"
    # 6. Genital Warts (includes warts and HPV)
    if any(w in stis for w in ["HPV", "Warts"]):
        return "Genital Warts"
        
    return None

def get_site_group(anatomical_site):
    """
    Groups anatomical sites into: Genitals, Anus, Other Skin, or NA.
    """
    if not anatomical_site or anatomical_site == "NA" or anatomical_site == "-----":
        return "NA"
    
    site_lower = anatomical_site.lower()
    
    # Check for Anus
    if 'anus' in site_lower or 'perianal' in site_lower:
        return "Anus"
        
    # Check for Genitals
    genital_keywords = ['penis', 'scrotum', 'vulva', 'vagina', 'cervix', 'glans', 'urethra', 'meatus', 'perineum']
    if any(kw in site_lower for kw in genital_keywords):
        return "Genitals"
        
    # All other sites map to Other Skin
    return "Other Skin"

def parse_alt(alt_text):
    """
    Parses the structured alt text of STIAtlas thumbnails.
    Example: *Title*STIs: X*Investigations: Y*Sex: Z*Sites: A*Syndromes: B*Photo: C*Tags: D*Description*~/images/full/file.jpg*Other conditions: E
    """
    if not alt_text:
        return {}
        
    parts = [p.strip() for p in alt_text.split("*") if p.strip()]
    
    data = {
        "title": "",
        "stis": "-----",
        "investigations": "-----",
        "sex": "Unspecified",
        "sites": "-----",
        "syndromes": "-----",
        "photo": "-----",
        "tags": "-----",
        "description": "NA",
        "full_image_path": "",
        "other_conditions": "-----"
    }
    
    if parts:
        data["title"] = parts[0]
        
    for part in parts[1:]:
        if part.startswith("STIs:"):
            data["stis"] = part.replace("STIs:", "").strip()
        elif part.startswith("Investigations:"):
            data["investigations"] = part.replace("Investigations:", "").strip()
        elif part.startswith("Sex:"):
            data["sex"] = part.replace("Sex:", "").strip()
        elif part.startswith("Sites:"):
            data["sites"] = part.replace("Sites:", "").strip()
        elif part.startswith("Syndromes:"):
            data["syndromes"] = part.replace("Syndromes:", "").strip()
        elif part.startswith("Photo:"):
            data["photo"] = part.replace("Photo:", "").strip()
        elif part.startswith("Tags:"):
            data["tags"] = part.replace("Tags:", "").strip()
        elif part.startswith("Other conditions:"):
            data["other_conditions"] = part.replace("Other conditions:", "").strip()
        elif part.startswith("~/images/full/"):
            data["full_image_path"] = part.strip()
        else:
            if not data["full_image_path"]:
                data["description"] = part
                
    return data

def crawl_manifest(metadata_dir):
    """
    Crawls stiatlas.org pages and builds a list of candidate records.
    """
    session = requests.Session()
    print("Connecting to STIAtlas and obtaining viewstate...")
    try:
        r_init = session.get(URL_BASE, headers=HEADERS, timeout=10)
        soup_init = BeautifulSoup(r_init.text, "html.parser")
        
        viewstate = soup_init.find("input", id="__VIEWSTATE").get("value", "")
        generator = soup_init.find("input", id="__VIEWSTATEGENERATOR").get("value", "")
        validation = soup_init.find("input", id="__EVENTVALIDATION").get("value", "")
    except Exception as e:
        print(f"Error initializing page: {e}")
        return []

    # Send search request to list all images
    print("Initiating full database query...")
    search_data = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": generator,
        "__EVENTVALIDATION": validation,
        "ctl00$ContentPlaceHolder1$ddListSex": "-----",
        "ctl00$ContentPlaceHolder1$ddListSite": "-----",
        "ctl00$ContentPlaceHolder1$ddListSyndrome": "-----",
        "ctl00$ContentPlaceHolder1$ddListCondition": "-----",
        "ctl00$ContentPlaceHolder1$ddListOtherCondition": "-----",
        "ctl00$ContentPlaceHolder1$ddListLab": "-----",
        "ctl00$ContentPlaceHolder1$btnDisplay": "SEARCH"
    }

    try:
        r_post = session.post(URL_BASE, data=search_data, headers=HEADERS, timeout=15)
        soup_post = BeautifulSoup(r_post.text, "html.parser")
    except Exception as e:
        print(f"Error executing search POST: {e}")
        return []

    # Find total pages from pager
    pager = soup_post.find(id="ContentPlaceHolder1_pnlBottomPager")
    total_pages = 1
    if pager:
        page_links = pager.find_all("a")
        pages = []
        for l in page_links:
            t = l.text.strip()
            if t.isdigit():
                pages.append(int(t))
        if pages:
            total_pages = max(pages)
            
    print(f"Total pages found: {total_pages}")
    
    raw_records = []
    
    def extract_page_images(soup, page_num):
        count = 0
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "thumbnail" in src:
                alt = img.get("alt", "")
                parsed = parse_alt(alt)
                if parsed:
                    parsed["thumbnail_src"] = src
                    parsed["page_num"] = page_num
                    raw_records.append(parsed)
                    count += 1
        return count

    # Page 1
    p1_count = extract_page_images(soup_post, 1)
    print(f"Page 1: extracted {p1_count} records")
    
    # Pages 2 to N
    for p in range(2, total_pages + 1):
        # Polite delay
        time.sleep(0.5)
        try:
            r_page = session.get(f"{URL_BASE}?pageidx={p}", headers=HEADERS, timeout=10)
            if r_page.status_code == 200:
                soup_page = BeautifulSoup(r_page.text, "html.parser")
                p_count = extract_page_images(soup_page, p)
                print(f"Page {p}: extracted {p_count} records")
            else:
                print(f"Failed to fetch page {p} (status {r_page.status_code})")
        except Exception as e:
            print(f"Exception on page {p}: {e}")

    return raw_records

def process_pipeline():
    project_root = Path("d:/STI_Project")
    stiatlas_dir = project_root / "01_STIAtlas"
    metadata_dir = stiatlas_dir / "metadata"
    raw_dir = stiatlas_dir / "raw"
    
    metadata_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = metadata_dir / "stiatlas_manifest.csv"
    duplicates_path = metadata_dir / "stiatlas_duplicates.csv"
    
    # 1. Crawl website
    raw_records = crawl_manifest(metadata_dir)
    print(f"\nTotal raw records crawled: {len(raw_records)}")
    
    if not raw_records:
        print("No records retrieved. Exiting.")
        return

    # 2. Map and identify unique/duplicate/unverified records
    manifest_records = []
    duplicate_records = []
    unverified_records = []
    
    seen_urls = {} # maps url -> original record
    
    # Counter for verified IDs
    verified_idx = 1
    
    for r in raw_records:
        full_image_path = r["full_image_path"]
        if not full_image_path:
            continue
            
        # Standardize URL
        relative_path = full_image_path.replace("~/", "")
        asset_url = urljoin("https://stiatlas.org/", quote(relative_path))
        orig_filename = os.path.basename(relative_path)
        
        disease_class = map_to_class(r["stis"], r["other_conditions"])
        
        site_val = r["sites"] if r["sites"] != "-----" else "NA"
        record_data = {
            "image_id": "NA",
            "source": "STIAtlas",
            "disease_class": disease_class if disease_class else "unverified",
            "source_page_url": f"https://stiatlas.org/SearchAtlas.aspx?pageidx={r['page_num']}",
            "image_asset_url": asset_url,
            "anatomical_site": site_val,
            "site_group": get_site_group(site_val),
            "review_status": "NA",
            "patient_gender": r["sex"] if r["sex"] != "-----" else "NA",
            "description": r["description"] if r["description"] != "-----" else "NA",
            "original_filename": orig_filename,
            "local_filename": "NA",
            "sha256": "NA",
            "file_extension": "NA",
            "file_size": "NA",
            "collection_status": "pending",
            "download_status": "pending",
            "download_timestamp": "NA",
            "raw_stis": r["stis"],
            "raw_other_conditions": r["other_conditions"],
            "title": r["title"]
        }
        
        # Deduplication check
        if asset_url in seen_urls:
            # Duplicate
            reason = "Duplicate Image URL"
            dup_info = {
                "duplicate_image": orig_filename,
                "duplicate_reason": reason,
                "urls_tags": f"Page {r['page_num']} ({r['stis']} / {r['other_conditions']})",
                "retained_record": seen_urls[asset_url]["original_filename"]
            }
            duplicate_records.append(dup_info)
        else:
            seen_urls[asset_url] = record_data
            if disease_class:
                # Verified record
                img_id = f"STIATLAS_{verified_idx:03d}"
                record_data["image_id"] = img_id
                
                # Manual review statuses
                if img_id in ["STIATLAS_039", "STIATLAS_133"]:
                    record_data["review_status"] = "microscopy_non_lesion"
                elif img_id in ["STIATLAS_114", "STIATLAS_263"]:
                    record_data["review_status"] = "unresolved_anatomical_site"
                else:
                    record_data["review_status"] = "verified_lesion"
                    
                verified_idx += 1
                manifest_records.append(record_data)
            else:
                # Unverified record
                unverified_records.append(record_data)

    # Save Manifest CSV
    # Manifest includes both verified and unverified unique records, but let's separate or keep them clearly labeled
    # The instructions say: "Only accept records belonging to these six classes... If a record cannot be mapped, place it in an unverified report/section instead of silently including it."
    # Let's write the manifest with all unique records but clearly marking verified vs unverified, and write unverified to a separate list or keep them labeled in the status.
    # To follow exactly: "Only accept records belonging to these six classes... place in unverified report instead of silently including it."
    # Let's save the main manifest with the verified records, and write unverified records to a separate file: stiatlas_unverified.csv.
    unverified_path = metadata_dir / "stiatlas_unverified.csv"
    
    # Save Verified Manifest
    headers = [
        "image_id", "source", "disease_class", "source_page_url", "image_asset_url", 
        "anatomical_site", "site_group", "review_status", "patient_gender", "description", "original_filename",
        "local_filename", "sha256", "file_extension", "file_size", 
        "collection_status", "download_timestamp", "raw_stis", "raw_other_conditions"
    ]
    
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in manifest_records:
            writer.writerow(r)
            
    # Save Unverified report
    with open(unverified_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in unverified_records:
            writer.writerow(r)

    # Save Duplicates report
    dup_headers = ["duplicate_image", "duplicate_reason", "urls_tags", "retained_record"]
    with open(duplicates_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dup_headers)
        writer.writeheader()
        for d in duplicate_records:
            writer.writerow(d)

    # Class distribution
    class_counts = collections.Counter(r["disease_class"] for r in manifest_records)
    
    print("\n==========================================")
    print("CRAWL AND DISCOVERY COMPLETE")
    print("==========================================")
    print(f"Target total: 597")
    print("\nDetected:")
    for cls in TARGET_CLASSES:
        print(f"  {cls}: {class_counts[cls]}")
    print(f"\nUnique images: {len(manifest_records)}")
    print(f"Duplicate records: {len(duplicate_records)}")
    print(f"Unverified records: {len(unverified_records)}")
    print(f"Missing metadata (e.g. description missing): {sum(1 for r in manifest_records if r['description'] == 'NA')}")
    print("==========================================\n")
    
    print(f"Created manifest: {manifest_path}")
    print(f"Created duplicates report: {duplicates_path}")
    print(f"Created unverified report: {unverified_path}")

def download_images():
    """
    Downloads only the verified target records and performs validation (Step 6-8).
    """
    project_root = Path("d:/STI_Project")
    stiatlas_dir = project_root / "01_STIAtlas"
    metadata_dir = stiatlas_dir / "metadata"
    raw_dir = stiatlas_dir / "raw"
    
    manifest_path = metadata_dir / "stiatlas_manifest.csv"
    download_report_path = metadata_dir / "stiatlas_download_report.csv"
    
    if not manifest_path.exists():
        print(f"Error: Manifest file {manifest_path} does not exist. Run in discovery mode first.")
        return
        
    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
            
    print(f"Loaded {len(records)} verified records from manifest.")
    
    download_report_records = []
    download_failures_records = []
    download_failures_path = metadata_dir / "stiatlas_download_failures.csv"
    downloaded_hashes = set()
    
    # Download loop
    for idx, r in enumerate(records):
        url = r["image_asset_url"]
        orig_filename = r["original_filename"]
        
        # Safeguard file extension
        ext = os.path.splitext(orig_filename)[1].lower()
        if not ext:
            ext = ".jpg"
            
        # Create safe unique filename to avoid collisions (e.g., STIATLAS_001.jpg)
        local_name = f"{r['image_id']}{ext}"
        local_path = raw_dir / local_name
        
        print(f"[{idx+1}/{len(records)}] Downloading {orig_filename} as {local_name}...")
        
        # Polite download rate: 1 second delay
        time.sleep(1.0)
        
        download_status = "failed"
        sha256_hash = "NA"
        file_size = "NA"
        timestamp = "NA"
        validation_notes = ""
        
        try:
            r_get = requests.get(url, headers=HEADERS, timeout=20)
            if r_get.status_code == 200:
                # Write original unmodified content
                with open(local_path, "wb") as f_img:
                    f_img.write(r_get.content)
                
                # Check file size
                file_size = len(r_get.content)
                timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                
                # Calculate SHA-256
                sha256_hash = hashlib.sha256(r_get.content).hexdigest()
                
                # Validation
                is_valid = True
                if file_size == 0:
                    is_valid = False
                    validation_notes = "Zero bytes file"
                else:
                    try:
                        # Attempt to open and verify image with PIL
                        img_buf = io.BytesIO(r_get.content)
                        with Image.open(img_buf) as img:
                            img.verify()
                        is_valid = True
                    except Exception as img_err:
                        is_valid = False
                        validation_notes = f"Corrupted or invalid image: {str(img_err)}"
                
                if is_valid:
                    if sha256_hash in downloaded_hashes:
                        is_valid = False
                        validation_notes = "Duplicate image file hash detected"
                        download_status = "failed_validation"
                    else:
                        downloaded_hashes.add(sha256_hash)
                        download_status = "success"
                else:
                    download_status = "failed_validation"
            else:
                validation_notes = f"HTTP Status {r_get.status_code}"
        except Exception as e:
            validation_notes = f"Exception: {str(e)}"
            print(f"Error downloading {orig_filename}: {e}")
            
        # Update manifest fields
        r["local_filename"] = f"01_STIAtlas/raw/{local_name}" if download_status == "success" else "NA"
        r["sha256"] = sha256_hash
        r["file_extension"] = ext
        r["file_size"] = str(file_size)
        r["collection_status"] = "collected" if download_status == "success" else "failed"
        r["download_timestamp"] = timestamp
        
        # Download report row
        report_row = {
            "image_id": r["image_id"],
            "disease_class": r["disease_class"],
            "image_asset_url": url,
            "original_filename": orig_filename,
            "local_filename": local_name if download_status == "success" else "NA",
            "file_exists": "True" if local_path.exists() and download_status == "success" else "False",
            "file_size_valid": "True" if file_size != "NA" and file_size > 0 else "False",
            "extension_valid": "True" if ext in [".jpg", ".jpeg", ".png"] else "False",
            "sha256": sha256_hash,
            "download_status": download_status,
            "validation_notes": validation_notes if validation_notes else "Passed"
        }
        download_report_records.append(report_row)
        
        if download_status != "success":
            failure_row = {
                "image_id": r["image_id"],
                "disease_class": r["disease_class"],
                "source_page_url": r["source_page_url"],
                "image_asset_url": url,
                "failure_reason": validation_notes if validation_notes else "Failed validation",
                "attempted_status": download_status
            }
            download_failures_records.append(failure_row)

    # Save Updated Manifest
    headers = [
        "image_id", "source", "disease_class", "source_page_url", "image_asset_url", 
        "anatomical_site", "site_group", "review_status", "patient_gender", "description", "original_filename",
        "local_filename", "sha256", "file_extension", "file_size", 
        "collection_status", "download_timestamp", "raw_stis", "raw_other_conditions"
    ]
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)
            
    # Save Download Report
    report_headers = [
        "image_id", "disease_class", "image_asset_url", "original_filename",
        "local_filename", "file_exists", "file_size_valid", "extension_valid",
        "sha256", "download_status", "validation_notes"
    ]
    with open(download_report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=report_headers)
        writer.writeheader()
        for r in download_report_records:
            writer.writerow(r)
            
    # Save Download Failures Report
    failure_headers = ["image_id", "disease_class", "source_page_url", "image_asset_url", "failure_reason", "attempted_status"]
    with open(download_failures_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=failure_headers)
        writer.writeheader()
        for f_rec in download_failures_records:
            writer.writerow(f_rec)
            
    # Count stats
    total_manifest = len(records)
    successful = sum(1 for row in download_report_records if row["download_status"] == "success")
    failed = len(download_failures_records)
    corrupted = sum(1 for row in download_report_records if "Corrupted" in row["validation_notes"])
    duplicate_hashes = sum(1 for row in download_report_records if "Duplicate" in row["validation_notes"])
    missing_desc = sum(1 for r in records if r["description"] == "NA")
    
    # Class counts actually downloaded
    downloaded_classes = [row["disease_class"] for row in download_report_records if row["download_status"] == "success"]
    class_counts = collections.Counter(downloaded_classes)
    
    print("\n==========================================")
    print("DOWNLOAD AND VALIDATION COMPLETE")
    print("==========================================")
    print(f"Total verified manifest records: {total_manifest}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed downloads: {failed}")
    print(f"Unreadable/corrupted files: {corrupted}")
    print(f"Duplicate hashes: {duplicate_hashes}")
    print(f"Missing metadata (e.g. description missing): {missing_desc}")
    print("\nClass counts actually downloaded:")
    for cls in TARGET_CLASSES:
        print(f"  {cls}: {class_counts[cls]}")
    print("==========================================\n")
            
    print(f"Download process complete.")
    print(f"Updated manifest: {manifest_path}")
    print(f"Created download report: {download_report_path}")
    print(f"Created download failures report: {download_failures_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="STIAtlas Dataset Collection Pipeline")
    parser.add_argument("--download", action="store_true", help="Download images in manifest")
    args = parser.parse_args()
    
    if args.download:
        download_images()
    else:
        process_pipeline()
