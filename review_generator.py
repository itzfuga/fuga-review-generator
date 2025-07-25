"""
Advanced Review Generation Engine
Matches the sophisticated Gen Z style of old_review.py with enhanced capabilities
"""
import random
from datetime import datetime, timedelta
import re

# Review titles with sophisticated language patterns
REVIEW_TITLES = {
    "de": {
        5: [
            "Absolut fantastisch!", "Perfektes Produkt!", "Begeistert!", "Übertrifft alle Erwartungen!",
            "Einfach traumhaft!", "Ein Muss für jeden!", "Kann ich nur empfehlen!", "Bestes Produkt ever!",
            "Erstklassige Qualität!", "Liebe es!", "Top Produkt!", "Hervorragende Wahl!", "Mega Teil!",
            "Voll cool!", "Krass gut!", "Einfach nur wow!", "Beste Entscheidung ever!"
        ],
        4: [
            "Sehr gutes Produkt", "Fast perfekt", "Wirklich schön", "Bin sehr zufrieden",
            "Gute Qualität", "Macht einen tollen Eindruck", "Empfehlenswert", "Positiv überrascht",
            "Toller Kauf", "Gutes Preis-Leistungs-Verhältnis", "Schönes Design", "Überzeugt mich",
            "Richtig nice", "Voll gut", "Echt cool", "Gefällt mir sehr"
        ],
        3: [
            "Ganz okay", "Erfüllt seinen Zweck", "Im Großen und Ganzen zufrieden", "Mittelmäßig",
            "Entspricht den Erwartungen", "Nicht schlecht", "Könnte besser sein", "Durchschnittlich",
            "Für den Preis in Ordnung", "Brauchbar", "Mittelklasse", "Okay für den Alltag",
            "Ganz nett", "Passt schon"
        ],
    },
    "en": {
        5: [
            "Absolutely amazing!", "Perfect product!", "Love it so much!", "Exceeds all expectations!",
            "Simply wonderful!", "A must-have!", "Highly recommend!", "Best product ever!",
            "First-class quality!", "Love it!", "Top product!", "Excellent choice!",
            "Obsessed with this!", "Literally perfect!", "Totally in love!", "So freaking good!"
        ],
        4: [
            "Very good product", "Almost perfect", "Really nice", "Very satisfied",
            "Good quality", "Makes a great impression", "Recommendable", "Positively surprised",
            "Great purchase", "Good value for money", "Beautiful design", "Convincing",
            "Really cool", "Pretty nice", "Very pleased with it", "Quite good"
        ],
        3: [
            "Decent", "Serves its purpose", "Satisfied overall", "Average",
            "Meets expectations", "Not bad", "Could be better", "Average",
            "Okay for the price", "Usable", "Middle-range", "Okay for everyday",
            "Pretty decent", "It's fine"
        ],
    }
}

# Shop references
SHOP_REFERENCES = {
    "de": [
        "Fuga Studios rockt einfach", "wieder mal bei Fuga zugeschlagen", "meine dritte Bestellung bei Fuga",
        "Fuga nie enttäuscht", "Fuga Studios ist mein go-to shop", "für Festival-Outfits ist Fuga unschlagbar",
        "Fuga kennt einfach den vibe", "Fuga versteht alternative fashion", "seit ich Fuga entdeckt hab kauf ich nix anderes mehr"
    ],
    "en": [
        "Fuga Studios rocks", "hit up Fuga again", "my third Fuga haul",
        "Fuga never disappoints", "Fuga Studios is my go-to", "for festival fits Fuga is unmatched",
        "Fuga just gets the vibe", "Fuga understands alt fashion", "since finding Fuga I don't shop anywhere else"
    ]
}

# Social media references
SOCIAL_MEDIA_REFS = {
    "de": [
        "hab's auf TikTok gesehen und sofort bestellt", "nach dem Insta Post musste ich es haben", 
        "auf TikTok viral gegangen und verständlich warum", "alle meine Freunde auf Insta fragen wo es her ist",
        "perfekt für meine aesthetic auf Insta", "war auf meiner wishlist seit dem TikTok von @", 
        "hab's im Fuga lookbook gesehen und sofort verliebt", "tiktok made me buy it - no regrets"
    ],
    "en": [
        "saw it on TikTok and ordered instantly", "had to cop after that Insta post", 
        "went viral on TikTok for a reason", "all my friends on Insta asking where it's from",
        "perfect for my Insta aesthetic", "been on my wishlist since @'s TikTok", 
        "saw it in Fuga's lookbook and fell in love", "tiktok made me buy it - zero regrets"
    ]
}

