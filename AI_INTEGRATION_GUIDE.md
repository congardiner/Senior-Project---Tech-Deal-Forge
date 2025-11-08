# AI/ML Integration Guide

Complete guide to add AI-powered insights to your Streamlit dashboard.

## 🎯 Two Options

### Option 1: Gemini AI (Easier - No Training Required)
- Real-time AI analysis
- Natural language descriptions
- Deal quality assessment
- Price trend predictions

### Option 2: Custom ML Model (More Accurate - Requires Training)
- Train on YOUR historical data
- Personalized predictions
- Offline (no API calls)
- Full control

**You can use BOTH for comprehensive insights!**

---

## 🔧 Setup Instructions

### Prerequisites

```powershell
# Install required packages
pip install google-generativeai scikit-learn joblib streamlit plotly pandas numpy
```

---

## 📝 Option 1: Gemini AI Setup

### Step 1: Get API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your API key

### Step 2: Add to Environment

**Option A: Environment Variable (Recommended)**
```powershell
# Add to your system environment variables
$env:GEMINI_API_KEY="your_api_key_here"
```

**Option B: Enter in Streamlit Sidebar**
- Just paste key in sidebar when running dashboard

### Step 3: Test Gemini Integration

```python
# Test script
from gemini_integration import GeminiDealAnalyzer

analyzer = GeminiDealAnalyzer("your_api_key_here")

test_deal = {
    'title': 'Samsung 55" OLED TV',
    'price_numeric': 899.99,
    'original_price': 1499.99,
    'discount_percent': 40,
    'category': 'TVs',
    'website': 'Best Buy',
    'rating': 4.5,
    'reviews_count': 1234
}

# Get AI description
description = analyzer.generate_deal_description(test_deal)
print(description)

# Get deal assessment
assessment = analyzer.assess_deal_quality(test_deal)
print(f"\nAssessment: {assessment['assessment']}")
print(f"Confidence: {assessment['confidence']}")
print(f"Reasoning: {assessment['reasoning']}")
```

---

## 🤖 Option 2: ML Model Setup

### Step 1: Prepare Data for Colab

1. Copy your `deals.db` SQLite database
2. Upload to Google Drive

### Step 2: Train Model in Google Colab

1. Open Google Colab: https://colab.research.google.com
2. Create new notebook
3. Copy contents from `train_model_colab.py`
4. Upload your `deals.db`
5. Run all cells (takes 5-10 minutes)

**What the training does:**
- Loads your historical data
- Engineers 18+ features
- Trains classification model (good vs bad deals)
- Trains regression model (price drop predictions)
- Evaluates performance
- Saves models as .joblib files

### Step 3: Download Models

After training completes, download these files:
- `deal_quality_classifier.joblib`
- `price_drop_predictor.joblib`
- `feature_scaler.joblib`
- `feature_names.txt`

### Step 4: Add Models to Project

```
botasaurus-project/
├── models/
│   ├── deal_quality_classifier.joblib
│   ├── price_drop_predictor.joblib
│   ├── feature_scaler.joblib
│   └── feature_names.txt
├── streamlit_ai_components.py
├── gemini_integration.py
├── ml_integration.py
└── streamlit_dashboard.py
```

### Step 5: Test ML Integration

```python
# Test script
from ml_integration import MLDealPredictor, get_ml_recommendation

test_deal = {
    'title': 'Samsung 55" OLED TV',
    'price_numeric': 899.99,
    'original_price': 1499.99,
    'discount_percent': 40,
    'category': 'TVs',
    'website': 'Best Buy',
    'rating': 4.5,
    'reviews_count': 1234,
    'link': 'https://bestbuy.com/...'
}

result = get_ml_recommendation(test_deal, 'models/deal_quality_classifier.joblib')

print(f"Deal Quality: {result['deal_quality']['prediction']}")
print(f"Confidence: {result['deal_quality']['confidence']:.1f}%")
print(f"Will drop? {result['price_prediction']['will_drop']}")
print(f"Drop probability: {result['price_prediction']['probability']:.0f}%")
```

