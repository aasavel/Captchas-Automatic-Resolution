# Sources used :
# https://github.com/sarrabenyahia/tuto-webscraping/blob/main/selenium/tuto-intro2selenium/main.py
# https://selenium-python.readthedocs.io
# https://python-course.readthedocs.io/projects/year1/en/latest/lessons/18-class.html#:~:text=Класс%20—%20шаблон%2C%20с%20помощью%20которого%20удобно%20описывать%20однотипные%20объекты.
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
    def __init__(self): # initializer
        options = webdriver.ChromeOptions() # Chrome as webdriver
        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        self.wait = WebDriverWait(self.driver, timeout)

        # Directories
        self.data_dir = "data"
        self.image_dir = os.path.join(self.data_dir, "raw")
        os.makedirs(self.image_dir, exist_ok=True)

        # Files
        self.meta_file = os.path.join(self.data_dir, "metadata.csv")
        self.json_file = os.path.join(self.data_dir, "results.json")

        # Init CSV
        if not os.path.exists(self.meta_file):
            with open(self.meta_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["filename", "url", "timestamp", "width", "height"])

        # Stats
        self.stats = {
            "pages_visited": 0,
            "captchas_collected": 0,
            "errors": 0
        }

    def collect_from_url(self, url):
        print(f"\nOpening page: {url}")
        self.stats["pages_visited"] += 1

        page_result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "captcha_found": False,
            "captcha_file": None
        }

        try:
            self.driver.get(url)

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "img"))
            )

            images = self.driver.find_elements(By.TAG_NAME, "img")
            captcha_img = None

            for img in images:
                src = (img.get_attribute("src") or "").lower()
                width = img.size.get("width", 0)
                height = img.size.get("height", 0)

                # Heuristic adapted for image CAPTCHA (excludes logo)
                if (
                    100 < width < 400
                    and 40 < height < 150
                    and "logo" not in src
                ):
                    captcha_img = img
                    break

            if captcha_img:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                filepath = os.path.join(self.image_dir, filename)

                print("Taking screenshot of CAPTCHA image...")
                captcha_img.screenshot(filepath)

                with open(self.meta_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([filename, url, timestamp, width, height])

                self.stats["captchas_collected"] += 1

                page_result["captcha_found"] = True
                page_result["captcha_file"] = filepath

                print(f"✓ CAPTCHA saved: {filepath}")

            else:
                print("⚠ No CAPTCHA detected on this page.")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            self.stats["errors"] += 1
            page_result["error"] = str(e)

        self._save_json(page_result)

    def _save_json(self, page_result):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"runs": []}

        data["runs"].append(page_result)

        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def close(self):
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DU SCRAPING")
        print("=" * 50)
        print(f"Pages visitées      : {self.stats['pages_visited']}")
        print(f"CAPTCHAs collectés  : {self.stats['captchas_collected']}")
        print(f"Erreurs rencontrées : {self.stats['errors']}")
        print("=" * 50)

        self.driver.quit()
        print("✓ Navigateur fermé\n")


def main():
    print("\n===Scraping with Selenium===")

    test_url = "https://solvecaptcha.com/demo/image-captcha"

    driver = CaptchaScraper()

    try:
        driver.collect_from_url(test_url)
    finally:
        driver.close()


if __name__ == "__main__":
    main()