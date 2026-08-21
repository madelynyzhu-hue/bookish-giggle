# 🧬 Project Presentation Deck: 100-Strain Bacterial Data Catalog

> **Formal Work Presentation & Video Script Template (Includes Code Evolution & GitHub Updates)**  
> *Target Application: Automated Data Mining, Codebase Iterations, Microbiological Profiling, and Biosafety Compliance for Biosensor Training & Testing*

---

## 📽️ How to Use This Presentation Template

1. **Web Interactive Mode**: Open `index.html` in your web browser. Use `←` / `→` or `Space` to navigate slides. Press **`S`** to toggle the built-in **Video Teleprompter Drawer** while recording your video presentation.
2. **Slide Software Mode**: Copy the slide content below directly into PowerPoint, Keynote, or Google Slides.
3. **Video Recording Script**: Each slide includes a word-for-word spoken teleprompter script tailored for a 2–3 minute video project report.

---

## 📊 Slide Structure Overview (5 Slides Total)

```
[Slide 1: Overview] ➔ [Slide 2: GitHub Code Evolution] ➔ [Slide 3: Scraping & Entity Resolution] ➔ [Slide 4: Isolation Sources] ➔ [Slide 5: Growth & Biosafety]
```

---

### 🎬 SLIDE 1: Title & Executive Overview

#### 🖥️ Visual Layout & Text Content
- **Header Badge**: 🔬 Biosensor Model Training Initiative
- **Slide Title**: 100-Strain Bacterial Data Catalog
- **Subtitle**: Project Report on Code Development Milestones, GitHub Refactoring, Entity Resolution, and Biosafety Compliance
- **Key Project Metadata Grid**:
  - **Code Evolution**: 4 Major GitHub Commit Iterations
  - **Project Scope**: 100 Target Strains Cataloged
  - **Primary Deliverable**: 37-Column Populated Schema (`200_Bug_Project_Populated_Comp.csv`)

#### 🎙️ Video Teleprompter Script (Spoken Words)
> *"Hello everyone. Today I'm presenting the project report for our 100-strain bacterial reference catalog. As the data analyst on this project, I developed the codebase and data mining pipeline from initial prototype to a production 37-column dataset for training our disease biosensor. In this presentation, I'll walk through our code development history on GitHub, our technical data engineering architecture, and key microbiological findings."*

---

### 🎬 SLIDE 2: Code Development Milestones & GitHub History

#### 🖥️ Visual Layout & Text Content
- **Header**: Slide 2 / 5 • Code Evolution & GitHub Updates
- **Title**: Code Development Milestones & GitHub History
- **Subtitle**: Key engineering iterations, codebase refactoring, and feature enhancements across the project repository lifecycle.
- **Left Column — GitHub Development History**:
  1. **v1.0 — Initial Scraper & Trial**: Built `atcc_scraper.py` using `urllib` & `BS4`. Ran trial parsing on `atcc_49176_details.txt`.
  2. **v2.0 — 37-Column Script (`atcc_scraper_Comp.py`)**: Scaled extraction to 37 metadata attributes, added `ThreadPoolExecutor` & disk caching (`cache/`).
  3. **v2.5 — GenBank Link Transformation**: Converted raw accession text into direct NCBI URLs (`ncbi.nlm.nih.gov/nuccore/`).
  4. **v3.0 — Scaling & Dataset Expansion**: Updated pipeline to process 148+ entries and refactored scripts for `200 Bug Project(FB).csv`.
- **Right Column — Key Technical Code Upgrades**:
  - **NBF Fallback**: Organism Name Resolution
  - **GenBank API**: Clickable NCBI Accession URLs
  - **Cache Engine**: HTML Disk Cache & Throttle (`cache/`)
  - **SSL Bypass**: macOS CA Cert Validation Fix

#### 🖼️ Recommended Visual Diagram
- **GitHub Commit Timeline Diagram**:
  ```text
  [Commit #2ed4911: v1.0 Initial Scraper] ──► [Commit #c27b641: v2.0 37-Col Scraper] ──► [Commit #bd64feb: v2.5 GenBank URLs] ──► [Commit #739b57d: v3.0 148 Entry Expansion]
  ```

#### 🎙️ Video Teleprompter Script (Spoken Words)
> *"Here on Slide 2, I've highlighted our major code updates and GitHub commits: We started with version 1.0, building a baseline scraper in Python using BeautifulSoup and urllib, and performing trial extractions on single-strain files. In version 2.0, I upgraded to atcc_scraper_Comp.py, expanding output schema to 37 columns and adding ThreadPoolExecutor multithreading with local disk caching to prevent rate-limiting. In version 2.5, I converted raw GenBank text into direct clickable NCBI accession URLs. Finally, in version 3.0, we scaled the pipeline up to handle 148+ strain entries for the 200 Bug Project."*

---

### 🎬 SLIDE 3: CS / Data Analysis — Scraping Engine & Entity Resolution

#### 🖥️ Visual Layout & Text Content
- **Header**: Slide 3 / 5 • CS & Technical Architecture
- **Title**: Scraping Engine & Entity Resolution
- **Subtitle**: Algorithmic mapping of missing catalog identifiers, null value management, and building clean feature stores for ML models.
- **3-Card Architecture Breakdown**:
  1. **Parallel Architecture**: Multithreaded fetching with disk caching keeps latency under 0.5 seconds while preventing server rate limiting.
  2. **Taxonomic Entity Resolution**: Automated resolution of `NBF` ("Not Being Found") species to primary ATCC reference catalog strains (e.g. *S. aureus* → `ATCC 25923`).
  3. **37-Column Schema Output**: Generates a populated metadata catalog that acts as a structured feature store for biosensor machine learning models.
