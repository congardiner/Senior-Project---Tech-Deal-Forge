"""
Simple ML Data Preparation Script
Consolidates all deal data into a single CSV for machine learning training
"""

import pandas as pd
import mysql.connector
from mysql_config import MYSQL_CONFIG
from datetime import datetime
from pathlib import Path

def load_all_deals_from_mysql():
    """Load all deals from MySQL database"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    
    query = """
    SELECT 
        d.id,
        d.title,
        d.link,
        d.description,
        d.price_numeric,
        d.original_price,
        d.discount_percent,
        d.rating,
        d.reviews_count,
        d.in_stock,
        d.scraped_at,
        w.name as website,
        c.name as category
    FROM deals d
    LEFT JOIN websites w ON d.website_id = w.id
    LEFT JOIN categories c ON d.category_id = c.id
    WHERE d.is_active = TRUE
    ORDER BY d.scraped_at DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"✅ Loaded {len(df)} deals from MySQL")
    return df

def create_ml_features(df):
    """Create ML features from raw data"""
    print("🔧 Engineering features...")
    
    # Convert scraped_at to datetime
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    
    # Temporal features
    df['hour'] = df['scraped_at'].dt.hour
    df['day_of_week'] = df['scraped_at'].dt.dayofweek
    df['month'] = df['scraped_at'].dt.month
    
    # Text features
    df['title_length'] = df['title'].str.len()
    df['has_description'] = df['description'].notna().astype(int)
    
    # Price features
    df['has_discount'] = (df['discount_percent'] > 0).astype(int)
    df['has_rating'] = (df['rating'] > 0).astype(int)
    df['high_rating'] = (df['rating'] >= 4.0).astype(int)
    
    # Fill missing values
    df['price_numeric'] = df['price_numeric'].fillna(0)
    df['discount_percent'] = df['discount_percent'].fillna(0)
    df['rating'] = df['rating'].fillna(0)
    df['reviews_count'] = df['reviews_count'].fillna(0)
    
    # Categorical encoding
    df['website_encoded'] = pd.Categorical(df['website']).codes
    df['category_encoded'] = pd.Categorical(df['category']).codes
    
    # Target variable: Deal Quality Score (0-100)
    df['deal_quality_score'] = (
        (df['discount_percent'] / df['discount_percent'].max() * 40) +
        (df['rating'] / 5.0 * 30) +
        (df['reviews_count'].clip(0, 100) / 100 * 30)
    ).fillna(0)
    
    print(f"✅ Created {len([col for col in df.columns if col not in ['id', 'title', 'link', 'description', 'scraped_at']])} features")
    return df

def save_ml_dataset(df):
    """Save ML-ready dataset"""
    output_dir = Path("output/ml_data")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save complete dataset
    complete_file = output_dir / f"ml_dataset_{timestamp}.csv"
    df.to_csv(complete_file, index=False)
    print(f"✅ Complete dataset: {complete_file}")
    
    # Save feature matrix only (for training)
    feature_cols = [
        'price_numeric', 'discount_percent', 'rating', 'reviews_count',
        'title_length', 'has_description', 'has_discount', 'has_rating', 'high_rating',
        'hour', 'day_of_week', 'month', 'website_encoded', 'category_encoded',
        'deal_quality_score'  # Target variable
    ]
    
    features_df = df[feature_cols]
    features_file = output_dir / f"ml_features_{timestamp}.csv"
    features_df.to_csv(features_file, index=False)
    print(f"✅ Feature matrix: {features_file}")
    
    # Print summary
    print(f"\n📊 ML Dataset Summary:")
    print(f"   Total records: {len(df):,}")
    print(f"   Date range: {df['scraped_at'].min()} to {df['scraped_at'].max()}")
    print(f"   Websites: {df['website'].nunique()}")
    print(f"   Categories: {df['category'].nunique()}")
    print(f"   Avg deal quality: {df['deal_quality_score'].mean():.2f}")
    
    return complete_file, features_file

def main():
    """Main ML data preparation pipeline"""
    print("🤖 Preparing ML Dataset from MySQL...")
    print("=" * 60)
    
    # Load data
    df = load_all_deals_from_mysql()
    
    if df.empty:
        print("❌ No data found in MySQL database")
        return
    
    # Create features
    df = create_ml_features(df)
    
    # Save datasets
    complete_file, features_file = save_ml_dataset(df)
    
    print("\n🎉 ML data preparation complete!")
    print(f"\n📥 Upload {features_file} to Google Colab or your ML environment")

if __name__ == "__main__":
    main()
