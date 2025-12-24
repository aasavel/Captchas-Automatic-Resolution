# Captchas-Automatic-Resolution-
This repo contains webscraping (selenium), OCR model &amp; API (FastApi) to resolve automatically visual captchas.

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

## OCR MODEL

===== VALIDATION PERFORMANCE =====
{'CER': 0.02111141598205207, 'Character Accuracy': 0.978888584017948, 'Exact Match Accuracy': 0.9026779882429784, 'Samples': 12248}

===== TEST PERFORMANCE =====
{'CER': 0.020052268180938245, 'Character Accuracy': 0.9799477318190618, 'Exact Match Accuracy': 0.9075918367346939, 'Samples': 12250}

## 📁 Project Structure

```text
captcha_solver/
│
├── README.md
├── requirements.txt
├── .env
├── .gitignore
│
├── models/
│   └── ocr_captcha_v1.keras
│
├── ocr/
│   ├── __init__.py
│   ├── model.py
│   ├── preprocess.py
│   ├── decoder.py
│   └── predictor.py
│
├── scraping/
│   ├── __init__.py
│   ├── selenium_client.py
│   ├── captcha_collector.py
│   └── solver.py
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   └── routes.py
│
├── ui/
│   ├── streamlit_app.py
│   └── assets/
│
├── scripts/
│   ├── test_ocr.py
│   ├── batch_predict.py
│   └── sanity_check.py
│
└── tests/
    ├── test_preprocess.py
    ├── test_decoder.py
    └── test_api.py
```


**Collaborateurs :**

- Anastasiia Sevolka
- Jean-Baptiste CHEZE
- Théo Linale