from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime
import pandas as pd

print("CURRENT WORKING DIR:", os.getcwd())


def save_metadata_to_csv_json(file_name, url, width, height, detection_method):
    """Save metadata to CSV and JSON files"""
    # Save to CSV
    with open('data/processed/metadata.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([file_name, url, width, height, detection_method, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    
    # Save to JSON
    try:
        with open('data/processed/results.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        data = [] 
    
    result = {
        'url': url, 
        'file': file_name,
        'width': width,
        'height': height,
        'detection_method': detection_method,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(result)
    
    with open('data/processed/results.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)


def check_and_save_captcha(driver, elements, url):
    """Check elements and save CAPTCHA if found"""
    captcha_keywords = ["captcha", "verify", "code", "challenge", "kcaptcha", "securimage", "cap_code"]
    recaptcha_keywords = ["recaptcha", "grecaptcha"]
    skip_keywords = ["logo", "banner", "icon", "avatar", "button"]
    
    for el in elements:
        try:
            width = el.size["width"]
            height = el.size["height"]
            
            # Get all attributes
            src = (el.get_attribute("src") or "").lower()
            alt = (el.get_attribute("alt") or "").lower()
            class_name = (el.get_attribute("class") or "").lower()
            id_attr = (el.get_attribute("id") or "").lower()
            name = (el.get_attribute("name") or "").lower()
            
            print(f"Element size: {width}x{height}")
            if src:
                print(f"  src: {src[:100]}")
            if class_name:
                print(f"  class: {class_name}")
            if id_attr:
                print(f"  id: {id_attr}")
            if name:
                print(f"  name: {name}")
            
            # Combine all attributes for checking
            all_attrs = f"{src} {alt} {class_name} {id_attr} {name}"
            
            # Check if it contains CAPTCHA keywords
            has_captcha = any(keyword in all_attrs for keyword in captcha_keywords)
            is_recaptcha = any(keyword in all_attrs for keyword in recaptcha_keywords)
            should_skip = any(keyword in all_attrs for keyword in skip_keywords)
            
            # Skip if it's reCAPTCHA or too small or should skip
            if is_recaptcha or width < 50 or height < 20:
                continue
            
            # Skip if contains logo/banner/etc
            if should_skip and not has_captcha:
                print(f"  → Skipping (detected as: {[k for k in skip_keywords if k in all_attrs]})")
                continue
            
            # Method 1: CAPTCHA keyword found
            if has_captcha:
                print(f"✓ CAPTCHA detected by keyword, size: {width}x{height}")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                path = f"data/raw/{filename}"
                
                el.screenshot(path)
                print(f"CAPTCHA saved: {path}")
                save_metadata_to_csv_json(filename, url, width, height, "keyword")
                return True
            
            # Method 2: Size-based detection for typical CAPTCHA dimensions
            # RuTracker CAPTCHA is around 150-200px wide, 50-80px tall
            # Being more specific to avoid false positives
            if (100 < width < 400 and 40 < height < 150) and not should_skip:
                print(f"✓ CAPTCHA candidate by size: {width}x{height}")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                path = f"data/raw/{filename}"
                
                el.screenshot(path)
                print(f"CAPTCHA saved: {path}")
                save_metadata_to_csv_json(filename, url, width, height, "size")
                return True
                
        except Exception as e:
            print(f"Error checking element: {e}")
            continue
    
    return False


def scrape_captcha_from_url(driver, wait, url):
    """Main scraping function for a given URL"""
    print(f"1. Opening: {url}")
    driver.get(url)
    time.sleep(3)  # Give page time to load
    print(f"Title: {driver.title}")
    
    try:
        # Scroll down to load all content
        print("\nScrolling page to load all content...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Check main page first
        print("\nChecking main page for visual elements")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
            elements = driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Visual elements found on main page: {len(elements)}")
            
            if check_and_save_captcha(driver, elements, url):
                return
        except TimeoutException:
            print("No visual elements on main page")
        
        # Check inside forms specifically (CAPTCHAs are often in forms)
        print("\nChecking inside forms...")
        try:
            forms = driver.find_elements(By.TAG_NAME, "form")
            print(f"Forms found: {len(forms)}")
            
            for idx, form in enumerate(forms, 1):
                print(f"Checking form {idx}/{len(forms)}")
                form_elements = form.find_elements(By.XPATH, ".//img | .//canvas")
                print(f"  Visual elements in form: {len(form_elements)}")
                
                if check_and_save_captcha(driver, form_elements, url):
                    return
        except Exception as e:
            print(f"Error checking forms: {e}")
        
        # Check iframes
        print("\nChecking for iframes")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        if not iframes:
            print("No iframes found")
        
        for i, iframe in enumerate(iframes):
            try:
                print(f"Checking iframe {i+1}/{len(iframes)}")
                driver.switch_to.frame(iframe)
                time.sleep(1)
                
                elements = driver.find_elements(By.XPATH, "//img | //canvas")
                print(f"Visual elements found in iframe: {len(elements)}")
                
                if check_and_save_captcha(driver, elements, url):
                    driver.switch_to.default_content()
                    return
                
                driver.switch_to.default_content()
            except Exception as e:
                print(f"Error in iframe {i+1}: {e}")
                driver.switch_to.default_content()
        
        print("\n⚠ No CAPTCHA detected on this page")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.switch_to.default_content()


def main():
    """Main function to run the scraper"""
    print("="*60)
    print("CAPTCHA Web Scraper - M2 MoSEF 2025-2026")
    print("="*60)
    
    # Create directories if they don't exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialize CSV with headers if it doesn't exist
    if not os.path.exists('data/processed/metadata.csv'):
        with open('data/processed/metadata.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['filename', 'url', 'width', 'height', 'detection_method', 'timestamp'])
    
    print("\n1. Setup WebDriver")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    wait = WebDriverWait(driver, 10)
    print("2. WebDriver ready")
    
    # Test URLs
    urls = [
        "https://rutracker.org/forum/profile.php?mode=register"
    ]
    
    print("\n3. Starting CAPTCHA scraping")
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] Processing URL...")
        scrape_captcha_from_url(driver, wait, url)
    
    print("\n4. Closing browser")
    driver.quit()
    print("Browser closed")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SCRAPING SUMMARY")
    print("="*60)
    try:
        with open('data/processed/results.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Total CAPTCHAs collected: {len(data)}")
            print(f"Images saved in: data/raw/")
            print(f"Metadata saved in: data/processed/metadata.csv")
            print(f"Results saved in: data/processed/results.json")
    except:
        print("No CAPTCHAs collected in this session")
    print("="*60)


if __name__ == "__main__":
    main()


# Sources used :
# https://github.com/sarrabenyahia/tuto-webscraping/blob/main/selenium/tuto-intro2selenium/main.py
# https://selenium-python.readthedocs.io
# https://www.youtube.com/watch?v=NB8OceGZGjA
# https://docs.python.org/3/tutorial/classes.html
# https://python-course.readthedocs.io/projects/year1/en/latest/lessons/18-class.html
# https://docs.python.org/3/library/csv.html
# https://www.youtube.com/watch?v=3mGZkmfrYIA&sttick=1

