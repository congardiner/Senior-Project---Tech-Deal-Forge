from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify

CATEGORY_URLS = [
    "https://slickdeals.net/computer-deals/",
    "https://slickdeals.net/deals/tech/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/deals/unlocked-phones/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/laptop-deals/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/deals/computer-parts/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/deals/video-card/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/deals/processor/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/monitor-deals/",
    "https://slickdeals.net/deals/desktop/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
    "https://slickdeals.net/deals/tablet/?filters%5Brating%5D%5B%5D=popular&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D="
]



@browser(headless=True, reuse_driver=True)
def scrape_tech_deals_fixed(driver: Driver, data=None):
    all_deals = []

    for url in CATEGORY_URLS:
        print(f"Scraping: {url}")
        driver.get(url)
        driver.sleep(3) 

        # Now the content will be fully loaded and not just the initial HTML
        # Also waited with a sleep timer to ensure that cloudflare and other JS content loads
        # NOTE: Dynamic Site has now been figured out!
        
        html = driver.page_html
        soup = soupify(html)
        
        # Use the correct selector we discovered
        cards = soup.select('.bp-c-card')
        print(f"Found {len(cards)} cards on {url}")
        
        for card in cards:
            
            title_link = card.select_one('a[href*="/f/"]')
            if not title_link:
                title_link = card.find('a', href=True)
                
            if title_link:
                # This will look for text to extract
                href = title_link.get('href', '')
                
                # Title Extraction...
                title_text = ""
                
                # Method 1: Direct text
                direct_text = title_link.get_text(strip=True)
                
                # Method 2: From title attribute
                title_attr = title_link.get('title', '')
                
                # Method 3: From aria-label
                aria_label = title_link.get('aria-label', '')
                
                # Method 4: Extract from URL if needed (fallback)
                if href.startswith('/f/'):
                    url_parts = href.split('-', 1)
                    if len(url_parts) > 1:
                        url_title = url_parts[1].replace('-', ' ').title()
                    else:
                        url_title = ""
                else:
                    url_title = ""
                
                # Title Options Priority
                if title_attr and len(title_attr) > 5:
                    title_text = title_attr
                elif aria_label and len(aria_label) > 5:
                    title_text = aria_label
                elif direct_text and len(direct_text) > 5:
                    title_text = direct_text
                elif url_title and len(url_title) > 10:
                    title_text = url_title[:80]  
                else:
                    title_text = f"Deal from {href[:50]}"
                
                # Get price if available
                price_elem = card.select_one('.bp-p-dealCard_price')
                price = price_elem.get_text(strip=True) if price_elem else None
                
                # Only add deals with meaningful content
                if title_text and len(title_text) > 5:
                    deal = {
                        "category": url,
                        "title": title_text,
                        "price": price,
                        "link": href if href.startswith('http') else f"https://slickdeals.net{href}",
                    }
                    all_deals.append(deal)
                    print(f"Added deal: {title_text[:50]}... | {price}")




    print(f"Total deals found: {len(all_deals)}")
    return {
        "deals": all_deals,
        "total_count": len(all_deals)
    }

if __name__ == "__main__":
    result = scrape_tech_deals_fixed()
    print(f"\nScraping completed. Found {result['total_count']} deals.")
    for deal in result['deals'][:5]: 
        print(f"- {deal['title'][:60]}... | {deal['price']} | {deal['category']}")