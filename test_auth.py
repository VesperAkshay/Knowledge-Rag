"""
Quick test script for authentication system
"""
import requests
import json
import random
import string

BASE_URL = "http://localhost:8000"

# Generate random username to avoid conflicts
random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
TEST_USERNAME = f"testuser_{random_suffix}"

print("=" * 60)
print("Testing Multi-User Authentication System")
print("=" * 60)

# Test 1: Register a new user
print("\n1. Testing user registration...")
register_data = {
    "username": TEST_USERNAME,
    "password": "test123456"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registration successful!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Username: {result['username']}")
    else:
        print(f"❌ Registration failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Login
print("\n2. Testing user login...")
login_data = {
    "username": TEST_USERNAME,
    "password": "test123456"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        result = response.json()
        session_cookie = response.cookies.get('session_id')
        print(f"✅ Login successful!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Session ID: {result['session_id'][:20]}...")
        print(f"   Cookie: {session_cookie[:20] if session_cookie else 'None'}...")
        
        # Save cookies for next requests
        cookies = response.cookies
    else:
        print(f"❌ Login failed: {response.text}")
        cookies = None
except Exception as e:
    print(f"❌ Error: {e}")
    cookies = None

if not cookies:
    print("\n❌ Cannot continue tests without login session")
    exit(1)

# Test 3: Get current user
print("\n3. Testing get current user...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/me", cookies=cookies)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Current user retrieved!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Username: {result['username']}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Try protected endpoint without credentials (should fail)
print("\n4. Testing protected endpoint without credentials...")
try:
    response = requests.get(f"{BASE_URL}/api/info", cookies=cookies)
    if response.status_code == 403:
        print(f"✅ Correctly blocked! (403 - No credentials configured)")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Save credentials (use dummy values for testing)
print("\n5. Testing save credentials...")
creds_data = {
    "google_api_key": "AIzaSyDummyKeyForTesting123456789",
    "chromadb_api_key": "chroma_test_api_key_123456789",
    "chromadb_tenant": "default-tenant",
    "chromadb_database": "default_database"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/credentials", json=creds_data, cookies=cookies)
    if response.status_code == 200:
        print(f"✅ Credentials saved successfully!")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Get masked credentials
print("\n6. Testing get credentials (should be masked)...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/credentials", cookies=cookies)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Credentials retrieved (masked):")
        print(f"   Google API Key: {result['google_api_key']}")
        print(f"   ChromaDB API Key: {result['chromadb_api_key']}")
        print(f"   ChromaDB Tenant: {result['chromadb_tenant']}")
        print(f"   ChromaDB Database: {result['chromadb_database']}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Get KB info (will fail with dummy credentials, which is expected)
print("\n7. Testing knowledge base info endpoint...")
print("   Note: This will fail because we're using dummy API keys")
try:
    response = requests.get(f"{BASE_URL}/api/info", cookies=cookies)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ KB info retrieved!")
        print(f"   Document count: {result['document_count']}")
    else:
        print(f"⚠️ Expected failure with dummy credentials: {response.status_code}")
        print(f"   This is normal - use real API keys for actual functionality")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Logout
print("\n8. Testing logout...")
try:
    response = requests.post(f"{BASE_URL}/api/auth/logout", cookies=cookies)
    if response.status_code == 200:
        print(f"✅ Logout successful!")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 9: Try accessing protected endpoint after logout (should fail)
print("\n9. Testing access after logout (should fail)...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/me", cookies=cookies)
    if response.status_code == 401:
        print(f"✅ Correctly blocked! (401 - Session invalid)")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Authentication system test complete!")
print("=" * 60)
