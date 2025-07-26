"""
Review Distribution Patterns
Generates more natural review count distributions
"""
import random

def get_natural_review_count(min_reviews=10, max_reviews=30, distribution='natural'):
    """
    Generate review counts with different distribution patterns
    
    Args:
        min_reviews: Minimum number of reviews
        max_reviews: Maximum number of reviews
        distribution: Distribution type ('natural', 'weighted', 'random')
    
    Returns:
        Number of reviews to generate
    """
    
    if distribution == 'random':
        # Simple random distribution
        return random.randint(min_reviews, max_reviews)
    
    elif distribution == 'weighted':
        # Weighted towards lower numbers (more realistic)
        # Most products have fewer reviews, some have many
        weights = []
        values = list(range(min_reviews, max_reviews + 1))
        
        for i, val in enumerate(values):
            # Higher weight for lower numbers
            weight = (len(values) - i) ** 2
            weights.append(weight)
        
        return random.choices(values, weights=weights)[0]
    
    elif distribution == 'natural':
        # Natural distribution based on real e-commerce patterns
        # Using a modified log-normal distribution
        
        # Parameters for realistic distribution
        # Most products: 10-20 reviews
        # Some products: 20-25 reviews  
        # Few products: 25-30 reviews
        
        ranges = [
            (min_reviews, min_reviews + (max_reviews - min_reviews) // 3, 0.6),  # 60% in lower third
            (min_reviews + (max_reviews - min_reviews) // 3, min_reviews + 2 * (max_reviews - min_reviews) // 3, 0.3),  # 30% in middle third
            (min_reviews + 2 * (max_reviews - min_reviews) // 3, max_reviews, 0.1)  # 10% in upper third
        ]
        
        # Select range based on weights
        range_choice = random.choices(ranges, weights=[r[2] for r in ranges])[0]
        return random.randint(range_choice[0], range_choice[1])
    
    else:
        # Default to natural distribution
        return get_natural_review_count(min_reviews, max_reviews, 'natural')

def get_product_category_factor(product_title):
    """
    Adjust review count based on product category
    Popular items get more reviews
    """
    title_lower = product_title.lower()
    
    # Popular categories tend to get more reviews
    popular_keywords = ['top', 'shirt', 'dress', 'pants', 'jeans', 'hoodie', 'jacket']
    niche_keywords = ['belt', 'chain', 'accessory', 'necklace', 'ring', 'bracelet']
    
    if any(keyword in title_lower for keyword in popular_keywords):
        return 1.2  # 20% more reviews for popular items
    elif any(keyword in title_lower for keyword in niche_keywords):
        return 0.8  # 20% fewer reviews for niche items
    else:
        return 1.0  # Normal amount

def get_age_based_review_count(product_created_at, min_reviews=10, max_reviews=30):
    """
    Older products tend to have more reviews
    """
    from datetime import datetime
    
    try:
        # Parse creation date
        if isinstance(product_created_at, str):
            created = datetime.fromisoformat(product_created_at.replace('Z', '+00:00'))
        else:
            created = product_created_at
        
        # Calculate age in days
        age_days = (datetime.now() - created.replace(tzinfo=None)).days
        
        # Adjust range based on age
        if age_days > 365:  # Over 1 year old
            adjusted_min = int(min_reviews * 1.5)
            adjusted_max = int(max_reviews * 1.5)
        elif age_days > 180:  # 6-12 months old
            adjusted_min = int(min_reviews * 1.2)
            adjusted_max = int(max_reviews * 1.2)
        elif age_days < 30:  # Less than 1 month old
            adjusted_min = int(min_reviews * 0.5)
            adjusted_max = int(max_reviews * 0.7)
        else:
            adjusted_min = min_reviews
            adjusted_max = max_reviews
        
        # Ensure we stay within reasonable bounds
        adjusted_min = max(5, min(adjusted_min, max_reviews))
        adjusted_max = max(adjusted_min + 5, min(adjusted_max, 50))
        
        return get_natural_review_count(adjusted_min, adjusted_max)
        
    except:
        # If date parsing fails, use default
        return get_natural_review_count(min_reviews, max_reviews)

def generate_bulk_review_distribution(products, min_reviews=10, max_reviews=30, use_smart_distribution=True):
    """
    Generate review counts for multiple products with realistic distribution
    
    Args:
        products: List of product dictionaries
        min_reviews: Minimum reviews per product
        max_reviews: Maximum reviews per product
        use_smart_distribution: Use smart distribution based on product attributes
    
    Returns:
        Dictionary mapping product_id to review_count
    """
    distribution = {}
    
    for product in products:
        product_id = str(product.get('id'))
        
        if use_smart_distribution:
            # Consider product age and category
            base_count = get_age_based_review_count(
                product.get('created_at'), 
                min_reviews, 
                max_reviews
            )
            
            # Apply category factor
            category_factor = get_product_category_factor(product.get('title', ''))
            final_count = int(base_count * category_factor)
            
            # Ensure within bounds
            final_count = max(min_reviews, min(final_count, max_reviews))
        else:
            # Simple natural distribution
            final_count = get_natural_review_count(min_reviews, max_reviews)
        
        distribution[product_id] = final_count
    
    return distribution