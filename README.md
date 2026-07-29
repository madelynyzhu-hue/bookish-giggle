# 🧬 ATCC Biological Data Scraper & Spreadsheet Generator (`bookish-giggle`)

An automated Python data extraction tool designed to parse product specifications, culture handling protocols, isolation source details, growth requirements, biosafety levels, and Safety Data Sheet (SDS) API links for biological cultures from the [ATCC (American Type Culture Collection)](https://www.atcc.org/) repository.

---

## 📋 Overview

This project provides a robust, parallel Python web scraper using `urllib` and `BeautifulSoup4` to parse ATCC product pages. It automatically extracts key microbiological parameters and safety information for a list of bacterial strains (such as `100 Bug Project(FB).csv`), generating a clean, non-destructive populated spreadsheet (`100_Bug_Project_Populated.csv`).

---

## ✨ Key Features

- **Primary Organism Name Lookup**: Looks up bacterial species names against ATCC reference strain catalog records.
- **ATCC Catalog Number Verification**: Verifies specified ATCC numbers (e.g. `ATCC 14025`, `ATCC 8750`, `ATCC 6939`) against catalog entries.
- **`NBF` Automatic Fallback**: Automatically resolves `NBF` ("Not Being Found") entries to their primary ATCC reference strains (e.g. *Staphylococcus aureus* $\rightarrow$ `ATCC 25923`, *Klebsiella pneumoniae* $\rightarrow$ `ATCC 13883`).
- **Non-Destructive File Processing**: Reads source input files (`100 Bug Project(FB).csv`) without modifying them, generating output spreadsheets (`100_Bug_Project_Populated.csv`).
- **Parallel HTTP Fetching & Caching**: Uses `ThreadPoolExecutor` and local disk caching (`cache/`) for instant re-runs and polite server throttling.
- **macOS SSL Compatibility**: Includes custom SSL context handling to resolve local CA certificate validation issues on macOS environments.

---

## 📊 Populated Metadata Columns

1. **Organism Name**: Full scientific binomial taxonomy.
2. **ATCC Number**: Formatted catalog identifier (`ATCC {number}`).
3. **Isolation Source (Where found)**: Host tissue, anatomical site, or environmental origin.
4. **Culture Medium**: Recommended ATCC growth medium formulation.
5. **Incubation Temperature**: Optimal growth temperature (°C).
6. **Atmosphere**: Gaseous requirement (Aerobic, Anaerobic, 5% CO2).
7. **Biosafety Level**: Biological containment rating (BSL-1, BSL-2).
8. **Safety Data Sheet (SDS API)**: Direct REST API link for Safety Data Sheets.
9. **ATCC Product Link**: Direct URL to the live ATCC catalog page.

---

## 🛠️ Requirements & Installation

### Prerequisites
- **Python**: Version `3.8` or higher installed.

### Dependencies
Install the required parsing library:
```bash
pip3 install beautifulsoup4
```

---

## 🚀 Usage Instructions

1. **Run Scraper on Source CSV (`100 Bug Project(FB).csv`)**:
   ```bash
   python3 atcc_scraper.py
   ```

2. **Run Scraper on Custom Input & Output Files**:
   ```bash
   python3 atcc_scraper.py --input "my_species_input.csv" --output "my_species_output.csv"
   ```

3. **View the Generated Populated Spreadsheet**:
   ```bash
   cat 100_Bug_Project_Populated.csv
   ```

---

## 📁 Repository Directory Layout

```
bookish-giggle/
├── README.md                          # Detailed project documentation
├── atcc_scraper.py                    # Main Python scraping & lookup script
├── 100 Bug Project(FB).csv            # Untouched source input CSV file
├── 100_Bug_Project_Populated.csv      # Generated populated output CSV file
├── cache/                             # Local disk HTML cache directory
└── data/                              # Data export directory
```

---

## 📜 Disclaimers

This project is created for laboratory research and educational data parsing purposes. Product data is property of the American Type Culture Collection (ATCC). All biological materials referenced are intended strictly for research use in compliance with appropriate biosafety guidelines (BSL-1 / BSL-2).
