"""
Consent & Cookies Selectors Parser 
Scraping button selectors from Consent-O-Matic GitHub public repo using 
Selenium & BeautifulSoup to extract selectors for scraper script.
""" 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import time

# Public open source GitHub containing rule lists for CMPs
url = "https://github.com/cavi-au/Consent-O-Matic/tree/master/rules"
selectors = []

def get_text_if_exist(e):
    if e:
        return e.text.strip()
    return None

# Using Selenium to render JS React
print("Opening GitHub page... Wait a moment please.")

# Configuration of Chrome WebDriver options & driver initialization
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_github_info(driver, url):
    # Get HTML after JS rendering
    try:
        driver.get(url)
        time.sleep(4) # Wait for page to load JS
        html = driver.page_source
        
        # Parse with bs4
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all JSON links with class 'Link--primary'
        links = get_text_if_exist(soup.find("a", class_='Link--primary'))
        links = soup.find_all('a', class_='Link--primary')
        
        json_files = []
        for link in links:
            href = link.get('href')

            if href and '.json' in href:
                filename = link.text.strip()

                if filename:
                    json_files.append(filename)
        
        print(f"Found {len(json_files)} JSON files on GitHub repo")
        return json_files
        
    except Exception as e:
        print(f"Error: {e}")
        return []
        
    finally:
        driver.quit()

json_files = get_github_info(driver,url)

# 408 files are too long to check, giant platforms do not use text captcha anymore, filtering main selectors by keywords
keywords = ['cookie', 'consent', 'cookiebot', 'cookiefirst', 'cookiepro', 
            'onetrust', 'quantcast', 'didomi', 'trustarc', 'usercentrics', 
            'sourcepoint', 'osano', 'complianz', 'iubenda', 'termly']

main_files = []

for filename in json_files:
    filename_lower=filename.lower()
    for keyword in keywords:
        if keyword in filename_lower:
            main_files.append(filename)
            break
print(f"Filtered: {len(main_files)} main files from {len(json_files)} total")

# Download main files to extract selectord from
absolute_url = "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/"

for filename in main_files:
    json_url=absolute_url+filename
    print(filename)
    
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
                                
                                # Convert CSS to xpath
                                xpath=None
                                # By ID
                                if selector.startswith('#') and ' ' not in selector and ',' not in selector:
                                    xpath = f"//*[@id='{selector[1:]}']"
                                    selectors.append(xpath)
                                # By class
                                elif selector.startswith('.') and ' ' not in selector and ',' not in selector:
                                    class_name = selector[1:].split(':')[0]
                                    xpath = f"//*[contains(@class, '{class_name}')]"
                                    if xpath not in selectors:
                                        selectors.append(xpath)
    else:
        print(f"Error: {json_response.status_code}")

print(f"Extracted {len(selectors)} selectors from JSON files")

# During demo testing we had searched for international sites, hence adding simple button selectors in other languages
manual_selectors = [
    "//button[contains(text(), 'Accept')]",
    "//button[contains(text(), 'Accept all')]",
    "//button[contains(text(), 'I agree')]",
    "//button[contains(text(), 'I accept')]",
    "//button[contains(text(), 'Agree')]",
    "//a[contains(text(), 'Accept')]",
    "//input[@value='Accept']",

    "//button[contains(text(), 'Accepter')]",
    "//button[contains(text(), \"J'accepte\")]",
    "//button[contains(text(), 'Tout accepter')]",
    
    # Spanish
    "//button[contains(text(), 'Aceptar')]",
    
    # Russian (for POC site)
    "//input[@value='Я согласен с этими правилами']",
    "//button[contains(text(), 'Согласен')]",
    "//button[contains(text(), 'Принимаю')]",
    "//button[contains(text(), 'Принять')]",
    "//input[contains(@value, 'согласен')]",
]

selectors.extend(manual_selectors)
print(f"Added {len(manual_selectors)} manual selectors\nTotal {len(selectors)} selectors")

# Saving in utils
with open('utils/consent_cookies_selectors.py', 'w', encoding='utf-8') as file:
    file.write('consent_selectors = [\n')
    for selector in selectors:
        selector = selector.replace("'", "\\'")
        file.write(f"    '{selector}',\n")
    file.write(']')
