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

def get_simplified_product_name(title, language="en"):
    """Simplify product name for natural reviews"""
    title_lower = title.lower()
    
    # Common simplifications
    if "jacket" in title_lower or "jacke" in title_lower:
        return "jacket" if language == "en" else "jacke"
    elif "hoodie" in title_lower:
        return "hoodie"
    elif "shirt" in title_lower:
        return "shirt"
    elif "dress" in title_lower:
        return "dress" if language == "en" else "kleid"
    elif "bag" in title_lower:
        return "bag" if language == "en" else "tasche"
    elif "belt" in title_lower or "gürtel" in title_lower:
        return "belt" if language == "en" else "gürtel"
    else:
        return "piece" if language == "en" else "teil"

def generate_review_content(product, rating, language="en"):
    """Generate Gen Z style review content like old_review.py"""
    # 15% chance for empty review
    if random.random() < 0.15:
        return ""
    
    # Get simplified product name
    simplified_name = get_simplified_product_name(product['title'], language)
    
    # 35% chance for short one-liner review
    if random.random() < 0.35:
        return random.choice(get_short_reviews(language))
    
    # Build modular review with multiple components
    review_components = []
    
    # Component 1: Intro based on rating and language
    intros = get_intro_phrases(simplified_name, rating, language)
    if intros:
        review_components.append(random.choice(intros))
    
    # Component 2: Product-specific phrases (60% chance)
    if random.random() < 0.6:
        category_phrases = get_category_phrases(product['title'], language)
        if category_phrases:
            selected_phrases = random.sample(category_phrases, min(2, len(category_phrases)))
            if review_components and random.random() < 0.5:
                # Connect with previous component
                connectors = get_connectors(language)
                conn = random.choice(connectors)
                if conn in [".", "!"]:
                    review_components[-1] += conn
                    review_components.append(" ".join(selected_phrases))
                else:
                    review_components[-1] += conn + " ".join(selected_phrases)
            else:
                review_components.append(" ".join(selected_phrases))
    
    # Component 3: Shop reference (25% chance)
    if random.random() < 0.25:
        shop_refs = get_shop_references(language)
        if shop_refs and review_components:
            connectors = [". ", "! ", " and " if language == "en" else " und "]
            conn = random.choice(connectors)
            if conn in [".", "!"]:
                review_components[-1] += conn
                review_components.append(random.choice(shop_refs))
            else:
                review_components[-1] += conn + random.choice(shop_refs)
    
    # Join components
    review = " ".join(review_components)
    
    # Apply youth writing style (40% chance - more like old_review.py)
    if random.random() < 0.4:
        review = apply_youth_style(review, language)
    
    return review

def get_short_reviews(language):
    """Short one-liner reviews with Gen Z slang"""
    short_reviews = {
        "de": [
            "krass gut!!!", "omg, neues lieblingsstück💖", "hab sofort zugeschlagen!!!", "vibes sind immaculate✨", "style ist brutal", 
            "10/10 würd nochmal kaufen", "Für parties perfekt!!", "hab schon 5 komplimente bekommen lol", "Mega fit check material",
            "aesthetic af", "obssessed damit!!!!", "Liebe das design sm", "straight fire 🔥🔥🔥", "fashion slay fr", 
            "direkt ausgegangen damit", "sieht 100x besser aus als auf insta", "fuga studios killt es wieder mal", "gibts in jeder farbe?",
            "shipping war flott", "insta feed material", "outfit mit diesem teil = iconic", "hatte fomo, aber jetz ist meins!",
            "kann nicht aufhören es zu tragen tbh", "so in love mit dem style", "muss es in allen farben haben lmaoo", "hab von fuga auf tiktok gehört"
        ],
        "en": [
            "obsessed!!!!", "new fav piece no cap", "copped instantly🔥", "the vibes are immaculate✨", "straight fire fit", 
            "10/10 would cop again", "perfect for partying!!", "got 5 compliments already lmao", "major fit check material",
            "aesthetic af", "literally can't take it off", "lowkey love this sm", "absolutely slayed", "fashion served frfr", 
            "went out in it right away", "looks 100x better irl", "fuga studios killing it again", "need this in every color",
            "shipping was quick", "literally my insta feed aesthetic", "outfit w this = iconic", "had fomo but now it's mine!",
            "can't stop wearing this tbh", "so in love w the style", "gotta have it in all colors lol", "saw fuga on tiktok and had to buy"
        ]
    }
    return short_reviews.get(language, short_reviews["en"])

def get_intro_phrases(simplified_name, rating, language):
    """Intro phrases with product name integration"""
    intros = {
        "de": {
            5: [
                f"obsessed mit diesem {simplified_name}!!!",
                f"hab das {simplified_name} direkt gecopt und zero regrets",
                f"omg dieser {simplified_name} ist literally perfection",
                f"brauchte ein {simplified_name} und hab jackpot gewonnen"
            ],
            4: [
                f"richtig nice {simplified_name}",
                f"hab das {simplified_name} endlich bekommen",
                f"das {simplified_name} ist echt cool",
                f"ziemlich happy mit dem {simplified_name}"
            ],
            3: [
                f"das {simplified_name} ist okay",
                f"{simplified_name} ist ganz nice",
                f"hab mir das {simplified_name} gegönnt",
                f"das {simplified_name} erfüllt seinen zweck"
            ]
        },
        "en": {
            5: [
                f"obsessed with this {simplified_name}!!!",
                f"copped this {simplified_name} and zero regrets",
                f"omg this {simplified_name} is literally perfection",
                f"needed a {simplified_name} and hit the jackpot"
            ],
            4: [
                f"really nice {simplified_name}",
                f"finally got this {simplified_name}",
                f"this {simplified_name} is pretty cool",
                f"pretty happy with the {simplified_name}"
            ],
            3: [
                f"this {simplified_name} is okay",
                f"{simplified_name} is nice enough",
                f"treated myself to this {simplified_name}",
                f"this {simplified_name} does the job"
            ]
        }
    }
    return intros.get(language, {}).get(rating, [])

