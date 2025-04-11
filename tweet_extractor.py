"""
Tweet Extractor Module

This module provides functionality to extract data from tweets using Selenium.
Optimized for Railway deployment with robust error handling and lightweight implementation.
"""

import logging
import json
import re
import time
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TweetExtractor:
    """
    A class to extract data from tweets using Selenium with Chrome Headless.
    Optimized for reliability and performance in production environments.
    """
    
    # Class-level constants
    PAGE_LOAD_TIMEOUT = 20  # Default timeout in seconds for page load
    ELEMENT_TIMEOUT = 10    # Default timeout in seconds for element location
    MAX_RETRIES = 2         # Maximum number of retries for extraction
    RETRY_DELAY = 1         # Base delay between retries in seconds
    
    def __init__(self):
        """Initialize the TweetExtractor with necessary configurations."""
        # Chrome options for headless browser
        self.options = Options()
        self.options.add_argument('--headless=new')  # Use new headless mode
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1280,720')
        
        # Performance optimizations
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-popup-blocking')
        
        # Reduce memory usage
        self.options.add_argument('--js-flags=--expose-gc')
        self.options.add_argument('--disable-features=site-per-process')
        
        # Improve stability in containerized environments
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-software-rasterizer')
        self.options.add_argument('--disable-setuid-sandbox')
        
        # Set user agent - use a more recent Chrome version
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Class-level function for extracting numbers from text
        self.extraer_numero_de_texto = lambda texto: self._extract_number_from_text(texto)
        
        # Increase timeouts for Railway environment
        self.PAGE_LOAD_TIMEOUT = 30  # Increased from 20
        self.ELEMENT_TIMEOUT = 15    # Increased from 10
        
    def _setup_driver(self):
        """
        Set up and return a configured Chrome WebDriver.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        try:
            import os
            import stat
            import platform
            import subprocess
            
            # Detect Chrome version in the environment
            chrome_version = None
            try:
                if platform.system() == "Linux":
                    # For Linux (Railway environment)
                    chrome_process = subprocess.Popen(
                        ['google-chrome', '--version'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    chrome_output, _ = chrome_process.communicate()
                    version_str = chrome_output.decode('utf-8').strip()
                    chrome_version = version_str.split()[-1]  # Extract version number
                    logger.info(f"Detected Chrome version: {chrome_version}")
            except Exception as e:
                logger.warning(f"Could not detect Chrome version: {str(e)}")
            
            # Install ChromeDriver with specific version if detected
            if chrome_version:
                driver_path = ChromeDriverManager(chrome_version=chrome_version).install()
            else:
                driver_path = ChromeDriverManager().install()
            
            # Verify we have the actual executable and not a text file
            if "THIRD_PARTY_NOTICES" in driver_path or not os.access(driver_path, os.X_OK):
                logger.warning(f"Found non-executable file: {driver_path}")
                
                # Search for the actual executable in parent directories
                driver_dir = os.path.dirname(driver_path)
                parent_dir = os.path.dirname(driver_dir)
                grandparent_dir = os.path.dirname(parent_dir)
                
                # Define possible locations for the chromedriver binary
                possible_drivers = []
                
                # Check for chromedriver in various possible locations
                for search_dir in [driver_dir, parent_dir, grandparent_dir]:
                    for root, dirs, files in os.walk(search_dir):
                        for file in files:
                            if file == "chromedriver" or file == "chromedriver.exe":
                                possible_path = os.path.join(root, file)
                                possible_drivers.append(possible_path)
                
                # Also check specific paths based on known directory structures
                if platform.system() == "Linux":
                    # Common paths in Linux environments
                    possible_drivers.extend([
                        os.path.join(driver_dir, "chromedriver"),
                        os.path.join(parent_dir, "chromedriver"),
                        os.path.join(parent_dir, "chromedriver-linux64", "chromedriver")
                    ])
                
                # Find the first executable chromedriver
                driver_path = None
                for possible_driver in possible_drivers:
                    if os.path.exists(possible_driver):
                        # Ensure the file is executable
                        try:
                            current_mode = os.stat(possible_driver).st_mode
                            os.chmod(possible_driver, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                            driver_path = possible_driver
                            logger.info(f"Found executable ChromeDriver at: {driver_path}")
                            break
                        except Exception as chmod_error:
                            logger.warning(f"Could not set executable permissions on {possible_driver}: {str(chmod_error)}")
                
                if not driver_path:
                    raise Exception("Could not find executable ChromeDriver binary")
            
            logger.info(f"Using ChromeDriver at: {driver_path}")
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=self.options)
            driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
            return driver
        except Exception as e:
            logger.error(f"Failed to set up Chrome driver: {str(e)}")
            
            # Fallback: Try to create the driver without specifying the path
            try:
                logger.info("Trying fallback method to create driver...")
                driver = webdriver.Chrome(options=self.options)
                driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
                return driver
            except Exception as e2:
                logger.error(f"Fallback method also failed: {str(e2)}")
                raise

    def _cleanup(self, driver):
        """
        Clean up resources by closing the WebDriver.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance to close
        """
        try:
            if driver:
                driver.quit()
        except Exception as e:
            logger.error(f"Error during driver cleanup: {str(e)}")
        
    def extract_tweet(self, url):
        """
        Extract tweet data using Selenium.
        
        Args:
            url (str): URL of the tweet to extract
            
        Returns:
            dict: Extracted tweet data or error information
        """
        tweet_data = {
            'url': url,
            'status': 'error',
            'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Validate and normalize URL
        if not self._is_valid_twitter_url(url):
            tweet_data['message'] = 'Invalid tweet URL'
            return tweet_data
            
        # Extract username from the URL
        username_match = re.search(r'(?:twitter|x)\.com/([^/]+)', url)
        if username_match:
            tweet_data['author'] = f"@{username_match.group(1)}"
        
        # Try to extract tweet data with retries
        driver = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                logger.info(f"Extraction attempt {attempt+1}/{self.MAX_RETRIES+1} for URL: {url}")
                
                # Set up a new driver for each attempt
                driver = self._setup_driver()
                
                # Extract tweet data
                result = self._extract_tweet_data(driver, url)
                
                if result and result.get('success'):
                    # Update tweet_data with extracted information
                    tweet_data.update({
                        'status': 'success',
                        'author_name': result.get('author_name', ''),
                        'text': result.get('text', ''),
                        'likes': result.get('likes', '0'),
                        'retweets': result.get('retweets', '0'),
                        'replies': result.get('replies', '0'),
                        'views': result.get('views', '0'),
                        'images': result.get('images', []),
                        'created_at': result.get('created_at', '')
                    })
                    
                    # Remove empty or None fields
                    tweet_data = {k: v for k, v in tweet_data.items() if v not in [None, '', []]}
                    return tweet_data
                    
            except Exception as e:
                logger.error(f"Error in extraction attempt {attempt+1}: {str(e)}")
                
            finally:
                # Clean up resources
                self._cleanup(driver)
                driver = None
            
            # If this wasn't the last attempt, wait before retrying
            if attempt < self.MAX_RETRIES:
                retry_delay = self.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
        # If all attempts fail
        tweet_data['message'] = 'Could not extract tweet information after multiple attempts'
        return tweet_data
    
    def _is_valid_twitter_url(self, url):
        """
        Validate if the URL is a proper Twitter/X tweet URL.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pattern = r'https?://(www\.)?(twitter|x)\.com/[^/]+/status/\d+'
        return bool(re.match(pattern, url))
        
    def _extract_tweet_data(self, driver, url):
        """
        Extract tweet data using Selenium.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            url (str): URL of the tweet to extract
            
        Returns:
            dict: Extracted data with success flag
        """
        try:
            # Navigate to the tweet URL
            logger.info(f"Navigating to URL: {url}")
            driver.get(url)
            
            # Wait for the page to load
            logger.info("Waiting for page to load...")
            
            # First check if we need to handle any consent dialogs or login prompts
            self._handle_dialogs(driver)
            
            # Wait for the tweet content to be visible
            logger.info("Waiting for tweet content...")
            WebDriverWait(driver, self.ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )
            
            # Extract tweet data
            logger.info("Extracting tweet data...")
            
            # Extract author information
            author_name = self._extract_author_name(driver)
            
            # Extract tweet text
            text = self._extract_tweet_text(driver)
            
            # Extract metrics (likes, retweets, replies, views)
            metrics = self._extract_metrics(driver)
            
            # Extract images
            images = self._extract_images(driver)
            
            # Extract date
            created_at = self._extract_date(driver)
            
            # Check if we extracted the essential data
            if not (author_name or text):
                logger.warning("Failed to extract essential tweet data")
                return {'success': False}
            
            return {
                'success': True,
                'author_name': author_name,
                'text': text,
                'likes': metrics.get('likes', '0'),
                'retweets': metrics.get('retweets', '0'),
                'replies': metrics.get('replies', '0'),
                'views': metrics.get('views', '0'),
                'images': images,
                'created_at': created_at
            }
            
        except TimeoutException as e:
            logger.error(f"Timeout while loading tweet: {str(e)}")
            return {'success': False}
        except Exception as e:
            logger.error(f"Error extracting tweet data: {str(e)}")
            return {'success': False}
    
    def _handle_dialogs(self, driver):
        """
        Handle any dialogs that might appear (consent, login prompts, etc.)
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
        """
        try:
            # Check for and dismiss login dialog
            login_dialogs = driver.find_elements(By.CSS_SELECTOR, 'div[aria-modal="true"] div[role="dialog"]')
            if login_dialogs:
                # Try to find and click the "X" close button
                close_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[aria-modal="true"] div[role="button"][aria-label="Close"]')
                if close_buttons:
                    close_buttons[0].click()
                    time.sleep(1)  # Wait for dialog to close
        except Exception as e:
            logger.warning(f"Error handling dialogs: {str(e)}")
            # Continue anyway, as this is not critical
    
    def _extract_author_name(self, driver):
        """
        Extract the author name from the tweet.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            
        Returns:
            str: Author name or empty string if not found
        """
        try:
            # Try multiple selectors for author name
            selectors = [
                'article[data-testid="tweet"] div[data-testid="User-Name"] span.css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0',
                'article[data-testid="tweet"] a[role="link"] div[dir="auto"] span span',
                'article[data-testid="tweet"] div[data-testid="User-Name"] > div:first-child > div:first-child span'
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements[0].text.strip()
            
            return ""
        except Exception as e:
            logger.warning(f"Error extracting author name: {str(e)}")
            return ""
    
    def _extract_tweet_text(self, driver):
        """
        Extract the tweet text.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            
        Returns:
            str: Tweet text or empty string if not found
        """
        try:
            # Try multiple selectors for tweet text
            selectors = [
                'article[data-testid="tweet"] div[data-testid="tweetText"]',
                'article[data-testid="tweet"] div[lang]'
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements[0].text.strip()
            
            return ""
        except Exception as e:
            logger.warning(f"Error extracting tweet text: {str(e)}")
            return ""
    
    def _extract_metrics(self, driver):
        """
        Extract tweet metrics (likes, retweets, replies, views).
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            
        Returns:
            dict: Dictionary with metrics
        """
        metrics = {
            'likes': '0',
            'retweets': '0',
            'replies': '0',
            'views': '0'
        }
        
        try:
            # Get the tweet article element
            article = WebDriverWait(driver, self.ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )
            
            # Wait a bit longer for metrics to load
            time.sleep(2)
            
            # MÉTODO 1: Original approach - using direct selectors
            try:
                # Replies
                reply_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"] div[data-testid="reply"]')
                if reply_elements:
                    reply_count_elements = reply_elements[0].find_elements(By.XPATH, './following-sibling::span')
                    if reply_count_elements:
                        metrics['replies'] = reply_count_elements[0].text.strip()
                
                # Retweets
                retweet_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"] div[data-testid="retweet"]')
                if retweet_elements:
                    retweet_count_elements = retweet_elements[0].find_elements(By.XPATH, './following-sibling::span')
                    if retweet_count_elements:
                        metrics['retweets'] = retweet_count_elements[0].text.strip()
                
                # Likes
                like_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"] div[data-testid="like"]')
                if like_elements:
                    like_count_elements = like_elements[0].find_elements(By.XPATH, './following-sibling::span')
                    if like_count_elements:
                        metrics['likes'] = like_count_elements[0].text.strip()
                
                # Views
                view_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"] a[aria-label*="view"]')
                if view_elements:
                    metrics['views'] = view_elements[0].text.strip()
                
                logger.info(f"Method 1 metrics: {metrics}")
            except Exception as e:
                logger.warning(f"Error in metrics extraction method 1: {str(e)}")
            
            # MÉTODO 2: Using data-testid attributes with count suffix
            try:
                interaction_buttons = driver.find_elements(By.CSS_SELECTOR, '[data-testid$="-count"]')
                for button in interaction_buttons:
                    button_id = button.get_attribute('data-testid')
                    count_text = button.text.strip()
                    count = self._extract_number_from_text(count_text)
                    
                    logger.info(f"Found button: {button_id} = {count_text} → {count}")
                    
                    if 'reply-count' in button_id and (metrics['replies'] == '0' or count > int(metrics['replies'])):
                        metrics['replies'] = str(count)
                    elif 'retweet-count' in button_id and (metrics['retweets'] == '0' or count > int(metrics['retweets'])):
                        metrics['retweets'] = str(count)
                    elif 'like-count' in button_id and (metrics['likes'] == '0' or count > int(metrics['likes'])):
                        metrics['likes'] = str(count)
                    elif 'bookmark-count' in button_id:
                        # Not used in the API response but collected for completeness
                        pass
            except Exception as e:
                logger.warning(f"Error in metrics extraction method 2: {str(e)}")
            
            # MÉTODO 3: Using aria-labels
            try:
                metrics_divs = article.find_elements(By.CSS_SELECTOR, '[role="group"] div')
                for div in metrics_divs:
                    aria_label = div.get_attribute('aria-label')
                    if aria_label:
                        logger.info(f"Found aria-label: {aria_label}")
                        
                        # Extract metrics based on aria-label text
                        count = self._extract_number_from_text(aria_label)
                        
                        if ('respuesta' in aria_label.lower() or 'reply' in aria_label.lower()) and (metrics['replies'] == '0' or count > int(metrics['replies'])):
                            metrics['replies'] = str(count)
                        elif 'retweet' in aria_label.lower() and (metrics['retweets'] == '0' or count > int(metrics['retweets'])):
                            metrics['retweets'] = str(count)
                        elif ('me gusta' in aria_label.lower() or 'like' in aria_label.lower()) and (metrics['likes'] == '0' or count > int(metrics['likes'])):
                            metrics['likes'] = str(count)
                        elif ('view' in aria_label.lower() or 'vista' in aria_label.lower()) and (metrics['views'] == '0' or count > int(metrics['views'])):
                            metrics['views'] = str(count)
            except Exception as e:
                logger.warning(f"Error in metrics extraction method 3: {str(e)}")
            
            # MÉTODO 4: Looking for buttons with numbers
            try:
                action_buttons = driver.find_elements(By.CSS_SELECTOR, '[role="button"]')
                for btn in action_buttons:
                    btn_text = btn.text.strip()
                    if btn_text and any(c.isdigit() for c in btn_text):
                        logger.info(f"Found button with number: {btn_text}")
                        
                        # Use button text and attributes to determine type
                        btn_aria = btn.get_attribute('aria-label') or ''
                        btn_id = btn.get_attribute('data-testid') or ''
                        
                        count = self._extract_number_from_text(btn_text)
                        
                        if ('reply' in btn_id.lower() or 'respuesta' in btn_aria.lower()) and (metrics['replies'] == '0' or count > int(metrics['replies'])):
                            metrics['replies'] = str(count)
                        elif ('retweet' in btn_id.lower() or 'retweet' in btn_aria.lower()) and (metrics['retweets'] == '0' or count > int(metrics['retweets'])):
                            metrics['retweets'] = str(count)
                        elif ('like' in btn_id.lower() or 'gusta' in btn_aria.lower()) and (metrics['likes'] == '0' or count > int(metrics['likes'])):
                            metrics['likes'] = str(count)
                        elif ('view' in btn_id.lower() or 'vista' in btn_aria.lower()) and (metrics['views'] == '0' or count > int(metrics['views'])):
                            metrics['views'] = str(count)
            except Exception as e:
                logger.warning(f"Error in metrics extraction method 4: {str(e)}")
            
            # MÉTODO 5: Direct search for divs with numbers
            try:
                # Find all divs containing numeric text or with K/M at the end
                potential_metrics = article.find_elements(By.XPATH, './/div[contains(text(), "K") or contains(text(), "M") or string-length(normalize-space()) <= 8]')
                potential_metrics = [pm for pm in potential_metrics if pm.text.strip() and any(c.isdigit() for c in pm.text)]
                
                logger.info(f"Potential metrics found: {[pm.text for pm in potential_metrics]}")
                
                # If we find 3-5 metrics in order, they're likely reply, retweet, like, (view)
                if 3 <= len(potential_metrics) <= 5:
                    metrics_found = []
                    for pm in potential_metrics:
                        if pm.text.strip() and any(c.isdigit() for c in pm.text):
                            metrics_found.append(self._extract_number_from_text(pm.text))
                    
                    logger.info(f"Numeric metrics extracted: {metrics_found}")
                    
                    # Assign in typical order if we have 3 or more
                    if len(metrics_found) >= 3:
                        if metrics['replies'] == '0':
                            metrics['replies'] = str(metrics_found[0])
                        if metrics['retweets'] == '0':
                            metrics['retweets'] = str(metrics_found[1])
                        if metrics['likes'] == '0':
                            metrics['likes'] = str(metrics_found[2])
                        if len(metrics_found) > 3 and metrics['views'] == '0':
                            metrics['views'] = str(metrics_found[3])
            except Exception as e:
                logger.warning(f"Error in metrics extraction method 5: {str(e)}")
            
            # Log final metrics
            logger.info(f"Final metrics: {metrics}")
            
            return metrics
        except Exception as e:
            logger.warning(f"Error extracting metrics: {str(e)}")
            return metrics
    
    def _extract_number_from_text(self, texto):
        """
        Extract numbers from text, including formats with K, M, etc.
        
        Args:
            texto (str): Text containing a number
            
        Returns:
            int: Extracted number value
        """
        if not texto:
            return 0
        
        # Look for patterns like "2.5K", "3M", etc.
        match = re.search(r'([\d,.]+)([KkMmBb])?', texto)
        if not match:
            return 0
        
        numero = match.group(1).replace(',', '.')
        unidad = match.group(2).upper() if match.group(2) else ''
        
        try:
            valor = float(numero)
            if unidad == 'K':
                valor *= 1000
            elif unidad == 'M':
                valor *= 1000000
            elif unidad == 'B':
                valor *= 1000000000
            return int(valor)
        except:
            return 0
    
    def _normalize_count(self, count_str):
        """
        Normalize count strings (e.g., "1.5K" to "1500").
        
        Args:
            count_str (str): Count string to normalize
            
        Returns:
            str: Normalized count as string
        """
        if not count_str or count_str == '0':
            return '0'
        
        count_str = count_str.strip().replace(',', '')
        
        # Handle "K" (thousands)
        if 'K' in count_str:
            count_str = count_str.replace('K', '')
            count = float(count_str) * 1000
            return str(int(count))
        
        # Handle "M" (millions)
        if 'M' in count_str:
            count_str = count_str.replace('M', '')
            count = float(count_str) * 1000000
            return str(int(count))
        
        # Handle "B" (billions)
        if 'B' in count_str:
            count_str = count_str.replace('B', '')
            count = float(count_str) * 1000000000
            return str(int(count))
        
        return count_str
    
    def _extract_images(self, driver):
        """
        Extract images from the tweet.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            
        Returns:
            list: List of image URLs
        """
        images = []
        try:
            # Try to find image elements
            image_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"] img[alt="Image"]')
            for img in image_elements:
                src = img.get_attribute('src')
                if src and 'profile' not in src and 'pbs.twimg.com' in src:
                    # Get the highest quality version by removing size parameters
                    base_url = re.sub(r'\?.*$', '', src)
                    if base_url not in images:
                        images.append(base_url)
            
            return images
        except Exception as e:
            logger.warning(f"Error extracting images: {str(e)}")
            return images
    
    def _extract_date(self, driver):
        """
        Extract the tweet date.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            
        Returns:
            str: Tweet date or empty string if not found
        """
        try:
            # Try to find time element
            time_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"] time')
            if time_elements:
                datetime_attr = time_elements[0].get_attribute('datetime')
                if datetime_attr:
                    # Parse and format the datetime
                    dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return ""
        except Exception as e:
            logger.warning(f"Error extracting date: {str(e)}")
            return ""


# Public API function for external use
def extract_tweet_data(url):
    """
    Extract data from a tweet URL.
    
    This is the main public function that should be used by external code.
    
    Args:
        url (str): URL of the tweet to extract
        
    Returns:
        dict: Extracted tweet data or error information
    """
    tweet_extractor = TweetExtractor()
    return tweet_extractor.extract_tweet(url)