# Shipping comments
SHIPPING_COMMENTS = {
    "de": [
        "Versand war schneller als erwartet", "Paket kam in nur 2 Tagen an - nice",
        "Verpackung war cute af", "Lieferung war mega schnell", 
        "Versand hat etwas gedauert aber war's wert", "kam pünktlich zum Festival an - danke!!!", 
        "Bestellung problemlos, nächstes mal bitte schnellerer Versand", "Bestellung kam mit süßer Notiz"
    ],
    "en": [
        "shipping was faster than expected", "package arrived in just 2 days - nice",
        "packaging was cute af", "delivery was super quick", 
        "shipping took a bit but so worth it", "arrived just in time for the festival - thanks!!!", 
        "ordering was easy, hope shipping is faster next time", "order came with a cute note"
    ]
}

# Short one-liner reviews
SHORT_REVIEWS = {
    "de": [
        "krass gut!!!", "omg, neues lieblingsstück💖", "hab sofort zugeschlagen!!!", "vibes sind immaculate✨", "style ist brutal", 
        "10/10 würd nochmal kaufen", "Für parties perfekt!!", "hab schon 5 komplimente bekommen lol", "Mega fit check material",
        "aesthetic af", "obssessed damit!!!!", "Liebe das design sm", "straight fire 🔥🔥🔥", "fashion slay fr", 
        "direkt ausgegangen damit", "sieht 100x besser aus als auf insta", "fuga studios killt es wieder mal", "gibts in jeder farbe?",
        "shipping war flott", "insta feed material", "outfit mit diesem teil = iconic", "hatte fomo, aber jetz ist meins!",
        "kann nicht aufhören es zu tragen tbh", "so in love mit dem style", "muss es in allen farben haben lmaoo", "hab von fuga auf tiktok gehört",
        "bin verliebt 😍", "quality ist insane", "perfekt für den summer", "endlich mal was gutes", "mega happy damit",
        "würde 6 sterne geben", "beste purchase dieses jahr", "passt zu allem", "fühlt sich teuer an", "chef's kiss 👌"
    ],
    "en": [
        "obsessed!!!!", "new fav piece no cap", "copped instantly🔥", "the vibes are immaculate✨", "straight fire fit", 
        "10/10 would cop again", "perfect for partying!!", "got 5 compliments already lmao", "major fit check material",
        "aesthetic af", "literally can't take it off", "lowkey love this sm", "absolutely slayed", "fashion served frfr", 
        "went out in it right away", "looks 100x better irl", "fuga studios killing it again", "need this in every color",
        "shipping was quick", "literally my insta feed aesthetic", "outfit w this = iconic", "had fomo but now it's mine!",
        "can't stop wearing this tbh", "so in love w the style", "gotta have it in all colors lol", "saw fuga on tiktok and had to buy",
        "am obsessed 😍", "quality is insane", "perfect for summer vibes", "finally something good", "so happy with this",
        "would give 6 stars", "best purchase this year", "goes with everything", "feels expensive af", "chef's kiss 👌"
    ]
}

