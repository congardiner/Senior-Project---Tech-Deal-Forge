from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def analyze_deal_structure(request: Request, data=None):
    """Analyze the structure of deal cards on Slickdeals"""
    
    url = "https://slickdeals.net/computer-deals/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = request.get(url, headers=headers)
    soup = soupify(response)
    
    # Find deal cards
    cards = soup.select('.bp-c-card')
    print(f"Found {len(cards)} deal cards")
    
    deals = []
    
    for i, card in enumerate(cards[:3]):  # Analyze first 3 cards
        print(f"\n=== Card {i+1} ===")
        
        # Look for title/link
        title_selectors = ['a[href*="/deals/"]', '.bp-p-dealCard_title', 'h3', 'h4', '.title', 'a']
        title_element = None
        for selector in title_selectors:
            title_element = card.select_one(selector)
            if title_element:
                print(f"Title found with selector: {selector}")
                break
        
        # Look for price
        price_selectors = ['.price', '.bp-p-dealCard_price', '[data-testid*="price"]', '.cost']
        price_element = None
        for selector in price_selectors:
            price_element = card.select_one(selector)
            if price_element:
                print(f"Price found with selector: {selector}")
                break
        
        # Extract data
        if title_element:
            title = title_element.get_text(strip=True)
            link = title_element.get('href', '')
            print(f"Title: {title[:80]}...")
            print(f"Link: {link}")
            
            if price_element:
                price = price_element.get_text(strip=True)
                print(f"Price: {price}")
            else:
                print("Price: Not found")
                
            deals.append({
                "title": title,
                "link": link,
                "price": price_element.get_text(strip=True) if price_element else None
            })
        else:
            print("No title/link found")
            
        # Show the HTML structure for debugging
        print(f"Card HTML (first 200 chars): {str(card)[:200]}...")
    
    return {
        "total_cards": len(cards),
        "sample_deals": deals
    }

if __name__ == "__main__":
    result = analyze_deal_structure()
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total cards: {result['total_cards']}")
    for i, deal in enumerate(result['sample_deals']):
        print(f"Deal {i+1}: {deal['title'][:50]}... | {deal['price']} | {deal['link'][:50]}...")