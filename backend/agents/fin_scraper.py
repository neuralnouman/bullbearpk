#!/usr/bin/env python3
"""
Simplified Single-Run Stock Data Scraper using Selenium
Author: AI Assistant
Date: 2025-07-18

This script performs a single scrape of real-time stock data and exports to JSON.
No menu, no continuous monitoring - just scrape once and exit.
"""

import time
import logging
import sys
import io
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import os

# Add parent directory to path for database import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import db_config

# Configure UTF-8 for console output to support emojis (optional)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    StaleElementReferenceException
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class StockData:
    sector: str
    code: str
    name: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            'sector': self.sector,
            'code': self.code,
            'name': self.name,
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'close_price': self.close_price,
            'volume': self.volume,
            'change': self.change,
            'change_percent': self.change_percent,
            'timestamp': self.timestamp.isoformat()
        }

class StockScraper:
    def __init__(self):
        self.base_url = "https://www.scstrade.com"
        self.target_url = f"{self.base_url}/MarketStatistics/MS_DailyActivity.aspx"
        self.driver = None
        self.wait = None
        self.wait_timeout = 30
        self.max_retries = 3
        self.scraped_dir = os.path.join(os.path.dirname(__file__), 'scraped')
        os.makedirs(self.scraped_dir, exist_ok=True)

    def setup_driver(self, headless: bool = True) -> bool:
        try:
            logger.info("Setting up Chrome WebDriver...")
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-features=TranslateUI,OptimizationGuideModelDownloading,AutofillServerCommunication')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            chrome_options.add_argument("--log-level=3")  # Only fatal errors
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            logger.info("Creating Chrome WebDriver instance...")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info("Executing webdriver script...")
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info("Setting up WebDriverWait...")
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            logger.info("Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def navigate_to_page(self) -> bool:
        try:
            logger.info(f"Navigating to: {self.target_url}")
            if not self.driver:
                logger.error("WebDriver is not initialized")
                return False
                
            self.driver.get(self.target_url)
            logger.info("Page loaded, waiting for table element...")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            logger.info("Successfully navigated to stock data page")
            return True
        except TimeoutException:
            logger.error("Timeout waiting for page to load")
            return False
        except WebDriverException as e:
            logger.error(f"WebDriver error during navigation: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during navigation: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def wait_for_data_load(self) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tr")))
            time.sleep(2)
            logger.info("Stock data loaded successfully")
            return True
        except TimeoutException:
            logger.error("Timeout waiting for stock data to load")
            return False

    def extract_stock_data(self) -> List[StockData]:
        stocks = []
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) < 2:
                    continue
                header_row_index = self._find_header_row(rows)
                if header_row_index is None:
                    continue
                for row in rows[header_row_index + 1:]:
                    try:
                        stock_data = self._extract_row_data(row)
                        if stock_data:
                            stocks.append(stock_data)
                    except StaleElementReferenceException:
                        logger.warning("Stale element encountered, skipping row")
                    except Exception as e:
                        logger.warning(f"Error extracting row data: {str(e)}")
            logger.info(f"Successfully extracted {len(stocks)} stock records")
            return stocks
        except Exception as e:
            logger.error(f"Error during stock data extraction: {str(e)}")
            return []

    def _find_header_row(self, rows) -> Optional[int]:
        header_keywords = ['SECTOR', 'CODE', 'NAME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
        for i, row in enumerate(rows):
            try:
                cells = row.find_elements(By.TAG_NAME, "th") or row.find_elements(By.TAG_NAME, "td")
                cell_texts = [cell.text.strip().upper() for cell in cells]
                if any(keyword in ' '.join(cell_texts) for keyword in header_keywords):
                    return i
            except Exception:
                continue
        return None

    def _extract_row_data(self, row) -> Optional[StockData]:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 8:
                return None
            cell_texts = [cell.text.strip() for cell in cells]
            sector = cell_texts[0] if cell_texts[0] else "Unknown"
            code = cell_texts[1] if len(cell_texts) > 1 else "Unknown"
            name = cell_texts[2] if len(cell_texts) > 2 else "Unknown"
            open_price = self._parse_float(cell_texts[3]) if len(cell_texts) > 3 else 0.0
            high_price = self._parse_float(cell_texts[4]) if len(cell_texts) > 4 else 0.0
            low_price = self._parse_float(cell_texts[5]) if len(cell_texts) > 5 else 0.0
            close_price = self._parse_float(cell_texts[6]) if len(cell_texts) > 6 else 0.0
            volume = self._parse_int(cell_texts[7]) if len(cell_texts) > 7 else 0
            change = self._parse_float(cell_texts[8]) if len(cell_texts) > 8 else 0.0
            change_percent = (change / open_price * 100) if open_price > 0 else 0.0
            return StockData(sector, code, name, open_price, high_price, low_price, close_price, volume, change, change_percent, datetime.now())
        except Exception as e:
            logger.warning(f"Error parsing row data: {str(e)}")
            return None

    def _parse_float(self, value: str) -> float:
        cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _parse_int(self, value: str) -> int:
        cleaned = ''.join(c for c in value if c.isdigit())
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def scrape_data(self) -> List[StockData]:
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{self.max_retries}")
                if not self.navigate_to_page():
                    if attempt == self.max_retries - 1:
                        logger.error("Failed to navigate to page after all retries")
                        return []
                    continue
                if not self.wait_for_data_load():
                    if attempt == self.max_retries - 1:
                        logger.error("Failed to load data after all retries")
                        return []
                    continue
                stocks = self.extract_stock_data()
                if stocks:
                    logger.info(f"Successfully scraped {len(stocks)} stocks")
                    return stocks
            except Exception as e:
                logger.error(f"Error during scraping attempt {attempt + 1}: {str(e)}")
                time.sleep(5)
        logger.error("All scraping attempts failed")
        return []

    def export_to_json(self, stocks: List[StockData]) -> str:
        filename = f"live_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.scraped_dir, filename)
        try:
            gainers = [s for s in stocks if s.change > 0]
            losers = [s for s in stocks if s.change < 0]
            data = {
                'scrape_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_stocks': len(stocks),
                    'gainers': len(gainers),
                    'losers': len(losers),
                    'unchanged': len(stocks) - len(gainers) - len(losers)
                },
                'market_summary': {
                    'top_gainer': max(gainers, key=lambda x: x.change_percent).to_dict() if gainers else None,
                    'top_loser': min(losers, key=lambda x: x.change_percent).to_dict() if losers else None,
                    'highest_volume': max(stocks, key=lambda x: x.volume).to_dict() if stocks else None
                },
                'stocks': [stock.to_dict() for stock in stocks]
            }
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, default=str)
            logger.info(f"[SUCCESS] Exported {len(stocks)} stocks to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return ""

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {str(e)}")

    def scrape_and_export(self) -> str:
        """Scrape data and export to JSON, returning the file path."""
        if not self.setup_driver():
            raise RuntimeError("WebDriver setup failed")
        try:
            stocks = self.scrape_data()
            if stocks:
                return self.export_to_json(stocks)
            else:
                raise RuntimeError("No stock data scraped")
        finally:
            self.cleanup()

# === Agentic Tool Function ===
def scrape_stocks_tool() -> Dict:
    """LangChain-compatible tool: Scrape stocks and return structured data."""
    scraper = None
    try:
        scraper = StockScraper()
        
        # Set up the WebDriver first
        if not scraper.setup_driver():
            logger.error("Failed to setup WebDriver")
            return {
                "success": False,
                "message": "Failed to setup WebDriver",
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Now scrape the data
        stocks = scraper.scrape_data()
        
        if stocks:
            # Convert to list of dictionaries
            stock_data = [stock.to_dict() for stock in stocks]
            
            # Clear existing data and save new data to database
            try:
                # First, clear existing stock data
                db_config.execute_query("DELETE FROM stocks")
                logger.info("Cleared existing stock data from database")
                
                # Then insert new stock data
                for stock in stocks:
                    try:
                        db_config.insert_stock_data(stock.to_dict())
                        logger.info(f"Saved {stock.code} to database")
                    except Exception as e:
                        logger.warning(f"Failed to save {stock.code} to database: {e}")
                
                logger.info(f"Successfully saved {len(stocks)} stocks to database")
            except Exception as e:
                logger.error(f"Database operation failed: {e}")
            
            return {
                "success": True,
                "message": f"Successfully scraped and saved {len(stocks)} stocks to database",
                "data": stock_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "No stock data could be scraped",
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error in scrape_stocks_tool: {e}")
        return {
            "success": False,
            "message": f"Error scraping stocks: {str(e)}",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }
    finally:
        # Always cleanup the scraper
        if scraper:
            scraper.cleanup()

def main():
    print("\U0001F680 Live Stock Data Scraper")
    print("=" * 40)
    scraper = StockScraper()
    try:
        print("\U0001F527 Setting up WebDriver...")
        if not scraper.setup_driver():
            print("[ERROR] Failed to setup WebDriver")
            return
        print("\U0001F4CA Scraping live stock data...")
        stocks = scraper.scrape_data()
        if stocks:
            print(f"[SUCCESS] Successfully scraped {len(stocks)} stocks")
            json_file = scraper.export_to_json(stocks)
            if json_file:
                print(f"\U0001F4C1 Data exported to: {json_file}")
                gainers = [s for s in stocks if s.change > 0]
                losers = [s for s in stocks if s.change < 0]
                print("\n\U0001F4C8 Market Summary:")
                print(f"   Total Stocks: {len(stocks)}")
                print(f"   Gainers: {len(gainers)}")
                print(f"   Losers: {len(losers)}")
                if gainers:
                    top_gainer = max(gainers, key=lambda x: x.change_percent)
                    print(f"   Top Gainer: {top_gainer.code} (+{top_gainer.change_percent:.2f}%)")
                if losers:
                    top_loser = min(losers, key=lambda x: x.change_percent)
                    print(f"   Top Loser: {top_loser.code} ({top_loser.change_percent:.2f}%)")
                print(f"\n\U0001F3AF Live data captured at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("[ERROR] Failed to export data")
        else:
            print("[ERROR] No stock data could be scraped")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"[ERROR] An error occurred: {str(e)}")
    finally:
        scraper.cleanup()
        print("\n\U0001F3C1 Scraping completed!")

if __name__ == "__main__":
    main()