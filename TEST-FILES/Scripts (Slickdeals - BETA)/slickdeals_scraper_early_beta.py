"""
Simple Multi-Website Scraper - Clean Version

# To be removed as this was apart of the test-and-compare exercise

"""

from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from data_pipeline import DealsDataPipeline
import logging
from typing import List, Dict, Any
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@browser(headless=True, reuse_driver=True)
def scrape_slickdeals(driver: Driver, data=None) -> Dict[str, Any]:
    """Scrape SlickDeals"""
    
    CATEGORY_URLS = [
        "https://slickdeals.net/computer-deals/",
        "https://slickdeals.net/deals/tech/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
        "https://slickdeals.net/laptop-deals/?filters%5Brating%5D%5B%5D=frontpage&filters%5Bprice%5D%5Bmin%5D=&filters%5Bprice%5D%5Bmax%5D=",
        "https://slickdeals.net/monitor-deals/",
    ]
    
    all_deals = []

    for url in CATEGORY_URLS:
        logger.info(f"Scraping SlickDeals: {url}")
        driver.get(url)
        driver.sleep(3)

        html = driver.page_html
        soup = soupify(html)
        
        cards = soup.select('.bp-c-card')
        logger.info(f"Found {len(cards)} cards on {url}")
        
        for card in cards:
            title_link = card.select_one('a[href*="/f/"]')
            if not title_link:
                title_link = card.find('a', href=True)
                
            if title_link:
                href = title_link.get('href', '')
                
                # Title extraction
                title_text = ""
                direct_text = title_link.get_text(strip=True)
                title_attr = title_link.get('title', '')
                aria_label = title_link.get('aria-label', '')
                
                if title_attr and len(title_attr) > 5:
                    title_text = title_attr
                elif aria_label and len(aria_label) > 5:
                    title_text = aria_label
                elif direct_text and len(direct_text) > 5:
                    title_text = direct_text
                else:
                    continue  # Skip if no good title
                
              
                price_elem = card.select_one('.bp-p-dealCard_price')
                price = price_elem.get_text(strip=True) if price_elem else None
                
           
                category = url.replace('https://slickdeals.net/', '').replace('/', '')
                if '?' in category:
                    category = category.split('?')[0]
                
                if title_text and len(title_text) > 5:
                    deal = {
                        "title": title_text,
                        "price": price,
                        "link": href if href.startswith('http') else f"https://slickdeals.net{href}",
                        "category": category,
                        "website": "slickdeals",
                        "scraped_at": datetime.now().isoformat()
                    }
                    all_deals.append(deal)

    logger.info(f"SlickDeals scraping completed: {len(all_deals)} deals found")
    
    return {
        "website": "slickdeals",
        "deals": all_deals,
        "total_count": len(all_deals),
        "success": True
    }




@browser(headless=True, reuse_driver=True) 
def scrape_newegg(driver: Driver, data=None) -> Dict[str, Any]:
    """Simple Newegg scraper"""
    
    TEST_URLS = [
        "https://www.newegg.com/promotions/specialoffer/16-1380"  # Shell Shocker deals
    ]
    
    all_deals = []
    
    for url in TEST_URLS:
        logger.info(f"Scraping Newegg: {url}")
        driver.get(url)
        driver.sleep(4)  # Newegg needs more time
        
        html = driver.page_html
        soup = soupify(html)
        
        # Try multiple selectors
        items = soup.select('.item-cell, .item-container, .list-item')
        logger.info(f"Found {len(items)} items on Newegg")
        
        for item in items[:10]:  # Limit to first 10
            # Find link
            link_elem = item.select_one('a[href*="/Product/Product.aspx"], a[href*="/p/"], .item-title a')
            if not link_elem:
                continue
                
            href = link_elem.get('href')
            if not href:
                continue
            
            # Get title
            title = link_elem.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            
            # Get price
            price_elem = item.select_one('.price-current, .item-price')
            price = price_elem.get_text(strip=True) if price_elem else None
            
            # Make absolute URL
            if not href.startswith('http'):
                href = f"https://www.newegg.com{href}"
            
            deal = {
                "title": title[:100],  # Limit length
                "price": price,
                "link": href,
                "category": "shell-shocker",
                "website": "newegg",
                "scraped_at": datetime.now().isoformat()
            }
            all_deals.append(deal)
    
    logger.info(f"Newegg scraping completed: {len(all_deals)} deals found")
    
    return {
        "website": "newegg", 
        "deals": all_deals,
        "total_count": len(all_deals),
        "success": len(all_deals) > 0
    }

def scrape_multiple_websites(websites: List[str] = None) -> Dict[str, Any]:
    """Scrape multiple websites and combine results"""
    
    if websites is None:
        websites = ['slickdeals']  # Default to safe option
    
    logger.info(f"Starting multi-website scrape: {websites}")
    
    all_deals = []
    website_results = {}
    
    # Available scrapers
    scrapers = {
        'slickdeals': scrape_slickdeals,
        'newegg': scrape_newegg
    }
    
    for website in websites:
        if website not in scrapers:
            logger.warning(f"Unknown website: {website}")
            continue
            
        logger.info(f"Starting {website} scraper...")
        result = scrapers[website]()
        
        if result and result.get('success', False):
            deals = result.get('deals', [])
            all_deals.extend(deals)
            website_results[website] = {
                'count': len(deals),
                'success': True
            }
            logger.info(f"✅ {website}: {len(deals)} deals")
        else:
            website_results[website] = {
                'count': 0,
                'success': False
            }
            logger.warning(f"❌ {website}: No deals found")
    
    # Generate summary
    summary = {
        'total_deals': len(all_deals),
        'websites_scraped': len(websites),
        'successful_websites': sum(1 for r in website_results.values() if r['success']),
        'by_website': website_results,
        'scraped_at': datetime.now().isoformat()
    }
    
    logger.info(f"Multi-website scrape completed: {len(all_deals)} total deals from {len(websites)} websites")
    
    return {
        'all_deals': all_deals,
        'summary': summary,
        'success': len(all_deals) > 0
    }

def scrape_and_save(websites: List[str] = None, **filters) -> Dict[str, Any]:
    """Complete pipeline: scrape multiple websites and save to database"""
    
    # Scrape data
    scrape_result = scrape_multiple_websites(websites)
    
    if not scrape_result['success']:
        return {
            'scraping': scrape_result,
            'pipeline': {'error': 'No deals scraped'},
            'success': False
        }
    
    # Process through data pipeline
    pipeline = DealsDataPipeline()
    pipeline_result = pipeline.process_deals(scrape_result['all_deals'], **filters)
    
    return {
        'scraping': scrape_result,
        'pipeline': pipeline_result,
        'success': True
    }

# Easy-to-use functions
def scrape_slickdeals_only():
    """Quick SlickDeals-only scrape"""
    return scrape_multiple_websites(['slickdeals'])

def scrape_all_websites():
    """Scrape all available websites"""
    return scrape_multiple_websites(['slickdeals', 'newegg'])

# Main execution
if __name__ == "__main__":
    print("🚀 MULTI-WEBSITE SCRAPER")
    print("=" * 40)
    
    # Test SlickDeals
    print("\nTesting SlickDeals...")
    result = scrape_slickdeals_only()
    print(f"✅ Found {result['summary']['total_deals']} deals")
    
    # Test complete pipeline
    print("\nTesting pipeline...")
    result = scrape_and_save(['slickdeals'])
    print(f"✅ Pipeline saved {result['pipeline'].get('database_rows_added', 0)} new deals")
    
    print("\n🎉 Scraper ready!")