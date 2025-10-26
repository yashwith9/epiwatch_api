"""
Test Authentication Endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_signup():
    """Test user registration"""
    print("\n🔐 Testing /auth/signup endpoint...")
    
    signup_data = {
        "fullName": "John Doe",
        "email": "john.doe@example.com",
        "organization": "World Health Organization",
        "password": "securepassword123",
        "confirmPassword": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Success: {data['message']}")
        print(f"Token: {data['token'][:50]}...")
        print(f"User: {data['user']['fullName']} ({data['user']['email']})")
        return data['token']
    else:
        print(f"❌ Error: {response.json()}")
        return None


def test_signup_duplicate():
    """Test duplicate email registration"""
    print("\n🔐 Testing duplicate email...")
    
    signup_data = {
        "fullName": "Jane Doe",
        "email": "john.doe@example.com",  # Same email
        "organization": "CDC",
        "password": "password123",
        "confirmPassword": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 409:
        print(f"✅ Correctly rejected: {response.json()['detail']}")
    else:
        print(f"❌ Unexpected response: {response.json()}")


def test_login():
    """Test user login"""
    print("\n🔐 Testing /auth/login endpoint...")
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['message']}")
        print(f"Token: {data['token'][:50]}...")
        print(f"User: {data['user']['fullName']} ({data['user']['email']})")
        return data['token']
    else:
        print(f"❌ Error: {response.json()}")
        return None


def test_login_invalid():
    """Test login with invalid credentials"""
    print("\n🔐 Testing invalid credentials...")
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print(f"✅ Correctly rejected: {response.json()['detail']}")
    else:
        print(f"❌ Unexpected response: {response.json()}")


def test_validate_token(token):
    """Test token validation"""
    print("\n🔐 Testing /auth/validate endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/validate", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['valid']:
            print(f"✅ Token valid!")
            print(f"User: {data['user']['fullName']} ({data['user']['email']})")
        else:
            print(f"❌ Token invalid!")
    else:
        print(f"❌ Error: {response.json()}")


def test_validate_invalid_token():
    """Test validation with invalid token"""
    print("\n🔐 Testing invalid token validation...")
    
    headers = {
        "Authorization": "Bearer invalid-token-12345"
    }
    
    response = requests.get(f"{BASE_URL}/auth/validate", headers=headers)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    if not data['valid']:
        print(f"✅ Correctly identified invalid token")
    else:
        print(f"❌ Incorrectly validated invalid token")


def test_password_mismatch():
    """Test password mismatch validation"""
    print("\n🔐 Testing password mismatch...")
    
    signup_data = {
        "fullName": "Test User",
        "email": "test@example.com",
        "organization": "Test Org",
        "password": "password123",
        "confirmPassword": "different123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 422:
        print(f"✅ Correctly rejected mismatched passwords")
    else:
        print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 EpiWatch Authentication API Tests")
    print("=" * 70)
    
    try:
        # Test signup
        token = test_signup()
        
        # Test duplicate email
        test_signup_duplicate()
        
        # Test password mismatch
        test_password_mismatch()
        
        # Test login
        login_token = test_login()
        
        # Test invalid login
        test_login_invalid()
        
        # Test token validation
        if token:
            test_validate_token(token)
        
        # Test invalid token
        test_validate_invalid_token()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure the server is running: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
