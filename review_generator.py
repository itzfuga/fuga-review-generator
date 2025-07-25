"""
Advanced Review Generation Engine
Ported from the original sophisticated review generator with enhanced capabilities
"""
import random
from datetime import datetime, timedelta

# Review templates with sophisticated language patterns
REVIEW_TITLES = {
    "de": {
        5: [
            "Absolut fantastisch!", "Perfektes Produkt!", "Begeistert!", "Übertrifft alle Erwartungen!",
            "Einfach traumhaft!", "Ein Muss für jeden!", "Beste Entscheidung ever!", "Mega Teil!",
            "Krass gut!", "10/10 würde wieder kaufen", "Bin so happy damit!", "Absolut verliebt!",
            "Das ist der Hammer!", "Perfekt für mich!", "Genau was ich gesucht hab!"
        ],
        4: [
            "Sehr gutes Produkt", "Fast perfekt", "Wirklich schön", "Bin sehr zufrieden", 
            "Toller Kauf", "Gute Qualität", "Sehr empfehlenswert", "Passt super"
        ],
        3: [
            "Ganz okay", "Erfüllt seinen Zweck", "Für den Preis in Ordnung", "Mittelmäßig",
            "Geht so", "Nicht schlecht", "Durchschnittlich"
        ]
    },
    "en": {
        5: [
            "Absolutely amazing!", "Perfect product!", "Love it so much!", "Obsessed with this!",
            "Simply wonderful!", "Best product ever!", "Totally in love!", "So freaking good!",
            "This is incredible!", "10/10 would recommend", "Exceeded expectations!", "Pure perfection!",
            "Can't live without it!", "Best purchase ever!", "Absolutely obsessed!"
        ],
        4: [
            "Very good product", "Almost perfect", "Really nice", "Very satisfied", 
            "Great purchase", "Good quality", "Highly recommend", "Really happy with this"
        ],
        3: [
            "Decent", "Serves its purpose", "Okay for the price", "Pretty decent", 
            "It's fine", "Not bad", "Average product"
        ]
    }
}

# Sophisticated name generation
FIRST_NAMES = {
    "de": [
        "Max", "Sophie", "Leon", "Marie", "Felix", "Emma", "Paul", "Mia", "Ben", "Hannah",
        "Luca", "Lea", "Noah", "Anna", "Tim", "Lina", "Jonas", "Clara", "Luis", "Zoe",
        "Finn", "Maja", "Nico", "Lisa", "Jan", "Sarah", "Tom", "Julia", "Alex", "Nina"
    ],
    "en": [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "Logan",
        "Mia", "Lucas", "Charlotte", "Oliver", "Amelia", "Elijah", "Harper", "James", "Evelyn", "Benjamin",
        "Emily", "Jacob", "Madison", "Michael", "Elizabeth", "Alexander", "Sofia", "William", "Victoria", "Daniel"
    ]
}

# Trendy usernames for alternative aesthetic
USERNAMES = [
    "dark", "goth", "alt", "witch", "rebel", "moon", "vibe", "aesthetic", "punk", "grunge",
    "angel", "devil", "retro", "vintage", "cyber", "neon", "toxic", "soul", "chaos", "void",
    "shadow", "mystic", "cosmic", "violet", "raven", "ghost", "dream", "skull", "velvet", "storm",
    "blood", "crystal", "night", "dead", "horror", "black", "evil", "death", "hell", "satan",
    "witch", "vampire", "zombie", "demon", "gothic", "metal", "rock", "punk", "emo", "scene"
]

def generate_username():
    """Generate trendy alternative username"""
    base = random.choice(USERNAMES)
    
    # Add numbers sometimes
    if random.random() < 0.4:
        base += str(random.randint(1, 99))
    
    # Add underscores sometimes
    if random.random() < 0.3:
        base += "_" + random.choice(["girl", "boy", "vibe", "aesthetic", "666", "13", "xoxo"])
    
    return base

