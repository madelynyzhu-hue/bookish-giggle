// Interactive Slide Deck & Teleprompter Controller - GitHub Code Evolution Included
document.addEventListener('DOMContentLoaded', () => {
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const slideCounter = document.getElementById('slide-counter');
  const scriptDrawer = document.getElementById('script-drawer');
  const scriptText = document.getElementById('script-text');
  const scriptSlideNum = document.getElementById('script-slide-num');
  const toggleScriptBtn = document.getElementById('toggle-script-btn');
  const closeScriptBtn = document.getElementById('close-script-btn');
  const fullscreenBtn = document.getElementById('fullscreen-btn');

  let currentSlide = 0;

  // Spoken Teleprompter Scripts (Slide 1: Overview, Slide 2: GitHub Code Evolution, Slide 3: Scraping & Entity Resolution, Slide 4: Isolation Sources, Slide 5: Bio Parameters & SDS)
  const presenterScripts = [
    // Slide 1: Executive Overview
    `"Hello everyone. Today I'm presenting the project report for our 100-strain bacterial reference catalog. As the data analyst on this project, I developed the codebase and data mining pipeline from initial prototype to a production 37-column dataset for training our disease biosensor. In this presentation, I'll walk through our code development history on GitHub, our technical data engineering architecture, and key microbiological findings."`,

    // Slide 2: Code Development Milestones & GitHub History
    `"Here on Slide 2, I've highlighted our major code updates and GitHub commits: We started with version 1.0, building a baseline scraper in Python using BeautifulSoup and urllib, and performing trial extractions on single-strain files. In version 2.0, I upgraded to atcc_scraper_Comp.py, expanding output schema to 37 columns and adding ThreadPoolExecutor multithreading with local disk caching to prevent rate-limiting. In version 2.5, I converted raw GenBank text into direct clickable NCBI accession URLs. Finally, in version 3.0, we scaled the pipeline up to handle 148+ strain entries for the 200 Bug Project."`,

    // Slide 3: CS / Data Analysis - Scraping Engine & Entity Resolution
    `"Zooming into technical feature highlights on Slide 3: my parallel web scraper uses disk caching to maintain sub-second re-run performance. A major engineering achievement was taxonomic entity resolution: automatically resolving missing 'NBF' entries to primary reference ATCC catalog numbers—such as mapping Staphylococcus aureus to ATCC 25923—which reduced dataset ambiguity from 22% down to 0%."`,

    // Slide 4: Bio Domain - Isolation Sources & Ecological Context
    `"Turning to our domain findings on Slide 4: we mapped isolation origins across three main ecological groups: clinical human specimens like blood and sputum for pathogens like Staphylococcus aureus; veterinary host samples like Rhodococcus equi from foal lung abscesses; and environmental wastewater samples like Corynebacterium glutamicum. Categorizing these origins is crucial for sensor data analysis because it helps us model background sample matrix noise—such as blood versus environmental water—preventing false-positive signals during field deployment."`,

    // Slide 5: Bio Domain - Growth Dynamics, Biosafety & SDS API Links
    `"Finally, on Slide 5 covering growth parameters and biosafety: we extracted incubation temperatures, media formulations, and gaseous atmospheres across all 100 strains. Clinical pathogens cluster at 37°C while environmental strains grow at 30°C, primarily using Trypticase Soy Agar or Brain Heart Infusion broth. Every strain is also categorized by Biosafety Level—BSL-1 versus BSL-2—and paired with direct REST API links for official Safety Data Sheets for instant lab safety access. Thank you."`
  ];

  function updateSlide(index) {
    if (index < 0 || index >= slides.length) return;
    
    slides[currentSlide].classList.remove('active');
    dots[currentSlide].classList.remove('active');

    currentSlide = index;

    slides[currentSlide].classList.add('active');
    dots[currentSlide].classList.add('active');

    // Update Counter & Controls
    slideCounter.textContent = `${currentSlide + 1} / ${slides.length}`;
    prevBtn.disabled = currentSlide === 0;
    nextBtn.disabled = currentSlide === slides.length - 1;

    // Update Teleprompter Script Text
    scriptSlideNum.textContent = `Slide ${currentSlide + 1}`;
    scriptText.textContent = presenterScripts[currentSlide];
  }

  // Event Listeners for Navigation Buttons
  prevBtn.addEventListener('click', () => updateSlide(currentSlide - 1));
  nextBtn.addEventListener('click', () => updateSlide(currentSlide + 1));

  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => updateSlide(index));
  });

  // Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      e.preventDefault();
      if (currentSlide < slides.length - 1) updateSlide(currentSlide + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      if (currentSlide > 0) updateSlide(currentSlide - 1);
    } else if (e.key.toLowerCase() === 's') {
      e.preventDefault();
      scriptDrawer.classList.toggle('open');
      toggleScriptBtn.classList.toggle('active');
    } else if (e.key.toLowerCase() === 'f') {
      e.preventDefault();
      toggleFullscreen();
    }
  });

  // Script Drawer Controls
  toggleScriptBtn.addEventListener('click', () => {
    scriptDrawer.classList.toggle('open');
    toggleScriptBtn.classList.toggle('active');
  });

  closeScriptBtn.addEventListener('click', () => {
    scriptDrawer.classList.remove('open');
    toggleScriptBtn.classList.remove('active');
  });

  // Fullscreen Handler
  fullscreenBtn.addEventListener('click', toggleFullscreen);

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  // Initialize First Slide Script
  updateSlide(0);
});
