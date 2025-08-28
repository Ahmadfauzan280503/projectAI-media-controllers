"""
Skrip jalankan alternatif dengan menu dan opsi yang ditingkatkan
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_banner():
    """Mencetak pada sistem program"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🎮 HAND TRACKING MEDIA CONTROLLER 🎮              ║
    ║                                                           ║
    ║     Control your media with hand gestures!                ║
    ║     Supports YouTube, Spotify, and TikTok                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_menu():
    """Print main menu"""
    print("\n" + "="*50)
    print("📋 MAIN MENU")
    print("="*50)
    print("1. 🚀 Run Application")
    print("2. 🧪 Test Installation") 
    print("3. ⚙️  Configure Settings")
    print("4. 📊 View Logs")
    print("5. 🔧 Troubleshooting")
    print("6. ℹ️  About")
    print("0. 🚪 Exit")
    print("="*50)

def check_installation():
    """Quick installation check"""
    print("🔍 Checking installation...")
    
    critical_files = ['main.py', 'config.py', 'src/hand_tracking/detector.py']
    missing_files = []
    
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing critical files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n💡 Please run install.py first")
        return False
    
    try:
        import cv2
        import mediapipe
        import selenium
        print("✅ Installation looks good")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Please run: pip install -r requirements.txt")
        return False

def run_application():
    """Run main application"""
    print("🚀 Starting Hand Tracking Media Controller...")
    
    if not check_installation():
        input("\nTekan Enter untuk melanjutkan...")
        return
    
    try:
    
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Aplikasi dihentikan oleh user")
    except Exception as e:
        print(f"❌ Kesalahan saat menjalankan aplikasi: {e}")
    
    input("\nTekan Enter untuk melanjutkan...")

def run_tests():
    """Run installation tests"""
    print("🧪 Running installation tests...")
    
    try:
        subprocess.run([sys.executable, "test_installation.py"])
    except FileNotFoundError:
        print("❌ test_installation.py not found")
    except Exception as e:
        print(f"❌ Error running tests: {e}")
    
    input("\nTekan Enter untuk melanjutkan...")

def configure_settings():
    """Configure application settings"""
    print("⚙️ Configuration Menu")
    print("="*30)
    print("1. Edit .env file (API keys)")
    print("2. Edit config.py")
    print("3. View current settings")
    print("0. Back to main menu")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        edit_env_file()
    elif choice == "2":
        edit_config_file()
    elif choice == "3":
        view_settings()
    elif choice == "0":
        return
    else:
        print("Invalid choice")
    
    input("\nTekan Enter untuk melanjutkan...")

