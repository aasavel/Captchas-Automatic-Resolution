# Pipeline: page loading => captcha detection sur visible area/scrolling till detection => if not - scrolling till consent handling + rescrolling captcha => iframe checking => saving image, csv, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import csv
import json
import time
import pandas as pd


def save_metadata_to_csv_json(captchaname, url):
    # Save data about captcha to csv and json
    with open('data/processed/metadata.csv', 'a', newline='', encoding='utf-8') as captcha:
        writer = csv.writer(captcha)
        writer.writerow([captchaname, url])

    try:
        with open('data/processed/results.json', 'r', encoding='utf-8') as captcha:
            data = json.load(captcha)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []

    data.append({'url': url, 'captchaname': captchaname})

    with open('data/processed/results.json', 'w', encoding='utf-8') as captcha:
        json.dump(data, captcha, indent=2)


def find_captcha_in_elements(elements, context=''):
    # Find captcha in given elements
    for element in elements:
        try:
            width = element.size['width']
            height = element.size['height']
            src = (element.get_attribute('src') or '').lower()
            
            # Проверка размера (CAPTCHA обычно 100-400 x 40-150)
            if 100 < width < 400 and 40 < height < 150:
                # Пропустить логотипы и баннеры
                if "logo" in src or "banner" in src:
                    continue
                
                print(f"   ✓ CAPTCHA found {context}: {width}x{height}")
                return el
        except:
            continue
    return None


def try_click_consent_buttons(driver):
    """Пытается найти и нажать кнопки согласия (универсально)"""
    print("\n   → Searching for consent buttons...")
    
    # Скроллить вниз (кнопки обычно внизу)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    # Список селекторов для кнопок согласия
    consent_selectors = [
        # Русские сайты
        "//input[@value='Я согласен с этими правилами']",
        "//input[contains(@value, 'согласен')]",
        "//input[contains(@value, 'принимаю')]",
        "//button[contains(text(), 'Согласен')]",
        "//button[contains(text(), 'Принимаю')]",
        # Английские сайты
        "//button[contains(text(), 'Accept')]",
        "//button[contains(text(), 'Agree')]",
        "//button[contains(text(), 'I accept')]",
        "//button[contains(text(), 'I agree')]",
        "//input[contains(@value, 'Accept')]",
        "//input[contains(@value, 'Agree')]",
        "//a[contains(text(), 'Accept')]",
        "//a[contains(text(), 'Agree')]",
    ]
    
    for selector in consent_selectors:
        try:
            button = driver.find_element(By.XPATH, selector)
            if button.is_displayed():
                button.click()
                print(f"   ✓ Consent button clicked!")
                time.sleep(3)  # Ждать перезагрузки
                return True
        except:
            continue
    
    print("   ℹ No consent button found")
    return False


def scrape_captcha_from_url(driver, wait, url):
    """
    УНИВЕРСАЛЬНАЯ функция scraping с умной стратегией
    """
    print(f"\n{'='*60}")
    print(f"Opening: {url}")
    driver.get(url)
    time.sleep(2)
    print(f"Title: {driver.title}")
    
    captcha_element = None
    
    # ============================================
    # ШАГИ ПОИСКА
    # ============================================
    
    # ШАГ 1: Поиск на видимой части страницы
    print("\n[Step 1] Searching for CAPTCHA on visible area...")
    try:
        elements = driver.find_elements(By.XPATH, "//img | //canvas")
        print(f"   Found {len(elements)} visual elements")
        captcha_element = find_captcha_in_elements(elements, "on main page")
    except:
        pass
    
    # ШАГ 2: Если не нашли - скроллить и искать снова
    if not captcha_element:
        print("\n[Step 2] Scrolling down and searching again...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        
        try:
            elements = driver.find_elements(By.XPATH, "//img | //canvas")
            captcha_element = find_captcha_in_elements(elements, "after scroll")
        except:
            pass
    
    # ШАГ 3: Если не нашли - попробовать нажать согласие
    if not captcha_element:
        print("\n[Step 3] No CAPTCHA yet, trying consent buttons...")
        consent_clicked = try_click_consent_buttons(driver)
        
        if consent_clicked:
            # После согласия - искать снова
            print("\n[Step 3.1] Searching for CAPTCHA after consent...")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            try:
                elements = driver.find_elements(By.XPATH, "//img | //canvas")
                captcha_element = find_captcha_in_elements(elements, "after consent")
            except:
                pass
    
    # ШАГ 4: Если всё равно не нашли - проверить iframe
    if not captcha_element:
        print("\n[Step 4] Checking iframes...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        if iframes:
            print(f"   Found {len(iframes)} iframe(s)")
            
            for idx, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    time.sleep(1)
                    
                    elements = driver.find_elements(By.XPATH, "//img | //canvas")
                    captcha_element = find_captcha_in_elements(elements, f"in iframe {idx+1}")
                    
                    if captcha_element:
                        break
                    
                    driver.switch_to.default_content()
                except:
                    driver.switch_to.default_content()
                    continue
        else:
            print("   No iframes found")
    
    # ============================================
    # СОХРАНЕНИЕ CAPTCHA
    # ============================================
    
    if captcha_element:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captcha_{timestamp}.png"
            path = f"data/raw/{filename}"
            
            captcha_element.screenshot(path)
            print(f"\n✓ CAPTCHA SAVED: {path}")
            
            save_metadata(filename, url)
            
            driver.switch_to.default_content()
            return True
        except Exception as e:
            print(f"\n✗ Error saving CAPTCHA: {e}")
            driver.switch_to.default_content()
            return False
    else:
        print("\n⚠ NO CAPTCHA FOUND on this page")
        driver.switch_to.default_content()
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   CAPTCHA Scraper - Universal Version                   ║
║   Projet M2 MoSEF 2025-2026                             ║
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
    
    print("\n1. Setup WebDriver")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 20)
    print("2. WebDriver ready")

    # URLs для тестирования
    urls = [
        "https://solvecaptcha.com/demo/image-captcha",
        "https://2captcha.com/demo/normal",
        "https://rutracker.org/forum/profile.php?mode=register",
    ]

    print("\n3. Starting CAPTCHA scraping")
    
    success_count = 0
    for idx, url in enumerate(urls, 1):
        print(f"\n{'#'*60}")
        print(f"[{idx}/{len(urls)}] Processing URL")
        print(f"{'#'*60}")
        
        if scrape_captcha_from_url(driver, wait, url):
            success_count += 1
        
        time.sleep(1)  # Пауза между сайтами

    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"URLs processed: {len(urls)}")
    print(f"CAPTCHAs found: {success_count}")
    print(f"Success rate: {success_count}/{len(urls)}")
    print(f"Images saved in: data/raw/")
    print(f"Metadata saved in: data/processed/")
    print(f"{'='*60}")

    print("\n4. Closing browser")
    driver.quit()
    print("✓ Browser closed")


if __name__ == "__main__":
    main()