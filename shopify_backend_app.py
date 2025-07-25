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
                    status = row.get('status', '').strip()
                    
                    # Only count published reviews
                    if product_id and status == 'published':
                        if product_id not in review_counts:
                            review_counts[product_id] = 0
                        review_counts[product_id] += 1
        
        print(f"CSV review counts loaded: {len(review_counts)} products, {sum(review_counts.values())} total reviews")
        return review_counts
    except Exception as e:
        print(f"Error loading CSV reviews: {str(e)}")
        return {}

def get_all_klaviyo_reviews():
    """Fetch all review counts - CSV first, then live Klaviyo reviews"""
    try:
        # Start with CSV data (imported reviews)
        review_counts = get_csv_review_counts()
        
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

@app.route('/api/klaviyo-events', methods=['GET'])
def get_klaviyo_events():
    """Diagnostic endpoint to discover Klaviyo event types"""
    try:
        if KLAVIYO_API_KEY == 'your-klaviyo-key':
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
        if KLAVIYO_API_KEY == 'your-klaviyo-key':
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
        if KLAVIYO_API_KEY == 'your-klaviyo-key':
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
        if KLAVIYO_API_KEY == 'your-klaviyo-key':
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
        fetch_klaviyo = KLAVIYO_API_KEY != 'your-klaviyo-key'
        
        # Load manually tracked live review counts (fallback if Klaviyo doesn't work)
        live_review_counts = load_live_review_counts()
        
        # Try Klaviyo first, but use manual counts as fallback
        klaviyo_review_counts = {}
        if fetch_klaviyo:
            try:
                print("Fetching Klaviyo reviews...")
                klaviyo_review_counts = get_all_klaviyo_reviews()
                print(f"Got review counts for {len(klaviyo_review_counts)} products")
            except Exception as e:
                print(f"Error fetching Klaviyo reviews: {str(e)}")
                klaviyo_review_counts = {}
        
        for product in products:
            product_id = str(product['id'])
            product_handle = product['handle']
            
            # Get live review count (Klaviyo first, then manual counts as fallback)
            # Try matching by product_id first (from Klaviyo Reviews API), then by handle (manual)
            klaviyo_reviews = klaviyo_review_counts.get(product_id, 0)
            if klaviyo_reviews == 0:
                klaviyo_reviews = klaviyo_review_counts.get(product_handle, 0)
            if klaviyo_reviews == 0:
                klaviyo_reviews = live_review_counts.get(product_handle, 0)
            
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

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'exports/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))