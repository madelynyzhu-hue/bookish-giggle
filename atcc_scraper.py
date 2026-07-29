#!/usr/bin/env python3
"""
ATCC Primary Name-Lookup Scraper with ATCC Number Verification & NBF Fallback
1. Reads the input CSV file "100 Bug Project(FB).csv".
2. Looks up organism names and ATCC numbers (resolving 'NBF' entries to reference strains).
3. Fetches and parses biological metadata from ATCC.org.
4. Generates a NEW populated CSV file ("100_Bug_Project_Populated.csv") WITHOUT modifying the input CSV file!
"""

import urllib.request
import ssl
import re
import sys
import os
import csv
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

INPUT_CSV = "100 Bug Project(FB).csv"
OUTPUT_CSV = "100_Bug_Project_Populated.csv"
DATA_DIR_CSV = "data/100_Bug_Project_Populated.csv"
BASE_URL = "https://www.atcc.org/products/"
DEFAULT_CACHE_DIR = "cache"

# Comprehensive Organism Name -> Primary ATCC Reference Strain Map (with typo handling)
ORGANISM_PRIMARY_REF_MAP = {
    "enterococcus avium": "14025",
    "alcaligenes faecalis": "8750",
    "rhodococcus equi": "6939",
    "corynebacterium glutamicum": "13032",
    "staphylococcus aureus": "25923",
    "staphylococcus aureus 10/2": "25923",
    "staphylococcus aureus sub sp. aureus": "29213",
    "kleisiella pneuminoa": "13883",
    "klebsiella pneumoniae": "13883",
    "klebsiella pneumoniae, subsp. pneumoniae": "13883",
    "enteroccus faecium": "19434",
    "enterococcus faecium": "19434",
    "enterobacter spp": "13047",
    "enterobacter cloacae": "13047",
    "kingella kingae": "23330",
    "proteus vulgaris": "6380",
    "morganella morganii": "25830",
    "morganella morganii subsp. morganii": "25830",
    "moraxella catarrhalis": "25238",
    "chromobacterium violaceum": "12472",
    "staphylococcus saprophyticus": "49453",
    "staphylococcus saprophylicus": "49453",
    "staphylococcus simulans": "27848",
    "staphylococcus auricularis": "33753",
    "staphylococcus schleiferi": "49545",
    "staphylococcus epidermidis": "12228",
    "pseudomonas aeruginosa": "27853",
    "streptococcus salivarius": "13419",
    "streptococcus salivarius subsp. salivaris": "13419",
    "staphylococcus haemolyticus": "29970",
    "staphylococcus lugdunensis": "49576",
    "acinetobatcor baumiini": "19606",
    "acinetobacter baumannii": "19606",
    "gram negative cocci": "19424",
    "staphylococcus capitis": "27840",
    "escherichia coli": "25922",
    "streptococcus mitis": "49456",
    "streptococcus mitis/oralis": "49456",
    "streptococcus gordonii": "10558",
    "presum. acid fast bacilli": "607",
    "streptococcus mutans": "25175",
    "serratia marcescens": "13880",
    "serratia marcescens , subsp marcescens": "13880",
    "klebsiella oxytoca": "700324",
    "enterococcus faecalis": "19433",
    "klebsiella planticola": "700831",
    "raoultella planticola": "700831",
    "streptococcus pyogenes": "19615",
    "streptococcus agalactiae": "13813",
    "proteus mirabilis": "29906",
    "achromobacter xylosoxidans": "27061",
    "erysipelothrix rhusiopathiae": "19414",
    "streptococcus bovis": "33317",
    "corynebacterium jeikeium": "43734",
    "elizabethkingia meningoseptica": "13253",
    "abiotrophia defectiva": "49176"
}

def ensure_directories():
    os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

