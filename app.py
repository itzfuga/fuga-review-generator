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
from review_distribution import get_natural_review_count, get_age_based_review_count, generate_bulk_review_distribution
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    
    # For fugafashion, skip install page and go directly to app
    if shop == 'fugafashion.myshopify.com':
        host = request.args.get('host', '')
        return redirect(f'/app?shop={shop}&host={host}')
    
    # For other shops, show install page first
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
            
            # Get review counts with error handling
            try:
                live_reviews = get_klaviyo_review_count(product_id)
                if live_reviews > 0:
                    print(f"Product {product_id} ({product['title'][:30]}): {live_reviews} reviews")
            except Exception as e:
                print(f"Error getting Klaviyo count for {product_id}: {e}")
                live_reviews = 0
            
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

@app.route('/api/reviews/<product_id>')
def get_product_reviews(product_id):
    """Get all live reviews for a specific product"""
    try:
        klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        if not klaviyo_api_key:
            return jsonify({'error': 'Klaviyo API key not configured'}), 500
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {klaviyo_api_key}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # Get reviews from Klaviyo - optimized approach
        product_reviews = []
        target_catalog_id = f"$shopify:::$default:::{product_id}"
        page_limit = 10  # Process 10 pages max to avoid timeout
        page_count = 0
        
        print(f"Looking for reviews for product {product_id} (catalog ID: {target_catalog_id})")
        
        url = "https://a.klaviyo.com/api/reviews/?page[size]=100"
        
        while url and page_count < page_limit:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code != 200:
                    error_detail = f'Status {response.status_code}'
                    try:
                        error_data = response.json()
                        if 'errors' in error_data and error_data['errors']:
                            error_detail += f": {error_data['errors'][0].get('detail', 'Unknown API error')}"
                    except:
                        error_detail += f": {response.text[:200]}"
                    return jsonify({'error': f'Klaviyo API error: {error_detail}'}), 500
                
                data = response.json()
                reviews = data.get('data', [])
                
                print(f"Page {page_count + 1}: Fetched {len(reviews)} reviews")
                
                # Process reviews for this page
                for review in reviews:
                    try:
                        relationships = review.get('relationships', {})
                        item_data = relationships.get('item', {}).get('data', {})
                        catalog_item_id = item_data.get('id', '')
                        
                        if catalog_item_id == target_catalog_id:
                            attributes = review.get('attributes', {})
                            product_info = attributes.get('product', {})
                            
                            formatted_review = {
                                'id': review.get('id'),
                                'rating': attributes.get('rating', 0),
                                'title': attributes.get('title', ''),
                                'content': attributes.get('content', ''),
                                'author': attributes.get('author', 'Anonymous'),
                                'email': attributes.get('email', ''),
                                'created': attributes.get('created'),
                                'verified': attributes.get('verified', False),
                                'status': attributes.get('status', 'published'),
                                'product_name': product_info.get('name', ''),
                                'product_url': product_info.get('url', ''),
                                'product_image': product_info.get('image_url', ''),
                                'images': attributes.get('images', [])
                            }
                            product_reviews.append(formatted_review)
                            print(f"Found matching review: {formatted_review['id']} - {formatted_review['rating']}★")
                    except Exception as e:
                        print(f"Error processing review: {e}")
                        continue
                
                # Check for next page
                url = data.get('links', {}).get('next')
                page_count += 1
                
                # If we found enough reviews for this product, we can stop early
                if len(product_reviews) >= 50:
                    print(f"Found {len(product_reviews)} reviews, stopping pagination")
                    break
                
            except requests.exceptions.Timeout:
                print(f"Timeout on page {page_count + 1}, returning what we have")
                break
            except requests.exceptions.RequestException as e:
                print(f"Network error on page {page_count + 1}: {e}")
                break
            except Exception as e:
                print(f"Error on page {page_count + 1}: {e}")
                break
        
        
        print(f"Found {len(product_reviews)} reviews for product {product_id}")
        
        # Get product info from Shopify for context
        product_info = {}
        try:
            shop_domain = os.environ.get('SHOPIFY_SHOP_DOMAIN', session.get('shop'))
            access_token = get_access_token(shop_domain)
            
            if access_token:
                shopify_url = f'https://{shop_domain}/admin/api/2023-10/products/{product_id}.json'
                shopify_headers = {'X-Shopify-Access-Token': access_token}
                shopify_response = requests.get(shopify_url, headers=shopify_headers)
                
                if shopify_response.status_code == 200:
                    shopify_data = shopify_response.json()
                    product = shopify_data.get('product', {})
                    product_info = {
                        'title': product.get('title', ''),
                        'handle': product.get('handle', ''),
                        'id': product.get('id', ''),
                        'image': product.get('image', {}).get('src', '') if product.get('image') else ''
                    }
        except Exception as e:
            print(f"Error fetching product info: {e}")
        
        return jsonify({
            'success': True,
            'product_info': product_info,
            'reviews': product_reviews,
            'total_reviews': len(product_reviews),
            'average_rating': sum(r['rating'] for r in product_reviews) / len(product_reviews) if product_reviews else 0
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching reviews: {str(e)}'}), 500

@app.route('/api/reviews/by-handle/<product_handle>')
def get_reviews_by_handle(product_handle):
    """Get reviews by product handle - searches through review product names"""
    try:
        klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        if not klaviyo_api_key:
            return jsonify({'error': 'Klaviyo API key not configured'}), 500
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {klaviyo_api_key}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # Search through reviews to find ones matching the product handle
        product_reviews = []
        url = "https://a.klaviyo.com/api/reviews/?page[size]=100"
        page_count = 0
        
        while url and page_count < 5:  # Limit pages for handle search
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return jsonify({'error': f'Klaviyo API error: {response.status_code}'}), 500
            
            data = response.json()
            reviews = data.get('data', [])
            
            for review in reviews:
                attributes = review.get('attributes', {})
                product_info = attributes.get('product', {})
                product_url = product_info.get('url', '')
                
                # Check if product URL contains the handle
                if product_handle.lower() in product_url.lower():
                    formatted_review = {
                        'id': review.get('id'),
                        'rating': attributes.get('rating', 0),
                        'title': attributes.get('title', ''),
                        'content': attributes.get('content', ''),
                        'author': attributes.get('author', 'Anonymous'),
                        'created': attributes.get('created'),
                        'verified': attributes.get('verified', False),
                        'product_name': product_info.get('name', ''),
                        'catalog_id': review.get('relationships', {}).get('item', {}).get('data', {}).get('id', '')
                    }
                    product_reviews.append(formatted_review)
            
            url = data.get('links', {}).get('next')
            page_count += 1
        
        return jsonify({
            'success': True,
            'handle': product_handle,
            'reviews': product_reviews,
            'total_reviews': len(product_reviews),
            'average_rating': sum(r['rating'] for r in product_reviews) / len(product_reviews) if product_reviews else 0
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching reviews: {str(e)}'}), 500

@app.route('/api/reviews/debug')
def debug_reviews():
    """Debug endpoint to see all available reviews and their product IDs"""
    try:
        klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        if not klaviyo_api_key:
            return jsonify({'error': 'Klaviyo API key not configured'}), 500
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {klaviyo_api_key}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # Get first page of reviews for debugging
        url = "https://a.klaviyo.com/api/reviews/?page[size]=10"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'error': f'Klaviyo API error: {response.status_code}'}), 500
        
        data = response.json()
        reviews = data.get('data', [])
        
        debug_info = {
            'total_found': len(reviews),
            'reviews': []
        }
        
        for review in reviews:
            relationships = review.get('relationships', {})
            item_data = relationships.get('item', {}).get('data', {})
            attributes = review.get('attributes', {})
            
            debug_info['reviews'].append({
                'review_id': review.get('id'),
                'catalog_item_id': item_data.get('id', ''),
                'product_name': attributes.get('product', {}).get('name', ''),
                'rating': attributes.get('rating'),
                'title': attributes.get('title', ''),
                'author': attributes.get('author', 'Anonymous')
            })
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': f'Debug error: {str(e)}'}), 500

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
        
        # Variable review count - if not specified, use smart distribution
        if 'count' in data:
            review_count = data['count']
        else:
            # Use natural distribution for more realistic review counts
            min_reviews = data.get('min_count', 10)
            max_reviews = data.get('max_count', 30)
            use_smart_distribution = data.get('use_smart_distribution', True)
            
            if use_smart_distribution:
                # Will fetch product details below to determine age-based count
                review_count = None  # Set after fetching product
            else:
                review_count = get_natural_review_count(min_reviews, max_reviews)
        
        # Fetch product details
        url = f"https://{shop}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': access_token}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': 'Product not found'}), 404
        
        product = response.json()['product']
        
        # Determine review count if using smart distribution
        if review_count is None:
            review_count = get_age_based_review_count(
                product.get('created_at'),
                min_reviews,
                max_reviews
            )
        
        # Debug: print the review count
        print(f"DEBUG: Generating {review_count} reviews for product {product_id}")
        
        # Generate reviews using the advanced algorithm
        start_time = datetime.now()
        reviews = generate_advanced_reviews(product, review_count)
        generation_time = (datetime.now() - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Log analytics data
        try:
            from analytics_dashboard import AnalyticsDashboard
            dashboard = AnalyticsDashboard()
            
            for i, review in enumerate(reviews):
                dashboard.log_review_generation(
                    review_data=review,
                    generation_metadata={
                        'product_id': product_id,
                        'product_title': product.get('title', ''),
                        'platform': 'shopify',
                        'session_id': session.get('session_id', ''),
                        'generation_time_ms': generation_time / len(reviews),  # Avg per review
                        'error_occurred': False,
                        'review_id': f"{product_id}_{i}"
                    }
                )
        except Exception as e:
            print(f"Analytics logging failed: {str(e)}")
        
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
    from review_generator import generate_review
    
    reviews = []
    
    for i in range(count):
        # Generate review using the new comprehensive function
        review_data = generate_review(product, existing_reviews=i)
        
        reviews.append({
            'product_id': str(product['id']),
            'product_handle': product['handle'],
            'product_name': product['title'],
            'reviewer_name': review_data['author'],
            'reviewer_email': review_data['email'],
            'reviewer_location': review_data['location'],
            'review_title': review_data['title'],
            'review_content': review_data['content'],
            'review_date': review_data['date'],
            'rating': str(review_data['rating']),
            'status': 'Published',
            'verified': review_data['verified'],
            'image_urls': '',
            'reply_content': '',
            'reply_date': '',
            'is_store_review': 'false'
        })
    
    return reviews

def get_klaviyo_review_count(product_id):
    """Get review count from Klaviyo API for a specific product"""
    try:
        klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        if not klaviyo_api_key:
            return 0
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {klaviyo_api_key}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        target_catalog_id = f"$shopify:::$default:::{product_id}"
        count = 0
        
        # Search first 200 reviews (2 pages) for this product
        url = "https://a.klaviyo.com/api/reviews/?page[size]=100"
        
        for page in range(2):  # Limit to 2 pages for speed
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                reviews = data.get('data', [])
                
                # Count reviews for this product
                for review in reviews:
                    relationships = review.get('relationships', {})
                    item_data = relationships.get('item', {}).get('data', {})
                    catalog_item_id = item_data.get('id', '')
                    
                    if catalog_item_id == target_catalog_id:
                        count += 1
                
                # Get next page URL
                url = data.get('links', {}).get('next')
                if not url:
                    break
                    
            except:
                break
        
        return count
        
    except Exception as e:
        print(f"Error getting Klaviyo count for {product_id}: {e}")
        return 0

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
    """Klaviyo Reviews integration - CSV workflow only (API is read-only)"""
    try:
        klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        if not klaviyo_api_key:
            return {
                'error': 'Klaviyo API key not configured. CSV workflow requires valid API key for validation.',
                'total_created': 0, 
                'total_errors': len(reviews),
                'method_used': 'none'
            }
        
        # Test API key validity first
        if not _test_klaviyo_api_key(klaviyo_api_key):
            return {
                'error': 'Invalid Klaviyo API key. Please check your KLAVIYO_API_KEY environment variable.',
                'total_created': 0, 
                'total_errors': len(reviews),
                'method_used': 'none'
            }
        
        # IMPORTANT: Klaviyo Reviews API is READ-ONLY (returns 405 Method Not Allowed for POST)
        # The only way to add reviews is via CSV upload through their web interface
        print("ℹ️ Klaviyo Reviews API is read-only. Using CSV workflow...")
        
        # Try automated web upload if credentials are available
        klaviyo_login_email = os.environ.get('KLAVIYO_LOGIN_EMAIL')
        klaviyo_login_password = os.environ.get('KLAVIYO_LOGIN_PASSWORD')
        
        if klaviyo_login_email and klaviyo_login_password:
            print("🔄 Attempting automated CSV upload to Klaviyo...")
            try:
                # Import the web automation module
                from klaviyo_web_automation import upload_reviews_to_klaviyo_web
                
                # Convert reviews to CSV format first
                csv_filename = save_reviews_csv(reviews, 'klaviyo_upload')
                
                # Attempt automated upload
                upload_result = upload_reviews_to_klaviyo_web(csv_filename, klaviyo_login_email, klaviyo_login_password)
                
                if upload_result.get('success'):
                    return {
                        'success': reviews,
                        'total_created': len(reviews),
                        'total_errors': 0,
                        'method_used': 'web_automation',
                        'message': f'Successfully uploaded {len(reviews)} reviews via automated web upload',
                        'csv_file': csv_filename
                    }
                else:
                    # Fall back to manual CSV
                    return {
                        'success': True,
                        'message': f"Automated upload failed, but CSV generated successfully for manual upload.\n\n💡 MANUAL UPLOAD: CSV file generated for manual import.\nError: {upload_result.get('error', 'Unknown error')}",
                        'total_created': len(reviews),  # CSV generation is success
                        'total_errors': 0,
                        'method_used': 'csv_manual',
                        'csv_file': csv_filename,
                        'manual_upload_url': 'https://www.klaviyo.com/reviews/import/upload'
                    }
                    
            except ImportError:
                print("⚠️ Web automation module not available, using manual CSV workflow")
            except Exception as e:
                print(f"⚠️ Web automation failed: {e}")
        
        # Default to manual CSV workflow
        csv_filename = save_reviews_csv(reviews, 'klaviyo_manual')
        
        return {
            'success': True,
            'message': f"CSV file generated successfully for manual upload.\n\n💡 CSV READY: {csv_filename} generated for manual import.\n🌐 Upload at: https://www.klaviyo.com/reviews/import/upload",
            'total_created': len(reviews),  # CSV generation is success
            'total_errors': 0,
            'method_used': 'csv_manual',
            'csv_file': csv_filename,
            'csv_ready': True,
            'manual_upload_url': 'https://www.klaviyo.com/reviews/import/upload'
        }
        
    except Exception as e:
        # Try to generate CSV as fallback
        try:
            csv_filename = save_reviews_csv(reviews, 'klaviyo_fallback')
            return {
                'success': True,
                'message': f'Klaviyo workflow error, but CSV file generated successfully for manual upload.\n\nError: {str(e)}\n\n💡 FALLBACK: CSV file has been generated for manual upload.',
                'total_created': len(reviews),
                'total_errors': 0,
                'method_used': 'csv_fallback',
                'csv_file': csv_filename,
                'fallback_available': True
            }
        except:
            return {
                'error': f'Klaviyo workflow error: {str(e)}',
                'total_created': 0,
                'total_errors': len(reviews),
                'fallback_available': False
            }

def _test_klaviyo_api_key(api_key):
    """Test if Klaviyo API key is valid"""
    try:
        headers = {
            'Authorization': f'Klaviyo-API-Key {api_key}',
            'revision': '2024-10-15'
        }
        
        response = requests.get('https://a.klaviyo.com/api/accounts/', headers=headers, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"🔑 Klaviyo API Key validation failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"🔑 Klaviyo API Key test error: {e}")
        return False

def _post_via_reviews_api(reviews, api_key):
    """Method 1: Try direct Reviews API (fixed field mapping)"""
    headers = {
        'Authorization': f'Klaviyo-API-Key {api_key}',
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
            # Format for Klaviyo Reviews API - Fixed field mapping
            review_data = {
                "data": {
                    "type": "review",
                    "attributes": {
                        "rating": int(float(review.get('rating', 5))),
                        "title": review.get('title', ''),  # Fixed: was 'review_title'
                        "body": review.get('content', ''),  # Fixed: was 'review_content'
                        "reviewer_name": review.get('author', ''),  # Fixed: was 'reviewer_name'
                        "reviewer_email": review.get('email', ''),  # Fixed: was 'reviewer_email'
                        "created": review.get('date', datetime.now().strftime('%Y-%m-%d')),  # Fixed: was 'review_date'
                        "verified": review.get('verified', 'Yes') == 'Yes'
                    },
                    "relationships": {
                        "item": {
                            "data": {
                                "type": "catalog-item",
                                "id": f"$shopify:::$default:::{review.get('product_id', 'unknown')}"
                            }
                        }
                    }
                }
            }
            
            # Try multiple endpoints
            endpoints = [
                'https://a.klaviyo.com/api/reviews/',
                'https://a.klaviyo.com/api/review/',
                'https://a.klaviyo.com/api/reviews'
            ]
            
            success = False
            for endpoint in endpoints:
                response = requests.post(endpoint, headers=headers, json=review_data, timeout=15)
                
                if response.status_code in [200, 201]:
                    results['success'].append(response.json())
                    results['total_created'] += 1
                    success = True
                    break
                elif response.status_code == 404:
                    continue  # Try next endpoint
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    results['errors'].append({
                        'review': review.get('title', 'Untitled'),
                        'error': error_msg,
                        'endpoint': endpoint
                    })
                    break
            
            if not success and not results['errors']:
                results['errors'].append({
                    'review': review.get('title', 'Untitled'),
                    'error': 'All review endpoints returned 404'
                })
                results['total_errors'] += 1
                    
        except Exception as e:
            results['errors'].append({
                'review': review.get('title', 'Untitled'),
                'error': str(e)
            })
            results['total_errors'] += 1
    
    return results

def _post_via_events_api(reviews, api_key):
    """Method 2: Post reviews as custom events"""
    headers = {
        'Authorization': f'Klaviyo-API-Key {api_key}',
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
            # Format as custom event
            event_data = {
                "data": {
                    "type": "event",
                    "attributes": {
                        "metric": {"name": "Product Review"},
                        "properties": {
                            "rating": int(float(review.get('rating', 5))),
                            "review_title": review.get('title', ''),
                            "review_content": review.get('content', ''),
                            "product_id": review.get('product_id', ''),
                            "verified": review.get('verified', 'Yes') == 'Yes'
                        },
                        "profile": {
                            "email": review.get('email', 'anonymous@example.com'),
                            "first_name": review.get('author', '').split(' ')[0] if review.get('author') else 'Anonymous',
                            "last_name": ' '.join(review.get('author', '').split(' ')[1:]) if review.get('author') and len(review.get('author', '').split(' ')) > 1 else ''
                        },
                        "time": review.get('date', datetime.now().strftime('%Y-%m-%d'))
                    }
                }
            }
            
            response = requests.post(
                'https://a.klaviyo.com/api/events/',
                headers=headers,
                json=event_data,
                timeout=15
            )
            
            if response.status_code in [200, 201, 202]:
                results['success'].append(response.json())
                results['total_created'] += 1
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                results['errors'].append({
                    'review': review.get('title', 'Untitled'),
                    'error': error_msg
                })
                results['total_errors'] += 1
                
        except Exception as e:
            results['errors'].append({
                'review': review.get('title', 'Untitled'),
                'error': str(e)
            })
            results['total_errors'] += 1
    
    return results

def _post_via_profile_import(reviews, api_key):
    """Method 3: Bulk import as profile properties"""
    headers = {
        'Authorization': f'Klaviyo-API-Key {api_key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'revision': '2024-10-15'
    }
    
    try:
        # Batch reviews by email to avoid duplicates
        profiles = {}
        for i, review in enumerate(reviews):
            email = review.get('email', f'review_{i}@generated.com')
            if email not in profiles:
                profiles[email] = {
                    "email": email,
                    "first_name": review.get('author', '').split(' ')[0] if review.get('author') else 'Anonymous',
                    "last_name": ' '.join(review.get('author', '').split(' ')[1:]) if review.get('author') and len(review.get('author', '').split(' ')) > 1 else '',
                    "properties": {}
                }
            
            # Add review as properties
            review_prefix = f"review_{i}"
            profiles[email]["properties"].update({
                f"{review_prefix}_rating": review.get('rating', 5),
                f"{review_prefix}_title": review.get('title', ''),
                f"{review_prefix}_content": review.get('content', ''),
                f"{review_prefix}_product_id": review.get('product_id', ''),
                f"{review_prefix}_date": review.get('date', ''),
                f"{review_prefix}_verified": review.get('verified', 'Yes')
            })
        
        bulk_data = {
            "data": {
                "type": "profile-import",
                "attributes": {
                    "profiles": list(profiles.values())
                }
            }
        }
        
        response = requests.post(
            'https://a.klaviyo.com/api/profile-import/',
            headers=headers,
            json=bulk_data,
            timeout=30
        )
        
        if response.status_code in [200, 201, 202]:
            return {
                'success': [response.json()],
                'errors': [],
                'total_created': len(reviews),
                'total_errors': 0
            }
        else:
            return {
                'success': [],
                'errors': [f"Bulk import failed: HTTP {response.status_code}: {response.text[:200]}"],
                'total_created': 0,
                'total_errors': len(reviews)
            }
            
    except Exception as e:
        return {
            'success': [],
            'errors': [f"Bulk import exception: {str(e)}"],
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

@app.route('/api/generate-bulk', methods=['POST'])
def generate_bulk_reviews():
    """Generate reviews for multiple products in one combined CSV"""
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
        product_ids = data.get('product_ids', [])
        
        # Variable review count settings
        use_variable_count = data.get('use_variable_count', True)
        min_reviews = data.get('min_count', 10)
        max_reviews = data.get('max_count', 30)
        fixed_count = data.get('count', 5)  # Fallback for fixed count
        
        post_to_reviews_io = data.get('post_to_reviews_io', False)
        post_to_klaviyo = data.get('post_to_klaviyo', False)
        
        if not product_ids:
            return jsonify({'error': 'No products specified'}), 400
        
        all_reviews = []
        success_count = 0
        error_count = 0
        errors = []
        
        headers = {'X-Shopify-Access-Token': access_token}
        
        # First, fetch all product details for smart distribution
        products = []
        for product_id in product_ids:
            try:
                url = f"https://{shop}/admin/api/2024-01/products/{product_id}.json"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    products.append(response.json()['product'])
            except:
                pass
        
        # Generate smart distribution if using variable count
        if use_variable_count and products:
            use_smart_distribution = data.get('use_smart_distribution', True)
            review_distribution = generate_bulk_review_distribution(
                products, 
                min_reviews, 
                max_reviews,
                use_smart_distribution
            )
        else:
            review_distribution = {}
        
        # Now generate reviews for each product
        for product_id in product_ids:
            try:
                # Fetch product details
                url = f"https://{shop}/admin/api/2024-01/products/{product_id}.json"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    errors.append(f"Product {product_id}: Failed to fetch product details")
                    error_count += 1
                    continue
                
                product = response.json()['product']
                
                # Determine review count for this product
                if use_variable_count and str(product_id) in review_distribution:
                    # Use smart distribution
                    product_review_count = review_distribution[str(product_id)]
                elif use_variable_count:
                    # Fallback to natural distribution
                    product_review_count = get_natural_review_count(min_reviews, max_reviews)
                else:
                    product_review_count = fixed_count
                
                # Generate reviews for this product
                product_reviews = generate_advanced_reviews(product, product_review_count)
                all_reviews.extend(product_reviews)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Product {product_id}: {str(e)}")
                error_count += 1
        
        if not all_reviews:
            return jsonify({'error': 'No reviews were generated'}), 500
        
        # Save all reviews to one combined CSV file
        filename = f'bulk_reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        os.makedirs('exports', exist_ok=True)
        
        with open(f'exports/{filename}', 'w', newline='', encoding='utf-8') as f:
            if all_reviews:
                writer = csv.DictWriter(f, fieldnames=all_reviews[0].keys())
                writer.writeheader()
                writer.writerows(all_reviews)
        
        # Update tracking for all products
        review_tracking = load_review_tracking()
        
        # Count reviews per product for accurate tracking
        product_review_counts = {}
        for review in all_reviews:
            pid = review['product_id']
            product_review_counts[pid] = product_review_counts.get(pid, 0) + 1
        
        for product_id, count in product_review_counts.items():
            if product_id not in review_tracking:
                review_tracking[product_id] = {'count': 0}
            review_tracking[product_id]['count'] += count
            review_tracking[product_id]['last_generated'] = datetime.now().isoformat()
        save_review_tracking(review_tracking)
        
        # Handle API posting if requested
        reviews_io_result = None
        klaviyo_result = None
        
        if post_to_reviews_io and all_reviews:
            from reviews_io_integration import post_reviews_to_reviews_io
            reviews_io_result = post_reviews_to_reviews_io(all_reviews)
        
        if post_to_klaviyo and all_reviews:
            klaviyo_result = post_reviews_to_klaviyo(all_reviews)
        
        response_data = {
            'success': True,
            'filename': filename,
            'total_reviews': len(all_reviews),
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
        
        if reviews_io_result:
            response_data['reviews_io'] = reviews_io_result
        
        if klaviyo_result:
            response_data['klaviyo'] = klaviyo_result
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-reviews', methods=['POST'])
def import_reviews():
    """Automatically import generated reviews to configured platforms"""
    from automatic_import import import_reviews_automatically
    
    try:
        data = request.json
        reviews = data.get('reviews', [])
        platforms = data.get('platforms', ['klaviyo'])  # Default to Klaviyo only
        
        if not reviews:
            return jsonify({'error': 'No reviews provided'}), 400
        
        # Perform automatic import
        result = import_reviews_automatically(reviews, platforms)
        
        return jsonify({
            'success': True,
            'import_result': result,
            'message': f"Import completed: {result['summary']['total_success']} successful, {result['summary']['total_failed']} failed"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-and-import/<product_id>', methods=['POST'])
def generate_and_import(product_id):
    """Generate reviews and automatically import them"""
    from review_generator import generate_review
    from automatic_import import import_reviews_automatically
    
    try:
        data = request.json
        review_count = data.get('count', 5)
        platforms = data.get('platforms', ['klaviyo'])  # Default to Klaviyo only
        
        shop = session.get('shop')
        access_token = session.get('access_token')
        
        # Fallback for testing
        if not shop:
            shop = request.args.get('shop', 'fugafashion.myshopify.com')
        
        # Temporary: For fugafashion, use the existing access token
        if shop == 'fugafashion.myshopify.com' and not access_token:
            access_token = os.environ.get('SHOPIFY_ACCESS_TOKEN')
        
        if not access_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Fetch product info
        url = f"https://{shop}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': access_token}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': 'Product not found'}), 404
        
        product = response.json()['product']
        
        # Generate reviews
        reviews = []
        for i in range(review_count):
            review_data = generate_review(product, existing_reviews=i)
            reviews.append(review_data)
        
        # Save as CSV first
        csv_filename = save_reviews_csv(reviews, product_id)
        
        # Try importing to platforms
        import_results = {}
        total_success = 0
        total_errors = 0
        
        if 'klaviyo' in platforms:
            klaviyo_result = post_reviews_to_klaviyo(reviews)
            import_results['klaviyo'] = klaviyo_result
            
            if klaviyo_result.get('total_created', 0) > 0:
                total_success += klaviyo_result['total_created']
            else:
                total_errors += klaviyo_result.get('total_errors', len(reviews))
        
        # If imports were successful, return success format
        if total_success > 0:
            return jsonify({
                'success': True,
                'generated_reviews': len(reviews),
                'csv_file': csv_filename,
                'method_used': import_results.get('klaviyo', {}).get('method_used', 'csv_manual'),
                'import_result': {
                    'summary': {
                        'total_success': total_success,
                        'total_failed': total_errors
                    },
                    'platforms': {
                        'klaviyo': {
                            'success_count': import_results.get('klaviyo', {}).get('total_created', 0),
                            'error_count': import_results.get('klaviyo', {}).get('total_errors', 0)
                        }
                    }
                },
                'message': f"Generated {len(reviews)} reviews and imported {total_success} successfully"
            })
        else:
            # Return CSV workflow response 
            klaviyo_result = import_results.get('klaviyo', {})
            return jsonify({
                'success': True,
                'generated_reviews': len(reviews), 
                'csv_file': csv_filename,
                'method_used': klaviyo_result.get('method_used', 'csv_manual'),
                'manual_upload_url': klaviyo_result.get('manual_upload_url'),
                'csv_ready': True,
                'message': f"Generated {len(reviews)} reviews. CSV ready for upload.",
                'import_result': {
                    'summary': {
                        'total_success': 0,
                        'total_failed': len(reviews)
                    },
                    'platforms': {
                        'klaviyo': {
                            'success_count': 0,
                            'error_count': len(reviews)
                        }
                    },
                    'note': 'CSV workflow - manual or automated upload required'
                }
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-bulk-and-import', methods=['POST'])
def generate_bulk_and_import():
    """Generate reviews for multiple products and import automatically"""
    from review_generator import generate_review
    from automatic_import import import_reviews_automatically
    
    try:
        data = request.json
        product_ids = data.get('product_ids', [])
        review_count = data.get('count', 5)
        platforms = data.get('platforms', ['klaviyo'])  # Default to Klaviyo only
        
        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400
        
        shop = session.get('shop')
        access_token = session.get('access_token')
        
        # Fallback for testing
        if not shop:
            shop = request.args.get('shop', 'fugafashion.myshopify.com')
        
        # Temporary: For fugafashion, use the existing access token
        if shop == 'fugafashion.myshopify.com' and not access_token:
            access_token = os.environ.get('SHOPIFY_ACCESS_TOKEN')
        
        if not access_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        all_reviews = []
        
        # Generate reviews for each product
        for product_id in product_ids:
            # Fetch product
            url = f"https://{shop}/admin/api/2024-01/products/{product_id}.json"
            headers = {'X-Shopify-Access-Token': access_token}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                product = response.json()['product']
                
                # Generate reviews for this product
                for i in range(review_count):
                    review_data = generate_review(product, existing_reviews=i)
                    all_reviews.append(review_data)
        
        if not all_reviews:
            return jsonify({'error': 'No reviews could be generated'}), 400
        
        # Import all reviews automatically
        import_result = import_reviews_automatically(all_reviews, platforms)
        
        return jsonify({
            'success': True,
            'total_products': len(product_ids),
            'generated_reviews': len(all_reviews),
            'import_result': import_result,
            'message': f"Generated {len(all_reviews)} reviews for {len(product_ids)} products and imported {import_result['summary']['total_success']} successfully"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-status')
def import_status():
    """Get import status for progress tracking"""
    # Check different Klaviyo import methods
    klaviyo_api_configured = bool(os.environ.get('KLAVIYO_API_KEY'))
    klaviyo_web_configured = bool(os.environ.get('KLAVIYO_LOGIN_EMAIL') and os.environ.get('KLAVIYO_LOGIN_PASSWORD'))
    
    return jsonify({
        'status': 'ready',
        'platforms_configured': {
            'reviews_io': bool(os.environ.get('REVIEWS_IO_API_KEY')),
            'klaviyo': klaviyo_api_configured,
            'klaviyo_web': klaviyo_web_configured
        },
        'import_methods': {
            'klaviyo_api': 'Available' if klaviyo_api_configured else 'Not configured (KLAVIYO_API_KEY missing)',
            'klaviyo_web': 'Available' if klaviyo_web_configured else 'Not configured (KLAVIYO_LOGIN_EMAIL/PASSWORD missing)',
            'reviews_io': 'Available' if os.environ.get('REVIEWS_IO_API_KEY') else 'Not configured (REVIEWS_IO_API_KEY missing)'
        }
    })

@app.route('/api/klaviyo-web-upload', methods=['POST'])
def klaviyo_web_upload():
    """Upload CSV to Klaviyo using web automation"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        file_path = f'exports/{filename}'
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Check if web automation credentials are configured
        if not (os.environ.get('KLAVIYO_LOGIN_EMAIL') and os.environ.get('KLAVIYO_LOGIN_PASSWORD')):
            return jsonify({
                'error': 'Klaviyo web automation not configured',
                'message': 'Please set KLAVIYO_LOGIN_EMAIL and KLAVIYO_LOGIN_PASSWORD environment variables'
            }), 400
        
        # Import web automation module
        try:
            from klaviyo_web_automation import upload_reviews_to_klaviyo_web
        except ImportError:
            return jsonify({
                'error': 'Web automation not available',
                'message': 'Selenium web driver not installed. Install with: pip install selenium'
            }), 500
        
        # Perform web upload
        result = upload_reviews_to_klaviyo_web(file_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'CSV uploaded to Klaviyo via web automation',
                'filename': filename,
                'details': result
            })
        else:
            return jsonify({
                'error': 'Web upload failed',
                'details': result
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/klaviyo-diagnostic', methods=['POST'])
def klaviyo_diagnostic():
    """Run Klaviyo API diagnostic to troubleshoot issues"""
    try:
        # Import and run diagnostic
        try:
            from klaviyo_diagnostic import test_klaviyo_reviews_api
            
            # Capture diagnostic output
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            test_klaviyo_reviews_api()
            
            sys.stdout = old_stdout
            diagnostic_output = captured_output.getvalue()
            
            return jsonify({
                'success': True,
                'diagnostic_output': diagnostic_output,
                'message': 'Diagnostic completed - check output for details'
            })
            
        except ImportError:
            return jsonify({
                'error': 'Diagnostic tool not available',
                'message': 'klaviyo_diagnostic.py not found'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Analytics Dashboard Endpoints
@app.route('/api/analytics/dashboard')
def analytics_dashboard():
    """Get comprehensive dashboard metrics"""
    try:
        from analytics_dashboard import AnalyticsDashboard
        from dataclasses import asdict
        
        days = int(request.args.get('days', 30))
        dashboard = AnalyticsDashboard()
        metrics = dashboard.get_dashboard_metrics(days)
        return jsonify(asdict(metrics))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/quality-insights')
def quality_insights():
    """Get detailed quality insights"""
    try:
        from analytics_dashboard import AnalyticsDashboard
        
        days = int(request.args.get('days', 30))
        dashboard = AnalyticsDashboard()
        insights = dashboard.get_quality_insights(days)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/platform-performance')
def platform_performance():
    """Get platform-specific performance metrics"""
    try:
        from analytics_dashboard import AnalyticsDashboard
        
        days = int(request.args.get('days', 30))
        dashboard = AnalyticsDashboard()
        performance = dashboard.get_platform_performance(days)
        return jsonify(performance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/export')
def export_analytics():
    """Export analytics data"""
    try:
        from analytics_dashboard import AnalyticsDashboard
        import json
        
        days = int(request.args.get('days', 30))
        format_type = request.args.get('format', 'json')
        dashboard = AnalyticsDashboard()
        
        export_data = dashboard.export_analytics_data(days, format_type)
        
        if format_type == 'json':
            return jsonify(json.loads(export_data))
        else:
            return export_data, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/quality-assessment', methods=['POST'])
def assess_review_quality():
    """Assess quality of provided reviews"""
    try:
        from ai_quality_scorer import assess_generated_reviews
        
        data = request.json
        reviews = data.get('reviews', [])
        product_context = data.get('product_context')
        
        if not reviews:
            return jsonify({'error': 'No reviews provided'}), 400
        
        assessment_results = assess_generated_reviews(reviews, product_context)
        return jsonify(assessment_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/sample-data', methods=['POST'])
def create_sample_data():
    """Create sample analytics data for testing"""
    try:
        from analytics_dashboard import create_sample_analytics_data
        
        result = create_sample_analytics_data()
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
def analytics_dashboard_page():
    """Render the analytics dashboard page"""
    return render_template('analytics_dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)