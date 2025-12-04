"""
Download images from a Google Sites webpage
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import time

def download_google_site(url, output_dir):
    """Download all images from a Google Sites page"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print(f"Fetching page: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all images
    images = soup.find_all('img')
    print(f"Found {len(images)} images")

    downloaded = []
    for i, img in enumerate(images, 1):
        src = img.get('src') or img.get('data-src')
        if not src:
            continue

        # Skip small icons/logos
        if 'googleusercontent.com' not in src:
            continue

        # Make URL absolute
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            src = 'https://www.joergosterrieder.com' + src

        print(f"\nDownloading image {i}: {src[:80]}...")

        try:
            img_response = requests.get(src, headers=headers, timeout=30)
            img_response.raise_for_status()

            # Determine extension
            content_type = img_response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'

            filename = f"image_{i:02d}{ext}"
            filepath = output_dir / filename

            with open(filepath, 'wb') as f:
                f.write(img_response.content)

            print(f"  Saved: {filepath}")
            downloaded.append(filepath)
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n\nDownloaded {len(downloaded)} images to {output_dir}")
    return downloaded

if __name__ == "__main__":
    url = "https://www.joergosterrieder.com/public-outreach"
    output = Path(__file__).parent / "static" / "images"
    download_google_site(url, output)