def generate_reviewer_info(language="en"):
    """Generate sophisticated reviewer information"""
    # 60% chance for trendy username, 40% for real name
    if random.random() < 0.6:
        name = generate_username()
        email = f"{name}@gmail.com"
    else:
        names = FIRST_NAMES.get(language, FIRST_NAMES["en"])
        first_name = random.choice(names)
        last_initial = random.choice(["S.", "M.", "K.", "L.", "B.", "T.", "R.", "H.", "C.", "J."])
        name = f"{first_name} {last_initial}"
        email = f"{first_name.lower()}.{last_initial[0].lower()}@gmail.com"
    
    # Location based on language with more variety
    if language == "de":
        location = random.choice(['DE', 'AT', 'CH', 'DE', 'DE'])  # Weighted towards DE
    else:
        location = random.choice(['US', 'UK', 'CA', 'AU', 'US', 'US'])  # Weighted towards US
    
    return name, email, location

def generate_review_content(product, rating, language="en"):
    """Generate sophisticated, context-aware review content"""
    # 8% chance for empty review (only on 5-star ratings)
    if random.random() < 0.08 and rating == 5:
        return ""
    
    # Product analysis
    title_lower = product['title'].lower()
    product_type = product.get('product_type', '').lower()
    
    # Advanced product categorization
    categories = {
        'clothing': ['jacket', 'hoodie', 'shirt', 't-shirt', 'dress', 'pants', 'jeans', 'top'],
        'accessories': ['bag', 'backpack', 'jewelry', 'necklace', 'ring', 'bracelet', 'earring'],
        'shoes': ['shoe', 'boot', 'sneaker', 'sandal'],
        'tech': ['phone', 'case', 'charger', 'cable', 'headphone', 'speaker'],
        'home': ['mug', 'pillow', 'blanket', 'poster', 'art', 'decoration']
    }
    
    detected_category = None
    for category, keywords in categories.items():
        if any(keyword in title_lower for keyword in keywords):
            detected_category = category
            break
    
    # Generate content based on category and rating
    if language == "de":
        content = generate_german_content(product, rating, detected_category, title_lower)
    else:
        content = generate_english_content(product, rating, detected_category, title_lower)
    
    return content

def generate_german_content(product, rating, category, title_lower):
    """Generate German review content"""
    if rating == 5:
        if category == 'clothing':
            return random.choice([
                "Bin mega happy damit! Sitzt perfekt und das Material ist top qualität. Hab schon mehrere Komplimente bekommen 😍",
                "Diese Jacke ist der absolute Hammer! Perfekt für Festivals und sieht einfach krass aus",
                "Qualität ist unglaublich gut, hab schon 3 Stück bestellt weil ich so begeistert bin",
                "Beste Techwear Jacke ever! Sitzt wie angegossen und hält richtig warm",
                "Bin so verliebt in das Teil! Material fühlt sich premium an und Design ist einfach 🔥"
            ])
        elif category == 'accessories':
            return random.choice([
                "Der Bag ist einfach perfekt! Passt super zu meinem Aesthetic und ist mega praktisch",
                "Qualität übertrifft alle Erwartungen. Sieht genauso aus wie auf den Bildern!",
                "Hab den schon seit Monaten und immer noch wie neu. Absolute Kaufempfehlung!"
            ])
        else:
            return random.choice([
                "Bin mega happy damit! Qualität top und Versand war schnell 🚀",
                "Absolut geil! Hab direkt noch eins bestellt für meine Schwester",
                "10/10 würde wieder kaufen, Fuga macht einfach die besten Sachen",
                "Perfekt! Genau was ich gesucht hab und noch besser als erwartet",
                "Bin so begeistert! Material ist top und Design einfach hammer",
                "Krass gut! Übertrifft alle Erwartungen und sieht mega aus",
                "Einfach nur wow! Beste Qualität die ich je hatte",
                "Bin total verliebt! Passt perfekt zu meinem Style",
                "Hammer Teil! Würde ich jedem empfehlen",
                "Richtig gute Investition! Material fühlt sich premium an",
                "Genial! Sieht noch besser aus als auf den Fotos",
                "Top Qualität und mega schnelle Lieferung! Danke!",
                "Bin restlos begeistert! Definitiv nicht mein letzter Kauf",
                "Wahnsinnig gut verarbeitet! Jeden Cent wert",
                "Einfach perfekt! Genau das was ich gesucht habe"
            ])
    
    elif rating == 4:
        return random.choice([
            "Sehr zufrieden mit dem Kauf. Gute Qualität für den Preis",
            "Wirklich schönes Produkt, nur die Lieferung hätte schneller sein können",
            "Fast perfekt, nur eine Kleinigkeit die mich stört aber sonst top",
            "Sehr gute Qualität, würde ich weiterempfehlen"
        ])
    
    else:  # rating == 3
        return random.choice([
            "Ganz okay für den Preis. Erfüllt seinen Zweck",
            "Mittelmäßige Qualität, aber auch nicht schlecht",
            "Für den Preis in Ordnung, hab schon bessere gesehen"
        ])

