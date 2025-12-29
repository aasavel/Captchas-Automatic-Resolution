"""
Consent Button Selectors
========================

Scraped from Consent-O-Matic GitHub using BeautifulSoup
Method: requests + BeautifulSoup (student edition)

Source: https://github.com/cavi-au/Consent-O-Matic
Total selectors: 20

Projet M2 MoSEF 2025-2026
"""

consent_selectors = [
    '//*[@id=\'onetrust-banner-sdk #onetrust-pc-btn-handler, .ot-sdk-show-settings:not([href])\']',
    '//*[contains(@class, \'save-preference-btn-handler\')]',
    '//*[contains(@class, \'qc-cmp-save-and-exit\')]',
    '//*[contains(@class, \'qc-cmp-ui-container\')]',
    '//button[contains(text(), \'Accept\')]',
    '//button[contains(text(), \'Accept all\')]',
    '//button[contains(text(), \'I agree\')]',
    '//button[contains(text(), \'Agree\')]',
    '//a[contains(text(), \'Accept\')]',
    '//input[@value=\'Accept\']',
    '//button[contains(text(), \'Accepter\')]',
    '//button[contains(text(), "J\'accepte")]',
    '//button[contains(text(), \'Tout accepter\')]',
    '//button[contains(text(), \'Akzeptieren\')]',
    '//button[contains(text(), \'Aceptar\')]',
    '//input[@value=\'Я согласен с этими правилами\']',
    '//button[contains(text(), \'Согласен\')]',
    '//button[contains(text(), \'Принимаю\')]',
    '//button[contains(text(), \'Принять\')]',
    '//input[contains(@value, \'согласен\')]',
]
