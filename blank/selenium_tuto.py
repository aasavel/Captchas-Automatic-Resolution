# Sources used :
# https://github.com/sarrabenyahia/tuto-webscraping/blob/main/selenium/tuto-intro2selenium/main.py
# https://selenium-python.readthedocs.io
# https://www.youtube.com/watch?v=NB8OceGZGjA
# https://docs.python.org/3/tutorial/classes.html
# https://python-course.readthedocs.io/projects/year1/en/latest/lessons/18-class.html
# https://docs.python.org/3/library/csv.html
# https://www.youtube.com/watch?v=3mGZkmfrYIA&sttick=1

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os
import csv
import json
import time

print("CURRENT WORKING DIR:", os.getcwd())


def save_metadata_to_csv_json(file_name, url):
    # Save results in csv and json
    with open('data/processed/metadata.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([file_name, url])

    try:
        with open('data/processed/results.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        data = [] 

    result = {'url': url, 'file': file_name}
    data.append(result)

    with open('data/processed/results.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)


def scrape_captcha_from_url(driver, wait, url):
    # Navigation
    print(f"1. Opening: {url}")
    driver.get(url)
    time.sleep(2)  # Даем странице время загрузиться
    print(f"Title: {driver.title}")

    try:
        # 1. Сначала проверяем основную страницу
        print("Checking main page for visual elements")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
            elements = driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Visual elements found on main page: {len(elements)}")
            
            if check_and_save_captcha(driver, elements, url):
                return
        except TimeoutException:
            print("No visual elements on main page")

        # 2. Теперь проверяем iframes
        print("Checking for iframes")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
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
        
        print("No CAPTCHA detected on this page")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.switch_to.default_content()


def check_and_save_captcha(driver, elements, url):
    """Проверяет элементы и сохраняет капчу если найдена"""
    for el in elements:
        try:
            width = el.size["width"]
            height = el.size["height"]
            src = el.get_attribute("src") or ""

            print(f"Element size: {width}x{height}")

            if 100 < width < 400 and 40 < height < 150:
                if "logo" in src.lower() or "banner" in src.lower():
                    continue
                
                print(f"CAPTCHA candidate detected, size: {width}x{height}")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                
                path = f"data/raw/{filename}"

                el.screenshot(path)
                print(f"CAPTCHA saved: {path}")

                save_metadata_to_csv_json(filename, url)
                return True
                
        except Exception as e:
            print(f"Error checking element: {e}")
            continue
    
    return False


def main():
    print("1. Setup WebDriver")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    wait = WebDriverWait(driver, 10)  # Уменьшил до 10 секунд

    print("2. WebDriver ready")

    urls = [
       "https://rutracker.org/forum/profile.php?mode=register"
    ]

    print("3. Starting CAPTCHA scraping")

    for url in urls:
        scrape_captcha_from_url(driver, wait, url)

    print("4. Closing browser")
    driver.quit()
    print("Browser closed")


if __name__ == "__main__":
    main()