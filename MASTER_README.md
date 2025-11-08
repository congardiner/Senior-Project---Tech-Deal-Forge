TEMPLATE

WILL want to include some screenshots of what the project itself looks like when running. 


## Workflow Overview

Scrapers (SlickDeals + BensBargains)
    ↓
DealsDataPipeline.process_deals()
    ↓
├── CSV Files (output/*.csv)          [Backup + Sharing]
|-- SQLite Database (output/deals.db)  [Local Storage]
    ↓
prepare_ml_data.py
    ↓
ML Features CSV (output/ml_data/*.csv) [Training Data]
    ↓
Google Colab / Local Training
    ↓
Trained Model (output/ml_model/deal_quality_model.pkl)
    ↓
Streamlit Dashboard (streamlit_dashboard.py)


## 📊 Architecture

```
┌─────────────────────┐
│  SlickDeals Scraper │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ BensBargains Scraper│
└──────────┬──────────┘
           │
     ┌─────▼─────┐
     │  Pipeline │
     └─────┬─────┘
           │
      ┌────▼────┐
      │  SQLITE  │ ◄── Local (for scrapers)
      │ (Local) │
      └────┬────┘
           │
      [Migration]
           │
      ┌────▼────┐
      │Supabase │ ◄── Cloud (for dashboard)
      │ (Cloud) │
      └────┬────┘
           │
    ┌──────▼──────┐
    │  Streamlit  │
    │  Dashboard  │
    └─────────────┘
```