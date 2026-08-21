#!/usr/bin/env python3
"""
ATCC Product Information Scraper (Comprehensive Version)
Scrapes product information for ATCC bacteria strains and populates 200_Bug_Project_Populated_Comp.csv

Features:
- Reads input CSV ('200 Bug Project(FB).csv') using organism name & ATCC number resolution (same as atcc_scraper.py).
- Formats shared columns (Strain name, Medium, Temp, Atmosphere, BSL, SDS API, ATCC Link) identically to 200_Bug_Project_Populated.csv.
- Converts long GenBank accession text into clean NCBI Direct Accession Links.
- Extracts 37 comprehensive columns per bacteria strain from ATCC web pages.
- Caches scraped HTML pages in 'cache/' directory to optimize performance.
- Strictly defaults missing ATCC values to "Unknown" (NEVER defaulting to 37°C, Aerobic, or BSL-1).
"""

import csv
import ssl
import sys
import os
import re
import time
import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Input & Output File Paths
INPUT_CSV = "200 Bug Project(FB).csv"
OUTPUT_CSV = "200_Bug_Project_Populated_Comp.csv"
CACHE_DIR = "cache"
BASE_URL = "https://www.atcc.org/products/"

# 37 Comprehensive Columns Schema
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
    "pa 10^4": "27853",
    "pa 104": "27853",
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
    "abiotrophia defectiva": "49176",
    "acinetobacter iwoffii": "15309",
    "acinetobacter lwoffii": "15309",
    "actinomyces gerencseriae": "27037",
    "acinetobacter pittii": "19004",
    "acinetobacter ursingii": "BAA-617",
    "actinomyces neuii": "700050",
    "acinetobacter calcoaceticus": "23055",
    "actinomyces israelii": "12102"
}

def ensure_directories():
    os.makedirs(CACHE_DIR, exist_ok=True)

