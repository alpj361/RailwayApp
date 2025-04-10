"""
Test script for the tweet_extractor module.
This script tests the extraction functionality with a sample tweet.
"""

import json
from tweet_extractor import extract_tweet_data

def test_extraction():
    """Test the tweet extraction with a sample tweet."""
    # Sample tweet URL
    url = "https://twitter.com/elonmusk/status/1686227187829968896"
    
    print(f"Testing extraction with URL: {url}")
    
    # Extract tweet data
    result = extract_tweet_data(url)
    
    # Print the result
    print("\nExtraction result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Check if extraction was successful
    if result.get("status") == "success":
        print("\n✅ Extraction successful!")
        
        # Print extracted fields
        print("\nExtracted fields:")
        for key, value in result.items():
            if key not in ["url", "status", "extracted_at"]:
                print(f"- {key}: {value}")
    else:
        print("\n❌ Extraction failed!")
        print(f"Error message: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_extraction()
