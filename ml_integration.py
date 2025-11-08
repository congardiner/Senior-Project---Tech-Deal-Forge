"""
ML Model Integration for Deal Prediction
Connect your Google Colab trained model to Streamlit dashboard
"""

import pandas as pd
import numpy as np
import pickle
import joblib
import requests
from typing import Dict, Optional, Tuple
import sqlite3
from datetime import datetime, timedelta

class MLDealPredictor:
    """
    Load and use ML model trained in Google Colab
    Supports multiple model formats and prediction types
    """
    
    def __init__(self, model_path: str, model_type: str = 'sklearn'):
        """
        Initialize ML predictor
        
        Args:
            model_path: Path to saved model file (.pkl, .joblib, or URL)
            model_type: Type of model ('sklearn', 'tensorflow', 'pytorch', 'xgboost')
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_columns = None
        
        self.load_model()
    
    def load_model(self):
        """Load model from file or URL"""
        try:
            # If URL, download first
            if self.model_path.startswith('http'):
                print(f"Downloading model from {self.model_path}")
                response = requests.get(self.model_path)
                
                if self.model_path.endswith('.pkl'):
                    self.model = pickle.loads(response.content)
                elif self.model_path.endswith('.joblib'):
                    import io
                    self.model = joblib.load(io.BytesIO(response.content))
            else:
                # Load from local file
                if self.model_path.endswith('.pkl'):
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                elif self.model_path.endswith('.joblib'):
                    self.model = joblib.load(self.model_path)
            
            print(f"Model loaded successfully: {type(self.model).__name__}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def load_scaler(self, scaler_path: str):
        """Load separate scaler if needed"""
        try:
            if scaler_path.endswith('.pkl'):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            elif scaler_path.endswith('.joblib'):
                self.scaler = joblib.load(scaler_path)
            
            print("Scaler loaded successfully")
        except Exception as e:
            print(f"Error loading scaler: {e}")
    
    def prepare_features(self, deal: Dict, historical_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Prepare features for ML model
        Match the features you used in Google Colab training
        
        Args:
            deal: Current deal data
            historical_data: Historical prices for feature engineering
        
        Returns:
            DataFrame with features ready for prediction
        """
        features = {}
        
        # Basic features
        features['price_numeric'] = deal.get('price_numeric', 0)
        features['discount_percent'] = deal.get('discount_percent', 0)
        
        # Rating features
        rating_str = deal.get('rating', '0')
        try:
            features['rating'] = float(str(rating_str).split()[0]) if rating_str else 0
        except:
            features['rating'] = 0
        
        # Review count
        reviews = deal.get('reviews_count', '0')
        try:
            features['reviews_count'] = int(str(reviews).replace(',', '')) if reviews else 0
        except:
            features['reviews_count'] = 0
        
        # Categorical encoding (you may need to adjust based on your training)
        website = deal.get('website', 'unknown')
        features['website_bestbuy'] = 1 if website == 'bestbuy' else 0
        features['website_slickdeals'] = 1 if website == 'slickdeals' else 0
        
        category = deal.get('category', 'unknown')
        features['category_gaming'] = 1 if 'gaming' in category.lower() else 0
        features['category_laptop'] = 1 if 'laptop' in category.lower() else 0
        features['category_monitor'] = 1 if 'monitor' in category.lower() else 0
        
        # Temporal features
        now = datetime.now()
        features['day_of_week'] = now.weekday()
        features['month'] = now.month
        features['is_weekend'] = 1 if now.weekday() >= 5 else 0
        
        # Historical features (if available)
        if historical_data is not None and not historical_data.empty:
            features['price_vs_avg'] = deal.get('price_numeric', 0) / historical_data['price_numeric'].mean()
            features['price_vs_min'] = deal.get('price_numeric', 0) / historical_data['price_numeric'].min()
            features['times_seen'] = len(historical_data)
            
            # Price volatility
            features['price_std'] = historical_data['price_numeric'].std()
            
            # Recent trend (last 5 entries)
            if len(historical_data) >= 5:
                recent = historical_data.tail(5)['price_numeric']
                features['recent_trend'] = (recent.iloc[-1] - recent.iloc[0]) / recent.iloc[0]
            else:
                features['recent_trend'] = 0
        else:
            features['price_vs_avg'] = 1.0
            features['price_vs_min'] = 1.0
            features['times_seen'] = 1
            features['price_std'] = 0
            features['recent_trend'] = 0
        
        return pd.DataFrame([features])
    
    def predict_deal_quality(self, deal: Dict, historical_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Predict if deal is good/bad
        
        Returns:
            Dictionary with prediction and probability
        """
        try:
            # Prepare features
            X = self.prepare_features(deal, historical_data)
            
            # Scale if scaler exists
            if self.scaler:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
            
            # Make prediction
            if hasattr(self.model, 'predict_proba'):
                # Classification model with probabilities
                probabilities = self.model.predict_proba(X_scaled)[0]
                prediction = self.model.predict(X_scaled)[0]
                confidence = max(probabilities) * 100
                
                return {
                    'prediction': 'GOOD_DEAL' if prediction == 1 else 'BAD_DEAL',
                    'confidence': confidence,
                    'probability_good': probabilities[1] * 100 if len(probabilities) > 1 else 0,
                    'probability_bad': probabilities[0] * 100 if len(probabilities) > 1 else 0
                }
            else:
                # Regression or simple classification
                prediction = self.model.predict(X_scaled)[0]
                
                return {
                    'prediction': prediction,
                    'confidence': 75.0,  # Default confidence
                    'score': float(prediction)
                }
        
        except Exception as e:
            return {
                'prediction': 'ERROR',
                'confidence': 0,
                'error': str(e)
            }
    
    def predict_price_drop(self, deal: Dict, historical_data: pd.DataFrame, days: int = 90) -> Dict:
        """
        Predict if price will drop in next N days
        
        Args:
            deal: Current deal
            historical_data: Historical price data
            days: Number of days to predict ahead
        
        Returns:
            Prediction with probability
        """
        try:
            # Prepare features
            X = self.prepare_features(deal, historical_data)
            
            # Scale if needed
            if self.scaler:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
            
            # Predict
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(X_scaled)[0]
                will_drop = probabilities[1] * 100  # Probability of price drop
                
                # Estimate amount of drop based on historical volatility
                if not historical_data.empty:
                    price_std = historical_data['price_numeric'].std()
                    current_price = deal.get('price_numeric', 0)
                    estimated_drop = price_std * 0.5  # Conservative estimate
                else:
                    estimated_drop = 0
                
                return {
                    'will_drop': will_drop > 50,
                    'probability': will_drop,
                    'estimated_drop_amount': estimated_drop,
                    'estimated_new_price': current_price - estimated_drop if will_drop > 50 else current_price,
                    'recommendation': 'WAIT' if will_drop > 60 else 'BUY NOW'
                }
            else:
                # Regression model - predict future price directly
                predicted_price = self.model.predict(X_scaled)[0]
                current_price = deal.get('price_numeric', 0)
                
                will_drop = predicted_price < current_price
                drop_amount = current_price - predicted_price
                probability = min(abs(drop_amount / current_price * 100), 100)
                
                return {
                    'will_drop': will_drop,
                    'probability': probability,
                    'estimated_drop_amount': drop_amount if will_drop else 0,
                    'estimated_new_price': predicted_price,
                    'recommendation': 'WAIT' if will_drop and drop_amount > current_price * 0.1 else 'BUY NOW'
                }
        
        except Exception as e:
            return {
                'will_drop': False,
                'probability': 0,
                'error': str(e),
                'recommendation': 'UNABLE_TO_PREDICT'
            }
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance if model supports it"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importance = self.model.feature_importances_
                feature_names = self.feature_columns if self.feature_columns else [f'feature_{i}' for i in range(len(importance))]
                
                df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                return df
            else:
                return pd.DataFrame({'message': ['Feature importance not available for this model']})
        except Exception as e:
            return pd.DataFrame({'error': [str(e)]})


def load_historical_data(deal_link: str, db_path: str = 'output/deals.db') -> pd.DataFrame:
    """
    Load historical data for a specific deal from SQLite
    
    Args:
        deal_link: URL of the deal
        db_path: Path to SQLite database
    
    Returns:
        DataFrame with historical prices
    """
    try:
        conn = sqlite3.connect(db_path)
        
        query = """
            SELECT price_numeric, scraped_at, discount_percent, rating, reviews_count
            FROM deals
            WHERE link = ?
            ORDER BY scraped_at ASC
        """
        
        df = pd.read_sql_query(query, conn, params=[deal_link])
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
        
        conn.close()
        
        return df
    
    except Exception as e:
        print(f"Error loading historical data: {e}")
        return pd.DataFrame()


# Example integration with Streamlit
def get_ml_recommendation(deal: Dict, model_path: str, db_path: str = 'output/deals.db') -> Dict:
    """
    Get complete ML-based recommendation for a deal
    
    Args:
        deal: Deal dictionary
        model_path: Path to trained model
        db_path: Path to database
    
    Returns:
        Complete recommendation
    """
    try:
        # Load model
        predictor = MLDealPredictor(model_path)
        
        # Load historical data
        historical = load_historical_data(deal.get('link', ''), db_path)
        
        # Get predictions
        quality = predictor.predict_deal_quality(deal, historical)
        price_drop = predictor.predict_price_drop(deal, historical)
        
        return {
            'deal_quality': quality,
            'price_prediction': price_drop,
            'historical_data_points': len(historical),
            'model_type': predictor.model_type
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'deal_quality': {'prediction': 'UNKNOWN'},
            'price_prediction': {'will_drop': False, 'probability': 0}
        }


if __name__ == "__main__":
    print("ML Deal Predictor")
    print("-" * 60)
    print("\nHow to use your Google Colab model:")
    print("\n1. Export model from Colab:")
    print("   ```python")
    print("   import joblib")
    print("   joblib.dump(model, 'deal_predictor_model.joblib')")
    print("   from google.colab import files")
    print("   files.download('deal_predictor_model.joblib')")
    print("   ```")
    print("\n2. Place model in project folder")
    print("\n3. Use in Streamlit:")
    print("   ```python")
    print("   predictor = MLDealPredictor('deal_predictor_model.joblib')")
    print("   result = predictor.predict_deal_quality(deal)")
    print("   ```")