def generate_english_content(product, rating, category, title_lower):
    """Generate English review content"""
    if rating == 5:
        if category == 'clothing':
            return random.choice([
                "Obsessed with this piece! Quality is insane and fits perfectly. Got so many compliments already 😍",
                "This jacket is absolutely incredible! Perfect for festivals and concerts, love the aesthetic",
                "Quality exceeded my expectations, already ordered 2 more because I'm so in love with it",
                "Best techwear piece I own! Fits like a glove and keeps me warm in any weather",
                "Can't stop wearing this! Material feels so premium and the design is just 🔥"
            ])
        elif category == 'accessories':
            return random.choice([
                "This bag is everything I wanted! Perfect size and matches my vibe perfectly",
                "Quality is amazing, looks exactly like the photos. Super happy with this purchase!",
                "Had this for months now and still looks brand new. Definitely recommend!"
            ])
        else:
            return random.choice([
                "So happy with this! Quality is top tier and shipping was super fast 🚀",
                "Absolutely love it! Ordered another one immediately for my friend",
                "10/10 would buy again, Fuga always delivers the best products",
                "Perfect! Exactly what I was looking for and even better than expected",
                "Totally obsessed! Material is amazing and design is fire",
                "This exceeded all my expectations! Worth every penny",
                "Amazing quality and super stylish. Love everything about it!",
                "Couldn't be happier with this purchase. Highly recommend!",
                "Outstanding product! The attention to detail is incredible",
                "Blown away by the quality. This is going to be my new favorite!",
                "Fantastic! Looks even better in person than in photos",
                "Love the craftsmanship and unique design. Perfect addition!",
                "Superior quality and fast shipping. Will definitely order again!",
                "This is exactly what I was looking for. Premium feel and look!",
                "Impressed by the build quality. Money well spent!"
            ])
    
    elif rating == 4:
        return random.choice([
            "Very satisfied with the purchase. Good quality for the price",
            "Really nice product, only wish shipping was faster",
            "Almost perfect, just one tiny thing bothers me but overall great",
            "Very good quality, would definitely recommend to others"
        ])
    
    else:  # rating == 3
        return random.choice([
            "Decent for the price. Does what it's supposed to do",
            "Average quality, but not bad either",
            "Okay for the price, seen better but also seen worse"
        ])

def generate_age_appropriate_slang(age_group, language="en"):
    """Generate age-appropriate slang and expressions"""
    if language == "de":
        if age_group == "young":  # 16-25
            return random.choice(["mega", "krass", "hammer", "geil", "fire", "wild"])
        elif age_group == "adult":  # 25-40
            return random.choice(["super", "toll", "schön", "gut"])
        else:  # 40+
            return random.choice(["sehr gut", "wunderbar", "ausgezeichnet"])
    else:
        if age_group == "young":  # 16-25
            return random.choice(["fire", "slaps", "no cap", "bussin", "periodt", "slay"])
        elif age_group == "adult":  # 25-40
            return random.choice(["amazing", "awesome", "great", "love it"])
        else:  # 40+
            return random.choice(["excellent", "wonderful", "very good", "satisfied"])

def add_realistic_touches(content, rating, language="en"):
    """Add realistic touches like typos, emojis, etc."""
    # Add emojis occasionally (higher chance on 5-star reviews)
    emoji_chance = 0.3 if rating == 5 else 0.1 if rating == 4 else 0.05
    
    if random.random() < emoji_chance:
        emojis = ["😍", "🔥", "💯", "✨", "👌", "🚀", "💖", "⭐"] if rating >= 4 else ["😐", "🤷‍♀️", "😕"]
        content += " " + random.choice(emojis)
    
    # Occasional typos for realism (very low chance)
    if random.random() < 0.05:
        typos = {
            "the": "teh", "and": "adn", "love": "lov", "great": "gerat",
            "quality": "qualiy", "perfect": "perfekt"
        }
        for original, typo in typos.items():
            if original in content.lower():
                content = content.replace(original, typo, 1)
                break
    
    return content