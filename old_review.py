import csv
import random
from datetime import datetime, timedelta
import re
import os
from faker import Faker

# Initialisieren der Faker-Library für mehrere Regionen
fake_de = Faker('de_DE')
fake_en = Faker('en_US')
fake_pl = Faker('pl_PL')
fake_ru = Faker('ru_RU')

# Listen mit möglichen Bewertungstiteln nach Sprache und Bewertungszahl
review_titles = {
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
    },
    "pl": {
        5: [
            "Absolutnie fantastyczny!", "Idealny produkt!", "Kocham to!", "Przekracza wszystkie oczekiwania!",
            "Po prostu cudowny!", "Trzeba mieć!", "Polecam!", "Najlepszy produkt!",
            "Pierwszorzędna jakość!", "Uwielbiam!", "Wspaniały wybór!", "Super rzecz!"
        ],
        4: [
            "Bardzo dobry produkt", "Prawie idealny", "Naprawdę ładny", "Bardzo zadowolony",
            "Dobra jakość", "Robi dobre wrażenie", "Godny polecenia", "Pozytywnie zaskoczony",
            "Świetny zakup", "Dobra wartość", "Piękny design"
        ],
        3: [
            "W porządku", "Spełnia swoje zadanie", "Ogólnie zadowolony", "Przeciętny",
            "Spełnia oczekiwania", "Niezły", "Mógłby być lepszy"
        ],
    },
    "ru": {
        5: [
            "Абсолютно потрясающе!", "Идеальный продукт!", "Обожаю это!", "Превосходит все ожидания!",
            "Просто замечательно!", "Обязательно иметь!", "Очень рекомендую!", "Лучший продукт!",
            "Первоклассное качество!", "Люблю это!", "Отличный выбор!"
        ],
        4: [
            "Очень хороший продукт", "Почти идеально", "Действительно красиво", "Очень доволен",
            "Хорошее качество", "Производит отличное впечатление", "Рекомендую", "Приятно удивлен",
            "Отличная покупка", "Хорошее соотношение цены и качества"
        ],
        3: [
            "Неплохо", "Служит своей цели", "В целом доволен", "Средний",
            "Соответствует ожиданиям", "Неплохо", "Могло быть лучше"
        ],
    }
}

# Variablen für Shop-Bezug, Social Media und mehr
shop_references = {
    "de": [
        "Fuga Studios rockt einfach", "wieder mal bei Fuga zugeschlagen", "meine dritte Bestellung bei Fuga",
        "Fuga nie enttäuscht", "Fuga Studios ist mein go-to shop", "für Festival-Outfits ist Fuga unschlagbar",
        "Fuga kennt einfach den vibe", "Fuga versteht alternative fashion", "seit ich Fuga entdeckt hab kauf ich nix anderes mehr"
    ],
    "en": [
        "Fuga Studios rocks", "hit up Fuga again", "my third Fuga haul",
        "Fuga never disappoints", "Fuga Studios is my go-to", "for festival fits Fuga is unmatched",
        "Fuga just gets the vibe", "Fuga understands alt fashion", "since finding Fuga I don't shop anywhere else"
    ],
    "pl": [
        "Fuga Studios nigdy nie zawodzi", "kolejne zamówienie z Fuga", "Fuga rozumie alternatywną modę"
    ],
    "ru": [
        "Fuga Studios никогда не разочаровывает", "очередной заказ из Fuga", "Fuga понимает альтернативную моду"
    ]
}

social_media_refs = {
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
    ],
    "pl": [
        "zobaczyłam na TikToku i od razu zamówiłam", "idealne do zdjęć na Instagram"
    ],
    "ru": [
        "увидела в ТикТоке и сразу заказала", "идеально для фото в Инстаграм"
    ]
}

shipping_comments = {
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
    ],
    "pl": [
        "dostawa była szybsza niż się spodziewałam", "przesyłka dotarła w zaledwie 2 dni"
    ],
    "ru": [
        "доставка была быстрее, чем ожидалось", "посылка пришла всего за 2 дня"
    ]
}

