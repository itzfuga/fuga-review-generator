"""
Advanced Review Generation Engine - Improved Version
Fixes repetition issues and ensures better language distribution
"""
import random
from datetime import datetime, timedelta
import re
import json
import os
from collections import defaultdict

# Persistent phrase tracking across sessions
PHRASE_TRACKING_FILE = "phrase_usage_tracking.json"

def load_phrase_tracking():
    """Load phrase usage tracking from file"""
    if os.path.exists(PHRASE_TRACKING_FILE):
        try:
            with open(PHRASE_TRACKING_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert lists back to sets
                return {lang: set(phrases) for lang, phrases in data.items()}
        except:
            pass
    return defaultdict(set)

def save_phrase_tracking(tracking):
    """Save phrase usage tracking to file"""
    # Convert sets to lists for JSON serialization
    data = {lang: list(phrases) for lang, phrases in tracking.items()}
    with open(PHRASE_TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Global phrase tracking with persistence
USED_PHRASES = load_phrase_tracking()

# Extended review components with more variety
REVIEW_COMPONENTS = {
    "opening_reactions": {
        "de": [
            "absolut verliebt in dieses", "total begeistert von diesem", "mega happy mit dem",
            "richtig zufrieden mit diesem", "komplett überzeugt von dem", "voll happy mit meinem neuen",
            "super zufrieden mit dem", "echt beeindruckt von diesem", "total in love mit dem",
            "richtig stolz auf diesen", "mega glücklich mit meinem", "voll überzeugt von diesem",
            "komplett zufrieden mit dem", "absolut happy mit diesem", "total verliebt in mein neues",
            "richtig begeistert von meinem", "mega zufrieden mit diesem", "voll beeindruckt von dem",
            "komplett happy mit meinem neuen", "absolut überzeugt von diesem"
        ],
        "en": [
            "absolutely in love with this", "totally obsessed with my new", "super happy with this",
            "really satisfied with my", "completely convinced by this", "so pleased with my new",
            "extremely happy with this", "genuinely impressed by this", "totally in love with my",
            "really proud of this", "incredibly happy with my", "fully convinced by this",
            "completely satisfied with my", "absolutely thrilled with this", "totally smitten with my new",
            "really excited about my", "super satisfied with this", "genuinely impressed with my",
            "completely happy with my new", "absolutely convinced by this"
        ],
        "es": [
            "absolutamente enamorada de este", "totalmente obsesionada con mi nuevo", "súper feliz con este",
            "realmente satisfecha con mi", "completamente convencida por este", "muy contenta con mi nuevo",
            "extremadamente feliz con este", "genuinamente impresionada por este", "totalmente enamorada de mi",
            "realmente orgullosa de este", "increíblemente feliz con mi", "totalmente convencida por este"
        ],
        "fr": [
            "absolument amoureuse de ce", "totalement obsédée par mon nouveau", "super heureuse avec ce",
            "vraiment satisfaite de mon", "complètement convaincue par ce", "très contente de mon nouveau",
            "extrêmement heureuse avec ce", "vraiment impressionnée par ce", "totalement amoureuse de mon",
            "vraiment fière de ce", "incroyablement heureuse avec mon", "entièrement convaincue par ce"
        ],
        "it": [
            "assolutamente innamorata di questo", "totalmente ossessionata dal mio nuovo", "super felice con questo",
            "davvero soddisfatta del mio", "completamente convinta da questo", "molto contenta del mio nuovo",
            "estremamente felice con questo", "davvero colpita da questo", "totalmente innamorata del mio",
            "davvero orgogliosa di questo", "incredibilmente felice con il mio", "pienamente convinta da questo"
        ]
    },
    "quality_comments": {
        "de": [
            "qualität ist der wahnsinn", "verarbeitung ist top notch", "material fühlt sich premium an",
            "haptik ist unglaublich gut", "stoff ist super hochwertig", "nähte sind perfekt verarbeitet",
            "details sind liebevoll gemacht", "material ist robust aber weich", "fühlt sich teurer an als es war",
            "qualität übertrifft den preis", "verarbeitung ist on point", "material ist first class",
            "haptik ist einfach premium", "stoff fühlt sich luxuriös an", "nähte halten bombenfest",
            "details machen den unterschied", "material ist langlebig", "fühlt sich wertig an",
            "qualität ist überraschend gut", "verarbeitung lässt nichts zu wünschen übrig"
        ],
        "en": [
            "quality is insane", "construction is top notch", "material feels premium",
            "texture is incredibly good", "fabric is super high quality", "seams are perfectly done",
            "details are thoughtfully made", "material is sturdy yet soft", "feels more expensive than it was",
            "quality exceeds the price", "construction is on point", "material is first class",
            "texture is just premium", "fabric feels luxurious", "seams hold up perfectly",
            "details make the difference", "material is durable", "feels high-end",
            "quality is surprisingly good", "construction leaves nothing to be desired"
        ],
        "es": [
            "la calidad es increíble", "la construcción es de primera", "el material se siente premium",
            "la textura es increíblemente buena", "la tela es súper alta calidad", "las costuras están perfectamente hechas",
            "los detalles están cuidadosamente hechos", "el material es resistente pero suave", "se siente más caro de lo que fue",
            "la calidad supera el precio", "la construcción está en su punto", "el material es de primera clase"
        ],
        "fr": [
            "la qualité est incroyable", "la construction est top", "le matériau est premium",
            "la texture est incroyablement bonne", "le tissu est de super haute qualité", "les coutures sont parfaitement faites",
            "les détails sont soigneusement réalisés", "le matériau est solide mais doux", "ça semble plus cher que c'était",
            "la qualité dépasse le prix", "la construction est parfaite", "le matériau est de première classe"
        ],
        "it": [
            "la qualità è pazzesca", "la costruzione è di prima classe", "il materiale sembra premium",
            "la texture è incredibilmente buona", "il tessuto è di altissima qualità", "le cuciture sono perfettamente fatte",
            "i dettagli sono fatti con cura", "il materiale è robusto ma morbido", "sembra più costoso di quanto fosse",
            "la qualità supera il prezzo", "la costruzione è perfetta", "il materiale è di prima classe"
        ]
    },
    "fit_comments": {
        "de": [
            "passt wie angegossen", "größe stimmt perfekt", "schnitt ist mega schmeichelhaft",
            "sitzt an allen richtigen stellen", "fällt true to size aus", "passform ist ein traum",
            "größentabelle war spot on", "schnitt betont die figur perfekt", "sitzt wie maßgeschneidert",
            "passform übertrifft erwartungen", "größe passt wie erwartet", "schnitt ist durchdacht",
            "sitzt bequem aber nicht zu locker", "passform ist genau richtig", "größe war perfekte wahl",
            "schnitt ist super flattering", "sitzt wie eine zweite haut", "passform könnte nicht besser sein"
        ],
        "en": [
            "fits like a glove", "size is perfect", "cut is super flattering",
            "sits in all the right places", "runs true to size", "fit is a dream",
            "size chart was spot on", "cut accentuates perfectly", "fits like it's tailored",
            "fit exceeds expectations", "size fits as expected", "cut is well thought out",
            "sits comfortably but not loose", "fit is just right", "size was perfect choice",
            "cut is super flattering", "fits like a second skin", "fit couldn't be better"
        ],
        "es": [
            "queda como un guante", "la talla es perfecta", "el corte es súper favorecedor",
            "se ajusta en todos los lugares correctos", "la talla es fiel", "el ajuste es un sueño",
            "la tabla de tallas fue exacta", "el corte acentúa perfectamente", "queda como a medida",
            "el ajuste supera las expectativas", "la talla queda como se esperaba", "el corte está bien pensado"
        ],
        "fr": [
            "va comme un gant", "la taille est parfaite", "la coupe est super flatteuse",
            "s'ajuste à tous les bons endroits", "taille normalement", "l'ajustement est un rêve",
            "le guide des tailles était exact", "la coupe accentue parfaitement", "va comme sur mesure",
            "l'ajustement dépasse les attentes", "la taille va comme prévu", "la coupe est bien pensée"
        ],
        "it": [
            "calza come un guanto", "la taglia è perfetta", "il taglio è super lusinghiero",
            "si adatta in tutti i punti giusti", "veste fedele alla taglia", "la vestibilità è un sogno",
            "la tabella taglie era precisa", "il taglio accentua perfettamente", "veste come su misura",
            "la vestibilità supera le aspettative", "la taglia veste come previsto", "il taglio è ben pensato"
        ]
    },
    "style_comments": {
        "de": [
            "style ist genau mein ding", "design ist einzigartig", "look ist edgy aber tragbar",
            "ästhetik trifft meinen geschmack", "style ist zeitlos modern", "design hebt sich ab",
            "look ist sophisticated", "ästhetik ist on point", "style macht statement",
            "design ist durchdacht", "look ist vielseitig", "ästhetik ist genau richtig",
            "style ist perfekt ausbalanciert", "design ist eye-catching", "look ist mühellos cool"
        ],
        "en": [
            "style is exactly my thing", "design is unique", "look is edgy but wearable",
            "aesthetic hits my taste", "style is timelessly modern", "design stands out",
            "look is sophisticated", "aesthetic is on point", "style makes a statement",
            "design is well thought out", "look is versatile", "aesthetic is just right",
            "style is perfectly balanced", "design is eye-catching", "look is effortlessly cool"
        ],
        "es": [
            "el estilo es exactamente lo mío", "el diseño es único", "el look es atrevido pero ponible",
            "la estética coincide con mi gusto", "el estilo es atemporal y moderno", "el diseño destaca",
            "el look es sofisticado", "la estética está en su punto", "el estilo hace una declaración"
        ],
        "fr": [
            "le style est exactement mon truc", "le design est unique", "le look est edgy mais portable",
            "l'esthétique correspond à mon goût", "le style est intemporel et moderne", "le design se démarque",
            "le look est sophistiqué", "l'esthétique est parfaite", "le style fait une déclaration"
        ],
        "it": [
            "lo stile è esattamente il mio genere", "il design è unico", "il look è edgy ma indossabile",
            "l'estetica colpisce il mio gusto", "lo stile è senza tempo e moderno", "il design si distingue",
            "il look è sofisticato", "l'estetica è perfetta", "lo stile fa una dichiarazione"
        ]
    },
    "usage_scenarios": {
        "de": [
            "perfekt für festivals", "ideal für clubbing", "great für alltag", "super für dates",
            "genial für konzerte", "klasse für parties", "toll für photoshoots", "spitze für events",
            "optimal für ausgehen", "bestens für feiern", "wunderbar für treffen", "exzellent für auftritte"
        ],
        "en": [
            "perfect for festivals", "ideal for clubbing", "great for everyday", "super for dates",
            "awesome for concerts", "brilliant for parties", "amazing for photoshoots", "excellent for events",
            "optimal for going out", "best for celebrations", "wonderful for meetups", "excellent for performances"
        ],
        "es": [
            "perfecto para festivales", "ideal para ir de clubes", "genial para el día a día", "súper para citas",
            "increíble para conciertos", "brillante para fiestas", "asombroso para sesiones de fotos", "excelente para eventos"
        ],
        "fr": [
            "parfait pour les festivals", "idéal pour le clubbing", "génial pour tous les jours", "super pour les rendez-vous",
            "génial pour les concerts", "brillant pour les fêtes", "incroyable pour les séances photo", "excellent pour les événements"
        ],
        "it": [
            "perfetto per i festival", "ideale per il clubbing", "ottimo per tutti i giorni", "super per gli appuntamenti",
            "fantastico per i concerti", "brillante per le feste", "incredibile per i servizi fotografici", "eccellente per gli eventi"
        ]
    },
    "personal_reactions": {
        "de": [
            "bin komplett verliebt", "könnte nicht glücklicher sein", "übertrifft alle erwartungen",
            "genau was ich gesucht hab", "besser als erwartet", "macht mich so happy",
            "erfüllt alle wünsche", "bin total begeistert", "hätte nicht gedacht dass es so gut ist",
            "bin positiv überrascht", "macht richtig spaß zu tragen", "fühle mich super darin"
        ],
        "en": [
            "i'm completely in love", "couldn't be happier", "exceeds all expectations",
            "exactly what i was looking for", "better than expected", "makes me so happy",
            "fulfills all wishes", "i'm totally thrilled", "didn't think it would be this good",
            "i'm positively surprised", "really fun to wear", "feel amazing in it"
        ],
        "es": [
            "estoy completamente enamorada", "no podría estar más feliz", "supera todas las expectativas",
            "exactamente lo que buscaba", "mejor de lo esperado", "me hace tan feliz",
            "cumple todos los deseos", "estoy totalmente emocionada", "no pensé que sería tan bueno"
        ],
        "fr": [
            "je suis complètement amoureuse", "je ne pourrais pas être plus heureuse", "dépasse toutes les attentes",
            "exactement ce que je cherchais", "mieux que prévu", "me rend si heureuse",
            "remplit tous les souhaits", "je suis totalement ravie", "je ne pensais pas que ce serait si bien"
        ],
        "it": [
            "sono completamente innamorata", "non potrei essere più felice", "supera tutte le aspettative",
            "esattamente quello che cercavo", "meglio del previsto", "mi rende così felice",
            "soddisfa tutti i desideri", "sono totalmente entusiasta", "non pensavo sarebbe stato così buono"
        ]
    }
}

# Extended short reviews with more variety
EXTENDED_SHORT_REVIEWS = {
    "de": [
        # Existing ones plus many new variations
        "krass gut!!!", "omg, neues lieblingsstück💖", "hab sofort zugeschlagen!!!", "vibes sind immaculate✨",
        "absolut fire 🔥", "brauche das in allen farben", "danke fuga für dieses meisterwerk", "mein neuer daily driver",
        "slay queen energy", "hauptsache fuga", "nimm mein geld", "10000/10 würde wieder kaufen",
        "blessed mit diesem teil", "manifestiert und bekommen", "universe said yes", "main character vibes",
        "living my best life", "no thoughts just vibes", "obsession level 1000", "brb ordering more",
        "wallet crying but worth it", "dopamine hit secured", "serotonin boost incoming", "peak fashion achieved",
        "style game elevated", "confidence level up", "compliment magnet activated", "outfit main event",
        "closet highlight reel", "fashion week ready", "street style approved", "influence worthy",
        "grid post material", "story worthy fit", "reel ready look", "tiktok famous incoming",
        "algorithm blessed", "fyp energy", "explore page vibes", "content creator approved",
        "photo dump essential", "feed curated", "aesthetic achieved", "vision board realized"
    ],
    "en": [
        # Existing ones plus many new variations
        "obsessed!!!!", "new fav piece no cap", "copped instantly🔥", "the vibes are immaculate✨",
        "absolutely fire 🔥", "need this in every color", "thank you fuga for this masterpiece", "my new daily driver",
        "slay queen energy", "fuga supremacy", "take my money", "10000/10 would buy again",
        "blessed with this piece", "manifested and received", "universe said yes", "main character vibes",
        "living my best life", "no thoughts just vibes", "obsession level 1000", "brb ordering more",
        "wallet crying but worth it", "dopamine hit secured", "serotonin boost incoming", "peak fashion achieved",
        "style game elevated", "confidence level up", "compliment magnet activated", "outfit main event",
        "closet highlight reel", "fashion week ready", "street style approved", "influence worthy",
        "grid post material", "story worthy fit", "reel ready look", "tiktok famous incoming",
        "algorithm blessed", "fyp energy", "explore page vibes", "content creator approved",
        "photo dump essential", "feed curated", "aesthetic achieved", "vision board realized",
        "closet staple secured", "wardrobe game changer", "style evolution complete", "fashion nirvana reached",
        "drip check passed", "fit check certified", "vibe check approved", "energy matched",
        "frequency aligned", "manifestation complete", "abundance flowing", "gratitude overflowing"
    ],
    "es": [
        "¡obsesionada!", "nueva pieza favorita", "comprado al instante🔥", "las vibras son inmaculadas✨",
        "absolutamente fuego 🔥", "necesito esto en todos los colores", "gracias fuga por esta obra maestra",
        "energía de reina", "supremacía fuga", "toma mi dinero", "10000/10 compraría de nuevo",
        "bendecida con esta pieza", "manifestado y recibido", "el universo dijo sí", "vibras de protagonista"
    ],
    "fr": [
        "obsédée!!!!", "nouvelle pièce préférée", "acheté instantanément🔥", "les vibes sont immaculées✨",
        "absolument feu 🔥", "j'ai besoin de ça dans toutes les couleurs", "merci fuga pour ce chef-d'œuvre",
        "énergie de reine", "suprématie fuga", "prends mon argent", "10000/10 j'achèterais encore",
        "bénie avec cette pièce", "manifesté et reçu", "l'univers a dit oui", "vibes de personnage principal"
    ],
    "it": [
        "ossessionata!!!!", "nuovo pezzo preferito", "comprato istantaneamente🔥", "le vibrazioni sono immacolate✨",
        "assolutamente fuoco 🔥", "ne ho bisogno in ogni colore", "grazie fuga per questo capolavoro",
        "energia da regina", "supremazia fuga", "prendi i miei soldi", "10000/10 comprerei di nuovo",
        "benedetta con questo pezzo", "manifestato e ricevuto", "l'universo ha detto sì", "vibrazioni da protagonista"
    ]
}

# Review titles with more variety
REVIEW_TITLES = {
    "de": {
        5: [
            "Absolut fantastisch!", "Perfektes Produkt!", "Begeistert!", "Übertrifft alle Erwartungen!",
            "Einfach traumhaft!", "Ein Muss für jeden!", "Kann ich nur empfehlen!", "Bestes Produkt ever!",
            "Erstklassige Qualität!", "Liebe es!", "Top Produkt!", "Hervorragende Wahl!", "Mega Teil!",
            "Voll cool!", "Krass gut!", "Einfach nur wow!", "Beste Entscheidung ever!", "Absolut genial!",
            "Traumhaft schön!", "Überragend!", "Spitzenklasse!", "Unglaublich gut!", "Hammer!",
            "Bombastisch!", "Phänomenal!", "Außergewöhnlich!", "Grandios!", "Spektakulär!"
        ],
        4: [
            "Sehr gutes Produkt", "Fast perfekt", "Wirklich schön", "Bin sehr zufrieden", "Gute Qualität",
            "Macht einen tollen Eindruck", "Empfehlenswert", "Positiv überrascht", "Toller Kauf",
            "Gutes Preis-Leistungs-Verhältnis", "Schönes Design", "Überzeugt mich", "Richtig nice",
            "Voll gut", "Echt cool", "Gefällt mir sehr", "Ziemlich gut", "Echt gelungen", "Super Sache",
            "Richtig schön", "Sehr zufriedenstellend", "Klasse Teil", "Echt empfehlenswert"
        ],
        3: [
            "Ganz okay", "Erfüllt seinen Zweck", "Im Großen und Ganzen zufrieden", "Mittelmäßig",
            "Entspricht den Erwartungen", "Nicht schlecht", "Könnte besser sein", "Durchschnittlich",
            "Für den Preis in Ordnung", "Brauchbar", "Mittelklasse", "Okay für den Alltag", "Ganz nett",
            "Passt schon", "Akzeptabel", "Befriedigend", "Standard", "Normal"
        ]
    },
    "en": {
        5: [
            "Absolutely amazing!", "Perfect product!", "Love it so much!", "Exceeds all expectations!",
            "Simply wonderful!", "A must-have!", "Highly recommend!", "Best product ever!",
            "First-class quality!", "Love it!", "Top product!", "Excellent choice!", "Obsessed with this!",
            "Literally perfect!", "Totally in love!", "So freaking good!", "Mind-blowing!", "Incredible!",
            "Outstanding!", "Phenomenal!", "Exceptional!", "Magnificent!", "Spectacular!", "Game changer!",
            "Life changing!", "Beyond amazing!", "Absolutely stellar!", "Pure perfection!"
        ],
        4: [
            "Very good product", "Almost perfect", "Really nice", "Very satisfied", "Good quality",
            "Makes a great impression", "Recommendable", "Positively surprised", "Great purchase",
            "Good value for money", "Beautiful design", "Convincing", "Really cool", "Pretty nice",
            "Very pleased with it", "Quite good", "Really well done", "Great item", "Pretty awesome",
            "Very satisfying", "Great piece", "Definitely recommend", "Solid choice"
        ],
        3: [
            "Decent", "Serves its purpose", "Satisfied overall", "Average", "Meets expectations",
            "Not bad", "Could be better", "Average", "Okay for the price", "Usable", "Middle-range",
            "Okay for everyday", "Pretty decent", "It's fine", "Acceptable", "Satisfactory", "Standard",
            "Regular", "Fair enough", "Reasonable"
        ]
    },
    "es": {
        5: [
            "¡Absolutamente increíble!", "¡Producto perfecto!", "¡Me encanta!", "¡Supera todas las expectativas!",
            "¡Simplemente maravilloso!", "¡Imprescindible!", "¡Lo recomiendo mucho!", "¡El mejor producto!",
            "¡Calidad de primera!", "¡Lo amo!", "¡Producto top!", "¡Excelente elección!", "¡Obsesionada con esto!",
            "¡Literalmente perfecto!", "¡Totalmente enamorada!", "¡Increíblemente bueno!", "¡Espectacular!",
            "¡Fenomenal!", "¡Excepcional!", "¡Magnífico!", "¡Extraordinario!"
        ],
        4: [
            "Muy buen producto", "Casi perfecto", "Realmente bonito", "Muy satisfecha", "Buena calidad",
            "Causa una gran impresión", "Recomendable", "Positivamente sorprendida", "Gran compra",
            "Buena relación calidad-precio", "Diseño hermoso", "Me convence", "Realmente genial",
            "Bastante bueno", "Muy contenta con esto", "Bastante bueno", "Realmente bien hecho"
        ],
        3: [
            "Decente", "Cumple su propósito", "Satisfecha en general", "Promedio", "Cumple las expectativas",
            "No está mal", "Podría ser mejor", "Promedio", "Bien por el precio", "Utilizable",
            "Gama media", "Bien para el día a día", "Bastante decente", "Está bien"
        ]
    },
    "fr": {
        5: [
            "Absolument incroyable!", "Produit parfait!", "Je l'adore!", "Dépasse toutes les attentes!",
            "Tout simplement merveilleux!", "Un incontournable!", "Je le recommande vivement!",
            "Le meilleur produit!", "Qualité de première classe!", "Je l'aime!", "Produit top!",
            "Excellent choix!", "Obsédée par ça!", "Littéralement parfait!", "Totalement amoureuse!",
            "Vraiment génial!", "Spectaculaire!", "Phénoménal!", "Exceptionnel!", "Magnifique!"
        ],
        4: [
            "Très bon produit", "Presque parfait", "Vraiment beau", "Très satisfaite", "Bonne qualité",
            "Fait une grande impression", "Recommandable", "Positivement surprise", "Excellent achat",
            "Bon rapport qualité-prix", "Beau design", "Me convainc", "Vraiment cool", "Assez bien",
            "Très contente", "Assez bon", "Vraiment bien fait"
        ],
        3: [
            "Correct", "Remplit son rôle", "Satisfaite dans l'ensemble", "Moyen", "Répond aux attentes",
            "Pas mal", "Pourrait être mieux", "Moyen", "Correct pour le prix", "Utilisable",
            "Milieu de gamme", "Correct pour tous les jours", "Assez correct", "Ça va"
        ]
    },
    "it": {
        5: [
            "Assolutamente incredibile!", "Prodotto perfetto!", "Lo adoro!", "Supera tutte le aspettative!",
            "Semplicemente meraviglioso!", "Un must-have!", "Lo raccomando vivamente!", "Il miglior prodotto!",
            "Qualità di prima classe!", "Lo amo!", "Prodotto top!", "Scelta eccellente!",
            "Ossessionata da questo!", "Letteralmente perfetto!", "Totalmente innamorata!",
            "Davvero fantastico!", "Spettacolare!", "Fenomenale!", "Eccezionale!", "Magnifico!"
        ],
        4: [
            "Prodotto molto buono", "Quasi perfetto", "Davvero bello", "Molto soddisfatta", "Buona qualità",
            "Fa una grande impressione", "Raccomandabile", "Positivamente sorpresa", "Ottimo acquisto",
            "Buon rapporto qualità-prezzo", "Design bellissimo", "Mi convince", "Davvero cool",
            "Abbastanza buono", "Molto contenta", "Abbastanza buono", "Davvero ben fatto"
        ],
        3: [
            "Decente", "Serve al suo scopo", "Soddisfatta nel complesso", "Nella media",
            "Soddisfa le aspettative", "Non male", "Potrebbe essere meglio", "Nella media",
            "Va bene per il prezzo", "Utilizzabile", "Fascia media", "Va bene per tutti i giorni",
            "Abbastanza decente", "Va bene"
        ]
    }
}

# Additional languages with basic phrases
ADDITIONAL_LANGUAGES = {
    "ru": {
        "greetings": ["привет", "здравствуйте", "добрый день"],
        "quality": ["качество отличное", "хорошее качество", "качество супер"],
        "satisfaction": ["очень довольна", "полностью удовлетворена", "счастлива с покупкой"],
        "recommendation": ["рекомендую", "советую всем", "стоит купить"]
    },
    "pl": {
        "greetings": ["cześć", "dzień dobry", "witam"],
        "quality": ["jakość świetna", "dobra jakość", "jakość super"],
        "satisfaction": ["bardzo zadowolona", "w pełni usatysfakcjonowana", "szczęśliwa z zakupu"],
        "recommendation": ["polecam", "polecam wszystkim", "warto kupić"]
    },
    "nl": {
        "greetings": ["hallo", "goedendag", "hoi"],
        "quality": ["kwaliteit uitstekend", "goede kwaliteit", "kwaliteit super"],
        "satisfaction": ["zeer tevreden", "volledig tevreden", "blij met aankoop"],
        "recommendation": ["aanbevelen", "raad iedereen aan", "de moeite waard"]
    },
    "sv": {
        "greetings": ["hej", "god dag", "hallå"],
        "quality": ["kvalitet utmärkt", "bra kvalitet", "kvalitet super"],
        "satisfaction": ["mycket nöjd", "helt nöjd", "glad med köp"],
        "recommendation": ["rekommenderar", "rekommenderar alla", "värt att köpa"]
    },
    "ja": {
        "greetings": ["こんにちは", "はじめまして"],
        "quality": ["品質最高", "良い品質", "クオリティ高い"],
        "satisfaction": ["とても満足", "完全に満足", "購入して良かった"],
        "recommendation": ["おすすめ", "みんなにおすすめ", "買う価値あり"]
    },
    "ko": {
        "greetings": ["안녕하세요", "안녕"],
        "quality": ["품질 최고", "좋은 품질", "퀄리티 굿"],
        "satisfaction": ["매우 만족", "완전 만족", "구매 만족"],
        "recommendation": ["추천", "모두에게 추천", "살 만한 가치"]
    },
    "zh": {
        "greetings": ["你好", "您好"],
        "quality": ["质量很好", "品质优秀", "质量超赞"],
        "satisfaction": ["非常满意", "完全满意", "购买满意"],
        "recommendation": ["推荐", "推荐给大家", "值得购买"]
    }
}

def generate_youthful_username():
    """Generate trendy, youth-oriented usernames with more variety"""
    prefixes = ["xX", "x", "lil", "big", "the", "its", "im", "ur", "ya", ""]
    
    themes = [
        # Dark/Gothic
        "dark", "goth", "emo", "shadow", "night", "moon", "vampire", "witch", "mystic", "chaos",
        "void", "abyss", "demon", "devil", "hell", "doom", "grim", "death", "soul", "spirit",
        # Fashion/Style
        "style", "fashion", "aesthetic", "vibe", "mood", "slay", "serve", "drip", "fit", "look",
        # Internet culture
        "cyber", "digital", "glitch", "pixel", "neon", "vapor", "wave", "core", "punk", "grunge",
        # Cute/Soft
        "baby", "angel", "fairy", "bunny", "kitty", "honey", "sugar", "cherry", "peach", "berry",
        # Cool/Edgy
        "rebel", "riot", "rage", "toxic", "psycho", "crazy", "wild", "savage", "beast", "monster",
        # Celestial
        "star", "galaxy", "cosmos", "astro", "lunar", "solar", "venus", "mars", "pluto", "nebula",
        # Music
        "rave", "techno", "bass", "beat", "rhythm", "melody", "harmony", "disco", "trap", "house"
    ]
    
    suffixes = ["Xx", "x", "xo", "666", "420", "69", "13", "777", "999", "2000", ""]
    
    # Add birth years
    current_year = datetime.now().year
    for year in range(current_year - 24, current_year - 18):
        suffixes.append(str(year % 100))
    
    # Generate username
    if random.random() < 0.3:  # 30% chance for complex username
        return f"{random.choice(prefixes)}{random.choice(themes)}_{random.choice(themes)}{random.choice(suffixes)}"
    else:
        return f"{random.choice(themes)}{random.choice(suffixes)}"

def generate_reviewer_info(language="en"):
    """Generate realistic reviewer information with better name variety"""
    # 70% chance for username vs real name (increased from 60%)
    if random.random() < 0.7:
        reviewer_name = generate_youthful_username()
        
        # Email domains by region
        email_domains = {
            "de": ["gmail.com", "web.de", "gmx.de", "gmx.net", "outlook.com", "yahoo.de", "icloud.com"],
            "en": ["gmail.com", "outlook.com", "icloud.com", "yahoo.com", "hotmail.com", "protonmail.com"],
            "es": ["gmail.com", "hotmail.com", "yahoo.es", "outlook.es", "icloud.com"],
            "fr": ["gmail.com", "orange.fr", "free.fr", "yahoo.fr", "outlook.fr", "laposte.net"],
            "it": ["gmail.com", "libero.it", "alice.it", "yahoo.it", "outlook.it", "virgilio.it"],
            "ru": ["gmail.com", "yandex.ru", "mail.ru", "rambler.ru", "outlook.com"],
            "pl": ["gmail.com", "wp.pl", "onet.pl", "interia.pl", "o2.pl", "outlook.com"],
            "ja": ["gmail.com", "yahoo.co.jp", "docomo.ne.jp", "ezweb.ne.jp", "outlook.jp"],
            "ko": ["gmail.com", "naver.com", "daum.net", "hanmail.net", "kakao.com"],
            "zh": ["gmail.com", "qq.com", "163.com", "126.com", "sina.com", "outlook.com"]
        }
        
        domains = email_domains.get(language, email_domains["en"])
        email = f"{reviewer_name.lower().replace(' ', '').replace('_', '.')}@{random.choice(domains)}"
    else:
        # Real names with much more variety
        name_database = {
            "de": {
                "first": ["Max", "Leon", "Felix", "Paul", "Ben", "Luca", "Noah", "Tim", "Jonas", "Luis",
                         "Finn", "Nico", "Jan", "Tom", "Alex", "Moritz", "David", "Simon", "Erik", "Marvin",
                         "Sophie", "Marie", "Emma", "Mia", "Hannah", "Lea", "Anna", "Lina", "Clara", "Zoe",
                         "Maja", "Lisa", "Sarah", "Julia", "Nina", "Laura", "Alina", "Amelie", "Emilia", "Mila"],
                "last": ["S.", "M.", "K.", "L.", "B.", "T.", "R.", "H.", "C.", "J.", "W.", "P.", "F.", "G.",
                        "N.", "D.", "V.", "Z.", "E.", "A.", "O.", "U.", "I.", "Q."]
            },
            "en": {
                "first": ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "Logan",
                         "Mia", "Lucas", "Charlotte", "Oliver", "Amelia", "Elijah", "Harper", "James", "Evelyn", "Benjamin",
                         "Emily", "Jacob", "Madison", "Michael", "Elizabeth", "Alexander", "Sofia", "William", "Victoria", "Daniel",
                         "Aiden", "Jackson", "Abigail", "Sebastian", "Aria", "Jack", "Scarlett", "Carter", "Grace", "Wyatt"],
                "last": ["S.", "M.", "K.", "L.", "B.", "T.", "R.", "H.", "C.", "J.", "W.", "P.", "D.", "A.",
                        "N.", "G.", "V.", "Z.", "E.", "F.", "O.", "U.", "I.", "Q."]
            },
            "es": {
                "first": ["Sofía", "Mateo", "Valentina", "Santiago", "Isabella", "Sebastián", "Camila", "Diego", "Lucía", "Nicolás",
                         "María", "Alejandro", "Martina", "Daniel", "Daniela", "Gabriel", "Victoria", "Samuel", "Natalia", "David"],
                "last": ["G.", "R.", "M.", "F.", "L.", "S.", "P.", "D.", "C.", "V.", "H.", "J.", "B.", "N."]
            },
            "fr": {
                "first": ["Emma", "Lucas", "Chloé", "Hugo", "Léa", "Louis", "Manon", "Nathan", "Camille", "Enzo",
                         "Sarah", "Mathis", "Inès", "Tom", "Jade", "Théo", "Louise", "Raphaël", "Zoé", "Arthur"],
                "last": ["M.", "B.", "D.", "L.", "R.", "P.", "C.", "F.", "G.", "H.", "V.", "J.", "S.", "T."]
            },
            "it": {
                "first": ["Giulia", "Francesco", "Sofia", "Alessandro", "Aurora", "Lorenzo", "Ginevra", "Matteo", "Alice", "Leonardo",
                         "Emma", "Gabriele", "Giorgia", "Riccardo", "Martina", "Tommaso", "Chiara", "Edoardo", "Anna", "Marco"],
                "last": ["R.", "B.", "C.", "F.", "G.", "M.", "P.", "S.", "V.", "D.", "L.", "T.", "N.", "A."]
            }
        }
        
        if language in name_database:
            names = name_database[language]
        else:
            names = name_database["en"]
        
        first_name = random.choice(names["first"])
        last_initial = random.choice(names["last"])
        reviewer_name = f"{first_name} {last_initial}"
        
        # Generate email
        domains = ["gmail.com", "outlook.com", "icloud.com", "yahoo.com", "hotmail.com"]
        email = f"{first_name.lower()}.{last_initial[0].lower()}{random.randint(1, 999)}@{random.choice(domains)}"
    
    # Location based on language with more variety
    locations = {
        "de": ["DE", "DE", "DE", "AT", "CH"],  # Germany weighted
        "en": ["US", "US", "UK", "CA", "AU", "NZ", "IE"],  # US weighted
        "es": ["ES", "ES", "MX", "AR", "CO", "CL"],  # Spain weighted
        "fr": ["FR", "FR", "BE", "CA", "CH"],  # France weighted
        "it": ["IT", "IT", "CH", "SM"],  # Italy weighted
        "ru": ["RU", "RU", "BY", "KZ"],
        "pl": ["PL", "PL", "PL"],
        "nl": ["NL", "NL", "BE"],
        "sv": ["SE", "SE", "FI"],
        "ja": ["JP", "JP"],
        "ko": ["KR", "KR"],
        "zh": ["CN", "TW", "HK", "SG"]
    }
    
    location = random.choice(locations.get(language, ["US", "UK", "CA", "AU"]))
    
    return reviewer_name, email, location

def get_simplified_product_name(product_title, language="en"):
    """Extract a natural, shorter product name from the full title with better variety"""
    if not product_title:
        # More variety in fallback terms
        fallbacks = {
            "en": ["piece", "item", "product", "article"],
            "de": ["Teil", "Stück", "Artikel", "Produkt"],
            "es": ["pieza", "artículo", "producto"],
            "fr": ["pièce", "article", "produit"],
            "it": ["pezzo", "articolo", "prodotto"]
        }
        return random.choice(fallbacks.get(language, fallbacks["en"]))
    
    # Extended clothing terms
    clothing_terms = {
        "en": [
            "belt", "chain", "necklace", "ring", "bracelet", "bag", "hat", "cap", "beanie", "bandana",
            "pants", "jeans", "leggings", "shorts", "skirt", "dress", "gown", "jumpsuit", "romper",
            "top", "shirt", "tee", "tank", "blouse", "crop", "bra", "corset", "bodysuit", "cami",
            "jacket", "coat", "hoodie", "cardigan", "sweater", "sweatshirt", "vest", "blazer", "bomber",
            "boots", "shoes", "sneakers", "heels", "sandals", "flats", "platforms", "docs",
            "socks", "tights", "stockings", "gloves", "scarf", "mask", "choker", "harness"
        ],
        "de": [
            "gürtel", "kette", "halskette", "ring", "armband", "tasche", "hut", "mütze", "cap",
            "hose", "jeans", "leggings", "shorts", "rock", "kleid", "jumpsuit", "overall",
            "top", "shirt", "t-shirt", "tanktop", "bluse", "croptop", "bh", "korsett", "bodysuit",
            "jacke", "mantel", "hoodie", "strickjacke", "pullover", "sweatshirt", "weste",
            "stiefel", "schuhe", "sneaker", "heels", "sandalen", "ballerinas", "plateaus"
        ]
    }
    
    words = product_title.split()
    title_lower = product_title.lower()
    
    # Try to find clothing terms
    terms = clothing_terms.get(language, clothing_terms["en"])
    
    for term in terms:
        if term in title_lower:
            # Return the actual word from title, preserving case
            for word in words:
                if word.lower() == term:
                    return word
            return term
    
    # Handle specific brands or styles
    if "opium" in title_lower:
        style_terms = {
            "en": ["piece", "style", "design", "item"],
            "de": ["Teil", "Style", "Design", "Stück"]
        }
        return random.choice(style_terms.get(language, style_terms["en"]))
    
    # Try to find any reasonable noun
    if len(words) >= 2:
        # Skip common adjectives and brand names
        skip_words = ["black", "white", "dark", "gothic", "punk", "vintage", "new", "best", "top", "premium"]
        for word in reversed(words):  # Start from end
            if word.lower() not in skip_words and len(word) > 3:
                return word
    
    # Final fallback
    return words[-1] if words else "item"

def get_product_category(product_info):
    """Determine product category with better detection"""
    title = product_info.get('title', '').lower()
    
    categories = []
    
    # Expanded category detection
    category_keywords = {
        'tops': ['top', 'shirt', 'blouse', 'tshirt', 't-shirt', 'tank', 'crop', 'tee', 'cami', 'tube'],
        'bottoms': ['pants', 'jeans', 'leggings', 'shorts', 'skirt', 'trousers', 'joggers', 'sweatpants'],
        'dresses': ['dress', 'gown', 'midi', 'maxi', 'mini'],
        'outerwear': ['jacket', 'coat', 'hoodie', 'cardigan', 'sweater', 'sweatshirt', 'blazer', 'bomber', 'parka'],
        'accessories': ['belt', 'bag', 'chain', 'necklace', 'ring', 'bracelet', 'hat', 'cap', 'choker', 'harness', 'jewelry'],
        'footwear': ['boots', 'shoes', 'sneakers', 'heels', 'sandals', 'platforms', 'docs', 'martens'],
        'gothic': ['gothic', 'goth', 'dark', 'black', 'mesh', 'lace', 'net', 'opium', 'pentagram', 'cross'],
        'punk': ['punk', 'rebel', 'studs', 'leather', 'tartan', 'plaid', 'chains', 'spikes', 'safety'],
        'vintage': ['vintage', 'retro', 'y2k', '90s', '80s', '70s', 'throwback', 'nostalgic']
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in title for keyword in keywords):
            categories.append(category)
    
    return categories if categories else ['general']

def generate_review_content(product, rating, language="en"):
    """Generate authentic Gen Z style review content with better variety"""
    global USED_PHRASES
    
    categories = get_product_category(product)
    simplified_name = get_simplified_product_name(product.get('title', ''), language)
    
    # 15% chance for empty review
    if random.random() < 0.15:
        return ""
    
    # 30% chance for short one-liner (reduced from 35%)
    if random.random() < 0.30:
        short_reviews = EXTENDED_SHORT_REVIEWS.get(language, EXTENDED_SHORT_REVIEWS["en"])
        return get_unique_phrase(short_reviews, language, "short")
    
    # Build review with varied components
    review_parts = []
    
    # Use different component combinations to avoid repetition
    component_patterns = [
        ["opening", "quality", "style"],
        ["personal", "fit", "usage"],
        ["opening", "style", "personal"],
        ["quality", "fit", "recommendation"],
        ["personal", "quality", "usage"],
        ["opening", "fit", "style", "ending"],
        ["style", "quality", "personal"],
        ["usage", "personal", "quality"]
    ]
    
    pattern = random.choice(component_patterns)
    
    for component in pattern:
        if component == "opening" and random.random() < 0.7:
            openings = REVIEW_COMPONENTS["opening_reactions"].get(language, REVIEW_COMPONENTS["opening_reactions"]["en"])
            opening = random.choice(openings)
            review_parts.append(f"{opening} {simplified_name}")
        
        elif component == "quality" and random.random() < 0.6:
            quality_comments = REVIEW_COMPONENTS["quality_comments"].get(language, REVIEW_COMPONENTS["quality_comments"]["en"])
            review_parts.append(random.choice(quality_comments))
        
        elif component == "fit" and random.random() < 0.5:
            fit_comments = REVIEW_COMPONENTS["fit_comments"].get(language, REVIEW_COMPONENTS["fit_comments"]["en"])
            review_parts.append(random.choice(fit_comments))
        
        elif component == "style" and random.random() < 0.6:
            style_comments = REVIEW_COMPONENTS["style_comments"].get(language, REVIEW_COMPONENTS["style_comments"]["en"])
            review_parts.append(random.choice(style_comments))
        
        elif component == "usage" and random.random() < 0.4:
            usage_scenarios = REVIEW_COMPONENTS["usage_scenarios"].get(language, REVIEW_COMPONENTS["usage_scenarios"]["en"])
            review_parts.append(random.choice(usage_scenarios))
        
        elif component == "personal" and random.random() < 0.5:
            personal_reactions = REVIEW_COMPONENTS["personal_reactions"].get(language, REVIEW_COMPONENTS["personal_reactions"]["en"])
            review_parts.append(random.choice(personal_reactions))
    
    # Join parts with varied punctuation
    if review_parts:
        review = ""
        for i, part in enumerate(review_parts):
            if i == 0:
                review = part
            else:
                # Varied connectors
                connectors = [". ", "! ", ", ", " - ", " and ", ". Also ", "!! ", "... "]
                weights = [30, 20, 15, 10, 10, 5, 5, 5]
                connector = random.choices(connectors, weights=weights, k=1)[0]
                review += connector + part
        
        # Youth writing style (20% chance)
        if random.random() < 0.20:
            # Lowercase variations
            if random.random() < 0.3:
                review = review.lower()
            
            # Add emojis/special characters
            if random.random() < 0.4:
                endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " fr fr", " no cap", " tbh", " ngl"]
                review += random.choice(endings)
    else:
        # Fallback to simple review
        simple_reviews = {
            "en": [f"love this {simplified_name}", f"great {simplified_name}", f"perfect {simplified_name}"],
            "de": [f"liebe dieses {simplified_name}", f"tolles {simplified_name}", f"perfektes {simplified_name}"],
            "es": [f"amo este {simplified_name}", f"gran {simplified_name}", f"perfecto {simplified_name}"],
            "fr": [f"j'adore ce {simplified_name}", f"super {simplified_name}", f"parfait {simplified_name}"],
            "it": [f"amo questo {simplified_name}", f"ottimo {simplified_name}", f"perfetto {simplified_name}"]
        }
        review = random.choice(simple_reviews.get(language, simple_reviews["en"]))
    
    return review