# Review endings based on rating
REVIEW_ENDINGS = {
    "de": {
        5: [
            "Absolut empfehlenswert!", 
            "Werde definitiv wieder bestellen!", 
            "Eines meiner Lieblingsteile!",
            "Bin rundum zufrieden!",
            "Klare Kaufempfehlung!",
            "Ein absolutes Lieblingsteil in meinem Kleiderschrank!",
            "Würde es sofort wieder kaufen!"
        ],
        4: [
            "Kann ich empfehlen.", 
            "Bin sehr zufrieden mit dem Kauf.", 
            "Ein guter Kauf.",
            "Würde ich wieder kaufen.",
            "Macht einen wertigen Eindruck.",
            "Bin zufrieden mit meiner Wahl.",
            "Erfüllt meinen Zweck gut."
        ],
        3: [
            "Ist okay für den Preis.", 
            "Erfüllt seinen Zweck.", 
            "Nicht perfekt, aber brauchbar.",
            "Könnte in einigen Punkten besser sein.",
            "Für gelegentliches Tragen in Ordnung.",
            "Weder besonders gut noch schlecht.",
            "Bin weder begeistert noch enttäuscht."
        ]
    },
    "en": {
        5: [
            "Highly recommended!", 
            "Will definitely order again!", 
            "One of my favorites!",
            "Completely satisfied!",
            "Clear buy recommendation!",
            "An absolute favorite in my wardrobe!",
            "Would buy it again in a heartbeat!"
        ],
        4: [
            "Can recommend.", 
            "Very satisfied with the purchase.", 
            "A good buy.",
            "Would buy again.",
            "Makes a quality impression.",
            "Satisfied with my choice.",
            "Serves my purpose well."
        ],
        3: [
            "It's okay for the price.", 
            "Serves its purpose.", 
            "Not perfect, but usable.",
            "Could be better in some areas.",
            "Okay for occasional wear.",
            "Neither particularly good nor bad.",
            "Neither thrilled nor disappointed."
        ]
    }
}

