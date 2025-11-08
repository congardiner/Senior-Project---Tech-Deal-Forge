"""
Streamlit Cloud Initialization Script
Handles database setup and sample data for cloud deployment
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

def init_cloud_database():
    """Initialize database with sample data for Streamlit Cloud"""
    
    db_path = Path("output/deals.db")
    db_path.parent.mkdir(exist_ok=True)
    
    # Check if database already has data
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deals")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✅ Database already initialized with {count} deals")
            return
    
    print("🔧 Initializing database for Streamlit Cloud...")
    
    # Create database schema
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT,
            link TEXT UNIQUE,
            category TEXT,
            price_text TEXT,
            price_numeric REAL,
            website TEXT DEFAULT 'slickdeals',
            image_url TEXT,
            description TEXT,
            discount_percent REAL,
            original_price REAL,
            rating REAL,
            reviews_count INTEGER,
            availability TEXT,
            in_stock BOOLEAN DEFAULT 1,
            is_active BOOLEAN DEFAULT 1,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Generate sample data
    sample_deals = generate_sample_deals()
    
    # Insert sample data
    for deal in sample_deals:
        conn.execute("""
            INSERT OR IGNORE INTO deals 
            (title, price_text, price_numeric, link, category, website, 
             discount_percent, original_price, rating, reviews_count, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deal['title'],
            deal['price_text'],
            deal['price_numeric'],
            deal['link'],
            deal['category'],
            deal['website'],
            deal['discount_percent'],
            deal['original_price'],
            deal['rating'],
            deal['reviews_count'],
            deal['scraped_at']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized with {len(sample_deals)} sample deals")

def generate_sample_deals(count=100):
    """Generate sample tech deals for demonstration"""
    
    categories = ['laptop', 'gaming', 'monitor', 'headphones', 'keyboard', 'mouse', 'webcam', 'storage']
    websites = ['slickdeals', 'bestbuy']
    
    products = {
        'laptop': [
            'Dell XPS 15 Laptop',
            'HP Pavilion Gaming Laptop',
            'Lenovo ThinkPad X1 Carbon',
            'ASUS ROG Gaming Laptop',
            'MacBook Air M2'
        ],
        'gaming': [
            'PlayStation 5 Console',
            'Xbox Series X',
            'Nintendo Switch OLED',
            'Gaming Controller Pro',
            'Gaming Headset RGB'
        ],
        'monitor': [
            '27" 4K Gaming Monitor',
            'Ultrawide Curved Monitor',
            'Dell 24" IPS Monitor',
            'ASUS Gaming Monitor 144Hz',
            'Samsung Odyssey G7'
        ],
        'headphones': [
            'Sony WH-1000XM5 Headphones',
            'Bose QuietComfort 45',
            'Apple AirPods Pro',
            'SteelSeries Gaming Headset',
            'Sennheiser HD 650'
        ],
        'keyboard': [
            'Mechanical Gaming Keyboard RGB',
            'Logitech MX Keys',
            'Corsair K95 RGB Platinum',
            'Razer BlackWidow V3',
            'Keychron K8 Wireless'
        ],
        'mouse': [
            'Logitech MX Master 3S',
            'Razer DeathAdder V3',
            'Logitech G502 HERO',
            'SteelSeries Rival 600',
            'Corsair M65 RGB'
        ],
        'webcam': [
            'Logitech C920 HD Webcam',
            'Razer Kiyo Pro',
            'Elgato Facecam',
            'Microsoft LifeCam Studio',
            'Logitech Brio 4K'
        ],
        'storage': [
            '1TB NVMe SSD',
            '2TB External Hard Drive',
            'Samsung 980 Pro SSD',
            'WD Black 4TB HDD',
            'SanDisk 512GB USB Flash Drive'
        ]
    }
    
    deals = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        category = random.choice(categories)
        product = random.choice(products[category])
        
        # Generate realistic price
        base_price = random.randint(50, 1500)
        discount = random.randint(10, 50)
        current_price = base_price * (1 - discount/100)
        
        # Generate date in last 30 days
        days_ago = random.randint(0, 30)
        scraped_date = base_date + timedelta(days=days_ago)
        
        deal = {
            'title': f"{product} - {random.choice(['On Sale', 'Limited Offer', 'Deal of the Day', 'Hot Deal'])}",
            'price_text': f"${current_price:.2f}",
            'price_numeric': current_price,
            'link': f"https://example.com/deal/{i}-{product.lower().replace(' ', '-')}",
            'category': category,
            'website': random.choice(websites),
            'discount_percent': discount,
            'original_price': base_price,
            'rating': round(random.uniform(3.5, 5.0), 1),
            'reviews_count': random.randint(50, 5000),
            'scraped_at': scraped_date.isoformat()
        }
        deals.append(deal)
    
    return deals

if __name__ == "__main__":
    init_cloud_database()
    print("🎉 Database ready for Streamlit Cloud deployment!")
