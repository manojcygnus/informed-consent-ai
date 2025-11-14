"""
API Testing Script - Test all endpoints
"""

import requests
import json

API_URL = "http://localhost:5000/api"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("Testing Health Endpoint")
    print("="*50)

    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.ok


def test_login(email, password):
    """Test login endpoint"""
    print("\n" + "="*50)
    print("Testing Login Endpoint")
    print("="*50)

    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(
        f"{API_URL}/login",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.ok:
        return response.json().get('session_token')
    return None


def test_stats(session_token):
    """Test stats endpoint"""
    print("\n" + "="*50)
    print("Testing Stats Endpoint")
    print("="*50)

    response = requests.get(
        f"{API_URL}/stats",
        headers={"Authorization": f"Bearer {session_token}"}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.ok


def test_query(session_token, query_text):
    """Test query endpoint"""
    print("\n" + "="*50)
    print("Testing Query Endpoint")
    print("="*50)

    payload = {
        "query": query_text
    }

    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {session_token}"
        }
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.ok


def test_logout(session_token):
    """Test logout endpoint"""
    print("\n" + "="*50)
    print("Testing Logout Endpoint")
    print("="*50)

    response = requests.post(
        f"{API_URL}/logout",
        headers={"Authorization": f"Bearer {session_token}"}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.ok


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Free Consent Management System - API Test Suite")
    print("="*60)

    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed! Is the API server running?")
        print("Start it with: cd api && python app.py")
        return

    print("\n✅ Health check passed!")

    # Get test credentials
    print("\n" + "="*60)
    email = input("Enter test patient email: ").strip()
    password = input("Enter test patient password: ").strip()

    # Test 2: Login
    session_token = test_login(email, password)

    if not session_token:
        print("\n❌ Login failed! Check credentials.")
        print("Process a PDF first with: cd scripts && python ingest_pdf.py path/to/pdf")
        return

    print("\n✅ Login successful!")

    # Test 3: Stats
    if test_stats(session_token):
        print("\n✅ Stats retrieval successful!")
    else:
        print("\n❌ Stats retrieval failed!")

    # Test 4: Query
    query_text = "What did I consent to?"
    if test_query(session_token, query_text):
        print("\n✅ Query successful!")
    else:
        print("\n❌ Query failed!")

    # Test 5: Logout
    if test_logout(session_token):
        print("\n✅ Logout successful!")
    else:
        print("\n❌ Logout failed!")

    print("\n" + "="*60)
    print("Test Suite Complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the API server is running:")
        print("  cd api && python app.py")
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