# Product-specific phrases
PRODUCT_PHRASES = {
    "de": {
        "tops": [
            "passt zu literally allem in meinem closet", 
            "schnitt ist ultra flattering", 
            "material fühlt sich besser an als erwartet",
            "qualität ist besser als die teuren mainstream marken",
            "farbe ist noch geiler irl",
            "verarbeitung on point",
            "bekomme nonstop komplimente",
            "style ist sooo mein vibe",
            "hab direkt outfit pics gepostet",
            "trägt sich mega angenehm",
            "fabric ist so soft aber trotzdem nicht dünn",
            "detail am ausschnitt ist so unique",
            "kann man dressed up oder casual stylen"
        ],
        "bottoms": [
            "sitzt wie eine zweite haut", 
            "legit der comfyste shit ever", 
            "länge ist perfekt für meine größe",
            "stretch game ist on point",
            "die taschen sind tief genug für handy!!",
            "im club super bequem",
            "hab schon 3x getragen diese woche lol"
        ],
        "dresses": [
            "sitzt besser als alle dresses die ich hab", 
            "cutouts sind strategisch an den richtigen stellen", 
            "perfekt fürs date oder club",
            "der stoff fällt einfach anders",
            "die details am rücken sind alles",
            "länge ist sexy ohne too much",
            "feel mich wie main character energy darin"
        ],
        "accessories": [
            "elevates literally jeden basic look", 
            "qualität könnte locker das dreifache kosten", 
            "meine friends sind alle neidisch",
            "passt zu jedem outfit vibe",
            "design ist edgy aber trotzdem wearable",
            "größe ist perfekt adjustable",
            "komplettes statement piece"
        ],
        "outerwear": [
            "warm aber nicht bulky", 
            "silhouette ist perfekt oversized", 
            "details sind nicht basic",
            "layering game changer",
            "regentauglich getestet lol",
            "pockets sind tief genug für alles",
            "robust aber trotzdem fashion"
        ],
        "gothic": [
            "düsterer vibe ohne cosplay zu wirken", 
            "edgy aber trotzdem alltagstauglich", 
            "perfekt für meine dark academia aesthetic",
            "für festivals und clubs erste wahl",
            "details sind wirklich unique",
            "statement piece für jeden goth look",
            "harmoniert mit meinen platforms",
            "mystisch aber nicht overdone",
            "dark romantik energy",
            "witchy aber wearable",
            "gothic eleganz ohne kitsch",
            "passt zu meiner alternative wardrobe",
            "düster und sophisticated zugleich"
        ],
        "punk": [
            "hardcore punk vibes ohne try hard", 
            "rebellious energy aber trotzdem tragbar", 
            "outfit-maker piece",
            "perfekt für konzerte und moshpits",
            "details geben dem ganzen den edge",
            "mein go-to für jedes punk event",
            "passt zu meinen docs und ketten",
            "authentisch rebellisch",
            "punk attitude ohne kostüm effekt",
            "rock chic mit attitude",
            "perfekt für underground events",
            "rebel style mit class",
            "subkultur vibes aber stylisch"
        ],
        "vintage": [
            "y2k aesthetic ist on point", 
            "hat den perfekten retro vibe ohne costume zu sein", 
            "old school cool mit modernem fit",
            "nostalgic details mit zeitgemäßem schnitt",
            "zeitlos aber irgendwie auch current",
            "vintage inspired ohne outdated zu wirken",
            "hat den 90s vibe den ich gesucht hab"
        ]
    },
    "en": {
        "tops": [
            "goes with literally everything in my closet", 
            "cut is ultra flattering", 
            "material feels way better than expected",
            "quality beats the expensive mainstream brands",
            "color is even better irl",
            "construction is on point",
            "getting nonstop compliments",
            "style is sooo my vibe",
            "posted outfit pics right away",
            "wears so comfortably",
            "fabric is soft but not thin",
            "neckline detail is so unique",
            "can be styled dressed up or casual",
            "just the right amount of crop",
            "sleeves hit at the perfect spot",
            "makes my waist look snatched",
            "breathable even at crowded parties",
            "tempted to sleep in it lol"
        ],
        "bottoms": [
            "fits like a second skin", 
            "legit the comfiest thing ever", 
            "length is perfect for my height",
            "stretch game is on point",
            "pockets are actually deep enough for phone!!",
            "so comfy in the club",
            "already worn it 3x this week lol",
            "makes my legs look so good",
            "waistband doesn't roll down when dancing",
            "hugs all the right places",
            "durable for festival season",
            "the slit is perfectly placed"
        ],
        "dresses": [
            "fits better than any dress i own", 
            "cutouts are strategically in the right places", 
            "perfect for date night or clubbing",
            "the fabric just hits different",
            "the back details are everything",
            "length is sexy without being too much",
            "feel like main character energy in it",
            "so many ways to style it",
            "flattering for every body type",
            "the drape is immaculate",
            "makes me feel unstoppable",
            "easy to dance in all night"
        ],
        "accessories": [
            "elevates literally any basic look", 
            "quality could easily cost triple", 
            "all my friends are jealous",
            "matches every outfit vibe",
            "design is edgy but still wearable",
            "size is perfectly adjustable",
            "complete statement piece",
            "turns heads every time",
            "durable enough for everyday",
            "gives that expensive look",
            "unique without trying too hard",
            "feels lightweight but substantial"
        ],
        "outerwear": [
            "warm without being bulky", 
            "silhouette is perfectly oversized", 
            "details are not basic",
            "layering game changer",
            "rain-tested lol",
            "pockets deep enough for everything",
            "sturdy but still fashion",
            "transitions from day to night",
            "looks expensive af",
            "stands out in the best way",
            "hood actually stays up",
            "perfect weight for unpredictable weather"
        ],
        "gothic": [
            "dark vibes without looking costumey", 
            "edgy but still wearable daily", 
            "perfect for my dark academia aesthetic",
            "first choice for festivals and clubs",
            "details are genuinely unique",
            "statement piece for any goth look",
            "pairs perfectly with my platforms",
            "gives that effortless alt vibe",
            "gothic without being tryhard",
            "witchy energy in the best way",
            "elevated goth that works anywhere",
            "works for both daytime and nightlife",
            "mysterious but not overdone",
            "dark romantic energy",
            "gothic elegance without the cringe",
            "fits my alternative wardrobe perfectly",
            "moody aesthetic done right",
            "sophisticated darkness"
        ],
        "punk": [
            "hardcore punk vibes without trying too hard", 
            "rebellious energy but still wearable", 
            "outfit-maker piece",
            "perfect for concerts and moshpits",
            "details give it the edge",
            "my go-to for any punk event",
            "goes with my docs and chains",
            "functional for the pit",
            "punk aesthetic that's actually comfortable",
            "authentic without looking like a costume",
            "stands up to rowdy shows",
            "distressing is done just right",
            "genuinely rebellious style",
            "punk attitude without the costume effect",
            "rock chic with attitude",
            "perfect for underground shows",
            "rebel style with class",
            "subculture vibes but stylish"
        ],
        "vintage": [
            "y2k aesthetic is spot on", 
            "perfect retro vibe without looking costumey", 
            "old school cool with modern fit",
            "nostalgic details with contemporary cut",
            "timeless but somehow current",
            "vintage inspired without being outdated",
            "has the 90s vibe i've been searching for",
            "childhood fashion dreams come true",
            "early 2000s energy without the cringe",
            "retro silhouette that still feels fresh",
            "nostalgic in all the right ways",
            "makes me feel like i'm in my favorite old movie"
        ]
    }
}

