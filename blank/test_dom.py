# Sources used :
# https://github.com/sarrabenyahia/tuto-webscraping/blob/main/selenium/tuto-intro2selenium/main.py
# https://selenium-python.readthedocs.io
# https://www.youtube.com/watch?v=NB8OceGZGjA
# https://docs.python.org/3/tutorial/classes.html
# https://python-course.readthedocs.io/projects/year1/en/latest/lessons/18-class.html#:~:text=Класс%20—%20шаблон%2C%20с%20помощью%20которого%20удобно%20описывать%20однотипные%20объекты.
# https://docs.python.org/3/library/csv.html
# https://www.youtube.com/watch?v=3mGZkmfrYIA&sttick=1

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

import os
print("CURRENT WORKING DIR:", os.getcwd())

def save_metadata_to_csv_json(file_name, url):
    # Save results in csv and json
    with open('data/processed/metadata.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([file_name, url])

    try:
        with open('data/processed/results.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = [] 

    result = {'url': url, 'file': file_name}
    data.append(result)

    with open('data/processed/results.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)


def scrape_captcha_from_url(driver, wait, url):
    # Navigation
    print(f"1. Opening: {url}")
    driver.get(url)
    print(f"Title: {driver.title}")

    # Finding elements by tag name & xpath
    try:
        # 1. Iframe handling
        print("Checking for iframes")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print("Iframe detected")
            driver.switch_to.frame(iframes[0])
        else:
            print("No iframe detected")

        # 2. Wait for visual elements
        print("Searching for visual elements")
        wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
        elements = driver.find_elements(By.XPATH, "//img | //canvas")
        print(f"Visual elements found: {len(elements)}")

        # 3. Heuristic CAPTCHA detection
        for el in elements:
            width = el.size["width"]
            height = el.size["height"]
            src = el.get_attribute("src") or ""

            print(f"Element size: {width}x{height}")

            if 100 < width < 400 and 40 < height < 150:
                if "logo" in src.lower() or "banner" in src.lower():
                    continue
                
                print(f"CAPTCHA candidate detected , size : {width}x{height}")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                
                path = f"data/raw/{filename}"

                el.screenshot(path)
                print(f"CAPTCHA saved: {path}")

                save_metadata_to_csv_json(filename, url)

                driver.switch_to.default_content()
                break
        else:
            print("No CAPTCHA detected on this page")

    except Exception as e:
        print("Error:", e)

    finally:
        driver.switch_to.default_content()


# =========================
# Main (STYLE PROF)
# =========================
def main():
    print("1. Setup WebDriver")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    wait = WebDriverWait(driver, 20)

    print("2. WebDriver ready")

    urls = [
        "https://rutracker.org/forum/profile.php?mode=register"
    print("3. Starting CAPTCHA scraping")

    for url in urls:
        scrape_captcha_from_url(driver, wait, url)

    print("4. Closing browser")
    driver.quit()
    print("Browser closed")


if __name__ == "__main__":
    main()