def extract_numeric_id(atcc_str):
    """Parses raw numeric ID from strings like 'ATCC 14025' or '14025'. Returns None for 'NBF'."""
    if not atcc_str or str(atcc_str).strip().upper() in ["NBF", "N/A", "NONE", ""]:
        return None
    match = re.search(r'\d+', str(atcc_str))
    return match.group(0) if match else None

def fetch_atcc_page(atcc_number, cache_dir=DEFAULT_CACHE_DIR):
    """Fetches HTML from ATCC website with local caching and macOS SSL context."""
    ensure_directories()
    cache_path = os.path.join(cache_dir, f"{atcc_number}.html")
    
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    url = f"{BASE_URL}{atcc_number}"
    print(f"[HTTP GET] Fetching ATCC {atcc_number} from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.4 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode('utf-8')
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            return html
    except Exception as e:
        print(f"[ERROR] Failed to fetch ATCC {atcc_number}: {e}", file=sys.stderr)
        return None

def parse_atcc_info(html, atcc_number):
    """Parses HTML to extract required biological metadata."""
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    title = f"ATCC {atcc_number}"
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)

    details = {}
    for dlist in soup.find_all('dl'):
        dts = dlist.find_all('dt')
        dds = dlist.find_all('dd')
        for dt, dd in zip(dts, dds):
            key = dt.get_text(strip=True)
            val = dd.get_text(strip=True)
            if key and val:
                details[key] = val

    def get_detail(target_key, default="N/A"):
        target_key_lower = target_key.lower()
        for k, v in details.items():
            if k.lower() == target_key_lower:
                return v
        return default

    bsl_level = "BSL 1"
    bsl_elem = soup.find(string=re.compile(r'BSL\s*\d', re.I))
    if bsl_elem:
        bsl_match = re.search(r'BSL\s*(\d)', bsl_elem, re.I)
        if bsl_match:
            bsl_level = f"BSL {bsl_match.group(1)}"
        else:
            bsl_level = bsl_elem.strip()
    elif 'BSL 2' in html:
        bsl_level = "BSL 2"

    organism_clean = title.split('(')[0].strip() if '(' in title else title

    return {
        "organism_name": organism_clean,
        "isolation_source": get_detail("Isolation source"),
        "culture_medium": get_detail("Medium"),
        "incubation_temperature": get_detail("Temperature", "37°C"),
        "atmosphere": get_detail("Atmosphere", "Aerobic"),
        "biosafety_level": bsl_level,
        "sds_api_url": f"https://www.atcc.org/api/product/sds?atcc_number={atcc_number}",
        "product_url": f"{BASE_URL}{atcc_number}"
    }

def resolve_organism_atcc_number(organism_name, specified_atcc=None):
    """Primary Name Lookup & Verification Strategy."""
    specified_num = extract_numeric_id(specified_atcc)
    if specified_num:
        return specified_num

    clean_name = organism_name.strip().lower()
    if clean_name in ["unknown", "#2", ""]:
        return None

    if clean_name in ORGANISM_PRIMARY_REF_MAP:
        return ORGANISM_PRIMARY_REF_MAP[clean_name]

    for key, atcc_id in ORGANISM_PRIMARY_REF_MAP.items():
        if key in clean_name or clean_name in key:
            return atcc_id

    return None