def generate_youthful_username():
    """Generate trendy, youth-oriented usernames"""
    first_parts = [
        "xX", "x", "", "", "", "", ""  # More empty strings for natural distribution
    ]
    
    middle_parts = [
        "dark", "goth", "emo", "alt", "witch", "rebel", "astro", "moon", "night",
        "vibe", "style", "fashion", "trend", "aesthetic", "punk", "grunge", "death",
        "sad", "mood", "angel", "devil", "toxic", "retro", "vintage", "y2k", "fairy",
        "cyber", "digital", "glitch", "disco", "rave", "trap", "techno", "house", "indie",
        "core", "wave", "lilith", "mystic", "chaos", "neon", "cosmic", "dreamy", "void",
        "soul", "psycho", "doll", "baby", "kitty", "bunny", "honey", "cherry", "kiki",
        "crystal", "shadow", "demon", "grim", "doom", "hell", "heaven", "divine", "blessed",
        "cursed", "broken", "cool", "party", "slay", "queen", "king", "prince", "princess",
        "vapor", "haze", "cloud", "storm", "thunder", "rain", "sun", "moon", "star",
        "galaxy", "alien", "space", "planet", "mars", "venus", "saturn", "jupiter", "pluto"
    ]
    
    end_parts = [
        "Xx", "x", "xoxo", "", "", "", "",  # More empty strings
        "_", ".", "__", "..", "_x", "x_", ".x", "x.", 
        "_xo", "_", ".", "", "", "", ""
    ]
    
    numbers = ["", "", "", ""]  # 50% chance for no number
    for year in range(97, 6):  # Birth years for 18-24 year olds
        numbers.append(str(year))
    for i in range(1, 10):
        numbers.append(str(i))
    for i in range(10, 100):
        numbers.append(str(i))
    for i in [666, 420, 69, 13]:  # Popular numbers
        numbers.append(str(i))
    
    # Various username patterns
    patterns = [
        lambda: f"{random.choice(middle_parts)}{random.choice(numbers)}{random.choice(end_parts)}",
        lambda: f"{random.choice(first_parts)}{random.choice(middle_parts)}{random.choice(end_parts)}",
        lambda: f"{random.choice(middle_parts)}_{random.choice(middle_parts)}{random.choice(numbers)}",
        lambda: f"{random.choice(middle_parts)}.{random.choice(middle_parts)}{random.choice(numbers)}",
        lambda: f"{random.choice(middle_parts)}{random.choice(numbers)}",
        lambda: f"{random.choice(first_parts)}{random.choice(middle_parts)}{random.choice(numbers)}{random.choice(end_parts)}"
    ]
    
    return random.choice(patterns)()

