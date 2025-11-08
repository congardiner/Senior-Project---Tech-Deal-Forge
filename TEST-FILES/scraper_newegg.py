from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from data_pipeline import DealsDataPipeline
import argparse
import json
import re
import time
import random
from datetime import datetime
from urllib.parse import urlparse, urljoin

# Newegg category URLs for different product types
CATEGORY_URLS = [
    "https://www.newegg.com/p/pl?d=graphics+cards&N=100007709",
    "https://www.newegg.com/p/pl?d=processors&N=100007671",
    "https://www.newegg.com/p/pl?d=laptops&N=100006740",
    "https://www.newegg.com/p/pl?d=motherboards&N=100007627", 
]


# URLs to exclude (promotional/ad links and non-products)
EXCLUDED_DOMAINS = [
    'adzerk.net',
    'doubleclick.net', 
    'googleadservices.com',
    'googlesyndication.com',
    'amazon-adsystem.com',
    'neweggbusiness.com',  
    'secure.newegg.com',  
]

# User agents for rotation to avoid detection (basic level - for rotating proxies)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

def should_exclude_link(url):
    """Check if a link should be excluded (promotional/ad links or non-products)"""
    if not url:
        return True
    
    # Check for excluded domains
    for domain in EXCLUDED_DOMAINS:
        if domain in url:
            return True
    
    # Newegg-specific exclusions
    if any(pattern in url.lower() for pattern in [
        '/help/', '/customer-service/', '/info/', '/contact/',
        '/account/', '/login/', '/register/', '/cart/',
        '/checkout/', '/warranty/', '/rebate/', '/promotion/',
        'javascript:', 'mailto:', '#', 'void(0)'
    ]):
        return True
    
    return False

def extract_newegg_price_details(price_container):
    """Extract detailed price information from Newegg's price structure"""
    if not price_container:
        return {
            'price_text': None,
            'price_numeric': None,
            'original_price': None,
            'discount_percent': None,
            'shipping_cost': None
        }
    
    # Newegg price selectors
    current_price = None
    original_price = None
    shipping_cost = None
    
    # Look for current price
    price_selectors = [
        '.price-current',
        '.item-price',
        '.price-was-data',
        '.price-save-percent',
        '.price'
    ]
    
    for selector in price_selectors:
        price_elem = price_container.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Extract numeric value
            price_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', price_text.replace(',', ''))
            if price_match:
                current_price = float(price_match.group(1))
                break
    
    # Look for original price (before discount)
    was_price_elem = price_container.select_one('.price-was')
    if was_price_elem:
        was_text = was_price_elem.get_text(strip=True)
        was_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', was_text.replace(',', ''))
        if was_match:
            original_price = float(was_match.group(1))
    
    # Look for shipping information
    shipping_elem = price_container.select_one('.price-ship, .shipping-text')
    if shipping_elem:
        shipping_text = shipping_elem.get_text(strip=True).lower()
        if 'free' in shipping_text:
            shipping_cost = 0.0
        else:
            shipping_match = re.search(r'\$?(\d+\.?\d*)', shipping_text)
            if shipping_match:
                shipping_cost = float(shipping_match.group(1))
    
    # Calculate discount percentage
    discount_percent = None
    if current_price and original_price and original_price > current_price:
        discount_percent = round(((original_price - current_price) / original_price) * 100, 1)
    
    # Look for explicit discount percentage
    if not discount_percent:
        discount_elem = price_container.select_one('.price-save-percent')
        if discount_elem:
            discount_text = discount_elem.get_text(strip=True)
            discount_match = re.search(r'(\d+)%', discount_text)
            if discount_match:
                discount_percent = float(discount_match.group(1))
    
    return {
        'price_text': f"${current_price:.2f}" if current_price else None,
        'price_numeric': current_price,
        'original_price': original_price,
        'discount_percent': discount_percent,
        'shipping_cost': shipping_cost
    }

def extract_newegg_rating_info(product_container):
    """Extract rating and review information from Newegg products"""
    rating = None
    reviews_count = None
    
    # Newegg uses specific rating selectors
    rating_selectors = [
        '.item-rating-num',
        '.rating-eggs',
        '.item-rating',
        '[data-rating]'
    ]
    
    for selector in rating_selectors:
        rating_elem = product_container.select_one(selector)
        if rating_elem:
            # Check for data attribute first
            if rating_elem.get('data-rating'):
                try:
                    rating = float(rating_elem.get('data-rating'))
                    break
                except (ValueError, TypeError):
                    pass
            
            # Extract from text
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                rating_value = float(rating_match.group(1))
                # Newegg typically uses 5-star or 5-egg rating
                if rating_value <= 5:
                    rating = rating_value
                    break
    
    # Look for review count
    review_selectors = [
        '.item-rating-num + a',
        '.item-review',
        '.rating-text',
        '[class*="review"]'
    ]
    
    for selector in review_selectors:
        review_elem = product_container.select_one(selector)
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            # Look for patterns like "(123)" or "123 reviews"
            review_match = re.search(r'(\d+)', review_text)
            if review_match:
                reviews_count = int(review_match.group(1))
                break
    
    return rating, reviews_count

