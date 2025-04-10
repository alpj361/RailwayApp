"""
Railway App for Tweet Extraction

This is a lightweight Flask application that serves the tweet extraction functionality.
It's designed to be deployed on Railway and called by the main application on Render.
"""

from flask import Flask, request, jsonify
import os
import time
from tweet_extractor import extract_tweet_data

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_tweet():
    """
    Extract data from a tweet URL.
    
    Expects a JSON payload with a 'url' field.
    Returns the extracted tweet data.
    """
    try:
        # Get request data
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request must be JSON"
            }), 400
            
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({
                "status": "error",
                "message": "URL is required"
            }), 400
            
        # Extract tweet data
        tweet_data = extract_tweet_data(url)
        
        # Return the result
        return jsonify({
            "status": "success" if tweet_data.get("status") != "error" else "error",
            "data": tweet_data
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/extract-batch', methods=['POST'])
def extract_batch():
    """
    Extract data from multiple tweet URLs.
    
    Expects a JSON payload with a 'urls' array.
    Returns the extracted data for each URL.
    """
    try:
        # Get request data
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request must be JSON"
            }), 400
            
        data = request.json
        urls = data.get('urls', [])
        
        if not urls or not isinstance(urls, list):
            return jsonify({
                "status": "error",
                "message": "URLs array is required"
            }), 400
            
        # Extract data for each URL
        results = []
        for url in urls:
            try:
                tweet_data = extract_tweet_data(url)
                results.append(tweet_data)
            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "message": str(e)
                })
                
        # Determine overall status
        success_count = sum(1 for r in results if r.get("status") != "error")
        
        if success_count == 0:
            status = "error"
            message = "Failed to extract data from any tweets"
        elif success_count < len(urls):
            status = "partial_success"
            message = f"Successfully extracted data from {success_count} of {len(urls)} tweets"
        else:
            status = "success"
            message = f"Successfully extracted data from all {len(urls)} tweets"
            
        return jsonify({
            "status": status,
            "message": message,
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "tweet-extractor",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/', methods=['GET'])
def home():
    """Simple home page."""
    return """
    <html>
    <head>
        <title>Tweet Extractor API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #1DA1F2; }
            .endpoint { margin-bottom: 20px; border-left: 3px solid #1DA1F2; padding-left: 15px; }
            code { background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Tweet Extractor API</h1>
        <p>Microservice for extracting data from tweets</p>
        
        <div class="endpoint">
            <h3>POST /extract</h3>
            <p>Extract data from a single tweet</p>
            <p><code>{"url": "https://x.com/user/status/123"}</code></p>
        </div>
        
        <div class="endpoint">
            <h3>POST /extract-batch</h3>
            <p>Extract data from multiple tweets</p>
            <p><code>{"urls": ["https://x.com/user/status/123", ...]}</code></p>
        </div>
        
        <div class="endpoint">
            <h3>GET /health</h3>
            <p>Health check endpoint</p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
