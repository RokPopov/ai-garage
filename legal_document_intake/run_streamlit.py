import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['streamlit', 'requests', 'pandas']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\n🔧 Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_backend():
    """Check if backend is running."""
    try:
        import requests
        from dotenv import load_dotenv
        
        load_dotenv()
        port = os.getenv("API_PORT", "8000")
        
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print("⚠️  Backend responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("💡 Start the backend first with: python run_backend.py")
        return False
    except ImportError:
        print("⚠️  requests not installed, skipping backend check")
        return True

def main():
    """Run the Streamlit frontend application."""
    print("🎨 Legal Document Intake System - Frontend")
    print("="*50)
    
    if not check_dependencies():
        sys.exit(1)
    
    backend_running = check_backend()
    
    if not backend_running:
        response = input("\n❓ Continue without backend connection? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    project_root = Path(__file__).parent
    
    print(f"✅ Starting Streamlit frontend...")
    print(f"📱 Frontend URL: http://localhost:8501")
    print(f"🎬 Ready for demo!")
    print("\n⚡ Press Ctrl+C to stop the application")
    print("="*50)
    
    try:
        streamlit_dir = project_root / "streamlit_ui"
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false"
        ], cwd=streamlit_dir)
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except FileNotFoundError:
        print("❌ Streamlit not found. Install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()