"""
Standalone review generator for Fuga Studios - no external dependencies
"""
import json
import requests
import csv
import random
from datetime import datetime, timedelta

# Shopify credentials (will be set via environment variables in production)
SHOP_DOMAIN = "your-shop.myshopify.com"
ACCESS_TOKEN = "your-access-token"
API_VERSION = "2024-01"

# Review templates from original generator
REVIEW_TITLES = {
    "de": {
        5: ["Absolut fantastisch!", "Perfektes Produkt!", "Begeistert!", "Übertrifft alle Erwartungen!",
            "Einfach traumhaft!", "Ein Muss für jeden!", "Beste Entscheidung ever!", "Mega Teil!"],
        4: ["Sehr gutes Produkt", "Fast perfekt", "Wirklich schön", "Bin sehr zufrieden", "Toller Kauf"],
        3: ["Ganz okay", "Erfüllt seinen Zweck", "Für den Preis in Ordnung", "Mittelmäßig"]
    },
    "en": {
        5: ["Absolutely amazing!", "Perfect product!", "Love it so much!", "Obsessed with this!",
            "Simply wonderful!", "Best product ever!", "Totally in love!", "So freaking good!"],
        4: ["Very good product", "Almost perfect", "Really nice", "Very satisfied", "Great purchase"],
        3: ["Decent", "Serves its purpose", "Okay for the price", "Pretty decent", "It's fine"]
    }
}

# Names for review generation
FIRST_NAMES = {
    "de": ["Max", "Sophie", "Leon", "Marie", "Felix", "Emma", "Paul", "Mia", "Ben", "Hannah"],
    "en": ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "Logan"]
}

USERNAMES = ["dark", "goth", "alt", "witch", "rebel", "moon", "vibe", "aesthetic", "punk", "grunge", 
             "angel", "devil", "retro", "vintage", "cyber", "neon", "toxic", "soul", "chaos", "void"]

def fetch_products():
    """Fetch all products from Shopify"""
    print("📦 Fetching products from Fuga Studios...")
    
    url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/products.json?limit=250"
    headers = {
        'X-Shopify-Access-Token': ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        products = response.json()['products']
        print(f"✅ Found {len(products)} products")
        return products
    return []

def generate_username():
    """Generate trendy username"""
    base = random.choice(USERNAMES)
    if random.random() < 0.5:
        base += str(random.randint(1, 99))
    return base

def generate_reviewer_info(language="en"):
    """Generate reviewer information"""
    # 60% chance for username
    if random.random() < 0.6:
        name = generate_username()
        email = f"{name}@gmail.com"
    else:
        names = FIRST_NAMES.get(language, FIRST_NAMES["en"])
        name = random.choice(names) + " " + random.choice(["S.", "M.", "K.", "L.", "B."])
        email = f"{name.lower().replace(' ', '.').replace('.', '')}@gmail.com"
    
    # Location based on language
    if language == "de":
        location = random.choice(['DE', 'AT', 'CH'])
    else:
        location = random.choice(['US', 'UK', 'CA'])
    
    return name, email, location

def generate_review_content(product, rating, language="en"):
    """Generate review content"""
    # 15% chance for empty review
    if random.random() < 0.15:
        return ""
    
    # Product type detection
    title_lower = product['title'].lower()
    product_type = product.get('product_type', '').lower()
    
    # Simple content templates
    if "jacket" in title_lower or "jacke" in title_lower:
        if language == "de" and rating == 5:
            return random.choice([
                "Diese Jacke ist der Hammer! Perfekt für Festivals und sieht mega aus",
                "Qualität ist krass gut, hab schon 3 Komplimente bekommen",
                "Beste Techwear Jacke ever, sitzt perfekt und hält warm"
            ])
        elif rating == 5:
            return random.choice([
                "This jacket is insane! Perfect for festivals and looks amazing",
                "Quality is incredible, already got 3 compliments",
                "Best techwear jacket ever, fits perfectly and keeps warm"
            ])
    
    # Generic templates
    if language == "de":
        if rating == 5:
            return random.choice([
                "Bin mega happy damit! Qualität top und Versand war schnell",
                "Absolut geil! Hab direkt noch eins bestellt",
                "10/10 würde wieder kaufen, Fuga macht einfach die besten Sachen"
            ])
        elif rating == 4:
            return "Sehr zufrieden mit dem Kauf. Gute Qualität für den Preis"
    else:
        if rating == 5:
            return random.choice([
                "So happy with this! Quality is top and shipping was fast",
                "Absolutely love it! Ordered another one right away",
                "10/10 would buy again, Fuga makes the best stuff"
            ])
        elif rating == 4:
            return "Very satisfied with the purchase. Good quality for the price"
    
    return "Good product"

def main():
    print("🛍️ FUGA STUDIOS REVIEW GENERATOR (Standalone)")
    print("=" * 45)
    
    # Fetch products
    products = fetch_products()
    if not products:
        print("❌ No products found")
        return
    
    # Generate reviews
    reviews = []
    review_count = 0
    
    for product in products:
        # Skip clearance/special products
        if 'clearance' in product['title'].lower():
            continue
        
        # Generate 3-8 reviews per product
        num_reviews = random.randint(3, 8)
        
        for _ in range(num_reviews):
            # Language distribution: 50% EN, 30% DE, 20% EN
            lang = random.choices(["en", "de", "en"], weights=[50, 30, 20])[0]
            
            # Rating distribution: 60% 5-star, 30% 4-star, 10% 3-star
            rating = random.choices([5, 4, 3], weights=[60, 30, 10])[0]
            
            # Generate reviewer
            name, email, location = generate_reviewer_info(lang)
            
            # Review title
            title = random.choice(REVIEW_TITLES[lang][rating])
            
            # Review content
            content = generate_review_content(product, rating, lang)
            
            # Random date in last 36 months
            days_ago = random.randint(1, 36 * 30)
            review_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            reviews.append({
                'product_id': str(product['id']),
                'product_handle': product['handle'],
                'product_sku': product.get('variants', [{}])[0].get('sku', ''),
                'product_name': product['title'],
                'reviewer_name': name,
                'reviewer_email': email,
                'reviewer_location': location,
                'review_title': title,
                'review_content': content,
                'review_date': review_date,
                'image_urls': '',
                'status': 'Published',
                'rating': str(rating),
                'verified': 'Yes' if random.random() > 0.05 else 'No',
                'reply_content': '',
                'reply_date': '',
                'is_store_review': 'false'
            })
            
            review_count += 1
            
        # Progress update
        if len(reviews) % 100 == 0:
            print(f"   Generated {len(reviews)} reviews so far...")
    
    print(f"\n✅ Generated {len(reviews)} reviews total")
    
    # Save to CSV
    filename = 'fuga_shopify_reviews.csv'
    print(f"\n💾 Saving to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)
    
    print(f"✅ Saved successfully!")
    
    # Show samples
    print("\n📝 Sample reviews:")
    for i, review in enumerate(reviews[:5]):
        print(f"\n{i+1}. {review['product_name']}")
        print(f"   {'⭐' * int(review['rating'])} - {review['review_title']}")
        print(f"   \"{review['review_content']}\"")
        print(f"   - {review['reviewer_name']} from {review['reviewer_location']}")

if __name__ == "__main__":
    main()