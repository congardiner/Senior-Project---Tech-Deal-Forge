from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify

@browser(headless=True)
def test_simple_selectors(driver: Driver, data=None):
    """Test simple selectors on Slickdeals"""
    
    driver.get("https://slickdeals.net/computer-deals/")
    driver.sleep(2)
    
    html = driver.page_html
    soup = soupify(html)
    
    # Test basic element counts
    results = {
        "total_divs": len(soup.find_all('div')),
        "total_links": len(soup.find_all('a')),
        "fpItem_count": len(soup.select('.fpItem')),
        "dealItem_count": len(soup.select('.dealItem')),
        "threaditem_count": len(soup.select('[data-role="threaditem"]')),
        "page_title": soup.title.get_text() if soup.title else "No title"
    }
    
    # Look for any elements that might contain deal info
    potential_selectors = [
        'article',
        '.thread',
        '.dealTile', 
        '.bp-p-dealCard',
        '[data-testid*="deal"]'
    ]
    
    for selector in potential_selectors:
        count = len(soup.select(selector))
        results[f"{selector}_count"] = count
        if count > 0:
            print(f"Found {count} elements with selector: {selector}")
    
    return results

if __name__ == "__main__":
    result = test_simple_selectors()
    print("Results:", result)