from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import csv
import random
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Your credentials from environment variables
SHOP_DOMAIN = os.environ.get('SHOPIFY_SHOP_DOMAIN', 'your-shop.myshopify.com')
ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN', 'your-access-token')
KLAVIYO_API_KEY = os.environ.get('KLAVIYO_API_KEY', 'your-klaviyo-key')

# File to track generated reviews
REVIEW_TRACKING_FILE = 'review_tracking.json'

def load_review_tracking():
    """Load tracking data for generated reviews"""
    if os.path.exists(REVIEW_TRACKING_FILE):
        with open(REVIEW_TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_review_tracking(data):
    """Save tracking data for generated reviews"""
    with open(REVIEW_TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_klaviyo_reviews_for_product(product_handle):
    """Fetch review count from Klaviyo for a specific product"""
    try:
        # Klaviyo uses events to track reviews
        # We'll search for review events related to this product
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # First, let's try to get events of type "Reviewed Product"
        # Note: The exact event name might vary based on your Klaviyo setup
        url = f"https://a.klaviyo.com/api/events/?filter=equals(metric.name,'Reviewed Product')"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            events = response.json().get('data', [])
            # Count reviews for this specific product
            review_count = 0
            for event in events:
                properties = event.get('attributes', {}).get('properties', {})
                if properties.get('ProductID') == product_handle or properties.get('product_handle') == product_handle:
                    review_count += 1
            return review_count
        else:
            print(f"Klaviyo API error: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"Error fetching Klaviyo reviews: {str(e)}")
        return 0

@app.route('/')
def index():
    return render_template('shopify_backend.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    """Fetch all products with review count tracking"""
    try:
        # Check if credentials are properly set
        if SHOP_DOMAIN == 'your-shop.myshopify.com' or ACCESS_TOKEN == 'your-access-token':
            return jsonify({
                'success': False, 
                'error': 'Shopify credentials not configured. Please set SHOPIFY_SHOP_DOMAIN and SHOPIFY_ACCESS_TOKEN environment variables.'
            }), 500
        
        # Fetch products from Shopify
        url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products.json?limit=250"
        headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
        response = requests.get(url, headers=headers)
        
        # Check if request was successful
        if response.status_code != 200:
            error_msg = f"Shopify API error: {response.status_code}"
            if response.text:
                error_msg += f" - {response.text}"
            return jsonify({'success': False, 'error': error_msg}), 500
        
        response_data = response.json()
        if 'products' not in response_data:
            return jsonify({'success': False, 'error': 'Invalid response from Shopify API'}), 500
            
        products = response_data['products']
        
        # Load review tracking data
        review_tracking = load_review_tracking()
        
        # Format products with review counts
        products_data = []
        
        # Check if we should fetch Klaviyo reviews (only if API key is set)
        fetch_klaviyo = KLAVIYO_API_KEY != 'your-klaviyo-key'
        
        for product in products:
            product_id = str(product['id'])
            
            # Get Klaviyo review count if available
            klaviyo_reviews = 0
            if fetch_klaviyo:
                klaviyo_reviews = get_klaviyo_reviews_for_product(product['handle'])
            
            products_data.append({
                'id': product_id,
                'title': product['title'],
                'handle': product['handle'],
                'image': product['images'][0]['src'] if product.get('images') else None,
                'variants_count': len(product.get('variants', [])),
                'generated_reviews': review_tracking.get(product_id, {}).get('count', 0),
                'klaviyo_reviews': klaviyo_reviews,
                'total_reviews': klaviyo_reviews + review_tracking.get(product_id, {}).get('count', 0),
                'last_generated': review_tracking.get(product_id, {}).get('last_generated', None),
                'created_at': product.get('created_at')
            })
        
        # Sort by created_at (newest first)
        products_data.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({'success': True, 'products': products_data})
    
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/generate/<product_id>', methods=['POST'])
def generate_for_product(product_id):
    """Generate reviews for a specific product"""
    from generate_fuga_reviews_standalone import REVIEW_TITLES, generate_reviewer_info, generate_review_content
    
    try:
        # Get review count from request
        data = request.json
        review_count = data.get('count', 5)
        
        # Fetch specific product
        url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
        response = requests.get(url, headers=headers)
        product = response.json()['product']
        
        # Generate reviews
        reviews = []
        for _ in range(review_count):
            lang = random.choice(['en', 'de'])
            rating = random.choices([5, 4, 3], weights=[60, 30, 10])[0]
            name, email, location = generate_reviewer_info(lang)
            title = random.choice(REVIEW_TITLES[lang][rating])
            content = generate_review_content(product['title'], rating, lang)
            
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
                'verified': 'Yes',
                'image_urls': '',
                'reply_content': '',
                'reply_date': '',
                'is_store_review': 'false'
            })
        
        # Save CSV
        filename = f'reviews_{product_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        os.makedirs('exports', exist_ok=True)
        with open(f'exports/{filename}', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
            writer.writeheader()
            writer.writerows(reviews)
        
        # Update tracking
        review_tracking = load_review_tracking()
        if product_id not in review_tracking:
            review_tracking[product_id] = {'count': 0}
        review_tracking[product_id]['count'] += len(reviews)
        review_tracking[product_id]['last_generated'] = datetime.now().isoformat()
        save_review_tracking(review_tracking)
        
        return jsonify({
            'success': True, 
            'count': len(reviews), 
            'filename': filename,
            'product_name': product['title']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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