"""
Hand Tracking Media Controller
Main entry point for the application - ENHANCED FIXED VERSION
"""

import os
import sys
import cv2
import time
import threading
import traceback
import signal
from pathlib import Path
from dotenv import load_dotenv

try:
    load_dotenv()
    print("✅ Environment variables loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load .env file: {e}")

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from src.hand_tracking.detector import HandDetector
    from src.hand_tracking.gestures import GestureRecognizer
    from src.media_controllers.base_controller import BaseMediaController
    from src.media_controllers.youtube_controller import YouTubeController
    from src.media_controllers.spotify_controller import SpotifyController
    from src.media_controllers.tiktok_controller import TikTokController
    from src.utils.logger import setup_logger
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Please ensure all required files are in place")
    sys.exit(1)

class MediaControllerApp:
    def __init__(self):
        self.logger = setup_logger()
        self.controllers = {}
        self.hand_detector = None
        self.gesture_recognizer = None
        self.cap = None
        self.running = False
        self.initialization_lock = threading.Lock()
        
        self.config = self._load_config()
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def _load_config(self):
        """Load configuration from environment variables with better defaults"""
        config = {
            'GESTURE_COOLDOWN': float(os.getenv('GESTURE_COOLDOWN', 1.5)),
            'CAMERA_INDEX': int(os.getenv('CAMERA_INDEX', 0)),
            'CAMERA_WIDTH': int(os.getenv('CAMERA_WIDTH', 640)),
            'CAMERA_HEIGHT': int(os.getenv('CAMERA_HEIGHT', 480)),
            'HAND_DETECTION_CONFIDENCE': float(os.getenv('HAND_DETECTION_CONFIDENCE', 0.7)),
            'HAND_TRACKING_CONFIDENCE': float(os.getenv('HAND_TRACKING_CONFIDENCE', 0.5)),
            'MAX_NUM_HANDS': int(os.getenv('MAX_NUM_HANDS', 1)),
            'GESTURE_THRESHOLD': float(os.getenv('GESTURE_THRESHOLD', 0.7)),
            'WEBDRIVER_TIMEOUT': int(os.getenv('WEBDRIVER_TIMEOUT', 60)),
            'MAX_RETRY_ATTEMPTS': int(os.getenv('MAX_RETRY_ATTEMPTS', 3)),
            'RETRY_DELAY': int(os.getenv('RETRY_DELAY', 3))
        }
        return config
        
    def show_menu(self):
        """Tampilkan menu pemilihan platform"""
        print("\n" + "="*60)
        print("🎮 HAND TRACKING MEDIA CONTROLLER v2.1 🎮")
        print("="*60)
        print("📱 PILIH PLATFORM MEDIA 📱")
        print("="*60)
        print("1. 🔴 YouTube")
        print("2. 🎵 Spotify")
        print("3. 📱 TikTok")
        print("4. 🌐 Semua platform")
        print("0. 🚪 Keluar")
        print("="*60)
        print("💡 Tips: Pastikan browser Chrome sudah terinstall dan diupdate!")
        print("💡 Tutup semua instance Chrome sebelum memulai!")
        print("="*60)

    def get_platform_choice(self):
        """Dapatkan pilihan platform user dengan validasi yang lebih baik"""
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                choice = input("Pilih platform (0-4): ").strip()
                if not choice:
                    print("❌ Pilihan tidak boleh kosong.")
                    attempts += 1
                    continue
                    
                choice = int(choice)
                if 0 <= choice <= 4:
                    return choice
                else:
                    print("❌ Pilihan tidak valid. Masukkan angka 0-4.")
                    attempts += 1
            except ValueError:
                print("❌ Masukkan angka yang valid.")
                attempts += 1
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
                
        print("❌ Terlalu banyak percobaan yang salah. Keluar...")
        return 0

    def _show_system_check(self):
        """Enhanced system check with better Chrome detection"""
        print("\n" + "="*50)
        print("🔍 ENHANCED SYSTEM CHECK")
        print("="*50)
        
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
        ]
        
        if sys.platform.startswith('linux'):
            chrome_paths.extend(['/usr/bin/google-chrome', '/usr/bin/chromium-browser'])
        elif sys.platform == 'darwin':
            chrome_paths.extend(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'])
        
        chrome_found = False
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_found = True
                chrome_path = path
                break
                
        if chrome_found:
            print(f"✅ Google Chrome: Found at {chrome_path}")
        else:
            print("❌ Google Chrome: Not found")
            print("   Please install Google Chrome from: https://www.google.com/chrome/")
            return False
        
        required_packages = {
            'cv2': 'opencv-python',
            'mediapipe': 'mediapipe', 
            'selenium': 'selenium',
            'requests': 'requests',
            'numpy': 'numpy'
        }
        
        missing_packages = []
        for package, pip_name in required_packages.items():
            try:
                __import__(package)
                print(f"✅ {package}: Installed")
            except ImportError:
                print(f"❌ {package}: Not found")
                missing_packages.append(pip_name)
                
        if missing_packages:
            print(f"\n💡 Install missing packages with:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        print("📷 Testing camera access...")
        test_cap = cv2.VideoCapture(self.config['CAMERA_INDEX'])
        if test_cap.isOpened():
            print("✅ Camera: Available")
            test_cap.release()
        else:
            print("❌ Camera: Not accessible")
            print("   Check if camera is in use by another application")
            return False
        
        print("✅ All system checks passed!")
        print("="*50)
        return True

    def initialize_controller(self, platform_choice):
        """Enhanced controller initialization with better error handling"""
        
        if not self._show_system_check():
            return None
        
        controllers = {}
        
        try:
            print("\n🔧 CONTROLLER INITIALIZATION")
            print("="*50)
            
            if platform_choice == 1:
                print("🔴 Initializing YouTube Controller...")
                controllers['youtube'] = self._safe_init_controller('YouTube', YouTubeController)
                
            elif platform_choice == 2:
                print("🎵 Initializing Spotify Controller...")
                controllers['spotify'] = self._safe_init_controller('Spotify', SpotifyController)
                
            elif platform_choice == 3:
                print("📱 Initializing TikTok Controller...")
                controllers['tiktok'] = self._safe_init_controller('TikTok', TikTokController)
                
            elif platform_choice == 4:
                print("🌐 Initializing All Controllers...")
                print("   ⚠️  This may take several minutes...")
                
                for name, controller_class in [
                    ('YouTube', YouTubeController),
                    ('Spotify', SpotifyController), 
                    ('TikTok', TikTokController)
                ]:
                    print(f"\n   Initializing {name}...")
                    controller = self._safe_init_controller(name, controller_class)
                    if controller:
                        controllers[name.lower()] = controller
                        time.sleep(2)  # Brief pause between initializations
            
            if not controllers:
                print("\n❌ No controllers were successfully initialized.")
                self._show_troubleshooting_guide()
                return None
                
            print(f"\n✅ Successfully initialized {len(controllers)} controller(s):")
            for controller_name in controllers.keys():
                print(f"   ✓ {controller_name.capitalize()}")
            
            print("="*50)
            return controllers
            
        except Exception as e:
            self.logger.error(f"Error in initialize_controller: {e}")
            print(f"❌ Critical error during controller initialization: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return None

    def _safe_init_controller(self, name, controller_class):
        """Safely initialize a controller with enhanced error handling"""
        try:
            with self.initialization_lock:
                print(f"   → Starting {name} controller...")
                
                controller = None
                exception = None
                initialization_complete = threading.Event()
                
                def init_controller():
                    nonlocal controller, exception
                    try:
                        
                        for attempt in range(self.config['MAX_RETRY_ATTEMPTS']):
                            try:
                                print(f"     Attempt {attempt + 1}/{self.config['MAX_RETRY_ATTEMPTS']}")
                                controller = controller_class()
                                if controller:
                                    break
                            except Exception as retry_e:
                                if attempt < self.config['MAX_RETRY_ATTEMPTS'] - 1:
                                    print(f"     Retry attempt {attempt + 1} failed: {retry_e}")
                                    time.sleep(self.config['RETRY_DELAY'])
                                else:
                                    raise retry_e
                    except Exception as e:
                        exception = e
                    finally:
                        initialization_complete.set()
                
                init_thread = threading.Thread(target=init_controller, daemon=True)
                init_thread.start()
                
                timeout = self.config['WEBDRIVER_TIMEOUT']
                if initialization_complete.wait(timeout=timeout):
                    if exception:
                        print(f"   ❌ {name} controller failed: {str(exception)[:100]}")
                        self.logger.error(f"{name} controller failed: {exception}")
                        return None
                        
                    if controller:
                        print(f"   ✅ {name} controller initialized successfully")
                        return controller
                    else:
                        print(f"   ❌ {name} controller returned None")
                        return None
                else:
                    print(f"   ❌ {name} controller initialization timed out after {timeout}s")
                    self.logger.warning(f"{name} controller timed out")
                    return None
                    
        except Exception as e:
            print(f"   ❌ {name} controller initialization error: {e}")
            self.logger.error(f"{name} controller initialization error: {e}")
            return None

    def _show_troubleshooting_guide(self):
        """Show comprehensive troubleshooting guide"""
        print("\n" + "="*60)
        print("🔧 TROUBLESHOOTING GUIDE")
        print("="*60)
        print("1. 🌐 Chrome Issues:")
        print("   • Update Chrome to latest version")
        print("   • Close ALL Chrome windows and processes")
        print("   • Disable Chrome extensions temporarily")
        print("   • Run as Administrator if needed")
        print()
        print("2. 🛡️  Security Software:")
        print("   • Temporarily disable antivirus/firewall")
        print("   • Add project folder to antivirus exclusions")
        print("   • Check Windows Defender settings")
        print()
        print("3. 🔧 System Issues:")
        print("   • Restart computer")
        print("   • Check available RAM (Chrome needs ~500MB per instance)")
        print("   • Ensure stable internet connection")
        print()
        print("4. 🐍 Python Environment:")
        print("   • Reinstall packages: pip install -r requirements.txt")
        print("   • Check Python version (3.8+ recommended)")
        print("   • Verify virtual environment activation")
        print("="*60)

    def display_gesture_info(self):
        """Display enhanced gesture information"""
        print("\n" + "="*60)
        print("🤲 GESTURE CONTROLS v2.1")
        print("="*60)
        print("✋ Open Hand              → ▶️  PLAY")
        print("✊ Closed Fist            → ⏸️  PAUSE")
        print("👍 Thumbs Up             → 🔊  Volume Up")
        print("👎 Thumbs Down           → 🔉  Volume Down")
        print("✌️  Peace Sign            → ⏭️  Next Track/Video")
        print("👆 Point Up              → ⏮️  Previous Track/Video")
        print("="*60)
        print("⌨️  KEYBOARD CONTROLS:")
        print("   'q' = Quit           'h' = Help")
        print("   'r' = Reconnect      'c' = Clear Console")
        print("   's' = Status         'f' = FPS Info")
        print("="*60)
        print("💡 TIPS:")
        print("   • Keep hand clearly visible to camera")
        print("   • Maintain good lighting")
        print("   • Make gestures deliberately and hold briefly")
        print("="*60)

    def execute_gesture_action(self, gesture):
        """Enhanced gesture execution with better error handling"""
        if not self.controllers:
            print("❌ No active controllers")
            return
            
        try:
            action_performed = False
            success_count = 0
            total_count = len(self.controllers)
            failed_controllers = []
            
            gesture_actions = {
                "membuka_tangan": ("play", "▶️ PLAY"),
                "menutup_tangan": ("pause", "⏸️ PAUSE"),
                "suka": ("volume_up", "🔊 VOLUME UP"),
                "tidak_suka": ("volume_down", "🔉 VOLUME DOWN"),
                "peace_sign": ("next_track", "⏭️ NEXT"),
                "point_up": ("previous_track", "⏮️ PREVIOUS")
            }
            
            if gesture not in gesture_actions:
                return
                
            action_method, action_display = gesture_actions[gesture]
            
            for controller_name, controller in self.controllers.items():
                try:
                    method = getattr(controller, action_method, None)
                    if method and callable(method):
                        method()
                        self.logger.info(f"{action_display} sent to {controller_name}")
                        success_count += 1
                        action_performed = True
                    else:
                        self.logger.warning(f"Method {action_method} not found in {controller_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error executing {gesture} on {controller_name}: {e}")
                    failed_controllers.append(controller_name)
                    
            if action_performed:
                status_msg = f"✅ {action_display} executed ({success_count}/{total_count} controllers)"
                print(status_msg)
                
                if failed_controllers:
                    print(f"⚠️  Failed on: {', '.join(failed_controllers)}")
                
        except Exception as e:
            self.logger.error(f"Critical error executing gesture action: {e}")
            print(f"❌ Critical error executing gesture: {e}")

    def initialize_components(self):
        """Enhanced component initialization"""
        try:
            print("\n🔧 INITIALIZING COMPONENTS")
            print("="*40)
            
            print("🤚 Initializing Hand Detector...")
            self.hand_detector = HandDetector(
                detection_confidence=self.config['HAND_DETECTION_CONFIDENCE'],
                tracking_confidence=self.config['HAND_TRACKING_CONFIDENCE'],
                max_num_hands=self.config['MAX_NUM_HANDS']
            )
            print("   ✅ Hand detector ready")
            
            print("🎯 Initializing Gesture Recognizer...")
            self.gesture_recognizer = GestureRecognizer(
                threshold=self.config['GESTURE_THRESHOLD'],
                cooldown=self.config['GESTURE_COOLDOWN']
            )
            print("   ✅ Gesture recognizer ready")
            
            print("📷 Initializing Camera...")
            camera_index = self.config['CAMERA_INDEX']
            
            for idx in range(camera_index, camera_index + 3):
                self.cap = cv2.VideoCapture(idx)
                if self.cap.isOpened():
                    print(f"   ✅ Camera {idx} opened successfully")
                    break
                self.cap.release()
                self.cap = None
            
            if not self.cap or not self.cap.isOpened():
                print("❌ Error: Could not open any camera")
                self._show_camera_troubleshooting()
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['CAMERA_WIDTH'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['CAMERA_HEIGHT'])
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
            
            ret, test_frame = self.cap.read()
            if not ret:
                print("❌ Error: Camera opened but cannot read frames")
                return False
                
            print("   ✅ Camera is working properly")
            print("="*40)
            print("✅ All components initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            print(f"❌ Error initializing components: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False

    def _show_camera_troubleshooting(self):
        """Show camera troubleshooting tips"""
        print("\n💡 CAMERA TROUBLESHOOTING:")
        print("   1. Check if camera is used by another application")
        print("   2. Try different CAMERA_INDEX values (0, 1, 2)")
        print("   3. Reconnect USB camera if external")
        print("   4. Update camera drivers")
        print("   5. Check Windows Camera privacy settings")

    def run_main_loop(self):
        """Enhanced main loop with better error handling and performance"""
        last_gesture_time = 0
        current_gesture = None
        gesture_cooldown = self.config['GESTURE_COOLDOWN']
        
        self.running = True
        frame_count = 0
        fps_history = []
        last_fps_time = time.time()
        performance_check_interval = 30  
        last_performance_check = time.time()
        
        try:
            print("\n🎥 Starting camera feed...")
            print("   Camera window will open shortly...")
            time.sleep(1)
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Could not read frame from camera")
                   
                    if self._reinitialize_camera():
                        continue
                    else:
                        break
                
                frame_count += 1
                frame = cv2.flip(frame, 1)
                
                try:
                    frame, hand_landmarks = self.hand_detector.detect_hands(frame)
                    
                    if hand_landmarks:
                        gesture = self.gesture_recognizer.recognize_gesture(hand_landmarks[0])
                        current_time = time.time()
                
                        if (gesture and 
                            gesture != current_gesture and 
                            current_time - last_gesture_time > gesture_cooldown):
                            
                            print(f"🎯 Gesture detected: {gesture}")
                            self.execute_gesture_action(gesture)
                            current_gesture = gesture
                            last_gesture_time = current_time
                        
                        if gesture:
                            gesture_display_map = {
                                "membuka_tangan": "✋ PLAY",
                                "menutup_tangan": "✊ PAUSE", 
                                "suka": "👍 VOL UP",
                                "tidak_suka": "👎 VOL DOWN",
                                "peace_sign": "✌️ NEXT",
                                "point_up": "👆 PREV"
                            }
                            
                            gesture_display = gesture_display_map.get(gesture, gesture.upper())
                            cv2.putText(frame, gesture_display, 
                                      (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                      1.0, (0, 255, 0), 2)
                        else:
                            cv2.putText(frame, "Hand detected - No gesture", 
                                      (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                      0.6, (0, 255, 255), 2)
                    else:
                        cv2.putText(frame, "No hand detected", 
                                  (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.7, (0, 255, 255), 2)
                    
                except Exception as e:
                    self.logger.error(f"Error in hand tracking: {e}")
                    cv2.putText(frame, "Hand tracking error", 
                               (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 0, 255), 2)
                
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    fps = frame_count / (current_time - last_fps_time)
                    fps_history.append(fps)
                    if len(fps_history) > 10:
                        fps_history.pop(0)
                    frame_count = 0
                    last_fps_time = current_time
                
                avg_fps = sum(fps_history) / len(fps_history) if fps_history else 30
                cv2.putText(frame, f"FPS: {int(avg_fps)}", 
                           (frame.shape[1] - 120, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                controller_status = f"Controllers: {len(self.controllers)} active"
                cv2.putText(frame, controller_status, 
                           (10, frame.shape[0] - 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                if self.controllers:
                    controller_names = ", ".join(self.controllers.keys())
                    cv2.putText(frame, f"Active: {controller_names}", 
                               (10, frame.shape[0] - 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                
                cv2.putText(frame, "Controls: q=Quit | h=Help | r=Reconnect | s=Status", 
                           (10, frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                if current_time - last_performance_check > performance_check_interval:
                    avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
                    if avg_fps < 15:
                        print(f"⚠️  Warning: Low FPS detected ({avg_fps:.1f})")
                        print("   Consider reducing camera resolution or closing other applications")
                    last_performance_check = current_time
                
                cv2.imshow('Hand Tracking Media Controller v2.1', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Quit command received")
                    break
                elif key == ord('h'):
                    self.display_gesture_info()
                elif key == ord('r'):
                    print("🔄 Reconnecting controllers...")
                    self.reconnect_controllers()
                elif key == ord('c'):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.display_gesture_info()
                elif key == ord('s'):
                    self.show_status()
                elif key == ord('f'):
                    avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
                    print(f"📊 Current FPS: {avg_fps:.2f}")
                    
        except KeyboardInterrupt:
            print("\n🛑 Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Critical error in main loop: {e}")
            print(f"❌ Critical error in main loop: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
        finally:
            self.running = False

    def _reinitialize_camera(self):
        """Attempt to reinitialize camera on failure"""
        try:
            print("🔄 Attempting to reinitialize camera...")
            if self.cap:
                self.cap.release()
            
            time.sleep(2)  # Wait before retry
            self.cap = cv2.VideoCapture(self.config['CAMERA_INDEX'])
            
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['CAMERA_WIDTH'])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['CAMERA_HEIGHT'])
                print("✅ Camera reinitialized successfully")
                return True
            else:
                print("❌ Failed to reinitialize camera")
                return False
                
        except Exception as e:
            print(f"❌ Error reinitializing camera: {e}")
            return False

    def show_status(self):
        """Enhanced status display"""
        print("\n" + "="*50)
        print("📊 APPLICATION STATUS v2.1")
        print("="*50)
        print(f"🤚 Hand Detection: {'✅ Active' if self.hand_detector else '❌ Inactive'}")
        print(f"🎯 Gesture Recognition: {'✅ Active' if self.gesture_recognizer else '❌ Inactive'}")
        print(f"📷 Camera: {'✅ Active' if self.cap and self.cap.isOpened() else '❌ Inactive'}")
        print(f"🎮 Controllers: {len(self.controllers)} active")
        
        if self.controllers:
            for name, controller in self.controllers.items():
                try:
                    
                    if hasattr(controller, 'driver') and controller.driver:
                        print(f"   ✓ {name.capitalize()} - Connected")
                    else:
                        print(f"   ⚠️  {name.capitalize()} - Connection unclear")
                except:
                    print(f"   ❌ {name.capitalize()} - Error checking status")
        
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"💾 Memory Usage: {memory_mb:.1f} MB")
        except ImportError:
            pass
            
        print("="*50)

    def reconnect_controllers(self):
        """Enhanced controller reconnection"""
        print("🔄 Attempting to reconnect controllers...")
        
        if not self.controllers:
            print("❌ No controllers to reconnect")
            return
            
        failed_controllers = []
        reconnected_controllers = []
        
        for controller_name, controller in list(self.controllers.items()):
            try:
                
                if hasattr(controller, 'driver') and controller.driver:
                    try:
                        
                        controller.driver.current_url
                        print(f"   ✅ {controller_name} - Still connected")
                        continue
                    except:
                        print(f"   ⚠️  {controller_name} - Connection lost, reconnecting...")
                        
                if hasattr(controller, 'close'):
                    try:
                        controller.close()
                    except:
                        pass
                        
                del self.controllers[controller_name]
                failed_controllers.append(controller_name)
                
                controller_classes = {
                    'youtube': YouTubeController,
                    'spotify': SpotifyController,
                    'tiktok': TikTokController
                }
                
                if controller_name in controller_classes:
                    new_controller = self._safe_init_controller(
                        controller_name.capitalize(), 
                        controller_classes[controller_name]
                    )
                    
                    if new_controller:
                        self.controllers[controller_name] = new_controller
                        reconnected_controllers.append(controller_name)
                        
            except Exception as e:
                self.logger.error(f"Error reconnecting {controller_name}: {e}")
                print(f"   ❌ {controller_name} - Reconnection failed: {e}")
                failed_controllers.append(controller_name)
        
        if reconnected_controllers:
            print(f"✅ Reconnected: {', '.join(reconnected_controllers)}")
        if failed_controllers:
            remaining_failed = [c for c in failed_controllers if c not in reconnected_controllers]
            if remaining_failed:
                print(f"❌ Failed to reconnect: {', '.join(remaining_failed)}")

    def cleanup(self):
        """Enhanced cleanup with better error handling"""
        print("🧹 Starting cleanup...")
        self.running = False
        
        try:
         
            if self.cap:
                self.cap.release()
                print("   ✅ Camera released")
                
            cv2.destroyAllWindows()
            print("   ✅ OpenCV windows closed")
            
            if self.controllers:
                for controller_name, controller in self.controllers.items():
                    try:
                        if hasattr(controller, 'close'):
                            controller.close()
                        print(f"   ✅ {controller_name} controller closed")
                        self.logger.info(f"Closed {controller_name} controller")
                    except Exception as e:
                        print(f"   ⚠️  Error closing {controller_name}: {e}")
                        self.logger.error(f"Error closing {controller_name}: {e}")
            
            print("✅ Cleanup completed successfully")
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            self.logger.error(f"Error during cleanup: {e}")

    def run(self):
        """Enhanced main application entry point"""
        try:
            print("🚀 Hand Tracking Media Controller v2.1")
            print("   Enhanced Error Handling & Auto WebDriver Setup")
            self.logger.info("Starting Hand Tracking Media Controller v2.1")
            
            self.show_menu()
            platform_choice = self.get_platform_choice()
            
            if platform_choice == 0:
                print("👋 Goodbye!")
                return
            
            print("\n⏳ Initializing system components...")
            print("   This may take a few moments...")
            
            self.controllers = self.initialize_controller(platform_choice)
            if not self.controllers:
                print("\n❌ Failed to initialize controllers.")
                input("\nPress Enter to exit...")
                return
            
            if not self.initialize_components():
                print("❌ Failed to initialize detection components. Exiting...")
                input("\nPress Enter to exit...")
                return
            
            print("\n🎉 System initialization complete!")
            print("📋 Setup Summary:")
            print(f"   • {len(self.controllers)} controller(s) active")
            print(f"   • Camera resolution: {self.config['CAMERA_WIDTH']}x{self.config['CAMERA_HEIGHT']}")
            print(f"   • Gesture cooldown: {self.config['GESTURE_COOLDOWN']}s")
            
            print("\n🎥 Starting camera feed in 3 seconds...")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            
            self.display_gesture_info()
            
            print("🎮 Application is now active!")
            print("   Position your hand in front of the camera")
            print("   Press 'q' in the camera window to quit\n")
            
            self.run_main_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in main: {e}")
            print(f"❌ Unexpected error: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            input("\nPress Enter to exit...")
        finally:
            self.cleanup()
            print("👋 Thank you for using Hand Tracking Media Controller!")

def main():
    """Enhanced entry point with better error handling"""
    try:
    
        script_dir = Path(__file__).parent.absolute()
        os.chdir(script_dir)
        
        logs_dir = script_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        print("🎮 Hand Tracking Media Controller v2.1")
        print("="*50)
        
        app = MediaControllerApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Please ensure all required packages are installed:")
        print("   pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()