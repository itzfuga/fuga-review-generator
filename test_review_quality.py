#!/usr/bin/env python3
"""
Test script to validate review quality improvements
"""

from review_generator import test_language_consistency, generate_review

def test_review_samples():
    """Generate sample reviews to check quality"""
    
    test_product = {
        'id': '12345',
        'title': 'Gothic Punk Mesh Shirt',
        'body_html': '<p>Edgy mesh shirt featuring decorative chains, zipper details, and punk aesthetic. Made from premium polyester mesh with velvet accents. Perfect for concerts and clubbing. Oversized fit for comfort.</p>',
        'handle': 'gothic-punk-mesh-shirt'
    }
    
    print("\n🎯 Generating 50 sample reviews to check quality:\n")
    print(f"{'Location':<8} {'Title':<35} {'Content':<100}")
    print("-" * 150)
    
    for i in range(50):
        review = generate_review(test_product, existing_reviews=i)
        location = review.get('location', '')
        title = review.get('title', '')[:35]
        content = review.get('content', '')[:100]
        
        # Only print non-empty reviews
        if title or content:
            print(f"{location:<8} {title:<35} {content:<100}")

if __name__ == "__main__":
    # Test language consistency
    print("=" * 80)
    print("TESTING LANGUAGE CONSISTENCY")
    print("=" * 80)
    test_language_consistency(100)
    
    # Show sample reviews
    print("\n" + "=" * 80)
    print("SAMPLE REVIEWS OUTPUT")
    print("=" * 80)
    test_review_samples()