"""
Test script to diagnose Gemini API key issues
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

# Test 1: Import google-genai
try:
    from google import genai
    print("✅ google-genai package imported successfully")
except Exception as e:
    print(f"❌ Failed to import google-genai: {e}")
    exit(1)

# Test 2: Create client
try:
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client created successfully")
except Exception as e:
    print(f"❌ Failed to create client: {e}")
    exit(1)

# Test 3: List models
try:
    print("\n📋 Attempting to list models...")
    models = client.models.list()
    model_names = [m.name for m in models]
    print(f"✅ Successfully listed {len(model_names)} models")
    print(f"   First 3 models: {model_names[:3]}")
except Exception as e:
    print(f"❌ Failed to list models: {e}")
    exit(1)

# Test 4: Try to generate content (simple text)
try:
    print("\n🧪 Attempting simple text generation...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello"
    )
    print(f"✅ Text generation successful: {response.text[:50]}")
except Exception as e:
    print(f"❌ Text generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ ALL TESTS PASSED - Your Gemini API key is working correctly!")
