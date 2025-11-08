from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def test_slickdeals_request(request: Request, data=None):
    """Test scraping Slickdeals using requests instead of browser"""
    
    url = "https://slickdeals.net/computer-deals/"
    print(f"Requesting: {url}")
    
    # Add headers to look more like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = request.get(url, headers=headers)
    soup = soupify(response)
    
    print(f"Status code: {response.status_code}")
    print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
    
    # Test various selectors
    selectors_to_test = [
        '.fpItem',
        '.dealItem', 
        '.threadItem',
        '[data-role="threaditem"]',
        'article',
        '.deal-tile',
        '.bp-c-card',
        '.thread'
    ]
    
    results = {}
    for selector in selectors_to_test:
        elements = soup.select(selector)
        count = len(elements)
        results[selector] = count
        print(f"{selector}: {count} elements")
        
        if count > 0 and count <= 3:  # Show details for first few elements
            for i, elem in enumerate(elements[:2]):
                print(f"  Element {i+1} classes: {elem.get('class', [])}")
                text = elem.get_text(strip=True)[:100]
                print(f"  Element {i+1} text: {text}")
    
    # Look for any deal-related content
    deal_links = soup.find_all('a', href=True)
    deal_count = len([link for link in deal_links if '/deals/' in link.get('href', '')])
    print(f"Links with '/deals/' in href: {deal_count}")
    
    return {
        "status_code": response.status_code,
        "selectors": results,
        "deal_links": deal_count
    }

if __name__ == "__main__":
    result = test_slickdeals_request()
    print(f"\nFinal result: {result}")