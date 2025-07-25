"""
Reviews.io API Integration
Direct API access to Reviews.io for fetching and managing reviews
"""
import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class ReviewsIOClient:
    """Reviews.io API client for direct integration"""
    
    def __init__(self, api_key: str = None, store_id: str = None):
        self.api_key = api_key or os.environ.get('REVIEWS_IO_API_KEY')
        self.store_id = store_id or os.environ.get('REVIEWS_IO_STORE_ID')
        self.base_url = "https://api.reviews.io/merchant"
        
        if not self.api_key or not self.store_id:
            print("Warning: Reviews.io credentials not configured")
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to Reviews.io API"""
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Reviews.io API error: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return {'error': str(e)}
    
    def get_product_reviews(self, product_id: str) -> Dict:
        """Get all reviews for a specific product"""
        params = {
            'store': self.store_id,
            'product_id': product_id,
            'per_page': 100  # Max per page
        }
        
        return self._make_request('reviews', params=params)
    
    def get_all_product_reviews(self) -> Dict:
        """Get all product reviews with pagination"""
        all_reviews = []
        page = 1
        
        while True:
            params = {
                'store': self.store_id,
                'page': page,
                'per_page': 100
            }
            
            response = self._make_request('reviews', params=params)
            
            if 'error' in response:
                return response
            
            reviews = response.get('reviews', [])
            if not reviews:
                break
                
            all_reviews.extend(reviews)
            
            # Check if there are more pages
            if len(reviews) < 100:
                break
                
            page += 1
        
        return {'reviews': all_reviews, 'total': len(all_reviews)}
    
    def get_review_counts_by_product(self) -> Dict[str, int]:
        """Get review counts grouped by product ID"""
        response = self.get_all_product_reviews()
        
        if 'error' in response:
            return {}
        
        review_counts = {}
        for review in response.get('reviews', []):
            product_id = str(review.get('product_id', ''))
            if product_id:
                review_counts[product_id] = review_counts.get(product_id, 0) + 1
        
        return review_counts
    
    def create_review(self, review_data: Dict) -> Dict:
        """Create a new review via API"""
        # Reviews.io typically requires these fields for product reviews
        required_fields = {
            'store': self.store_id,
            'email': review_data.get('reviewer_email'),
            'name': review_data.get('reviewer_name'),
            'review_content': review_data.get('review_content'),
            'rating': int(review_data.get('rating', 5)),
            'product_id': review_data.get('product_id'),
            'product_name': review_data.get('product_name'),
            'product_url': review_data.get('product_url', ''),
            'order_id': review_data.get('order_id', ''),
            'review_date': review_data.get('review_date', datetime.now().strftime('%Y-%m-%d'))
        }
        
        # Add optional fields if present
        optional_fields = ['review_title', 'verified', 'location', 'image_urls']
        for field in optional_fields:
            if field in review_data and review_data[field]:
                required_fields[field] = review_data[field]
        
        return self._make_request('reviews', method='POST', data=required_fields)
    
    def bulk_create_reviews(self, reviews_list: List[Dict]) -> Dict:
        """Create multiple reviews in bulk"""
        results = {
            'success': [],
            'errors': [],
            'total_created': 0,
            'total_errors': 0
        }
        
        for review in reviews_list:
            result = self.create_review(review)
            
            if 'error' in result:
                results['errors'].append({
                    'review': review.get('product_name', 'Unknown'),
                    'error': result['error']
                })
                results['total_errors'] += 1
            else:
                results['success'].append(result)
                results['total_created'] += 1
        
        return results
    
    def get_store_stats(self) -> Dict:
        """Get store statistics from Reviews.io"""
        params = {'store': self.store_id}
        return self._make_request('store/stats', params=params)
    
    def test_connection(self) -> bool:
        """Test if API credentials work"""
        if not self.api_key or not self.store_id:
            return False
        
        response = self.get_store_stats()
        return 'error' not in response

def get_reviews_io_count(product):
    """Get review count for a product from Reviews.io"""
    try:
        # First check CSV file for imported reviews
        csv_counts = get_csv_review_counts()
        product_id = str(product.get('id', ''))
        
        if product_id in csv_counts:
            return csv_counts[product_id]
        
        # If no CSV data, try Reviews.io API
        client = ReviewsIOClient()
        
        if not client.test_connection():
            return 0
        
        # Try different product identifiers
        product_handle = product.get('handle', '')
        
        # First try with product ID
        reviews = client.get_product_reviews(product_id)
        
        if 'error' not in reviews and reviews.get('reviews'):
            return len(reviews['reviews'])
        
        # Try with product handle if ID doesn't work
        if product_handle:
            reviews = client.get_product_reviews(product_handle)
            if 'error' not in reviews and reviews.get('reviews'):
                return len(reviews['reviews'])
        
        return 0
        
    except Exception as e:
        print(f"Error fetching Reviews.io count: {str(e)}")
        return 0

def get_csv_review_counts():
    """Get review counts from the CSV export file"""
    try:
        import csv
        import os
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

def sync_reviews_io_counts() -> Dict[str, int]:
    """Sync all review counts from Reviews.io"""
    try:
        client = ReviewsIOClient()
        
        if not client.test_connection():
            return {}
        
        return client.get_review_counts_by_product()
        
    except Exception as e:
        print(f"Error syncing Reviews.io counts: {str(e)}")
        return {}

def post_reviews_to_reviews_io(reviews: List[Dict]) -> Dict:
    """Post generated reviews directly to Reviews.io"""
    try:
        client = ReviewsIOClient()
        
        if not client.test_connection():
            return {
                'error': 'Reviews.io not configured or connection failed',
                'total_created': 0,
                'total_errors': len(reviews)
            }
        
        # Transform review data for Reviews.io format
        reviews_io_format = []
        for review in reviews:
            reviews_io_format.append({
                'reviewer_email': review.get('reviewer_email'),
                'reviewer_name': review.get('reviewer_name'),
                'review_content': review.get('review_content'),
                'review_title': review.get('review_title'),
                'rating': review.get('rating'),
                'product_id': review.get('product_id'),
                'product_name': review.get('product_name'),
                'review_date': review.get('review_date'),
                'verified': review.get('verified', 'Yes'),
                'location': review.get('reviewer_location')
            })
        
        return client.bulk_create_reviews(reviews_io_format)
        
    except Exception as e:
        return {
            'error': str(e),
            'total_created': 0,
            'total_errors': len(reviews)
        }

# Export the main functions for use in app.py
__all__ = [
    'ReviewsIOClient',
    'get_reviews_io_count', 
    'sync_reviews_io_counts',
    'post_reviews_to_reviews_io'
]