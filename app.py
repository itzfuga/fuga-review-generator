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
                    print(f"Klaviyo API Error: {error_msg}")
                    print(f"Request data: {review_data}")
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
        
        # Import automatically
        import_result = import_reviews_automatically(reviews, platforms)
        
        return jsonify({
            'success': True,
            'generated_reviews': len(reviews),
            'import_result': import_result,
            'message': f"Generated {len(reviews)} reviews and imported {import_result['summary']['total_success']} successfully"
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