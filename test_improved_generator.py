#!/usr/bin/env python3
"""
Test script for the improved review generator
Shows better variety and less repetition
"""

import review_generator_improved as generator
from collections import Counter
import re

def analyze_reviews(reviews):
    """Analyze reviews for variety and repetition"""
    all_content = []
    languages = Counter()
    ratings = Counter()
    
    # Common repetitive phrases to check
    repetitive_phrases = [
        "obsessed with this",
        "copped this",
        "zero regrets", 
        "literally perfection",
        "really nice",
        "pretty happy",
        "needed a",
        "hit the jackpot"
    ]
    
    phrase_counts = Counter()
    
    for review in reviews:
        content = review['content'].lower()
        all_content.append(content)
        
        # Count languages based on location
        languages[review['location']] += 1
        ratings[review['rating']] += 1
        
        # Count repetitive phrases
        for phrase in repetitive_phrases:
            if phrase in content:
                phrase_counts[phrase] += 1
    
    return {
        'total': len(reviews),
        'languages': dict(languages),
        'ratings': dict(ratings),
        'phrase_repetition': dict(phrase_counts),
        'unique_content_ratio': len(set(all_content)) / len(all_content) if all_content else 0
    }

def main():
    # Test product
    test_product = {
        'title': 'Gothic Dark Mesh Top - Black Lace Design',
        'id': 'test-123'
    }
    
    print("Generating 50 reviews to test variety and language distribution...\n")
    
    # Generate reviews
    all_reviews = []
    for i in range(10):  # Generate 10 batches of 5 reviews
        reviews = generator.generate_reviews_for_product(test_product, num_reviews=5)
        all_reviews.extend(reviews)
    
    # Analyze results
    analysis = analyze_reviews(all_reviews)
    
    print(f"Total reviews generated: {analysis['total']}")
    print(f"\nLanguage distribution (by location):")
    for loc, count in sorted(analysis['languages'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {loc}: {count} ({count/analysis['total']*100:.1f}%)")
    
    print(f"\nRating distribution:")
    for rating in sorted(analysis['ratings'].keys(), reverse=True):
        count = analysis['ratings'][rating]
        print(f"  {rating} stars: {count} ({count/analysis['total']*100:.1f}%)")
    
    print(f"\nContent uniqueness: {analysis['unique_content_ratio']*100:.1f}% unique reviews")
    
    print(f"\nRepetitive phrase usage (out of {analysis['total']} reviews):")
    for phrase, count in sorted(analysis['phrase_repetition'].items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  '{phrase}': {count} times ({count/analysis['total']*100:.1f}%)")
    
    # Show sample reviews in different languages
    print("\n" + "="*60)
    print("SAMPLE REVIEWS IN DIFFERENT LANGUAGES:")
    print("="*60)
    
    # Group by language
    by_language = {}
    for review in all_reviews[:20]:  # First 20 reviews
        lang = review['location']
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(review)
    
    for lang, reviews in list(by_language.items())[:5]:  # Show 5 different languages
        print(f"\n[{lang}] - {reviews[0]['author']} - {reviews[0]['rating']}★")
        if reviews[0]['title']:
            print(f"Title: {reviews[0]['title']}")
        print(f"Content: {reviews[0]['content']}")
    
    # Show variety in opening phrases
    print("\n" + "="*60)
    print("VARIETY IN REVIEW OPENINGS:")
    print("="*60)
    
    openings = []
    for review in all_reviews[:30]:
        if review['content']:
            # Get first 50 characters or until punctuation
            opening = re.split(r'[.!,]', review['content'])[0][:50]
            if opening:
                openings.append(opening)
    
    unique_openings = list(set(openings))[:15]
    for opening in unique_openings:
        print(f"- {opening}...")

if __name__ == "__main__":
    main()