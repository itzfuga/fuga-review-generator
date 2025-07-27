#!/usr/bin/env python3
"""
Enhanced Klaviyo Reviews API Debug Tool
Real-time debugging to identify specific API issues
"""

import os
import requests
import json
from datetime import datetime

def main():
    print("🔧 Enhanced Klaviyo Reviews API Debug Tool")
    print("=" * 60)
    
    # Check environment
    api_key = os.environ.get('KLAVIYO_API_KEY')
    if not api_key:
        print("❌ KLAVIYO_API_KEY not found in environment")
        print("\n💡 Quick Fix:")
        print("export KLAVIYO_API_KEY='your-actual-key-here'")
        return
    
    print(f"✅ API Key found: {api_key[:15]}...")
    
    # Test 1: API key validation
    print(f"\n1️⃣ Testing API Key Validity...")
    if test_api_key(api_key):
        print("✅ API Key is valid")
    else:
        print("❌ API Key is invalid or expired")
        return
    
    # Test 2: Reviews API discovery
    print(f"\n2️⃣ Testing Reviews API Endpoints...")
    test_reviews_endpoints(api_key)
    
    # Test 3: Sample review creation
    print(f"\n3️⃣ Testing Review Creation...")
    test_review_creation(api_key)
    
    # Test 4: Alternative approaches
    print(f"\n4️⃣ Testing Alternative Approaches...")
    test_alternatives(api_key)

def test_api_key(api_key):
    """Test if API key works"""
    try:
        headers = {
            'Authorization': f'Klaviyo-API-Key {api_key}',
            'revision': '2024-10-15'
        }
        
        response = requests.get('https://a.klaviyo.com/api/accounts/', headers=headers, timeout=10)
        
        if response.status_code == 200:
            account = response.json().get('data', [{}])[0]
            org_name = account.get('attributes', {}).get('contact_information', {}).get('organization_name', 'Unknown')
            print(f"   Account: {org_name}")
            return True
        else:
            print(f"   Error: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def test_reviews_endpoints(api_key):
    """Test various reviews endpoints"""
    headers = {
        'Authorization': f'Klaviyo-API-Key {api_key}',
        'Accept': 'application/json',
        'revision': '2024-10-15'
    }
    
    endpoints = [
        ('GET Reviews', 'https://a.klaviyo.com/api/reviews/'),
        ('GET Review Schema', 'https://a.klaviyo.com/api/reviews/$schema'),
        ('GET Catalog Items', 'https://a.klaviyo.com/api/catalog-items/?page[size]=5'),
        ('GET Profiles', 'https://a.klaviyo.com/api/profiles/?page[size]=5'),
        ('GET Events', 'https://a.klaviyo.com/api/events/?page[size]=5'),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   {name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    print(f"      → Found {len(data['data'])} items")
                else:
                    print(f"      → Response: {str(data)[:100]}...")
            elif response.status_code == 403:
                print(f"      → Permission denied - Reviews API might not be enabled")
            elif response.status_code == 404:
                print(f"      → Endpoint not found")
            else:
                print(f"      → Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   {name}: Exception - {e}")

def test_review_creation(api_key):
    """Test creating a sample review"""
    headers = {
        'Authorization': f'Klaviyo-API-Key {api_key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'revision': '2024-10-15'
    }
    
    # Sample review data with various formats
    review_formats = [
        {
            "name": "Standard Format",
            "data": {
                "data": {
                    "type": "review",
                    "attributes": {
                        "rating": 5,
                        "title": "Test Review - Debug Tool",
                        "body": "This is a test review created by the debug tool",
                        "reviewer_name": "Debug User",
                        "reviewer_email": "debug@test.com",
                        "created": datetime.now().strftime('%Y-%m-%d'),
                        "verified": True
                    },
                    "relationships": {
                        "item": {
                            "data": {
                                "type": "catalog-item",
                                "id": "$shopify:::$default:::test-product-123"
                            }
                        }
                    }
                }
            }
        },
        {
            "name": "Minimal Format",
            "data": {
                "data": {
                    "type": "review",
                    "attributes": {
                        "rating": 4,
                        "body": "Simple test review"
                    }
                }
            }
        }
    ]
    
    endpoints = [
        'https://a.klaviyo.com/api/reviews/',
        'https://a.klaviyo.com/api/review/',
        'https://a.klaviyo.com/api/reviews'
    ]
    
    for format_info in review_formats:
        print(f"\n   Testing {format_info['name']}:")
        
        for endpoint in endpoints:
            try:
                response = requests.post(endpoint, headers=headers, json=format_info['data'], timeout=15)
                print(f"      {endpoint}: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"         ✅ SUCCESS!")
                    return True
                elif response.status_code == 404:
                    print(f"         → Endpoint not found")
                elif response.status_code == 422:
                    print(f"         → Validation error: {response.text[:200]}")
                elif response.status_code == 403:
                    print(f"         → Permission denied")
                else:
                    print(f"         → Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"      {endpoint}: Exception - {e}")
    
    return False

def test_alternatives(api_key):
    """Test alternative approaches"""
    headers = {
        'Authorization': f'Klaviyo-API-Key {api_key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'revision': '2024-10-15'
    }
    
    # Test 1: Events API
    print("   Testing Events API for review tracking:")
    event_data = {
        "data": {
            "type": "event",
            "attributes": {
                "metric": {"name": "Product Review"},
                "properties": {
                    "rating": 5,
                    "review_title": "Test Review via Events",
                    "review_content": "Testing events API",
                    "product_id": "test-123"
                },
                "profile": {
                    "email": "test@example.com"
                }
            }
        }
    }
    
    try:
        response = requests.post('https://a.klaviyo.com/api/events/', headers=headers, json=event_data, timeout=15)
        print(f"      Events API: {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print(f"         ✅ Events approach might work!")
        else:
            print(f"         → {response.text[:100]}")
    except Exception as e:
        print(f"      Events API: Exception - {e}")
    
    # Test 2: Profile Import
    print("   Testing Profile Import for review data:")
    profile_data = {
        "data": {
            "type": "profile-import",
            "attributes": {
                "profiles": [{
                    "email": "test@example.com",
                    "properties": {
                        "last_review_rating": 5,
                        "last_review_title": "Great product!",
                        "last_review_date": datetime.now().strftime('%Y-%m-%d')
                    }
                }]
            }
        }
    }
    
    try:
        response = requests.post('https://a.klaviyo.com/api/profile-import/', headers=headers, json=profile_data, timeout=15)
        print(f"      Profile Import: {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print(f"         ✅ Profile import approach might work!")
        else:
            print(f"         → {response.text[:100]}")
    except Exception as e:
        print(f"      Profile Import: Exception - {e}")

if __name__ == "__main__":
    main()