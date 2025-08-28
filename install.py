"""
Easy installation script for Hand Tracking Media Controller
This script will guide you through the installation process
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("=" * 50)
    print("🎮 HAND TRACKING MEDIA CONTROLLER 🎮")
    print("=" * 50)
    print("Skrip ini akan membantu Anda menginstal dan mengkonfigurasi")
    print("Hand Tracking Media Controller pada sistem Anda.")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Memeriksa versi Python...")
    
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Error: Python 3.8 or higher required. Found: {version.major}.{version.minor}")
        print("Please install Python 3.8+ and try again.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_pip():
    """Periksa apakah pip tersedia"""
    print("📋 Memeriksa pip...")
    
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip not found. Please install pip and try again.")
        return False

def check_system_requirements():
    """Check system requirements"""
    print("📋 Checking system requirements...")
    
    system = platform.system().lower()
    print(f"🖥️  Operating System: {platform.system()} {platform.release()}")
    
    print("📷 Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera detected")
            cap.release()
        else:
            print("⚠️  Warning: No camera detected. You may need to connect a webcam.")
    except ImportError:
        print("⚠️  OpenCV not installed yet - will be installed with dependencies")
    
    print("🌐 Checking for Chrome/Chromium...")
    chrome_paths = {
        'windows': [
            'C:/Program Files/Google/Chrome/Application/chrome.exe',
            'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
        ],
        'darwin': [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        ],
        'linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
        ]
    }
    
    chrome_found = False
    for path in chrome_paths.get(system, []):
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("⚠️  Warning: Chrome/Chromium not found. Please install Chrome for web automation.")
        print("   You can download it from: https://www.google.com/chrome/")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        
        print("Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        print("Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Try running manually: pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found. Please run this script from the project directory.")
        return False

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("✅ .env file created")
        
        print("\n⚠️  IMPORTANT: Please edit the .env file and add your API keys:")
        print("   - YOUTUBE_API_KEY (from Google Developer Console)")
        print("   - SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET (from Spotify Developer Dashboard)")
        print(f"   - File location: {env_file.absolute()}")
        
        try:
            if platform.system() == "Windows":
                os.startfile(env_file)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(env_file)])
            else:
                subprocess.run(["xdg-open", str(env_file)])
        except:
            print("   Silakan buka file secara manual untuk mengeditnya.")
    else:
        print("✅ .env file already exists")
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    return True

def test_installation():
    """Test if installation works"""
    print("\n🧪 Instalasi pengujian...")
    
    try:
        print("Testing imports...")
        
        test_imports = [
            "cv2",
            "mediapipe", 
            "selenium",
            "spotipy",
            "googleapiclient"
        ]
        
        for module in test_imports:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError as e:
                print(f"  ❌ {module}: {e}")
                return False
        
        print("✅ Semua import berhasil")
        return True
        
    except Exception as e:
        print(f"❌ Tes instalasi gagal: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n" + "=" * 60)
    print("🎉 INSTALLATION COMPLETE!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Edit .env file and add your API keys:")
    print("   • YouTube API Key (Google Developer Console)")
    print("   • Spotify Client ID & Secret (Spotify Developer Dashboard)")
    print()
    print("2. Run the application:")
    print("   python main.py")
    print()
    print("3. Follow the on-screen instructions to:")
    print("   • Select your media platform")
    print("   • Position your camera")
    print("   • Start using hand gestures!")
    print()
    print("🤲 GESTURE CONTROLS:")
    print("   ✋ Buka Tangan     → Play")
    print("   ✊ Membuka Tangan  → Pause") 
    print("   👍 Suka       → Volume Up")
    print("   👎 Tidak Suka     → Volume Down")
    print("   ✌️ Peace Sign      → Next Track")
    print("   👆 Point Up        → Previous Track")
    print()
    print("📚 Untuk bantuan lebih lanjut, periksa README.md")
    print("🐛 Report issues: https://github.com/Ahmadfauzan280503/Media-controller/issues")
    print("=" * 50)

def main():
    """Main installation function"""
    print_banner()
    
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    check_system_requirements()
    
    print("\n" + "=" * 60)
    response = input("Continue with installation? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("Installation cancelled.")
        return False
    
    success = True
    
    success &= install_dependencies()
    success &= setup_environment()  
    success &= setup_directories()
    success &= test_installation()
    
    if success:
        show_next_steps()
        return True
    else:
        print("\n❌ Instalasi gagal. Silakan periksa kesalahan di atas dan coba lagi.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Instalasi dibatalkan oleh user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)