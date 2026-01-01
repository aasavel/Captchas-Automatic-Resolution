# Sources used:
# https://github.com/sarrabenyahia/tuto-webscraping/blob/main/selenium/tuto-intro2selenium/main.py
# https://selenium-python.readthedocs.io
# https://www.youtube.com/watch?v=NB8OceGZGjA

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import csv
import json
import time

print("CURRENT WORKING DIR:", os.getcwd())


def save_metadata_to_csv_json(file_name, url):
    """Save results in csv and json"""
    with open('data/processed/metadata.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([file_name, url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    try:
        with open('data/processed/results.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        data = [] 

    result = {'url': url, 'file': file_name, 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    data.append(result)

    with open('data/processed/results.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)


def handle_consent_button(driver):
    """Handle consent/agreement buttons (for rutracker etc.)"""
    try:
        # Scroll to bottom to see the button
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Try to find and click consent button
        consent_button = driver.find_element(By.XPATH, "//input[@value='Я согласен с этими правилами']")
        consent_button.click()
        print("✓ Consent button clicked")
        time.sleep(3)  # Wait for page to reload
        return True
    except:
        # No consent button, continue
        return False


def scrape_captcha_from_url(driver, wait, url):
    """Main scraping function"""
    print(f"\n{'='*60}")
    print(f"1. Opening: {url}")
    driver.get(url)
    time.sleep(2)
    print(f"Title: {driver.title}")
    
    # Try to handle consent button
    handle_consent_button(driver)

    try:
        # 1. Check for iframes
        print("\n2. Checking for iframes")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"   Iframe detected: {len(iframes)}")
            driver.switch_to.frame(iframes[0])
        else:
            print("   No iframe detected")

        # 2. Wait for visual elements
        print("\n3. Searching for visual elements")
        wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
        elements = driver.find_elements(By.XPATH, "//img | //canvas")
        print(f"   Visual elements found: {len(elements)}")

        # 3. CAPTCHA detection heuristic
        print("\n4. Analyzing elements for CAPTCHA...")
        for el in elements:
            width = el.size["width"]
            height = el.size["height"]
            src = el.get_attribute("src") or ""

            # Check if size matches CAPTCHA dimensions
            if 100 < width < 400 and 40 < height < 150:
                # Skip logos and banners
                if "logo" in src.lower() or "banner" in src.lower():
                    print(f"   Skipped (logo/banner): {width}x{height}")
                    continue
                
                print(f"   ✓ CAPTCHA candidate detected: {width}x{height}")

                # Save CAPTCHA
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                path = f"data/raw/{filename}"

                el.screenshot(path)
                print(f"   ✓ CAPTCHA saved: {path}")

                save_metadata_to_csv_json(filename, url)

                driver.switch_to.default_content()
                return True

        print("   ⚠ No CAPTCHA detected on this page")
        return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

    finally:
        driver.switch_to.default_content()


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   CAPTCHA Scraper - Projet M2 MoSEF 2025-2026          ║
║   Université Paris 1 Panthéon-Sorbonne                  ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Create directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialize CSV
    if not os.path.exists('data/processed/metadata.csv'):
        with open('data/processed/metadata.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'url', 'timestamp'])
    
    print("1. Setup WebDriver")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    wait = WebDriverWait(driver, 20)
    print("2. WebDriver ready")

    # URLs to scrape
    urls = [
        "https://rutracker.org/forum/profile.php?mode=register",
        "https://2captcha.com/demo/normal",
    ]

    print("\n3. Starting CAPTCHA scraping")
    
    success_count = 0
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] Processing URL...")
        if scrape_captcha_from_url(driver, wait, url):
            success_count += 1

    print(f"\n{'='*60}")
    print("📊 SCRAPING SUMMARY")
    print(f"{'='*60}")
    print(f"URLs processed: {len(urls)}")
    print(f"CAPTCHAs found: {success_count}")
    print(f"Images saved in: data/raw/")
    print(f"Metadata saved in: data/processed/")
    print(f"{'='*60}")

    print("\n4. Closing browser")
    driver.quit()
    print("Browser closed")


if __name__ == "__main__":
    main()