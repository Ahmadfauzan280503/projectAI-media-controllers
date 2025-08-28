"""
Configuration file untuk Media Controller
Simpan sebagai config.py di root project
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
DRIVERS_DIR = PROJECT_ROOT / "drivers"
CONFIG_DIR = PROJECT_ROOT / "config"

LOGS_DIR.mkdir(exist_ok=True)
DRIVERS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0))
CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', 640))
CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', 480))
CAMERA_FPS = int(os.getenv('CAMERA_FPS', 30))

HAND_DETECTION_CONFIDENCE = float(os.getenv('HAND_DETECTION_CONFIDENCE', 0.7))
HAND_TRACKING_CONFIDENCE = float(os.getenv('HAND_TRACKING_CONFIDENCE', 0.5))
MAX_NUM_HANDS = int(os.getenv('MAX_NUM_HANDS', 1))

GESTURE_THRESHOLD = float(os.getenv('GESTURE_THRESHOLD', 0.7))
GESTURE_COOLDOWN = float(os.getenv('GESTURE_COOLDOWN', 1.0))

CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')
CHROME_HEADLESS = os.getenv('CHROME_HEADLESS', 'false').lower() == 'true'
CHROME_WINDOW_SIZE = os.getenv('CHROME_WINDOW_SIZE', '1280x720')
WEBDRIVER_TIMEOUT = int(os.getenv('WEBDRIVER_TIMEOUT', 30))
MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 2))

BROWSER_IMPLICIT_WAIT = int(os.getenv('BROWSER_IMPLICIT_WAIT', 10))
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', 30))
SCRIPT_TIMEOUT = int(os.getenv('SCRIPT_TIMEOUT', 30))

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', '')

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

APP_NAME = "Hand Tracking Media Controller"
APP_VERSION = "2.0"
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage", 
    "--disable-gpu",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--mute-audio",
    f"--window-size={CHROME_WINDOW_SIZE}",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "--log-level=3"
]

if CHROME_HEADLESS:
    CHROME_OPTIONS.append("--headless")

PLATFORM_URLS = {
    'youtube': 'https://www.youtube.com',
    'spotify': 'https://open.spotify.com',
    'tiktok': 'https://www.tiktok.com'
}

# Gesture mappings
GESTURE_MAPPINGS = {
    'membuka_tangan': {
        'action': 'play',
        'display': '✋ PLAY',
        'description': 'Membuka tangan untuk memutar media'
    },
    'menutup_tangan': {
        'action': 'pause', 
        'display': '✊ PAUSE',
        'description': 'Menutup tangan untuk menjeda media'
    },
    'suka': {
        'action': 'volume_up',
        'display': '👍 VOL UP', 
        'description': 'Thumbs up untuk menaikkan volume'
    },
    'tidak_suka': {
        'action': 'volume_down',
        'display': '👎 VOL DOWN',
        'description': 'Thumbs down untuk menurunkan volume'  
    },
    'peace_sign': {
        'action': 'next_track',
        'display': '✌️ NEXT',
        'description': 'Peace sign untuk lagu/video berikutnya'
    },
    'point_up': {
        'action': 'previous_track', 
        'display': '👆 PREV',
        'description': 'Point up untuk lagu/video sebelumnya'
    }
}

def validate_config():
    """Validate configuration settings"""
    errors = []
    warnings = []
    
    if not LOGS_DIR.exists():
        warnings.append(f"Logs directory does not exist: {LOGS_DIR}")
    
    if CAMERA_INDEX < 0:
        errors.append("CAMERA_INDEX must be >= 0")
    
    if CAMERA_WIDTH <= 0 or CAMERA_HEIGHT <= 0:
        errors.append("Camera dimensions must be > 0")
    
    if not (0.0 <= HAND_DETECTION_CONFIDENCE <= 1.0):
        errors.append("HAND_DETECTION_CONFIDENCE must be between 0.0 and 1.0")
    
    if not (0.0 <= HAND_TRACKING_CONFIDENCE <= 1.0):
        errors.append("HAND_TRACKING_CONFIDENCE must be between 0.0 and 1.0")
    
    if not (0.0 <= GESTURE_THRESHOLD <= 1.0):
        errors.append("GESTURE_THRESHOLD must be between 0.0 and 1.0")
    
    if not YOUTUBE_API_KEY:
        warnings.append("YOUTUBE_API_KEY not set")
    
    if not SPOTIFY_CLIENT_ID:
        warnings.append("SPOTIFY_CLIENT_ID not set") 
    
    return errors, warnings

def print_config_summary():
    """Print configuration summary"""
    print("\n" + "="*50)
    print(f"📋 {APP_NAME} v{APP_VERSION} Configuration")
    print("="*50)
    print(f"🎥 Camera: Index {CAMERA_INDEX}, {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    print(f"🤚 Hand Detection: {HAND_DETECTION_CONFIDENCE} confidence")
    print(f"🎯 Gesture Threshold: {GESTURE_THRESHOLD}")
    print(f"⏱️ Gesture Cooldown: {GESTURE_COOLDOWN}s")
    print(f"🌐 WebDriver Timeout: {WEBDRIVER_TIMEOUT}s")
    print(f"📝 Log Level: {LOG_LEVEL}")
    print(f"🔑 YouTube API: {'✅ Set' if YOUTUBE_API_KEY else '❌ Not Set'}")
    print(f"🔑 Spotify API: {'✅ Set' if SPOTIFY_CLIENT_ID else '❌ Not Set'}")
    print("="*50)

if __name__ == "__main__":
    # Validate configuration when run directly
    errors, warnings = validate_config()
    
    print_config_summary()
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print("\n⚠️ Configuration Warnings:")  
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors:
        print("\n✅ Configuration is valid!")