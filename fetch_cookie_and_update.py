# fetch_cookie_and_update.py
"""
This script fetches fresh cookies and API URL/headers for multiple pincodes from the Amul website using Selenium, and writes them to a GitHub Gist as a mapping.
Run this script every 2 hours (e.g., on Render, GitHub Actions, or your local machine).
"""
import json
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

GITHUB_TOKEN = os.environ.get("TOKEN_GITHUB")
GIST_ID = os.environ.get("GIST_ID")
GIST_FILENAME = os.environ.get("GIST_FILENAME", "api_url_and_headers.json")

# The base URL and JS to extract cookies/headers
BROWSE_URL_TEMPLATE = "https://shop.amul.com/en/browse/protein?pincode={pincode}"
API_URL_TEMPLATE = "https://shop.amul.com/api/1/entity/ms.products?...&filters[0][value][0]=protein...&substore={substore_id}"

# Helper to update the Gist
def update_gist(content):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "files": {
            GIST_FILENAME: {
                "content": content
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Gist updated successfully.")
    else:
        print(f"Failed to update Gist: {response.status_code} {response.text}")

# Use Selenium to get cookies, user-agent, and substore id for a pincode
def fetch_headers_for_pincode(pincode):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    # Set up logging for performance (network) logs
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options)
    try:
        url = f'https://shop.amul.com/en/browse/protein?pincode={pincode}'
        driver.get(url)
        time.sleep(5)  # Wait for page to load and cookies to be set
        cookies = driver.get_cookies()
        cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        # Get the actual API URL from network logs
        api_url = None
        logs = driver.get_log('performance')
        for entry in logs:
            msg = entry.get('message')
            if not msg:
                continue
            try:
                msg_json = json.loads(msg)
                params = msg_json.get('message', {}).get('params', {})
                request = params.get('request', {})
                url_candidate = request.get('url', '')
                if url_candidate.startswith('https://shop.amul.com/api/1/entity/ms.products'):
                    api_url = url_candidate
                    break
            except Exception:
                continue
        if not api_url:
            print(f"No API URL found for pincode {pincode}")
            return None
        return {"API_URL": api_url, "COOKIE": cookie_str}
    finally:
        driver.quit()

# Main function to loop over pincodes and update Gist
def main():
    # Load pincodes from pincodes.txt
    all_pincodes = []
    try:
        with open("pincodes.txt", "r", encoding="utf-8") as f:
            for line in f:
                pc = line.strip()
                if pc.isdigit() and len(pc) == 6:
                    all_pincodes.append(pc)
    except Exception as e:
        print(f"Could not read pincodes.txt: {e}")
    # Try to load current Gist content
    result = {}
    try:
        gist_url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        resp = requests.get(gist_url, headers=headers)
        if resp.status_code == 200:
            gist_data = resp.json()
            file_content = gist_data['files'].get(GIST_FILENAME, {}).get('content', '{}')
            result = json.loads(file_content)
    except Exception as e:
        print(f"Could not load current Gist content: {e}")
    for pincode in all_pincodes:
        print(f"Fetching headers for pincode {pincode}...")
        data = fetch_headers_for_pincode(pincode)
        if data:
            result[pincode] = data
            json_content = json.dumps(result, ensure_ascii=False, indent=2)
            update_gist(json_content)
            print(f"Updated Gist with data for pincode {pincode}.")
    if not result:
        print("No data fetched for any pincode.")

if __name__ == "__main__":
    main()