def extract_newegg_specs(product_container):
    """Extract key product specifications"""
    specs = {}
    
    # Look for specification lists
    spec_selectors = [
        '.item-features li',
        '.item-info li', 
        '.product-bullets li',
        '.spec-list li'
    ]
    
    for selector in spec_selectors:
        spec_items = product_container.select(selector)
        for item in spec_items:
            spec_text = item.get_text(strip=True)
            if spec_text and ':' in spec_text:
                key, value = spec_text.split(':', 1)
                specs[key.strip()] = value.strip()
    
    return specs

def extract_newegg_availability(product_container):
    """Extract availability and stock information"""
    availability = None
    in_stock = False
    
    # Newegg availability selectors
    availability_selectors = [
        '.item-stock',
        '.availability',
        '.stock-info',
        '.item-promo'
    ]
    
    for selector in availability_selectors:
        avail_elem = product_container.select_one(selector)
        if avail_elem:
            avail_text = avail_elem.get_text(strip=True).lower()
            availability = avail_text
            
            # Determine if in stock
            if any(phrase in avail_text for phrase in ['in stock', 'available', 'ships today']):
                in_stock = True
            elif any(phrase in avail_text for phrase in ['out of stock', 'unavailable', 'discontinued']):
                in_stock = False
            break
    
    return availability, in_stock

def extract_rating_info(card):
    """Legacy function - redirects to Newegg-specific version"""
    return extract_newegg_rating_info(card)

def extract_image_url(card):
    """Extract product image URL from Newegg product cards"""
    # Newegg-specific image selectors
    img_selectors = [
        '.item-img img',
        '.item-container img',
        '.product-image img',
        'img[src*="neweggimages.com"]',
        'img[alt*="product"]'
    ]
    
    for selector in img_selectors:
        img = card.select_one(selector)
        if img and img.get('src'):
            src = img.get('src')
            # Handle relative URLs
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://www.newegg.com' + src
            
            # Ensure it's a valid image URL
            if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return src
    
    return None

def extract_description(card):
    """Extract product description from Newegg cards"""
    # Newegg description selectors
    desc_selectors = [
        '.item-title',
        '.item-info',
        '.product-title',
        '.item-features'
    ]
    
    for selector in desc_selectors:
        desc_elem = card.select_one(selector)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if desc_text and len(desc_text) > 10:
                # Limit description length and clean up
                desc_text = re.sub(r'\s+', ' ', desc_text)  # Remove extra whitespace
                return desc_text[:300] + '...' if len(desc_text) > 300 else desc_text
    
    return None

def get_category_from_url(url):
    """Extract clean category name from Newegg URL"""
    # Extract category from search parameter
    if 'd=' in url:
        category_match = re.search(r'd=([^&]+)', url)
        if category_match:
            category = category_match.group(1).replace('+', ' ')
            return category
    
    # Fallback to URL path analysis
    if 'graphics' in url.lower():
        return 'graphics-cards'
    elif 'processor' in url.lower() or 'cpu' in url.lower():
        return 'processors'
    elif 'laptop' in url.lower():
        return 'laptops'
    elif 'motherboard' in url.lower():
        return 'motherboards'
    elif 'memory' in url.lower() or 'ram' in url.lower():
        return 'memory'
    elif 'ssd' in url.lower():
        return 'storage'
    elif 'monitor' in url.lower():
        return 'monitors'
    elif 'power' in url.lower():
        return 'power-supplies'
    
    return 'tech-products'

def wait_with_jitter(base_seconds=2, jitter_range=1):
    """Add randomized delay to avoid detection"""
    delay = base_seconds + random.uniform(-jitter_range, jitter_range)
    time.sleep(max(0.5, delay))  # Minimum 0.5 second delay

