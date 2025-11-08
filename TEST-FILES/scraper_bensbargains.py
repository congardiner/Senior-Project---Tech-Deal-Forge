from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from data_pipeline import DealsDataPipeline
from datetime import datetime
import pandas as pd

BENSBARGAINS_URLS = [
    "https://bensbargains.com/c/desktop-computers/",
    "https://bensbargains.com/c/laptops/",
    "https://bensbargains.com/c/wireless-headphones/",
    "https://bensbargains.com/c/tablets/",
    "https://bensbargains.com/c/cpus/",
    "https://bensbargains.com/c/smartphones/",
    "https://bensbargains.com/c/tvs/",
    "https://bensbargains.com/c/motherboards/"
]

@browser(headless=True, reuse_driver=True)
def scrape_bensbargains(driver: Driver, data=None):
    deals = []
    for url in BENSBARGAINS_URLS:
        category = url.split('/')[-2] if url.split('/')[-2] else "deals"
        print(f"Scraping {url}")
        driver.get(url)
        driver.sleep(5)  # Wait longer for JS to load
        
        # Scroll down to trigger lazy loading
        driver.scroll_to_bottom()
        driver.sleep(2)
        
        soup = soupify(driver.page_html)
        
        # Get ALL links on the page
        all_links = soup.select("a[href]")
        print(f"Found {len(all_links)} total links on page")
        
        for link_elem in all_links:
            link = link_elem.get("href", "")
            if not link:
                continue
            
            if link.startswith("/"):
                link = "https://bensbargains.com" + link
            
            
            # Must be a bensbargains deal link
            if "bensbargains.com" not in link:
                continue
            
            title = link_elem.get_text(strip=True)
            if len(title) < 15:  # Skip short text like "Read More"
                continue
            
            deal = {
                "title": title,
                "price": None,
                "price_text": None,
                "price_numeric": None,
                "link": link,
                "category": category,
                "website": "bensbargains",
                "image_url": None,
                "description": None,
                "discount_percent": None,
                "original_price": None,
                "rating": None,
                "reviews_count": None,
                "scraped_at": datetime.now().isoformat(),
            }
            deals.append(deal)
            print(f"  ✅ {title[:50]}...")
    
    return deals

if __name__ == "__main__":
    print("🔍 Scraping BensBargains...")
    deals = scrape_bensbargains()
    
    if not deals:
        print("No deals found")
    else:
        print(f"Scraped {len(deals)} deals")
        
     
        pipeline = DealsDataPipeline(use_mysql=False)
     
        results = pipeline.process_deals(deals)
        

        print()
        print(f"\n Results:")
        print(f"   CSV: {results['csv']}")
        print(f"   MySQL: Added {results['database_rows_added']} new deals")
        print(f"   Total deals: {results['summary']['total_deals']}")
        print(f"\n Data saved to CSV + MySQL!")
        print()
