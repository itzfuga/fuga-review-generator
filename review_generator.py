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
        ],
        "pl": [
            "absolutnie zakochana w tym", "totalnie zafascynowana moim nowym", "super szczęśliwa z tym",
            "naprawdę zadowolona z mojego", "całkowicie przekonana tym", "bardzo zadowolona z mojego nowego",
            "niesamowicie szczęśliwa z tym", "naprawdę pod wrażeniem tego", "totalnie zakochana w moim",
            "naprawdę dumna z tego", "niewiarygodnie szczęśliwa z mojego", "w pełni przekonana tym",
            "całkowicie usatysfakcjonowana moim", "absolutnie zachwycona tym", "totalnie oczarowana moim nowym",
            "naprawdę podekscytowana moim", "super zadowolona z tego", "naprawdę pod wrażeniem mojego",
            "całkowicie szczęśliwa z mojego nowego", "absolutnie przekonana tym"
        ],
        "cs": [
            "absolutně zamilovaná do tohoto", "totálně posedlá mým novým", "super šťastná s tímto",
            "opravdu spokojená s mým", "úplně přesvědčená tímto", "velmi spokojená s mým novým",
            "extrémně šťastná s tímto", "opravdu ohromená tímto", "totálně zamilovaná do mého",
            "opravdu hrdá na tento", "neuvěřitelně šťastná s mým", "plně přesvědčená tímto",
            "kompletně spokojená s mým", "absolutně nadšená tímto", "totálně okouzlená mým novým"
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
            "qualität ist überraschend gut", "verarbeitung lässt nichts zu wünschen übrig",
            "material ist mega nice", "qualität stimmt zu 100%", "verarbeitung ist erstklassig",
            "stoff hat eine tolle struktur", "material ist angenehm schwer", "nähte sind sauber gesetzt",
            "haptik ist butterweich", "qualität rechtfertigt jeden cent", "material ist richtig edel",
            "verarbeitung ist makellos", "stoff ist dick und stabil", "details sind perfekt durchdacht",
            "material hat gewicht", "qualität ist jeden euro wert", "verarbeitung zeigt handwerkskunst"
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
        ],
        "pl": [
            "jakość jest niesamowita", "wykonanie pierwsza klasa", "materiał czuje się premium",
            "tekstura jest niewiarygodnie dobra", "tkanina super wysokiej jakości", "szwy są perfekcyjnie wykonane",
            "detale są przemyślane", "materiał jest mocny ale miękki", "czuje się drożej niż kosztował",
            "jakość przewyższa cenę", "wykonanie na poziomie", "materiał pierwszej klasy",
            "dotyk jest po prostu premium", "tkanina czuje się luksusowo", "szwy trzymają się idealnie",
            "detale robią różnicę", "materiał jest trwały", "czuje się ekskluzywnie",
            "jakość jest zaskakująco dobra", "wykonanie nie pozostawia nic do życzenia"
        ],
        "cs": [
            "kvalita je šílená", "konstrukce je prvotřídní", "materiál působí prémiově",
            "textura je neuvěřitelně dobrá", "látka je super vysoké kvality", "švy jsou perfektně provedené",
            "detaily jsou pečlivě zpracované", "materiál je pevný ale měkký", "působí dráž než stál",
            "kvalita převyšuje cenu", "konstrukce je na úrovni", "materiál je první třídy",
            "na dotek je prostě prémiový", "látka působí luxusně", "švy drží perfektně"
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
        ],
        "pl": [
            "pasuje jak ulał", "rozmiar jest idealny", "krój jest super pochlebny",
            "leży we wszystkich właściwych miejscach", "rozmiar zgodny z opisem", "dopasowanie jest wymarzone",
            "tabela rozmiarów była dokładna", "krój podkreśla idealnie", "pasuje jakby szyte na miarę",
            "dopasowanie przekracza oczekiwania", "rozmiar pasuje jak należy", "krój jest przemyślany",
            "siedzi wygodnie ale nie luźno", "dopasowanie jest w sam raz", "rozmiar był idealnym wyborem",
            "krój jest super pochlebny", "pasuje jak druga skóra", "dopasowanie nie mogłoby być lepsze"
        ],
        "cs": [
            "sedí jako ulité", "velikost je perfektní", "střih je super lichotivý",
            "sedí na všech správných místech", "velikost odpovídá", "střih je sen",
            "tabulka velikostí byla přesná", "střih zdůrazňuje perfektně", "sedí jako na míru",
            "střih překonává očekávání", "velikost sedí jak má", "střih je promyšlený"
        ]
    },
    "style_comments": {
        "de": [
            "style ist genau mein ding", "design ist einzigartig", "look ist edgy aber tragbar",
            "ästhetik trifft meinen geschmack", "style ist zeitlos modern", "design hebt sich ab",
            "look ist sophisticated", "ästhetik ist on point", "style macht statement",
            "design ist durchdacht", "look ist vielseitig", "ästhetik ist genau richtig",
            "style ist perfekt ausbalanciert", "design ist eye-catching", "look ist mühellos cool",
            "optik ist der hammer", "schnitt ist modern", "style ist voll meins",
            "design spricht mich an", "look passt perfekt zu mir", "stil ist unverwechselbar",
            "aussehen ist top", "design hat das gewisse etwas", "style ist fresh",
            "optik überzeugt total", "look ist genau mein vibe", "design ist next level"
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
        ],
        "pl": [
            "styl jest dokładnie w moim typie", "design jest unikalny", "wygląd jest edgy ale do noszenia",
            "estetyka trafia w mój gust", "styl jest ponadczasowo nowoczesny", "design się wyróżnia",
            "wygląd jest wyrafinowany", "estetyka jest na miejscu", "styl robi wrażenie",
            "design jest przemyślany", "wygląd jest wszechstronny", "estetyka jest w sam raz",
            "styl jest idealnie wyważony", "design przyciąga wzrok", "wygląd jest bezproblemowo fajny"
        ],
        "cs": [
            "styl je přesně můj šálek kávy", "design je jedinečný", "vzhled je odvážný ale nositelný",
            "estetika sedí mému vkusu", "styl je nadčasově moderní", "design vyčnívá",
            "vzhled je sofistikovaný", "estetika je na místě", "styl dělá dojem"
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
        ],
        "pl": [
            "idealny na festiwale", "świetny do klubu", "super na co dzień", "genialny na randki",
            "niesamowity na koncerty", "rewelacyjny na imprezy", "bomba na sesje zdjęciowe", "doskonały na eventy",
            "optymalny na wyjścia", "najlepszy na celebracje", "wspaniały na spotkania", "wybitny na występy"
        ],
        "cs": [
            "perfektní na festivaly", "ideální na kluby", "skvělý na každý den", "super na rande",
            "úžasný na koncerty", "brilantní na párty", "bombový na focení", "vynikající na eventy"
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
        ],
        "pl": [
            "jestem kompletnie zakochana", "nie mogłabym być szczęśliwsza", "przekracza wszystkie oczekiwania",
            "dokładnie to czego szukałam", "lepsze niż się spodziewałam", "sprawia że jestem taka szczęśliwa",
            "spełnia wszystkie życzenia", "jestem totalnie zachwycona", "nie myślałam że będzie tak dobre",
            "jestem pozytywnie zaskoczona", "naprawdę fajnie się nosi", "czuję się w tym super"
        ],
        "cs": [
            "jsem úplně zamilovaná", "nemohla bych být šťastnější", "překonává všechna očekávání",
            "přesně to co jsem hledala", "lepší než jsem čekala", "dělá mi takovou radost",
            "splňuje všechna přání", "jsem totálně nadšená", "nemyslela jsem že to bude tak dobré"
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
    ],
    "pl": [
        "obsesja!!!!", "nowy ulubiony element", "kupione natychmiast🔥", "vibesy są nieskazitelne✨",
        "absolutny ogień 🔥", "potrzebuję tego w każdym kolorze", "dzięki fuga za to arcydzieło",
        "energia królowej", "supremacja fugi", "bierz moje pieniądze", "10000/10 kupiłabym znowu",
        "błogosławiona tym elementem", "zamanifestowane i otrzymane", "wszechświat powiedział tak", "vibesy głównej bohaterki",
        "żyję swoim najlepszym życiem", "zero myśli tylko vibesy", "poziom obsesji 1000", "już zamawiam więcej",
        "portfel płacze ale warto", "dopamina dostarczona", "serotonina nadchodzi", "szczyt mody osiągnięty",
        "gra stylowa podniesiona", "poziom pewności siebie w górę", "magnes na komplementy aktywowany", "główne wydarzenie stroju"
    ],
    "cs": [
        "posedlá!!!!", "nový oblíbený kousek", "koupeno okamžitě🔥", "vibrace jsou dokonalé✨",
        "absolutní oheň 🔥", "potřebuju to v každé barvě", "díky fuga za toto mistrovské dílo",
        "energie královny", "nadvláda fugy", "ber moje peníze", "10000/10 koupila bych znovu",
        "požehnaná tímto kouskem", "manifestováno a přijato", "vesmír řekl ano", "vibrace hlavní postavy"
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
    "pl": {
        5: [
            "Absolutnie niesamowite!", "Perfekcyjny produkt!", "Kocham to!", "Przekracza wszystkie oczekiwania!",
            "Po prostu wspaniałe!", "Must-have!", "Gorąco polecam!", "Najlepszy produkt!",
            "Jakość pierwsza klasa!", "Uwielbiam!", "Topowy produkt!", "Doskonały wybór!", "Obsesja!",
            "Literalnie perfekcyjne!", "Totalnie zakochana!", "Tak cholernie dobre!", "Niesamowite!", "Niewiarygodne!",
            "Wybitne!", "Fenomenalne!", "Wyjątkowe!", "Wspaniałe!", "Spektakularne!", "Zmienia grę!",
            "Zmienia życie!", "Ponad niesamowite!", "Absolutnie genialne!", "Czysta perfekcja!"
        ],
        4: [
            "Bardzo dobry produkt", "Prawie perfekcyjny", "Naprawdę ładny", "Bardzo zadowolona", "Dobra jakość",
            "Robi świetne wrażenie", "Godny polecenia", "Pozytywnie zaskoczona", "Świetny zakup",
            "Dobry stosunek jakości do ceny", "Piękny design", "Przekonujący", "Naprawdę fajny", "Całkiem ładny",
            "Bardzo zadowolona", "Całkiem dobry", "Naprawdę dobrze zrobiony", "Świetna rzecz", "Całkiem niesamowity",
            "Bardzo satysfakcjonujący", "Świetny element", "Zdecydowanie polecam", "Solidny wybór"
        ],
        3: [
            "W porządku", "Spełnia swoje zadanie", "Ogólnie zadowolona", "Średni", "Spełnia oczekiwania",
            "Nieźle", "Mogłoby być lepiej", "Przeciętny", "Ok jak na cenę", "Używalny", "Średnia półka",
            "Ok na co dzień", "Całkiem przyzwoity", "Jest ok", "Akceptowalny", "Satysfakcjonujący", "Standardowy",
            "Zwykły", "Wystarczająco dobry", "Rozsądny"
        ]
    },
    "cs": {
        5: [
            "Absolutně úžasné!", "Perfektní produkt!", "Miluji to!", "Překonává všechna očekávání!",
            "Prostě nádherné!", "Musíte mít!", "Vřele doporučuji!", "Nejlepší produkt!",
            "Prvotřídní kvalita!", "Zbožňuji to!", "Top produkt!", "Vynikající volba!", "Posedlost!",
            "Doslova perfektní!", "Totálně zamilovaná!", "Tak zatraceně dobré!", "Ohromující!", "Neuvěřitelné!",
            "Vynikající!", "Fenomenální!", "Výjimečné!", "Skvělé!", "Spektakulární!"
        ],
        4: [
            "Velmi dobrý produkt", "Téměř perfektní", "Opravdu pěkné", "Velmi spokojená", "Dobrá kvalita",
            "Dělá skvělý dojem", "Doporučitelné", "Pozitivně překvapená", "Skvělý nákup",
            "Dobrý poměr cena/výkon", "Krásný design", "Přesvědčivé", "Opravdu cool", "Docela pěkné",
            "Velmi spokojená", "Docela dobré", "Opravdu dobře zpracované", "Skvělá věc", "Docela úžasné"
        ],
        3: [
            "V pořádku", "Splňuje svůj účel", "Celkově spokojená", "Průměrné", "Splňuje očekávání",
            "Není špatné", "Mohlo by být lepší", "Průměrné", "Ok za tu cenu", "Použitelné", "Střední třída",
            "Ok na každý den", "Docela slušné", "Je to ok", "Přijatelné", "Uspokojivé", "Standardní"
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

def extract_product_features(product, language="en"):
    """Extract key features from product description for targeted reviews"""
    title = product.get('title', '').lower()
    description = product.get('body_html', '').lower() if product.get('body_html') else ''
    
    # Remove HTML tags from description
    import re
    description = re.sub(r'<[^>]+>', ' ', description)
    
    # Combine title and description for analysis
    content = f"{title} {description}"
    
    insights = {
        'material': [],
        'style': [],
        'features': [],
        'occasions': [],
        'colors': [],
        'fit': []
    }
    
    # Material detection
    materials = {
        'cotton': ['cotton', 'baumwolle', 'coton', 'cotone', 'algodón'],
        'polyester': ['polyester', 'poly'],
        'leather': ['leather', 'leder', 'cuir', 'cuero', 'pelle'],
        'denim': ['denim', 'jeans'],
        'silk': ['silk', 'seide', 'soie', 'seta'],
        'lace': ['lace', 'spitze', 'dentelle', 'pizzo', 'encaje'],
        'mesh': ['mesh', 'netz'],
        'velvet': ['velvet', 'samt', 'velours', 'velluto'],
        'satin': ['satin', 'raso']
    }
    
    for material, keywords in materials.items():
        if any(keyword in content for keyword in keywords):
            insights['material'].append(material)
    
    # Style detection
    styles = {
        'gothic': ['gothic', 'goth', 'dark', 'black', 'dunkel', 'noir', 'nero'],
        'punk': ['punk', 'rock', 'metal', 'spike', 'stud'],
        'vintage': ['vintage', 'retro', 'classic', 'klassisch'],
        'elegant': ['elegant', 'classy', 'sophisticated', 'chic'],
        'casual': ['casual', 'everyday', 'comfort', 'lässig'],
        'party': ['party', 'club', 'night', 'festive', 'celebration']
    }
    
    for style, keywords in styles.items():
        if any(keyword in content for keyword in keywords):
            insights['style'].append(style)
    
    # Feature detection
    features = {
        'pockets': ['pocket', 'tasche', 'poche', 'tasca', 'bolsillo'],
        'zipper': ['zipper', 'zip', 'reißverschluss', 'cremallera'],
        'buttons': ['button', 'knopf', 'bouton', 'bottone', 'botón'],
        'sleeves': ['sleeve', 'ärmel', 'manche', 'manica', 'manga'],
        'hood': ['hood', 'kapuze', 'capuche', 'cappuccio', 'capucha'],
        'belt': ['belt', 'gürtel', 'ceinture', 'cintura'],
        'adjustable': ['adjustable', 'verstellbar', 'réglable', 'regolabile']
    }
    
    for feature, keywords in features.items():
        if any(keyword in content for keyword in keywords):
            insights['features'].append(feature)
    
    # Occasions
    occasions = {
        'party': ['party', 'club', 'night', 'evening', 'celebration'],
        'casual': ['casual', 'everyday', 'daily', 'comfortable'],
        'work': ['work', 'office', 'professional', 'business'],
        'date': ['date', 'romantic', 'dinner', 'special'],
        'festival': ['festival', 'concert', 'music', 'event']
    }
    
    for occasion, keywords in occasions.items():
        if any(keyword in content for keyword in keywords):
            insights['occasions'].append(occasion)
    
    # Colors
    colors = {
        'black': ['black', 'schwarz', 'noir', 'nero', 'negro'],
        'white': ['white', 'weiß', 'blanc', 'bianco', 'blanco'],
        'red': ['red', 'rot', 'rouge', 'rosso', 'rojo'],
        'blue': ['blue', 'blau', 'bleu', 'blu', 'azul'],
        'green': ['green', 'grün', 'vert', 'verde'],
        'purple': ['purple', 'violet', 'lila', 'viola', 'morado'],
        'pink': ['pink', 'rosa', 'rose']
    }
    
    for color, keywords in colors.items():
        if any(keyword in content for keyword in keywords):
            insights['colors'].append(color)
    
    # Fit information
    fits = {
        'oversized': ['oversized', 'loose', 'baggy', 'weit'],
        'fitted': ['fitted', 'tight', 'slim', 'eng', 'ajusté'],
        'stretchy': ['stretch', 'elastic', 'flexible', 'dehnbar'],
        'comfortable': ['comfortable', 'comfort', 'bequem', 'confortable']
    }
    
    for fit, keywords in fits.items():
        if any(keyword in content for keyword in keywords):
            insights['fit'].append(fit)
    
    return insights

def generate_product_specific_comment(product_insights, language="en"):
    """Generate comments based on actual product features"""
    comments = []
    
    # Material comments
    if product_insights['material']:
        material_comments = {
            'de': {
                'cotton': 'aus Baumwolle und super angenehm',
                'leather': 'Leder fühlt sich hochwertig an',
                'lace': 'die Spitze ist wunderschön verarbeitet',
                'denim': 'Denim Qualität ist top',
                'velvet': 'Samt fühlt sich luxuriös an'
            },
            'en': {
                'cotton': 'cotton feels so comfortable',
                'leather': 'leather quality is amazing',
                'lace': 'lace detailing is gorgeous',
                'denim': 'denim is perfect weight',
                'velvet': 'velvet texture is so soft'
            },
            'pl': {
                'cotton': 'bawełna jest bardzo wygodna',
                'leather': 'skóra jest wysokiej jakości',
                'lace': 'koronka jest pięknie wykonana',
                'denim': 'denim ma idealną wagę',
                'velvet': 'aksamit jest tak miękki'
            },
            'it': {
                'cotton': 'cotone molto confortevole',
                'leather': 'pelle di ottima qualità',
                'lace': 'pizzo bellissimo',
                'denim': 'denim peso perfetto',
                'velvet': 'velluto così morbido'
            },
            'fr': {
                'cotton': 'coton très confortable',
                'leather': 'cuir de qualité incroyable',
                'lace': 'dentelle magnifique',
                'denim': 'denim poids parfait',
                'velvet': 'velours si doux'
            },
            'es': {
                'cotton': 'algodón muy cómodo',
                'leather': 'cuero de calidad increíble',
                'lace': 'encaje hermoso',
                'denim': 'denim peso perfecto',
                'velvet': 'terciopelo tan suave'
            },
            'cs': {
                'cotton': 'bavlna velmi pohodlná',
                'leather': 'kůže skvělé kvality',
                'lace': 'krajka nádherná',
                'denim': 'denim perfektní váha',
                'velvet': 'samet tak měkký'
            }
        }
        
        for material in product_insights['material']:
            lang_comments = material_comments.get(language, material_comments['en'])
            if material in lang_comments:
                comments.append(lang_comments[material])
    
    # Feature comments
    if product_insights['features']:
        feature_comments = {
            'de': {
                'pockets': 'Taschen sind praktisch',
                'zipper': 'Reißverschluss läuft smooth',
                'hood': 'Kapuze ist perfekt geschnitten',
                'sleeves': 'Ärmel haben die perfekte Länge'
            },
            'en': {
                'pockets': 'pockets are so useful',
                'zipper': 'zipper quality is great',
                'hood': 'hood fits perfectly', 
                'sleeves': 'sleeve length is perfect'
            },
            'pl': {
                'pockets': 'kieszenie są bardzo praktyczne',
                'zipper': 'zamek błyskawiczny działa świetnie',
                'hood': 'kaptur pasuje idealnie',
                'sleeves': 'długość rękawów jest idealna'
            },
            'it': {
                'pockets': 'tasche molto utili',
                'zipper': 'qualità della cerniera ottima',
                'hood': 'cappuccio veste perfettamente',
                'sleeves': 'lunghezza maniche perfetta'
            },
            'fr': {
                'pockets': 'poches très utiles',
                'zipper': 'qualité de la fermeture éclair excellente',
                'hood': 'capuche s\'ajuste parfaitement',
                'sleeves': 'longueur des manches parfaite'
            },
            'es': {
                'pockets': 'bolsillos muy útiles',
                'zipper': 'calidad de la cremallera excelente',
                'hood': 'capucha ajusta perfectamente',
                'sleeves': 'longitud de mangas perfecta'
            },
            'cs': {
                'pockets': 'kapsy velmi praktické',
                'zipper': 'kvalita zipu vynikající',
                'hood': 'kapuce sedí dokonale',
                'sleeves': 'délka rukávů perfektní'
            }
        }
        
        for feature in product_insights['features']:
            lang_comments = feature_comments.get(language, feature_comments['en'])
            if feature in lang_comments:
                comments.append(lang_comments[feature])
    
    # Style comments
    if product_insights['style']:
        style_comments = {
            'de': {
                'gothic': 'der Gothic Style ist genau mein Ding',
                'punk': 'Punk Vibe ist authentisch',
                'vintage': 'Vintage Look ist zeitlos',
                'elegant': 'elegant und raffiniert'
            },
            'en': {
                'gothic': 'gothic aesthetic is perfect',
                'punk': 'punk vibe is authentic',
                'vintage': 'vintage style is timeless',
                'elegant': 'elegant and classy'
            },
            'pl': {
                'gothic': 'gotycki styl jest idealny',
                'punk': 'punkowy klimat jest autentyczny',
                'vintage': 'vintage styl jest ponadczasowy',
                'elegant': 'elegancki i stylowy'
            },
            'it': {
                'gothic': 'estetica gotica è perfetta',
                'punk': 'vibe punk è autentico',
                'vintage': 'stile vintage è senza tempo',
                'elegant': 'elegante e di classe'
            },
            'fr': {
                'gothic': 'esthétique gothique est parfaite',
                'punk': 'vibe punk est authentique',
                'vintage': 'style vintage est intemporel',
                'elegant': 'élégant et chic'
            },
            'es': {
                'gothic': 'estética gótica es perfecta',
                'punk': 'vibe punk es auténtico',
                'vintage': 'estilo vintage es atemporal',
                'elegant': 'elegante y con clase'
            },
            'cs': {
                'gothic': 'gotický styl je perfektní',
                'punk': 'punkový vibe je autentický',
                'vintage': 'vintage styl je nadčasový',
                'elegant': 'elegantní a stylový'
            }
        }
        
        for style in product_insights['style']:
            lang_comments = style_comments.get(language, style_comments['en'])
            if style in lang_comments:
                comments.append(lang_comments[style])
    
    # Fit comments
    if product_insights['fit']:
        fit_comments = {
            'de': {
                'oversized': 'oversized Fit ist mega gemütlich',
                'fitted': 'tailliert und schmeichelt der Figur',
                'stretchy': 'Material ist schön dehnbar',
                'comfortable': 'unglaublich bequem zu tragen'
            },
            'en': {
                'oversized': 'oversized fit is so comfy',
                'fitted': 'fitted perfectly to my body',
                'stretchy': 'material has great stretch',
                'comfortable': 'incredibly comfortable to wear'
            },
            'pl': {
                'oversized': 'oversized krój jest bardzo wygodny',
                'fitted': 'dopasowany idealnie do ciała',
                'stretchy': 'materiał ma świetną elastyczność',
                'comfortable': 'niesamowicie wygodny do noszenia'
            },
            'it': {
                'oversized': 'vestibilità oversized è comoda',
                'fitted': 'aderente perfettamente al corpo',
                'stretchy': 'materiale ha ottima elasticità',
                'comfortable': 'incredibilmente comodo da indossare'
            },
            'fr': {
                'oversized': 'coupe oversized est confortable',
                'fitted': 'ajusté parfaitement au corps',
                'stretchy': 'matériau a une grande élasticité',
                'comfortable': 'incroyablement confortable à porter'
            },
            'es': {
                'oversized': 'ajuste oversized es cómodo',
                'fitted': 'ajustado perfectamente al cuerpo',
                'stretchy': 'material tiene gran elasticidad',
                'comfortable': 'increíblemente cómodo de usar'
            },
            'cs': {
                'oversized': 'oversized střih je pohodlný',
                'fitted': 'přiléhavý dokonale k tělu',
                'stretchy': 'materiál má skvělou pružnost',
                'comfortable': 'neuvěřitelně pohodlný na nošení'
            }
        }
        
        for fit in product_insights['fit']:
            lang_comments = fit_comments.get(language, fit_comments['en'])
            if fit in lang_comments:
                comments.append(lang_comments[fit])
    
    # Occasion comments
    if product_insights['occasions']:
        occasion_comments = {
            'de': {
                'party': 'perfekt für Partys',
                'casual': 'ideal für den Alltag',
                'date': 'super für Dates',
                'work': 'auch fürs Büro geeignet'
            },
            'en': {
                'party': 'perfect for parties',
                'casual': 'great for everyday wear',
                'date': 'amazing for date nights',
                'work': 'works for office too'
            },
            'pl': {
                'party': 'idealne na imprezy',
                'casual': 'świetne na co dzień',
                'date': 'super na randki',
                'work': 'sprawdza się też w pracy'
            },
            'it': {
                'party': 'perfetto per le feste',
                'casual': 'ottimo per tutti i giorni',
                'date': 'fantastico per gli appuntamenti',
                'work': 'va bene anche per l\'ufficio'
            },
            'fr': {
                'party': 'parfait pour les fêtes',
                'casual': 'excellent pour tous les jours',
                'date': 'génial pour les rendez-vous',
                'work': 'convient aussi au bureau'
            },
            'es': {
                'party': 'perfecto para fiestas',
                'casual': 'genial para el día a día',
                'date': 'increíble para citas',
                'work': 'funciona para la oficina también'
            },
            'cs': {
                'party': 'perfektní na večírky',
                'casual': 'skvělé na každý den',
                'date': 'úžasné na rande',
                'work': 'hodí se i do kanceláře'
            }
        }
        
        for occasion in product_insights['occasions']:
            lang_comments = occasion_comments.get(language, occasion_comments['en'])
            if occasion in lang_comments:
                comments.append(lang_comments[occasion])
    
    # Always return a comment if we have any insights, otherwise create a generic one
    if comments:
        return random.choice(comments)
    
    # Fallback generic product-specific comments if no specific insights found
    generic_comments = {
        'de': ['genau was ich gesucht hab', 'entspricht der Beschreibung', 'wie auf den Bildern'],
        'en': ['exactly what I was looking for', 'matches the description', 'just like in the pictures'],
        'pl': ['dokładnie tego szukałam', 'zgodne z opisem', 'jak na zdjęciach'],
        'it': ['esattamente quello che cercavo', 'corrisponde alla descrizione', 'come nelle foto'],
        'fr': ['exactement ce que je cherchais', 'correspond à la description', 'comme sur les photos'],
        'es': ['exactamente lo que buscaba', 'coincide con la descripción', 'como en las fotos'],
        'cs': ['přesně to co jsem hledala', 'odpovídá popisu', 'jako na fotkách']
    }
    
    fallback = generic_comments.get(language, generic_comments['en'])
    return random.choice(fallback)

def generate_youthful_username():
    """Generate trendy, youth-oriented usernames with more variety and realism"""
    
    # 40% chance for simple, normal usernames
    if random.random() < 0.4:
        normal_usernames = [
            "sarah_m", "alex_k", "emma_95", "mike_j", "lea_s", "tom_b", "nina_x", "ben_l",
            "mia_2024", "luke_s", "anna_k", "max_t", "lara_m", "finn_b", "zoe_l", "jan_s",
            "lily_r", "noah_k", "maya_s", "erik_m", "luna_j", "dean_b", "ivy_x", "cole_s",
            "ruby_k", "jude_m", "sage_l", "kai_b", "nova_s", "cruz_k", "rain_j", "fox_m",
            "user12345", "reviewer99", "customer2024", "shopper_x", "buyer123", "guest_user"
        ]
        return random.choice(normal_usernames)
    
    # For the rest, generate trendy usernames but less obvious
    prefixes = ["", "", "", "", "lil", "big", "the", "its", "my", "ur", "x", ""]  # More empty prefixes
    
    themes = [
        # Reduced dark/gothic themes, added more normal ones
        "style", "fashion", "vibe", "mood", "aesthetic", "trend", "look", "fit", "drip",
        "music", "beat", "rhythm", "melody", "dance", "party", "fun", "cool", "chill",
        "star", "moon", "sun", "sky", "dream", "hope", "joy", "love", "peace", "free",
        "art", "photo", "travel", "nature", "ocean", "forest", "mountain", "city", "home",
        "book", "game", "tech", "digital", "online", "web", "net", "social", "connect",
        # Keep some edgy but less obvious
        "rebel", "wild", "free", "chaos", "storm", "fire", "ice", "thunder", "shadow", "light"
    ]
    
    suffixes = ["", "", "", "", "", "x", "2024", "23", "24", "99", "00", "01", "02", "03"]
    
    # Add some birth years (less obvious)
    current_year = datetime.now().year
    for year in range(current_year - 24, current_year - 18):
        suffixes.append(str(year % 100))
    
    # Generate username - simpler structure
    if random.random() < 0.2:  # 20% chance for complex username (reduced from 30%)
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
            },
            "pl": {
                "first": ["Maja", "Jakub", "Zuzanna", "Kacper", "Julia", "Szymon", "Lena", "Filip", "Aleksandra", "Jan",
                         "Zofia", "Antoni", "Oliwia", "Franciszek", "Natalia", "Mikołaj", "Maria", "Wojciech", "Alicja", "Adam",
                         "Wiktoria", "Michał", "Emilia", "Marcel", "Hanna", "Wiktor", "Amelia", "Piotr", "Nikola", "Igor"],
                "last": ["K.", "W.", "N.", "L.", "Z.", "S.", "M.", "B.", "G.", "P.", "C.", "J.", "D.", "R.",
                        "T.", "A.", "O.", "E.", "F.", "H."]
            },
            "cs": {
                "first": ["Tereza", "Jakub", "Eliška", "Jan", "Anna", "Tomáš", "Adéla", "Matyáš", "Natálie", "Vojtěch",
                         "Sofie", "Adam", "Viktorie", "Ondřej", "Karolína", "Filip", "Kristýna", "Lukáš", "Barbora", "David"],
                "last": ["N.", "K.", "P.", "S.", "V.", "M.", "H.", "D.", "C.", "B.", "L.", "T.", "J.", "R."]
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
    
    # Location based on real Shopify ORDER data (customers who actually buy)
    locations = {
        "de": ["DE", "DE", "DE", "DE", "DE", "AT", "CH"],  # 37% DE + 4% AT + 4% CH
        "pl": ["PL", "PL", "PL", "CZ", "SK"],  # 11% Polish customers + neighbors
        "en": ["US", "US", "US", "UK", "UK", "CA", "AU"],  # 9% US + 4% UK + 1% CA
        "it": ["IT", "IT", "IT", "IT", "CH"],  # 6% Italian customers
        "fr": ["FR", "FR", "BE", "CH"],  # 2% France + Belgium
        "es": ["ES", "ES", "ES"],  # 2% Spanish customers
        "nl": ["NL", "NL", "BE"],  # 2% Netherlands
        "sv": ["SE", "SE", "DK"],  # 1% Sweden + Denmark
        "cs": ["CZ", "CZ", "SK"],  # 2% Czech Republic
        "ja": ["JP", "JP"],  # 2% Japan
        "ko": ["KR"],  # 1% South Korea
        "ru": ["RU", "BY", "KZ", "LT"],  # 1% Russia + neighbors
        "da": ["DK", "NO"],
        "sk": ["SK", "CZ"],
        "tr": ["TR"],
        "fi": ["FI"],
        "no": ["NO"],
        "hu": ["HU"],
        "zh": ["CN", "TW", "HK"]
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
            "it": ["pezzo", "articolo", "prodotto"],
            "pl": ["element", "rzecz", "artykuł", "produkt"],
            "cs": ["kousek", "věc", "produkt", "zboží"]
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

def generate_review_content(product, rating, language="en", product_insights=None):
    """Generate authentic Gen Z style review content with product-specific details"""
    global USED_PHRASES
    
    if product_insights is None:
        product_insights = extract_product_features(product, language)
    
    categories = get_product_category(product)
    simplified_name = get_simplified_product_name(product.get('title', ''), language)
    
    # 5% chance for empty review (reduced from 15%)
    if random.random() < 0.05:
        return ""
    
    # 20% chance for short one-liner (reduced from 30%)
    if random.random() < 0.20:
        short_reviews = EXTENDED_SHORT_REVIEWS.get(language, EXTENDED_SHORT_REVIEWS["en"])
        return get_unique_phrase(short_reviews, language, "short")
    
    # Build review with varied components
    review_parts = []
    
    # Use different component combinations with more product-specific emphasis
    component_patterns = [
        ["opening", "product_specific", "quality"],
        ["product_specific", "fit", "personal"],
        ["opening", "product_specific", "personal"],
        ["quality", "product_specific", "style"],
        ["product_specific", "quality", "usage"],
        ["opening", "fit", "product_specific"],
        ["style", "product_specific", "personal"],
        ["usage", "product_specific", "quality"],
        ["product_specific", "quality", "style"],
        ["personal", "product_specific", "fit"],
        ["product_specific", "style", "usage"],
        ["opening", "product_specific", "ending"]
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
        
        elif component == "product_specific" and random.random() < 0.95:
            # Add product-specific insights from description (increased from 80% to 95%)
            specific_comment = generate_product_specific_comment(product_insights, language)
            if specific_comment:
                review_parts.append(specific_comment)
        
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
                # Language-specific connectors
                if language == "de":
                    connectors = [". ", "! ", ", ", " - ", " und ", ". Außerdem ", "!! ", "... "]
                elif language == "pl":
                    connectors = [". ", "! ", ", ", " - ", " i ", ". Dodatkowo ", "!! ", "... "]
                elif language == "cs":
                    connectors = [". ", "! ", ", ", " - ", " a ", ". Také ", "!! ", "... "]
                elif language == "it":
                    connectors = [". ", "! ", ", ", " - ", " e ", ". Inoltre ", "!! ", "... "]
                elif language == "fr":
                    connectors = [". ", "! ", ", ", " - ", " et ", ". De plus ", "!! ", "... "]
                elif language == "es":
                    connectors = [". ", "! ", ", ", " - ", " y ", ". Además ", "!! ", "... "]
                else:  # English default
                    connectors = [". ", "! ", ", ", " - ", " and ", ". Also ", "!! ", "... "]
                    
                weights = [30, 20, 15, 10, 10, 5, 5, 5]
                connector = random.choices(connectors, weights=weights, k=1)[0]
                review += connector + part
        
        # Youth writing style (20% chance)
        if random.random() < 0.20:
            # Lowercase variations
            if random.random() < 0.3:
                review = review.lower()
            
            # Add emojis/special characters with language-appropriate slang
            if random.random() < 0.4:
                if language == "en":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " fr fr", " no cap", " tbh", " ngl"]
                elif language == "de":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " echt jetzt", " safe", " digga", " krass"]
                elif language == "pl":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " serio", " czad", " kozak", " sztos"]
                elif language == "cs":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " fakt", " super", " paráda"]
                elif language == "it":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " davvero", " pazzesco", " top"]
                elif language == "fr":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " grave", " trop bien", " chanmé"]
                elif language == "es":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤", " literal", " que guay", " brutal"]
                else:
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤"]
                review += random.choice(endings)
    else:
        # Fallback to simple review
        simple_reviews = {
            "en": [f"love this {simplified_name}", f"great {simplified_name}", f"perfect {simplified_name}"],
            "de": [f"liebe dieses {simplified_name}", f"tolles {simplified_name}", f"perfektes {simplified_name}"],
            "es": [f"amo este {simplified_name}", f"gran {simplified_name}", f"perfecto {simplified_name}"],
            "fr": [f"j'adore ce {simplified_name}", f"super {simplified_name}", f"parfait {simplified_name}"],
            "it": [f"amo questo {simplified_name}", f"ottimo {simplified_name}", f"perfetto {simplified_name}"],
            "pl": [f"kocham ten {simplified_name}", f"świetny {simplified_name}", f"perfekcyjny {simplified_name}"],
            "cs": [f"miluji tento {simplified_name}", f"skvělý {simplified_name}", f"perfektní {simplified_name}"]
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
    """Select language based on real Shopify ORDER data (not sessions)"""
    # Based on actual orders: 37% DE, 11% PL, 9% US, 6% IT, 4% UK, 4% AT, etc.
    languages = ["de", "pl", "en", "it", "fr", "es", "nl", "sv", "da", "cs", 
                "ja", "ko", "ru", "tr", "sk", "fi", "no", "hu", "el", "pt", "zh"]
    
    # Real order-based weights: 37% German, 11% Polish, 9% English, 6% Italian
    weights = [37, 11, 13, 6, 2, 2, 2, 1, 1, 2, 
              2, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5]
    
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
    """Generate a single review for a product using product description"""
    language = select_language()
    rating = generate_rating_distribution()
    reviewer_name, reviewer_email, reviewer_location = generate_reviewer_info(language)
    
    # Extract product insights from description
    product_insights = extract_product_features(product, language)
    
    # Title generation with better consistency
    if random.random() < 0.12:  # 12% no title (slightly increased)
        review_title = ""
    else:
        titles = REVIEW_TITLES.get(language, REVIEW_TITLES["en"])
        if rating in titles and titles[rating]:
            review_title = get_unique_phrase(titles[rating], language, f"title_{rating}")
        else:
            # Fallback titles for missing ratings
            fallback_titles = {
                "de": ["Gute Qualität", "Zufrieden", "Okay", "Top!", "Empfehlenswert"],
                "en": ["Good quality", "Satisfied", "Nice!", "Great!", "Recommended"],
                "es": ["Buena calidad", "Satisfecho", "¡Bien!", "¡Genial!", "Recomendado"],
                "fr": ["Bonne qualité", "Satisfait", "Sympa!", "Super!", "Recommandé"],
                "it": ["Buona qualità", "Soddisfatto", "Bello!", "Ottimo!", "Consigliato"]
            }
            fallback = fallback_titles.get(language, fallback_titles["en"])
            review_title = random.choice(fallback)
    
    review_content = generate_review_content(product, rating, language, product_insights)
    
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

# Testing function to validate language consistency
def test_language_consistency(num_tests=50):
    """Test that reviews maintain language consistency"""
    import re
    
    # Common cross-language contamination patterns
    contamination_patterns = {
        'de': {
            'forbidden': [r'\b(and|also|the|is|for|with)\b', r'\b(no cap|tbh|fr fr|ngl)\b'],
            'allowed': ['und', 'auch', 'der', 'die', 'das', 'ist', 'für', 'mit']
        },
        'pl': {
            'forbidden': [r'\b(and|also|the|is|for|with|und|der|die|das)\b', r'\b(no cap|tbh|fr fr|ngl)\b'],
            'allowed': ['i', 'także', 'jest', 'dla', 'z']
        },
        'cs': {
            'forbidden': [r'\b(and|also|the|is|for|with|und|der|die|das)\b', r'\b(no cap|tbh|fr fr|ngl)\b'],
            'allowed': ['a', 'také', 'je', 'pro', 's']
        },
        'it': {
            'forbidden': [r'\b(and|also|the|is|for|with)\b', r'\b(no cap|tbh|fr fr|ngl)\b'],
            'allowed': ['e', 'anche', 'il', 'la', 'è', 'per', 'con']
        },
        'fr': {
            'forbidden': [r'\b(and|also|the|is|for|with)\b', r'\b(no cap|tbh|fr fr|ngl)\b'],
            'allowed': ['et', 'aussi', 'le', 'la', 'est', 'pour', 'avec']
        },
        'es': {
            'forbidden': [r'\b(and|also|the|is|for|with)\b', r'\b(no cap|tbh|fr fr|ngl)\b'],
            'allowed': ['y', 'también', 'el', 'la', 'es', 'para', 'con']
        }
    }
    
    # Test product
    test_product = {
        'id': '12345',
        'title': 'Gothic Punk Mesh Top with Chains',
        'body_html': '<p>Edgy mesh top featuring decorative chains and punk aesthetic. Perfect for concerts and clubbing.</p>',
        'handle': 'gothic-punk-mesh-top'
    }
    
    results = {
        'total': num_tests,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    print(f"\n🧪 Testing language consistency with {num_tests} reviews...\n")
    
    for i in range(num_tests):
        # Generate a review
        review_data = generate_review(test_product, existing_reviews=i)
        
        language = review_data.get('location', 'US')[:2].lower()
        
        # Map location to language
        location_language_map = {
            'de': 'de', 'at': 'de',
            'ch': 'de',  # Switzerland is complex - could be de/fr/it but we'll default to de
            'pl': 'pl', 
            'cz': 'cs', 'sk': 'cs',
            'it': 'it',
            'fr': 'fr', 'be': 'fr',
            'es': 'es',
            'us': 'en', 'uk': 'en', 'ca': 'en', 'au': 'en',
            'nl': 'nl', 'se': 'sv', 'dk': 'da', 'no': 'no',
            'fi': 'fi', 'hu': 'hu', 'jp': 'ja', 'kr': 'ko',
            'ru': 'ru', 'by': 'ru', 'kz': 'ru', 'lt': 'ru',
            'tr': 'tr', 'cn': 'zh', 'tw': 'zh', 'hk': 'zh'
        }
        
        expected_language = location_language_map.get(language, 'en')
        
        # Check title and content for contamination
        title = review_data.get('title', '')
        content = review_data.get('content', '')
        full_text = f"{title} {content}".lower()
        
        # Skip empty reviews
        if not full_text.strip():
            results['passed'] += 1
            continue
        
        # Check for forbidden patterns
        has_contamination = False
        if expected_language in contamination_patterns:
            patterns = contamination_patterns[expected_language]
            for pattern in patterns['forbidden']:
                if re.search(pattern, full_text, re.IGNORECASE):
                    has_contamination = True
                    error = {
                        'review_num': i + 1,
                        'location': review_data.get('location'),
                        'expected_language': expected_language,
                        'pattern_found': pattern,
                        'title': title,
                        'content': content[:100] + '...' if len(content) > 100 else content
                    }
                    results['errors'].append(error)
                    break
        
        if has_contamination:
            results['failed'] += 1
        else:
            results['passed'] += 1
    
    # Print results
    print(f"✅ Passed: {results['passed']}/{results['total']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"❌ Failed: {results['failed']}/{results['total']} ({results['failed']/results['total']*100:.1f}%)")
    
    if results['errors']:
        print("\n⚠️  Language contamination detected:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"\n  Review #{error['review_num']}:")
            print(f"  Location: {error['location']} (Expected: {error['expected_language']})")
            print(f"  Found pattern: {error['pattern_found']}")
            print(f"  Title: {error['title']}")
            print(f"  Content: {error['content']}")
    
    # Check distribution
    print("\n📊 Language distribution check:")
    language_counts = {}
    for i in range(100):
        lang = select_language()
        language_counts[lang] = language_counts.get(lang, 0) + 1
    
    expected_distribution = {
        'de': 37, 'pl': 11, 'en': 13, 'it': 6, 'fr': 2, 'es': 2, 
        'nl': 2, 'sv': 1, 'da': 1, 'cs': 2, 'ja': 2, 'ko': 1, 
        'ru': 1, 'tr': 1, 'sk': 1, 'fi': 1, 'no': 1
    }
    
    print(f"{'Language':<10} {'Expected':<10} {'Actual':<10} {'Diff':<10}")
    print("-" * 40)
    for lang in ['de', 'pl', 'en', 'it', 'cs', 'fr', 'es']:
        expected = expected_distribution.get(lang, 0)
        actual = language_counts.get(lang, 0)
        diff = actual - expected
        print(f"{lang:<10} {expected:<10} {actual:<10} {diff:+<10}")
    
    return results