@browser(headless=False, reuse_driver=True, user_agent=random.choice(USER_AGENTS))
def scrape_newegg_products_with_pipeline(driver: Driver, data=None):
    """Enhanced Newegg scraper handling dynamic content and anti-bot measures"""
    all_products = []
    excluded_count = 0

    for url in CATEGORY_URLS:
        print(f"🛒 Scraping Newegg: {url}")
        
        # Navigate with random delay
        driver.get(url)
        wait_with_jitter(3, 1)  # 2-4 second delay
        
        # Handle potential bot detection popup
        try:
            # Look for and handle any popups or bot challenges
            popup_selectors = ['.modal', '.popup', '.overlay', '#challenge-form']
            for selector in popup_selectors:
                popup = driver.get_element_or_none(selector)
                if popup:
                    print("⚠️ Detected popup/challenge - waiting...")
                    wait_with_jitter(5, 2)
                    break
        except Exception:
            pass
        
        # Scroll to load more products (Newegg uses lazy loading)
        print("📜 Scrolling to load dynamic content...")
        for i in range(3):  # Scroll 3 times
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_with_jitter(2, 0.5)
        
        # Wait for products to load
        driver.wait_for_element('.item-container, .item-cell', timeout=10)
        
        html = driver.page_html
        soup = soupify(html)
        
        # Newegg product card selectors (they use multiple layouts)
        product_selectors = [
            '.item-container',
            '.item-cell', 
            '.items-view .item',
            '.product-item'
        ]
        
        products = []
        for selector in product_selectors:
            products = soup.select(selector)
            if products:
                print(f"✅ Found {len(products)} products using selector: {selector}")
                break
        
        if not products:
            print(f"❌ No products found on {url}")
            continue

        for product in products:
            try:
                # Extract product title and link
                title_link = None
                title_selectors = [
                    '.item-title a',
                    '.item-info a',
                    'a.item-title',
                    'h3 a'
                ]
                
                for selector in title_selectors:
                    title_link = product.select_one(selector)
                    if title_link:
                        break
                
                if not title_link:
                    continue
                
                href = title_link.get('href', '')
                if should_exclude_link(href):
                    excluded_count += 1
                    continue
                
                # Extract title
                title_text = title_link.get_text(strip=True)
                if not title_text or len(title_text) < 5:
                    continue
                
                # Clean and validate title
                title_text = re.sub(r'\s+', ' ', title_text)  # Remove extra whitespace
                
                # Extract pricing information using Newegg-specific methods
                price_container = product.select_one('.item-price, .price-current-label')
                price_details = extract_newegg_price_details(price_container)
                
                # Extract rating and reviews
                rating, reviews_count = extract_newegg_rating_info(product)
                
                # Extract image URL
                image_url = extract_image_url(product)
                
                # Extract description
                description = extract_description(product)
                
                # Extract specifications
                specs = extract_newegg_specs(product)
                
                # Extract availability
                availability, in_stock = extract_newegg_availability(product)
                
                # Get category from URL
                category = get_category_from_url(url)
                
                # Create full URL
                full_link = href if href.startswith('http') else f"https://www.newegg.com{href}"
                
                # Create comprehensive product data
                product_data = {
                    'title': title_text,
                    'price_text': price_details['price_text'],
                    'price_numeric': price_details['price_numeric'],
                    'link': full_link,
                    'category': category,
                    'website': 'newegg',
                    'image_url': image_url,
                    'description': description,
                    'discount_percent': price_details['discount_percent'],
                    'original_price': price_details['original_price'],
                    'rating': rating,
                    'reviews_count': reviews_count,
                    'availability': availability,
                    'in_stock': in_stock,
                    'shipping_cost': price_details.get('shipping_cost'),
                    'specs': specs,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Only add products with meaningful content
                if title_text and len(title_text) > 5:
                    all_products.append(product_data)
                    
            except Exception as e:
                print(f"⚠️ Error processing product: {e}")
                continue
        
        # Random delay between pages
        wait_with_jitter(3, 1)

    print(f"🎉 Total Newegg products scraped: {len(all_products)}")
    print(f"🚫 Excluded non-product links: {excluded_count}")
    
    # Show data quality metrics
    products_with_prices = sum(1 for p in all_products if p['price_numeric'])
    products_with_images = sum(1 for p in all_products if p['image_url'])
    products_with_ratings = sum(1 for p in all_products if p['rating'])
    products_with_discounts = sum(1 for p in all_products if p['discount_percent'])
    
    print(f"📊 Data Quality:")
    print(f"   • With prices: {products_with_prices}/{len(all_products)} ({products_with_prices/len(all_products)*100:.1f}%)")
    print(f"   • With images: {products_with_images}/{len(all_products)} ({products_with_images/len(all_products)*100:.1f}%)")
    print(f"   • With ratings: {products_with_ratings}/{len(all_products)} ({products_with_ratings/len(all_products)*100:.1f}%)")
    print(f"   • With discounts: {products_with_discounts}/{len(all_products)} ({products_with_discounts/len(all_products)*100:.1f}%)")
    
    return all_products

def main():
    """Main function with command-line options for filtering and export"""
    parser = argparse.ArgumentParser(description='Scrape Newegg products and process with data pipeline')
    parser.add_argument('--min-price', type=float, help='Minimum price filter')
    parser.add_argument('--max-price', type=float, help='Maximum price filter')
    parser.add_argument('--keywords', nargs='+', help='Keywords to include')
    parser.add_argument('--exclude', nargs='+', help='Keywords to exclude')
    parser.add_argument('--format', choices=['csv', 'parquet', 'database', 'all'], 
                       default='all', help='Output format')
    parser.add_argument('--no-scrape', action='store_true', 
                       help='Skip scraping, use existing data')
    parser.add_argument('--in-stock-only', action='store_true',
                       help='Only include products that are in stock')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = DealsDataPipeline()
    
    # Get products data
    if args.no_scrape:
        # Load from existing file
        try:
            with open('output/newegg_products.json', 'r') as f:
                data = json.load(f)
                products = data.get('products', [])
            print(f"📦 Loaded {len(products)} products from existing file")
        except FileNotFoundError:
            print("❌ No existing data found. Running scraper...")
            products = scrape_newegg_products_with_pipeline()
    else:
        # Run scraper
        products = scrape_newegg_products_with_pipeline()
    
    if not products:
        print("❌ No products found!")
        return
    
    # Save raw data
    output_file = f"output/newegg_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({'products': products, 'scraped_at': datetime.now().isoformat()}, f, indent=2)
    print(f"💾 Raw data saved to: {output_file}")
    
    # Prepare filter arguments
    filter_args = {}
    if args.min_price is not None:
        filter_args['min_price'] = args.min_price
    if args.max_price is not None:
        filter_args['max_price'] = args.max_price
    if args.keywords:
        filter_args['keywords'] = args.keywords
    if args.exclude:
        filter_args['exclude_keywords'] = args.exclude
    
    # Filter for in-stock products if requested
    if args.in_stock_only:
        products = [p for p in products if p.get('in_stock', False)]
        print(f"🟢 Filtered to {len(products)} in-stock products")
    
    # Process products through pipeline
    print(f"\n🔄 Processing {len(products)} products through pipeline...")
    if filter_args:
        print(f"🔍 Applying filters: {filter_args}")
    
    results = pipeline.process_deals(products, **filter_args)
    
    # Display results
    print("\n=== 📊 PROCESSING RESULTS ===")
    summary = results['summary']
    print(f"📦 Total products processed: {summary['total_deals']}")
    print(f"💰 Products with prices: {summary['deals_with_prices']}")
    
    if summary['price_range']['min'] is not None:
        print(f"💵 Price range: ${summary['price_range']['min']:.2f} - ${summary['price_range']['max']:.2f}")
        print(f"📈 Average price: ${summary['price_range']['avg']:.2f}")
    
    print(f"📂 Categories: {summary['categories']}")
    
    # Show file locations
    if 'csv' in results:
        print(f"📄 CSV exported to: {results['csv']}")
    if 'parquet' in results:
        print(f"📄 Parquet exported to: {results['parquet']}")
    if 'database_rows_added' in results:
        print(f"🗄️ Database: Added {results['database_rows_added']} new rows")
    
    # Show sample products with enhanced information
    print(f"\n=== 🛍️ SAMPLE NEWEGG PRODUCTS ===")
    print(f"Showing up to 5 products after cleaning and filtering:")
    clean_df = pipeline.clean_data(products)
    if filter_args:
        clean_df = pipeline.filter_deals(clean_df, **filter_args)
    
    for i, (_, product) in enumerate(clean_df.head(5).iterrows()):
        price_str = f" | ${product['price_numeric']:.2f}" if product['price_numeric'] else " | No price"
        rating_str = f" | ⭐{product['rating']}" if product['rating'] else ""
        stock_str = " | 🟢 In Stock" if product.get('in_stock') else " | 🔴 Out of Stock" if product.get('in_stock') is False else ""
        
        print(f"{i+1}. {product['title'][:60]}...{price_str}{rating_str}{stock_str}")
        if product.get('specs'):
            specs_preview = list(product['specs'].items())[:2]  # Show first 2 specs
            for spec_key, spec_value in specs_preview:
                print(f"    • {spec_key}: {spec_value}")

if __name__ == "__main__":
    main()