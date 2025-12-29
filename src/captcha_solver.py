"""
Consent Selectors Parser 
Scraping consent button selectors from Consent-O-Matic GitHub repository using 
Requests library and BeautifulSoup for HTML parsing.
"""

import requests
from bs4 import BeautifulSoup
import json

# Public GitHub URL for Consent-O-Matic rules
url = "https://github.com/cavi-au/Consent-O-Matic/tree/master/rules"

def get_text_if_exist(e):
    if e:
        return e.text.strip()
    return None

# Store all selectors
all_selectors = []

print("Parsing Consent-O-Matic GitHub repo for consent button selectors...")
print(f"URL: {url}\n")

# Make request
response = requests.get(url)
response.encoding = response.apparent_encoding

if response.status_code == 200:
    print(f"Status code: {response.status_code}")
    html = response.text
    
    f = open("github_response.html", "w", encoding='utf-8')
    f.write(html)
    f.close()
    print("HTML saved to: github_response.html")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    
    # Find all JSON file links
    # GitHub structure: <a> tags with .json files
    links = soup.find_all("a", class_="Link--primary")
    
    json_files = []
    for link in links:
        href = link.get('href')
        if href and '.json' in href:
            filename = link.text.strip()
            json_files.append(filename)
            print(f"Found: {filename}")
    
    print(f"\n✓ Found {len(json_files)} JSON files")
    
    # Download and parse main JSON files - cookies, onetrust, quantcast
    json_urls = [
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/cookiebot.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/onetrust.json",
        "https://raw.githubusercontent.com/cavi-au/Consent-O-Matic/master/rules/quantcast.json",
    ]
    
    for json_url in json_urls:
        json_response = requests.get(json_url)
        
        if json_response.status_code == 200:
            data = json.loads(json_response.text)
            
            # Extract selectors (simple version)
            for cmp_name, cmp_data in data.items():
                if cmp_name.startswith('$'):
                    continue
                
                print(f"    Parsing: {cmp_name}")
                
                # Simple extraction
                if 'methods' in cmp_data:
                    for method in cmp_data['methods']:
                        if 'action' in method:
                            action = method['action']
                            
                            # Extract selector from target
                            if isinstance(action, dict) and 'target' in action:
                                target = action['target']
                                if isinstance(target, dict) and 'selector' in target:
                                    selector = target['selector']
                                    
                                    # Convert CSS to XPath
                                    if selector.startswith('#'):
                                        xpath = f"//*[@id='{selector[1:]}']"
                                        all_selectors.append(xpath)
                                    elif selector.startswith('.'):
                                        xpath = f"//*[contains(@class, '{selector[1:]}')]"
                                        all_selectors.append(xpath)
        else:
            print(f"    ✗ Error: {json_response.status_code}")
    
    # Add manual selectors (comme dans le TP, on ajoute manuellement)
    print("\n\nAdding manual text-based selectors...")
    
    # English buttons
    manual_selectors = [
        # English
        "//button[contains(text(), 'Accept')]",
        "//button[contains(text(), 'Accept all')]",
        "//button[contains(text(), 'I agree')]",
        "//button[contains(text(), 'Agree')]",
        "//a[contains(text(), 'Accept')]",
        "//input[@value='Accept']",
        
        # French
        "//button[contains(text(), 'Accepter')]",
        "//button[contains(text(), \"J'accepte\")]",
        "//button[contains(text(), 'Tout accepter')]",
        
        # German
        "//button[contains(text(), 'Akzeptieren')]",
        
        # Spanish
        "//button[contains(text(), 'Aceptar')]",
        
        # Russian (for RuTracker POC site)
        "//input[@value='Я согласен с этими правилами']",
        "//button[contains(text(), 'Согласен')]",
        "//button[contains(text(), 'Принимаю')]",
        "//button[contains(text(), 'Принять')]",
        "//input[contains(@value, 'согласен')]",
    ]
    
    all_selectors.extend(manual_selectors)
    print(f"Added {len(manual_selectors)} manual selectors")
    
    # Save to file (comme dans le TP)
    print(f"\nSaving to file...")
    
    f = open("consent_selectors.py", "w", encoding='utf-8')
    
    # Write header
    f.write('"""\n')
    f.write('Consent Button Selectors\n')
    f.write('========================\n')
    f.write('\n')
    f.write('Scraped from Consent-O-Matic GitHub using BeautifulSoup\n')
    f.write('Method: requests + BeautifulSoup (student edition)\n')
    f.write('\n')
    f.write('Source: https://github.com/cavi-au/Consent-O-Matic\n')
    f.write(f'Total selectors: {len(all_selectors)}\n')
    f.write('\n')
    f.write('Projet M2 MoSEF 2025-2026\n')
    f.write('"""\n\n')
    f.write('CONSENT_SELECTORS = [\n')
    
    # Write each selector (comme écrire les prix)
    for selector in all_selectors:
        # Escape quotes
        escaped = selector.replace("'", "\\'")
        f.write(f"    '{escaped}',\n")
    
    f.write(']\n')
    f.close()
    
    print(f"✓ File saved: consent_selectors.py")
    print(f"✓ Total selectors: {len(all_selectors)}")

else:
    print(f"✗ Error: {response.status_code}")

print("\nFIN")