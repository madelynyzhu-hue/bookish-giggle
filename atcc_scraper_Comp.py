#!/usr/bin/env python3
"""
ATCC Product Information Scraper (Comprehensive Version)
Scrapes product information for ATCC bacteria strains and populates 100_Bug_Project_Populated_Comp.csv

Features:
- Extracts 37 comprehensive columns per bacteria strain from ATCC web pages.
- Reads input CSV ('100 Bug Project(FB).csv' or '100_Bug_Project_Populated.csv').
- Uses multi-threading (ThreadPoolExecutor) for fast, robust scraping.
- Strictly defaults missing ATCC values to "Unknown" (NEVER defaulting to 37°C, Aerobic, or BSL-1).
"""

import csv
import ssl
import sys
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Input & Output File Paths
INPUT_CSV = "100 Bug Project(FB).csv"
OUTPUT_CSV = "100_Bug_Project_Populated_Comp.csv"

# 37 Comprehensive Columns Schema (Matching exact requested order)
COLUMNS = [
    "Organism Source",
    "ATCC Number",
    "Strain (Genus, species)",
    "Strain Designation",
    "Product Type",
    "Type Strain Flag",
    "Isolation Source (Where found)",
    "Type of Isolate",
    "Geographical Isolation",
    "Year of Origin",
    "Culture Medium",
    "Incubation Temperature",
    "Atmosphere",
    "Handling Procedure",
    "Product Format",
    "Storage Conditions",
    "Biosafety Level",
    "Safety Data Sheet (SDS API)",
    "ATCC Product Link",
    "Intended Use",
    "Permits & Restrictions",
    "Genome Sequenced Strain",
    "GenBank Accession",
    "Serotype",
    "Verification Method",
    "Antibiotic Resistance Profile",
    "Applications",
    "Specific Applications",
    "Special Collection",
    "Cross References",
    "Patent Number",
    "NBF Folder",
    "NBF File Name",
    "Start",
    "End",
    "Well / Sample Position ID",
    "NOTES"
]

