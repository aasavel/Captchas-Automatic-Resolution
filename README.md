# 🧠 Automated CAPTCHA Solver  
**Web Scraping • Computer Vision • FastAPI**


## Project Objective

The goal of this project is to design a **robust web scraping system capable of bypassing visual CAPTCHAs**, relying on three main components:

1. **Web scraping using Selenium**
2. **Deep learning model for CAPTCHA recognition (letters & digits)**
3. **REST API to orchestrate and industrialize the full pipeline using FastAPI**



## Project Architecture

The system is composed of three independent but connected modules:

### Web Scraping (Selenium)
- Automated navigation on websites protected by visual CAPTCHAs
- Detection and extraction of CAPTCHA images
- Robust browser configuration (headless mode, waits, retries)

### CAPTCHA Recognition Model
- Supervised deep learning model (CNN / CRNN)
- Recognition of **letters and digits** (not reCAPTCHA)
- Image preprocessing and evaluation metrics
- Trained on open-source CAPTCHA datasets

### API Orchestration (FastAPI)
- Centralized control of scraping and prediction
- REST endpoints for:
  - triggering scraping
  - solving CAPTCHAs
  - monitoring system health
- Designed for scalability and production-like deployment


## 📁 Project Structure

```text
Сaptchas-Automatic-Resolution/
│
├── README.md
├── pyproject.toml         
├── poetry.lock
├── .gitignore
├── .env.example
│
├── data/
│   ├── raw/                # Raw CAPTCHA images
│   ├── processed/          # Preprocessed images
│   └── samples/            # Small test samples
│
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_evaluation.ipynb
│
├── scraper/
│   ├── selenium_scraper.py
│   ├── captcha_collector.py
│   ├── browser.py
│   └── utils.py
│
├── captcha_model/
│   ├── dataset.py
│   ├── model.py
│   ├── train.py
│   ├── predict.py
│   ├── metrics.py
│   └── preprocessing.py
│
├── api/
│   ├── main.py             # FastAPI entrypoint
│   ├── schemas.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── scrape.py
│   │   └── predict.py
│   └── services/
│       ├── scraper_service.py
│       └── captcha_service.py
│
├── tests/
│   ├── test_scraper.py
│   ├── test_model.py
│   └── test_api.py
│
├── scripts/
│   ├── download_dataset.py
│   ├── train_model.py
│   └── run_scraper.py
│
└── reports/
    ├── figures/
    └── results.md



## Installation

This project uses **Poetry** for dependency management.

```bash
git clone https://github.com/aasavel/Captchas-Automatic-Resolution.git
cd captcha-solver-project
poetry install
poetry shell


```markdown

## Running the API

```bash
uvicorn api.main:app --reload




                /\_/\ 
               ( o.o )
                > ^ <
             __/|___|\__
            /  /     \  \
           /__/       \__\
           \  \  ___  /  /
            \__\/___\/__/
               /  |  \
              /___|___\
               (__) (__)
