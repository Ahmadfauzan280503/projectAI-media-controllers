"""
Complete Base Media Controller with all necessary imports and error handling
File: src/media_controllers/base_controller.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import logging
import os
import sys
import psutil
import subprocess
from pathlib import Path

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    HAS_WEBDRIVER_MANAGER = False
    print("⚠️  webdriver-manager not found. Will try to use system chromedriver.")

class BaseMediaController:
    """Base class for all media controllers with robust WebDriver handling"""
    
    def __init__(self, platform_name, base_url, timeout=30):
        self.platform_name = platform_name
        self.base_url = base_url
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(f"{platform_name}Controller")
        self.max_retries = 3
        self.retry_delay = 5
        
        try:
            self._initialize_driver()
        except Exception as e:
            self.logger.error(f"Failed to initialize {platform_name} controller: {e}")
            raise Exception(f"{platform_name} initialization failed: {e}")
    
    def _get_chrome_executable_path(self):
        """Find Chrome executable path"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _get_chromedriver_path(self):
        """Get ChromeDriver path"""
        if HAS_WEBDRIVER_MANAGER:
            try:
                return ChromeDriverManager().install()
            except Exception as e:
                self.logger.warning(f"ChromeDriverManager failed: {e}")
        
        possible_paths = [
            "./chromedriver.exe",
            "./drivers/chromedriver.exe", 
            "chromedriver.exe",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        try:
            result = subprocess.run(["where", "chromedriver"] if os.name == 'nt' else ["which", "chromedriver"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def _get_chrome_options(self):
        """Get Chrome options with proper configuration"""
        options = Options()
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        
        options.add_argument('--memory-pressure-off')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        options.add_argument('--window-size=1280,720')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            }
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        chrome_path = self._get_chrome_executable_path()
        if chrome_path:
            options.binary_location = chrome_path
        
        return options
    
    def _cleanup_chrome_processes(self):
        """Clean up any hanging Chrome processes"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        if proc.info['cmdline'] and any('--test-type' in str(cmd) or '--automation' in str(cmd) 
                                                       for cmd in proc.info['cmdline']):
                            proc.terminate()
                            proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
        except Exception as e:
            self.logger.warning(f"Error cleaning up Chrome processes: {e}")
    
    def _initialize_driver(self):
        """Initialize WebDriver with proper error handling and retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Initializing {self.platform_name} WebDriver (attempt {attempt + 1}/{self.max_retries})")
                
                if attempt > 0:
                    self._cleanup_chrome_processes()
                    time.sleep(2)
                
                options = self._get_chrome_options()
                
                driver_path = self._get_chromedriver_path()
                if not driver_path:
                    raise Exception("ChromeDriver not found. Please install ChromeDriver or use 'pip install webdriver-manager'")
                
                service = Service(executable_path=driver_path)
                
                self.logger.info(f"Creating WebDriver with ChromeDriver: {driver_path}")
                self.driver = webdriver.Chrome(service=service, options=options)
                
                self.driver.set_page_load_timeout(self.timeout)
                self.driver.implicitly_wait(10)
                
                self.wait = WebDriverWait(self.driver, self.timeout)
                
                self.logger.info(f"Testing {self.platform_name} WebDriver...")
                test_html = "<html><head><title>Test</title></head><body><h1>WebDriver Test OK</h1></body></html>"
                self.driver.get(f"data:text/html,{test_html}")
                
                if "Test" in self.driver.title:
                    self.logger.info(f"{self.platform_name} WebDriver initialized successfully")
                    return
                else:
                    raise Exception("WebDriver test failed")
                
            except Exception as e:
                self.logger.error(f"{self.platform_name} WebDriver initialization attempt {attempt + 1} failed: {e}")
                
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to initialize {self.platform_name} WebDriver after {self.max_retries} attempts: {e}")
    
    def navigate_to_platform(self):
        """Navigate to the platform with retry mechanism"""
        if not self.driver:
            raise Exception(f"{self.platform_name} WebDriver not initialized")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Navigating to {self.platform_name} (attempt {attempt + 1}/{max_retries})")
                self.driver.get(self.base_url)
                
                self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                
                self.logger.info(f"Successfully navigated to {self.platform_name}")
                return True
                
            except TimeoutException:
                self.logger.warning(f"Timeout navigating to {self.platform_name} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Error navigating to {self.platform_name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    raise
        return False
    
    def find_element_safe(self, by, value, timeout=10):
        """Safely find element with timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.debug(f"Element not found: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {by}={value}: {e}")
            return None
    
    def click_element_safe(self, by, value, timeout=10):
        """Safely click element"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except TimeoutException:
            self.logger.debug(f"Element not clickable: {by}={value}")
            return False
        except Exception as e:
            self.logger.error(f"Error clicking element {by}={value}: {e}")
            return False
    
    def execute_script_safe(self, script):
        """Safely execute JavaScript"""
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Error executing script: {e}")
            return None
    
    def send_keys_safe(self, keys):
        """Safely send keys to page"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self.driver).send_keys(keys).perform()
            return True
        except Exception as e:
            self.logger.error(f"Error sending keys: {e}")
            return False
    
    def is_driver_alive(self):
        """Check if WebDriver is still alive"""
        try:
            if not self.driver:
                return False
            self.driver.current_url
            return True
        except:
            return False
    
    def restart_driver(self):
        """Restart the WebDriver"""
        self.logger.info(f"Restarting {self.platform_name} WebDriver...")
        self.close()
        time.sleep(2)
        self._initialize_driver()
    
    def play(self):
        """Play media - to be implemented by subclasses"""
        if not self.is_driver_alive():
            self.logger.warning("Driver not alive, attempting restart...")
            try:
                self.restart_driver()
                self.navigate_to_platform()
            except Exception as e:
                self.logger.error(f"Failed to restart driver: {e}")
                return False
        raise NotImplementedError("Subclass must implement play method")
    
    def pause(self):
        """Pause media - to be implemented by subclasses"""
        if not self.is_driver_alive():
            self.logger.warning("Driver not alive, attempting restart...")
            try:
                self.restart_driver()
                self.navigate_to_platform()
            except Exception as e:
                self.logger.error(f"Failed to restart driver: {e}")
                return False
        raise NotImplementedError("Subclass must implement pause method")
    
    def next_track(self):
        """Next track/video - to be implemented by subclasses"""
        if not self.is_driver_alive():
            self.logger.warning("Driver not alive, attempting restart...")
            try:
                self.restart_driver()
                self.navigate_to_platform()
            except Exception as e:
                self.logger.error(f"Failed to restart driver: {e}")
                return False
        raise NotImplementedError("Subclass must implement next_track method")
    
    def previous_track(self):
        """Previous track/video - to be implemented by subclasses"""
        if not self.is_driver_alive():
            self.logger.warning("Driver not alive, attempting restart...")
            try:
                self.restart_driver()
                self.navigate_to_platform()
            except Exception as e:
                self.logger.error(f"Failed to restart driver: {e}")
                return False
        raise NotImplementedError("Subclass must implement previous_track method")
    
    def volume_up(self):
        """Increase volume - to be implemented by subclasses"""
        if not self.is_driver_alive():
            self.logger.warning("Driver not alive, attempting restart...")
            try:
                self.restart_driver()
                self.navigate_to_platform()
            except Exception as e:
                self.logger.error(f"Failed to restart driver: {e}")
                return False
        raise NotImplementedError("Subclass must implement volume_up method")
    
    def volume_down(self):
        """Decrease volume - to be implemented by subclasses"""
        if not self.is_driver_alive():
            self.logger.warning("Driver not alive, attempting restart...")
            try:
                self.restart_driver()
                self.navigate_to_platform()
            except Exception as e:
                self.logger.error(f"Failed to restart driver: {e}")
                return False
        raise NotImplementedError("Subclass must implement volume_down method")
    
    def close(self):
        """Close WebDriver and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info(f"{self.platform_name} WebDriver closed")
            except Exception as e:
                self.logger.error(f"Error closing {self.platform_name} WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None
        
        time.sleep(1)
        self._cleanup_chrome_processes()