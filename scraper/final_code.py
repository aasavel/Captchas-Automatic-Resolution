# Sources used :
# https://github.com/sarrabenyahia/tuto-webscraping/blob/main/selenium/tuto-intro2selenium/main.py
# https://selenium-python.readthedocs.io
# https://www.youtube.com/watch?v=NB8OceGZGjA
# https://docs.python.org/3/tutorial/classes.html
# https://python-course.readthedocs.io/projects/year1/en/latest/lessons/18-class.html#:~:text=Класс%20—%20шаблон%2C%20с%20помощью%20которого%20удобно%20описывать%20однотипные%20объекты.
# https://docs.python.org/3/library/csv.html
# https://www.youtube.com/watch?v=3mGZkmfrYIA&sttick=1

from selenium import webdriver
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


class CaptchaScraper:
    # Setup Chrome WebDriver
    def __init__(self):
        # Create browser
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 20)
        
        # Paths settings
        self.image = "data/raw"
        self.csv = "data/metadata.csv"
        self.json = "data/results.json"

        if os.path.exists(self.csv):
            pass
        else:
            with open(self.csv, 'w', newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile)
                writer.writerow(['filename', 'url'])

    def scrape_and_save(self, url):
        print("1. Opening your url")
        self.driver.get(url)

        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            images = self.driver.find_elements(By.TAG_NAME, "img")

            for img in images:
                width = img.size["width"]
                height = img.size["height"]
                src = img.get_attribute("src") or ""

                # Very simple heuristic
                if 100 < width < 400 and 40 < height < 150 and "logo" not in src:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"captcha_{timestamp}.png"
                    path = os.path.join(self.image_dir, filename)

                    img.screenshot(path)

                    print("CAPTCHA saved:", path)

                    # Save CSV
                    with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([filename, url, timestamp])

                    # Save JSON
                    result = {
                        "url": url,
                        "timestamp": timestamp,
                        "file": path
                    }

                    if os.path.exists(self.json_file):
                        with open(self.json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    else:
                        data = []

                    data.append(result)

                    with open(self.json_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

                    return

            print("No CAPTCHA found")

        except Exception as e:
            print("Error:", e)

    def close(self):
        self.driver.quit()
        print("Browser closed")


def main():
    url = "https://solvecaptcha.com/demo/image-captcha" # using this as demo -> will change with api

    scraper = CaptchaScraper()
    scraper.scrape(url)
    scraper.close()
#https://nopecha.com/captcha/textcaptcha

if __name__ == "__main__":
    main()