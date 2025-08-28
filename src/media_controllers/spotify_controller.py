"""
Spotify Controller - FIXED VERSION
Enhanced Spotify Web Player controller with proper inheritance
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_controller import BaseMediaController

class SpotifyController(BaseMediaController):
    def __init__(self):

        super().__init__("Spotify", "https://open.spotify.com", timeout=30)
        self.current_track_url = None
        self.is_initialized = False
        try:
            self._initialize_spotify()
            self.is_initialized = True
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify: {e}")
    
    def _initialize_spotify(self):
        """Initialize Spotify Web Player"""
        try:
           
            success = self.navigate_to_platform()
            if not success:
                raise Exception("Failed to navigate to Spotify")
            
            time.sleep(5)
            
            self.logger.info("Spotify controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify: {e}")
            raise
    
    def play(self):
        """Play music"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_spotify()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
                self.logger.info("Spotify play command sent via spacebar")
                time.sleep(0.5)
                return True
            except Exception as e:
                self.logger.debug(f"Spacebar method failed: {e}")
            
            play_selectors = [
                'button[data-testid="control-button-playpause"]',
                'button[aria-label="Play"]',
                'button[title="Play"]',
                '.player-controls__buttons button[aria-label*="Play"]',
                '.spoticon-play-16',
                'button.control-button'
            ]
            
            for selector in play_selectors:
                if self.click_element_safe(By.CSS_SELECTOR, selector, timeout=3):
                    self.logger.info("Spotify play command sent via button click")
                    return True
            
            try:
                script = """
                var playButtons = document.querySelectorAll('button[data-testid="control-button-playpause"], button[aria-label*="Play"]');
                for (var i = 0; i < playButtons.length; i++) {
                    playButtons[i].click();
                    return 'clicked';
                }
                return 'not_found';
                """
                result = self.execute_script_safe(script)
                if result == 'clicked':
                    self.logger.info("Spotify play command sent via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript method failed: {e}")
            
            self.logger.warning("All Spotify play methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in Spotify play: {e}")
            return False
    
    def pause(self):
        """Pause music"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_spotify()
            
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
                self.logger.info("Spotify pause command sent via spacebar")
                time.sleep(0.5)
                return True
            except Exception as e:
                self.logger.debug(f"Spacebar method failed: {e}")
            
            pause_selectors = [
                'button[data-testid="control-button-playpause"]',
                'button[aria-label="Pause"]',
                'button[title="Pause"]',
                '.player-controls__buttons button[aria-label*="Pause"]',
                '.spoticon-pause-16'
            ]
            
            for selector in pause_selectors:
                if self.click_element_safe(By.CSS_SELECTOR, selector, timeout=3):
                    self.logger.info("Spotify pause command sent via button click")
                    return True
            
            self.logger.warning("All Spotify pause methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in Spotify pause: {e}")
            return False
    
    def volume_up(self):
        """Increase volume"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_spotify()
            
            volume_selectors = [
                'button[data-testid="volume-bar-toggle-mute-button"]',
                '.volume-bar__slider-container',
                'input[data-testid="volume-bar-slider"]'
            ]
            
            for selector in volume_selectors:
                element = self.find_element_safe(By.CSS_SELECTOR, selector, timeout=3)
                if element:
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(element).click().perform()
                        self.logger.info("Spotify volume up command sent")
                        return True
                    except Exception as e:
                        self.logger.debug(f"Volume control failed: {e}")
            
            try:
                script = """
                var audio = document.querySelector('audio');
                if (audio) {
                    audio.volume = Math.min(1.0, audio.volume + 0.1);
                    return 'volume_increased';
                }
                return 'no_audio';
                """
                result = self.execute_script_safe(script)
                if result == 'volume_increased':
                    self.logger.info("Spotify volume increased via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript volume control failed: {e}")
            
            self.logger.warning("Spotify volume up failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in Spotify volume up: {e}")
            return False
    
    def volume_down(self):
        """Decrease volume"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_spotify()
            
            try:
                script = """
                var audio = document.querySelector('audio');
                if (audio) {
                    audio.volume = Math.max(0.0, audio.volume - 0.1);
                    return 'volume_decreased';
                }
                return 'no_audio';
                """
                result = self.execute_script_safe(script)
                if result == 'volume_decreased':
                    self.logger.info("Spotify volume decreased via JavaScript")
                    return True
            except Exception as e:
                self.logger.debug(f"JavaScript volume control failed: {e}")
            
            self.logger.warning("Spotify volume down failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in Spotify volume down: {e}")
            return False
    
    def next_track(self):
        """Next track"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_spotify()
            
            next_selectors = [
                'button[data-testid="control-button-skip-forward"]',
                'button[aria-label="Next"]',
                'button[title="Next"]',
                '.player-controls__buttons button[aria-label*="Next"]',
                'button.control-button-skip-forward'
            ]
            
            for selector in next_selectors:
                if self.click_element_safe(By.CSS_SELECTOR, selector, timeout=3):
                    self.logger.info("Spotify next track command sent")
                    return True
            
            self.logger.warning("Spotify next track failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in Spotify next track: {e}")
            return False
    
    def previous_track(self):
        """Previous track"""
        try:
            if not self.is_driver_alive():
                self.logger.warning("Driver not alive, restarting...")
                self.restart_driver()
                self._initialize_spotify()
            
            prev_selectors = [
                'button[data-testid="control-button-skip-back"]',
                'button[aria-label="Previous"]',
                'button[title="Previous"]',
                '.player-controls__buttons button[aria-label*="Previous"]',
                'button.control-button-skip-back'
            ]
            
            for selector in prev_selectors:
                if self.click_element_safe(By.CSS_SELECTOR, selector, timeout=3):
                    self.logger.info("Spotify previous track command sent")
                    return True
            
            self.logger.warning("Spotify previous track failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in Spotify previous track: {e}")
            return False