# Kurze Review-Varianten (für authentische Ein-Satz-Reviews)
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
    ],
    "pl": [
        "totalnie zakochana!!!", "natychmiast kupiłam!", "wygląda lepiej niż na zdjęciach", "obsesja kompletna!!!", 
        "idealne do klubu", "fuga studios zawsze daje radę", "przesyłka super szybka", "muszę mieć więcej takich rzeczy", 
        "pasuje do wszystkiego", "komplimenty murowane", "obserwuję fuga na insta i w końcu kupiłam", "estetyka 10/10",
        "wyróżniam się w tym totalnie", "nie mogę się doczekać kolejnej imprezy"
    ],
    "ru": [
        "просто одержима!!!", "сразу купила!", "выглядит лучше чем на фото", "полная обсессия!!!", 
        "идеально для клуба", "fuga studios всегда топ", "доставка супер быстрая", "нужно больше таких вещей", 
        "сочетается со всем", "комплименты гарантированы", "слежу за fuga в инсте и наконец купила", "эстетика 10/10",
        "выделяюсь в этом", "не могу дождаться следующей вечеринки"
    ]
}

# Variationen für das Review-Ende nach Sprache
review_endings = {
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
    },
    "pl": {
        5: [
            "Gorąco polecam!", 
            "Na pewno zamówię ponownie!", 
            "Jedno z moich ulubionych!",
            "Całkowicie zadowolony!",
            "Zdecydowanie warto kupić!",
            "Absolutny faworyt w mojej garderobie!",
            "Kupiłbym to ponownie bez wahania!"
        ],
        4: [
            "Mogę polecić.", 
            "Bardzo zadowolony z zakupu.", 
            "Dobry zakup.",
            "Kupiłbym ponownie.",
            "Sprawia wrażenie jakościowego.",
            "Zadowolony z mojego wyboru.",
            "Dobrze spełnia swoje zadanie."
        ],
        3: [
            "W porządku za tę cenę.", 
            "Spełnia swoje zadanie.", 
            "Nie idealne, ale używalne.",
            "Mogłoby być lepsze w niektórych aspektach.",
            "W porządku do okazjonalnego noszenia.",
            "Ani szczególnie dobre, ani złe.",
            "Ani zachwycony, ani rozczarowany."
        ]
    },
    "ru": {
        5: [
            "Очень рекомендую!", 
            "Обязательно закажу снова!", 
            "Одна из моих любимых вещей!",
            "Полностью удовлетворен!",
            "Определенно стоит купить!",
            "Абсолютный фаворит в моем гардеробе!",
            "Купил бы это снова не раздумывая!"
        ],
        4: [
            "Могу рекомендовать.", 
            "Очень доволен покупкой.", 
            "Хорошая покупка.",
            "Купил бы снова.",
            "Производит качественное впечатление.",
            "Доволен своим выбором.",
            "Хорошо выполняет свою функцию."
        ],
        3: [
            "Нормально за эту цену.", 
            "Выполняет свою задачу.", 
            "Не идеально, но пригодно.",
            "Могло бы быть лучше в некоторых аспектах.",
            "Нормально для случайной носки.",
            "Ни особенно хорошо, ни плохо.",
            "Ни в восторге, ни разочарован."
        ]
    }
}

