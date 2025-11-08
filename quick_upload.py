"""
SIMPLEST Supabase Upload - Just run this!
Automatically uploads all your deals data to Supabase
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv

load_dotenv()

def quick_upload():
    """Upload ALL data from SQLite to Supabase - Simple & Fast"""
    
    print("="*60)
    print("🚀 Quick Upload to Supabase")
    print("="*60)
    
    # Check SQLite database
    db_path = 'output/deals.db'
    if not os.path.exists(db_path):
        print(f"\n❌ Database not found: {db_path}")
        return
    
    # Connect to SQLite
    print(f"\n📂 Reading from: {db_path}")
    sqlite_conn = sqlite3.connect(db_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Count deals
    sqlite_cursor.execute("SELECT COUNT(*) FROM deals")
    total = sqlite_cursor.fetchone()[0]
    print(f"✅ Found {total} deals in local database")
    
    # Get all deals
    sqlite_cursor.execute("SELECT * FROM deals")
    columns = [desc[0] for desc in sqlite_cursor.description]
    deals = sqlite_cursor.fetchall()
    sqlite_conn.close()
    
    # Connect to Supabase
    print("\n☁️  Connecting to Supabase...")
    try:
        supabase_conn = psycopg2.connect(
            host=os.getenv('SUPABASE_HOST'),
            port=os.getenv('SUPABASE_PORT', '5432'),
            database=os.getenv('SUPABASE_DATABASE', 'postgres'),
            user=os.getenv('SUPABASE_USER', 'postgres'),
            password=os.getenv('SUPABASE_PASSWORD')
        )
        print("✅ Connected to Supabase!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Check your .env file has correct Supabase credentials")
        return
    
    cursor = supabase_conn.cursor()
    
    # Prepare insert query
    insert_query = """
        INSERT INTO deals (
            title, link, description, image_url,
            price_text, price_numeric, original_price, discount_percent,
            rating, reviews_count, category, website,
            availability, in_stock, is_active, scraped_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (link) DO UPDATE SET
            title = EXCLUDED.title,
            price_numeric = EXCLUDED.price_numeric,
            discount_percent = EXCLUDED.discount_percent,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = NOW()
    """
    
    # Upload data
    print(f"\n🚀 Uploading {len(deals)} deals...")
    uploaded = 0
    
    for deal in deals:
        try:
            # Map SQLite columns to Supabase (skip id)
            values = (
                deal[1],  # title
                deal[2],  # link
                deal[9] if len(deal) > 9 else None,  # description
                deal[7] if len(deal) > 7 else None,  # image_url
                deal[3],  # price or price_text
                deal[5] if len(deal) > 5 else None,  # price_numeric
                deal[10] if len(deal) > 10 else None,  # original_price
                deal[11] if len(deal) > 11 else None,  # discount_percent
                deal[12] if len(deal) > 12 else None,  # rating
                deal[13] if len(deal) > 13 else 0,  # reviews_count
                deal[4] if len(deal) > 4 else 'Uncategorized',  # category
                deal[6] if len(deal) > 6 else 'slickdeals',  # website
                deal[14] if len(deal) > 14 else 'Unknown',  # availability
                bool(deal[15]) if len(deal) > 15 else True,  # in_stock
                bool(deal[16]) if len(deal) > 16 else True,  # is_active
                deal[17] if len(deal) > 17 else None  # scraped_at
            )
            
            cursor.execute(insert_query, values)
            uploaded += 1
            
            if uploaded % 100 == 0:
                print(f"   Progress: {uploaded}/{len(deals)}...")
                supabase_conn.commit()
        
        except Exception as e:
            if uploaded < 5:  # Show first few errors
                print(f"   ⚠️  Error: {str(e)[:60]}...")
    
    supabase_conn.commit()
    
    # Final stats
    print(f"\n✅ Upload complete! {uploaded} deals uploaded")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM deals")
    total_in_supabase = cursor.fetchone()[0]
    print(f"📊 Total deals in Supabase: {total_in_supabase}")
    
    cursor.execute("""
        SELECT website, COUNT(*) 
        FROM deals 
        GROUP BY website 
        ORDER BY COUNT(*) DESC
    """)
    
    print("\n📊 Deals by website:")
    for website, count in cursor.fetchall():
        print(f"   {website}: {count}")
    
    supabase_conn.close()
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Your data is now in Supabase!")
    print("="*60)
    print("\n🎯 View your data:")
    print("   https://supabase.com/dashboard/project/ouogccaijsagiwoywhaw/editor")
    print("\n🎯 Next: Update your code to use Supabase")
    print("   pipeline = DataPipeline(use_supabase=True)")

if __name__ == "__main__":
    try:
        quick_upload()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check .env file has Supabase credentials")
        print("2. Verify output/deals.db exists")
        print("3. Make sure you ran supabase_setup.sql first")