- **Technical Impact Callout**:
  - Taxonomic entity resolution reduced catalog ambiguity from 22% in raw input to 0% in the final analytical dataset, ensuring clean join keys for machine learning model training.

#### 🎙️ Video Teleprompter Script (Spoken Words)
> *"Zooming into technical feature highlights on Slide 3: my parallel web scraper uses disk caching to maintain sub-second re-run performance. A major engineering achievement was taxonomic entity resolution: automatically resolving missing 'NBF' entries to primary reference ATCC catalog numbers—such as mapping Staphylococcus aureus to ATCC 25923—which reduced dataset catalog ambiguity from 22% down to 0%."*

---

### 🎬 SLIDE 4: Bio Domain — Isolation Sources & Ecological Context

#### 🖥️ Visual Layout & Text Content
- **Header**: Slide 4 / 5 • Microbiological Domain
- **Title**: Isolation Sources & Ecological Provenance
- **Subtitle**: Mapping isolation origins to establish sample diversity, target specificity, and real-world background matrix conditions for sensor testing.
- **3-Card Breakdown**:
  1. **Clinical & Human Isolates**: Isolated from blood, sputum, wound exudates, and tissue. Critical for benchmarking sensor sensitivity on human clinical pathogens (e.g., *Staphylococcus aureus*).
  2. **Veterinary Host Specimens**: Derived from animal host lesions and veterinary infections. Expands sensor target recognition across zoonotic vectors (e.g., *Rhodococcus equi* from foal lung abscess).
  3. **Environmental & Sewage**: Sampled from soil, wastewater, and sludge. Essential for testing sensor cross-reactivity against background non-target flora (e.g., *Corynebacterium glutamicum* from wastewater).
- **Sensor Matrix Relevance Callout**:
  - Categorizing isolation origins directly guides sample preparation (e.g. blood lysate filtering vs. environmental water concentration) and prevents false-positive signals during field testing.

#### 🎙️ Video Teleprompter Script (Spoken Words)
> *"Turning to our domain findings on Slide 4: we mapped isolation origins across three main ecological groups: clinical human specimens like blood and sputum for pathogens like Staphylococcus aureus; veterinary host samples like Rhodococcus equi from foal lung abscesses; and environmental wastewater samples like Corynebacterium glutamicum. Categorizing these origins is crucial for sensor data analysis because it helps us model background sample matrix noise—such as blood versus environmental water—preventing false-positive signals during field deployment."*

---

### 🎬 SLIDE 5: Bio Domain — Growth Dynamics, Biosafety & Safety Data Sheets

#### 🖥️ Visual Layout & Text Content
- **Header**: Slide 5 / 5 • Safety & Culture Parameters
- **Title**: Growth Dynamics, Biosafety & Safety Data Sheets
- **Subtitle**: Standardized culture growth requirements, biosafety containment levels, and direct REST API Safety Data Sheet integration.
- **Top 2 Cards**:
  - **Growth Parameters & Culture Profiles**: Incubation Temp (37°C clinical vs 30°C environmental), Culture Media (TSA #18/#260: 65%, BHI #44: 20%), Atmosphere (Aerobic: 85%, CO₂/Microaerophilic: 15%).
  - **Biosafety Rating & SDS API Links**: BSL-1 rating (low risk controls), BSL-2 rating (clinical pathogens requiring hood containment), Direct SDS REST API links (`/api/product/sds?atcc_number=...`).
- **Representative Data Table Excerpt**:

| ATCC # | Organism Binomial | Isolation Source | Culture Medium | Temp | Atmosphere | BSL Rating |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ATCC 14025** | *Enterococcus avium* | Quality Control Record | TSA w/ Sheep Blood (#260) | 37°C | Aerobic | **BSL 1** |
| **ATCC 8750** | *Alcaligenes faecalis* | Preceptrol Culture | Trypticase Soy (#18) | 37°C | Aerobic | **BSL 1** |
| **ATCC 6939** | *Rhodococcus equi* | Foal Lung Abscess | Brain Heart Infusion (#44) | 37°C | Aerobic | **BSL 2** |
| **ATCC 13032** | *Corynebacterium glutamicum* | Sewage / Wastewater | Nutrient Agar (#3) | 37°C | Aerobic | **BSL 1** |

#### 🎙️ Video Teleprompter Script (Spoken Words)
> *"Finally, on Slide 5 covering growth parameters and biosafety: we extracted incubation temperatures, media formulations, and gaseous atmospheres across all 100 strains. Clinical pathogens cluster at 37°C while environmental strains grow at 30°C, primarily using Trypticase Soy Agar or Brain Heart Infusion broth. Every strain is also categorized by Biosafety Level—BSL-1 versus BSL-2—and paired with direct REST API links for official Safety Data Sheets for instant lab safety access. Thank you."*

---

## 📽️ Video Recording Tips

1. **GitHub Development Story**: Slide 2 clearly shows your active role in coding, iterating, and scaling the codebase on GitHub.
2. **Teleprompter Drawer**: Open `index.html` in Chrome/Safari, press **`F`** for Fullscreen, and press **`S`** to display the teleprompter drawer while recording!
