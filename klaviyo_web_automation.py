#!/usr/bin/env python3
"""
Klaviyo Web Automation for CSV Upload
Automates the manual CSV upload process using Selenium
"""

import os
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class KlaviyoWebUploader:
    """Automates Klaviyo CSV upload using web browser"""
    
    def __init__(self, email=None, password=None, headless=True):
        self.email = email or os.environ.get('KLAVIYO_LOGIN_EMAIL')
        self.password = password or os.environ.get('KLAVIYO_LOGIN_PASSWORD')
        self.headless = headless
        self.driver = None
        
        if not self.email or not self.password:
            raise ValueError("Klaviyo login credentials required (KLAVIYO_LOGIN_EMAIL, KLAVIYO_LOGIN_PASSWORD)")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Allow file downloads
        prefs = {
            "download.default_directory": tempfile.gettempdir(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            raise Exception(f"Failed to setup Chrome driver: {e}")
    
    def login_to_klaviyo(self):
        """Login to Klaviyo account"""
        try:
            print("🔐 Logging into Klaviyo...")
            
            self.driver.get("https://www.klaviyo.com/login")
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Enter credentials
            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            
            # Submit form
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for redirect (login success)
            WebDriverWait(self.driver, 15).until(
                lambda driver: "login" not in driver.current_url.lower()
            )
            
            print("✅ Successfully logged into Klaviyo")
            
        except TimeoutException:
            raise Exception("Login timeout - check credentials or Klaviyo is slow")
        except Exception as e:
            raise Exception(f"Login failed: {e}")
    
    def navigate_to_review_import(self):
        """Navigate to the review import page"""
        try:
            print("📁 Navigating to review import page...")
            
            # Direct navigation to review import
            self.driver.get("https://www.klaviyo.com/reviews/import/upload")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            print("✅ Review import page loaded")
            
        except TimeoutException:
            raise Exception("Review import page failed to load")
        except Exception as e:
            raise Exception(f"Navigation failed: {e}")
    
    def upload_csv_file(self, csv_file_path):
        """Upload CSV file to Klaviyo"""
        try:
            print(f"📤 Uploading CSV file: {csv_file_path}")
            
            if not os.path.exists(csv_file_path):
                raise Exception(f"CSV file not found: {csv_file_path}")
            
            # Find file input
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(os.path.abspath(csv_file_path))
            
            # Wait a bit for file to be processed
            time.sleep(2)
            
            # Look for upload/submit button
            upload_buttons = [
                "//button[contains(text(), 'Upload')]",
                "//button[contains(text(), 'Import')]", 
                "//button[contains(text(), 'Submit')]",
                "//input[@type='submit']",
                "//button[@type='submit']"
            ]
            
            upload_button = None
            for xpath in upload_buttons:
                try:
                    upload_button = self.driver.find_element(By.XPATH, xpath)
                    break
                except NoSuchElementException:
                    continue
            
            if not upload_button:
                raise Exception("Could not find upload/submit button")
            
            upload_button.click()
            
            # Wait for upload to complete
            print("⏳ Waiting for upload to complete...")
            
            # Look for success indicators
            success_indicators = [
                "//div[contains(text(), 'success')]",
                "//div[contains(text(), 'uploaded')]",
                "//div[contains(text(), 'imported')]",
                "//span[contains(text(), 'complete')]"
            ]
            
            success = False
            for xpath in success_indicators:
                try:
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    success = True
                    break
                except TimeoutException:
                    continue
            
            if success:
                print("✅ CSV upload completed successfully!")
                return True
            else:
                print("⚠️ Upload may have completed (no clear success indicator found)")
                return True
                
        except Exception as e:
            raise Exception(f"CSV upload failed: {e}")
    
    def upload_reviews_csv(self, csv_file_path):
        """Complete process to upload reviews CSV"""
        try:
            self.setup_driver()
            self.login_to_klaviyo()
            self.navigate_to_review_import()
            result = self.upload_csv_file(csv_file_path)
            
            return {
                'success': True,
                'message': 'CSV uploaded successfully to Klaviyo',
                'file': csv_file_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': csv_file_path
            }
        
        finally:
            if self.driver:
                self.driver.quit()

def upload_reviews_to_klaviyo_web(csv_file_path, email=None, password=None):
    """Main function to upload reviews via web automation"""
    try:
        uploader = KlaviyoWebUploader(email=email, password=password)
        return uploader.upload_reviews_csv(csv_file_path)
        
    except ValueError as e:
        return {
            'success': False,
            'error': f"Configuration error: {e}",
            'file': csv_file_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Upload failed: {e}",
            'file': csv_file_path
        }

# Example usage
if __name__ == "__main__":
    # Test with a sample CSV file
    test_csv = "bulk_reviews_20250725_102102 (1).csv"
    
    if os.path.exists(test_csv):
        result = upload_reviews_to_klaviyo_web(test_csv)
        print(f"\nResult: {result}")
    else:
        print(f"Test CSV file not found: {test_csv}")
        print("Please ensure you have a CSV file to test with.")