---

## 🎨 Integrate with Streamlit Dashboard

### Quick Integration (5 minutes)

Add to your existing `streamlit_dashboard.py`:

```python
# At the top, add imports
from streamlit_ai_components import (
    add_ai_sidebar_controls,
    display_ai_deal_card,
    display_ai_insights_summary,
    display_price_prediction_dashboard
)

# In your main() function, add:
def main():
    st.title("🎯 Tech Deals Dashboard")
    
    # Add AI controls to sidebar
    ai_config = add_ai_sidebar_controls()
    
    # Load your deals
    df = load_deals()  # Your existing function
    
    # Add AI Insights section
    if st.sidebar.checkbox("🤖 Show AI Insights", value=True):
        display_ai_insights_summary(df, ai_config)
    
    # Add Price Predictions
    if st.sidebar.checkbox("📊 Show Price Predictions"):
        if ai_config.get('ml_model_path'):
            display_price_prediction_dashboard(df, ai_config['ml_model_path'])
        else:
            st.warning("Upload ML model in sidebar to see predictions")
    
    # Enhanced deal cards
    st.header("📦 All Deals")
    for _, deal in df.iterrows():
        display_ai_deal_card(
            deal,
            gemini_api_key=ai_config.get('gemini_api_key'),
            ml_model_path=ai_config.get('ml_model_path')
        )
```

### What You Get:

**Sidebar Controls:**
- Gemini API key input
- ML model upload
- Configuration status

**Deal Cards with AI Tabs:**
- 📝 Details (existing info)
- 🤖 AI Analysis (Gemini descriptions & recommendations)
- 📊 ML Prediction (trained model predictions)
- 📈 History (price timeline)

**AI Insights Summary:**
- Top 5 deals analyzed
- BUY NOW / WAIT / SKIP recommendations
- Confidence scores
- Reasoning explanations

**Price Prediction Dashboard:**
- Analyzes 20+ deals
- Shows drop probability
- Recommends buy timing
- Visual charts

---

## 🧪 Testing Your Setup

### Test 1: Check Imports

```python
import streamlit as st
from streamlit_ai_components import add_ai_sidebar_controls
from gemini_integration import GeminiDealAnalyzer
from ml_integration import MLDealPredictor

print("✅ All imports successful!")
```

### Test 2: Gemini API

```powershell
python -c "from gemini_integration import GeminiDealAnalyzer; print(GeminiDealAnalyzer('test').api_key)"
```

### Test 3: ML Model

```python
from ml_integration import MLDealPredictor
import os

if os.path.exists('models/deal_quality_classifier.joblib'):
    predictor = MLDealPredictor('models/deal_quality_classifier.joblib')
    print("✅ ML model loaded!")
else:
    print("❌ Model not found. Train in Colab first.")
```

### Test 4: Run Dashboard

```powershell
streamlit run streamlit_dashboard.py
```

---

## 📊 Expected Performance

### Gemini AI:
- **Response Time:** 1-3 seconds per deal
- **Cost:** ~$0.001 per analysis (very cheap)
- **Accuracy:** High for descriptions, moderate for predictions
- **Best For:** Rich descriptions, user-friendly recommendations

### ML Model:
- **Response Time:** <0.1 seconds per deal (instant)
- **Cost:** Free after training
- **Accuracy:** Depends on your data (typically 70-85%)
- **Best For:** Fast predictions, offline use, personalized to YOUR deals

---

## 🎯 Usage Tips

### When to Use Gemini:
- Want detailed product descriptions
- Need natural language explanations
- Don't have enough historical data yet
- Want quick setup without training

### When to Use ML Model:
- Have 500+ historical data points
- Want fast, offline predictions
- Need consistent predictions
- Want full control over algorithm

### Use BOTH for Best Results:
- Gemini for descriptions & reasoning
- ML model for accurate predictions
- Compare outputs for confidence
- Show both to users for transparency

---