def get_category_phrases(title, language):
    """Category-specific phrases based on product type like old_review.py"""
    title_lower = title.lower()
    
    # Gothic/alternative style phrases (Opium, Rebel, Dark, etc.)
    if any(word in title_lower for word in ["opium", "goth", "black", "dark", "rebel", "skull", "rave", "punk"]):
        if language == "de":
            return [
                "dark vibes ohne costumey zu wirken",
                "edgy aber trotzdem alltagstauglich", 
                "perfekt für mein dark academia aesthetic",
                "erste wahl für festivals und clubs",
                "details sind echt unique",
                "statement piece für jeden goth look",
                "passt perfekt zu meinen platforms",
                "gothic ohne tryhard zu sein",
                "witchy energy in der besten art",
                "elevated goth das überall funktioniert"
            ]
        else:
            return [
                "dark vibes without looking costumey",
                "edgy but still wearable daily",
                "perfect for my dark academia aesthetic", 
                "first choice for festivals and clubs",
                "details are genuinely unique",
                "statement piece for any goth look",
                "pairs perfectly with my platforms",
                "gothic without being tryhard",
                "witchy energy in the best way",
                "elevated goth that works anywhere",
                "hardcore punk vibes without trying too hard",
                "rebellious energy but still wearable"
            ]
    
    # Tops/clothing phrases
    elif any(word in title_lower for word in ["top", "shirt", "jacket", "hoodie", "dress"]):
        if language == "de":
            return [
                "sitzt wie angegossen",
                "material fühlt sich premium an", 
                "perfekt für layering",
                "bekomm ständig komplimente dafür",
                "sieht teurer aus als es war",
                "perfekte oversized silhouette",
                "details sind nicht basic",
                "übergang von tag zu nacht",
                "warm ohne bulky zu sein"
            ]
        else:
            return [
                "fits like a second skin",
                "material feels premium af",
                "perfect for layering", 
                "getting compliments non-stop",
                "looks way more expensive than it was",
                "silhouette is perfectly oversized",
                "details are not basic",
                "transitions from day to night",
                "warm without being bulky",
                "just the right amount of crop",
                "breathable even at crowded parties"
            ]
    
    # Default phrases with more Gen Z energy
    if language == "de":
        return [
            "qualität ist krass gut",
            "sieht genauso aus wie auf den bildern", 
            "würd ich definitiv weiterempfehlen",
            "shipping war mega schnell",
            "hab schon 5 komplimente bekommen lol",
            "aesthetic af",
            "straight fire design",
            "kann nicht aufhören es zu tragen tbh"
        ]
    else:
        return [
            "quality is insane",
            "looks exactly like the pics",
            "would definitely recommend", 
            "shipping was super fast",
            "got 5 compliments already lmao",
            "aesthetic af",
            "straight fire design", 
            "can't stop wearing this tbh",
            "literally my insta feed aesthetic",
            "major fit check material"
        ]

def get_shop_references(language):
    """Shop and brand references"""
    if language == "de":
        return [
            "fuga studios macht einfach die besten sachen",
            "hab schon mehrere teile von fuga",
            "fuga enttäuscht nie",
            "wieder mal ein hit von fuga"
        ]
    else:
        return [
            "fuga studios never misses",
            "already have multiple pieces from fuga",
            "fuga always delivers",
            "another banger from fuga"
        ]

def get_connectors(language):
    """Connecting words for joining review components"""
    if language == "de":
        return [" und ", " - ", ", ", ". ", "! ", " btw ", " aber "]
    else:
        return [" and ", " - ", ", ", ". ", "! ", " btw ", " but "]

def apply_youth_style(review, language):
    """Apply Gen Z writing style"""
    import re
    
    # Lowercase sentence start sometimes
    if random.random() < 0.3:
        review = review[0].lower() + review[1:] if len(review) > 1 else review.lower()
    
    # Multiple exclamation marks
    if review and review[-1] in [".", "!"]:
        num_excl = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10], k=1)[0]
        review = review[:-1] + "!" * num_excl
        
        # Add emojis (50% chance)
        if random.random() < 0.5:
            emojis = ["💖", "✨", "🔥", "👌", "💯", "🙌", "😍", "🤩", "🥰", "💕", "❤️", "🖤", "👑", "🌟"]
            num_emojis = random.choices([1, 2, 3], weights=[50, 30, 20], k=1)[0]
            selected_emojis = random.sample(emojis, min(num_emojis, len(emojis)))
            review += "".join(selected_emojis)
    
    return review

