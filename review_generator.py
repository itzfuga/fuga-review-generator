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
            "bin absolut verliebt in dieses", "total begeistert von diesem Teil", "so happy mit dem Kauf",
            "richtig zufrieden damit", "komplett überzeugt", "voll happy mit meinem neuen Teil",
            "super zufrieden", "echt beeindruckt", "bin total verliebt",
            "richtig stolz auf den Kauf", "mega glücklich", "voll überzeugt",
            "komplett zufrieden", "absolut happy", "total verliebt in mein neues Teil",
            "richtig begeistert", "mega zufrieden", "voll beeindruckt",
            "komplett happy mit dem neuen Teil", "absolut überzeugt"
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
            "absolutnie zakochana w tym", "jestem zachwycona moim nowym", "super szczęśliwa z tym",
            "naprawdę zadowolona", "całkowicie przekonana", "bardzo zadowolona z nowego",
            "niesamowicie szczęśliwa", "naprawdę pod wrażeniem", "totalnie zakochana",
            "naprawdę dumna z zakupu", "niewiarygodnie szczęśliwa", "w pełni przekonana",
            "całkowicie usatysfakcjonowana", "absolutnie zachwycona", "totalnie oczarowana",
            "naprawdę podekscytowana", "super zadowolona", "naprawdę pod wrażeniem",
            "całkowicie szczęśliwa z nowego", "absolutnie przekonana"
        ],
        "cs": [
            "absolutně zamilovaná do tohoto", "jsem nadšená mým novým", "super šťastná s tímto",
            "opravdu spokojená", "úplně přesvědčená", "velmi spokojená s novým",
            "extrémně šťastná", "opravdu ohromená", "totálně zamilovaná",
            "opravdu hrdá na nákup", "neuvěřitelně šťastná", "plně přesvědčená",
            "kompletně spokojená s mým", "absolutně nadšená tímto", "totálně okouzlená mým novým"
        ]
    },
    "quality_comments": {
        "de": [
            "qualität ist der wahnsinn", "verarbeitung ist erstklassig", "material fühlt sich premium an",
            "haptik ist unglaublich gut", "stoff ist super hochwertig", "nähte sind perfekt verarbeitet",
            "details sind liebevoll gemacht", "material ist robust aber weich", "fühlt sich teurer an als es war",
            "qualität übertrifft den preis", "verarbeitung ist perfekt", "material ist erstklassig",
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
        # Pure German youth expressions
        "krass gut", "neues lieblingsstück", "sofort gekauft", "total verliebt",
        "absolut genial", "brauche das in allen farben", "danke fuga für dieses teil", "mein neuer favorit",
        "bin so happy", "fuga ist einfach top", "nimm mein geld", "würde ich wieder kaufen",
        "mega zufrieden damit", "genau was ich wollte", "könnte nicht besser sein", "macht mich glücklich",
        "lebe für diesen style", "einfach perfekt", "total obsessed", "bestelle gleich mehr",
        "teuer aber jeden cent wert", "qualität überzeugt total", "glück pur", "fashion ziele erreicht",
        "style komplett verwandelt", "selbstbewusstsein durch die decke", "komplimente garantiert", "outfit highlight",
        "kleiderschrank essential", "perfekte ergänzung", "style ziele", "fashion gewinn",
        "sieht teurer aus", "premium qualität", "absolut stunning", "erwartungen übertroffen",
        "foto ready", "perfekt für anlässe", "ästhetik on point", "traumhaft schön",
        "basis garderobe", "style investment", "qualität spricht bände", "statement piece",
        "sofortiger confidence boost", "magnet für komplimente", "outfit perfektion", "style zufriedenheit",
        "premium feeling", "luxus gefühl", "designer qualität", "absolut gorgeous",
        "perfekte passform", "genau wie beschrieben", "qualität beeindruckend", "style revolution"
    ],
    "en": [
        # Natural youth expressions without forced slang
        "obsessed with this piece", "new favorite item", "bought instantly", "so happy with this",
        "absolutely love it", "need this in every color", "thank you fuga for this", "my new go-to piece",
        "feels so premium", "worth every penny", "take my money", "would buy again instantly",
        "blessed with this purchase", "exactly what I wanted", "couldn't be happier", "makes me so confident",
        "living for this style", "no regrets buying this", "obsession level max", "ordering more colors",
        "expensive but worth it", "quality exceeded expectations", "happiness delivered", "fashion goals achieved",
        "style transformation complete", "confidence boost secured", "compliments guaranteed", "outfit game strong",
        "wardrobe essential now", "perfect addition", "style goals", "fashion win",
        "looks more expensive", "premium quality feel", "absolutely stunning", "exceeded expectations",
        "photo ready", "perfect for occasions", "aesthetic on point", "vision board material",
        "wardrobe staple", "style investment", "quality speaks volumes", "fashion statement piece",
        "instant confidence boost", "compliment magnet", "outfit perfection", "style satisfaction",
        "premium vibes", "luxury feel", "designer quality", "absolutely gorgeous",
        "perfect fit achieved", "exactly as described", "quality impressive", "style revolution"
    ],
    "es": [
        "obsesionada con esto", "nueva pieza favorita", "comprado al instante", "muy feliz con esto",
        "absolutamente genial", "necesito esto en todos los colores", "gracias fuga por esto", "mi nueva obsesión",
        "calidad increíble", "supremacía fuga", "toma mi dinero", "compraría de nuevo",
        "perfecta compra", "exactamente lo que quería", "no podría estar más feliz", "me hace tan feliz",
        "viviendo para este estilo", "sin dudas la mejor compra", "obsesión total", "pidiendo más colores",
        "caro pero vale la pena", "calidad superó expectativas", "felicidad pura", "objetivos de moda",
        "transformación completa", "confianza por las nubes", "cumplidos asegurados", "protagonista del outfit",
        "esencial en el armario", "adición perfecta", "objetivos de estilo", "victoria de moda",
        "parece más caro", "calidad premium", "absolutamente hermoso", "superó expectativas",
        "listo para fotos", "perfecto para ocasiones", "estética perfecta", "material de sueños",
        "básico del guardarropa", "inversión de estilo", "calidad habla por sí", "pieza declaración",
        "confianza instantánea", "imán de cumplidos", "perfección de outfit", "satisfacción total",
        "vibras premium", "sensación de lujo", "calidad de diseñador", "absolutamente hermoso",
        "ajuste perfecto", "exactamente como describían", "calidad impresionante", "revolución de estilo"
    ],
    "fr": [
        "obsédée avec cette pièce", "nouvelle pièce préférée", "acheté instantanément🔥", "trop contente de cet achat",
        "absolument génial", "j'ai besoin de ça dans toutes les couleurs", "merci fuga pour ce chef-d'œuvre",
        "confiance au top", "vraiment top fuga", "prends mon argent", "10000/10 j'achèterais encore",
        "super heureuse avec ça", "manifesté et reçu", "exactement ce que je voulais", "style parfait pour moi",
        "qualité exceptionnelle", "livraison rapide merci", "taille parfaite", "matière agréable au toucher",
        "coupe très flatteuse", "couleur magnifique", "finitions soignées", "rapport qualité prix",
        "vraiment bien fini", "confortable à porter", "style intemporel", "parfait comme décrit",
        "aucun regret d'achat", "investissement mode", "pièce indispensable", "look complet",
        "style transformé", "confiance boostée", "compliments assurés", "garde-robe enrichie",
        "achat vraiment malin", "qualité premium", "rendu parfait", "satisfaction totale"
    ],
    "it": [
        "ossessionata con questo pezzo", "nuovo pezzo preferito", "comprato istantaneamente🔥", "davvero soddisfatta",
        "assolutamente fantastico", "ne ho bisogno in ogni colore", "grazie fuga per questo capolavoro",
        "fiducia alle stelle", "fuga sempre al top", "prendi i miei soldi", "10000/10 comprerei di nuovo",
        "super felice con questo", "manifestato e ricevuto", "esattamente quello che volevo", "stile perfetto per me",
        "qualità eccezionale", "spedizione veloce grazie", "taglia perfetta", "materiale piacevole",
        "taglio molto lusinghiero", "colore bellissimo", "finiture curate", "rapporto qualità prezzo",
        "davvero ben rifinito", "comodo da indossare", "stile senza tempo", "perfetto come descritto",
        "nessun rimpianto", "investimento moda", "pezzo indispensabile", "look completo",
        "stile trasformato", "fiducia aumentata", "complimenti garantiti", "guardaroba arricchito",
        "acquisto davvero intelligente", "qualità premium", "risultato perfetto", "soddisfazione totale"
    ],
    "pl": [
        "obsesja z tym elementem", "nowy ulubiony element", "kupione natychmiast🔥", "naprawdę zadowolona",
        "absolutnie fantastyczne", "potrzebuję tego w każdym kolorze", "dzięki fuga za to arcydzieło",
        "pewność siebie na maxa", "fuga zawsze najlepsza", "bierz moje pieniądze", "10000/10 kupiłabym znowu",
        "super szczęśliwa z tym", "zamanifestowane i otrzymane", "dokładnie to czego chciałam", "idealny dla mojego stylu",
        "jakość wyjątkowa", "szybka dostawa dzięki", "rozmiar idealny", "materiał przyjemny w dotyku",
        "krój bardzo pochlebiający", "kolor przepiękny", "wykończenia staranne", "stosunek jakości do ceny",
        "naprawdę dobrze wykonane", "wygodne do noszenia", "styl ponadczasowy", "dokładnie jak opisane",
        "zero żalu za zakup", "inwestycja w modę", "element niezbędny", "kompletny look",
        "styl przeobrażony", "pewność siebie wzrosła", "komplementy gwarantowane", "szafa wzbogacona",
        "naprawdę mądry zakup", "jakość premium", "efekt idealny", "całkowita satysfakcja"
    ],
    "cs": [
        "posedlá tímto kouskem", "nový oblíbený kousek", "koupeno okamžitě🔥", "opravdu spokojená",
        "absolutně fantastické", "potřebuju to v každé barvě", "díky fuga za toto mistrovské dílo",
        "sebevědomí na vrcholu", "fuga vždy nejlepší", "ber moje peníze", "10000/10 koupila bych znovu",
        "super šťastná s tímto", "manifestováno a přijato", "přesně co jsem chtěla", "styl ideální pro mě",
        "kvalita výjimečná", "rychlé doručení děkuji", "velikost ideální", "materiál příjemný na dotek",
        "střih velmi lichotivý", "barva nádherná", "zpracování pečlivé", "poměr kvality a ceny",
        "opravdu dobře udělané", "pohodlné na nošení", "styl nadčasový", "přesně jak popsáno",
        "nula lítosti za nákup", "investice do módy", "kousek nezbytný", "kompletní look",
        "styl transformován", "sebevědomí vzrostlo", "komplimenty zaručené", "šatník obohacen",
        "opravdu chytrý nákup", "kvalita premium", "efekt ideální", "úplná spokojenost"
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
    """Generate comments based on actual product features with anti-repetition"""
    comments = []
    
    # Material comments with variety and tracking
    if product_insights['material']:
        material_phrases = {
            'de': {
                'cotton': [
                    'aus Baumwolle und super angenehm', 'Baumwoll-Material fühlt sich toll an', 
                    'Baumwolle ist mega comfortable', 'tolles Baumwoll-Gefühl auf der Haut',
                    'weiche Baumwolle liebt die Haut', 'Baumwolle in bester Qualität'
                ],
                'leather': [
                    'Leder fühlt sich hochwertig an', 'echtes Leder in top Qualität',
                    'Lederverarbeitung ist erstklassig', 'das Leder riecht so gut',
                    'hochwertiges Leder überzeugt total', 'Leder wirkt sehr edel'
                ],
                'lace': [
                    'die Spitze ist wunderschön verarbeitet', 'Spitzen-Details sind ein Traum',
                    'Spitze verleiht den perfect touch', 'edle Spitze macht den Unterschied',
                    'filigrane Spitzenarbeit beeindruckt', 'Spitze sieht richtig teuer aus'
                ],
                'denim': [
                    'Denim Qualität ist top', 'perfekter Jeansstoff mit tollem Fall',
                    'Denim hat die ideale Dicke', 'hochwertiger Jeansstoff überzeugt',
                    'Denim fühlt sich authentisch an', 'klassischer Denim in bester Qualität'
                ],
                'velvet': [
                    'Samt fühlt sich luxuriös an', 'samtweich und total edel',
                    'Velvet bringt Luxus-Feeling', 'Samt-Material ist ein Traum',
                    'weicher Samt strahlt Eleganz aus', 'Samtoberfläche ist butterweich'
                ]
            },
            'en': {
                'cotton': [
                    'cotton feels so comfortable', 'cotton material is amazing quality',
                    'soft cotton against the skin', 'breathable cotton fabric',
                    'premium cotton construction', 'cotton texture is perfect'
                ],
                'leather': [
                    'leather quality is amazing', 'genuine leather feels luxurious',
                    'leather craftsmanship is top-tier', 'leather has that rich smell',
                    'high-quality leather throughout', 'leather looks expensive'
                ],
                'lace': [
                    'lace detailing is gorgeous', 'lace work is intricate and beautiful',
                    'delicate lace adds perfect touch', 'lace pattern is stunning',
                    'fine lace craftsmanship shows', 'lace details elevate the whole piece'
                ],
                'denim': [
                    'denim is perfect weight', 'denim quality exceeds expectations',
                    'substantial denim fabric', 'authentic denim feel',
                    'premium denim construction', 'denim has great structure'
                ],
                'velvet': [
                    'velvet texture is so soft', 'luxurious velvet material',
                    'velvet adds elegance', 'plush velvet finish',
                    'rich velvet texture', 'velvet feels expensive'
                ]
            },
            'pl': {
                'cotton': [
                    'bawełna jest bardzo wygodna', 'materiał bawełniany w super jakości',
                    'miękka bawełna na skórze', 'oddychająca tkanina bawełniana',
                    'premium bawełna zachwyca', 'bawełna ma idealną strukturę'
                ],
                'leather': [
                    'skóra jest wysokiej jakości', 'prawdziwa skóra luksusowa',
                    'rzemiosło skórzane na najwyższym poziomie', 'skóra ma bogaty zapach',
                    'wysokiej jakości skóra wszędzie', 'skóra wygląda drogo'
                ],
                'lace': [
                    'koronka jest pięknie wykonana', 'koronkowa robota jest skomplikowana i piękna',
                    'delikatna koronka dodaje idealny akcent', 'wzór koronki jest oszałamiający',
                    'subtelne rzemiosło koronkowe', 'detale koronkowe podnoszą całość'
                ],
                'denim': [
                    'denim ma idealną wagę', 'jakość denimu przewyższa oczekiwania',
                    'solidna tkanina denim', 'autentyczne uczucie denimu',
                    'premium konstrukcja denim', 'denim ma świetną strukturę'
                ],
                'velvet': [
                    'aksamit jest tak miękki', 'luksusowy materiał aksamitny',
                    'aksamit dodaje elegancji', 'pluszowe wykończenie aksamitne',
                    'bogata tekstura aksamitu', 'aksamit wydaje się drogi'
                ]
            },
            'it': {
                'cotton': [
                    'cotone molto confortevole', 'materiale cotone qualità eccellente',
                    'cotone morbido sulla pelle', 'tessuto cotone traspirante',
                    'cotone premium stupendo', 'cotone texture perfetta'
                ],
                'leather': [
                    'pelle di ottima qualità', 'pelle genuina lussuosa',
                    'lavorazione pelle di alto livello', 'pelle profumo ricco',
                    'pelle alta qualità ovunque', 'pelle sembra costosa'
                ],
                'lace': [
                    'pizzo bellissimo', 'lavorazione pizzo intricata e bella',
                    'pizzo delicato aggiunge tocco perfetto', 'motivo pizzo stupendo',
                    'artigianato pizzo sottile', 'dettagli pizzo elevano tutto'
                ],
                'denim': [
                    'denim peso perfetto', 'qualità denim supera aspettative',
                    'tessuto denim sostanziale', 'sensazione denim autentica',
                    'costruzione denim premium', 'denim struttura ottima'
                ],
                'velvet': [
                    'velluto così morbido', 'materiale velluto lussuoso',
                    'velluto aggiunge eleganza', 'finitura velluto morbida',
                    'texture velluto ricca', 'velluto sembra costoso'
                ]
            },
            'fr': {
                'cotton': [
                    'coton très confortable', 'matériau coton qualité excellente',
                    'coton doux sur la peau', 'tissu coton respirant',
                    'coton premium magnifique', 'coton texture parfaite'
                ],
                'leather': [
                    'cuir de qualité incroyable', 'cuir véritable luxueux',
                    'artisanat cuir haut niveau', 'cuir odeur riche',
                    'cuir haute qualité partout', 'cuir semble cher'
                ],
                'lace': [
                    'dentelle magnifique', 'travail dentelle complexe et beau',
                    'dentelle délicate ajoute touche parfaite', 'motif dentelle époustouflant',
                    'artisanat dentelle fin', 'détails dentelle élèvent tout'
                ],
                'denim': [
                    'denim poids parfait', 'qualité denim dépasse attentes',
                    'tissu denim substantiel', 'sensation denim authentique',
                    'construction denim premium', 'denim excellente structure'
                ],
                'velvet': [
                    'velours si doux', 'matériau velours luxueux',
                    'velours ajoute élégance', 'finition velours moelleuse',
                    'texture velours riche', 'velours semble cher'
                ]
            },
            'es': {
                'cotton': [
                    'algodón muy cómodo', 'material algodón calidad excelente',
                    'algodón suave en la piel', 'tejido algodón transpirable',
                    'algodón premium magnífico', 'algodón textura perfecta'
                ],
                'leather': [
                    'cuero de calidad increíble', 'cuero genuino lujoso',
                    'artesanía cuero alto nivel', 'cuero olor rico',
                    'cuero alta calidad en todo', 'cuero parece caro'
                ],
                'lace': [
                    'encaje hermoso', 'trabajo encaje intrincado y bello',
                    'encaje delicado añade toque perfecto', 'patrón encaje impresionante',
                    'artesanía encaje fino', 'detalles encaje elevan todo'
                ],
                'denim': [
                    'denim peso perfecto', 'calidad denim supera expectativas',
                    'tejido denim sustancial', 'sensación denim auténtica',
                    'construcción denim premium', 'denim excelente estructura'
                ],
                'velvet': [
                    'terciopelo tan suave', 'material terciopelo lujoso',
                    'terciopelo añade elegancia', 'acabado terciopelo suave',
                    'textura terciopelo rica', 'terciopelo parece caro'
                ]
            },
            'cs': {
                'cotton': [
                    'bavlna velmi pohodlná', 'bavlněný materiál vynikající kvality',
                    'bavlna měkká na kůži', 'bavlněná látka prodyšná',
                    'prémiová bavlna nádherná', 'bavlna textura dokonalá'
                ],
                'leather': [
                    'kůže skvělé kvality', 'pravá kůže luxusní',
                    'kožené řemeslo vysoké úrovně', 'kůže bohatá vůně',
                    'vysoká kvalita kůže všude', 'kůže vypadá draho'
                ],
                'lace': [
                    'krajka nádherná', 'krajková práce složitá a krásná',
                    'jemná krajka dodává dokonalý dotek', 'vzor krajky úžasný',
                    'jemné krajkové řemeslo', 'detaily krajky povyšují vše'
                ],
                'denim': [
                    'denim perfektní váha', 'kvalita denim překračuje očekávání',
                    'podstatná džínová látka', 'autentický pocit denim',
                    'prémiová konstrukce denim', 'denim vynikající struktura'
                ],
                'velvet': [
                    'samet tak měkký', 'luxusní sametový materiál',
                    'samet dodává eleganci', 'plyšové sametové povrchová úprava',
                    'bohatá sametová textura', 'samet vypadá draho'
                ]
            }
        }
        
        for material in product_insights['material']:
            lang_phrases = material_phrases.get(language, material_phrases['en'])
            if material in lang_phrases:
                phrase = get_unique_phrase(lang_phrases[material], language, f"material_{material}")
                if phrase:
                    comments.append(phrase)
    
    # Feature comments with variety and tracking
    if product_insights['features']:
        feature_phrases = {
            'de': {
                'pockets': [
                    'Taschen sind praktisch', 'die Taschen sind mega funktional',
                    'praktische Taschen erleichtern alles', 'Taschen perfekt platziert',
                    'genügend Taschen für alles wichtige', 'durchdachte Taschen-Lösung'
                ],
                'zipper': [
                    'Reißverschluss läuft smooth', 'Zipper Qualität überzeugt total',
                    'Reißverschluss funktioniert einwandfrei', 'hochwertiger Zipper verbaut',
                    'Reißverschluss läuft wie Butter', 'stabiler Zipper hält ewig'
                ],
                'hood': [
                    'Kapuze ist perfekt geschnitten', 'Hoodie-Form sitzt ideal',
                    'Kapuze bietet optimalen Schutz', 'Kapuze hat die richtige Größe',
                    'Kapuze fällt schön natürlich', 'durchdachte Kapuzen-Konstruktion'
                ],
                'sleeves': [
                    'Ärmel haben die perfekte Länge', 'Ärmellänge sitzt genau richtig',
                    'Ärmel enden an der idealen Stelle', 'Ärmel-Schnitt überzeugt',
                    'Ärmellänge passt wie angegossen', 'Ärmel sind optimal proportioniert'
                ]
            },
            'en': {
                'pockets': [
                    'pockets are so useful', 'pockets functionality is amazing',
                    'practical pockets make life easier', 'pockets perfectly placed',
                    'enough pockets for all essentials', 'thoughtful pocket design'
                ],
                'zipper': [
                    'zipper quality is great', 'zipper operates smoothly',
                    'zipper works flawlessly', 'high-quality zipper hardware',
                    'zipper glides like butter', 'sturdy zipper built to last'
                ],
                'hood': [
                    'hood fits perfectly', 'hoodie shape sits ideally',
                    'hood provides optimal coverage', 'hood has the right proportions',
                    'hood drapes naturally', 'thoughtful hood construction'
                ],
                'sleeves': [
                    'sleeve length is perfect', 'sleeve length sits just right',
                    'sleeves end at ideal spot', 'sleeve cut is convincing',
                    'sleeve length fits like a glove', 'sleeves optimally proportioned'
                ]
            },
            'pl': {
                'pockets': [
                    'kieszenie są bardzo praktyczne', 'funkcjonalność kieszeni jest niesamowita',
                    'praktyczne kieszenie ułatwiają życie', 'kieszenie idealnie umieszczone',
                    'wystarczająco kieszeni na wszystko', 'przemyślany design kieszeni'
                ],
                'zipper': [
                    'zamek błyskawiczny działa świetnie', 'zamek błyskawiczny działa gładko',
                    'zamek błyskawiczny działa bez zarzutu', 'wysokiej jakości hardware zamka',
                    'zamek ślizga się jak masło', 'mocny zamek zbudowany na lata'
                ],
                'hood': [
                    'kaptur pasuje idealnie', 'kształt bluzy siedzi idealnie',
                    'kaptur zapewnia optymalne pokrycie', 'kaptur ma właściwe proporcje',
                    'kaptur układa się naturalnie', 'przemyślana konstrukcja kaptura'
                ],
                'sleeves': [
                    'długość rękawów jest idealna', 'długość rękawów siedzi w sam raz',
                    'rękawy kończą się w idealnym miejscu', 'krój rękawów przekonuje',
                    'długość rękawów pasuje jak ulał', 'rękawy optymalnie proporcjonalne'
                ]
            },
            'it': {
                'pockets': [
                    'tasche molto utili', 'funzionalità tasche incredibile',
                    'tasche pratiche rendono vita più facile', 'tasche perfettamente posizionate',
                    'abbastanza tasche per tutto essenziale', 'design tasche ponderato'
                ],
                'zipper': [
                    'qualità della cerniera ottima', 'cerniera funziona liscia',
                    'cerniera funziona perfettamente', 'hardware cerniera alta qualità',
                    'cerniera scivola come burro', 'cerniera robusta costruita per durare'
                ],
                'hood': [
                    'cappuccio veste perfettamente', 'forma felpa siedeidealmente',
                    'cappuccio fornisce copertura ottimale', 'cappuccio ha proporzioni giuste',
                    'cappuccio cade naturalmente', 'costruzione cappuccio ponderata'
                ],
                'sleeves': [
                    'lunghezza maniche perfetta', 'lunghezza maniche siede giusto',
                    'maniche finiscono punto ideale', 'taglio maniche convincente',
                    'lunghezza maniche calza guanto', 'maniche ottimamente proporzionate'
                ]
            },
            'fr': {
                'pockets': [
                    'poches très utiles', 'fonctionnalité poches incroyable',
                    'poches pratiques facilitent vie', 'poches parfaitement placées',
                    'assez poches pour tout essentiel', 'design poches réfléchi'
                ],
                'zipper': [
                    'qualité de la fermeture éclair excellente', 'fermeture éclair fonctionne lisse',
                    'fermeture éclair fonctionne parfaitement', 'hardware fermeture éclair haute qualité',
                    'fermeture éclair glisse comme beurre', 'fermeture éclair robuste construite durer'
                ],
                'hood': [
                    'capuche s\'ajuste parfaitement', 'forme sweat siège idéalement',
                    'capuche fournit couverture optimale', 'capuche a bonnes proportions',
                    'capuche tombe naturellement', 'construction capuche réfléchie'
                ],
                'sleeves': [
                    'longueur des manches parfaite', 'longueur manches siège juste',
                    'manches finissent endroit idéal', 'coupe manches convaincante',
                    'longueur manches ajuste gant', 'manches optimalement proportionnées'
                ]
            },
            'es': {
                'pockets': [
                    'bolsillos muy útiles', 'funcionalidad bolsillos increíble',
                    'bolsillos prácticos facilitan vida', 'bolsillos perfectamente ubicados',
                    'suficientes bolsillos para todo esencial', 'diseño bolsillos considerado'
                ],
                'zipper': [
                    'calidad de la cremallera excelente', 'cremallera funciona suave',
                    'cremallera funciona perfectamente', 'hardware cremallera alta calidad',
                    'cremallera desliza como mantequilla', 'cremallera robusta construida durar'
                ],
                'hood': [
                    'capucha ajusta perfectamente', 'forma sudadera sienta idealmente',
                    'capucha proporciona cobertura óptima', 'capucha tiene proporciones correctas',
                    'capucha cae naturalmente', 'construcción capucha considerada'
                ],
                'sleeves': [
                    'longitud de mangas perfecta', 'longitud mangas sienta justo',
                    'mangas terminan lugar ideal', 'corte mangas convincente',
                    'longitud mangas ajusta guante', 'mangas óptimamente proporcionadas'
                ]
            },
            'cs': {
                'pockets': [
                    'kapsy velmi praktické', 'funkcionalita kapes neuvěřitelná',
                    'praktické kapsy usnadňují život', 'kapsy dokonale umístěné',
                    'dostatek kapes pro vše podstatné', 'promyšlený design kapes'
                ],
                'zipper': [
                    'kvalita zipu vynikající', 'zip funguje hladce',
                    'zip funguje bezchybně', 'hardware zip vysoká kvalita',
                    'zip klouzá jako máslo', 'robustní zip postavený vydržet'
                ],
                'hood': [
                    'kapuce sedí dokonale', 'tvar mikiny sedí ideálně',
                    'kapuce poskytuje optimální pokrytí', 'kapuce má správné proporce',
                    'kapuce padá přirozeně', 'promyšlená konstrukce kapuce'
                ],
                'sleeves': [
                    'délka rukávů perfektní', 'délka rukávů sedí správně',
                    'rukávy končí ideálním místě', 'střih rukávů přesvědčivý',
                    'délka rukávů sedí jako rukavice', 'rukávy optimálně proporcionální'
                ]
            }
        }
        
        for feature in product_insights['features']:
            lang_phrases = feature_phrases.get(language, feature_phrases['en'])
            if feature in lang_phrases:
                phrase = get_unique_phrase(lang_phrases[feature], language, f"feature_{feature}")
                if phrase:
                    comments.append(phrase)
    
    # Style comments with variety and tracking  
    if product_insights['style']:
        style_phrases = {
            'de': {
                'gothic': [
                    'der Gothic Style ist genau mein Ding', 'Gothic Ästhetik trifft meinen Geschmack',
                    'düstere Eleganz überzeugt total', 'Gothic Vibe ist authentisch dark',
                    'perfekte Gothic Atmosphäre eingefangen', 'dark aesthetic passt perfect zu mir'
                ],
                'punk': [
                    'Punk Vibe ist authentisch', 'echter Punk Spirit spürbar',
                    'rebellische Energie strahlt aus', 'Punk Ästhetik on point',
                    'raw punk attitude eingefangen', 'underground Feeling perfekt getroffen'
                ],
                'vintage': [
                    'Vintage Look ist zeitlos', 'retro Charme überzeugt',
                    'nostalgischer Vibe trifft genau', 'vintage Ästhetik perfekt umgesetzt',
                    'klassischer vintage spirit', 'zeitlose Eleganz eingefangen'
                ],
                'elegant': [
                    'elegant und raffiniert', 'sophisticated und stilvoll',
                    'edle Ausstrahlung guaranteed', 'klassische Eleganz überzeugt',
                    'zeitlos elegant designed', 'noble Ästhetik perfect'
                ]
            },
            'en': {
                'gothic': [
                    'gothic aesthetic is perfect', 'gothic vibe hits different',
                    'dark elegance captured beautifully', 'authentic gothic atmosphere',
                    'gothic mood perfectly executed', 'dark aesthetic speaks to my soul'
                ],
                'punk': [
                    'punk vibe is authentic', 'real punk spirit shines through',
                    'rebellious energy radiates', 'punk aesthetic on point',
                    'raw punk attitude captured', 'underground feeling perfectly hit'
                ],
                'vintage': [
                    'vintage style is timeless', 'retro charm convinces',
                    'nostalgic vibe hits exactly', 'vintage aesthetic perfectly executed',
                    'classic vintage spirit', 'timeless elegance captured'
                ],
                'elegant': [
                    'elegant and classy', 'sophisticated and stylish',
                    'refined aura guaranteed', 'classic elegance convinces',
                    'timelessly elegant designed', 'noble aesthetic perfect'
                ]
            },
            'pl': {
                'gothic': [
                    'gotycki styl jest idealny', 'gotycki klimat trafia inaczej',
                    'mroczna elegancja pięknie uchwycona', 'autentyczna gotycka atmosfera',
                    'gotycki nastrój perfekcyjnie wykonany', 'mroczna estetyka przemawia do duszy'
                ],
                'punk': [
                    'punkowy klimat jest autentyczny', 'prawdziwy duch punk świeci',
                    'buntownicza energia promieniuje', 'estetyka punk na miejscu',
                    'surowa postawa punk uchwycona', 'podziemne uczucie idealnie trafione'
                ],
                'vintage': [
                    'vintage styl jest ponadczasowy', 'retro urok przekonuje',
                    'nostalgiczny klimat trafia dokładnie', 'vintage estetyka perfekcyjnie wykonana',
                    'klasyczny vintage duch', 'ponadczasowa elegancja uchwycona'
                ],
                'elegant': [
                    'elegancki i stylowy', 'wyrafinowany i stylowy',
                    'wyrafinowana aura gwarantowana', 'klasyczna elegancja przekonuje',
                    'ponadczasowo elegancko zaprojektowany', 'szlachetna estetyka idealna'
                ]
            },
            'it': {
                'gothic': [
                    'estetica gotica è perfetta', 'vibe gotico colpisce diversamente',
                    'eleganza oscura catturata bellamente', 'atmosfera gotica autentica',
                    'umore gotico perfettamente eseguito', 'estetica oscura parla anima'
                ],
                'punk': [
                    'vibe punk è autentico', 'vero spirito punk risplende',
                    'energia ribelle irradia', 'estetica punk sul punto',
                    'atteggiamento punk crudo catturato', 'sensazione underground perfettamente colpita'
                ],
                'vintage': [
                    'stile vintage è senza tempo', 'fascino retro convince',
                    'vibe nostalgico colpisce esattamente', 'estetica vintage perfettamente eseguita',
                    'spirito vintage classico', 'eleganza senza tempo catturata'
                ],
                'elegant': [
                    'elegante e di classe', 'sofisticato e elegante',
                    'aura raffinata garantita', 'eleganza classica convince',
                    'elegantemente senza tempo progettato', 'estetica nobile perfetta'
                ]
            },
            'fr': {
                'gothic': [
                    'esthétique gothique est parfaite', 'vibe gothique frappe différemment',
                    'élégance sombre capturée magnifiquement', 'atmosphère gothique authentique',
                    'humeur gothique parfaitement exécutée', 'esthétique sombre parle âme'
                ],
                'punk': [
                    'vibe punk est authentique', 'vrai esprit punk brille',
                    'énergie rebelle rayonne', 'esthétique punk sur point',
                    'attitude punk brute capturée', 'sensation underground parfaitement frappée'
                ],
                'vintage': [
                    'style vintage est intemporel', 'charme rétro convainc',
                    'vibe nostalgique frappe exactement', 'esthétique vintage parfaitement exécutée',
                    'esprit vintage classique', 'élégance intemporelle capturée'
                ],
                'elegant': [
                    'élégant et chic', 'sophistiqué et élégant',
                    'aura raffinée garantie', 'élégance classique convainc',
                    'élégamment intemporel conçu', 'esthétique noble parfaite'
                ]
            },
            'es': {
                'gothic': [
                    'estética gótica es perfecta', 'vibe gótico golpea diferente',
                    'elegancia oscura capturada hermosamente', 'atmósfera gótica auténtica',
                    'estado ánimo gótico perfectamente ejecutado', 'estética oscura habla alma'
                ],
                'punk': [
                    'vibe punk es auténtico', 'verdadero espíritu punk brilla',
                    'energía rebelde irradia', 'estética punk en punto',
                    'actitud punk cruda capturada', 'sensación underground perfectamente golpeada'
                ],
                'vintage': [
                    'estilo vintage es atemporal', 'encanto retro convence',
                    'vibe nostálgico golpea exactamente', 'estética vintage perfectamente ejecutada',
                    'espíritu vintage clásico', 'elegancia atemporal capturada'
                ],
                'elegant': [
                    'elegante y con clase', 'sofisticado y elegante',
                    'aura refinada garantizada', 'elegancia clásica convence',
                    'elegantemente atemporal diseñado', 'estética noble perfecta'
                ]
            },
            'cs': {
                'gothic': [
                    'gotický styl je perfektní', 'gotický vibe zasahuje jinak',
                    'temná elegance krásně zachycena', 'autentická gotická atmosféra',
                    'gotická nálada dokonale provedena', 'temná estetika mluví k duši'
                ],
                'punk': [
                    'punkový vibe je autentický', 'skutečný punk duch svítí',
                    'rebelská energie vyzařuje', 'punk estetika na místě',
                    'surový punk postoj zachycen', 'underground pocit dokonale zasažen'
                ],
                'vintage': [
                    'vintage styl je nadčasový', 'retro kouzlo přesvědčuje',
                    'nostalgický vibe zasahuje přesně', 'vintage estetika dokonale provedena',
                    'klasický vintage duch', 'nadčasová elegance zachycena'
                ],
                'elegant': [
                    'elegantní a stylový', 'sofistikovaný a stylový',
                    'rafinovaná aura zaručena', 'klasická elegance přesvědčuje',
                    'nadčasově elegantně navrženo', 'ušlechtilá estetika dokonalá'
                ]
            }
        }
        
        for style in product_insights['style']:
            lang_phrases = style_phrases.get(language, style_phrases['en'])
            if style in lang_phrases:
                phrase = get_unique_phrase(lang_phrases[style], language, f"style_{style}")
                if phrase:
                    comments.append(phrase)
    
    # Fit comments with variety and tracking
    if product_insights['fit']:
        fit_phrases = {
            'de': {
                'oversized': [
                    'oversized Fit ist mega gemütlich', 'lockerer Schnitt sitzt perfekt',
                    'oversized Style bringt Komfort', 'weiter Schnitt ist so bequem',
                    'relaxed Fit ist super bequem', 'oversized Schnitt ist perfekt'
                ],
                'fitted': [
                    'tailliert und schmeichelt der Figur', 'enger Schnitt betont Silhouette',
                    'figurbetont und mega schmeichelnd', 'perfekt anliegend geschnitten',
                    'körpernah und vorteilhaft', 'fitted Style zeigt tolle Form'
                ],
                'stretchy': [
                    'Material ist schön dehnbar', 'elastischer Stoff gibt nach',
                    'stretch Material bewegt sich mit', 'dehnbares Gewebe ist angenehm',
                    'flexible Materialien überzeugen', 'stretch Eigenschaft ist perfekt'
                ],
                'comfortable': [
                    'unglaublich bequem zu tragen', 'so comfortable den ganzen Tag',
                    'mega gemütlich und weich', 'trägt sich wie eine zweite Haut',
                    'comfort Level ist outstanding', 'bequemer geht es nicht'
                ]
            },
            'en': {
                'oversized': [
                    'oversized fit is so comfy', 'loose cut fits perfectly',
                    'oversized style brings comfort', 'relaxed fit feels amazing',
                    'roomy fit accommodates everything', 'oversized silhouette works great'
                ],
                'fitted': [
                    'fitted perfectly to my body', 'snug cut emphasizes silhouette',
                    'form-fitting and flattering', 'perfectly contoured design',
                    'body-hugging and advantageous', 'fitted style shows great shape'
                ],
                'stretchy': [
                    'material has great stretch', 'elastic fabric gives flexibility',
                    'stretch material moves with you', 'stretchable fabric feels nice',
                    'flexible materials convince', 'stretch property is perfect'
                ],
                'comfortable': [
                    'incredibly comfortable to wear', 'so comfortable all day long',
                    'extremely cozy and soft', 'wears like a second skin',
                    'comfort level is outstanding', 'can\'t get more comfortable'
                ]
            },
            'pl': {
                'oversized': [
                    'oversized krój jest bardzo wygodny', 'luźny krój pasuje idealnie',
                    'oversized styl zapewnia komfort', 'relaxed fit czuje się niesamowicie',
                    'przestronny krój pomieści wszystko', 'oversized sylwetka działa świetnie'
                ],
                'fitted': [
                    'dopasowany idealnie do ciała', 'obcisły krój podkreśla sylwetkę',
                    'dopasowany i schlebiający', 'perfekcyjnie wyprofilowany design',
                    'przylegający do ciała i korzystny', 'dopasowany styl pokazuje świetny kształt'
                ],
                'stretchy': [
                    'materiał ma świetną elastyczność', 'elastyczna tkanina daje elastyczność',
                    'stretch materiał porusza się z tobą', 'rozciągliwa tkanina jest miła',
                    'elastyczne materiały przekonują', 'właściwość stretch jest idealna'
                ],
                'comfortable': [
                    'niesamowicie wygodny do noszenia', 'tak wygodny przez cały dzień',
                    'bardzo przytulny i miękki', 'nosi się jak druga skóra',
                    'poziom komfortu jest wspaniały', 'nie może być wygodniej'
                ]
            },
            'it': {
                'oversized': [
                    'vestibilità oversized è comoda', 'taglio largo veste perfettamente',
                    'stile oversized porta comfort', 'vestibilità rilassata è incredibile',
                    'taglio spazioso accoglie tutto', 'silhouette oversized funziona benissimo'
                ],
                'fitted': [
                    'aderente perfettamente al corpo', 'taglio aderente enfatizza silhouette',
                    'aderente e lusinghiero', 'design perfettamente sagomato',
                    'aderente al corpo e vantaggioso', 'stile aderente mostra forma ottima'
                ],
                'stretchy': [
                    'materiale ha ottima elasticità', 'tessuto elastico dà flessibilità',
                    'materiale stretch si muove con te', 'tessuto estensibile è piacevole',
                    'materiali flessibili convincono', 'proprietà stretch è perfetta'
                ],
                'comfortable': [
                    'incredibilmente comodo da indossare', 'così comodo tutto il giorno',
                    'estremamente accogliente e morbido', 'indossa come seconda pelle',
                    'livello comfort è eccezionale', 'non può essere più comodo'
                ]
            },
            'fr': {
                'oversized': [
                    'coupe oversized est confortable', 'coupe ample s\'ajuste parfaitement',
                    'style oversized apporte confort', 'coupe décontractée est incroyable',
                    'coupe spacieuse accueille tout', 'silhouette oversized fonctionne très bien'
                ],
                'fitted': [
                    'ajusté parfaitement au corps', 'coupe ajustée met en valeur silhouette',
                    'ajusté et flatteur', 'design parfaitement galbé',
                    'près du corps et avantageux', 'style ajusté montre belle forme'
                ],
                'stretchy': [
                    'matériau a une grande élasticité', 'tissu élastique donne flexibilité',
                    'matériau stretch bouge avec vous', 'tissu extensible est agréable',
                    'matériaux flexibles convainquent', 'propriété stretch est parfaite'
                ],
                'comfortable': [
                    'incroyablement confortable à porter', 'si confortable toute la journée',
                    'extrêmement douillet et doux', 'porte comme seconde peau',
                    'niveau confort est exceptionnel', 'ne peut pas être plus confortable'
                ]
            },
            'es': {
                'oversized': [
                    'ajuste oversized es cómodo', 'corte holgado ajusta perfectamente',
                    'estilo oversized trae comodidad', 'ajuste relajado es increíble',
                    'corte espacioso acomoda todo', 'silueta oversized funciona genial'
                ],
                'fitted': [
                    'ajustado perfectamente al cuerpo', 'corte ajustado enfatiza silueta',
                    'ajustado y favorecedor', 'diseño perfectamente contorneado',
                    'pegado al cuerpo y ventajoso', 'estilo ajustado muestra forma genial'
                ],
                'stretchy': [
                    'material tiene gran elasticidad', 'tela elástica da flexibilidad',
                    'material stretch se mueve contigo', 'tela extensible es agradable',
                    'materiales flexibles convencen', 'propiedad stretch es perfecta'
                ],
                'comfortable': [
                    'increíblemente cómodo de usar', 'tan cómodo todo el día',
                    'extremadamente acogedor y suave', 'se usa como segunda piel',
                    'nivel comodidad es excepcional', 'no puede ser más cómodo'
                ]
            },
            'cs': {
                'oversized': [
                    'oversized střih je pohodlný', 'volný střih sedí dokonale',
                    'oversized styl přináší pohodlí', 'relaxed střih je neuvěřitelný',
                    'prostorný střih pojme všechno', 'oversized silueta funguje skvěle'
                ],
                'fitted': [
                    'přiléhavý dokonale k tělu', 'těsný střih zdůrazňuje siluetu',
                    'přiléhavý a lichotivý', 'dokonale tvarovaný design',
                    'těsně k tělu a výhodný', 'přiléhavý styl ukazuje skvělý tvar'
                ],
                'stretchy': [
                    'materiál má skvělou pružnost', 'elastická látka dává flexibilitu',
                    'stretch materiál se pohybuje s vámi', 'roztažitelná látka je příjemná',
                    'flexibilní materiály přesvědčují', 'vlastnost stretch je dokonalá'
                ],
                'comfortable': [
                    'neuvěřitelně pohodlný na nošení', 'tak pohodlný celý den',
                    'extrémně útulný a měkký', 'nosí se jako druhá kůže',
                    'úroveň pohodlí je výjimečná', 'nemůže být pohodlnější'
                ]
            }
        }
        
        for fit in product_insights['fit']:
            lang_phrases = fit_phrases.get(language, fit_phrases['en'])
            if fit in lang_phrases:
                phrase = get_unique_phrase(lang_phrases[fit], language, f"fit_{fit}")
                if phrase:
                    comments.append(phrase)
    
    # Occasion comments with variety and tracking
    if product_insights['occasions']:
        occasion_phrases = {
            'de': {
                'party': [
                    'perfekt für Partys', 'ideal zum Feiern',
                    'party-ready und stylish', 'macht auf jeder Party eine gute Figur',
                    'Clubbing Outfit complete', 'für Events einfach perfect'
                ],
                'casual': [
                    'ideal für den Alltag', 'perfekt für jeden Tag',
                    'casual Style on point', 'everyday Look guaranteed',
                    'alltagstauglich und bequem', 'für entspannte Tage ideal'
                ],
                'date': [
                    'super für Dates', 'date night ready',
                    'romantic Look achieved', 'für romantische Abende perfect',
                    'date Outfit approved', 'macht Eindruck beim Date'
                ],
                'work': [
                    'auch fürs Büro geeignet', 'business casual approved',
                    'workplace appropriate', 'für die Arbeit totally fine',
                    'office Look möglich', 'professional und stylish'
                ]
            },
            'en': {
                'party': [
                    'perfect for parties', 'ideal for celebrations',
                    'party-ready and stylish', 'makes great impression at parties',
                    'clubbing outfit complete', 'event-ready and gorgeous'
                ],
                'casual': [
                    'great for everyday wear', 'perfect for daily use',
                    'casual style on point', 'everyday look guaranteed',
                    'suitable for daily activities', 'ideal for relaxed days'
                ],
                'date': [
                    'amazing for date nights', 'date night ready',
                    'romantic look achieved', 'perfect for romantic evenings',
                    'date outfit approved', 'makes impression on dates'
                ],
                'work': [
                    'works for office too', 'business casual approved',
                    'workplace appropriate', 'totally fine for work',
                    'office look possible', 'professional and stylish'
                ]
            },
            'pl': {
                'party': [
                    'idealne na imprezy', 'idealne na celebrację',
                    'gotowe na imprezę i stylowe', 'robi świetne wrażenie na imprezach',
                    'strój na clubbing kompletny', 'gotowe na wydarzenia i wspaniałe'
                ],
                'casual': [
                    'świetne na co dzień', 'idealne do codziennego użytku',
                    'casual styl na miejscu', 'codzienny look gwarantowany',
                    'odpowiednie na codzienne aktywności', 'idealne na spokojne dni'
                ],
                'date': [
                    'super na randki', 'gotowe na randkę',
                    'romantyczny look osiągnięty', 'idealne na romantyczne wieczory',
                    'strój na randkę zatwierdzony', 'robi wrażenie na randkach'
                ],
                'work': [
                    'sprawdza się też w pracy', 'biznes casual zatwierdzone',
                    'odpowiednie do miejsca pracy', 'całkowicie w porządku do pracy',
                    'biurowy look możliwy', 'profesjonalne i stylowe'
                ]
            },
            'it': {
                'party': [
                    'perfetto per le feste', 'ideale per celebrazioni',
                    'pronto per la festa e stiloso', 'fa ottima impressione alle feste',
                    'outfit clubbing completo', 'pronto per eventi e stupendo'
                ],
                'casual': [
                    'ottimo per tutti i giorni', 'perfetto per uso quotidiano',
                    'stile casual centrato', 'look quotidiano garantito',
                    'adatto per attività quotidiane', 'ideale per giorni rilassati'
                ],
                'date': [
                    'fantastico per gli appuntamenti', 'pronto per appuntamento',
                    'look romantico raggiunto', 'perfetto per serate romantiche',
                    'outfit appuntamento approvato', 'fa impressione agli appuntamenti'
                ],
                'work': [
                    'va bene anche per l\'ufficio', 'business casual approvato',
                    'appropriato per posto lavoro', 'totalmente bene per lavoro',
                    'look ufficio possibile', 'professionale e stiloso'
                ]
            },
            'fr': {
                'party': [
                    'parfait pour les fêtes', 'idéal pour célébrations',
                    'prêt pour fête et stylé', 'fait excellente impression aux fêtes',
                    'tenue clubbing complète', 'prêt pour événements et magnifique'
                ],
                'casual': [
                    'excellent pour tous les jours', 'parfait pour usage quotidien',
                    'style décontracté au point', 'look quotidien garanti',
                    'approprié pour activités quotidiennes', 'idéal pour jours détendus'
                ],
                'date': [
                    'génial pour les rendez-vous', 'prêt pour rendez-vous',
                    'look romantique atteint', 'parfait pour soirées romantiques',
                    'tenue rendez-vous approuvée', 'fait impression aux rendez-vous'
                ],
                'work': [
                    'convient aussi au bureau', 'business décontracté approuvé',
                    'approprié pour lieu travail', 'totalement bien pour travail',
                    'look bureau possible', 'professionnel et stylé'
                ]
            },
            'es': {
                'party': [
                    'perfecto para fiestas', 'ideal para celebraciones',
                    'listo para fiesta y estiloso', 'hace gran impresión en fiestas',
                    'outfit clubbing completo', 'listo para eventos y hermoso'
                ],
                'casual': [
                    'genial para el día a día', 'perfecto para uso diario',
                    'estilo casual en punto', 'look cotidiano garantizado',
                    'apropiado para actividades diarias', 'ideal para días relajados'
                ],
                'date': [
                    'increíble para citas', 'listo para cita',
                    'look romántico logrado', 'perfecto para noches románticas',
                    'outfit cita aprobado', 'hace impresión en citas'
                ],
                'work': [
                    'funciona para la oficina también', 'business casual aprobado',
                    'apropiado para lugar trabajo', 'totalmente bien para trabajo',
                    'look oficina posible', 'profesional y estiloso'
                ]
            },
            'cs': {
                'party': [
                    'perfektní na večírky', 'ideální na oslavy',
                    'připraveno na párty a stylové', 'dělá skvělý dojem na večírcích',
                    'clubbing outfit kompletní', 'připraveno na události a nádherné'
                ],
                'casual': [
                    'skvělé na každý den', 'perfektní pro denní použití',
                    'casual styl na místě', 'každodenní look zaručený',
                    'vhodné pro denní aktivity', 'ideální pro uvolněné dny'
                ],
                'date': [
                    'úžasné na rande', 'připraveno na rande',
                    'romantický look dosažen', 'perfektní pro romantické večery',
                    'rande outfit schváleno', 'dělá dojem na randích'
                ],
                'work': [
                    'hodí se i do kanceláře', 'business casual schváleno',
                    'vhodné pro pracoviště', 'zcela v pořádku pro práci',
                    'kancelářský look možný', 'profesionální a stylové'
                ]
            }
        }
        
        for occasion in product_insights['occasions']:
            lang_phrases = occasion_phrases.get(language, occasion_phrases['en'])
            if occasion in lang_phrases:
                phrase = get_unique_phrase(lang_phrases[occasion], language, f"occasion_{occasion}")
                if phrase:
                    comments.append(phrase)
    
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
    
    # Location based on real Shopify ORDER data (only languages with full translations)
    locations = {
        "de": ["DE", "DE", "DE", "DE", "DE", "AT", "CH"],  # German speakers
        "pl": ["PL", "PL", "PL"],  # Polish speakers  
        "en": ["US", "US", "US", "UK", "UK", "CA", "AU", "NZ", "IE"],  # English speakers
        "it": ["IT", "IT", "IT", "IT"],  # Italian speakers
        "fr": ["FR", "FR", "BE", "CH", "MC"],  # French speakers
        "es": ["ES", "ES", "MX", "AR"],  # Spanish speakers
        "cs": ["CZ", "CZ", "SK"]  # Czech/Slovak speakers (similar languages)
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
                    connectors = [". ", "! ", ", ", " - ", " und ", ". Dazu ", "!! ", "... "]
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
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤"]
                elif language == "de":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤"]
                elif language == "pl":
                    endings = ["!!!", "!!", "!", "...", "💖", "✨", "🔥", "👌", "💯", "🖤"]
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
    """Select language based on real Shopify ORDER data (only languages with full translations)"""
    # Focus on languages with complete translations: DE, PL, EN, IT, FR, ES, CS
    # Redistribute the remaining percentages to these core languages
    languages = ["de", "pl", "en", "it", "fr", "es", "cs"]
    
    # Adjusted weights to total 100% across translated languages
    # Original: 37% DE, 11% PL, 13% EN, 6% IT, 2% FR, 2% ES, 2% CS = 73%
    # Redistributed remaining 27% proportionally
    weights = [42, 13, 16, 8, 6, 6, 9]  # Totals 100%
    
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
        
        # Map location to language (only languages with full translations)
        location_language_map = {
            'de': 'de', 'at': 'de', 'ch': 'de',
            'pl': 'pl', 
            'cz': 'cs', 'sk': 'cs',
            'it': 'it',
            'fr': 'fr', 'be': 'fr', 'mc': 'fr',
            'es': 'es', 'mx': 'es', 'ar': 'es',
            'us': 'en', 'uk': 'en', 'ca': 'en', 'au': 'en', 'nz': 'en', 'ie': 'en'
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
        'de': 42, 'pl': 13, 'en': 16, 'it': 8, 'fr': 6, 'es': 6, 'cs': 9
    }
    
    print(f"{'Language':<10} {'Expected':<10} {'Actual':<10} {'Diff':<10}")
    print("-" * 40)
    for lang in ['de', 'pl', 'en', 'it', 'cs', 'fr', 'es']:
        expected = expected_distribution.get(lang, 0)
        actual = language_counts.get(lang, 0)
        diff = actual - expected
        print(f"{lang:<10} {expected:<10} {actual:<10} {diff:+<10}")
    
    return results