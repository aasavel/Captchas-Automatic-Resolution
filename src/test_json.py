"""
Consent & Cookies Selectors Parser 
Scraping button selectors from Consent-O-Matic GitHub public repo using 
Selenium & BeautifulSoup to extract selectors for scraper script.

FINAL FIXED VERSION: Correct XPath generation

Projet M2 MoSEF 2025-2026 - Université Paris 1 Panthéon-Sorbonne
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

# Keywords to filter important platforms
IMPORTANT_KEYWORDS = [
    'cookie', 'consent', 'onetrust', 'cookiebot', 'quantcast',
    'didomi', 'trustarc', 'usercentrics', 'sourcepoint', 'osano',
    'complianz', 'iubenda', 'termly', 'cookiefirst', 'cookiepro'
]

all_selectors = []

# Using Selenium to render JS React
print("Opening GitHub page... Wait a moment please.")

# Configuration of Chrome WebDriver options & driver initialization
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_page_info(driver, url):
    # Get HTML after JS rendering
    try:
        driver.get(url)
        time.sleep(4)  # Wait for page to load JS
        html = driver.page_source
        
        with open('github_response.html', 'w', encoding='utf-8') as file:
            file.write(html)
            print("HTML saved to github_response.html")
        
        # Parse with bs4
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all JSON links with class 'Link--primary'
        links = soup.find_all("a", class_='Link--primary')
        
        json_files = []
        for link in links:
            href = link.get('href')
            
            if href and '.json' in href:
                filename = link.text.strip()
                
                if filename:
                    json_files.append(filename)
        
        print(f"Found {len(json_files)} JSON files on GitHub repo\n")
        return json_files
        
    except Exception as e:
        print(f"Error: {e}")
        return []
        
    finally:
        driver.quit()
        print("Browser closed\n")


# Get all JSON files
json_files = get_page_info(driver, url)

# ============================================
# FILTER: Keep only important files
# ============================================
print("Filtering important files...")

important_files = []
for filename in json_files:
    filename_lower = filename.lower()
    # Check if any keyword is in filename
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in filename_lower:
            important_files.append(filename)
            print(f"  ✓ {filename}")
            break

print(f"\nFiltered: {len(important_files)} important files (from {len(json_files)} total)\n")

# ============================================
# DOWNLOAD AND PARSE: Important files only
# ============================================
print("Downloading important platform JSON files...\n")

base_url = "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/"

for filename in important_files:
    json_url = base_url + filename
    print(f"📥 Downloading: {filename}")
    
    json_response = requests.get(json_url)
    
    if json_response.status_code == 200:
        data = json.loads(json_response.text)
        
        # Extract selectors
        for cmp_name, cmp_data in data.items():
            if cmp_name.startswith('$'):
                continue
            
            # Simple extraction
            if 'methods' in cmp_data:
                for method in cmp_data['methods']:
                    if 'action' in method:
                        action = method['action']
                        
                        # Get selector from target
                        if isinstance(action, dict) and 'target' in action:
                            target = action['target']
                            if isinstance(target, dict) and 'selector' in target:
                                selector = target['selector']
                                
                                # Convert CSS to XPath (ONLY SIMPLE SELECTORS!)
                                xpath = None
                                
                                # Skip complex selectors
                                if ' ' in selector or ',' in selector or '>' in selector or '+' in selector or '~' in selector:
                                    continue  # Skip complex selectors
                                
                                # Single ID: #my-id
                                if selector.startswith('#'):
                                    xpath = f'//*[@id="{selector[1:]}"]'
                                
                                # Single class: .my-class
                                elif selector.startswith('.'):
                                    # Remove CSS pseudoclasses (:hover, :first-child, etc)
                                    class_name = selector[1:].split(':')[0].split('[')[0]
                                    if class_name:  # Make sure not empty
                                        xpath = f'//*[contains(@class, "{class_name}")]'
                                
                                # Attribute selector: [data-test='value']
                                elif selector.startswith('[') and selector.endswith(']'):
                                    try:
                                        attr_part = selector.strip('[]')
                                        
                                        # Check for different operators
                                        if '^=' in attr_part:  # starts-with
                                            attr, value = attr_part.split('^=', 1)
                                            value = value.strip().strip('"\'')
                                            xpath = f'//*[starts-with(@{attr}, "{value}")]'
                                        elif '*=' in attr_part:  # contains
                                            attr, value = attr_part.split('*=', 1)
                                            value = value.strip().strip('"\'')
                                            xpath = f'//*[contains(@{attr}, "{value}")]'
                                        elif '=' in attr_part:  # equals
                                            attr, value = attr_part.split('=', 1)
                                            value = value.strip().strip('"\'')
                                            xpath = f'//*[@{attr}="{value}"]'
                                    except:
                                        pass  # Skip malformed selectors
                                
                                # Add to list if valid and not duplicate
                                if xpath and xpath not in all_selectors:
                                    all_selectors.append(xpath)
    else:
        print(f"   ✗ Error: {json_response.status_code}")

print(f"\n✓ Extracted {len(all_selectors)} selectors from JSON files")

# ============================================
# ADD MANUAL SELECTORS
# ============================================
print("\nAdding manual text-based selectors...")

manual_selectors = [
    # English
    '//button[contains(text(), "Accept")]',
    '//button[contains(text(), "Accept all")]',
    '//button[contains(text(), "Accept All")]',
    '//button[contains(text(), "I agree")]',
    '//button[contains(text(), "Agree")]',
    '//a[contains(text(), "Accept")]',
    '//input[@value="Accept"]',
    
    # French
    '//button[contains(text(), "Accepter")]',
    '//button[contains(text(), "J\'accepte")]',
    '//button[contains(text(), "Tout accepter")]',
    
    # German
    '//button[contains(text(), "Akzeptieren")]',
    '//button[contains(text(), "Alle akzeptieren")]',
    
    # Spanish
    '//button[contains(text(), "Aceptar")]',
    '//button[contains(text(), "Aceptar todo")]',
    
    # Russian (for RuTracker POC site)
    '//input[@value="Я согласен с этими правилами"]',
    '//button[contains(text(), "Согласен")]',
    '//button[contains(text(), "Принимаю")]',
    '//button[contains(text(), "Принять")]',
    '//input[contains(@value, "согласен")]',
]

all_selectors.extend(manual_selectors)
print(f"✓ Added {len(manual_selectors)} manual selectors")

# ============================================
# SAVE TO FILE
# ============================================
print(f"\nSaving to file...")

f = open("consent_selectors.py", "w", encoding='utf-8')

# Write header
f.write('"""\n')
f.write('Consent Button Selectors\n')
f.write('========================\n')
f.write('\n')
f.write('Scraped from Consent-O-Matic GitHub using Selenium + BeautifulSoup\n')
f.write('Method: Keyword filtering + Simple CSS to XPath conversion\n')
f.write('\n')
f.write('Source: https://github.com/cavi-au/Consent-O-Matic\n')
f.write(f'Total files on GitHub: {len(json_files)}\n')
f.write(f'Important files processed: {len(important_files)}\n')
f.write(f'Keywords: {", ".join(IMPORTANT_KEYWORDS[:5])}...\n')
f.write(f'Total selectors: {len(all_selectors)}\n')
f.write('\n')
f.write('Note: Only simple CSS selectors converted (single ID/class/attribute)\n')
f.write('Complex selectors (spaces, commas, combinators) are skipped for accuracy\n')
f.write('\n')
f.write('Platforms covered: Cookie, Consent, OneTrust, Cookiebot, and other major CMPs\n')
f.write('\n')
f.write('Projet M2 MoSEF 2025-2026 - Université Paris 1 Panthéon-Sorbonne\n')
f.write('"""\n\n')
f.write('CONSENT_SELECTORS = [\n')

# Write each selector
for selector in all_selectors:
    # Escape single quotes properly
    escaped = selector.replace("'", "\\'")
    f.write(f"    '{escaped}',\n")

f.write(']\n\n')
f.write('if __name__ == "__main__":\n')
f.write('    print(f"Total consent selectors: {len(CONSENT_SELECTORS)}")\n')
f.write('    print("\\nBreakdown:")\n')
f.write(f'    print(f"  - From JSON: {len(all_selectors) - len(manual_selectors)}")\n')
f.write(f'    print(f"  - Manual: {len(manual_selectors)}")\n')
f.close()

print(f"✓ File saved: consent_selectors.py")
print(f"✓ Total selectors: {len(all_selectors)}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"GitHub files found: {len(json_files)}")
print(f"Important files: {len(important_files)}")
print(f"Keywords used: {', '.join(IMPORTANT_KEYWORDS[:5])}...")
print(f"Total selectors: {len(all_selectors)}")
print(f"  - From JSON: {len(all_selectors) - len(manual_selectors)}")
print(f"  - Manual: {len(manual_selectors)}")
print("\nNote: Complex CSS selectors were skipped (only simple ones converted)")
print("="*60)

print("\nFIN")