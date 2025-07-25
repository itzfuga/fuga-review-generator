"""
Automatic Review Import System
Handles direct API imports to Reviews.io and Klaviyo
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from reviews_io_integration import ReviewsIOClient, post_reviews_to_reviews_io

class AutomaticReviewImporter:
    """Handles automatic import of generated reviews to multiple platforms"""
    
    def __init__(self):
        self.reviews_io_client = ReviewsIOClient()
        self.klaviyo_api_key = os.environ.get('KLAVIYO_API_KEY')
        self.import_status = {
            'total_reviews': 0,
            'reviews_io_success': 0,
            'reviews_io_failed': 0,
            'klaviyo_success': 0,
            'klaviyo_failed': 0,
            'errors': []
        }
    
    def import_reviews_batch(self, reviews: List[Dict], platforms: List[str] = None) -> Dict:
        """Import reviews to specified platforms (defaults to available platforms)"""
        if not platforms:
            # Default to available platforms
            platforms = []
            if self.reviews_io_client.test_connection():
                platforms.append('reviews_io')
            if self.klaviyo_api_key:
                platforms.append('klaviyo')
        
        self.import_status['total_reviews'] = len(reviews)
        results = {
            'platforms': {},
            'summary': {
                'total_reviews': len(reviews),
                'total_success': 0,
                'total_failed': 0
            },
            'warnings': []
        }
        
        # Import to Reviews.io
        if 'reviews_io' in platforms:
            if self.reviews_io_client.test_connection():
                reviews_io_result = self._import_to_reviews_io(reviews)
                results['platforms']['reviews_io'] = reviews_io_result
                results['summary']['total_success'] += reviews_io_result['success_count']
                results['summary']['total_failed'] += reviews_io_result['error_count']
            else:
                results['warnings'].append('Reviews.io API not configured - skipping Reviews.io import')
        
        # Import to Klaviyo
        if 'klaviyo' in platforms:
            if self.klaviyo_api_key:
                klaviyo_result = self._import_to_klaviyo(reviews)
                results['platforms']['klaviyo'] = klaviyo_result
                results['summary']['total_success'] += klaviyo_result['success_count']
                results['summary']['total_failed'] += klaviyo_result['error_count']
            else:
                results['warnings'].append('Klaviyo API key not configured - skipping Klaviyo import')
        
        # If no platforms are available, return error
        if not results['platforms']:
            results['error'] = 'No platforms are configured for automatic import'
        
        return results
    
    def _import_to_reviews_io(self, reviews: List[Dict]) -> Dict:
        """Import reviews to Reviews.io with progress tracking"""
        result = {
            'platform': 'Reviews.io',
            'success_count': 0,
            'error_count': 0,
            'errors': [],
            'imported_reviews': []
        }
        
        # Process in batches of 10 for better error handling
        batch_size = 10
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i + batch_size]
            
            try:
                batch_result = post_reviews_to_reviews_io(batch)
                
                if 'error' in batch_result:
                    result['error_count'] += len(batch)
                    result['errors'].append({
                        'batch': f"{i}-{i+len(batch)}",
                        'error': batch_result['error']
                    })
                else:
                    result['success_count'] += batch_result.get('total_created', 0)
                    result['error_count'] += batch_result.get('total_errors', 0)
                    
                    if batch_result.get('errors'):
                        result['errors'].extend(batch_result['errors'])
                    
                    if batch_result.get('success'):
                        result['imported_reviews'].extend(batch_result['success'])
                        
            except Exception as e:
                result['error_count'] += len(batch)
                result['errors'].append({
                    'batch': f"{i}-{i+len(batch)}",
                    'error': str(e)
                })
        
        return result
    
    def _import_to_klaviyo(self, reviews: List[Dict]) -> Dict:
        """Import reviews to Klaviyo Reviews API"""
        result = {
            'platform': 'Klaviyo',
            'success_count': 0,
            'error_count': 0,
            'errors': [],
            'imported_reviews': []
        }
        
        headers = {
            'Authorization': f'Klaviyo-API-Key {self.klaviyo_api_key}',
            'revision': '2024-10-15',
            'Content-Type': 'application/json'
        }
        
        for review in reviews:
            try:
                # Transform to Klaviyo format
                klaviyo_review = self._transform_to_klaviyo_format(review)
                
                response = requests.post(
                    'https://a.klaviyo.com/api/reviews/',
                    headers=headers,
                    json={'data': klaviyo_review}
                )
                
                if response.status_code == 201:
                    result['success_count'] += 1
                    result['imported_reviews'].append(response.json())
                else:
                    result['error_count'] += 1
                    result['errors'].append({
                        'product': review.get('product_name'),
                        'error': f"Status {response.status_code}: {response.text}"
                    })
                    
            except Exception as e:
                result['error_count'] += 1
                result['errors'].append({
                    'product': review.get('product_name'),
                    'error': str(e)
                })
        
        return result
    
    def _transform_to_klaviyo_format(self, review: Dict) -> Dict:
        """Transform review data to Klaviyo API format"""
        return {
            'type': 'review',
            'attributes': {
                'title': review.get('review_title', ''),
                'body': review.get('review_content', ''),
                'rating': int(review.get('rating', 5)),
                'author_name': review.get('reviewer_name'),
                'author_email': review.get('reviewer_email'),
                'product_id': str(review.get('product_id')),
                'product_name': review.get('product_name'),
                'product_url': review.get('product_url', ''),
                'verified_buyer': review.get('verified', 'Yes') == 'Yes',
                'created': review.get('review_date', datetime.now().isoformat()),
                'locale': self._detect_locale(review)
            }
        }
    
    def _detect_locale(self, review: Dict) -> str:
        """Detect locale from reviewer location"""
        location = review.get('reviewer_location', '').upper()
        locale_map = {
            'US': 'en_US',
            'UK': 'en_GB',
            'CA': 'en_CA',
            'AU': 'en_AU',
            'DE': 'de_DE',
            'AT': 'de_AT',
            'CH': 'de_CH',
            'PL': 'pl_PL',
            'RU': 'ru_RU'
        }
        return locale_map.get(location, 'en_US')

def import_reviews_automatically(reviews: List[Dict], platforms: List[str] = None) -> Dict:
    """Main function to import reviews automatically"""
    importer = AutomaticReviewImporter()
    return importer.import_reviews_batch(reviews, platforms)

# Progress tracking with SSE (Server-Sent Events) support
class ImportProgressTracker:
    """Track import progress for real-time updates"""
    
    def __init__(self):
        self.progress = {
            'status': 'idle',
            'current_platform': None,
            'total_reviews': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'current_batch': 0,
            'total_batches': 0,
            'messages': []
        }
    
    def start_import(self, total_reviews: int, platforms: List[str]):
        """Initialize import progress"""
        self.progress.update({
            'status': 'importing',
            'total_reviews': total_reviews,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'platforms': platforms,
            'start_time': datetime.now().isoformat()
        })
    
    def update_platform(self, platform: str):
        """Update current platform being processed"""
        self.progress['current_platform'] = platform
        self.progress['messages'].append(f"Starting import to {platform}")
    
    def update_batch(self, batch_num: int, total_batches: int):
        """Update batch progress"""
        self.progress.update({
            'current_batch': batch_num,
            'total_batches': total_batches
        })
    
    def record_success(self, count: int = 1):
        """Record successful imports"""
        self.progress['success'] += count
        self.progress['processed'] += count
    
    def record_failure(self, count: int = 1, error: str = None):
        """Record failed imports"""
        self.progress['failed'] += count
        self.progress['processed'] += count
        if error:
            self.progress['messages'].append(f"Error: {error}")
    
    def complete(self):
        """Mark import as complete"""
        self.progress.update({
            'status': 'complete',
            'end_time': datetime.now().isoformat(),
            'current_platform': None
        })
        self.progress['messages'].append(
            f"Import complete: {self.progress['success']} successful, "
            f"{self.progress['failed']} failed"
        )
    
    def get_progress(self) -> Dict:
        """Get current progress state"""
        return self.progress.copy()