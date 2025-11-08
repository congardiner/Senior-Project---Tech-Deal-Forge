@echo off
echo ============================================
echo DealForge - Run All Scrapers
echo ============================================
echo.

echo [1/4] Scraping SlickDeals...
python slickdeals_webscraper.py --format database
echo.

echo [2/4] Scraping Best Buy...
python bestbuy_api_scraper.py
echo.

echo [3/4] Preparing ML Data...
python prepare_ml_data.py
echo.

echo [4/4] Verifying MySQL Backup...
python verify_mysql.py
echo.

echo ============================================
echo Done! All data saved to:
echo   - CSV: output\*.csv
echo   - MySQL: deal_intelligence database
echo   - ML Data: output\ml_data\*.csv
echo ============================================

REM Log completion with timestamp
echo [%date% %time%] Scraping completed >> scraper_log.txt