#!/usr/bin/env python3

"""
Test script to verify Meowzon installation and dependencies
"""

import sys


def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    required = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'pytesseract': 'pytesseract',
        'pandas': 'pandas',
        'tqdm': 'tqdm',
        'requests': 'requests',
        'yaml': 'pyyaml',
    }
    
    optional = {
        'openai': 'openai',
        'anthropic': 'anthropic',
        'google.generativeai': 'google-generativeai',
        'matplotlib': 'matplotlib',
        'openpyxl': 'openpyxl',
    }
    
    failed = []
    
    # Test required
    print("\n✓ Required packages:")
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            failed.append(package)
    
    # Test optional
    print("\n✓ Optional packages (AI/Analytics):")
    for module, package in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  - {package} - not installed (optional)")
    
    return failed


def test_tesseract():
    """Test if Tesseract is accessible"""
    print("\n✓ Testing Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"  ✗ Tesseract not accessible: {e}")
        print("  Install from: https://github.com/tesseract-ocr/tesseract")
        return False


def test_meowzon_package():
    """Test if Meowzon package can be imported"""
    print("\n✓ Testing Meowzon package...")
    
    try:
        from meowzon import ExtractorConfig, MeowzonExtractor
        print("  ✓ Meowzon package imported successfully")
        
        # Test config creation
        config = ExtractorConfig()
        print("  ✓ ExtractorConfig created successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed to import Meowzon: {e}")
        return False


def test_ollama():
    """Test if Ollama is running (optional)"""
    print("\n✓ Testing Ollama (optional)...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"  ✓ Ollama is running")
            if models:
                print(f"  ✓ Available models: {len(models)}")
                for model in models[:3]:
                    print(f"    - {model.get('name', 'unknown')}")
            else:
                print("  - No models pulled yet. Run: ollama pull qwen2-vl:7b")
            return True
        else:
            print("  - Ollama not running (optional)")
            return False
    except:
        print("  - Ollama not running (optional)")
        print("  Install from: https://ollama.com")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🐱 MEOWZON INSTALLATION TEST")
    print("=" * 70)
    
    # Test imports
    failed_packages = test_imports()
    
    # Test Tesseract
    tesseract_ok = test_tesseract()
    
    # Test Meowzon
    meowzon_ok = test_meowzon_package()
    
    # Test Ollama (optional)
    ollama_ok = test_ollama()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    if failed_packages:
        print("\n❌ FAILED - Missing required packages:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\nInstall with: pip install " + " ".join(failed_packages))
        return 1
    
    if not tesseract_ok:
        print("\n⚠️  WARNING - Tesseract OCR not accessible")
        print("Tesseract is required for core functionality")
        return 1
    
    if not meowzon_ok:
        print("\n⚠️  WARNING - Meowzon package not properly installed")
        print("Run: pip install -e .")
        return 1
    
    print("\n✅ SUCCESS - All required components are installed!")
    
    if not ollama_ok:
        print("\n💡 TIP: Install Ollama for local AI processing (optional)")
        print("   https://ollama.com")
    
    print("\n🚀 You're ready to use Meowzon!")
    print("   Try: python main.py -i ./screenshots -o orders.csv")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
