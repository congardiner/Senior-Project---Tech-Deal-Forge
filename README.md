# Tech Deal Forge - Streamlit Dashboard
🔥 **Real-time tech deals aggregator and price tracker**
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tech-deal-forge-dashboard.streamlit.app/)

## Overview of the Project 

The 'Tech Deal Forge' is an all-in-one dashboard for discovering real tech deals without the noise. It consolidates web-scraped pricing data, historical trends, and lightweight machine-learning predictions into a single streamlined platform. By aggregating product information from multiple sources and presenting it through a simple Streamlit interface, the project helps users quickly determine whether a tech product is fairly priced, discounted, or worth waiting for.

## Problem Statement

Finding a genuine “good deal” on tech products is time-consuming, inconsistent, and often misleading due to scattered information, promotional bias, and fluctuating prices. Users are forced to manually search multiple sites or rely on community forums that don’t always provide historical context or price-trend insights.

## Real World Impact

Tech Deal Forge reduces the time, stress, and uncertainty involved in tech-deal hunting. By combining historical price data, simple visual analytics, and a basic ML model to estimate potential price drops, users can make more informed purchasing decisions and avoid overpaying—especially valuable for students, budget-conscious buyers, and anyone who wants data-driven guidance rather than marketing-driven claims.

## Target Audience

- Students and budget-conscious consumers
- Tech enthusiasts tracking price changes
- Deal hunters who want historical data, not 'projected hype' but a real-world timeline
- Anyone looking for a central hub to evaluate tech pricing quickly without needing to 'churn' the internet 
- Users who want personalized, data-driven insights into whether a product is a “good deal”

## Limitations

1. **Limited Data Sources**
- My database is limited to output rendered and provided by my webscrapers in the timeframe of this project, as a result of this, I am currently unable to provide a complete and accurate capture of *all* historical price trends for *all* tech-related consumer products.
  - While the project aggregates data from multiple sites, it does not cover every retailer or every type of tech product.
  - The insights are only as comprehensive as the platforms being scraped.

 2. **Scraper Reliability & Website Changes**
- Web-scraping depends on website structure and accessibility:
  - Any layout changes on a dynamic website can break the webscrapers / any additional that are added to the project.
  - Certain sites may restrict access via robots.txt
  - CAPTCHAs or rate limits may cause inconsistent results
   - The project reflects best-effort data collection, not enterprise-level scraping reliability.
3. **Not a Real-Time Price Tracker**
- This is not a live, instantly updated price-monitoring service.
Scrapers run at scheduled intervals, so:
  - Prices may lag behind real-time market changes.
  - Sudden promotions or flash deals may not always be captured immediately.

4. **Ethical & Legal Scraping Boundaries**
- The project follows ethical scraping principles, but:
  - It only collects publicly accessible data
  - It cannot bypass access restrictions
  - Rate limiting and responsible usage are enforced


## Features
-  **Price History Tracking** - Track deal prices over time
-  **Price Drop Alerts** - See the biggest discounts on tech products (by keywords & categories)
-  **Analytics Dashboard** - Interactive charts and insights
-  **AI Predictions** - ML-powered deal quality scoring
-  **Multi-Source Aggregation** - SlickDeals & Best Buy

## 🚀 Live Demo
Visit the live dashboard: [Tech Deal Forge](https://tech-deal-forge-dashboard.streamlit.app/)

## Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Senior-Project-Tech-Deal-Forge.git
cd Senior-Project-Tech-Deal-Forge

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run streamlit_dashboard.py
```

## Data Sources
The dashboard displays aggregated data from:
- SlickDeals (Open Global Community Forum)
- Best Buy (Featured Consumer Technology Deals)
- Historical price tracking (SQLite database)

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Visualization:** Plotly
- **Data Processing:** Pandas
- **Database:** SQLite
- **Web Scraping:** Botasaurus + BeautifulSoup
- **ML:** scikit-learn trained utilizing Google Colab

## Project Structure
```
Senior-Project-Tech-Deal-Forge/
├── streamlit_dashboard.py      # Main dashboard app
├── slickdeals_webscraper.py    # SlickDeals scraper
├── bestbuy_webscraper.py       # Best Buy scraper
├── data_pipeline.py            # Data processing pipeline
├── output/
│   └── deals.db                # SQLite database
└── requirements.txt            # Python dependencies
```

## 🔄 Updating Data
The dashboard displays cached data that is refreshed every 60 seconds. To manually update:
1. Run scrapers: `python run_all_scrapers.bat`
2. Or use the "🔄 Refresh Data" button in the sidebar

## Limitations
- Data relevance depends on my webscraper(s) and their intake frequencies and may not reflect the 'best' deals in real-time, as this is only utilizing aggregations from two different sources, over a span of several months at the time of writing (Q4, 2025).
- ML predictions are based on historical data and may not always accurately predict future deal quality, which is why the overall deal score is a combination of both the ML prediction and the current discount percentage; with this in mind, any results or recommendations as represented are not to be taken as financial advice rather, this is an attempt to streamline the deal discovery process for all users, in a free and open usage manner. 
- There is no user authentication or personalization features at this time, this a feature that is planned for future development, and will be added in later versions.
- Feel free to contribute or suggest improvements, as this is aimed to become an open-source project for the community once proper testing and documentation is complete.


## 📝 License
MIT License - See LICENSE file for details
- If you use this project or any part of it, please give appropriate credit, see LICENSE file for details.

## 👨‍💻 Author
Created as a Senior Project by Conner Gardiner
