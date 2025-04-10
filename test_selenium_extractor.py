"""
Test script for the Selenium-based tweet extractor.

This script tests the extraction functionality with a sample tweet.
"""

import json
import time
from tweet_extractor import extract_tweet_data

def test_extraction():
    """Test the tweet extraction with a sample tweet."""
    # Sample tweet URL - replace with a valid tweet URL if needed
    url = "https://twitter.com/elonmusk/status/1686227187829968896"
    
    print(f"Testing Selenium-based extraction with URL: {url}")
    print("This may take a few moments as the browser loads...")
    
    start_time = time.time()
    
    # Extract tweet data
    result = extract_tweet_data(url)
    
    end_time = time.time()
    extraction_time = end_time - start_time
    
    # Print the result
    print("\nExtraction result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\nExtraction completed in {extraction_time:.2f} seconds")
    
    # Check if extraction was successful
    if result.get("status") == "success":
        print("\n✅ Extraction successful!")
        
        # Print extracted fields
        print("\nExtracted fields:")
        for key, value in result.items():
            if key not in ["url", "status", "extracted_at"]:
                if isinstance(value, list):
                    print(f"- {key}: {', '.join(value) if value else 'None'}")
                else:
                    print(f"- {key}: {value}")
    else:
        print("\n❌ Extraction failed!")
        print(f"Error message: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_extraction()
