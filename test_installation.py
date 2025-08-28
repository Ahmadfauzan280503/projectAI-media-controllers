"""
Test installation script for Hand Tracking Media Controller
This script tests all components to ensure everything is working correctly
"""

import sys
import os
import time
import traceback
from pathlib import Path

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*50}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*50}")

def print_result(test_name, success, message=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")

def test_python_version():
    """Test Python version compatibility"""
    print_test_header("Python Version")
    
    version = sys.version_info
    success = version.major == 3 and version.minor >= 8
    
    print_result(
        f"Python {version.major}.{version.minor}.{version.micro}",
        success,
        "Requires Python 3.8+" if not success else "Compatible"
    )
    return success

def test_dependencies():
    """Test if all dependencies are installed"""
    print_test_header("Dependencies")
    
    dependencies = {
        'opencv-python': 'cv2',
        'mediapipe': 'mediapipe',
        'selenium': 'selenium',
        'webdriver-manager': 'webdriver_manager',
        'google-api-python-client': 'googleapiclient',
        'spotipy': 'spotipy',
        'python-dotenv': 'dotenv',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'colorlog': 'colorlog',
        'numpy': 'numpy'
    }
    
    all_success = True
    for package, import_name in dependencies.items():
        try:
            __import__(import_name)
            print_result(package, True)
        except ImportError as e:
            print_result(package, False, str(e))
            all_success = False
    
    return all_success

def test_camera_access():
    """Test camera access"""
    print_test_header("Camera Access")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        success = cap.isOpened()
        
        if success:
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print_result("Camera Access", True, f"Resolution: {width}x{height}")
            else:
                print_result("Camera Access", False, "Cannot read frames")
                success = False
        else:
            print_result("Camera Access", False, "Cannot open camera")
        
        cap.release()
        return success
        
    except Exception as e:
        print_result("Camera Access", False, str(e))
        return False

def test_mediapipe():
    """Test MediaPipe hand detection"""
    print_test_header("MediaPipe Hand Detection")
    
    try:
        import mediapipe as mp
        import cv2
        import numpy as np
        
        # Initialize MediaPipe
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        
        # Create a dummy image with a hand-like shape
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(dummy_image, (320, 240), 50, (255, 255, 255), -1)  # Palm
        cv2.circle(dummy_image, (300, 200), 20, (255, 255, 255), -1)  # Finger
        
        # Process the image
        results = hands.process(cv2.cvtColor(dummy_image, cv2.COLOR_BGR2RGB))
        
        hands.close()
        
        print_result("MediaPipe Initialization", True)
        print_result("Hand Detection Model", True, "Model loaded successfully")
        
        return True
        
    except Exception as e:
        print_result("MediaPipe", False, str(e))
        return False

def test_web_driver():
    """Test Selenium WebDriver setup"""
    print_test_header("Web Driver Setup")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test navigation
        driver.get("https://www.google.com")
        title = driver.title
        
        driver.quit()
        
        print_result("ChromeDriver Installation", True)
        print_result("Browser Navigation", True, f"Title: {title[:30]}...")
        
        return True
        
    except Exception as e:
        print_result("Web Driver", False, str(e))
        return False

def test_project_structure():
    """Test project file structure"""
    print_test_header("Project Structure")
    
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        '.env.example',
        'src/__init__.py',
        'src/hand_tracking/__init__.py',
        'src/hand_tracking/detector.py',
        'src/hand_tracking/gestures.py',
        'src/media_controllers/__init__.py',
        'src/media_controllers/base_controller.py',
        'src/media_controllers/youtube_controller.py',
        'src/media_controllers/spotify_controller.py',
        'src/media_controllers/tiktok_controller.py',
        'src/api/__init__.py',
        'src/api/youtube_api.py',
        'src/api/spotify_api.py',
        'src/utils/__init__.py',
        'src/utils/logger.py'
    ]
    
    all_success = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_result(file_path, exists)
        if not exists:
            all_success = False
    
    # Test directories
    required_dirs = ['src', 'src/hand_tracking', 'src/media_controllers', 'src/api', 'src/utils']
    for dir_path in required_dirs:
        exists = Path(dir_path).is_dir()
        print_result(f"{dir_path}/", exists, "Directory")
        if not exists:
            all_success = False
    
    return all_success

def test_module_imports():
    """Test importing project modules"""
    print_test_header("Module Imports")
    
    # Add src to Python path
    src_path = Path(__file__).parent / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    modules_to_test = [
        ('src.hand_tracking.detector', 'HandDetector'),
        ('src.hand_tracking.gestures', 'GestureRecognizer'),
        ('src.media_controllers.base_controller', 'BaseMediaController'),
        ('src.media_controllers.youtube_controller', 'YouTubeController'),
        ('src.media_controllers.spotify_controller', 'SpotifyController'),
        ('src.media_controllers.tiktok_controller', 'TikTokController'),
        ('src.api.youtube_api', 'YouTubeAPI'),
        ('src.api.spotify_api', 'SpotifyAPI'),
        ('src.utils.logger', 'setup_logger')
    ]
    
    all_success = True
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_result(f"{module_name}.{class_name}", True)
        except Exception as e:
            print_result(f"{module_name}.{class_name}", False, str(e))
            all_success = False
    
    return all_success

