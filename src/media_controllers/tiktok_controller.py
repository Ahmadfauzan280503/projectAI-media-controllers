# src/media_controllers/tiktok_controller.py

"""
TikTok Controller - FIXED VERSION
Enhanced TikTok web controller with proper inheritance
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import with correct inheritance
from .base_controller import BaseMediaController

class TikTokController(BaseMediaController):
    def __init__(self):
        # Initialize with proper base class parameters
        super().__init__("TikTok", "https://www.tiktok.com/foryou", timeout=30)
        self.is_initialized = False
        try:
            self._initialize_tiktok()
            self.is_initialized = True
        except Exception as e:
            self.logger.error(f"Failed to initialize TikTok: {e}")
    
    def _initialize_tiktok(self):
        """Initialize TikTok web"""
        try:
            # Navigate to TikTok
            success = self.navigate_to_platform()
            if not success:
                raise Exception("Failed to navigate to TikTok")
            
            # Wait for page to load and videos to appear
            time.sleep(5)
            
            # Try to find video elements
            video_found = self._wait_for_video()
            if not video_found:
                self.logger.warning("No videos found, but continuing...")
            
            self.logger.info("TikTok controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TikTok: {e}")
            raise
    
    def _wait_for_video(self):
        """Wait for TikTok videos to load"""
        try:
            video_selectors = [
                'video',
                '[data-e2e="video-player"] video',
                '.video-player video',
                'div[data-e2e="video-container"] video'
            ]
            
            for selector in video_selectors:
                video = self.find_element_safe(By.CSS_SELECTOR, selector, timeout=10)
                if video:
                    self.logger.info("TikTok video found")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error waiting for video: {e}")
            return False
    
    def _get_video_element(self):
        """Get the current video element"""
        video_selectors = [
            'video',
            '[data-e2e="video-player"] video',
            '.video-player video',
            'div[data-e2e="video-container"] video',
            '.tiktok-x6y88p-DivVideoContainer video'
        ]
        
        for selector in video_selectors:
            video = self.find_element_safe(By.CSS_SELECTOR, selector, timeout=3)
            if video:
                return video
        
        return None
    
    def play(self):
        """Play video"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_tiktok()
            
            # Method 1: Click on video to play/pause
            video = self._get_video_element()
            if video:
                try:
                    # Check if video is paused
                    is_paused = self.execute_script_safe("return arguments[0].paused;", video)
                    if is_paused:
                        video.click()
                        self.logger.info("TikTok play command sent via video click")
                        return True
                    else:
                        self.logger.info("TikTok video is already playing")
                        return True
                except Exception as e:
                    self.logger.debug(f"Video click failed: {e}")
            
            # Method 2: Try JavaScript play
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    if (videos[i].paused) {
                        videos[i].play();
                        return 'played';
                    }
                }
                return 'already_playing';
                """
                result = self.execute_script_safe(script)
                if result in ['played', 'already_playing']:
                    self.logger.info("TikTok play command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript play failed: {e}")
            
            # Method 3: Try spacebar
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
                self.logger.info("TikTok play command sent via spacebar")
                return True
            except Exception as e:
                self.logger.debug(f"Spacebar method failed: {e}")
            
            self.logger.warning("All TikTok play methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in TikTok play: {e}")
            return False
    
    def pause(self):
        """Pause video"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_tiktok()
            
            # Method 1: Click on video to pause
            video = self._get_video_element()
            if video:
                try:
                    # Check if video is playing
                    is_paused = self.execute_script_safe("return arguments[0].paused;", video)
                    if not is_paused:
                        video.click()
                        self.logger.info("TikTok pause command sent via video click")
                        return True
                    else:
                        self.logger.info("TikTok video is already paused")
                        return True
                except Exception as e:
                    self.logger.debug(f"Video click failed: {e}")
            
            # Method 2: Try JavaScript pause
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    if (!videos[i].paused) {
                        videos[i].pause();
                        return 'paused';
                    }
                }
                return 'already_paused';
                """
                result = self.execute_script_safe(script)
                if result in ['paused', 'already_paused']:
                    self.logger.info("TikTok pause command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript pause failed: {e}")
            
            # Method 3: Try spacebar
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
                self.logger.info("TikTok pause command sent via spacebar")
                return True
            except Exception as e:
                self.logger.debug(f"Spacebar method failed: {e}")
            
            self.logger.warning("All TikTok pause methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in TikTok pause: {e}")
            return False
    
    def volume_up(self):
        """Increase volume"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_tiktok()
            
            # TikTok web usually doesn't have visible volume controls
            # Use JavaScript to control video volume
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    var currentVolume = videos[i].volume;
                    videos[i].volume = Math.min(1.0, currentVolume + 0.25);
                    return 'volume_up_' + Math.round(videos[i].volume * 100);
                }
                return 'no_video';
                """
                result = self.execute_script_safe(script)
                if result and result.startswith('volume_up_'):
                    volume_percent = result.split('_')[-1]
                    self.logger.info(f"TikTok volume set to {volume_percent}%")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript volume control failed: {e}")
            
            # Try keyboard shortcut (if supported)
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_UP)
                self.logger.info("TikTok volume up command sent via keyboard")
                return True
            except Exception as e:
                self.logger.debug(f"Keyboard volume control failed: {e}")
            
            self.logger.warning("TikTok volume up failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in TikTok volume up: {e}")
            return False
    
    def volume_down(self):
        """Decrease volume"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_tiktok()
            
            # Use JavaScript to control video volume
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    var currentVolume = videos[i].volume;
                    videos[i].volume = Math.max(0.0, currentVolume - 0.25);
                    return 'volume_down_' + Math.round(videos[i].volume * 100);
                }
                return 'no_video';
                """
                result = self.execute_script_safe(script)
                if result and result.startswith('volume_down_'):
                    volume_percent = result.split('_')[-1]
                    self.logger.info(f"TikTok volume set to {volume_percent}%")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript volume control failed: {e}")
            
            # Try keyboard shortcut
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_DOWN)
                self.logger.info("TikTok volume down command sent via keyboard")
                return True
            except Exception as e:
                self.logger.debug(f"Keyboard volume control failed: {e}")
            
            self.logger.warning("TikTok volume down failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in TikTok volume down: {e}")
            return False
    
    def next_track(self):
        """Next video (scroll down)"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_tiktok()
            
            # Method 1: Scroll down to next video
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_DOWN)
                time.sleep(1)
                self.logger.info("TikTok next video command sent via scroll")
                return True
            except Exception as e:
                self.logger.debug(f"Scroll method failed: {e}")
            
            # Method 2: Try JavaScript scroll
            try:
                script = """
                window.scrollBy(0, window.innerHeight);
                return 'scrolled';
                """
                result = self.execute_script_safe(script)
                if result == 'scrolled':
                    self.logger.info("TikTok next video command sent via JavaScript scroll")
                    time.sleep(1)
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript scroll failed: {e}")
            
            # Method 3: Try Page Down key
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
                self.logger.info("TikTok next video command sent via Page Down")
                return True
            except Exception as e:
                self.logger.debug(f"Page Down method failed: {e}")
            
            self.logger.warning("TikTok next video failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in TikTok next video: {e}")
            return False
    
    def previous_track(self):
        """Previous video (scroll up)"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_tiktok()
            
            # Method 1: Scroll up to previous video
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_UP)
                time.sleep(1)
                self.logger.info("TikTok previous video command sent via scroll")
                return True
            except Exception as e:
                self.logger.debug(f"Scroll method failed: {e}")
            
            # Method 2: Try JavaScript scroll
            try:
                script = """
                window.scrollBy(0, -window.innerHeight);
                return 'scrolled';
                """
                result = self.execute_script_safe(script)
                if result == 'scrolled':
                    self.logger.info("TikTok previous video command sent via JavaScript scroll")
                    time.sleep(1)
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript scroll failed: {e}")
            
            # Method 3: Try Page Up key
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.PAGE_UP)
                time.sleep(1)
                self.logger.info("TikTok previous video command sent via Page Up")
                return True
            except Exception as e:
                self.logger.debug(f"Page Up method failed: {e}")
            
            self.logger.warning("TikTok previous video failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in TikTok previous video: {e}")
            return False