def generate_reviewer_info(language="en"):
    """Generate realistic reviewer information"""
    # 60% chance for trendy username vs real name
    if random.random() < 0.6:
        reviewer_name = generate_youthful_username()
        
        # Email based on username
        domains = ["gmail.com", "outlook.com", "icloud.com", "yahoo.com", "hotmail.com", 
                  "protonmail.com", "web.de", "gmx.de", "gmx.net", "live.com"]
        email = f"{reviewer_name.lower().replace(' ', '').replace('.', '_')}@{random.choice(domains)}"
    else:
        # Real names based on language
        if language == "de":
            first_names = ["Max", "Sophie", "Leon", "Marie", "Felix", "Emma", "Paul", "Mia", "Ben", "Hannah",
                          "Luca", "Lea", "Noah", "Anna", "Tim", "Lina", "Jonas", "Clara", "Luis", "Zoe",
                          "Finn", "Maja", "Nico", "Lisa", "Jan", "Sarah", "Tom", "Julia", "Alex", "Nina"]
            last_initials = ["S.", "M.", "K.", "L.", "B.", "T.", "R.", "H.", "C.", "J.", "W.", "P.", "F.", "G."]
        else:  # English
            first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "Logan",
                          "Mia", "Lucas", "Charlotte", "Oliver", "Amelia", "Elijah", "Harper", "James", "Evelyn", "Benjamin",
                          "Emily", "Jacob", "Madison", "Michael", "Elizabeth", "Alexander", "Sofia", "William", "Victoria", "Daniel"]
            last_initials = ["S.", "M.", "K.", "L.", "B.", "T.", "R.", "H.", "C.", "J.", "W.", "P.", "D.", "A."]
        
        first_name = random.choice(first_names)
        last_initial = random.choice(last_initials)
        reviewer_name = f"{first_name} {last_initial}"
        
        # Generate email
        domains = ["gmail.com", "outlook.com", "icloud.com", "yahoo.com", "hotmail.com"]
        email = f"{first_name.lower()}.{last_initial[0].lower()}@{random.choice(domains)}"
    
    # Location based on language
    if language == "de":
        location = random.choice(['DE', 'AT', 'CH', 'DE', 'DE'])  # Weighted towards DE
    else:
        location = random.choice(['US', 'UK', 'CA', 'AU', 'US', 'US'])  # Weighted towards US
    
    return reviewer_name, email, location

def get_simplified_product_name(product_title, language="en"):
    """Extract a natural, shorter product name from the full title"""
    if not product_title:
        return "piece" if language == "en" else "Teil"
    
    # Short titles can be used completely
    if len(product_title) < 15:
        return product_title
    
    words = product_title.split()
    title_lower = product_title.lower()
    
    # Priority order: specific clothing terms first
    clothing_terms = {
        "en": ["belt", "chain", "necklace", "ring", "bracelet", "bag", "hat", "cap",
               "pants", "jeans", "leggings", "shorts", "skirt", "dress", "gown", "jumpsuit",
               "top", "shirt", "tee", "tank", "blouse", "crop", "bra", "corset", "bodysuit",
               "jacket", "coat", "hoodie", "cardigan", "sweater", "sweatshirt", "vest"],
        "de": ["gürtel", "kette", "halskette", "ring", "armband", "tasche", "hut", "mütze", 
               "hose", "jeans", "leggings", "shorts", "rock", "kleid", "jumpsuit",
               "top", "shirt", "t-shirt", "tanktop", "bluse", "croptop", "bh", "korsett", "bodysuit",
               "jacke", "mantel", "hoodie", "strickjacke", "pullover", "sweatshirt", "weste"]
    }
    
    terms = clothing_terms.get(language, clothing_terms["en"])
    
    # First check for exact word matches in priority order
    for term in terms:
        if f" {term}" in f" {title_lower}" or title_lower.startswith(term):
            # Return the actual word from the title, preserving case
            for word in words:
                if word.lower() == term:
                    return word
            return term  # fallback
    
    # Handle Opium brand products - be more specific
    if "opium" in title_lower:
        # Look for specific product types within Opium products
        opium_mappings = {
            "en": {
                "belt": "belt", "chain": "chain", "necklace": "necklace",
                "top": "top", "shirt": "shirt", "dress": "dress",
                "pants": "pants", "shorts": "shorts"
            },
            "de": {
                "belt": "gürtel", "gürtel": "gürtel", "chain": "kette", "kette": "kette",
                "top": "top", "shirt": "shirt", "dress": "kleid", "kleid": "kleid",
                "pants": "hose", "hose": "hose", "shorts": "shorts"
            }
        }
        
        mappings = opium_mappings.get(language, opium_mappings["en"])
        for key, value in mappings.items():
            if key in title_lower:
                return value
        
        # If no specific type found, use generic term
        return "piece" if language == "en" else "Teil"
    
    # Fallback: try to find any clothing term
    for word in words:
        if word.lower() in terms:
            return word
    
    # Final fallback
    if len(words) >= 2:
        return words[-1]
    
    return "piece" if language == "en" else "Teil"

