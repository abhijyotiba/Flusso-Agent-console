"""Test script to verify data loader functionality"""

import sys
import os
from pathlib import Path

# Get the server directory
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from app.services.data_loader import ProductDatabase
import json

print("="*60)
print("DATA LOADER TEST")
print("="*60)

# Initialize database with correct path
data_path = server_dir / 'data'
db = ProductDatabase(str(data_path))

# Load data
print("\n1. Loading data...")
db.load_data()

# Get stats
print("\n2. Database Statistics:")
stats = db.get_stats()
print(json.dumps(stats, indent=2))

# Test product lookup by model number
print("\n3. Testing product lookup...")
test_models = ['10.FGC.4003CP', '10.FGC.4003BN', '10.FGC.4003MB']

for model in test_models:
    product = db.find_product(model)
    if product:
        print(f"\n✓ Found: {product.model_number}")
        print(f"  Confidence: {product.matched_confidence:.2f}")
        print(f"  Spec fields: {len(product.specs)}")
        print(f"  Images: {len(product.media.get('images', []))}")
        print(f"  Videos: {len(product.media.get('videos', []))}")
        print(f"  Documents: {len(product.documents)}")
        
        # Show key specs
        if product.specs:
            print(f"  Product Title: {product.specs.get('Product_Title', 'N/A')}")
            print(f"  Finish: {product.specs.get('Finish', 'N/A')}")
            print(f"  List Price: {product.specs.get('List_Price', 'N/A')}")
            print(f"  Category: {product.specs.get('Product_Category', 'N/A')}")
    else:
        print(f"\n✗ Not found: {model}")

# Test search by category
print("\n4. Testing category search...")
categories_to_test = ['Showering', 'Kitchen', 'Bathing']

for category in categories_to_test:
    results = db.search_by_category(category)
    print(f"\n  {category}: {len(results)} products found")

# Test fuzzy search
print("\n5. Testing fuzzy search in queries...")
test_queries = [
    "What is the price of 10.FGC.4003CP?",
    "Tell me about model 10FGC4003BN",
    "How do I install 10-FGC-4003-MB?"
]

for query in test_queries:
    product = db.find_product(query)
    if product:
        print(f"\n✓ Query: '{query}'")
        print(f"  Found: {product.model_number} (confidence: {product.matched_confidence:.2f})")
    else:
        print(f"\n✗ Query: '{query}' - No product found")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