def edit_env_file():
    """Edit .env file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env from template...")
        env_file.write_text(env_example.read_text())
    
    if env_file.exists():
        print(f"Opening {env_file} for editing...")
        try:
            if sys.platform == "win32":
                os.startfile(env_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(env_file)])
            else:
                subprocess.run(["xdg-open", str(env_file)])
        except:
            print(f"Please edit {env_file} manually")
    else:
        print("❌ .env file not found")

def edit_config_file():
    """Edit config.py file"""
    config_file = Path("config.py")
    
    if config_file.exists():
        print(f"Opening {config_file} for editing...")
        try:
            if sys.platform == "win32":
                os.startfile(config_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(config_file)])
            else:
                subprocess.run(["xdg-open", str(config_file)])
        except:
            print(f"Please edit {config_file} manually")
    else:
        print("❌ config.py not found")

def view_settings():
    """View current settings"""
    print("📋 Current Settings")
    print("="*30)
    
    try:
        import config
        
        settings = [
            ("Hand Detection Confidence", getattr(config, 'HAND_DETECTION_CONFIDENCE', 'Not set')),
            ("Hand Tracking Confidence", getattr(config, 'HAND_TRACKING_CONFIDENCE', 'Not set')),
            ("Max Number of Hands", getattr(config, 'MAX_NUM_HANDS', 'Not set')),
            ("Gesture Threshold", getattr(config, 'GESTURE_THRESHOLD', 'Not set')),
            ("Gesture Cooldown", getattr(config, 'GESTURE_COOLDOWN', 'Not set')),
            ("Camera Index", getattr(config, 'CAMERA_INDEX', 'Not set')),
            ("Camera Width", getattr(config, 'CAMERA_WIDTH', 'Not set')),
            ("Camera Height", getattr(config, 'CAMERA_HEIGHT', 'Not set')),
        ]
        
        for setting, value in settings:
            print(f"{setting}: {value}")
        
        env_file = Path(".env")
        if env_file.exists():
            print("\n🔑 API Keys:")
            content = env_file.read_text()
            
            keys = ["YOUTUBE_API_KEY", "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"]
            for key in keys:
                if key in content and not content.split(f"{key}=")[1].split()[0].endswith("_here"):
                    print(f"{key}: ✅ Set")
                else:
                    print(f"{key}: ❌ Not set")
        
    except Exception as e:
        print(f"❌ Error reading settings: {e}")

def view_logs():
    """View application logs"""
    print("📊 Log Viewer")
    print("="*20)
    
    log_file = Path("logs/app.log")
    
    if not log_file.exists():
        print("📝 No log file found")
        print("💡 Run the application first to generate logs")
        input("\nTekan Enter untuk melanjutkan...")
        return
    
    print("1. View last 20 lines")
    print("2. View last 50 lines") 
    print("3. View all logs")
    print("4. Open log file")
    print("0. Back")
    
    choice = input("\nSelect option: ").strip()
    
    try:
        if choice == "1":
            show_log_lines(log_file, 20)
        elif choice == "2":
            show_log_lines(log_file, 50)
        elif choice == "3":
            show_log_lines(log_file, None)
        elif choice == "4":
            open_log_file(log_file)
        elif choice == "0":
            return
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"❌ Error viewing logs: {e}")
    
    input("\nTekan Enter untuk melanjutkan...")

def show_log_lines(log_file, num_lines):
    """Show log lines"""
    content = log_file.read_text()
    lines = content.splitlines()
    
    if num_lines is None:
        display_lines = lines
    else:
        display_lines = lines[-num_lines:]
    
    print(f"\n📊 Log Content ({'Last ' + str(num_lines) + ' lines' if num_lines else 'All lines'}):")
    print("-" * 50)
    
    for line in display_lines:
        print(line)
    
    print("-" * 50)

def open_log_file(log_file):
    """Open log file in default editor"""
    try:
        if sys.platform == "win32":
            os.startfile(log_file)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(log_file)])
        else:
            subprocess.run(["xdg-open", str(log_file)])
        print("📝 Log file opened in default editor")
    except:
        print(f"Please open {log_file} manually")

def troubleshooting():
    """Show troubleshooting information"""
    print("🔧 Troubleshooting Guide")
    print("="*30)
    print()
    
    issues = [
        {
            "problem": "Camera not detected",
            "solution": "1. Check camera connection\n2. Try different CAMERA_INDEX in config.py\n3. Test: python -c \"import cv2; print(cv2.VideoCapture(0).isOpened())\""
        },
        {
            "problem": "ChromeDriver issues", 
            "solution": "1. Update: pip install --upgrade webdriver-manager\n2. Install Chrome browser\n3. Check Chrome version compatibility"
        },
        {
            "problem": "API key errors",
            "solution": "1. Check .env file has correct API keys\n2. Verify keys are valid and active\n3. Check API quota limits"
        },
        {
            "problem": "Hand detection not working",
            "solution": "1. Ensure good lighting\n2. Clean background\n3. Adjust HAND_DETECTION_CONFIDENCE in config.py"
        },
        {
            "problem": "Performance issues",
            "solution": "1. Lower camera resolution in config.py\n2. Increase GESTURE_COOLDOWN\n3. Close unnecessary applications"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"{i}. Problem: {issue['problem']}")
        print(f"   Solution: {issue['solution']}")
        print()
    
    print("💡 For more help:")
    print("   - Check README.md")
    print("   - Run test_installation.py")
    print("   - Create issue on GitHub")
    
    input("\nPress Enter to continue...")

def show_about():
    """Tampilkan tentang informasi"""
    print("ℹ️ Tentang Hand Tracking Media Controller")
    print("="*40)
    print()
    print("Version: 1.0.0")
    print("Author: AHMAD FAUZAN")
    print("License: MIT")
    print()
    print("Description:")
    print("Control media playback on YouTube, Spotify, and TikTok")
    print("using hand gestures detected through computer vision.")
    print()
    print("Technologies Used:")
    print("- MediaPipe (Hand tracking)")
    print("- OpenCV (Computer vision)")
    print("- Selenium (Web automation)")
    print("- Python 3.8+")
    print()
    print("Gerakan yang Didukung:")
    print("✋ Membuka Tangan    → Play")
    print("✊ Menutup Tangan    → Pause")
    print("👍 suka              → Volume Up")
    print("👎 Tidak Suka        → Volume Down")
    print("✌️ Peace Sign        → Next Track/Video")
    print("👆 Point Up          → Previous Track/Video")
    print()
    print("GitHub: https://github.com/Ahmadfauzan280503/Media-controller")
    
    input("\nTekan Enter untuk melanjutkan...")

def main():
    """Main menu loop"""
    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print_banner()
            print_menu()
            
            choice = input("Pilih sebuah opsi (0-6): ").strip()
            
            if choice == "1":
                run_application()
            elif choice == "2":
                run_tests()
            elif choice == "3":
                configure_settings()
            elif choice == "4":
                view_logs()
            elif choice == "5":
                troubleshooting()
            elif choice == "6":
                show_about()
            elif choice == "0":
                print("\n👋 Terima kasih telah menggunakan Hand Tracking Media Controller!")
                break
            else:
                print("❌ Pilihan tidak valid. Silakan coba lagi.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            input("Tekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()