def generate_rating_distribution():
    """Generate realistic rating distribution with slight variation"""
    # Base: 60% 5-star, 30% 4-star, 10% 3-star
    # Add small random variation
    weights = [60 + random.randint(-5, 5), 30 + random.randint(-5, 5), 10 + random.randint(-2, 2)]
    # Normalize weights
    total = sum(weights)
    weights = [w/total * 100 for w in weights]
    
    return random.choices([5, 4, 3], weights=weights, k=1)[0]

def generate_review_date(max_months_back=36):
    """Generate random review date with realistic distribution"""
    # More recent reviews are more likely
    if random.random() < 0.4:  # 40% from last 3 months
        days_back = random.randint(1, 90)
    elif random.random() < 0.7:  # 30% from 3-12 months
        days_back = random.randint(91, 365)
    else:  # 30% from 12-36 months
        days_back = random.randint(366, max_months_back * 30)
    
    review_date = datetime.now() - timedelta(days=days_back)
    return review_date.strftime('%Y-%m-%d')

def select_language():
    """Select language with realistic distribution for European/US market"""
    # Updated weights for better distribution
    languages = ["de", "en", "es", "fr", "it", "ru", "pl", "nl", "sv", "da", 
                "fi", "cs", "hu", "tr", "ar", "el", "ko", "ja", "zh", "id", "pt"]
    
    # Weights that ensure good variety
    weights = [18, 22, 8, 7, 6, 4, 4, 3, 3, 2, 
              2, 2, 2, 2, 2, 2, 3, 3, 3, 2, 2]
    
    return random.choices(languages, weights=weights, k=1)[0]

