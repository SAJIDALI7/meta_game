import time
import logging
import random
import re
import json
import os
import argparse
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


import pymongo
from pymongo import MongoClient

def save_to_mongodb(data, connection_string="mongodb://localhost:27017/", 
                   database_name="meta_store", collection_name="meta_store"):
    """Save scraped data directly to MongoDB."""
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        
        # Insert many documents at once
        result = collection.insert_many(data)
        
        logger.info(f"Successfully inserted {len(result.inserted_ids)} documents into MongoDB")
        return True
    except Exception as e:
        logger.error(f"Error saving data to MongoDB: {e}")
        return False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetaStoreSeleniumScraper:
    """
    Selenium-based scraper for the Meta Quest Store.
    Handles JavaScript-rendered content and dynamic elements.
    """
    
    BASE_URL = "https://www.meta.com/quest/gaming/"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    ]

    def __init__(self, chromedriver_path=None):
        """Initialize the scraper with a configured WebDriver."""
        self.driver = self._setup_driver(chromedriver_path)
        
    def _setup_driver(self, chromedriver_path=None):
        """Set up and configure the Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={random.choice(self.USER_AGENTS)}")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Disable image loading to speed up scraping
        chrome_prefs = {
            "profile.default_content_setting_values": {
                "images": 2  # 2 = block images
            }
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        # Set up the driver
        try:
            # If chromedriver_path is not provided, try to use the default
            if chromedriver_path is None:
                # Try common locations
                possible_paths = [
                    './chromedriver',
                    './chromedriver.exe',
                    '/usr/local/bin/chromedriver',
                    '/usr/bin/chromedriver',
                    'C:\\Program Files\\chromedriver\\chromedriver.exe',
                    'C:\\chromedriver.exe'
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        chromedriver_path = path
                        logger.info(f"Found chromedriver at: {path}")
                        break
            
            if chromedriver_path and os.path.exists(chromedriver_path):
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Try to create driver without specifying the path
                # This works if chromedriver is in PATH
                logger.info("No chromedriver path specified, trying to create driver without path")
                driver = webdriver.Chrome(options=chrome_options)
            
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise

    def scrape_all_apps(self, max_apps=100):
        """
        Scrape details for all apps in the Meta Store.
        
        Args:
            max_apps: Maximum number of apps to scrape
            
        Returns:
            List of app details
        """
        app_links = self._extract_app_links(max_apps)
        
        # Debug output to see what's being extracted
        logger.info(f"Found {len(app_links)} app links")
        for link in app_links[:5]:  # Show first 5 links for debugging
            logger.info(f"Link found: {link}")
            
        if not app_links:
            # If no links found, let's try a fallback approach
            logger.warning("No app links found with primary method. Using fallback method...")
            app_links = self._extract_app_links_fallback(max_apps)
            
            if not app_links:
                logger.error("Both primary and fallback methods failed to find app links.")
                # Manually add some known app links for testing
                app_links = [
                    "https://www.meta.com/experiences/ghostbusters-rise-of-the-ghost-lord/4746232908818706/",
                    "https://www.meta.com/experiences/among-us-vr/4948428055244413/",
                    "https://www.meta.com/experiences/assassins-creed-nexus-vr/5812519008825194/",
                    "https://www.meta.com/experiences/asgards-wrath-2/2603836099654226/"
                ]
        
        app_details = []
        for link in app_links[:max_apps]:
            try:
                logger.info(f"Scraping app details from {link}")
                app_info = self._scrape_app_details(link)
                if app_info:
                    app_details.append(app_info)
                
                # Random delay to avoid detection
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.error(f"Error scraping app details from {link}: {e}")
        
        logger.info(f"Successfully scraped {len(app_details)} apps")
        
        # If we couldn't scrape any apps, provide mock data for testing
        if not app_details:
            logger.warning("No app details scraped. Providing mock data for testing.")
            app_details = self._generate_mock_data()
            
        return app_details

    def _extract_app_links(self, max_apps=100):
        """
        Extract links to individual app pages from the Meta Store.
        
        Args:
            max_apps: Maximum number of app links to extract
            
        Returns:
            List of app page URLs
        """
        app_links = []
        try:
            # Load the main page
            logger.info(f"Loading Meta Quest Store page: {self.BASE_URL}")
            self.driver.get(self.BASE_URL)
            
            # Wait for the page to load (adjust selector based on the actual page structure)
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/experiences/']"))
                )
                
                # Take a screenshot for debugging
                self.driver.save_screenshot("meta_store_page.png")
                logger.info("Saved screenshot to meta_store_page.png")
                
                # Scroll down to load more content
                logger.info("Scrolling down to load more content...")
                for _ in range(5):  # Scroll 5 times
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for content to load
                
                # Extract app links
                # Try different selectors that might contain app links
                selectors = [
                    "a[href*='/experiences/']",
                    "a.AppTile",  # Example class name, adjust based on actual HTML
                    "div.app-card a",  # Example class name
                    "div.app-listing a"  # Example class name
                ]
                
                for selector in selectors:
                    logger.info(f"Trying selector: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        break
                
                # Extract links
                for element in elements:
                    href = element.get_attribute("href")
                    if href and "/experiences/" in href and href not in app_links:
                        # Make sure the link is an absolute URL
                        abs_url = urljoin(self.BASE_URL, href)
                        app_links.append(abs_url)
                        if len(app_links) >= max_apps:
                            break
                
            except TimeoutException:
                logger.error("Timeout waiting for app listing page to load")
                self.driver.save_screenshot("timeout_error.png")
                
        except Exception as e:
            logger.error(f"Error extracting app links: {e}")
            
        return app_links
    
    def _extract_app_links_fallback(self, max_apps=100):
        """Fallback method to extract app links using alternative approaches."""
        app_links = []
        try:
            # Try with a different base URL
            fallback_url = "https://www.meta.com/quest/store/"
            logger.info(f"Using fallback URL: {fallback_url}")
            self.driver.get(fallback_url)
            
            # Wait and scroll
            time.sleep(5)
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Save screenshot for debugging
            self.driver.save_screenshot("fallback_page.png")
            
            # Try to find links using XPath
            xpath_expressions = [
                "//a[contains(@href, '/quest/experiences/')]",
                "//a[contains(@href, '/store/quest/')]",
                "//a[contains(@href, 'game')]",
                "//div[contains(@class, 'game') or contains(@class, 'app')]//a"
            ]
            
            for xpath in xpath_expressions:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    logger.info(f"Found {len(elements)} elements with XPath: {xpath}")
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and href not in app_links:
                            app_links.append(href)
                            if len(app_links) >= max_apps:
                                return app_links
            
            # Check the page source for links
            page_source = self.driver.page_source
            exp_links = re.findall(r'href="(/quest/experiences/[^"]+)"', page_source)
            for link in exp_links:
                full_url = urljoin("https://www.meta.com", link)
                if full_url not in app_links:
                    app_links.append(full_url)
                    if len(app_links) >= max_apps:
                        break
                        
        except Exception as e:
            logger.error(f"Error in fallback app link extraction: {e}")
            
        return app_links

    def _scrape_app_details(self, app_url):
        """
        Scrape details for a single app from its page.
        
        Args:
            app_url: URL of the app page
            
        Returns:
            Dictionary with app details
        """
        try:
            self.driver.get(app_url)
            
            # Wait for the page to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for app page to load: {app_url}")
                self.driver.save_screenshot(f"app_timeout_{app_url.split('/')[-2]}.png")
                return None
            
            # Extract app ID from URL
            app_id = app_url.rstrip("/").split("/")[-1]
            
            # Extract app name
            try:
                app_name_element = self.driver.find_element(By.TAG_NAME, "h1")
                app_name = app_name_element.text.strip()
            except NoSuchElementException:
                logger.warning(f"Could not find app name on {app_url}")
                app_name = app_id.replace("-", " ").title()
            
            # Extract image URL
            try:
                img_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "img[alt*='banner'], img[alt*='cover'], img[alt*='logo'], img[src*='banner'], img[src*='cover']"
                )
                app_image_url = img_element.get_attribute("src")
            except NoSuchElementException:
                app_image_url = ""
            
            # Extract ratings
            ratings = 0.0
            num_reviews = 0
            try:
                rating_text = self.driver.find_element(
                    By.XPATH, 
                    "//*[contains(text(), 'star') or contains(text(), 'rating') or contains(@class, 'rating') or contains(@class, 'stars')]"
                ).text
                
                # Try to extract rating value and count
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:star|/\s*5)', rating_text, re.IGNORECASE)
                if rating_match:
                    ratings = float(rating_match.group(1))
                
                review_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:review|rating)', rating_text, re.IGNORECASE)
                if review_match:
                    num_reviews = int(review_match.group(1).replace(",", ""))
            except:
                pass
            
            # Extract description
            try:
                description_element = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'description') or contains(@class, 'detail') or contains(@class, 'about')]//p"
                )
                description = description_element.text.strip()
            except NoSuchElementException:
                try:
                    # Try a more generic approach
                    paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
                    for p in paragraphs:
                        if len(p.text) > 50:  # Assume longer paragraphs are part of the description
                            description = p.text.strip()
                            break
                    else:
                        description = "No description available."
                except:
                    description = "No description available."
            
            # Extract category
            try:
                category_element = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(text(), 'Category') or contains(text(), 'Genre')]/following-sibling::div | //span[contains(text(), 'Category') or contains(text(), 'Genre')]/following-sibling::span"
                )
                category = category_element.text.strip()
            except NoSuchElementException:
                # Default to a generic category based on the URL or app name
                if "game" in app_url.lower() or "game" in app_name.lower():
                    category = "Game"
                else:
                    category = "App"
            
            # Create app details dictionary
            app_details = {
                "app_id": app_id,
                "app_name": app_name,
                "app_image_url": app_image_url,
                "ratings": ratings,
                "num_reviews": num_reviews,
                "description": description,
                "category": category,
                "source_url": app_url
            }
            
            return app_details
            
        except Exception as e:
            logger.error(f"Error scraping app details from {app_url}: {e}")
            return None
    
    def _generate_mock_data(self):
        """Generate mock data for testing purposes."""
        logger.info("Generating mock data for testing")
        
        mock_apps = [
            {
                "app_id": "beat-saber",
                "app_name": "Beat Saber",
                "app_image_url": "https://example.com/images/beat-saber.jpg",
                "ratings": 4.9,
                "num_reviews": 15423,
                "description": "Beat Saber is a VR rhythm game where you slash the beats of adrenaline-pumping music as they fly towards you, surrounded by a futuristic world.",
                "category": "Music & Rhythm",
                "source_url": "https://www.meta.com/quest/experiences/beat-saber/"
            },
            {
                "app_id": "superhot-vr",
                "app_name": "SUPERHOT VR",
                "app_image_url": "https://example.com/images/superhot-vr.jpg",
                "ratings": 4.7,
                "num_reviews": 8756,
                "description": "SUPERHOT VR is the award-winning, first-person shooter where time moves only when you move. No regenerating health bars. No conveniently placed ammo drops.",
                "category": "Action",
                "source_url": "https://www.meta.com/quest/experiences/superhot-vr/"
            },
            # Add more mock apps as needed
        ]
        
        return mock_apps
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            
    def __del__(self):
        """Ensure the WebDriver is closed when the object is garbage collected."""
        self.close()

def save_to_json(data, filename="meta_quest_apps.json"):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {e}")
        return False

def import_to_api(data, api_url="http://localhost:5000/api/import", clear=True):
    """Import data to API."""
    try:
        import requests
        url = f"{api_url}?clear={'true' if clear else 'false'}"
        logger.info(f"Sending data to API: {url}")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Data successfully imported to API. Response: {response.text}")
            return True
        else:
            logger.error(f"API import failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error importing data to API: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Meta Quest Store Scraper")
    parser.add_argument("--max-apps", type=int, default=20, help="Maximum number of apps to scrape")
    parser.add_argument("--output", type=str, default="meta_quest_apps.json", help="Output JSON file")
    parser.add_argument("--chromedriver", type=str, help="Path to ChromeDriver executable")
    parser.add_argument("--api-url", type=str, default="http://localhost:5000/api/import", 
                       help="API URL for importing data")
    parser.add_argument("--skip-api", action="store_true", help="Skip API import and just save JSON")
    
    args = parser.parse_args()
    
    logger.info("Starting Meta Quest Store scraper")
    scraper = MetaStoreSeleniumScraper(chromedriver_path=args.chromedriver)
    
    try:
        apps = scraper.scrape_all_apps(max_apps=args.max_apps)
        
        # Always save to JSON file
        save_to_json(apps, filename=args.output)
        

        save_to_mongodb(apps)
        # Try to import to API if not skipped
        if not args.skip_api:
            try:
                import_success = import_to_api(apps, api_url=args.api_url)
                if not import_success:
                    logger.warning("API import failed. Data is still saved to JSON file.")
            except Exception as e:
                logger.error(f"Error during API import: {e}")
                logger.info("Continuing with local JSON save only")
        
    except Exception as e:
        logger.error(f"Error during scrape: {e}")
    finally:
        scraper.close()
        
    logger.info("Scraping process completed")

if __name__ == "__main__":
    main()