from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import csv
import random
from datetime import datetime, timedelta
import json
import difflib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Your credentials from environment variables
SHOP_DOMAIN = os.environ.get('SHOPIFY_SHOP_DOMAIN', 'your-shop.myshopify.com')
ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN', 'your-access-token')
KLAVIYO_API_KEY = os.environ.get('KLAVIYO_API_KEY')

# File to track generated reviews
REVIEW_TRACKING_FILE = 'review_tracking.json'
# File to manually track live review counts
LIVE_REVIEW_TRACKING_FILE = 'live_review_counts.json'

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

def load_live_review_counts():
    """Load manually tracked live review counts"""
    if os.path.exists(LIVE_REVIEW_TRACKING_FILE):
        with open(LIVE_REVIEW_TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_live_review_counts(data):
    """Save manually tracked live review counts"""
    with open(LIVE_REVIEW_TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def fuzzy_match_product(target_name, available_keys, threshold=0.6):
    """Find the best fuzzy match for a product name among available keys"""
    target_clean = target_name.lower().strip()
    
    best_match = None
    best_ratio = 0
    
    for key in available_keys:
        key_clean = str(key).lower().strip()
        
        # Try different matching approaches
        ratios = [
            difflib.SequenceMatcher(None, target_clean, key_clean).ratio(),
            difflib.SequenceMatcher(None, target_clean.replace('-', ' '), key_clean.replace('-', ' ')).ratio(),
            # Check if key words are contained
            len([word for word in target_clean.split() if word in key_clean]) / max(len(target_clean.split()), 1)
        ]
        
        max_ratio = max(ratios)
        
        if max_ratio > best_ratio and max_ratio >= threshold:
            best_ratio = max_ratio
            best_match = key
    
    return best_match, best_ratio

def get_csv_review_counts():
    """Get review counts from the CSV export file"""
    try:
        import csv
        review_counts = {}
        csv_file_path = 'review_export_150f0ab9-09fe-445b-8854-d9ee9890ceb0.csv'
        
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    product_id = row.get('product_id', '').strip()
                    product_handle = row.get('product_handle', '').strip()
                    product_name = row.get('product_name', '').strip()
                    status = row.get('status', '').strip()
                    
                    # Only count published reviews
                    if product_id and status == 'published':
                        # Count by product ID (primary)
                        if product_id not in review_counts:
                            review_counts[product_id] = 0
                        review_counts[product_id] += 1
                        
                        # Also count by handle for fallback matching
                        if product_handle and product_handle not in review_counts:
                            review_counts[product_handle] = 0
                        if product_handle:
                            review_counts[product_handle] += 1
        
        print(f"📊 CSV review counts loaded: {len(review_counts)} products, {sum(review_counts.values())} total reviews")
        print(f"📋 CSV products found: {list(review_counts.keys())[:10]}...")  # Show first 10
        return review_counts
    except Exception as e:
        print(f"❌ Error loading CSV reviews: {str(e)}")
        return {}

def get_all_klaviyo_reviews():
    """Fetch all review counts - CSV first, then live Klaviyo reviews"""
    try:
        # Start with CSV data (imported reviews)
        review_counts = get_csv_review_counts()
        
        # Check if Klaviyo API key is available
        if not KLAVIYO_API_KEY:
            print("⚠️ KLAVIYO_API_KEY not configured, using CSV counts only")
            return review_counts
        
        # Add live Klaviyo reviews (from email workflow)
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # Try to access Klaviyo Reviews API directly
        # This is the actual reviews database, not events
        reviews_url = "https://a.klaviyo.com/api/reviews/?page[size]=500"
        
        try:
            response = requests.get(reviews_url, headers=headers)
            print(f"Klaviyo Reviews API response: {response.status_code}")
            
            if response.status_code == 200:
                reviews_data = response.json()
                reviews = reviews_data.get('data', [])
                print(f"Found {len(reviews)} reviews in Klaviyo Reviews")
                
                # Get all pages of reviews
                all_reviews = reviews[:]
                
                # Check if there are more pages
                next_url = reviews_data.get('links', {}).get('next')
                while next_url and len(all_reviews) < 1000:  # Safety limit
                    next_response = requests.get(next_url, headers=headers)
                    if next_response.status_code == 200:
                        next_data = next_response.json()
                        all_reviews.extend(next_data.get('data', []))
                        next_url = next_data.get('links', {}).get('next')
                    else:
                        break
                
                print(f"Total reviews found across all pages: {len(all_reviews)}")
                
                for review in all_reviews:
                    # Get product info from relationships section
                    relationships = review.get('relationships', {})
                    item_data = relationships.get('item', {}).get('data', {})
                    catalog_item_id = item_data.get('id')
                    
                    if catalog_item_id:
                        # Extract Shopify product ID from catalog item ID
                        # Format: "$shopify:::$default:::PRODUCT_ID"
                        if ':::' in catalog_item_id:
                            parts = catalog_item_id.split(':::')
                            if len(parts) >= 3:
                                shopify_product_id = parts[-1]  # Last part is the product ID
                                
                                # Add to existing CSV counts
                                if shopify_product_id not in review_counts:
                                    review_counts[shopify_product_id] = 0
                                review_counts[shopify_product_id] += 1
                
                print(f"Review counts by Shopify product ID: {review_counts}")
                return review_counts
                
            elif response.status_code == 404:
                print("Klaviyo Reviews API not available - might not be enabled")
            else:
                print(f"Klaviyo Reviews API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error accessing Klaviyo Reviews API: {str(e)}")
        
        # Fallback to events-based approach
        print("Falling back to events-based review counting...")
        for metric_name in ['Submitted review', 'ReviewsIOProductReview']:
            url = f"https://a.klaviyo.com/api/events/?filter=equals(metric.name,'{metric_name}')&page[size]=500"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                events = response.json().get('data', [])
                
                for event in events:
                    properties = event.get('attributes', {}).get('properties', {})
                    
                    # Try to extract product handle/identifier
                    possible_handles = [
                        properties.get('ProductID'),
                        properties.get('product_handle'),
                        properties.get('Product Handle'),
                        properties.get('product_id'),
                        properties.get('handle')
                    ]
                    
                    for handle in possible_handles:
                        if handle and isinstance(handle, str) and handle.strip():
                            product_handle = handle.strip()
                            if product_handle not in review_counts:
                                review_counts[product_handle] = 0
                            review_counts[product_handle] += 1
                            break
        
        print(f"Total review counts found: {len(review_counts)}")
        return review_counts
            
    except Exception as e:
        print(f"Error fetching Klaviyo reviews: {str(e)}")
        return {}

def get_klaviyo_reviews_for_product(product_handle):
    """Legacy function - kept for compatibility"""
    all_reviews = get_all_klaviyo_reviews()
    return all_reviews.get(product_handle, 0)

@app.route('/')
def index():
    return render_template('shopify_backend.html')

@app.route('/klaviyo-diagnostic')
def klaviyo_diagnostic():
    return render_template('klaviyo_diagnostic.html')

@app.route('/api/test')
def test_route():
    return jsonify({'test': 'working', 'message': 'Test route is functional'})

@app.route('/api/reviews/<product_id>')
def get_product_reviews(product_id):
    """Get all live reviews for a specific product"""
    try:
        if not KLAVIYO_API_KEY:
            return jsonify({'error': 'Klaviyo API key not configured'}), 500
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # Get all reviews from Klaviyo
        all_reviews = []
        url = "https://a.klaviyo.com/api/reviews/?page[size]=500"
        
        while url and len(all_reviews) < 2000:  # Safety limit
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return jsonify({'error': f'Klaviyo API error: {response.status_code}'}), 500
            
            data = response.json()
            reviews = data.get('data', [])
            all_reviews.extend(reviews)
            
            # Check for next page
            url = data.get('links', {}).get('next')
        
        # Filter reviews for this specific product
        product_reviews = []
        target_catalog_id = f"$shopify:::$default:::{product_id}"
        
        for review in all_reviews:
            # Check if this review is for the requested product
            relationships = review.get('relationships', {})
            item_data = relationships.get('item', {}).get('data', {})
            catalog_item_id = item_data.get('id', '')
            
            if catalog_item_id == target_catalog_id:
                # Format the review data
                attributes = review.get('attributes', {})
                product_info = attributes.get('product', {})
                
                formatted_review = {
                    'id': review.get('id'),
                    'rating': attributes.get('rating'),
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
        
        # Get product info from Shopify for context
        product_info = {}
        try:
            shopify_url = f'https://{SHOP_DOMAIN}/admin/api/2023-10/products/{product_id}.json'
            shopify_headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
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

@app.route('/api/klaviyo-events', methods=['GET'])
def get_klaviyo_events():
    """Diagnostic endpoint to discover Klaviyo event types"""
    try:
        if not KLAVIYO_API_KEY:
            return jsonify({
                'success': False, 
                'error': 'Klaviyo API key not configured'
            }), 500
            
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # First, let's get all metrics (event types) in your account
        metrics_url = "https://a.klaviyo.com/api/metrics/"
        response = requests.get(metrics_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({
                'success': False, 
                'error': f'Klaviyo API error: {response.status_code} - {response.text}'
            }), 500
            
        metrics_data = response.json()
        metrics = metrics_data.get('data', [])
        
        # Filter for review-related metrics
        review_metrics = []
        all_metrics = []
        
        for metric in metrics:
            metric_name = metric.get('attributes', {}).get('name', '')
            metric_id = metric.get('id', '')
            
            all_metrics.append({
                'id': metric_id,
                'name': metric_name,
                'integration': metric.get('attributes', {}).get('integration', {}).get('name', 'Unknown')
            })
            
            # Check if this might be a review-related metric
            if any(keyword in metric_name.lower() for keyword in ['review', 'rating', 'feedback', 'testimonial']):
                review_metrics.append({
                    'id': metric_id,
                    'name': metric_name,
                    'integration': metric.get('attributes', {}).get('integration', {}).get('name', 'Unknown')
                })
        
        # Also try to get some recent events to see their structure
        events_url = "https://a.klaviyo.com/api/events/?page[size]=10"
        events_response = requests.get(events_url, headers=headers)
        
        sample_events = []
        if events_response.status_code == 200:
            events_data = events_response.json()
            for event in events_data.get('data', [])[:5]:  # Get first 5 events
                sample_events.append({
                    'metric_name': event.get('attributes', {}).get('metric', {}).get('data', {}).get('attributes', {}).get('name', 'Unknown'),
                    'timestamp': event.get('attributes', {}).get('timestamp', ''),
                    'properties': event.get('attributes', {}).get('properties', {})
                })
        
        return jsonify({
            'success': True,
            'review_metrics': review_metrics,
            'all_metrics': all_metrics,
            'sample_events': sample_events,
            'total_metrics': len(all_metrics)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/klaviyo-review-samples', methods=['GET'])
def get_klaviyo_review_samples():
    """Get sample review events to understand their structure"""
    try:
        if not KLAVIYO_API_KEY:
            return jsonify({
                'success': False, 
                'error': 'Klaviyo API key not configured'
            }), 500
            
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        review_samples = []
        
        # Try ALL the review-related metrics we found earlier
        review_metric_names = [
            'Submitted review',
            'ReviewsIOProductReview', 
            'ReviewsIOReview',
            'Ready to review',
            'Edited review',
            'Submitted rating',
            'ReviewsIONegativeProductReview',
            'ReviewsIOPositiveReview',
            'ReviewsIONegativeReview',
            'ReviewsIOPositiveProductReview',
            'Edited rating'
        ]
        
        for metric_name in review_metric_names:
            url = f"https://a.klaviyo.com/api/events/?filter=equals(metric.name,'{metric_name}')&page[size]=5"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                events = response.json().get('data', [])
                
                for event in events:
                    properties = event.get('attributes', {}).get('properties', {})
                    review_samples.append({
                        'metric_name': metric_name,
                        'timestamp': event.get('attributes', {}).get('timestamp', ''),
                        'properties': properties,
                        'all_property_keys': list(properties.keys())
                    })
                    
                    # Stop after we get some samples
                    if len(review_samples) >= 10:
                        break
            
            if len(review_samples) >= 10:
                break
        
        return jsonify({
            'success': True,
            'review_samples': review_samples,
            'total_samples': len(review_samples)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/debug-reviews', methods=['GET'])
def debug_reviews():
    """Debug where reviews might be stored"""
    try:
        if not KLAVIYO_API_KEY:
            return jsonify({
                'success': False, 
                'error': 'Klaviyo API key not configured'
            }), 500
            
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        debug_info = {}
        
        # 1. Check if reviews are stored as profile properties
        profiles_url = "https://a.klaviyo.com/api/profiles/?page[size]=5"
        profiles_response = requests.get(profiles_url, headers=headers)
        
        if profiles_response.status_code == 200:
            profiles = profiles_response.json().get('data', [])
            profile_properties = []
            
            for profile in profiles[:3]:  # Check first 3 profiles
                properties = profile.get('attributes', {}).get('properties', {})
                review_related_props = {}
                
                for key, value in properties.items():
                    if any(keyword in key.lower() for keyword in ['review', 'rating', 'feedback']):
                        review_related_props[key] = value
                
                if review_related_props:
                    profile_properties.append({
                        'profile_id': profile.get('id'),
                        'email': profile.get('attributes', {}).get('email'),
                        'review_properties': review_related_props
                    })
            
            debug_info['profile_review_properties'] = profile_properties
        
        # 2. Try a broader event search with recent events
        recent_events_url = "https://a.klaviyo.com/api/events/?page[size]=20"
        recent_response = requests.get(recent_events_url, headers=headers)
        
        if recent_response.status_code == 200:
            events = recent_response.json().get('data', [])
            recent_events_summary = []
            
            for event in events:
                metric_name = event.get('attributes', {}).get('metric', {}).get('data', {}).get('attributes', {}).get('name', 'Unknown')
                properties = event.get('attributes', {}).get('properties', {})
                
                # Check if any properties might be product-related
                product_related = any(keyword in str(properties).lower() for keyword in ['product', 'item', 'sku'])
                
                recent_events_summary.append({
                    'metric_name': metric_name,
                    'timestamp': event.get('attributes', {}).get('timestamp', ''),
                    'has_product_data': product_related,
                    'property_keys': list(properties.keys())
                })
            
            debug_info['recent_events'] = recent_events_summary
        
        # 3. Check specific product in Shopify for review data in metafields
        if SHOP_DOMAIN != 'your-shop.myshopify.com':
            shopify_headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
            products_url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products.json?limit=1"
            products_response = requests.get(products_url, headers=shopify_headers)
            
            if products_response.status_code == 200:
                products = products_response.json().get('products', [])
                if products:
                    product = products[0]
                    # Check if this product has metafields that might contain review data
                    metafields_url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products/{product['id']}/metafields.json"
                    metafields_response = requests.get(metafields_url, headers=shopify_headers)
                    
                    if metafields_response.status_code == 200:
                        metafields = metafields_response.json().get('metafields', [])
                        review_metafields = []
                        
                        for metafield in metafields:
                            if any(keyword in metafield.get('key', '').lower() for keyword in ['review', 'rating', 'feedback']):
                                review_metafields.append({
                                    'key': metafield.get('key'),
                                    'namespace': metafield.get('namespace'),
                                    'value': metafield.get('value'),
                                    'type': metafield.get('type')
                                })
                        
                        debug_info['shopify_review_metafields'] = {
                            'product_title': product.get('title'),
                            'product_handle': product.get('handle'),
                            'review_metafields': review_metafields,
                            'all_metafields': [{'key': m.get('key'), 'namespace': m.get('namespace')} for m in metafields]
                        }
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/test-klaviyo-reviews', methods=['GET'])
def test_klaviyo_reviews():
    """Test endpoint to check Klaviyo Reviews API access"""
    try:
        if not KLAVIYO_API_KEY:
            return jsonify({
                'success': False, 
                'error': 'Klaviyo API key not configured'
            })
            
        headers = {
            'Authorization': f'Klaviyo-API-Key {KLAVIYO_API_KEY}',
            'Accept': 'application/json',
            'revision': '2024-10-15'
        }
        
        # Test Klaviyo Reviews API
        reviews_url = "https://a.klaviyo.com/api/reviews/?page[size]=10"
        response = requests.get(reviews_url, headers=headers)
        
        result = {
            'success': True,
            'reviews_api_status': response.status_code,
            'reviews_api_response': response.text[:1000] if response.text else 'No response text',
            'review_counts': {}
        }
        
        if response.status_code == 200:
            try:
                reviews_data = response.json()
                reviews = reviews_data.get('data', [])
                result['total_reviews_found'] = len(reviews)
                result['sample_review'] = reviews[0] if reviews else None
                
                # Count reviews by product
                for review in reviews:
                    attributes = review.get('attributes', {})
                    product_id = attributes.get('product_id')
                    if product_id:
                        if product_id not in result['review_counts']:
                            result['review_counts'][product_id] = 0
                        result['review_counts'][product_id] += 1
                        
            except Exception as e:
                result['json_parse_error'] = str(e)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/api/compare-reviews', methods=['GET'])
def compare_reviews():
    """Compare CSV reviews with Klaviyo Reviews API"""
    try:
        import csv
        
        # Count reviews from CSV file
        csv_counts = {}
        csv_file_path = 'review_export_150f0ab9-09fe-445b-8854-d9ee9890ceb0.csv'
        
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    product_id = row.get('product_id', '').strip()
                    if product_id and product_id not in csv_counts:
                        csv_counts[product_id] = 0
                    if product_id:
                        csv_counts[product_id] += 1
        
        # Get reviews from Klaviyo API
        klaviyo_counts = get_all_klaviyo_reviews()
        
        # Compare
        comparison = {
            'csv_total_reviews': sum(csv_counts.values()),
            'csv_products_with_reviews': len(csv_counts),
            'klaviyo_total_reviews': sum(klaviyo_counts.values()),
            'klaviyo_products_with_reviews': len(klaviyo_counts),
            'sample_csv_counts': dict(list(csv_counts.items())[:5]),
            'sample_klaviyo_counts': dict(list(klaviyo_counts.items())[:5]),
            'missing_from_klaviyo': []
        }
        
        # Find products with reviews in CSV but not in Klaviyo
        for product_id, count in csv_counts.items():
            if product_id not in klaviyo_counts:
                comparison['missing_from_klaviyo'].append({
                    'product_id': product_id,
                    'csv_count': count
                })
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

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
        fetch_klaviyo = bool(KLAVIYO_API_KEY)
        
        # No more manual tracking - use real API data only
        
        # Try Klaviyo first, but use manual counts as fallback
        klaviyo_review_counts = {}
        if fetch_klaviyo:
            try:
                print("🔄 Fetching Klaviyo reviews...")
                klaviyo_review_counts = get_all_klaviyo_reviews()
                print(f"✅ Got review counts for {len(klaviyo_review_counts)} products")
                print(f"📊 Klaviyo review counts: {klaviyo_review_counts}")
            except Exception as e:
                print(f"❌ Error fetching Klaviyo reviews: {str(e)}")
                klaviyo_review_counts = {}
        
        for product in products:
            product_id = str(product['id'])
            product_handle = product['handle']
            product_title = product['title']
            
            # Debug logging for product details
            print(f"🔍 Processing product: {product_title}")
            print(f"   ID: {product_id}, Handle: {product_handle}")
            
            # Get live review count (Klaviyo first, then manual counts as fallback)
            # Try matching by product_id first (from Klaviyo Reviews API), then by handle (manual)
            klaviyo_reviews = klaviyo_review_counts.get(product_id, 0)
            print(f"   Klaviyo reviews by ID: {klaviyo_reviews}")
            
            if klaviyo_reviews == 0:
                klaviyo_reviews = klaviyo_review_counts.get(product_handle, 0)
                print(f"   Klaviyo reviews by handle: {klaviyo_reviews}")
                
            # Only use real Klaviyo API data - no more manual BS
            
            print(f"   ✅ Final live review count: {klaviyo_reviews}")
            
            generated_reviews = review_tracking.get(product_id, {}).get('count', 0)
            
            products_data.append({
                'id': product_id,
                'title': product['title'],
                'handle': product_handle,
                'image': product['images'][0]['src'] if product.get('images') else None,
                'variants_count': len(product.get('variants', [])),
                'generated_reviews': generated_reviews,
                'klaviyo_reviews': klaviyo_reviews,
                'total_reviews': klaviyo_reviews + generated_reviews,
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
    from review_generator import generate_review, select_language
    
    try:
        # Get review count from request
        data = request.json
        review_count = data.get('count', 5)
        
        # Fetch specific product
        url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'Failed to fetch product: {response.status_code}'}), 500
            
        response_data = response.json()
        if 'product' not in response_data:
            return jsonify({'success': False, 'error': f'Product not found in response: {response_data}'}), 500
            
        product = response_data['product']
        print(f"Fetched product: {product.get('title', 'Unknown')} (ID: {product.get('id', 'Unknown')})")
        
        # Generate reviews
        reviews = []
        for i in range(review_count):
            try:
                print(f"Generating review {i+1}/{review_count} for product: {product.get('title')}")
                print(f"Product keys available: {list(product.keys())}")
                
                # Generate review using the new function
                review_data = generate_review(product, existing_reviews=i)
                print(f"Generated content: {review_data['content'][:50] if review_data['content'] else 'Empty'}...")
                
            except Exception as e:
                print(f"Error generating review {i+1}: {str(e)}")
                return jsonify({'success': False, 'error': f'Error generating review: {str(e)}'}), 500
            
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
    from review_generator import generate_review, select_language
    
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
        num_reviews = random.randint(3, 8)
        for i in range(num_reviews):
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
                'verified': review_data['verified']
            })
    
    # Save CSV
    filename = f'reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    os.makedirs('exports', exist_ok=True)
    with open(f'exports/{filename}', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)
    
    return jsonify({'success': True, 'count': len(reviews), 'filename': filename})

@app.route('/api/generate-bulk', methods=['POST'])
def generate_bulk_reviews():
    """Generate reviews for multiple products in one combined CSV"""
    from review_generator import generate_review
    
    try:
        # Get request data
        data = request.json
        product_ids = data.get('product_ids', [])
        review_count = data.get('count', 5)
        
        if not product_ids:
            return jsonify({'error': 'No products specified'}), 400
        
        all_reviews = []
        success_count = 0
        error_count = 0
        errors = []
        
        headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
        
        for product_id in product_ids:
            try:
                # Fetch product details
                url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products/{product_id}.json"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    errors.append(f"Product {product_id}: Failed to fetch product details")
                    error_count += 1
                    continue
                
                product = response.json()['product']
                
                # Generate reviews for this product
                for i in range(review_count):
                    review_data = generate_review(product, existing_reviews=i)
                    
                    all_reviews.append({
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
        for product_id in product_ids:
            if product_id not in review_tracking:
                review_tracking[product_id] = {'count': 0}
            review_tracking[product_id]['count'] += review_count
            review_tracking[product_id]['last_generated'] = datetime.now().isoformat()
        save_review_tracking(review_tracking)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'total_reviews': len(all_reviews),
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-reviews', methods=['POST'])
def import_reviews():
    """Automatically import generated reviews to configured platforms"""
    from automatic_import import import_reviews_automatically
    
    try:
        data = request.json
        reviews = data.get('reviews', [])
        platforms = data.get('platforms', ['reviews_io', 'klaviyo'])
        
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
        platforms = data.get('platforms', ['reviews_io', 'klaviyo'])
        
        # Fetch product info
        url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
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
        platforms = data.get('platforms', ['reviews_io', 'klaviyo'])
        
        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400
        
        all_reviews = []
        
        # Generate reviews for each product
        for product_id in product_ids:
            # Fetch product
            url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/products/{product_id}.json"
            headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
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
    # This would connect to a progress tracker instance
    # For now, return a simple status
    return jsonify({
        'status': 'ready',
        'platforms_configured': {
            'reviews_io': bool(os.environ.get('REVIEWS_IO_API_KEY')),
            'klaviyo': bool(os.environ.get('KLAVIYO_API_KEY'))
        }
    })

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'exports/{filename}', as_attachment=True)

@app.route('/analytics')
def analytics_dashboard():
    """Analytics dashboard with advanced visualizations and bulk actions"""
    return render_template('analytics_dashboard.html')

@app.route('/api/analytics/dashboard')
def analytics_dashboard_data():
    """API endpoint for dashboard metrics"""
    days = request.args.get('days', 30, type=int)
    
    # Sample analytics data - in production this would come from your database
    sample_data = {
        'total_reviews_generated': random.randint(150, 500),
        'quality_scores': {
            'overall': round(random.uniform(0.7, 0.95), 3),
            'authenticity': round(random.uniform(0.65, 0.9), 3),
            'readability': round(random.uniform(0.8, 0.95), 3),
            'uniqueness': round(random.uniform(0.6, 0.85), 3),
            'commercial_value': round(random.uniform(0.7, 0.9), 3)
        },
        'generation_methods': {
            'ai_enhanced': random.randint(80, 150),
            'template_based': random.randint(50, 100)
        },
        'error_rates': {
            'klaviyo': round(random.uniform(1, 8), 1),
            'reviews_io': round(random.uniform(2, 12), 1)
        },
        'language_distribution': {
            'en': random.randint(100, 200),
            'es': random.randint(20, 50),
            'fr': random.randint(10, 30),
            'de': random.randint(15, 40)
        },
        'rating_distribution': {
            '5': random.randint(200, 300),
            '4': random.randint(80, 150),
            '3': random.randint(20, 60),
            '2': random.randint(5, 20),
            '1': random.randint(1, 10)
        },
        'performance_trends': {
            'daily_reviews': [
                {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
                 'count': random.randint(5, 25),
                 'quality': round(random.uniform(0.6, 0.9), 2)}
                for i in range(days, 0, -1)
            ]
        },
        'top_products': [
            {
                'title': 'Gothic Oversized Hoodie',
                'review_count': random.randint(20, 50),
                'avg_quality': round(random.uniform(0.7, 0.95), 3)
            },
            {
                'title': 'Vintage Band Tee Collection', 
                'review_count': random.randint(15, 40),
                'avg_quality': round(random.uniform(0.6, 0.9), 3)
            },
            {
                'title': 'Punk Rock Leather Jacket',
                'review_count': random.randint(25, 60),
                'avg_quality': round(random.uniform(0.65, 0.85), 3)
            }
        ]
    }
    
    return jsonify(sample_data)

@app.route('/api/analytics/quality-insights')
def quality_insights():
    """API endpoint for AI quality insights"""
    # Sample quality insights
    insights = {
        'quality_statistics': {
            'mean': round(random.uniform(0.7, 0.85), 3),
            'min': round(random.uniform(0.4, 0.6), 3),
            'max': round(random.uniform(0.9, 0.98), 3),
            'std_dev': round(random.uniform(0.08, 0.15), 3)
        },
        'recommendations': [
            'Consider increasing uniqueness focus for better authenticity scores',
            'Review generation rate is optimal for current quality targets',
            'Language distribution shows good market coverage'
        ]
    }
    
    return jsonify(insights)

@app.route('/api/analytics/platform-performance')
def platform_performance():
    """API endpoint for platform performance metrics"""
    # Sample platform data
    performance = {
        'klaviyo': {
            'total_reviews': random.randint(100, 300),
            'avg_quality': round(random.uniform(0.7, 0.9), 3),
            'error_rate': round(random.uniform(2, 8), 1),
            'avg_generation_time_ms': random.randint(800, 2000)
        },
        'reviews_io': {
            'total_reviews': random.randint(50, 150),
            'avg_quality': round(random.uniform(0.65, 0.85), 3), 
            'error_rate': round(random.uniform(5, 15), 1),
            'avg_generation_time_ms': random.randint(1200, 3000)
        }
    }
    
    return jsonify(performance)

@app.route('/api/analytics/export')
def export_analytics():
    """Export analytics data"""
    days = request.args.get('days', 30, type=int)
    format_type = request.args.get('format', 'json')
    
    # Get dashboard data for export
    dashboard_response = analytics_dashboard_data()
    data = dashboard_response.get_json()
    
    if format_type == 'json':
        return jsonify(data)
    else:
        # Could implement CSV/XML export here
        return jsonify({'error': 'Format not supported yet'})

@app.route('/api/analytics/sample-data', methods=['POST'])
def create_sample_data():
    """Create sample analytics data"""
    # In a real implementation, this would generate sample data in your database
    return jsonify({'success': True, 'message': 'Sample data created'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))