def process_100_bug_project(input_file=INPUT_CSV, output_file=OUTPUT_CSV):
    """Reads input CSV, resolves ATCC metadata, and writes to a NEW output CSV without modifying input CSV!"""
    if not os.path.exists(input_file):
        print(f"[ERROR] Input CSV file '{input_file}' not found.", file=sys.stderr)
        return False

    ensure_directories()

    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_headers = list(reader.fieldnames) if reader.fieldnames else []
        headers = [h.strip() for h in raw_headers if h and h.strip()]
        rows = list(reader)

    # Clean rows to only include valid headers
    cleaned_rows = []
    for r in rows:
        clean_r = {k: v for k, v in r.items() if k and k.strip() in headers}
        cleaned_rows.append(clean_r)
    rows = cleaned_rows

    if not headers:
        print("[ERROR] Input CSV file has no headers.", file=sys.stderr)
        return False

    target_columns = [
        "Isolation Source (Where found)",
        "Culture Medium",
        "Incubation Temperature",
        "Atmosphere",
        "Biosafety Level",
        "Safety Data Sheet (SDS API)",
        "ATCC Product Link"
    ]

    for col in target_columns:
        if col not in headers:
            headers.append(col)

    name_col = next((h for h in headers if "name" in h.lower() or "organism" in h.lower()), headers[0])
    atcc_col = next((h for h in headers if "atcc" in h.lower() or "number" in h.lower() or "id" in h.lower()), None)

    print(f"[INFO] Reading '{input_file}' ({len(rows)} entries)...")

    # Resolve target ATCC numbers for every row
    row_target_nums = []
    unique_atcc_nums = set()

    for row in rows:
        org_name = row.get(name_col, "")
        specified_atcc = row.get(atcc_col, "") if atcc_col else None
        target_num = resolve_organism_atcc_number(org_name, specified_atcc)
        row_target_nums.append(target_num)
        if target_num:
            unique_atcc_nums.add(target_num)

    unique_atccs = list(unique_atcc_nums)
    print(f"[INFO] Fetching ATCC pages for {len(unique_atccs)} reference catalog strains in parallel...")

    # Parallel HTTP fetch
    html_cache = {}
    if unique_atccs:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_atcc_page, num): num for num in unique_atccs}
            for future in as_completed(futures):
                num = futures[future]
                try:
                    html_cache[num] = future.result()
                except Exception as e:
                    print(f"[ERROR] Failed fetching ATCC {num}: {e}")

    # Parse metadata
    parsed_records = {}
    for num, html in html_cache.items():
        if html:
            parsed_records[num] = parse_atcc_info(html, num)

    # Build new output rows
    populated_rows = []
    for idx, row in enumerate(rows):
        new_row = dict(row)
        target_num = row_target_nums[idx]
        rec = parsed_records.get(target_num) if target_num else None

        if rec:
            new_row["Isolation Source (Where found)"] = rec["isolation_source"]
            new_row["Culture Medium"] = rec["culture_medium"]
            new_row["Incubation Temperature"] = rec["incubation_temperature"]
            new_row["Atmosphere"] = rec["atmosphere"]
            new_row["Biosafety Level"] = rec["biosafety_level"]
            new_row["Safety Data Sheet (SDS API)"] = rec["sds_api_url"]
            new_row["ATCC Product Link"] = rec["product_url"]
            if atcc_col and (not new_row[atcc_col] or new_row[atcc_col].strip().upper() == "NBF"):
                new_row[atcc_col] = f"ATCC {target_num}"
        else:
            new_row["Isolation Source (Where found)"] = "N/A"
            new_row["Culture Medium"] = "N/A"
            new_row["Incubation Temperature"] = "N/A"
            new_row["Atmosphere"] = "N/A"
            new_row["Biosafety Level"] = "N/A"
            new_row["Safety Data Sheet (SDS API)"] = "N/A"
            new_row["ATCC Product Link"] = "N/A"

        populated_rows.append(new_row)

    # Save to NEW output CSV files without modifying INPUT_CSV
    for path in [output_file, DATA_DIR_CSV]:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(populated_rows)
        print(f"[SUCCESS] Created NEW populated CSV spreadsheet -> {path}")

    return True

def main():
    parser = argparse.ArgumentParser(description="ATCC Scraper (Generates New Populated CSV)")
    parser.add_argument("--input", default=INPUT_CSV, help="Path to input CSV")
    parser.add_argument("--output", default=OUTPUT_CSV, help="Path to output CSV")
    args = parser.parse_args()

    process_100_bug_project(args.input, args.output)

if __name__ == "__main__":
    main()
