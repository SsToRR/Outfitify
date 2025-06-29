#!/usr/bin/env python3
"""
Test script to verify Outfitify bot setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import telebot
        print("✅ pyTelegramBotAPI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pyTelegramBotAPI: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite3 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SQLite3: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pillow: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False
    
    return True

def test_local_modules():
    """Test if local modules can be imported"""
    print("\n🔍 Testing local modules...")
    
    try:
        from config import TELEGRAM_TOKEN, OPENAI_API_KEY
        print("✅ Config module imported successfully")
        
        if TELEGRAM_TOKEN and TELEGRAM_TOKEN != 'your_telegram_bot_token_here':
            print("✅ Telegram token is configured")
        else:
            print("⚠️  Telegram token needs to be configured")
        
        if OPENAI_API_KEY:
            print("✅ OpenAI API key is configured")
        else:
            print("⚠️  OpenAI API key needs to be configured")
            
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from database import Database
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database: {e}")
        return False
    
    try:
        from ai_service import AIService
        print("✅ AI service module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI service: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database...")
    
    try:
        from database import Database
        db = Database()
        print("✅ Database initialized successfully")
        
        # Test adding a user
        db.add_user(12345, "test_user", "Test", "User")
        print("✅ User addition test passed")
        
        # Test getting user clothes
        clothes = db.get_user_clothes(12345)
        print(f"✅ User clothes retrieval test passed (found {len(clothes)} items)")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ai_service():
    """Test AI service functionality"""
    print("\n🔍 Testing AI service...")
    
    try:
        from ai_service import AIService
        from config import OPENAI_API_KEY
        
        if not OPENAI_API_KEY:
            print("⚠️  Skipping AI service test - no API key configured")
            return True
        
        ai = AIService()
        print("✅ AI service initialized successfully")
        
        # Test text analysis
        test_description = "Blue cotton t-shirt"
        analysis = ai.analyze_text_description(test_description)
        
        if analysis and 'name' in analysis:
            print("✅ Text analysis test passed")
        else:
            print("⚠️  Text analysis returned unexpected format")
        
        return True
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing environment...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - create one from env_example.txt")
    
    # Check if photos directory exists
    if os.path.exists('photos'):
        print("✅ photos directory exists")
    else:
        print("ℹ️  photos directory will be created when needed")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 7:
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} is too old (need 3.7+)")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Outfitify Bot Setup Test\n")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_local_modules,
        test_database,
        test_ai_service,
        test_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📝 Next steps:")
        print("1. Configure your API keys in .env file")
        print("2. Run 'python main.py' to start the bot")
        print("3. Test the bot on Telegram")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check your API keys configuration")
        print("3. Ensure you have Python 3.7+ installed")

if __name__ == "__main__":
    main() 