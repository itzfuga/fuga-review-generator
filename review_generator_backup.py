"""
Advanced Review Generation Engine
Matches the sophisticated Gen Z style of old_review.py with enhanced capabilities
"""
import random
from datetime import datetime, timedelta
import re

# Review titles with sophisticated language patterns for all 20 shop languages
REVIEW_TITLES = {
    "de": {
        5: ["Absolut fantastisch!", "Perfektes Produkt!", "Begeistert!", "Übertrifft alle Erwartungen!", "Einfach traumhaft!", "Ein Muss für jeden!", "Kann ich nur empfehlen!", "Bestes Produkt ever!", "Erstklassige Qualität!", "Liebe es!", "Top Produkt!", "Hervorragende Wahl!", "Mega Teil!", "Voll cool!", "Krass gut!", "Einfach nur wow!", "Beste Entscheidung ever!"],
        4: ["Sehr gutes Produkt", "Fast perfekt", "Wirklich schön", "Bin sehr zufrieden", "Gute Qualität", "Macht einen tollen Eindruck", "Empfehlenswert", "Positiv überrascht", "Toller Kauf", "Gutes Preis-Leistungs-Verhältnis", "Schönes Design", "Überzeugt mich", "Richtig nice", "Voll gut", "Echt cool", "Gefällt mir sehr"],
        3: ["Ganz okay", "Erfüllt seinen Zweck", "Im Großen und Ganzen zufrieden", "Mittelmäßig", "Entspricht den Erwartungen", "Nicht schlecht", "Könnte besser sein", "Durchschnittlich", "Für den Preis in Ordnung", "Brauchbar", "Mittelklasse", "Okay für den Alltag", "Ganz nett", "Passt schon"]
    },
    "en": {
        5: ["Absolutely amazing!", "Perfect product!", "Love it so much!", "Exceeds all expectations!", "Simply wonderful!", "A must-have!", "Highly recommend!", "Best product ever!", "First-class quality!", "Love it!", "Top product!", "Excellent choice!", "Obsessed with this!", "Literally perfect!", "Totally in love!", "So freaking good!"],
        4: ["Very good product", "Almost perfect", "Really nice", "Very satisfied", "Good quality", "Makes a great impression", "Recommendable", "Positively surprised", "Great purchase", "Good value for money", "Beautiful design", "Convincing", "Really cool", "Pretty nice", "Very pleased with it", "Quite good"],
        3: ["Decent", "Serves its purpose", "Satisfied overall", "Average", "Meets expectations", "Not bad", "Could be better", "Average", "Okay for the price", "Usable", "Middle-range", "Okay for everyday", "Pretty decent", "It's fine"]
    },
    "es": {
        5: ["¡Absolutamente increíble!", "¡Producto perfecto!", "¡Me encanta!", "¡Supera todas las expectativas!", "¡Simplemente maravilloso!", "¡Imprescindible!", "¡Lo recomiendo mucho!", "¡El mejor producto!", "¡Calidad de primera!", "¡Lo amo!", "¡Producto top!", "¡Excelente elección!", "¡Obsesionada con esto!", "¡Literalmente perfecto!", "¡Totalmente enamorada!", "¡Increíblemente bueno!"],
        4: ["Muy buen producto", "Casi perfecto", "Realmente bonito", "Muy satisfecha", "Buena calidad", "Causa una gran impresión", "Recomendable", "Positivamente sorprendida", "Gran compra", "Buena relación calidad-precio", "Diseño hermoso", "Me convence", "Realmente genial", "Bastante bueno", "Muy contenta con esto", "Bastante bueno"],
        3: ["Decente", "Cumple su propósito", "Satisfecha en general", "Promedio", "Cumple las expectativas", "No está mal", "Podría ser mejor", "Promedio", "Bien por el precio", "Utilizable", "Gama media", "Bien para el día a día", "Bastante decente", "Está bien"]
    },
    "fr": {
        5: ["Absolument incroyable!", "Produit parfait!", "Je l'adore!", "Dépasse toutes les attentes!", "Tout simplement merveilleux!", "Un incontournable!", "Je le recommande vivement!", "Le meilleur produit!", "Qualité de première classe!", "Je l'aime!", "Produit top!", "Excellent choix!", "Obsédée par ça!", "Littéralement parfait!", "Totalement amoureuse!", "Vraiment génial!"],
        4: ["Très bon produit", "Presque parfait", "Vraiment beau", "Très satisfaite", "Bonne qualité", "Fait une grande impression", "Recommandable", "Positivement surprise", "Excellent achat", "Bon rapport qualité-prix", "Beau design", "Me convainc", "Vraiment cool", "Assez bien", "Très contente", "Assez bon"],
        3: ["Correct", "Remplit son rôle", "Satisfaite dans l'ensemble", "Moyen", "Répond aux attentes", "Pas mal", "Pourrait être mieux", "Moyen", "Correct pour le prix", "Utilisable", "Milieu de gamme", "Correct pour tous les jours", "Assez correct", "Ça va"]
    },
    "it": {
        5: ["Assolutamente incredibile!", "Prodotto perfetto!", "Lo adoro!", "Supera tutte le aspettative!", "Semplicemente meraviglioso!", "Un must-have!", "Lo raccomando vivamente!", "Il miglior prodotto!", "Qualità di prima classe!", "Lo amo!", "Prodotto top!", "Scelta eccellente!", "Ossessionata da questo!", "Letteralmente perfetto!", "Totalmente innamorata!", "Davvero fantastico!"],
        4: ["Prodotto molto buono", "Quasi perfetto", "Davvero bello", "Molto soddisfatta", "Buona qualità", "Fa una grande impressione", "Raccomandabile", "Positivamente sorpresa", "Ottimo acquisto", "Buon rapporto qualità-prezzo", "Design bellissimo", "Mi convince", "Davvero cool", "Abbastanza buono", "Molto contenta", "Abbastanza buono"],
        3: ["Decente", "Serve al suo scopo", "Soddisfatta nel complesso", "Nella media", "Soddisfa le aspettative", "Non male", "Potrebbe essere meglio", "Nella media", "Va bene per il prezzo", "Utilizzabile", "Fascia media", "Va bene per tutti i giorni", "Abbastanza decente", "Va bene"]
    },
    "ru": {
        5: ["Абсолютно невероятно!", "Идеальный продукт!", "Обожаю это!", "Превосходит все ожидания!", "Просто замечательно!", "Обязательно нужно иметь!", "Очень рекомендую!", "Лучший продукт!", "Качество первого класса!", "Люблю это!", "Топ продукт!", "Отличный выбор!", "Одержима этим!", "Буквально идеально!", "Полностью влюблена!", "Невероятно хорошо!"],
        4: ["Очень хороший продукт", "Почти идеально", "Действительно красиво", "Очень довольна", "Хорошее качество", "Производит отличное впечатление", "Рекомендую", "Приятно удивлена", "Отличная покупка", "Хорошее соотношение цены и качества", "Красивый дизайн", "Убеждает меня", "Действительно классно", "Довольно хорошо", "Очень довольна", "Довольно хорошо"],
        3: ["Прилично", "Служит своей цели", "В целом довольна", "Средне", "Соответствует ожиданиям", "Неплохо", "Могло бы быть лучше", "Средне", "Нормально за эту цену", "Пригодно", "Средний класс", "Нормально для повседневного использования", "Довольно прилично", "Нормально"]
    },
    "pl": {
        5: ["Absolutnie niesamowite!", "Idealny produkt!", "Uwielbiam to!", "Przewyższa wszystkie oczekiwania!", "Po prostu cudowne!", "Musisz to mieć!", "Gorąco polecam!", "Najlepszy produkt!", "Jakość pierwszej klasy!", "Kocham to!", "Produkt top!", "Doskonały wybór!", "Jestem obsesyjnie zakochana!", "Dosłownie idealne!", "Całkowicie zakochana!", "Niesamowicie dobre!"],
        4: ["Bardzo dobry produkt", "Prawie idealny", "Naprawdę ładny", "Bardzo zadowolona", "Dobra jakość", "Robi świetne wrażenie", "Polecam", "Miło zaskoczona", "Świetny zakup", "Dobry stosunek jakości do ceny", "Piękny design", "Przekonuje mnie", "Naprawdę fajny", "Całkiem dobry", "Bardzo zadowolona", "Całkiem dobry"],
        3: ["Przyzwoity", "Spełnia swoje zadanie", "Zadowolona ogólnie", "Średni", "Spełnia oczekiwania", "Nieźle", "Mógłby być lepszy", "Średni", "W porządku za tę cenę", "Użyteczny", "Średnia półka", "W porządku na co dzień", "Całkiem przyzwoity", "W porządku"]
    },
    "nl": {
        5: ["Absoluut geweldig!", "Perfect product!", "Ik hou er zo van!", "Overtreft alle verwachtingen!", "Gewoon prachtig!", "Een must-have!", "Raad het ten zeerste aan!", "Beste product ooit!", "Eersteklas kwaliteit!", "Ik hou ervan!", "Top product!", "Uitstekende keuze!", "Geobsedeerd door dit!", "Letterlijk perfect!", "Helemaal verliefd!", "Zo ongelooflijk goed!"],
        4: ["Zeer goed product", "Bijna perfect", "Echt mooi", "Zeer tevreden", "Goede kwaliteit", "Maakt een geweldige indruk", "Aanbevelenswaardig", "Positief verrast", "Geweldige aankoop", "Goede prijs-kwaliteitverhouding", "Prachtig ontwerp", "Overtuigt me", "Echt cool", "Behoorlijk goed", "Zeer tevreden", "Behoorlijk goed"],
        3: ["Redelijk", "Vervult zijn doel", "Over het algemeen tevreden", "Gemiddeld", "Voldoet aan verwachtingen", "Niet slecht", "Zou beter kunnen", "Gemiddeld", "Oké voor de prijs", "Bruikbaar", "Middensegment", "Oké voor dagelijks gebruik", "Behoorlijk fatsoenlijk", "Het is prima"]
    },
    "sv": {
        5: ["Helt fantastisk!", "Perfekt produkt!", "Älskar det så mycket!", "Överträffar alla förväntningar!", "Helt underbart!", "Ett måste!", "Rekommenderar starkt!", "Bästa produkten!", "Förstklassig kvalitet!", "Älskar det!", "Toppprodukt!", "Utmärkt val!", "Besatt av detta!", "Bokstavligen perfekt!", "Helt förälskad!", "Så otroligt bra!"],
        4: ["Mycket bra produkt", "Nästan perfekt", "Riktigt snyggt", "Mycket nöjd", "Bra kvalitet", "Gör ett bra intryck", "Rekommenderas", "Positivt överraskad", "Fantastiskt köp", "Bra värde för pengarna", "Vacker design", "Övertygar mig", "Riktigt coolt", "Ganska bra", "Mycket nöjd", "Ganska bra"],
        3: ["Okej", "Fyller sitt syfte", "Nöjd överlag", "Genomsnittlig", "Uppfyller förväntningarna", "Inte dåligt", "Kunde vara bättre", "Genomsnittlig", "Okej för priset", "Användbar", "Mellanklass", "Okej för vardagsbruk", "Ganska okej", "Det är bra"]
    },
    "da": {
        5: ["Helt fantastisk!", "Perfekt produkt!", "Elsker det så meget!", "Overgår alle forventninger!", "Simpelthen vidunderligt!", "Et must-have!", "Anbefaler stærkt!", "Bedste produkt nogensinde!", "Førsteklasses kvalitet!", "Elsker det!", "Top produkt!", "Fremragende valg!", "Besat af dette!", "Bogstaveligt perfekt!", "Totalt forelsket!", "Så utroligt godt!"],
        4: ["Meget godt produkt", "Næsten perfekt", "Virkelig pænt", "Meget tilfreds", "God kvalitet", "Gør et godt indtryk", "Kan anbefales", "Positivt overrasket", "Fantastisk køb", "God værdi for pengene", "Smukt design", "Overbeviser mig", "Virkelig cool", "Ret godt", "Meget tilfreds", "Ret godt"],
        3: ["Anstændig", "Opfylder sit formål", "Tilfreds overordnet", "Gennemsnitlig", "Opfylder forventningerne", "Ikke dårligt", "Kunne være bedre", "Gennemsnitlig", "Okay for prisen", "Brugbar", "Mellemklasse", "Okay til daglig brug", "Ret anstændig", "Det er fint"]
    },
    "fi": {
        5: ["Aivan fantastinen!", "Täydellinen tuote!", "Rakastan sitä niin paljon!", "Ylittää kaikki odotukset!", "Yksinkertaisesti ihana!", "Pakollinen hankinta!", "Suosittelen lämpimästi!", "Paras tuote ikinä!", "Ensiluokkainen laatu!", "Rakastan sitä!", "Huipputuote!", "Erinomainen valinta!", "Pakkomielle tähän!", "Kirjaimellisesti täydellinen!", "Täysin rakastunut!", "Niin uskomattoman hyvä!"],
        4: ["Erittäin hyvä tuote", "Melkein täydellinen", "Todella kaunis", "Erittäin tyytyväinen", "Hyvä laatu", "Tekee hienon vaikutuksen", "Suositeltava", "Positiivisesti yllättynyt", "Loistava osto", "Hyvä hinta-laatusuhde", "Kaunis muotoilu", "Vakuuttaa minut", "Todella siisti", "Melko hyvä", "Erittäin tyytyväinen", "Melko hyvä"],
        3: ["Kunnollinen", "Täyttää tarkoituksensa", "Tyytyväinen kaiken kaikkiaan", "Keskiverto", "Täyttää odotukset", "Ei huono", "Voisi olla parempi", "Keskiverto", "OK hinnaltaan", "Käyttökelpoinen", "Keskiluokka", "OK arkikäyttöön", "Melko kunnollinen", "Se on hyvä"]
    },
    "cs": {
        5: ["Naprosto úžasné!", "Perfektní produkt!", "Miluju to tak moc!", "Předčí všechna očekávání!", "Jednoduše nádherné!", "Musíte mít!", "Vřele doporučuji!", "Nejlepší produkt vůbec!", "Prvotřídní kvalita!", "Miluji to!", "Špičkový produkt!", "Vynikající volba!", "Jsem tím posedlá!", "Doslova dokonalé!", "Úplně zamilovaná!", "Tak neuvěřitelně dobré!"],
        4: ["Velmi dobrý produkt", "Skoro dokonalý", "Opravdu pěkný", "Velmi spokojená", "Dobrá kvalita", "Dělá skvělý dojem", "Doporučuji", "Příjemně překvapená", "Skvělý nákup", "Dobrý poměr ceny a kvality", "Krásný design", "Přesvědčuje mě", "Opravdu cool", "Docela dobré", "Velmi spokojená", "Docela dobré"],
        3: ["Slušné", "Plní svůj účel", "Celkově spokojená", "Průměrné", "Splňuje očekávání", "Není špatné", "Mohlo by být lepší", "Průměrné", "OK za tu cenu", "Použitelné", "Střední třída", "OK pro každodenní použití", "Docela slušné", "Je to dobré"]
    },
    "hu": {
        5: ["Teljesen elképesztő!", "Tökéletes termék!", "Annyira szeretem!", "Felülmúlja az összes elvárást!", "Egyszerűen csodálatos!", "Kötelező darab!", "Melegen ajánlom!", "A legjobb termék valaha!", "Első osztályú minőség!", "Imádom!", "Csúcs termék!", "Kiváló választás!", "Megszállottja vagyok ennek!", "Szó szerint tökéletes!", "Teljesen szerelmes vagyok!", "Olyan hihetetlenül jó!"],
        4: ["Nagyon jó termék", "Majdnem tökéletes", "Igazán szép", "Nagyon elégedett", "Jó minőség", "Nagyszerű benyomást kelt", "Ajánlható", "Kellemesen meglepett", "Fantasztikus vásárlás", "Jó ár-érték arány", "Gyönyörű design", "Meggyőz engem", "Igazán menő", "Elég jó", "Nagyon elégedett", "Elég jó"],
        3: ["Tisztességes", "Betölti a célját", "Összességében elégedett", "Átlagos", "Teljesíti az elvárásokat", "Nem rossz", "Lehetne jobb", "Átlagos", "Rendben az árért", "Használható", "Középkategória", "Rendben napi használatra", "Elég tisztességes", "Jó"]
    },
    "tr": {
        5: ["Kesinlikle harika!", "Mükemmel ürün!", "Çok seviyorum!", "Tüm beklentileri aşıyor!", "Basitçe harika!", "Mutlaka alınmalı!", "Şiddetle tavsiye ederim!", "Şimdiye kadarki en iyi ürün!", "Birinci sınıf kalite!", "Bayılıyorum!", "En iyi ürün!", "Mükemmel seçim!", "Buna takıntılıyım!", "Kelimenin tam anlamıyla mükemmel!", "Tamamen aşığım!", "İnanılmaz derecede iyi!"],
        4: ["Çok iyi ürün", "Neredeyse mükemmel", "Gerçekten güzel", "Çok memnun", "İyi kalite", "Harika bir izlenim bırakıyor", "Tavsiye edilir", "Olumlu şaşırdım", "Harika alışveriş", "İyi fiyat-kalite oranı", "Güzel tasarım", "Beni ikna ediyor", "Gerçekten cool", "Oldukça iyi", "Çok memnun", "Oldukça iyi"],
        3: ["Düzgün", "Amacını yerine getiriyor", "Genel olarak memnun", "Ortalama", "Beklentileri karşılıyor", "Fena değil", "Daha iyi olabilirdi", "Ortalama", "Fiyatına göre tamam", "Kullanılabilir", "Orta sınıf", "Günlük kullanım için tamam", "Oldukça düzgün", "İyi"]
    },
    "ar": {
        5: ["رائع تماماً!", "منتج مثالي!", "أحبه كثيراً!", "يفوق كل التوقعات!", "رائع ببساطة!", "يجب اقتناؤه!", "أنصح به بشدة!", "أفضل منتج على الإطلاق!", "جودة من الدرجة الأولى!", "أعشقه!", "منتج ممتاز!", "اختيار ممتاز!", "مهووسة به!", "مثالي حرفياً!", "واقعة في حبه تماماً!", "جيد بشكل لا يصدق!"],
        4: ["منتج جيد جداً", "مثالي تقريباً", "جميل حقاً", "راضية جداً", "جودة جيدة", "يترك انطباعاً رائعاً", "يُنصح به", "تفاجأت بشكل إيجابي", "شراء رائع", "نسبة جيدة بين السعر والجودة", "تصميم جميل", "يقنعني", "رائع حقاً", "جيد إلى حد كبير", "راضية جداً", "جيد إلى حد كبير"],
        3: ["لائق", "يحقق الغرض", "راضية بشكل عام", "متوسط", "يلبي التوقعات", "ليس سيئاً", "يمكن أن يكون أفضل", "متوسط", "مقبول للسعر", "قابل للاستخدام", "فئة متوسطة", "مقبول للاستخدام اليومي", "لائق إلى حد كبير", "إنه جيد"]
    },
    "el": {
        5: ["Απολύτως καταπληκτικό!", "Τέλειο προϊόν!", "Το λατρεύω τόσο πολύ!", "Ξεπερνά όλες τις προσδοκίες!", "Απλά θαυμάσιο!", "Πρέπει να το έχεις!", "Το συνιστώ ανεπιφύλακτα!", "Το καλύτερο προϊόν ποτέ!", "Ποιότητα πρώτης τάξης!", "Το αγαπώ!", "Κορυφαίο προϊόν!", "Εξαιρετική επιλογή!", "Είμαι εμμονική με αυτό!", "Κυριολεκτικά τέλειο!", "Εντελώς ερωτευμένη!", "Τόσο απίστευτα καλό!"],
        4: ["Πολύ καλό προϊόν", "Σχεδόν τέλειο", "Πραγματικά όμορφο", "Πολύ ικανοποιημένη", "Καλή ποιότητα", "Κάνει εξαιρετική εντύπωση", "Συστήνεται", "Θετικά εκπλήσσομαι", "Φανταστική αγορά", "Καλή σχέση ποιότητας-τιμής", "Όμορφος σχεδιασμός", "Με πείθει", "Πραγματικά cool", "Αρκετά καλό", "Πολύ ικανοποιημένη", "Αρκετά καλό"],
        3: ["Αξιοπρεπές", "Εκπληρώνει τον σκοπό του", "Ικανοποιημένη συνολικά", "Μέτριο", "Ανταποκρίνεται στις προσδοκίες", "Όχι κακό", "Θα μπορούσε να είναι καλύτερο", "Μέτριο", "Εντάξει για την τιμή", "Χρησιμοποιήσιμο", "Μεσαία κατηγορία", "Εντάξει για καθημερινή χρήση", "Αρκετά αξιοπρεπές", "Είναι καλό"]
    },
    "ko": {
        5: ["정말 놀라워요!", "완벽한 제품!", "너무 사랑해요!", "모든 기대를 뛰어넘어요!", "정말 멋져요!", "꼭 있어야 할 아이템!", "강력 추천!", "최고의 제품!", "일류 품질!", "정말 좋아해요!", "최고 제품!", "훌륭한 선택!", "이것에 빠져있어요!", "말 그대로 완벽해요!", "완전히 반했어요!", "믿을 수 없을 정도로 좋아요!"],
        4: ["아주 좋은 제품", "거의 완벽해요", "정말 예뻐요", "매우 만족해요", "좋은 품질", "훌륭한 인상을 줘요", "추천해요", "좋게 놀랐어요", "훌륭한 구매", "좋은 가성비", "아름다운 디자인", "저를 설득해요", "정말 멋져요", "꽤 좋아요", "매우 만족해요", "꽤 좋아요"],
        3: ["괜찮아요", "목적을 달성해요", "전반적으로 만족해요", "평균적", "기대에 부응해요", "나쁘지 않아요", "더 좋을 수 있어요", "평균적", "가격 대비 괜찮아요", "사용 가능해요", "중간급", "일상 사용에 괜찮아요", "꽤 괜찮아요", "좋아요"]
    },
    "ja": {
        5: ["絶対に素晴らしい！", "完璧な商品！", "とても愛してる！", "すべての期待を上回る！", "シンプルに素晴らしい！", "必須アイテム！", "強くお勧めします！", "今まで最高の商品！", "一流の品質！", "大好き！", "トップ商品！", "素晴らしい選択！", "これに夢中！", "文字通り完璧！", "完全に恋してる！", "信じられないほど良い！"],
        4: ["とても良い商品", "ほぼ完璧", "本当に美しい", "とても満足", "良い品質", "素晴らしい印象を与える", "お勧めできる", "良い意味で驚いた", "素晴らしい買い物", "良いコスパ", "美しいデザイン", "私を納得させる", "本当にクール", "かなり良い", "とても満足", "かなり良い"],
        3: ["まあまあ", "目的を果たす", "全体的に満足", "平均的", "期待に応える", "悪くない", "もっと良くできる", "平均的", "価格にしては大丈夫", "使える", "中級", "日常使いには大丈夫", "かなりまあまあ", "良い"]
    },
    "zh": {
        5: ["绝对惊人！", "完美的产品！", "太爱了！", "超出所有期望！", "简直太棒了！", "必备单品！", "强烈推荐！", "有史以来最好的产品！", "一流品质！", "爱死了！", "顶级产品！", "绝佳选择！", "对此着迷！", "字面意思的完美！", "完全爱上了！", "好得令人难以置信！"],
        4: ["非常好的产品", "几乎完美", "真的很漂亮", "非常满意", "质量很好", "给人很好的印象", "值得推荐", "惊喜地满意", "很棒的购买", "性价比很好", "漂亮的设计", "说服了我", "真的很酷", "还不错", "非常满意", "还不错"],
        3: ["还行", "达到目的", "总体满意", "一般", "符合期望", "不算差", "可以更好", "一般", "价格还行", "可用", "中等", "日常使用还行", "还算不错", "还好"]
    },
    "id": {
        5: ["Benar-benar luar biasa!", "Produk sempurna!", "Sangat menyukainya!", "Melampaui semua harapan!", "Sangat menakjubkan!", "Wajib punya!", "Sangat merekomendasikan!", "Produk terbaik yang pernah ada!", "Kualitas kelas satu!", "Sangat menyukainya!", "Produk terbaik!", "Pilihan yang luar biasa!", "Terobsesi dengan ini!", "Benar-benar sempurna!", "Benar-benar jatuh cinta!", "Luar biasa sekali!"],
        4: ["Produk yang sangat bagus", "Hampir sempurna", "Benar-benar bagus", "Sangat puas", "Kualitas bagus", "Memberikan kesan yang bagus", "Direkomendasikan", "Terkejut dengan positif", "Pembelian yang bagus", "Nilai yang bagus untuk uang", "Desain yang indah", "Meyakinkan saya", "Benar-benar keren", "Cukup bagus", "Sangat puas", "Cukup bagus"],
        3: ["Lumayan", "Melayani tujuannya", "Puas secara keseluruhan", "Rata-rata", "Memenuhi harapan", "Tidak buruk", "Bisa lebih baik", "Rata-rata", "Oke untuk harganya", "Dapat digunakan", "Kelas menengah", "Oke untuk penggunaan sehari-hari", "Cukup lumayan", "Bagus"]
    },
    "pt": {
        5: ["Absolutamente incrível!", "Produto perfeito!", "Amo muito!", "Supera todas as expectativas!", "Simplesmente maravilhoso!", "Indispensável!", "Recomendo vivamente!", "Melhor produto de sempre!", "Qualidade de primeira!", "Adoro!", "Produto top!", "Excelente escolha!", "Obcecada por isto!", "Literalmente perfeito!", "Completamente apaixonada!", "Incrivelmente bom!"],
        4: ["Produto muito bom", "Quase perfeito", "Realmente bonito", "Muito satisfeita", "Boa qualidade", "Causa uma ótima impressão", "Recomendável", "Positivamente surpreendida", "Ótima compra", "Boa relação qualidade-preço", "Design lindo", "Convence-me", "Realmente fixe", "Bastante bom", "Muito satisfeita", "Bastante bom"],
        3: ["Decente", "Serve o seu propósito", "Satisfeita no geral", "Médio", "Cumpre as expectativas", "Não é mau", "Podia ser melhor", "Médio", "Está bem pelo preço", "Utilizável", "Gama média", "Está bem para uso diário", "Bastante decente", "Está bom"]
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
            return get_unique_phrase(SHORT_REVIEWS[language], language, "short")
        else:
            return get_unique_phrase(SHORT_REVIEWS["en"], "en", "short")
    
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
        review_components.append(get_unique_phrase(intros[language_to_use][rating], language_to_use, "intro"))
    
    # Component 2: Product-specific phrases (70% chance, reduced from 85%)
    if random.random() < 0.70 and language in PRODUCT_PHRASES:
        phrases = []
        for category in categories:
            if category in PRODUCT_PHRASES[language]:
                phrases.extend(PRODUCT_PHRASES[language][category])
        
        if phrases:
            # Reduce phrase count for better flow
            phrase_count = random.choices([1, 2], weights=[70, 30], k=1)[0]
            # Use unique phrases to avoid repetition
            available_phrases = [p for p in phrases if p not in USED_PHRASES[language]]
            if len(available_phrases) < phrase_count:
                available_phrases = phrases  # fallback if not enough unique phrases
            selected_phrases = random.sample(available_phrases, min(phrase_count, len(available_phrases)))
            # Mark selected phrases as used
            for phrase in selected_phrases:
                USED_PHRASES[language].add(phrase)
            
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
            review_components.append(get_unique_phrase(SHOP_REFERENCES[language], language, "shop"))
        else:
            review_components.append(get_unique_phrase(SHOP_REFERENCES[language], language, "shop"))
    
    # Component 4: Social media reference (15% chance, reduced)
    if random.random() < 0.15 and language in SOCIAL_MEDIA_REFS:
        if len(review_components) > 0:
            # Always use sentence break for social media references
            review_components[-1] += ". " if not review_components[-1].endswith(('.', '!')) else " "
            review_components.append(get_unique_phrase(SOCIAL_MEDIA_REFS[language], language, "social"))
        else:
            review_components.append(get_unique_phrase(SOCIAL_MEDIA_REFS[language], language, "social"))
    
    # Component 5: Shipping comment (10% chance, reduced)
    if random.random() < 0.10 and language in SHIPPING_COMMENTS:
        if len(review_components) > 0:
            # Use btw connector or sentence break
            connectors = [". ", "! ", " btw "]
            conn = random.choice(connectors)
            if conn in [".", "!"]:
                review_components[-1] += conn
                review_components.append(get_unique_phrase(SHIPPING_COMMENTS[language], language, "shipping"))
            else:
                review_components[-1] += conn + get_unique_phrase(SHIPPING_COMMENTS[language], language, "shipping")
        else:
            review_components.append(get_unique_phrase(SHIPPING_COMMENTS[language], language, "shipping"))
    
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

# Global phrase tracking to prevent repetition
USED_PHRASES = {
    "de": set(), "en": set(), "es": set(), "fr": set(), "it": set(), "ru": set(),
    "pl": set(), "nl": set(), "sv": set(), "da": set(), "fi": set(), "cs": set(),
    "hu": set(), "tr": set(), "ar": set(), "el": set(), "ko": set(), "ja": set(),
    "zh": set(), "id": set(), "pt": set()
}

def select_language():
    """Select language based on all 20 shop languages with realistic distribution"""
    # Based on global fashion/youth market distribution
    languages = ["de", "en", "es", "fr", "it", "ru", "pl", "nl", "sv", "da", 
                "fi", "cs", "hu", "tr", "ar", "el", "ko", "ja", "zh", "id", "pt"]
    weights = [15, 25, 10, 8, 7, 6, 5, 4, 3, 3, 2, 2, 2, 2, 2, 2, 3, 3, 4, 2, 3]  # Total: 100
    return random.choices(languages, weights=weights, k=1)[0]

def get_unique_phrase(phrase_list, language, category="general"):
    """Get a unique phrase that hasn't been used recently"""
    global USED_PHRASES
    
    available_phrases = [p for p in phrase_list if p not in USED_PHRASES[language]]
    
    # If we've used all phrases, reset the tracking for this language
    if not available_phrases:
        USED_PHRASES[language].clear()
        available_phrases = phrase_list
    
    # Select random phrase and mark as used
    phrase = random.choice(available_phrases)
    USED_PHRASES[language].add(phrase)
    
    # Keep only recent phrases (limit to 50% of total phrases per language)
    if len(USED_PHRASES[language]) > len(phrase_list) * 0.5:
        # Remove oldest phrases (random selection to clear some)
        phrases_to_remove = random.sample(list(USED_PHRASES[language]), 
                                        len(USED_PHRASES[language]) // 3)
        for p in phrases_to_remove:
            USED_PHRASES[language].discard(p)
    
    return phrase

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
            review_title = get_unique_phrase(REVIEW_TITLES[language][rating], language, "title")
        else:
            review_title = get_unique_phrase(REVIEW_TITLES["en"][rating], "en", "title")
    
    review_content = generate_review_content(product, rating, language)
    
    # Add review ending (30% chance) for longer reviews
    if len(review_content) > 50 and random.random() < 0.3:
        if language in REVIEW_ENDINGS and rating in REVIEW_ENDINGS[language]:
            ending = get_unique_phrase(REVIEW_ENDINGS[language][rating], language, "ending")
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