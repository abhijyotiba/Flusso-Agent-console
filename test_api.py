"""Test the chat API endpoint"""

import requests
import json

# API endpoint
url = "http://localhost:8000/api/chat"

# Test queries
test_queries = [
    {
        "query": "What is the price of 10.FGC.4003CP?",
        "model_mode": "flash"
    },
    {
        "query": "Tell me about the features and specifications of 10.FGC.4003BN",
        "model_mode": "flash"
    },
    {
        "query": "Compare 10.FGC.4003CP, 10.FGC.4003BN, and 10.FGC.4003MB",
        "model_mode": "flash"
    }
]

print("="*70)
print("TESTING AGENT ASSIST CONSOLE API")
print("="*70)

for i, test_data in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}: {test_data['query']}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Status: Success")
            print(f"✓ Model Used: {result.get('model_used', 'N/A')}")
            print(f"✓ Matched Product: {result.get('matched_product', 'None')}")
            print(f"✓ Confidence: {result.get('confidence', 0):.2f}")
            print(f"✓ Sources: {len(result.get('sources', []))} items")
            
            # Display response
            print(f"\n📝 Response:")
            print("-" * 70)
            print(result.get('markdown_response', 'No response')[:500])
            if len(result.get('markdown_response', '')) > 500:
                print("... (truncated)")
            print("-" * 70)
            
            # Display media assets if available
            if result.get('media_assets'):
                media = result['media_assets']
                specs = media.get('specs', {})
                images = media.get('images', [])
                videos = media.get('videos', [])
                docs = media.get('documents', [])
                
                print(f"\n📦 Media Assets:")
                print(f"   - Specs: {len(specs)} fields")
                print(f"   - Images: {len(images)}")
                print(f"   - Videos: {len(videos)}")
                print(f"   - Documents: {len(docs)}")
                
                if specs:
                    print(f"\n   Key Specs:")
                    for key in ['Product_Title', 'Finish', 'List_Price', 'Product_Category']:
                        if key in specs:
                            print(f"      - {key}: {specs[key]}")
        else:
            print(f"\n✗ Status: Failed")
            print(f"✗ HTTP {response.status_code}")
            print(f"✗ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n✗ Request timed out after 60 seconds")
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

print(f"\n{'='*70}")
print("TESTING COMPLETE")
print(f"{'='*70}")
