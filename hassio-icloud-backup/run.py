#!/usr/bin/env python3
"""
Home Assistant iCloud Backup Add-on
Uploads Home Assistant backups to iCloud Drive using browser automation (Selenium)
"""
import os
import sys
import json
import logging
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from /data/options.json"""
    config_file = Path('/data/options.json')
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

def create_browser():
    """Create a headless Chrome browser instance"""
    logger.info("Initializing headless browser...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.binary_location = '/usr/bin/chromium-browser'
    
    service = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    
    return driver

def login_to_icloud(driver, username, password):
    """Login to iCloud.com using browser automation"""
    logger.info("Navigating to iCloud.com...")
    
    try:
        driver.get("https://www.icloud.com/")
        
        # Wait for login page to load
        logger.info("Waiting for login form...")
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "account_name_text_field"))
        )
        
        # Enter username
        logger.info(f"Entering username: {username}")
        username_field.clear()
        username_field.send_keys(username)
        
        # Click continue button
        continue_button = driver.find_element(By.ID, "sign-in")
        continue_button.click()
        
        time.sleep(2)
        
        # Enter password
        logger.info("Entering password...")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password_text_field"))
        )
        password_field.clear()
        password_field.send_keys(password)
        
        # Click sign in
        sign_in_button = driver.find_element(By.ID, "sign-in")
        sign_in_button.click()
        
        logger.info("Credentials submitted, waiting for authentication...")
        time.sleep(5)
        
        # Check if 2FA is required
        if "two-factor" in driver.current_url.lower() or "verify" in driver.current_url.lower():
            logger.error("Two-factor authentication is required!")
            logger.error("Browser automation cannot bypass Apple's 2FA requirement.")
            return False
        
        # Wait for iCloud dashboard
        logger.info("Waiting for iCloud dashboard...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "app-icon"))
        )
        
        logger.info("Successfully logged in to iCloud!")
        return True
        
    except TimeoutException as e:
        logger.error(f"Timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during login: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function"""
    logger.info("Starting iCloud Backup (Browser Automation Test)...")
    
    config = load_config()
    username = config.get('icloud_username', '')
    password = config.get('icloud_password', '')
    
    if not username or not password:
        logger.error("iCloud username and password are required!")
        sys.exit(1)
    
    driver = None
    
    try:
        driver = create_browser()
        
        if not login_to_icloud(driver, username, password):
            logger.error("Failed to login - likely due to 2FA requirement")
            sys.exit(1)
        
        # Save screenshot
        driver.save_screenshot('/data/icloud_success.png')
        logger.info("Login successful! Screenshot saved.")
        logger.info("Browser automation approach is VIABLE if 2FA can be handled!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    try:
        main()
        time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