## 🚀 Advanced Features

### Custom Prompts (Gemini)

Edit `gemini_integration.py` to customize:
- Description style (technical vs casual)
- Assessment criteria (aggressive vs conservative)
- Prediction timeframes (30, 60, 90 days)

### Model Tuning (ML)

Edit `train_model_colab.py` to:
- Adjust feature engineering
- Try different algorithms
- Tune hyperparameters
- Add custom scoring

### Batch Processing

```python
# Analyze 100 deals at once
from gemini_integration import GeminiDealAnalyzer

analyzer = GeminiDealAnalyzer(api_key)
results = analyzer.batch_analyze_deals(df.head(100))

for result in results:
    print(f"{result['title']}: {result['recommendation']}")
```

---

## 🐛 Troubleshooting

### "Module not found: google.generativeai"
```powershell
pip install google-generativeai
```

### "Invalid API key"
- Check key at: https://makersuite.google.com/app/apikey
- Make sure no extra spaces
- Try regenerating key

### "ML model not loading"
- Check file exists: `models/deal_quality_classifier.joblib`
- Ensure trained in Colab first
- Check sklearn version matches (pip install scikit-learn==1.3.0)

### "Not enough historical data"
- Need 2+ price points per product
- Run scrapers daily for a week
- ML works best with 500+ data points

### "Predictions seem wrong"
- Retrain model with more data
- Check feature engineering
- Verify data quality in SQLite

---

## 📈 Next Steps

1. **Start Simple**: Get Gemini working first (5 mins)
2. **Collect Data**: Run scrapers daily for 1-2 weeks
3. **Train Model**: Use Colab when you have 500+ entries
4. **Compare**: See which gives better recommendations
5. **Refine**: Adjust prompts and features based on results

---

## 💡 Example Use Cases

### Use Case 1: Deal Hunter
- User browses deals in dashboard
- Clicks "AI Analysis" on interesting deal
- Gemini explains if it's a good value
- ML predicts if price will drop
- User decides to buy now or wait

### Use Case 2: Price Tracker
- User tracks specific product
- ML predicts 80% chance of price drop
- User sets alert
- Price drops after 2 weeks
- User gets notified and purchases

### Use Case 3: Budget Planning
- User wants new laptop
- AI analyzes 50 laptop deals
- Shows top 5 best values
- Predicts Black Friday drops
- User plans purchase timing

---

## 📞 Need Help?

Common questions:

**Q: Do I need both Gemini AND ML?**
A: No! Start with Gemini (easier). Add ML later for better predictions.

**Q: How much does Gemini cost?**
A: Very cheap (~$0.001 per deal analysis). Free tier: 60 requests/minute.

**Q: How much data do I need for ML?**
A: Minimum 200 deals, ideally 500+ with historical price changes.

**Q: Can I train ML on my laptop?**
A: Yes, but Google Colab is recommended (faster, free GPU).

**Q: Will this slow down my dashboard?**
A: Gemini adds 1-3s per analysis. ML is instant (<0.1s).

---

## ✅ Checklist

Before going live:

- [ ] Installed all packages
- [ ] Got Gemini API key (if using)
- [ ] Trained ML model (if using)
- [ ] Downloaded model files
- [ ] Created models/ folder
- [ ] Tested imports
- [ ] Tested Gemini with sample deal
- [ ] Tested ML with sample deal
- [ ] Integrated with Streamlit
- [ ] Ran dashboard locally
- [ ] Verified AI insights appear
- [ ] Checked predictions make sense

**Ready to launch!** 🚀

---

## 📝 Quick Start Commands

```powershell
# Install everything
pip install google-generativeai scikit-learn joblib streamlit plotly pandas numpy

# Set Gemini key
$env:GEMINI_API_KEY="your_key_here"

# Create models folder
New-Item -ItemType Directory -Force -Path "models"

# Run dashboard
streamlit run streamlit_dashboard.py
```

**That's it!** Your dashboard now has AI superpowers. 🧠✨
