from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import csv
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Your credentials
SHOP_DOMAIN = "fugafashion.myshopify.com"
ACCESS_TOKEN = "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"

@app.route('/')
def index():
    return render_template('shopify_backend.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    from generate_fuga_reviews_standalone import REVIEW_TITLES, generate_reviewer_info, generate_review_content
    
    # Fetch products
    url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products.json?limit=250"
    headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    products = response.json()['products']
    
    # Generate reviews
    reviews = []
    for product in products:
        if 'clearance' in product['title'].lower():
            continue
        for _ in range(random.randint(3, 8)):
            lang = random.choice(['en', 'de'])
            rating = random.choices([5, 4, 3], weights=[60, 30, 10])[0]
            name, email, location = generate_reviewer_info(lang)
            title = random.choice(REVIEW_TITLES[lang][rating])
            content = generate_review_content(product, rating, lang)
            
            reviews.append({
                'product_id': str(product['id']),
                'product_handle': product['handle'],
                'product_name': product['title'],
                'reviewer_name': name,
                'reviewer_email': email,
                'reviewer_location': location,
                'review_title': title,
                'review_content': content,
                'review_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                'rating': str(rating),
                'status': 'Published',
                'verified': 'Yes'
            })
    
    # Save CSV
    filename = f'reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    os.makedirs('exports', exist_ok=True)
    with open(f'exports/{filename}', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)
    
    return jsonify({'success': True, 'count': len(reviews), 'filename': filename})

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'exports/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))