def get_ssl_context():
    """Creates SSL context compatible with macOS CA certificates."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def extract_numeric_id(atcc_str):
    """Parses raw numeric ID from strings like 'ATCC 14025' or 'ATCC BAA-617'. Returns None for 'NBF'."""
    if not atcc_str or str(atcc_str).strip().upper() in ["NBF", "N/A", "NONE", "", "BLANK FB", "PA 10^4"]:
        return None
    match = re.search(r'BAA[-\s]*\d+', str(atcc_str), re.I)
    if match:
        return re.sub(r'\s+', '', match.group(0).upper())
    match = re.search(r'\d+', str(atcc_str))
    return match.group(0) if match else None

def resolve_organism_atcc_number(organism_name, specified_atcc=None):
    """Resolves target ATCC number from explicit catalog string or organism name lookup."""
    specified_num = extract_numeric_id(specified_atcc)
    if specified_num:
        return specified_num

    if not organism_name:
        return None

    clean_name = str(organism_name).strip().lower()
    if clean_name in ["unknown", "#2", "", "nbf", "blank fb"]:
        return None

    # 1. Exact match in map
    if clean_name in ORGANISM_PRIMARY_REF_MAP:
        return ORGANISM_PRIMARY_REF_MAP[clean_name]

    # 2. Substring match sorted by key length descending
    for key in sorted(ORGANISM_PRIMARY_REF_MAP.keys(), key=len, reverse=True):
        if key in clean_name or clean_name in key:
            return ORGANISM_PRIMARY_REF_MAP[key]

    return None

def clean_species_name(h1_title, raw_input_name):
    """Cleans organism species name to standard binomial format (e.g. Enterococcus avium)."""
    if raw_input_name and raw_input_name.strip():
        name = raw_input_name.strip()
        if name.lower() not in ['nbf', 'unknown', 'none', 'blank fb', ''] and not name.upper().startswith('ATCC'):
            return name

    if not h1_title or h1_title == 'Unknown':
        return 'Unknown'

    # Extract clean genus species from ATCC H1 title
    name = h1_title.split('(')[0].strip()
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name) # Separate camelCase concatenation
    name = re.sub(r'\s*subsp\..*', '', name, flags=re.I)
    name = re.sub(r'\s+(Collins|Castellani|Goodfellow|Abe|Rosenbach|Migula|Kawamura|Bouvet|Nemec|et al\.).*', '', name, flags=re.I)
    return name.strip()

def format_genbank_accession_links(cross_refs_text):
    """Converts raw GenBank cross-reference string into clean NCBI Direct Accession URLs."""
    if not cross_refs_text or cross_refs_text == "Unknown":
        return "Unknown"
    
    accessions = re.findall(r'GenBank([A-Z]{1,3}\d{5,6})', cross_refs_text)
    if not accessions:
        return cross_refs_text

    unique_accs = list(dict.fromkeys(accessions))
    ncbi_urls = [f"https://www.ncbi.nlm.nih.gov/nuccore/{acc}" for acc in unique_accs]
    return " ; ".join(ncbi_urls)

def fetch_atcc_page(atcc_number):
    """Fetches HTML from ATCC website with local disk caching and macOS SSL context."""
    if not atcc_number:
        return atcc_number, None
        
    ensure_directories()
    cache_path = os.path.join(CACHE_DIR, f"{atcc_number}.html")
    
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8", errors="replace") as f:
            return atcc_number, f.read()

    url = f"{BASE_URL}{atcc_number}"
    print(f"Fetching ATCC {atcc_number} ({url})...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = get_ssl_context()
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
            html = response.read().decode('utf-8', errors='replace')
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            return atcc_number, html
    except Exception as e:
        print(f"  Warning: Failed to fetch ATCC {atcc_number}: {e}")
        return atcc_number, None

def parse_atcc_html(html, atcc_number, raw_input_name=""):
    """
    Parses ATCC product HTML and returns extracted details.
    Missing fields strictly default to 'Unknown' (never defaulting to 37°C, Aerobic, or BSL-1).
    """
    data = {col: "Unknown" for col in COLUMNS}
    
    if not html:
        data["Strain (Genus, species)"] = clean_species_name("", raw_input_name)
        return data

    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Page Title / Organism Name
    h1 = soup.find('h1')
    h1_title = h1.get_text(strip=True) if h1 else "Unknown"
    data["Strain (Genus, species)"] = clean_species_name(h1_title, raw_input_name)
    
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
    data["ATCC Number"] = f"ATCC {atcc_number}" if atcc_number else "Unknown"
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
    
    # Convert GenBank text block into direct NCBI links
    data["GenBank Accession"] = format_genbank_accession_links(get_val("Cross references"))
    
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

def process_csv(input_path=INPUT_CSV, output_path=OUTPUT_CSV):
    """Reads input CSV ('100 Bug Project(FB).csv'), scrapes ATCC details, and writes 100_Bug_Project_Populated_Comp.csv."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Reading input CSV: '{input_path}'...")
    with open(input_path, 'r', encoding='utf-8-sig', errors='replace') as infile:
        reader = csv.DictReader(infile)
        fieldnames = [f.strip() for f in (reader.fieldnames or []) if f]
        raw_rows = list(reader)
        
    if not raw_rows:
        print("Error: Input CSV is empty.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Processing {len(raw_rows)} data rows from '{input_path}'...")
    
    # Identify key columns flexibly
    name_col = next((f for f in fieldnames if "strain" in f.lower() or "genus" in f.lower() or "name" in f.lower()), fieldnames[0])
    atcc_col = next((f for f in fieldnames if "source" in f.lower() or "atcc" in f.lower() or "number" in f.lower()), None)
    nbf_folder_col = next((f for f in fieldnames if "folder" in f.lower()), None)
    nbf_file_col = next((f for f in fieldnames if "file" in f.lower()), None)
    start_col = next((f for f in fieldnames if "start" in f.lower()), None)
    end_col = next((f for f in fieldnames if "end" in f.lower()), None)
    notes_col = next((f for f in fieldnames if "note" in f.lower()), None)
    
    # Resolve target ATCC numbers for every row
    row_target_nums = []
    unique_atccs = set()
    for row in raw_rows:
        org_source = row.get(atcc_col, "").strip() if atcc_col else ""
        strain_name = row.get(name_col, "").strip() if name_col else ""
        
        target_num = resolve_organism_atcc_number(strain_name, org_source)
        row_target_nums.append(target_num)
        if target_num:
            unique_atccs.add(target_num)
            
    print(f"Found {len(unique_atccs)} unique reference ATCC strains. Scraping pages concurrently...")
    
    # Scrape unique ATCC pages concurrently with local caching
    cache = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_atcc = {executor.submit(fetch_atcc_page, atcc_num): atcc_num for atcc_num in unique_atccs}
        for future in as_completed(future_to_atcc):
            atcc_num, html = future.result()
            cache[atcc_num] = html

    print("Parsing ATCC page details and assembling populated rows...")
    populated_rows = []
    
    for idx, row in enumerate(raw_rows):
        org_source = row.get(atcc_col, "").strip() if atcc_col else "Unknown"
        strain_name = row.get(name_col, "").strip() if name_col else "Unknown"
        nbf_folder = row.get(nbf_folder_col, "").strip() if nbf_folder_col else "Unknown"
        nbf_filename = row.get(nbf_file_col, "").strip() if nbf_file_col else "Unknown"
        start_time = row.get(start_col, "").strip() if start_col else "Unknown"
        end_time = row.get(end_col, "").strip() if end_col else "Unknown"
        notes = row.get(notes_col, "").strip() if notes_col else "Unknown"
        
        # Get positional well ID if present
        well_id = "Unknown"
        for k, v in row.items():
            if k and ("well" in k.lower() or "position" in k.lower() or k.strip() == "") and v and v.strip():
                well_id = v.strip()
                break
        
        target_atcc_num = row_target_nums[idx]
        
        if target_atcc_num and target_atcc_num in cache:
            html = cache[target_atcc_num]
            atcc_data = parse_atcc_html(html, target_atcc_num, strain_name)
        else:
            atcc_data = {col: "Unknown" for col in COLUMNS}
            atcc_data["ATCC Number"] = "Unknown"
            
        # Merge input row values with ATCC scraped data
        row_dict = {col: "Unknown" for col in COLUMNS}
        row_dict.update(atcc_data)
        
        row_dict["Organism Source"] = org_source if org_source else (f"ATCC {target_atcc_num}" if target_atcc_num else "Unknown")
        row_dict["Strain (Genus, species)"] = clean_species_name(row_dict.get("Strain (Genus, species)"), strain_name)
            
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
    parser = argparse.ArgumentParser(description="ATCC Scraper (Comprehensive 37-Column CSV Generator)")
    parser.add_argument("--input", default=INPUT_CSV, help="Path to input CSV")
    parser.add_argument("--output", default=OUTPUT_CSV, help="Path to output CSV")
    args = parser.parse_args()

    process_csv(args.input, args.output)

if __name__ == "__main__":
    main()
