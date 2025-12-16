import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_assessment_details(assessment):
    """Fetch duration from assessment detail page (optional)."""
    try:
        response = requests.get(assessment["url"], headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            sections = soup.find_all("div", class_="product-detail__section")
            for sec in sections:
                text = sec.text.lower()
                match = re.search(r'(\d+)\s*(min|minute)', text)
                if match:
                    assessment["duration"] = f"{match.group(1)} minutes"
                    break
    except Exception as e:
        print("Detail fetch error:", e)

    return assessment

def scrape_table(table):
    assessments = []
    rows = table.find_all("tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        name_tag = cols[0].find("a")
        if not name_tag:
            continue

        assessments.append({
            "name": name_tag.text.strip(),
            "url": "https://www.shl.com" + name_tag["href"],
            "duration": "N/A",
            "remote_testing": "Yes" if cols[1].find("span", class_="-yes") else "No",
            "adaptive_irt": "Yes" if cols[2].find("span", class_="-yes") else "No",
            "test_type": ", ".join(
                span.text.strip()
                for span in cols[3].find_all("span", class_="product-catalogue__key")
            )
        })

    return assessments

def scrape_individual_tests(max_pages=3):  # DEBUG MODE
    all_assessments = []

    print("🔍 Starting Individual Test Solutions scraping")

    for page in range(0, max_pages * 12, 12):
        url = f"{BASE_URL}?start={page}&type=1"
        print(f"➡ Fetching page: {url}")

        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print("❌ Failed page:", response.status_code)
            break

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        if not table:
            print("❌ No table found, stopping")
            break

        page_data = scrape_table(table)
        print(f"   ✓ Found {len(page_data)} assessments")

        all_assessments.extend(page_data)
        time.sleep(1)

    return all_assessments

def main():
    print("🚀 SHL SCRAPER STARTED")

    assessments = scrape_individual_tests(max_pages=32 )  # keep 3 for now
    print(f"📦 Total assessments collected: {len(assessments)}")

    print("🔍 Fetching duration details...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_assessment_details, a) for a in assessments]
        for i, _ in enumerate(as_completed(futures), 1):
            if i % 10 == 0:
                print(f"   Processed {i}/{len(assessments)}")

    df = pd.DataFrame(assessments)
    df.to_csv("shl_assessments.csv", index=False)
    print("✅ Saved shl_assessments.csv")

if __name__ == "__main__":
    main()
