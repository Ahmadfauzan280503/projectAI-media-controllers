"""
Complete YouTube Controller
File: src/media_controllers/youtube_controller.py
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_controller import BaseMediaController
import time
import logging

class YouTubeController(BaseMediaController):
    """YouTube media controller with improved reliability"""
    
    def __init__(self):
        super().__init__("YouTube", "https://www.youtube.com", timeout=30)
        self.current_video_url = None
        self.is_initialized = False
        try:
            self._initialize_youtube()
            self.is_initialized = True
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube: {e}")
    
    def _initialize_youtube(self):
        """Initialize YouTube with a test video"""
        try:
        
            success = self.navigate_to_platform()
            if not success:
                raise Exception("Failed to navigate to YouTube")
            
            time.sleep(3)
            
            self._find_and_play_test_video()
            
            self.logger.info("YouTube controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube: {e}")
            raise
    
    def _find_and_play_test_video(self):
        """Find and play a test video"""
        try:
            search_box = self.find_element_safe(By.NAME, "search_query", timeout=10)
            if search_box:
                search_box.clear()
                search_box.send_keys("lofi music")
                search_box.send_keys(Keys.RETURN)
                
                time.sleep(3)
                
                video_selectors = [
                    "a#video-title",
                    "a.ytd-video-renderer",
                    "#video-title-link"
                ]
                
                for selector in video_selectors:
                    video_link = self.find_element_safe(By.CSS_SELECTOR, selector, timeout=5)
                    if video_link:
                        self.current_video_url = video_link.get_attribute('href')
                        video_link.click()
                        
                        time.sleep(5)
                        
                        video_player = self.find_element_safe(By.CSS_SELECTOR, "video", timeout=15)
                        if video_player:
                            self.logger.info("Test video loaded successfully")
                            return
                        break
            
            self.logger.info("Search method failed, trying trending...")
            self.driver.get("https://www.youtube.com/feed/trending")
            time.sleep(3)
            
            trending_video = self.find_element_safe(By.CSS_SELECTOR, "a#video-title", timeout=10)
            if trending_video:
                trending_video.click()
                time.sleep(5)
                
                video_player = self.find_element_safe(By.CSS_SELECTOR, "video", timeout=15)
                if video_player:
                    self.logger.info("Trending video loaded successfully")
                    return
            
            self.logger.warning("Could not load any video, but continuing...")
                
        except Exception as e:
            self.logger.warning(f"Could not play test video: {e}")
    
    def _get_video_element(self):
        """Get the video element"""
        selectors = ["video", ".html5-main-video", "#movie_player video"]
        for selector in selectors:
            element = self.find_element_safe(By.CSS_SELECTOR, selector, timeout=3)
            if element:
                return element
        return None
    
    def _get_play_button(self):
        """Get the play/pause button"""
        selectors = [
            "button.ytp-play-button",
            ".ytp-play-button",
            "button[aria-label*='Play']",
            "button[aria-label*='Pause']",
            ".ytp-large-play-button"
        ]
        
        for selector in selectors:
            element = self.find_element_safe(By.CSS_SELECTOR, selector, timeout=2)
            if element:
                return element
        
        return None
    
    def play(self):
        """Play YouTube video"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_youtube()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
                self.logger.info("Play command sent via spacebar")
                time.sleep(0.5)  
                return True
            except Exception as e:
                self.logger.debug(f"Spacebar method failed: {e}")
            
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    if (videos[i].paused) {
                        videos[i].play();
                        return 'played';
                    }
                }
                return 'no_paused_video';
                """
                result = self.execute_script_safe(script)
                if result == 'played':
                    self.logger.info("Play command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript method failed: {e}")
            
            play_button = self._get_play_button()
            if play_button:
                try:
                    play_button.click()
                    self.logger.info("Play command sent via button click")
                    return True
                except Exception as e:
                    self.logger.debug(f"Button click failed: {e}")
            
            video_element = self._get_video_element()
            if video_element:
                try:
                    video_element.click()
                    self.logger.info("Play command sent via video click")
                    return True
                except Exception as e:
                    self.logger.debug(f"Video click failed: {e}")
            
            self.logger.warning("All play methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in play: {e}")
            return False
    
    def pause(self):
        """Pause YouTube video"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_youtube()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
                self.logger.info("Pause command sent via spacebar")
                time.sleep(0.5)
                return True
            except Exception as e:
                self.logger.debug(f"Spacebar method failed: {e}")
            
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    if (!videos[i].paused) {
                        videos[i].pause();
                        return 'paused';
                    }
                }
                return 'no_playing_video';
                """
                result = self.execute_script_safe(script)
                if result == 'paused':
                    self.logger.info("Pause command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript method failed: {e}")
            
            pause_button = self._get_play_button()
            if pause_button:
                try:
                    pause_button.click()
                    self.logger.info("Pause command sent via button click")
                    return True
                except Exception as e:
                    self.logger.debug(f"Button click failed: {e}")
            
            video_element = self._get_video_element()
            if video_element:
                try:
                    video_element.click()
                    self.logger.info("Pause command sent via video click")
                    return True
                except Exception as e:
                    self.logger.debug(f"Video click failed: {e}")
            
            self.logger.warning("All pause methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in pause: {e}")
            return False
    
    def next_track(self):
        """Next video"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_youtube()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SHIFT + "n")
                self.logger.info("Next video command sent via keyboard")
                time.sleep(1)
                return True
            except Exception as e:
                self.logger.debug(f"Keyboard shortcut failed: {e}")
            
            next_selectors = [
                "a.ytp-next-button",
                ".ytp-next-button", 
                "button[aria-label*='Next']",
                ".ytp-next-button.ytp-button"
            ]
            
            for selector in next_selectors:
                if self.click_element_safe(By.CSS_SELECTOR, selector, timeout=3):
                    self.logger.info("Next video command sent via button click")
                    time.sleep(1)
                    return True
            
            try:
                script = """
                var nextBtn = document.querySelector('a.ytp-next-button') || 
                             document.querySelector('.ytp-next-button');
                if (nextBtn) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'not_found';
                """
                result = self.execute_script_safe(script)
                if result == 'clicked':
                    self.logger.info("Next video command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript method failed: {e}")
            
            self.logger.warning("Could not execute next video command")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in next_track: {e}")
            return False
    
    def previous_track(self):
        """Previous video"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_youtube()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SHIFT + "p")
                self.logger.info("Previous video command sent via keyboard")
                time.sleep(1)
                return True
            except Exception as e:
                self.logger.debug(f"Keyboard shortcut failed: {e}")
            
            try:
                self.driver.back()
                time.sleep(2)
                self.logger.info("Previous video command sent via browser back")
                return True
            except Exception as e:
                self.logger.debug(f"Browser back failed: {e}")
            
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    videos[i].currentTime = 0;
                    return 'restarted';
                }
                return 'no_video';
                """
                result = self.execute_script_safe(script)
                if result == 'restarted':
                    self.logger.info("Video restarted from beginning")
                    return True
            except Exception as e:
                self.logger.debug(f"Video restart failed: {e}")
            
            self.logger.warning("Could not execute previous video command")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in previous_track: {e}")
            return False
    
    def volume_up(self):
        """Increase volume"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_youtube()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_UP)
                self.logger.info("Volume up command sent via keyboard")
                time.sleep(0.5)
                return True
            except Exception as e:
                self.logger.debug(f"Keyboard method failed: {e}")
            
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    var currentVolume = videos[i].volume;
                    videos[i].volume = Math.min(1.0, currentVolume + 0.1);
                    return 'volume_changed';
                }
                return 'no_video';
                """
                result = self.execute_script_safe(script)
                if result == 'volume_changed':
                    self.logger.info("Volume up command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript method failed: {e}")
            
            self.logger.warning("Could not execute volume up command")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in volume_up: {e}")
            return False
    
    def volume_down(self):
        """Decrease volume"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_youtube()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_DOWN)
                self.logger.info("Volume down command sent via keyboard")
                time.sleep(0.5)
                return True
            except Exception as e:
                self.logger.debug(f"Keyboard method failed: {e}")
            
            try:
                script = """
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    var currentVolume = videos[i].volume;
                    videos[i].volume = Math.max(0.0, currentVolume - 0.1);
                    return 'volume_changed';
                }
                return 'no_video';
                """
                result = self.execute_script_safe(script)
                if result == 'volume_changed':
                    self.logger.info("Volume down command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript method failed: {e}")
            
            self.logger.warning("Could not execute volume down command")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in volume_down: {e}")
            return False