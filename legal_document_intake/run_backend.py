import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['fastapi', 'uvicorn', 'docling', 'openai', 'instructor', 'langgraph', 'reportlab']
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

def check_environment():
    """Check if environment is properly configured."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not found!")
        print("\n🔧 Add OPENAI_API_KEY to your .env file")
        print("💡 Copy .env.example to .env and add your key")
        return False
    
    # Create required directories
    Path("uploads").mkdir(exist_ok=True)
    Path("generated_pdfs").mkdir(exist_ok=True)
    
    return True

if __name__ == "__main__":
    print("🚀 Legal Document Intake System - Backend")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"✅ All checks passed!")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print("\n⚡ Press Ctrl+C to stop the server")
    print("\n🎬 Ready for demo!")
    print("="*50)
    
    try:
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)