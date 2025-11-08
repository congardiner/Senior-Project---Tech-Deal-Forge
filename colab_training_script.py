"""
Google Colab ML Training Script
Upload this to Google Colab to train your deal predictor model

Steps:
1. Upload to Colab
2. Upload your deals CSV (from output folder)
3. Run all cells
4. Download the trained model
5. Place model in your project folder
"""

# ============================================
# CELL 1: Install dependencies (if needed)
# ============================================
# !pip install scikit-learn pandas joblib

# ============================================
# CELL 2: Upload data
# ============================================
from google.colab import files
import pandas as pd
import numpy as np

print("📁 Upload your deals CSV file:")
uploaded = files.upload()
filename = list(uploaded.keys())[0]
print(f"✅ Uploaded: {filename}")

# ============================================
# CELL 3: Load and prepare data
# ============================================
df = pd.read_csv(filename)
print(f"📊 Loaded {len(df)} deals")

# Data preparation function
def prepare_training_data(df):
    """Prepare features matching ml_integration.py"""
    
    # Clean numeric columns
    df['price_numeric'] = pd.to_numeric(df['price_numeric'], errors='coerce')
    df['discount_percent'] = pd.to_numeric(df['discount_percent'], errors='coerce').fillna(0)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
    df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce').fillna(0)
    
    # Website encoding
    df['website_bestbuy'] = (df['website'] == 'bestbuy').astype(int)
    df['website_slickdeals'] = (df['website'] == 'slickdeals').astype(int)
    df['website_newegg'] = (df['website'] == 'newegg').astype(int)
    
    # Category encoding (adjust based on YOUR categories)
    df['category_gaming'] = df['category'].str.contains('gaming|game', case=False, na=False).astype(int)
    df['category_laptop'] = df['category'].str.contains('laptop|notebook', case=False, na=False).astype(int)
    df['category_monitor'] = df['category'].str.contains('monitor|display', case=False, na=False).astype(int)
    df['category_electronics'] = df['category'].str.contains('electronics|tech', case=False, na=False).astype(int)
    
    # Temporal features
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    df['day_of_week'] = df['scraped_at'].dt.dayofweek
    df['month'] = df['scraped_at'].dt.month
    df['is_weekend'] = (df['scraped_at'].dt.dayofweek >= 5).astype(int)
    
    # Historical features (simple version - no lookback)
    df['price_vs_avg'] = 1.0
    df['price_vs_min'] = 1.0
    df['times_seen'] = 1
    df['price_std'] = 0
    df['recent_trend'] = 0
    
    # CREATE TARGET: Deal Quality Score (0-100)
    max_discount = df['discount_percent'].max() if df['discount_percent'].max() > 0 else 1
    
    df['deal_quality_score'] = (
        (df['discount_percent'] / max_discount * 40) +  # 40% weight on discount
        (df['rating'] / 5.0 * 30) +                     # 30% weight on rating
        (np.clip(df['reviews_count'], 0, 100) / 100 * 30)  # 30% weight on reviews
    )
    
    # Fill missing scores with median
    df['deal_quality_score'] = df['deal_quality_score'].fillna(df['deal_quality_score'].median())
    
    # Select features - MUST MATCH ml_integration.py prepare_features()
    feature_cols = [
        'price_numeric', 'discount_percent', 'rating', 'reviews_count',
        'website_bestbuy', 'website_slickdeals',
        'category_gaming', 'category_laptop', 'category_monitor',
        'day_of_week', 'month', 'is_weekend',
        'price_vs_avg', 'price_vs_min', 'times_seen', 'price_std', 'recent_trend'
    ]
    
    X = df[feature_cols].fillna(0)
    y = df['deal_quality_score']
    
    # Remove any rows with NaN in target
    valid_idx = ~y.isna()
    X = X[valid_idx]
    y = y[valid_idx]
    
    return X, y, feature_cols

# Prepare data
X, y, feature_names = prepare_training_data(df)
print(f"\n✅ Training data prepared:")
print(f"   - {X.shape[0]} deals")
print(f"   - {X.shape[1]} features")
print(f"   - Target range: {y.min():.1f} - {y.max():.1f}")
print(f"\n📋 Features: {feature_names}")

# ============================================
# CELL 4: Train the model
# ============================================
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"🔄 Training on {len(X_train)} deals, testing on {len(X_test)} deals...")

# Train Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

print(f"\n✅ Model trained successfully!")
print(f"📊 Performance Metrics:")
print(f"   - R² Score: {r2:.3f} (closer to 1.0 is better)")
print(f"   - RMSE: {rmse:.2f} points")
print(f"   - MAE: {mae:.2f} points")

# ============================================
# CELL 5: Feature importance
# ============================================
import matplotlib.pyplot as plt

# Feature importance
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🔍 Feature Importance:")
print(importance_df.to_string(index=False))

# Plot
plt.figure(figsize=(10, 6))
plt.barh(importance_df['feature'][:10], importance_df['importance'][:10])
plt.xlabel('Importance')
plt.title('Top 10 Most Important Features')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# ============================================
# CELL 6: Test predictions
# ============================================
# Test on a few examples
test_samples = X_test.head(5)
test_actuals = y_test.head(5)
test_predictions = model.predict(test_samples)

print("\n🎯 Sample Predictions:")
comparison = pd.DataFrame({
    'Actual Score': test_actuals.values,
    'Predicted Score': test_predictions,
    'Difference': test_predictions - test_actuals.values
})
print(comparison.to_string(index=False))

# ============================================
# CELL 7: Save and download model
# ============================================
import joblib
from datetime import datetime

# Save model
model_filename = f"deal_predictor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
joblib.dump(model, model_filename)

print(f"\n💾 Model saved: {model_filename}")
print(f"📊 Model info:")
print(f"   - Type: Random Forest Regressor")
print(f"   - Features: {len(feature_names)}")
print(f"   - R² Score: {r2:.3f}")

# Download the model
files.download(model_filename)

print("\n✅ TRAINING COMPLETE!")
print("\n📝 Next steps:")
print("1. Place downloaded model in your project folder")
print("2. Update streamlit_dashboard.py to use the model")
print(f"3. Model path: '{model_filename}'")
