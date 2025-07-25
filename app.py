"""
Fuga Studios Review Generator - Shopify App
A native Shopify app for generating high-quality product reviews
"""
import os
import json
import hmac
import hashlib
import base64
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, redirect, session, render_template, jsonify, send_file
import requests
from datetime import datetime, timedelta
import csv
import random

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Shopify App Configuration
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
SHOPIFY_SCOPES = 'read_products,write_products,read_customers,write_customers'
SHOPIFY_REDIRECT_URI = os.environ.get('SHOPIFY_REDIRECT_URI', 'https://your-app.com/auth/callback')

# App URLs
BASE_URL = os.environ.get('BASE_URL', 'https://your-app.com')

def verify_webhook(data, hmac_header):
    """Verify Shopify webhook"""
    if not hmac_header:
        return False
    
    computed_hmac = base64.b64encode(
        hmac.new(SHOPIFY_API_SECRET.encode('utf-8'), data, hashlib.sha256).digest()
    )
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

def verify_shopify_request(query_params):
    """Verify request came from Shopify"""
    if 'hmac' not in query_params:
        return False
    
    hmac_to_verify = query_params.pop('hmac')[0]
    query_string = '&'.join([f"{key}={value[0]}" for key, value in sorted(query_params.items())])
    
    computed_hmac = hmac.new(
        SHOPIFY_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_hmac, hmac_to_verify)

@app.route('/')
def index():
    """App installation/auth page"""
    shop = request.args.get('shop')
    
    if not shop:
        return render_template('install.html'), 400
    
    # Verify this is a valid .myshopify.com domain
    if not shop.endswith('.myshopify.com'):
        return render_template('install.html'), 400
    
    # Always show install page first (don't auto-redirect to /app)
    # This ensures proper OAuth flow
    return render_template('install.html', shop=shop)

@app.route('/auth/start', methods=['POST'])
def auth_start():
    """Start OAuth flow"""
    shop = request.form.get('shop')
    
    if not shop or not shop.endswith('.myshopify.com'):
        return "Invalid shop", 400
    
    # Start OAuth flow
    auth_url = f"https://{shop}/admin/oauth/authorize"
    params = {
        'client_id': SHOPIFY_API_KEY,
        'scope': SHOPIFY_SCOPES,
        'redirect_uri': SHOPIFY_REDIRECT_URI,
        'state': shop  # Use shop as state for verification
    }
    
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    return redirect(f"{auth_url}?{query_string}")

