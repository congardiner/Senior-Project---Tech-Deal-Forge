"""
Gemini API Integration for Deal Analysis
Provides AI-powered descriptions and deal quality assessment
"""

import google.generativeai as genai
import os
from typing import Dict, Optional
import pandas as pd

class GeminiDealAnalyzer:
    """
    Analyze deals using Google's Gemini API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API
        
        Args:
            api_key: Your Gemini API key (or set GEMINI_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Either:\n"
                "1. Pass api_key parameter\n"
                "2. Set GEMINI_API_KEY environment variable\n"
                "Get your key at: https://makersuite.google.com/app/apikey"
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_deal_description(self, deal: Dict) -> str:
        """
        Generate AI description for a deal
        
        Args:
            deal: Dictionary with keys: title, price, category, original_price, etc.
        
        Returns:
            AI-generated description
        """
        prompt = f"""
        Analyze this tech deal and provide a concise, helpful description (2-3 sentences):
        
        Product: {deal.get('title', 'Unknown')}
        Price: {deal.get('price', 'N/A')}
        Original Price: {deal.get('original_price', 'N/A')}
        Category: {deal.get('category', 'Tech')}
        Rating: {deal.get('rating', 'N/A')}
        Reviews: {deal.get('reviews_count', 'N/A')}
        
        Focus on:
        - Key product features and use cases
        - Value proposition at this price
        - Who this deal is best for
        
        Keep it under 100 words and professional.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Description unavailable: {str(e)}"
    
    def assess_deal_quality(self, deal: Dict, historical_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Assess if a deal is worth buying
        
        Args:
            deal: Current deal information
            historical_data: Historical price data for comparison
        
        Returns:
            Dictionary with assessment and reasoning
        """
        # Prepare historical context
        historical_context = ""
        if historical_data is not None and not historical_data.empty:
            avg_price = historical_data['price_numeric'].mean()
            min_price = historical_data['price_numeric'].min()
            max_price = historical_data['price_numeric'].max()
            
            historical_context = f"""
            Historical Price Data:
            - Average: ${avg_price:.2f}
            - Lowest: ${min_price:.2f}
            - Highest: ${max_price:.2f}
            - Times seen: {len(historical_data)}
            """
        
        prompt = f"""
        Evaluate this tech deal and determine if it's worth buying:
        
        Product: {deal.get('title', 'Unknown')}
        Current Price: {deal.get('price_numeric', 'N/A')}
        Original Price: {deal.get('original_price', 'N/A')}
        Discount: {deal.get('discount_percent', 'N/A')}%
        Category: {deal.get('category', 'Tech')}
        Rating: {deal.get('rating', 'N/A')}
        Reviews: {deal.get('reviews_count', 'N/A')}
        
        {historical_context}
        
        Provide:
        1. Overall Assessment: BUY NOW / WAIT / SKIP (one word)
        2. Confidence: HIGH / MEDIUM / LOW
        3. Brief Reasoning (2-3 sentences)
        
        Format your response as:
        ASSESSMENT: [BUY NOW/WAIT/SKIP]
        CONFIDENCE: [HIGH/MEDIUM/LOW]
        REASONING: [Your reasoning here]
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse response
            lines = text.split('\n')
            assessment = "UNKNOWN"
            confidence = "UNKNOWN"
            reasoning = ""
            
            for line in lines:
                if line.startswith('ASSESSMENT:'):
                    assessment = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    confidence = line.split(':', 1)[1].strip()
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
            
            return {
                'assessment': assessment,
                'confidence': confidence,
                'reasoning': reasoning,
                'raw_response': text
            }
        
        except Exception as e:
            return {
                'assessment': 'ERROR',
                'confidence': 'N/A',
                'reasoning': f'Analysis failed: {str(e)}',
                'raw_response': ''
            }
    
    def predict_price_trend(self, deal: Dict, historical_data: pd.DataFrame) -> Dict:
        """
        Predict if price might drop in next 90 days based on historical patterns
        
        Args:
            deal: Current deal
            historical_data: Historical price data
        
        Returns:
            Prediction with reasoning
        """
        if historical_data.empty or len(historical_data) < 3:
            return {
                'prediction': 'INSUFFICIENT_DATA',
                'probability': 0,
                'reasoning': 'Not enough historical data for prediction'
            }
        
        # Calculate price statistics
        current_price = deal.get('price_numeric', 0)
        avg_price = historical_data['price_numeric'].mean()
        min_price = historical_data['price_numeric'].min()
        max_price = historical_data['price_numeric'].max()
        price_std = historical_data['price_numeric'].std()
        
        # Calculate recent trend (last 5 entries)
        recent_prices = historical_data.tail(5)['price_numeric'].tolist()
        
        prompt = f"""
        Predict if this product's price will drop in the next 90 days:
        
        Product: {deal.get('title', 'Unknown')}
        Current Price: ${current_price:.2f}
        
        Historical Analysis:
        - Average Price: ${avg_price:.2f}
        - Lowest Price: ${min_price:.2f}
        - Highest Price: ${max_price:.2f}
        - Price Volatility: ${price_std:.2f}
        - Recent Prices: {[f'${p:.2f}' for p in recent_prices]}
        - Number of Price Points: {len(historical_data)}
        
        Based on the data, predict:
        1. Will price drop? YES / NO / MAYBE
        2. Probability: [percentage]
        3. Reasoning: Why you think this (consider trends, volatility, current position vs avg)
        
        Format:
        PREDICTION: [YES/NO/MAYBE]
        PROBABILITY: [0-100]%
        REASONING: [Your analysis]
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse response
            lines = text.split('\n')
            prediction = "MAYBE"
            probability = 50
            reasoning = ""
            
            for line in lines:
                if line.startswith('PREDICTION:'):
                    prediction = line.split(':', 1)[1].strip()
                elif line.startswith('PROBABILITY:'):
                    prob_str = line.split(':', 1)[1].strip().replace('%', '')
                    try:
                        probability = int(prob_str)
                    except:
                        probability = 50
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
            
            return {
                'prediction': prediction,
                'probability': probability,
                'reasoning': reasoning,
                'raw_response': text
            }
        
        except Exception as e:
            return {
                'prediction': 'ERROR',
                'probability': 0,
                'reasoning': f'Prediction failed: {str(e)}',
                'raw_response': ''
            }
    
    def batch_analyze_deals(self, deals: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Analyze multiple deals and return ranked recommendations
        
        Args:
            deals: DataFrame of deals
            top_n: Number of top deals to analyze
        
        Returns:
            DataFrame with AI assessments
        """
        results = []
        
        for idx, deal in deals.head(top_n).iterrows():
            deal_dict = deal.to_dict()
            assessment = self.assess_deal_quality(deal_dict)
            
            results.append({
                'title': deal.get('title', ''),
                'price': deal.get('price_numeric', 0),
                'assessment': assessment['assessment'],
                'confidence': assessment['confidence'],
                'reasoning': assessment['reasoning']
            })
        
        return pd.DataFrame(results)


# Example usage functions
def analyze_deal_with_gemini(deal: Dict, api_key: str) -> Dict:
    """
    Quick function to analyze a single deal
    
    Args:
        deal: Deal dictionary
        api_key: Gemini API key
    
    Returns:
        Analysis results
    """
    analyzer = GeminiDealAnalyzer(api_key)
    
    return {
        'description': analyzer.generate_deal_description(deal),
        'assessment': analyzer.assess_deal_quality(deal)
    }


def get_deal_recommendation(deal: Dict, historical_data: pd.DataFrame, api_key: str) -> str:
    """
    Get a complete recommendation for a deal
    
    Args:
        deal: Current deal
        historical_data: Historical prices
        api_key: Gemini API key
    
    Returns:
        Formatted recommendation string
    """
    analyzer = GeminiDealAnalyzer(api_key)
    
    description = analyzer.generate_deal_description(deal)
    assessment = analyzer.assess_deal_quality(deal, historical_data)
    prediction = analyzer.predict_price_trend(deal, historical_data)
    
    recommendation = f"""
    DEAL ANALYSIS
    
    {description}
    
    RECOMMENDATION: {assessment['assessment']} (Confidence: {assessment['confidence']})
    {assessment['reasoning']}
    
    PRICE PREDICTION (90 days):
    {prediction['prediction']} - {prediction['probability']}% probability
    {prediction['reasoning']}
    """
    
    return recommendation


if __name__ == "__main__":
    # Example usage
    print("Gemini Deal Analyzer")
    print("-" * 60)
    print("\nSetup Instructions:")
    print("1. Get API key: https://makersuite.google.com/app/apikey")
    print("2. Set environment variable: GEMINI_API_KEY=your_key")
    print("3. Or pass api_key to GeminiDealAnalyzer()")
    print("\nInstall required package:")
    print("pip install google-generativeai")
