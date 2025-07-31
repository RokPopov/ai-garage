import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def run_integration_tests():
    """Run custom integration tests."""
    print("🔧 Running Integration Tests...")
    print("="*50)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from tests.test_document_processing import run_integration_tests as run_doc_tests
        from tests.test_api_endpoints import run_api_tests
        
        # Run document processing tests
        doc_results, doc_passed = run_doc_tests()
        
        # Run API tests
        api_results, api_passed = run_api_tests()
        
        all_results = {**doc_results, **api_results}
        all_passed = doc_passed and api_passed
        
        print("\n" + "="*50)
        print("📊 INTEGRATION TEST SUMMARY")
        print("="*50)
        
        passed_count = sum(1 for result in all_results.values() if result["passed"])
        total_count = len(all_results)
        
        for test_name, test_result in all_results.items():
            print(f"{test_name}: {test_result['result']}")
        
        print(f"\n📈 Results: {passed_count}/{total_count} tests passed")
        
        if all_passed:
            print("🎉 All integration tests passed!")
        else:
            print("❌ Some integration tests failed")
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 This usually means dependencies are not installed.")
        print("🔧 Install dependencies with: pip install -r requirements.txt")
        print("📦 Or install in virtual environment:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        return False

def run_pytest_suite():
    """Run pytest test suite."""
    print("\n🔬 Running Pytest Suite...")
    print("="*50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--disable-warnings"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Could not run pytest: {e}")
        return False

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking Environment...")
    print("="*50)
    
    checks = [
        ("Python version", lambda: sys.version_info >= (3, 8)),
        ("OpenAI API key", lambda: bool(os.getenv("OPENAI_API_KEY"))),
        ("Project structure", lambda: Path("backend").exists() and Path("streamlit_ui").exists()),
        ("Required directories", lambda: Path("uploads").exists() and Path("generated_pdfs").exists()),
        ("Requirements file", lambda: Path("requirements.txt").exists()),
    ]
    
    dependency_checks = [
        ("FastAPI", "fastapi"),
        ("Streamlit", "streamlit"),
        ("Docling", "docling"),
        ("OpenAI", "openai"),
        ("Instructor", "instructor"),
        ("LangGraph", "langgraph"),
        ("ReportLab", "reportlab"),
        ("Requests", "requests"),
        ("Pandas", "pandas"),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{check_name}: {status}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"{check_name}: ❌ ERROR - {e}")
            all_passed = False
    
    print("\n📦 Checking Dependencies...")
    dependencies_missing = []
    for dep_name, dep_module in dependency_checks:
        try:
            __import__(dep_module)
            print(f"{dep_name}: ✅ INSTALLED")
        except ImportError:
            print(f"{dep_name}: ❌ MISSING")
            dependencies_missing.append(dep_module)
            all_passed = False
    
    if dependencies_missing:
        print(f"\n💡 Missing dependencies: {', '.join(dependencies_missing)}")
        print("🔧 Install with: pip install -r requirements.txt")
        print("📦 Or create virtual environment:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
    
    return all_passed

def main():
    """Main test runner."""
    print("🚀 Legal Document Intake System - Test Suite")
    print("="*60)
    print("Professional Testing Framework")
    print("="*60)
    
    env_ok = check_environment()
    
    if not env_ok:
        print("\n⚠️  Environment check found issues, but continuing with tests...")
    
    integration_passed = run_integration_tests()
    
    pytest_passed = run_pytest_suite()
    
    print("\n" + "="*60)
    print("🎯 FINAL TEST SUMMARY")
    print("="*60)
    print(f"Environment Check: {'✅ PASS' if env_ok else '⚠️  ISSUES'}")
    print(f"Integration Tests: {'✅ PASS' if integration_passed else '❌ FAIL'}")
    print(f"Pytest Suite: {'✅ PASS' if pytest_passed else '❌ FAIL'}")
    
    tests_passed = integration_passed and pytest_passed
    
    if tests_passed:
        print("\n🎉 All tests passed! System is ready for demo.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
    
    print("\n💡 Tips for YouTube Demo:")
    print("- Make sure OpenAI API key is set")
    print("- Upload sample documents to test the workflow")  
    print("- Check both backend and frontend are running")
    print("- Test the complete user journey")
    
    return tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)