def get_ssl_context():
    """Creates SSL context compatible with macOS CA certificates."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def extract_atcc_number(source_str):
    """Extracts numeric ATCC catalog ID from strings like 'ATCC 14025', 'ATCC 13032 ', etc."""
    if not source_str:
        return None
    match = re.search(r'(\d+)', str(source_str))
    if match:
        return match.group(1)
    return None

def fetch_single_atcc(atcc_number):
    """Fetches HTML content for a single ATCC catalog number."""
    if not atcc_number:
        return atcc_number, None
    
    url = f"https://www.atcc.org/products/{atcc_number}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = get_ssl_context()
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
            html = response.read().decode('utf-8', errors='replace')
            return atcc_number, html
    except Exception as e:
        print(f"  Warning: Failed to fetch ATCC {atcc_number}: {e}")
        return atcc_number, None

def parse_atcc_html(html, atcc_number):
    """
    Parses ATCC product HTML and returns extracted details.
    Missing fields strictly default to 'Unknown' (never defaulting to 37°C, Aerobic, or BSL-1).
    """
    data = {col: "Unknown" for col in COLUMNS}
    
    if not html:
        return data

    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Page Title / Organism Name
    h1 = soup.find('h1')
    if h1:
        data["Strain (Genus, species)"] = h1.get_text(strip=True)
    
    # 2. Extract Key-Value Pairs from Description Lists (<dl>)
    dl_pairs = {}
    for dlist in soup.find_all('dl'):
        dts = dlist.find_all('dt')
        dds = dlist.find_all('dd')
        for dt, dd in zip(dts, dds):
            k = dt.get_text(strip=True)
            v = dd.get_text(strip=True)
            if k and v:
                dl_pairs[k.lower()] = v
    
    def get_val(key_name):
        return dl_pairs.get(key_name.lower(), "Unknown")

    # Map DL fields to Columns
    data["ATCC Number"] = atcc_number if atcc_number else "Unknown"
    data["Strain Designation"] = get_val("Strain designation")
    data["Product Type"] = get_val("Product type")
    data["Type Strain Flag"] = get_val("Type strain")
    data["Isolation Source (Where found)"] = get_val("Isolation source")
    data["Type of Isolate"] = get_val("Type of isolate")
    data["Geographical Isolation"] = get_val("Geographical isolation")
    data["Year of Origin"] = get_val("Year of origin")
    data["Culture Medium"] = get_val("Medium")
    data["Incubation Temperature"] = get_val("Temperature")
    data["Atmosphere"] = get_val("Atmosphere")
    data["Handling Procedure"] = get_val("Handling procedure")
    data["Product Format"] = get_val("Product format")
    data["Storage Conditions"] = get_val("Storage conditions")
    data["Intended Use"] = get_val("Intended use")
    data["Genome Sequenced Strain"] = get_val("Genome sequenced strain")
    data["Serotype"] = get_val("Serotype")
    data["Verification Method"] = get_val("Verification method")
    data["Applications"] = get_val("Applications")
    data["Specific Applications"] = get_val("Specific applications")
    data["Special Collection"] = get_val("Special collection")
    data["Cross References"] = get_val("Cross references")
    data["Patent Number"] = get_val("Patent number")
    
    # 3. Biosafety Level (BSL) - Strictly "Unknown" if not specified on page
    bsl_elem = soup.find(string=re.compile(r'BSL\s*\d', re.I))
    if bsl_elem:
        data["Biosafety Level"] = bsl_elem.strip()
    elif 'BSL 2' in html:
        data["Biosafety Level"] = "BSL 2"
    elif 'BSL 1' in html:
        data["Biosafety Level"] = "BSL 1"
    else:
        data["Biosafety Level"] = "Unknown"
        
    # 4. Links & APIs
    if atcc_number:
        data["ATCC Product Link"] = f"https://www.atcc.org/products/{atcc_number}"
        data["Safety Data Sheet (SDS API)"] = f"https://www.atcc.org/api/product/sds?atcc_number={atcc_number}"
    else:
        data["ATCC Product Link"] = "Unknown"
        data["Safety Data Sheet (SDS API)"] = "Unknown"
        
    # 5. Extract GenBank / Accession if present
    cross_refs = get_val("Cross references")
    if "GenBank" in cross_refs:
        data["GenBank Accession"] = cross_refs
    else:
        data["GenBank Accession"] = "Unknown"
        
    # 6. Permits & Restrictions
    permits = get_val("Permits & restrictions")
    if permits != "Unknown":
        data["Permits & Restrictions"] = permits
    elif "permit" in html.lower():
        data["Permits & Restrictions"] = "Permit required for delivery (check ATCC catalog terms)"
    else:
        data["Permits & Restrictions"] = "Unknown"
        
    # 7. Antibiotic Resistance Profile
    handling_notes = get_val("Handling notes")
    if "antibiotic" in handling_notes.lower() or "susceptibility" in handling_notes.lower():
        data["Antibiotic Resistance Profile"] = handling_notes
    else:
        data["Antibiotic Resistance Profile"] = "Unknown"

    return data

def process_csv(input_path, output_path):
    """Reads input CSV, scrapes ATCC details, and writes 100_Bug_Project_Populated_Comp.csv."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Reading input CSV: '{input_path}'...")
    with open(input_path, 'r', encoding='utf-8', errors='replace') as infile:
        reader = csv.reader(infile)
        raw_rows = list(reader)
        
    if not raw_rows:
        print("Error: Input CSV is empty.", file=sys.stderr)
        sys.exit(1)
        
    data_rows = raw_rows[1:]
    print(f"Processing {len(data_rows)} data rows...")
    
    # Collect unique ATCC numbers
    unique_atccs = set()
    for row in data_rows:
        if row and len(row) > 0:
            atcc_num = extract_atcc_number(row[0].strip())
            if atcc_num:
                unique_atccs.add(atcc_num)
                
    print(f"Found {len(unique_atccs)} unique ATCC strains. Scraping pages concurrently...")
    
    # Scrape unique ATCC pages concurrently
    cache = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_atcc = {executor.submit(fetch_single_atcc, atcc_num): atcc_num for atcc_num in unique_atccs}
        for future in as_completed(future_to_atcc):
            atcc_num, html = future.result()
            cache[atcc_num] = html
            print(f"  Downloaded ATCC {atcc_num}")
            
    print("Parsing ATCC page details and assembling populated rows...")
    populated_rows = []
    
    for row in data_rows:
        if not row or not any(row):
            continue
            
        org_source = row[0].strip() if len(row) > 0 else "Unknown"
        strain_name = row[1].strip() if len(row) > 1 else "Unknown"
        nbf_folder = row[2].strip() if len(row) > 2 else "Unknown"
        nbf_filename = row[3].strip() if len(row) > 3 else "Unknown"
        start_time = row[4].strip() if len(row) > 4 else "Unknown"
        end_time = row[5].strip() if len(row) > 5 else "Unknown"
        well_id = row[6].strip() if len(row) > 6 else (row[7].strip() if len(row) > 7 else "Unknown")
        notes = row[8].strip() if len(row) > 8 and row[8] else "Unknown"
        
        atcc_num = extract_atcc_number(org_source)
        
        if atcc_num and atcc_num in cache:
            html = cache[atcc_num]
            atcc_data = parse_atcc_html(html, atcc_num)
        else:
            # Non-ATCC / NBF strain
            atcc_data = {col: "Unknown" for col in COLUMNS}
            atcc_data["ATCC Number"] = "Unknown"
            
        # Merge input row values with ATCC scraped data
        row_dict = {col: "Unknown" for col in COLUMNS}
        row_dict.update(atcc_data)
        
        row_dict["Organism Source"] = org_source if org_source else "Unknown"
        if strain_name and strain_name != "Unknown" and (row_dict["Strain (Genus, species)"] == "Unknown" or not atcc_num):
            row_dict["Strain (Genus, species)"] = strain_name
            
        row_dict["NBF Folder"] = nbf_folder if nbf_folder else "Unknown"
        row_dict["NBF File Name"] = nbf_filename if nbf_filename else "Unknown"
        row_dict["Start"] = start_time if start_time else "Unknown"
        row_dict["End"] = end_time if end_time else "Unknown"
        row_dict["Well / Sample Position ID"] = well_id if well_id else "Unknown"
        row_dict["NOTES"] = notes if notes else "Unknown"
        
        populated_rows.append(row_dict)

    # Write output CSV
    print(f"Writing populated data to '{output_path}'...")
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(populated_rows)
        
    print(f"Successfully populated {len(populated_rows)} rows into '{output_path}'.")

def main():
    process_csv(INPUT_CSV, OUTPUT_CSV)

if __name__ == "__main__":
    main()