# Phrasen für verschiedene Produkttypen und Eigenschaften nach Sprache
product_phrases = {
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
            "harmoniert mit meinen platforms"
        ],
        "punk": [
            "hardcore punk vibes ohne try hard", 
            "rebellious energy aber trotzdem tragbar", 
            "outfit-maker piece",
            "perfekt für konzerte und moshpits",
            "details geben dem ganzen den edge",
            "mein go-to für jedes punk event",
            "passt zu meinen docs und ketten"
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
            "works for both daytime and nightlife"
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
            "distressing is done just right"
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
    },
    "pl": {
        "tops": [
            "pasuje do całej mojej szafy", 
            "krój jest mega pochlebny", 
            "materiał lepszy niż się spodziewałam",
            "jakość lepsza niż drogie sieciówki",
            "kolor żywszy na żywo",
            "wykonanie perfekcyjne",
            "ciągle dostaję komplementy",
            "styl totalnie w moim klimacie",
            "od razu wrzuciłam zdjęcia na insta",
            "nosi się bardzo wygodnie",
            "materiał miękki ale nie prześwituje",
            "detal przy dekolcie super oryginalny"
        ],
        "bottoms": [
            "leży jak druga skóra", 
            "najwygodniejsza rzecz ever", 
            "długość idealna do mojego wzrostu",
            "elastyczność na wysokim poziomie",
            "kieszenie wystarczająco głębokie na telefon!!",
            "komfortowe nawet w klubie",
            "nosiłam już 3x w tym tygodniu lol"
        ],
        "dresses": [
            "leży lepiej niż wszystkie moje sukienki", 
            "wycięcia strategicznie w dobrych miejscach", 
            "idealna na randkę lub do klubu",
            "materiał po prostu inny",
            "detale z tyłu są wszystkim",
            "długość seksowna ale nie przesadzona",
            "czuję się jak główna bohaterka"
        ],
        "accessories": [
            "podnosi każdą stylizację", 
            "jakość mogłaby kosztować trzy razy więcej", 
            "wszyscy znajomi zazdroszczą",
            "pasuje do każdego klimatu",
            "design oryginalny ale noszalny",
            "rozmiar idealnie regulowany",
            "całkowicie wyróżniający element"
        ],
        "gothic": [
            "mroczny klimat bez efektu przebrania", 
            "ostre ale nadal noszalne na co dzień", 
            "idealne do mojej dark academia estetyki",
            "pierwszy wybór na festiwale i do klubów",
            "detale naprawdę oryginalne",
            "kluczowy element każdej gotyciej stylizacji",
            "idealnie pasuje do moich platformów"
        ]
    },
    "ru": {
        "tops": [
            "сочетается буквально со всем в моем гардеробе", 
            "крой очень выигрышный", 
            "материал намного лучше, чем ожидалось",
            "качество превосходит дорогие бренды",
            "цвет еще лучше вживую",
            "исполнение безупречное",
            "постоянно получаю комплименты",
            "стиль полностью соответствует моему вайбу",
            "сразу же выложила фото в образе",
            "носится очень комфортно",
            "ткань мягкая, но не просвечивает",
            "деталь у выреза очень уникальная"
        ],
        "bottoms": [
            "сидит как вторая кожа", 
            "буквально самая удобная вещь", 
            "длина идеальна для моего роста",
            "тянется идеально",
            "карманы достаточно глубокие для телефона!!",
            "комфортно даже в клубе",
            "уже надела 3 раза на этой неделе лол"
        ],
        "dresses": [
            "сидит лучше любого платья, что у меня есть", 
            "вырезы стратегически в нужных местах", 
            "идеально для свидания или клуба",
            "ткань просто другого уровня",
            "детали на спине - это всё",
            "длина сексуальная, но не слишком",
            "чувствую себя главной героиней в нем",
            "столько способов стилизовать",
            "выглядит flattering на любой фигуре",
            "драпировка безупречная",
            "заставляет чувствовать себя неостановимой",
            "легко танцевать всю ночь"
        ],
        "gothic": [
            "темный вайб без эффекта костюма", 
            "edge но можно носить каждый день", 
            "идеально для моей dark academia эстетики",
            "первый выбор для фестивалей и клубов",
            "детали действительно уникальные",
            "statement piece для любого гот образа",
            "идеально сочетается с моими платформами"
        ]
    }
}

