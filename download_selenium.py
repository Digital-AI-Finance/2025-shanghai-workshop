"""
Download images from Google Sites using Selenium browser automation
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
from pathlib import Path

def download_with_selenium(url, output_dir, section_anchor="h.1z0x9146tw94"):
    """Use Selenium to load page and get image URLs with proper session"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    print("Starting Chrome browser...")
    driver = webdriver.Chrome(options=options)

    try:
        # Load the page
        full_url = f"{url}#{section_anchor}" if section_anchor else url
        print(f"Loading: {full_url}")
        driver.get(full_url)

        # Wait for images to load
        print("Waiting for page to load...")
        time.sleep(5)

        # Scroll down to load lazy images
        print("Scrolling to load all images...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Find all images
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"Found {len(images)} images on page")

        # Get cookies for session
        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        # Filter to googleusercontent images (the actual content images)
        google_images = []
        for img in images:
            src = img.get_attribute('src') or img.get_attribute('data-src')
            if src and 'googleusercontent.com' in src and 'sitesv' in src:
                google_images.append(src)

        print(f"Found {len(google_images)} Google content images")

        # Download each image
        downloaded = []
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Referer': url
        }

        for i, src in enumerate(google_images, 1):
            print(f"\nDownloading image {i}/{len(google_images)}...")
            print(f"  URL: {src[:80]}...")

            try:
                response = session.get(src, headers=headers, timeout=30)
                response.raise_for_status()

                # Determine extension
                content_type = response.headers.get('content-type', '')
                if 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'

                filename = f"shanghai_{i:02d}{ext}"
                filepath = output_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"  Saved: {filepath}")
                downloaded.append(filepath)

            except Exception as e:
                print(f"  Error: {e}")

            time.sleep(0.5)

        print(f"\n\nDownloaded {len(downloaded)} images to {output_dir}")
        return downloaded

    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.joergosterrieder.com/public-outreach"
    output = Path(__file__).parent / "static" / "images"
    download_with_selenium(url, output)