@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback from Shopify"""
    # Verify the request
    query_params = dict(request.args.lists())
    
    if not verify_shopify_request(query_params.copy()):
        return "Unauthorized", 401
    
    shop = request.args.get('shop')
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not shop or not code or state != shop:
        return "Invalid request", 400
    
    # Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"
    token_data = {
        'client_id': SHOPIFY_API_KEY,
        'client_secret': SHOPIFY_API_SECRET,
        'code': code
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code != 200:
        return "Failed to get access token", 500
    
    token_info = response.json()
    access_token = token_info.get('access_token')
    
    if not access_token:
        return "No access token received", 500
    
    # Store in session (in production, store in database)
    session['shop'] = shop
    session['access_token'] = access_token
    
    # Redirect to app
    return redirect(f'/app?shop={shop}&host={request.args.get("host", "")}')

@app.route('/app')
def app_page():
    """Main app interface"""
    shop = request.args.get('shop')
    host = request.args.get('host', '')
    
    if not shop:
        return "Missing shop parameter", 400
    
    # Store shop in session if not already there
    if not session.get('shop'):
        session['shop'] = shop
    
    # For embedded apps, we need the host parameter
    # But for direct access, we can work without it
    return render_template('app.html', shop=shop, api_key=SHOPIFY_API_KEY, host=host)

@app.route('/api/products')
def get_products():
    """Get products with review counts"""
    shop = session.get('shop')
    access_token = session.get('access_token')
    
    
    # Fallback for testing
    if not shop:
        shop = request.args.get('shop', 'fugafashion.myshopify.com')
    
    # Temporary: For fugafashion, use the existing access token
    if shop == 'fugafashion.myshopify.com' and not access_token:
        
        # This is your existing access token from the old app
        access_token = os.environ.get('PRIVATE_APP_TOKEN', os.environ.get('SHOPIFY_ACCESS_TOKEN', ''))
        print(f"Using private app token for {shop}: {access_token[:10]}..." if access_token else "No token found")
    
    if not access_token:
        # Debug what's happening
        print(f"No access token found for shop: {shop}")
        print(f"Session shop: {session.get('shop')}")
        print(f"ENV SHOPIFY_ACCESS_TOKEN exists: {'SHOPIFY_ACCESS_TOKEN' in os.environ}")
        return jsonify({'error': 'Authentication required. Please reinstall the app.'}), 401
    
    try:
        # Fetch real products from Shopify
        url = f"https://{shop}/admin/api/2024-01/products.json?limit=250"
        headers = {'X-Shopify-Access-Token': access_token}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            error_detail = {
                'error': f'Shopify API error: {response.status_code}',
                'shop': shop,
                'token_exists': bool(access_token),
                'token_prefix': access_token[:15] + '...' if access_token else 'None',
                'response_text': response.text[:200] if response.text else 'No response text'
            }
            print(f"Shopify API Error: {error_detail}")
            return jsonify(error_detail), 500
        
        products = response.json().get('products', [])
        
        # Load review tracking
        review_tracking = load_review_tracking()
        
        # Format products with review data
        products_data = []
        for product in products:
            product_id = str(product['id'])
            
            # Get review counts
            live_reviews = get_reviews_io_count(product)
            if live_reviews > 0:
                print(f"Product {product_id} ({product['title'][:30]}): {live_reviews} reviews")
            generated_reviews = review_tracking.get(product_id, {}).get('count', 0)
            
            products_data.append({
                'id': product_id,
                'title': product['title'],
                'handle': product['handle'],
                'image': product['images'][0]['src'] if product.get('images') else None,
                'live_reviews': live_reviews,
                'generated_reviews': generated_reviews,
                'total_reviews': live_reviews + generated_reviews,
                'created_at': product.get('created_at')
            })
        
        # Sort by created_at (newest first)
        products_data.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({'products': products_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/<product_id>', methods=['POST'])
def generate_reviews(product_id):
    """Generate reviews for a specific product"""
    shop = session.get('shop')
    access_token = session.get('access_token')
    
    # Fallback for testing
    if not shop:
        shop = request.args.get('shop', 'fugafashion.myshopify.com')
    
    # Temporary: For fugafashion, use the existing access token
    if shop == 'fugafashion.myshopify.com' and not access_token:
        access_token = os.environ.get('PRIVATE_APP_TOKEN', os.environ.get('SHOPIFY_ACCESS_TOKEN', ''))
    
    if not shop or not access_token:
        return jsonify({'error': 'Authentication required. Please reinstall the app.'}), 401
    
    try:
        data = request.json
        review_count = data.get('count', 5)
        
        # Fetch product details
        url = f"https://{shop}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': access_token}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': 'Product not found'}), 404
        
        product = response.json()['product']
        
        # Generate reviews using the advanced algorithm
        reviews = generate_advanced_reviews(product, review_count)
        
        # Save to CSV for Reviews.io import
        filename = save_reviews_csv(reviews, product_id)
        
        # Optionally post directly to Reviews.io (if configured)
        reviews_io_result = None
        post_to_reviews_io = data.get('post_to_reviews_io', False)
        
        if post_to_reviews_io:
            from reviews_io_integration import post_reviews_to_reviews_io
            reviews_io_result = post_reviews_to_reviews_io(reviews)
        
        # Optionally post to Klaviyo Reviews API
        klaviyo_result = None
        post_to_klaviyo = data.get('post_to_klaviyo', False)
        
        if post_to_klaviyo:
            klaviyo_result = post_reviews_to_klaviyo(reviews)
        
        # Update tracking
        review_tracking = load_review_tracking()
        if product_id not in review_tracking:
            review_tracking[product_id] = {'count': 0}
        review_tracking[product_id]['count'] += len(reviews)
        review_tracking[product_id]['last_generated'] = datetime.now().isoformat()
        save_review_tracking(review_tracking)
        
        response_data = {
            'success': True,
            'count': len(reviews),
            'filename': filename,
            'product_name': product['title']
        }
        
        if reviews_io_result:
            response_data['reviews_io'] = reviews_io_result
        
        if klaviyo_result:
            response_data['klaviyo'] = klaviyo_result
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Review Generation Logic (ported from old_review.py)
def generate_advanced_reviews(product, count=5):
    """Generate sophisticated reviews using the original algorithm"""
    # Import review generation components
    from review_generator import (
        REVIEW_TITLES, FIRST_NAMES, USERNAMES,
        generate_username, generate_reviewer_info, generate_review_content
    )
    
    reviews = []
    
    for i in range(count):
        # Language distribution: 50% EN, 30% DE, 20% EN  
        lang = random.choices(["en", "de", "en"], weights=[50, 30, 20])[0]
        
        # Rating distribution: 60% 5-star, 30% 4-star, 10% 3-star
        rating = random.choices([5, 4, 3], weights=[60, 30, 10])[0]
        
        # Generate reviewer
        name, email, location = generate_reviewer_info(lang)
        
        # Review title
        title = random.choice(REVIEW_TITLES[lang][rating])
        
        # Review content
        content = generate_review_content(product, rating, lang)
        
        # Random date in last 36 months
        days_ago = random.randint(1, 36 * 30)
        review_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        reviews.append({
            'product_id': str(product['id']),
            'product_handle': product['handle'],
            'product_name': product['title'],
            'reviewer_name': name,
            'reviewer_email': email,
            'reviewer_location': location,
            'review_title': title,
            'review_content': content,
            'review_date': review_date,
            'rating': str(rating),
            'status': 'Published',
            'verified': 'Yes' if random.random() > 0.05 else 'No',
            'image_urls': '',
            'reply_content': '',
            'reply_date': '',
            'is_store_review': 'false'
        })
    
    return reviews

def get_reviews_io_count(product):
    """Get review count from Reviews.io API"""
    from reviews_io_integration import get_reviews_io_count as get_count
    return get_count(product)

def load_review_tracking():
    """Load review tracking data"""
    if os.path.exists('review_tracking.json'):
        with open('review_tracking.json', 'r') as f:
            return json.load(f)
    return {}

def save_review_tracking(data):
    """Save review tracking data"""
    with open('review_tracking.json', 'w') as f:
        json.dump(data, f, indent=2)

def save_reviews_csv(reviews, product_id):
    """Save reviews to CSV file"""
    filename = f'reviews_{product_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    os.makedirs('exports', exist_ok=True)
    
    with open(f'exports/{filename}', 'w', newline='', encoding='utf-8') as f:
        if reviews:
            writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
            writer.writeheader()
            writer.writerows(reviews)
    
    return filename

def post_reviews_to_klaviyo(reviews):
    """Post generated reviews directly to Klaviyo Reviews API"""
    try:
        klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        if not klaviyo_api_key:
            return {'error': 'Klaviyo API key not configured', 'total_created': 0, 'total_errors': len(reviews)}
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {klaviyo_api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'revision': '2024-10-15'
        }
        
        results = {
            'success': [],
            'errors': [],
            'total_created': 0,
            'total_errors': 0
        }
        
        for review in reviews:
            try:
                # Format for Klaviyo Reviews API
                review_data = {
                    "data": {
                        "type": "review",
                        "attributes": {
                            "rating": int(float(review.get('rating', 5))),
                            "title": review.get('review_title', ''),
                            "body": review.get('review_content', ''),
                            "reviewer_name": review.get('reviewer_name', ''),
                            "reviewer_email": review.get('reviewer_email', ''),
                            "created": review.get('review_date', datetime.now().strftime('%Y-%m-%d')),
                            "verified": review.get('verified', 'Yes') == 'Yes'
                        },
                        "relationships": {
                            "item": {
                                "data": {
                                    "type": "catalog-item",
                                    "id": f"$shopify:::$default:::{review.get('product_id')}"
                                }
                            }
                        }
                    }
                }
                
                # Post to Klaviyo Reviews API
                response = requests.post(
                    'https://a.klaviyo.com/api/reviews/',
                    headers=headers,
                    json=review_data
                )
                
                if response.status_code in [200, 201]:
                    results['success'].append(response.json())
                    results['total_created'] += 1
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    results['errors'].append({
                        'review': review.get('review_title', 'Untitled'),
                        'error': error_msg
                    })
                    results['total_errors'] += 1
                    
            except Exception as e:
                results['errors'].append({
                    'review': review.get('review_title', 'Untitled'),
                    'error': str(e)
                })
                results['total_errors'] += 1
        
        return results
        
    except Exception as e:
        return {
            'error': str(e),
            'total_created': 0,
            'total_errors': len(reviews)
        }

@app.route('/webhooks/app/uninstalled', methods=['POST'])
def app_uninstalled():
    """Handle app uninstallation"""
    # Verify webhook
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    if not verify_webhook(request.data, hmac_header):
        return "Unauthorized", 401
    
    # Clean up app data for this shop
    webhook_data = request.json
    shop = webhook_data.get('domain')
    
    # TODO: Clean up database records for this shop
    
    return "OK", 200

@app.route('/download/<filename>')
def download(filename):
    """Download generated CSV files"""
    try:
        file_path = f'exports/{filename}'
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': f'File not found: {filename}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)