def get_product_category(product_info):
    """Determine product category based on title"""
    title = product_info.get('title', '').lower()
    
    categories = []
    
    # Check for specific product types
    if any(word in title for word in ['top', 'shirt', 'blouse', 'tshirt', 't-shirt', 'tank', 'crop', 'tee']):
        categories.append('tops')
    if any(word in title for word in ['pants', 'jeans', 'leggings', 'shorts', 'skirt', 'trousers']):
        categories.append('bottoms')
    if any(word in title for word in ['dress', 'gown']):
        categories.append('dresses')
    if any(word in title for word in ['jacket', 'coat', 'hoodie', 'cardigan', 'sweater', 'sweatshirt']):
        categories.append('outerwear')
    if any(word in title for word in ['belt', 'bag', 'chain', 'necklace', 'ring', 'bracelet', 'hat', 'cap']):
        categories.append('accessories')
    
    # Check for style categories
    if any(word in title for word in ['gothic', 'goth', 'dark', 'black', 'mesh', 'lace', 'net', 'opium']):
        categories.append('gothic')
    if any(word in title for word in ['punk', 'rebel', 'studs', 'leather', 'tartan', 'plaid']):
        categories.append('punk')
    if any(word in title for word in ['vintage', 'retro', 'y2k', '90s', '80s']):
        categories.append('vintage')
    
    return categories if categories else ['tops']  # Default to tops

def generate_review_content(product, rating, language="en"):
    """Generate authentic Gen Z style review content"""
    categories = get_product_category(product)
    simplified_name = get_simplified_product_name(product.get('title', ''), language)
    
    # 15% chance for empty review
    if random.random() < 0.15:
        return ""
    
    # 35% chance for short one-liner
    if random.random() < 0.35:
        if language in SHORT_REVIEWS:
            return random.choice(SHORT_REVIEWS[language])
        else:
            return random.choice(SHORT_REVIEWS["en"])
    
    # Build review components
    review_components = []
    
    # Component 1: Intro (75% chance)
    if random.random() < 0.75:
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
        
        language_to_use = language if language in intros else "en"
        review_components.append(random.choice(intros[language_to_use][rating]))
    
    # Component 2: Product-specific phrases (70% chance, reduced from 85%)
    if random.random() < 0.70 and language in PRODUCT_PHRASES:
        phrases = []
        for category in categories:
            if category in PRODUCT_PHRASES[language]:
                phrases.extend(PRODUCT_PHRASES[language][category])
        
        if phrases:
            # Reduce phrase count for better flow
            phrase_count = random.choices([1, 2], weights=[70, 30], k=1)[0]
            selected_phrases = random.sample(phrases, min(phrase_count, len(phrases)))
            
            if selected_phrases:
                if len(review_components) > 0 and random.random() < 0.6:
                    # Better connectors for more natural flow
                    connectors = {
                        "de": [". ", "! ", ", "],
                        "en": [". ", "! ", ", "]
                    }
                    conn = random.choice(connectors.get(language, connectors["en"]))
                    review_components[-1] += conn
                    review_components.append(" ".join(selected_phrases))
                else:
                    review_components.append(" ".join(selected_phrases))
    
    # Component 3: Shop reference (20% chance, reduced)
    if random.random() < 0.20 and language in SHOP_REFERENCES:
        if len(review_components) > 0:
            # Always use sentence break for shop references
            review_components[-1] += ". " if not review_components[-1].endswith(('.', '!')) else " "
            review_components.append(random.choice(SHOP_REFERENCES[language]))
        else:
            review_components.append(random.choice(SHOP_REFERENCES[language]))
    
    # Component 4: Social media reference (15% chance, reduced)
    if random.random() < 0.15 and language in SOCIAL_MEDIA_REFS:
        if len(review_components) > 0:
            # Always use sentence break for social media references
            review_components[-1] += ". " if not review_components[-1].endswith(('.', '!')) else " "
            review_components.append(random.choice(SOCIAL_MEDIA_REFS[language]))
        else:
            review_components.append(random.choice(SOCIAL_MEDIA_REFS[language]))
    
    # Component 5: Shipping comment (10% chance, reduced)
    if random.random() < 0.10 and language in SHIPPING_COMMENTS:
        if len(review_components) > 0:
            # Use btw connector or sentence break
            connectors = [". ", "! ", " btw "]
            conn = random.choice(connectors)
            if conn in [".", "!"]:
                review_components[-1] += conn
                review_components.append(random.choice(SHIPPING_COMMENTS[language]))
            else:
                review_components[-1] += conn + random.choice(SHIPPING_COMMENTS[language])
        else:
            review_components.append(random.choice(SHIPPING_COMMENTS[language]))
    
    # Build review from components
    review = " ".join(review_components)
    
    # Youth writing style (15% chance - matching old_review.py)
    if random.random() < 0.15:
        # No capital "I" at start
        review = re.sub(r"^Ich ", "ich ", review)
        review = re.sub(r"^I ", "i ", review)
        
        # Lowercase start (30% chance)
        if random.random() < 0.3:
            review = review[0].lower() + review[1:] if len(review) > 1 else review.lower()
        
        # Multiple exclamation marks and emojis
        if review and review[-1] in [".", "!"]:
            num_excl = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10], k=1)[0]
            review = review[:-1] + "!" * num_excl
            
            # Emojis (50% chance)
            if random.random() < 0.5:
                emojis = ["💖", "✨", "🔥", "👌", "💯", "🙌", "😍", "🤩", "🥰", "💕", "❤️", "🖤", "👑", "🌟"]
                num_emojis = random.choices([1, 2, 3], weights=[50, 30, 20], k=1)[0]
                selected_emojis = random.sample(emojis, num_emojis)
                review += "".join(selected_emojis)
    
    return review

