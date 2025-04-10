"""
Test script for the Railway Flask API.
This script tests the API endpoints with sample requests.
"""

import requests
import json
import time

def test_api(base_url="http://localhost:8080"):
    """Test the API endpoints with sample requests."""
    print(f"Testing API at {base_url}")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test single tweet extraction
    print("\n2. Testing single tweet extraction...")
    try:
        payload = {
            "url": "https://twitter.com/elonmusk/status/1686227187829968896"
        }
        response = requests.post(f"{base_url}/extract", json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test batch extraction
    print("\n3. Testing batch extraction...")
    try:
        payload = {
            "urls": [
                "https://twitter.com/elonmusk/status/1686227187829968896",
                "https://twitter.com/NASA/status/1678143677359783936"
            ]
        }
        response = requests.post(f"{base_url}/extract-batch", json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Main function to run the tests."""
    print("Tweet Extractor API Test")
    print("=======================")
    
    # Check if the API is running locally
    print("Checking if the API is running locally...")
    try:
        requests.get("http://localhost:8080/health", timeout=2)
        print("API is running locally!")
        test_api()
    except requests.exceptions.ConnectionError:
        print("API is not running locally.")
        print("Please start the API with 'python railway_app.py' and run this test again.")
        print("Or provide a custom API URL when running this script:")
        print("python test_api.py http://your-api-url")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Use provided URL
        test_api(sys.argv[1])
    else:
        # Use default URL
        main()