def get_unique_phrase(phrase_list, language, category="general"):
    """Get a unique phrase with better tracking"""
    global USED_PHRASES
    
    # Create category-specific tracking
    category_key = f"{language}_{category}"
    if category_key not in USED_PHRASES:
        USED_PHRASES[category_key] = set()
    
    available_phrases = [p for p in phrase_list if p not in USED_PHRASES[category_key]]
    
    # If we've used many phrases, clear some old ones
    if len(available_phrases) < len(phrase_list) * 0.3:
        # Clear half of the used phrases
        used_list = list(USED_PHRASES[category_key])
        random.shuffle(used_list)
        for phrase in used_list[:len(used_list)//2]:
            USED_PHRASES[category_key].discard(phrase)
        available_phrases = [p for p in phrase_list if p not in USED_PHRASES[category_key]]
    
    if not available_phrases:
        available_phrases = phrase_list
    
    phrase = random.choice(available_phrases)
    USED_PHRASES[category_key].add(phrase)
    
    # Persist tracking periodically
    if random.random() < 0.1:  # 10% chance to save
        save_phrase_tracking(USED_PHRASES)
    
    return phrase

def generate_review(product, existing_reviews=0):
    """Generate a single review for a product"""
    language = select_language()
    rating = generate_rating_distribution()
    reviewer_name, reviewer_email, reviewer_location = generate_reviewer_info(language)
    
    # Title generation with variety
    if random.random() < 0.08:  # 8% no title
        review_title = ""
    else:
        titles = REVIEW_TITLES.get(language, REVIEW_TITLES["en"])
        if rating in titles:
            review_title = get_unique_phrase(titles[rating], language, f"title_{rating}")
        else:
            review_title = ""
    
    review_content = generate_review_content(product, rating, language)
    
    # Less frequent endings to reduce repetition
    if len(review_content) > 100 and random.random() < 0.15:  # Only 15% chance for longer reviews
        endings = {
            "de": {
                5: ["Klare Empfehlung!", "Top Kauf!", "Mega zufrieden!", "Immer wieder gerne!"],
                4: ["Guter Kauf.", "Bin zufrieden.", "Kann man kaufen.", "Solide Wahl."],
                3: ["Geht so.", "Okay.", "Mittelmäßig.", "Akzeptabel."]
            },
            "en": {
                5: ["Highly recommend!", "Great buy!", "Super satisfied!", "Would buy again!"],
                4: ["Good purchase.", "Satisfied.", "Worth buying.", "Solid choice."],
                3: ["It's okay.", "Average.", "Decent.", "Acceptable."]
            }
        }
        
        if language in endings and rating in endings[language]:
            ending = random.choice(endings[language][rating])
            review_content += f" {ending}"
    
    review_date = generate_review_date()
    
    # 7% chance for unverified
    verified = 'Yes' if random.random() > 0.07 else 'No'
    
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
    
    # Ensure language variety within product reviews
    min_languages = min(3, num_reviews)
    languages_used = set()
    
    for i in range(num_reviews):
        review = generate_review(product_info, existing_reviews=i)
        
        # Track language diversity
        review_lang = review.get('location', 'US')[:2]
        languages_used.add(review_lang)
        
        reviews.append(review)
    
    # Save phrase tracking at the end
    save_phrase_tracking(USED_PHRASES)
    
    return reviews

# Clean up function to reset tracking if needed
def reset_phrase_tracking():
    """Reset all phrase tracking - use sparingly"""
    global USED_PHRASES
    USED_PHRASES = defaultdict(set)
    if os.path.exists(PHRASE_TRACKING_FILE):
        os.remove(PHRASE_TRACKING_FILE)
    print("Phrase tracking reset")