def test_configuration():
    """Test configuration setup"""
    print_test_header("Configuration")
    
    try:
        import config
        
        # Test required configuration variables
        required_configs = [
            'HAND_DETECTION_CONFIDENCE',
            'HAND_TRACKING_CONFIDENCE',
            'MAX_NUM_HANDS',
            'GESTURE_THRESHOLD',
            'GESTURE_COOLDOWN',
            'CAMERA_INDEX',
            'CAMERA_WIDTH',
            'CAMERA_HEIGHT'
        ]
        
        all_success = True
        for config_var in required_configs:
            has_config = hasattr(config, config_var)
            print_result(config_var, has_config)
            if not has_config:
                all_success = False
        
        # Test .env file
        env_exists = Path('.env').exists()
        env_example_exists = Path('.env.example').exists()
        
        print_result(".env.example", env_example_exists)
        print_result(".env", env_exists, "Create from .env.example if missing" if not env_exists else "")
        
        return all_success and env_example_exists
        
    except Exception as e:
        print_result("Configuration", False, str(e))
        return False

def test_hand_detector():
    """Test hand detector functionality"""
    print_test_header("Hand Detector Functionality")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from hand_tracking.detector import HandDetector
        import numpy as np
        
        # Initialize detector
        detector = HandDetector()
        print_result("HandDetector Initialization", True)
        
        # Create dummy image
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test detection (should return no hands for black image)
        annotated_image, landmarks = detector.detect_hands(dummy_image)
        
        success = annotated_image is not None
        print_result("Hand Detection Process", success)
        
        # Test utility methods
        if landmarks:
            fingers_up = detector.get_fingers_up(landmarks[0])
            print_result("Finger Detection", isinstance(fingers_up, list))
        else:
            print_result("No Hands Detected", True, "Expected for blank image")
        
        return True
        
    except Exception as e:
        print_result("Hand Detector", False, str(e))
        traceback.print_exc()
        return False

def test_gesture_recognizer():
    """Test gesture recognizer functionality"""
    print_test_header("Gesture Recognizer")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from hand_tracking.gestures import GestureRecognizer
        
        # Initialize recognizer
        recognizer = GestureRecognizer()
        print_result("GestureRecognizer Initialization", True)
        
        # Test with dummy landmarks (21 points for MediaPipe hand)
        dummy_landmarks = [[i*10, i*10] for i in range(21)]
        
        # Test gesture recognition
        gesture = recognizer.recognize_gesture(dummy_landmarks)
        print_result("Gesture Recognition Process", True, f"Result: {gesture or 'No gesture'}")
        
        # Test available gestures
        gestures = recognizer.get_all_possible_gestures()
        print_result("Available Gestures", len(gestures) > 0, f"Count: {len(gestures)}")
        
        return True
        
    except Exception as e:
        print_result("Gesture Recognizer", False, str(e))
        traceback.print_exc()
        return False

def test_logging():
    """Test logging functionality"""
    print_test_header("Logging System")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from utils.logger import setup_logger, PerformanceLogger, GestureLogger
        
        # Test main logger
        logger = setup_logger("TestLogger")
        logger.info("Test log message")
        print_result("Main Logger", True)
        
        # Test performance logger
        perf_logger = PerformanceLogger(logger)
        perf_logger.start_timer("test_operation")
        time.sleep(0.1)
        perf_logger.end_timer("test_operation")
        print_result("Performance Logger", True)
        
        # Test gesture logger
        gesture_logger = GestureLogger()
        gesture_logger.log_gesture("test_gesture", 0.95, 50.0)
        print_result("Gesture Logger", True)
        
        # Check log file creation
        log_file_exists = Path("logs/app.log").exists()
        print_result("Log File Creation", log_file_exists)
        
        return True
        
    except Exception as e:
        print_result("Logging", False, str(e))
        traceback.print_exc()
        return False

def test_api_integration():
    """Test API integration (without actual API calls)"""
    print_test_header("API Integration")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from api.youtube_api import YouTubeAPI
        from api.spotify_api import SpotifyAPI
        
        youtube_api = YouTubeAPI("")  # Empty API key for testing
        print_result("YouTube API Initialization", True)
        
        # Test Spotify API initialization
        spotify_api = SpotifyAPI("", "")  # Empty credentials for testing
        print_result("Spotify API Initialization", True)
        
        return True
        
    except Exception as e:
        print_result("API Integration", False, str(e))
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and return summary"""
    print("🧪 HAND TRACKING MEDIA CONTROLLER - INSTALLATION TEST")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Camera Access", test_camera_access),
        ("MediaPipe", test_mediapipe),
        ("Web Driver", test_web_driver),
        ("Project Structure", test_project_structure),
        ("Module Imports", test_module_imports),
        ("Configuration", test_configuration),
        ("Hand Detector", test_hand_detector),
        ("Gesture Recognizer", test_gesture_recognizer),
        ("Logging System", test_logging),
        ("API Integration", test_api_integration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_result(test_name, False, f"Test error: {e}")
            results[test_name] = False
    
    print_test_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your installation is working correctly!")
        print("🚀 You can now run: python main.py")
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
        print("❌ Please check the failed tests above")
        print("💡 Try running install.py again or check the troubleshooting guide")
    
    print("\n" + "=" * 60)
    
    return passed == total

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n🛑 Tests cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())