def generate_rating_distribution():
    """Generate realistic rating distribution"""
    # 60% 5-star, 30% 4-star, 10% 3-star
    return random.choices([5, 4, 3], weights=[60, 30, 10], k=1)[0]

def generate_review_date(max_months_back=36):
    """Generate random review date within last 36 months"""
    days_back = random.randint(1, max_months_back * 30)
    review_date = datetime.now() - timedelta(days=days_back)
    return review_date.strftime('%Y-%m-%d')

def select_language():
    """Select language based on desired distribution"""
    # 30% German, 70% English (simplified from old_review.py for current app)
    return random.choices(["de", "en"], weights=[30, 70], k=1)[0]

def generate_review(product, existing_reviews=0):
    """Generate a single review for a product"""
    language = select_language()
    rating = generate_rating_distribution()
    reviewer_name, reviewer_email, reviewer_location = generate_reviewer_info(language)
    
    # 5% chance for no title (typical for young reviewers)
    if random.random() < 0.05:
        review_title = ""
    else:
        if language in REVIEW_TITLES and rating in REVIEW_TITLES[language]:
            review_title = random.choice(REVIEW_TITLES[language][rating])
        else:
            review_title = random.choice(REVIEW_TITLES["en"][rating])
    
    review_content = generate_review_content(product, rating, language)
    
    # Add review ending (30% chance) for longer reviews
    if len(review_content) > 50 and random.random() < 0.3:
        if language in REVIEW_ENDINGS and rating in REVIEW_ENDINGS[language]:
            ending = random.choice(REVIEW_ENDINGS[language][rating])
            if review_content and review_content[-1] not in [".", "!"]:
                review_content += ". "
            elif review_content and review_content[-1] in [".", "!"]:
                review_content += " "
            review_content += ending
    
    review_date = generate_review_date()
    
    # 5% chance for unverified
    verified = 'Yes' if random.random() > 0.05 else 'No'
    
    return {
        'rating': rating,
        'title': review_title,
        'content': review_content,
        'author': reviewer_name,
        'email': reviewer_email,
        'location': reviewer_location,
        'date': review_date,
        'verified': verified
    }

def generate_reviews_for_product(product_info, num_reviews=5):
    """Generate multiple reviews for a product"""
    reviews = []
    for i in range(num_reviews):
        review = generate_review(product_info, existing_reviews=i)
        reviews.append(review)
    return reviews