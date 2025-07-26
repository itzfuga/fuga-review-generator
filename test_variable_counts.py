#!/usr/bin/env python3
"""
Test script for variable review count feature
Demonstrates natural distribution vs fixed counts
"""

from review_distribution import get_natural_review_count, generate_bulk_review_distribution
from datetime import datetime, timedelta
from collections import Counter

def test_distribution_patterns():
    """Test different distribution patterns"""
    print("=== TESTING VARIABLE REVIEW COUNTS ===\n")
    
    # Test 1: Compare fixed vs variable counts
    print("1. Fixed Count vs Variable Count for 20 products:")
    print("   Fixed (all get 15 reviews): 15, 15, 15, 15, 15...")
    
    variable_counts = [get_natural_review_count(10, 30) for _ in range(20)]
    print(f"   Variable (natural): {variable_counts}")
    print(f"   Range: {min(variable_counts)}-{max(variable_counts)}, Avg: {sum(variable_counts)/len(variable_counts):.1f}\n")
    
    # Test 2: Distribution analysis
    print("2. Distribution Analysis (1000 products):")
    large_sample = [get_natural_review_count(10, 30) for _ in range(1000)]
    distribution = Counter(large_sample)
    
    ranges = {
        "10-15 reviews": len([x for x in large_sample if 10 <= x <= 15]),
        "16-20 reviews": len([x for x in large_sample if 16 <= x <= 20]),
        "21-25 reviews": len([x for x in large_sample if 21 <= x <= 25]),
        "26-30 reviews": len([x for x in large_sample if 26 <= x <= 30])
    }
    
    for range_name, count in ranges.items():
        percentage = (count / 1000) * 100
        print(f"   {range_name}: {count} products ({percentage:.1f}%)")
    
    # Test 3: Age-based distribution
    print("\n3. Age-Based Distribution (considering product age):")
    
    # Create test products with different ages
    test_products = [
        {'id': '1', 'title': 'Old Popular Top', 'created_at': (datetime.now() - timedelta(days=500)).isoformat()},
        {'id': '2', 'title': 'Medium Age Dress', 'created_at': (datetime.now() - timedelta(days=200)).isoformat()},
        {'id': '3', 'title': 'Recent Release', 'created_at': (datetime.now() - timedelta(days=20)).isoformat()},
        {'id': '4', 'title': 'Brand New Item', 'created_at': (datetime.now() - timedelta(days=5)).isoformat()}
    ]
    
    distribution = generate_bulk_review_distribution(test_products, 10, 30, use_smart_distribution=True)
    
    for product in test_products:
        pid = str(product['id'])
        age_days = (datetime.now() - datetime.fromisoformat(product['created_at'])).days
        print(f"   {product['title']}: {distribution[pid]} reviews (age: {age_days} days)")
    
    # Test 4: Category influence
    print("\n4. Category-Based Distribution:")
    category_products = [
        {'id': '10', 'title': 'Gothic Black Top - Popular', 'created_at': datetime.now().isoformat()},
        {'id': '11', 'title': 'Silver Chain Necklace - Niche', 'created_at': datetime.now().isoformat()},
        {'id': '12', 'title': 'Dark Academic Dress - Popular', 'created_at': datetime.now().isoformat()},
        {'id': '13', 'title': 'Gothic Ring Set - Niche', 'created_at': datetime.now().isoformat()}
    ]
    
    cat_distribution = generate_bulk_review_distribution(category_products, 15, 25, use_smart_distribution=True)
    
    for product in category_products:
        pid = str(product['id'])
        category = "Popular" if any(word in product['title'].lower() for word in ['top', 'dress']) else "Niche"
        print(f"   {product['title'][:30]}...: {cat_distribution[pid]} reviews ({category})")
    
    print("\n=== BENEFITS ===")
    print("✓ Products now have varied review counts (10-30 instead of all same)")
    print("✓ Older products automatically get more reviews (realistic)")
    print("✓ Popular categories get slightly more reviews")
    print("✓ New products get fewer reviews (authentic behavior)")
    print("✓ Distribution looks natural, not systematic")

if __name__ == "__main__":
    test_distribution_patterns()