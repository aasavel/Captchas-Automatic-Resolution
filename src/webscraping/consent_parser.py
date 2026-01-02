"""
CONSENT SELECTOR PARSER
The goal is to scrape button selectors from Consent-O-Matic GitHub public repo to extract selectors for scraper script.
""" 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import json
import time

# Public open source GitHub containing rule lists for CMPs
url = "https://github.com/cavi-au/Consent-O-Matic/tree/master/rules"

def get_text_if_exist(element):
    if element:
        return element.text.strip()
    return None

# Configuration chrome webdriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)
print("Opening GitHub. Please wait for a moment...")

def get_json_files(driver, wait, url):
    # Using Selenium to render JS React & waiting for page to load JS
    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.Link--primary")))
        
        # Parse with bs4
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all JSON links with class 'Link--primary'
        links = soup.find_all('a', class_='Link--primary')
        json_files = []

        for link in links:
            link_url=link.get('href')
            if link_url and '.json' in link_url:
                file=link.text.strip()
                if file:
                    json_files.append(file)
        return json_files 
    except TimeoutException:
        return []
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        driver.quit()

json_files = get_json_files(driver,wait, url)

# 408 files are too long to check, a) long with bs4 b) giant platforms do not use text captcha anymore, 
# => Filtering main selectors by keywords : cookie & top gouvernances platforms 
keywords = ['consent', 'cookie', 'cookiebot', 'cookiefirst', 'cookiepro', 'onetrust', 
            'quantcast', 'consentmanager', 'sourcepoint', 'osano', 'complianz']

main_files = []

for file in json_files:
    file_lower=file.lower()
    for keyword in keywords:
        if keyword in file_lower:
            main_files.append(file)
            break
print(f"Filtered: {len(main_files)} main files from {len(json_files)} total on GitHub repo")

# Parsing JSON files to extract CSS selectors
absolute_url = "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/"
css_selectors = []

for file in main_files:
    json_url=absolute_url+file
    print(file)
    
    json_response = requests.get(json_url)
    
    if json_response.status_code == 200:
        data = json.loads(json_response.text)
        
        # Extract selectors
        for cmp_name, cmp_data in data.items():
            if cmp_name.startswith('$'):
                continue
            
            if 'methods' in cmp_data:
                for method in cmp_data['methods']:
                    if 'action' in method:
                        action = method['action']
                        
                        # Get selector from target
                        if isinstance(action, dict) and 'target' in action:
                            target = action['target']
                            if isinstance(target, dict) and 'selector' in target:
                                selector = target['selector']
                                # CSS selectors for By.CSS selectors
                                if selector.startswith('#') or selector.startswith('.'):
                                    if ' ' not in selector and ',' not in selector:
                                        if selector not in css_selectors:
                                            css_selectors.append(selector)
                                        else:
                                            if selector not in css_selectors:
                                                css_selectors.append(selector)        
    else:
        print(f"Error: {json_response.status_code}")

print(f"Parsered {len(css_selectors)} selectors")

# During demo testing we had searched for international sites, hence adding simple button XPATH selectors in different languages
xpath_selectors = [
    "//button[contains(text(),'Accept')]",
    "//button[contains(text(),'Accept all')]",
    "//button[contains(text(),'I agree')]",
    "//button[contains(text(),'I accept')]",
    "//button[contains(text(),'Agree')]",
    "//a[contains(text(),'Accept')]",
    "//a[contains(text(),'I accept')]",
    "//a[contains(text(),'Agree')]",
    "//input[@value='Accept']",
    "//button[contains(text(),'Accepter')]",
    "//button[contains(text(),'Tout accepter')]",
    "//input[@value='Accept']",
    "//input[@value='Accepter']",
    "//a[contains(text(),'Accepter')]",
    "//button[contains(text(),'Aceptar')]",
    "//button[contains(text(),'Acepto')]",
    "//a[contains(text(),'Accepter')]",
    "//a[contains(text(),'Aceptar')]",
    "//button[contains(text(),'Akzeptieren')]",
    
    # Russian (for the real forum POC site we tested (rutracker.org))
    "//input[@value='Я согласен с этими правилами']"
]

print(f"Total: {len(css_selectors)} CSS + {len(xpath_selectors)} XPath = {len(css_selectors)+len(xpath_selectors)} in total")

# Saving in utils
with open('src/webscraping/utils/consent_selectors.py', 'w', encoding='utf-8') as file:
    file.write('# CSS SELECTORS \n')
    file.write('css_selectors = [')
    for selector in css_selectors:
        selector = selector.replace("'", "\\'")
        file.write(f"'{selector}',")
    file.write(']\n')
    file.write('# XPATH SELECTORS \n')
    file.write('xpath_selectors = [')
    for selector in xpath_selectors:
        selector = selector.replace("'", "\\'")
        file.write(f"'{selector}',")
    file.write(']\n')