def clean_html(raw_html):
    """Entfernt HTML-Tags aus Text"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_simplified_product_name(product_title, language="en"):
    """Extrahiert einen natürlicheren, kürzeren Produktnamen aus dem vollständigen Titel"""
    if not product_title:
        return "piece" if language == "en" else "Teil" if language == "de" else "produkt" if language == "pl" else "вещь"
        
    # Wenn der Titel kurz ist (< 15 Zeichen), kann er komplett verwendet werden
    if len(product_title) < 15:
        return product_title
        
    words = product_title.split()
    
    # Einfachste Möglichkeit: Nur das letzte Wort verwenden, wenn es ein Kleidungsstück ist
    clothing_terms = {
        "en": ["pants", "top", "shirt", "dress", "skirt", "jacket", "coat", "sweater", "hoodie", "cardigan", "jeans", "leggings", "shorts", "set", "bra", "corset", "gown", "jumpsuit", "bodysuit", "tee", "tank", "sweatshirt", "jumper", "blouse", "vest", "suit", "bikini", "swimsuit", "robe", "kimono", "crop", "hat", "cap"],
        "de": ["hose", "top", "shirt", "kleid", "rock", "jacke", "mantel", "pullover", "hoodie", "strickjacke", "jeans", "leggings", "shorts", "set", "bh", "korsett", "abendkleid", "jumpsuit", "bodysuit", "t-shirt", "tanktop", "sweatshirt", "pulli", "bluse", "weste", "anzug", "bikini", "badeanzug", "bademantel", "kimono", "croptop", "hut", "mütze"],
        "pl": ["spodnie", "top", "koszula", "sukienka", "spódnica", "kurtka", "płaszcz", "sweter", "bluza", "kardigan", "dżinsy", "leginsy", "szorty", "zestaw", "biustonosz", "gorset", "suknia", "kombinezon", "body", "koszulka", "top", "bluza", "sweter", "bluzka", "kamizelka", "garnitur", "bikini", "strój kąpielowy", "szlafrok", "kimono", "crop", "kapelusz", "czapka"],
        "ru": ["брюки", "топ", "рубашка", "платье", "юбка", "куртка", "пальто", "свитер", "худи", "кардиган", "джинсы", "леггинсы", "шорты", "комплект", "бюстгальтер", "корсет", "платье", "комбинезон", "боди", "футболка", "майка", "свитшот", "свитер", "блузка", "жилет", "костюм", "бикини", "купальник", "халат", "кимоно", "кроп", "шляпа", "кепка"]
    }
    
    # Fallback auf Englisch, wenn die Sprache nicht unterstützt wird
    terms = clothing_terms.get(language, clothing_terms["en"])
    
    # Schaue, ob das letzte Wort ein Kleidungsstück ist
    last_word_lower = words[-1].lower()
    if last_word_lower in terms:
        # Wenn ja, nutze das letzte Wort in seinem Original-Case
        return words[-1]
        
    # Alternative: Schau nach einem Kleidungsstück im gesamten Titel
    for word in words:
        if word.lower() in terms:
            return word
    
    # Wenn "Opium" im Namen ist (typisch für diese Marke), nutze das generische Kleidungsstück
    # basierend auf den Kategorien und der Sprache
    if "opium" in product_title.lower() or "Opium" in product_title:
        categories = []
        text = product_title.lower()
        for category in ["top", "pants", "dress", "skirt", "jacket", "coat", "cardigan"]:
            if category in text:
                categories.append(category)
        
        if categories:
            if language == "de":
                translation = {"top": "top", "pants": "hose", "dress": "kleid", "skirt": "rock", 
                              "jacket": "jacke", "coat": "mantel", "cardigan": "strickjacke"}
                return translation.get(categories[0], "Teil")
            elif language == "pl":
                translation = {"top": "top", "pants": "spodnie", "dress": "sukienka", "skirt": "spódnica", 
                              "jacket": "kurtka", "coat": "płaszcz", "cardigan": "kardigan"}
                return translation.get(categories[0], "rzecz")
            elif language == "ru":
                translation = {"top": "топ", "pants": "брюки", "dress": "платье", "skirt": "юбка", 
                              "jacket": "куртка", "coat": "пальто", "cardigan": "кардиган"}
                return translation.get(categories[0], "вещь")
            else:
                return categories[0]
        
        # Wenn es ein Opium-Produkt ist, aber keine bestimmte Kategorie erkannt wurde,
        # verwende nur "Opium"
        return "Opium"
    
    # Fallback 1: Gib nur die letzten 1-2 Wörter zurück (typisch für Produktnamen)
    if len(words) >= 3:
        return f"{words[-2]} {words[-1]}"
    elif len(words) == 2:
        return words[-1]
    
    # Fallback 2: Gib den generischen Begriff je nach Sprache zurück
    generic_terms = {
        "de": "Teil",
        "en": "piece",
        "pl": "rzecz",
        "ru": "вещь"
    }
    
    return generic_terms.get(language, "piece")

def get_product_category(product_info):
    """Bestimmt die Produktkategorie basierend auf Titel, Typ, Tags oder Beschreibung"""
    categories = []
    
    keywords = {
        'tops': ['top', 'shirt', 'bluse', 'tshirt', 't-shirt', 'pullover', 'sweatshirt', 'hoodie', 'tanktop'],
        'bottoms': ['hose', 'jeans', 'leggings', 'rock', 'shorts', 'skirt', 'pants'],
        'dresses': ['kleid', 'dress'],
        'accessories': ['schmuck', 'kette', 'armband', 'ring', 'ohrring', 'tasche', 'bag', 'schal', 'mütze', 'handschuhe'],
        'outerwear': ['jacke', 'mantel', 'coat', 'jacket', 'cardigan', 'weste', 'vest'],
        'gothic': ['gothic', 'dark', 'schwarz', 'black', 'mesh', 'spitze', 'lace', 'net'],
        'punk': ['punk', 'nieten', 'studs', 'leather', 'leder', 'tartan', 'plaid'],
        'vintage': ['vintage', 'retro', 'klassisch', 'classic']
    }
    
    text = (product_info.get('Title', '') + ' ' + 
            product_info.get('Type', '') + ' ' + 
            product_info.get('Tags', '') + ' ' + 
            clean_html(product_info.get('Body (HTML)', ''))).lower()
    
    for category, words in keywords.items():
        if any(word in text for word in words):
            categories.append(category)
    
    return categories if categories else ['tops']  # Default to 'tops' if no category detected

def select_language():
    """Wählt eine Sprache basierend auf der gewünschten Verteilung aus"""
    # 30% Deutsch, 50% Englisch, 10% Polnisch, 10% Russisch
    languages = random.choices(["de", "en", "pl", "ru"], weights=[30, 50, 10, 10], k=1)[0]
    return languages

def generate_youthful_username():
    """Generiert trendige, jugendliche Benutzernamen für 18-24-Jährige"""
    first_parts = [
        "xX", "x", "", "", "", "", ""  # Leere Strings häufiger für natürlichere Verteilung
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
        "Xx", "x", "xoxo", "", "", "", "",  # Leere Strings häufiger für natürlichere Verteilung
        "_", ".", "__", "..", "_x", "x_", ".x", "x.", 
        "_xo", "_", ".", "", "", "", ""
    ]
    
    numbers = ["", "", "", ""]  # 50% Chance, keine Zahl zu haben
    for year in range(97, 6):  # Geburtsjahre für ca. 18-24-Jährige
        numbers.append(str(year))
    for i in range(1, 10):
        numbers.append(str(i))
    for i in range(10, 100):
        numbers.append(str(i))
    
    # Verschiedene Muster für Benutzernamen
    patterns = [
        lambda: f"{random.choice(middle_parts)}{random.choice(numbers)}{random.choice(end_parts)}",
        lambda: f"{random.choice(first_parts)}{random.choice(middle_parts)}{random.choice(end_parts)}",
        lambda: f"{random.choice(middle_parts)}_{random.choice(middle_parts)}{random.choice(numbers)}",
        lambda: f"{random.choice(middle_parts)}.{random.choice(middle_parts)}{random.choice(numbers)}",
        lambda: f"{random.choice(middle_parts)}{random.choice(numbers)}",
        lambda: f"{random.choice(first_parts)}{random.choice(middle_parts)}{random.choice(numbers)}{random.choice(end_parts)}"
    ]
    
    return random.choice(patterns)()

def generate_reviewer_info(language):
    """Generiert zufällige Rezensenten-Informationen basierend auf der Sprache"""
    # 60% Chance für einen jugendlichen Benutzernamen statt eines "echten" Namens
    if random.random() < 0.6:
        reviewer_name = generate_youthful_username()
        
        # E-Mail basierend auf dem Benutzernamen generieren
        domains = ["gmail.com", "outlook.com", "icloud.com", "yahoo.com", "hotmail.com", 
                  "protonmail.com", "web.de", "gmx.de", "gmx.net", "live.com"]
        email = f"{reviewer_name.lower().replace(' ', '').replace('.', '_')}@{random.choice(domains)}"
    else:
        if language == "de":
            first_name = fake_de.first_name()
            last_initial = fake_de.last_name()[0]
            email = fake_de.email()
            location = random.choice(['DE', 'AT', 'CH'])
        elif language == "pl":
            first_name = fake_pl.first_name()
            last_initial = fake_pl.last_name()[0]
            email = fake_pl.email()
            location = 'PL'
        elif language == "ru":
            first_name = fake_ru.first_name()
            last_initial = fake_ru.last_name()[0]
            email = fake_ru.email()
            location = 'RU'
        else:  # English oder fallback
            first_name = fake_en.first_name()
            last_initial = fake_en.last_name()[0]
            email = fake_en.email()
            location = random.choice(['US', 'UK', 'CA', 'AU'])
        
        reviewer_name = f"{first_name} {last_initial}."
    
    # Location festlegen, wenn nicht bereits geschehen
    if 'location' not in locals():
        if language == "de":
            location = random.choice(['DE', 'AT', 'CH'])
        elif language == "pl":
            location = 'PL'
        elif language == "ru":
            location = 'RU'
        else:
            location = random.choice(['US', 'UK', 'CA', 'AU'])
    
    return reviewer_name, email, location

def generate_rating_distribution():
    """Generiert eine realistische Verteilung von Bewertungen (nur 3, 4 und 5 Sterne)"""
    # Gewichtete Verteilung: 5★: 60%, 4★: 30%, 3★: 10%
    rating = random.choices([5, 4, 3], weights=[60, 30, 10], k=1)[0]
    return rating

def generate_review_content(product_info, rating, language):
    """Generiert einen passenden Review-Text basierend auf Produktinfo, Bewertung und Sprache"""
    categories = get_product_category(product_info)
    
    # Vereinfachten Produktnamen für natürlichere Reviews generieren
    simplified_name = get_simplified_product_name(product_info.get('Title', ''), language)
    
    # 15% Chance, einen leeren Kommentar zu haben (nur Bewertung ohne Text)
    if random.random() < 0.15:
        return ""
    
    # 35% Chance auf einen kurzen Ein-Satz-Review
    if random.random() < 0.35:
        if language in short_reviews:
            return random.choice(short_reviews[language])
        else:
            return random.choice(short_reviews["en"])  # Fallback auf Englisch
    
    # Einleitungssätze basierend auf der Bewertung und Sprache
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
        },
        "pl": {
            5: [
                f"obsesja na punkcie tego {simplified_name}!!!",
                f"kupiłam ten {simplified_name} i zero żalu",
                f"omg ten {simplified_name} to dosłownie perfekcja",
                f"potrzebowałam {simplified_name} i trafiłam idealnie"
            ],
            4: [
                f"naprawdę ładny {simplified_name}",
                f"w końcu mam ten {simplified_name}",
                f"ten {simplified_name} jest całkiem fajny",
                f"całkiem zadowolona z {simplified_name}"
            ],
            3: [
                f"ten {simplified_name} jest ok",
                f"{simplified_name} jest wystarczająco dobry",
                f"zrobiłam sobie prezent w postaci {simplified_name}",
                f"ten {simplified_name} spełnia swoje zadanie"
            ]
        },
        "ru": {
            5: [
                f"одержима этим {simplified_name}!!!",
                f"купила этот {simplified_name} и ни о чем не жалею",
                f"омг этот {simplified_name} буквально идеален",
                f"нужно было {simplified_name} и попала в точку"
            ],
            4: [
                f"действительно классный {simplified_name}",
                f"наконец получила этот {simplified_name}",
                f"этот {simplified_name} довольно крутой",
                f"довольна этим {simplified_name}"
            ],
            3: [
                f"этот {simplified_name} нормальный",
                f"{simplified_name} достаточно хороший",
                f"побаловала себя этим {simplified_name}",
                f"этот {simplified_name} выполняет свою задачу"
            ]
        }
    }
    
    # Fallback auf Englisch, wenn die Sprache nicht verfügbar ist
    if language not in intros:
        language_to_use = "en"
    else:
        language_to_use = language
    
    # Review-Komponenten sammeln
    review_components = []
    
    # Komponente 1: Intro hinzufügen (75% Chance)
    if random.random() < 0.75:
        review_components.append(random.choice(intros[language_to_use][rating]))
    
    # Komponente 2: Produkt-spezifische Phrasen (85% Chance)
    if random.random() < 0.85 and language in product_phrases:
        phrases = []
        for category in categories:
            if category in product_phrases[language]:
                phrases.extend(product_phrases[language][category])
        
        # Nur wenn Phrasen vorhanden sind
        if phrases:
            # 60% Chance für 1 Phrase, 30% Chance für 2, 10% Chance für 3
            phrase_chances = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
            selected_phrases = random.sample(phrases, min(phrase_chances, len(phrases)))
            
            if selected_phrases:
                if len(review_components) > 0 and random.random() < 0.5:
                    # Mit Verbindungswort anhängen
                    connectors = {
                        "de": [" und ", " - ", ", ", ". ", "! ", " btw ", " aber "],
                        "en": [" and ", " - ", ", ", ". ", "! ", " btw ", " but "],
                        "pl": [" i ", " - ", ", ", ". ", "! ", " btw ", " ale "],
                        "ru": [" и ", " - ", ", ", ". ", "! ", " кстати ", " но "]
                    }
                    conn = random.choice(connectors.get(language, connectors["en"]))
                    if conn in [".", "!"]:
                        review_components[-1] += conn
                        review_components.append(" ".join(selected_phrases))
                    else:
                        review_components[-1] += conn + " ".join(selected_phrases)
                else:
                    review_components.append(" ".join(selected_phrases))
    
    # Komponente 3: Shop-Bezug (25% Chance)
    if random.random() < 0.25 and language in shop_references:
        if len(review_components) > 0 and random.random() < 0.5:
            # Am Ende des letzten Komponente anhängen
            connectors = {
                "de": [". ", "! ", " und ", " - ", ", "],
                "en": [". ", "! ", " and ", " - ", ", "],
                "pl": [". ", "! ", " i ", " - ", ", "],
                "ru": [". ", "! ", " и ", " - ", ", "]
            }
            conn = random.choice(connectors.get(language, connectors["en"]))
            if conn in [".", "!"]:
                review_components[-1] += conn
                review_components.append(random.choice(shop_references[language]))
            else:
                review_components[-1] += conn + random.choice(shop_references[language])
        else:
            review_components.append(random.choice(shop_references[language]))
    
    # Komponente 4: Social Media-Bezug (20% Chance)
    if random.random() < 0.20 and language in social_media_refs:
        if len(review_components) > 0 and random.random() < 0.5:
            # Am Ende des letzten Komponente anhängen
            connectors = {
                "de": [". ", "! ", " und ", " - ", ", "],
                "en": [". ", "! ", " and ", " - ", ", "],
                "pl": [". ", "! ", " i ", " - ", ", "],
                "ru": [". ", "! ", " и ", " - ", ", "]
            }
            conn = random.choice(connectors.get(language, connectors["en"]))
            if conn in [".", "!"]:
                review_components[-1] += conn
                review_components.append(random.choice(social_media_refs[language]))
            else:
                review_components[-1] += conn + random.choice(social_media_refs[language])
        else:
            review_components.append(random.choice(social_media_refs[language]))
    
    # Komponente 5: Versand-Kommentare (15% Chance)
    if random.random() < 0.15 and language in shipping_comments:
        if len(review_components) > 0:
            # Am Ende des letzten Komponente anhängen
            connectors = {
                "de": [". ", "! ", " btw "],
                "en": [". ", "! ", " btw "],
                "pl": [". ", "! ", " btw "],
                "ru": [". ", "! ", " кстати "]
            }
            conn = random.choice(connectors.get(language, connectors["en"]))
            if conn in [".", "!"]:
                review_components[-1] += conn
                review_components.append(random.choice(shipping_comments[language]))
            else:
                review_components[-1] += conn + random.choice(shipping_comments[language])
        else:
            review_components.append(random.choice(shipping_comments[language]))
    
    # Review aus Komponenten zusammenbauen
    review = " ".join(review_components)
    
    # Jugendliche Schreibweise (15% Chance)
    if random.random() < 0.15:
        # Kein "ich" am Satzanfang
        review = re.sub(r"^Ich ", "ich ", review)
        
        # Keine Großschreibung am Satzanfang (30% Chance wenn aktiviert)
        if random.random() < 0.3:
            review = review[0].lower() + review[1:]
        
        # Mehr Ausrufezeichen und Emojis
        if review and review[-1] in [".", "!"]:
            num_excl = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10], k=1)[0]
            review = review[:-1] + "!" * num_excl
            
            # Emojis hinzufügen (50% Chance wenn Ausrufezeichen vorhanden)
            if random.random() < 0.5:
                emojis = ["💖", "✨", "🔥", "👌", "💯", "🙌", "😍", "🤩", "🥰", "💕", "❤️", "🖤", "👑", "🌟"]
                num_emojis = random.choices([1, 2, 3], weights=[50, 30, 20], k=1)[0]
                selected_emojis = random.sample(emojis, num_emojis)
                review += "".join(selected_emojis)
    
    return review

def generate_review_date(max_months_back=36):
    """Generiert ein zufälliges Datum innerhalb der letzten 36 Monate"""
    days_back = random.randint(1, max_months_back * 30)
    review_date = datetime.now() - timedelta(days=days_back)
    return review_date.strftime('%Y-%m-%d')

def main():
    input_file = 'products_export_1 5.csv'
    output_file = 'generated_reviews.csv'
    
    products = []
    
    # Einlesen der Produktdaten
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            products.append(row)
    
    print(f"{len(products)} Produkte gefunden.")
    
    # Erstellen der Reviews
    reviews = []
    product_handles_processed = set()
    
    for product in products:
        product_handle = product.get('Handle', '')
        
        # Überspringe Duplikate (da manche Handles mehrfach vorkommen können für verschiedene Varianten)
        if product_handle in product_handles_processed:
            continue
        
        product_handles_processed.add(product_handle)
        
        # Pro Produkt 3-10 Reviews erstellen (typisch für jugendliche Zielgruppe)
        num_reviews = random.randint(3, 10)
        
        for _ in range(num_reviews):
            # Wähle eine Sprache nach der vorgegebenen Verteilung
            language = select_language()
            
            rating = generate_rating_distribution()
            reviewer_name, reviewer_email, reviewer_location = generate_reviewer_info(language)
            
            # Wähle einen Titel in der passenden Sprache und Bewertung
            # 5% Chance auf keinen Titel (typisch für junge Reviewer)
            if random.random() < 0.05:
                review_title = ""
            else:
                if language in review_titles and rating in review_titles[language]:
                    review_title = random.choice(review_titles[language][rating])
                else:
                    # Fallback auf Englisch
                    review_title = random.choice(review_titles["en"][rating])
            
            review_content = generate_review_content(product, rating, language)
            review_date = generate_review_date(max_months_back=36)  # Innerhalb der letzten 36 Monate
            
            # 5% Chance auf keine Verifizierung
            verified = 'Yes' if random.random() > 0.05 else 'No'
            
            review = {
                'product_id': '',  # Leer lassen, wenn product_handle verwendet wird
                'product_handle': product_handle,
                'product_sku': product.get('Variant SKU', ''),
                'product_name': product.get('Title', ''),
                'reviewer_name': reviewer_name,
                'reviewer_email': reviewer_email,
                'reviewer_location': reviewer_location,
                'review_title': review_title,
                'review_content': review_content,
                'review_date': review_date,
                'image_urls': '',  # Leer lassen
                'status': 'Published',
                'rating': str(rating),
                'verified': verified,
                'reply_content': '',  # Leer lassen
                'reply_date': '',  # Leer lassen
                'is_store_review': 'false'
            }
            
            reviews.append(review)
    
    # Schreiben der generierten Reviews in eine CSV-Datei
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'product_id', 'product_handle', 'product_sku', 'product_name', 
            'reviewer_name', 'reviewer_email', 'reviewer_location', 
            'review_title', 'review_content', 'review_date', 
            'image_urls', 'status', 'rating', 'verified', 
            'reply_content', 'reply_date', 'is_store_review'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)
    
    print(f"{len(reviews)} Reviews für {len(product_handles_processed)} Produkte erstellt und in '{output_file}' gespeichert.")
    
    # Optional: Beispielreviews für ein bestimmtes Produkt anzeigen
    example_handle = "opium-gothic-mesh-top"
    example_reviews = [review for review in reviews if review['product_handle'] == example_handle]
    
    if example_reviews:
        print(f"\nBeispiel-Reviews für '{example_handle}':")
        for i, review in enumerate(example_reviews, 1):
            print(f"\nReview {i}:")
            print(f"Sprache: {('DE' if review['reviewer_location'] in ['DE', 'AT', 'CH'] else 'EN' if review['reviewer_location'] in ['US', 'UK', 'CA', 'AU'] else 'PL' if review['reviewer_location'] == 'PL' else 'RU')}")
            print(f"Bewertung: {review['rating']} Sterne")
            print(f"Titel: {review['review_title']}")
            print(f"Inhalt: {review['review_content']}")
            print(f"Datum: {review['review_date']}")
            print(f"Rezensent: {review['reviewer_name']} aus {review['reviewer_location']}")
    else:
        print(f"\nKein Produkt mit dem Handle '{example_handle}' gefunden.")

if __name__ == "__main__":
    main()