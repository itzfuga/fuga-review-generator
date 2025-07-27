"""
AI-Powered Review Generator - Phase 1A Implementation
Advanced review generation using GPT-4 and computer vision
"""
import os
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import openai
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from textblob import TextBlob

@dataclass
class ReviewRequest:
    """Structured review generation request"""
    product_id: str
    product_title: str
    product_description: str
    product_images: List[str]
    target_language: str
    target_rating: int
    review_style: str  # 'authentic', 'enthusiastic', 'detailed', 'casual'
    customer_persona: str  # 'gen_z', 'millennial', 'gen_x', 'boomer'
    market_context: Dict  # Brand positioning, competitor info, etc.

class AIReviewGenerator:
    """Advanced AI-powered review generation engine"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY')
        )
        self.quality_thresholds = {
            'min_authenticity_score': 0.8,
            'min_readability_score': 0.7,
            'max_similarity_threshold': 0.6
        }
        
    def analyze_product_from_image(self, image_url: str) -> Dict:
        """Use GPT-4 Vision to analyze product images"""
        try:
            if not self.openai_client.api_key:
                return {'analysis': 'Image analysis unavailable - OpenAI API key not configured'}
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this product image and provide:
                                1. Material composition (fabric, leather, metal, etc.)
                                2. Style category (gothic, punk, vintage, modern, etc.)
                                3. Key visual features (colors, textures, patterns)
                                4. Target demographic appeal
                                5. Quality indicators visible in image
                                6. Unique selling points
                                
                                Respond in JSON format with these keys: materials, style, features, demographic, quality_indicators, selling_points"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                return json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback: return raw analysis
                return {'analysis': analysis_text}
                
        except Exception as e:
            print(f"Image analysis error: {str(e)}")
            return {'analysis': f'Image analysis failed: {str(e)}'}
    
    def generate_ai_review(self, request: ReviewRequest) -> Dict:
        """Generate review using GPT-4 with advanced prompting"""
        try:
            if not self.openai_client.api_key:
                return self._fallback_generation(request)
            
            # Analyze product images if available
            image_analysis = {}
            if request.product_images:
                image_analysis = self.analyze_product_from_image(request.product_images[0])
            
            # Build sophisticated prompt
            prompt = self._build_advanced_prompt(request, image_analysis)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(request.target_language)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800,
                presence_penalty=0.6,
                frequency_penalty=0.4
            )
            
            review_text = response.choices[0].message.content
            
            # Parse and structure the response
            structured_review = self._parse_ai_response(review_text, request)
            
            # Quality assessment
            quality_score = self._assess_review_quality(structured_review, request)
            
            # If quality is below threshold, regenerate with different approach
            if quality_score < self.quality_thresholds['min_authenticity_score']:
                return self._regenerate_with_fallback(request, image_analysis)
            
            structured_review['ai_quality_score'] = quality_score
            structured_review['generation_method'] = 'gpt4_primary'
            
            return structured_review
            
        except Exception as e:
            print(f"AI generation error: {str(e)}")
            return self._fallback_generation(request)
    
    def _build_advanced_prompt(self, request: ReviewRequest, image_analysis: Dict) -> str:
        """Build sophisticated prompt for GPT-4"""
        
        persona_context = {
            'gen_z': 'Write as an 18-24 year old who uses social media actively, casual language, some slang, emoji occasionally',
            'millennial': 'Write as a 25-40 year old professional, detailed but accessible, references quality and value',
            'gen_x': 'Write as a 40-55 year old, practical focus, values durability and authenticity',
            'boomer': 'Write as a 55+ year old, formal language, emphasizes traditional quality markers'
        }
        
        style_context = {
            'authentic': 'Natural, honest tone with both positives and minor critiques',
            'enthusiastic': 'Very positive, excited tone showing genuine satisfaction',
            'detailed': 'Comprehensive review covering multiple aspects thoroughly',
            'casual': 'Brief, conversational style focusing on key impressions'
        }
        
        image_context = ""
        if image_analysis:
            image_context = f"\nBased on product image analysis: {json.dumps(image_analysis, indent=2)}"
        
        prompt = f"""
        Generate an authentic product review for: {request.product_title}
        
        Product Description: {request.product_description}
        {image_context}
        
        Review Requirements:
        - Language: {request.target_language}
        - Rating: {request.target_rating}/5 stars
        - Customer Persona: {persona_context.get(request.customer_persona, 'General customer')}
        - Style: {style_context.get(request.review_style, 'Natural and authentic')}
        
        Include specific details about:
        1. Product quality and materials (refer to image analysis if available)
        2. Fit, comfort, or usability
        3. Styling and appearance
        4. Value for money
        5. Personal experience with the product
        
        Make the review feel authentic by:
        - Using natural language patterns
        - Including specific but believable details
        - Showing personality appropriate to the customer persona
        - Mentioning realistic usage scenarios
        - Being honest (minor critiques make reviews more believable)
        
        Format the response as JSON with these fields:
        {{
            "title": "Review title (short, engaging)",
            "content": "Full review content",
            "rating": {request.target_rating},
            "author_name": "Realistic name for persona",
            "author_location": "Appropriate location",
            "verified_purchase": true,
            "helpful_votes": 0,
            "review_date": "Recent date",
            "key_points": ["list", "of", "main", "points"]
        }}
        """
        
        return prompt
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for specific language"""
        base_prompt = """You are an expert at writing authentic product reviews that help customers make informed decisions. Your reviews should be:

1. Genuine and believable
2. Culturally appropriate for the target language
3. Specific and detailed without being overly technical
4. Balanced (mostly positive but with minor realistic critiques when appropriate)
5. Engaging and helpful to potential buyers

Always respond in valid JSON format."""

        language_specific = {
            'de': base_prompt + " Write in natural German, using appropriate regional expressions and cultural references.",
            'en': base_prompt + " Write in natural English, considering the target demographic's communication style.",
            'es': base_prompt + " Write in natural Spanish, using appropriate regional expressions and cultural nuances.",
            'fr': base_prompt + " Write in natural French, incorporating appropriate cultural context and expressions.",
            'it': base_prompt + " Write in natural Italian, using appropriate regional expressions and cultural references.",
            'pl': base_prompt + " Write in natural Polish, incorporating appropriate cultural context and expressions.",
            'cs': base_prompt + " Write in natural Czech, using appropriate cultural expressions and regional nuances."
        }
        
        return language_specific.get(language, base_prompt)
    
    def _parse_ai_response(self, response_text: str, request: ReviewRequest) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to parse as JSON first
            parsed = json.loads(response_text)
            
            # Ensure all required fields are present
            required_fields = ['title', 'content', 'rating', 'author_name', 'author_location']
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = self._generate_fallback_field(field, request)
            
            # Add metadata
            parsed['generated_at'] = datetime.now().isoformat()
            parsed['language'] = request.target_language
            parsed['persona'] = request.customer_persona
            parsed['style'] = request.review_style
            
            return parsed
            
        except json.JSONDecodeError:
            # Fallback: try to extract components manually
            return self._manual_parse_response(response_text, request)
    
    def _manual_parse_response(self, response_text: str, request: ReviewRequest) -> Dict:
        """Manually parse response if JSON parsing fails"""
        # Extract title (first line or quoted text)
        title_match = re.search(r'"([^"]+)"', response_text)
        title = title_match.group(1) if title_match else "Great Product!"
        
        # Use the response as content if it's coherent
        content = response_text.strip()
        
        # Generate other fields
        return {
            'title': title,
            'content': content,
            'rating': request.target_rating,
            'author_name': self._generate_fallback_field('author_name', request),
            'author_location': self._generate_fallback_field('author_location', request),
            'verified_purchase': True,
            'helpful_votes': 0,
            'review_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'key_points': [content[:50] + "..."],
            'generated_at': datetime.now().isoformat(),
            'language': request.target_language,
            'persona': request.customer_persona,
            'style': request.review_style,
            'generation_method': 'manual_parse'
        }
    
    def _generate_fallback_field(self, field: str, request: ReviewRequest) -> str:
        """Generate fallback values for missing fields"""
        fallbacks = {
            'author_name': {
                'gen_z': ['Alex', 'Jordan', 'Riley', 'Casey', 'Avery', 'Morgan'],
                'millennial': ['Sarah', 'Mike', 'Jessica', 'David', 'Emily', 'Chris'],
                'gen_x': ['Lisa', 'Mark', 'Karen', 'Steve', 'Linda', 'Paul'],
                'boomer': ['Robert', 'Patricia', 'James', 'Mary', 'John', 'Barbara']
            },
            'author_location': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'],
            'title': ['Great purchase!', 'Love it!', 'Highly recommend', 'Perfect!', 'Excellent quality']
        }
        
        if field == 'author_name':
            return random.choice(fallbacks['author_name'].get(request.customer_persona, fallbacks['author_name']['millennial']))
        elif field in fallbacks:
            return random.choice(fallbacks[field])
        else:
            return ""
    
    def _assess_review_quality(self, review: Dict, request: ReviewRequest) -> float:
        """Assess the quality of generated review"""
        score = 0.0
        
        # Content length appropriateness (0.2 weight)
        content_length = len(review.get('content', ''))
        if 50 <= content_length <= 500:
            score += 0.2
        elif content_length > 20:
            score += 0.1
        
        # Language appropriateness (0.3 weight)
        content = review.get('content', '')
        if content:
            # Check if content contains appropriate language patterns
            blob = TextBlob(content)
            try:
                detected_lang = blob.detect_language()
                if detected_lang == request.target_language[:2]:  # Compare language codes
                    score += 0.3
                else:
                    score += 0.1
            except:
                score += 0.15  # Partial credit if detection fails
        
        # Sentiment appropriateness (0.25 weight)
        if content:
            sentiment = blob.sentiment.polarity
            expected_sentiment = {1: -0.5, 2: -0.2, 3: 0.1, 4: 0.4, 5: 0.7}
            target_sentiment = expected_sentiment.get(request.target_rating, 0.5)
            sentiment_diff = abs(sentiment - target_sentiment)
            if sentiment_diff < 0.3:
                score += 0.25
            elif sentiment_diff < 0.5:
                score += 0.15
            else:
                score += 0.05
        
        # Structure completeness (0.25 weight)
        required_fields = ['title', 'content', 'rating', 'author_name']
        present_fields = sum(1 for field in required_fields if review.get(field))
        score += (present_fields / len(required_fields)) * 0.25
        
        return min(1.0, score)
    
    def _regenerate_with_fallback(self, request: ReviewRequest, image_analysis: Dict) -> Dict:
        """Regenerate with different approach if quality is low"""
        # Try with different temperature and style
        try:
            simplified_prompt = f"""
            Write a {request.target_rating}-star review for: {request.product_title}
            
            Language: {request.target_language}
            Style: Natural and authentic
            Length: 100-200 words
            
            Include: quality, fit, appearance, value
            Tone: {request.review_style}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Write authentic product reviews in the specified language."},
                    {"role": "user", "content": simplified_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            
            return {
                'title': self._generate_fallback_field('title', request),
                'content': content,
                'rating': request.target_rating,
                'author_name': self._generate_fallback_field('author_name', request),
                'author_location': self._generate_fallback_field('author_location', request),
                'verified_purchase': True,
                'helpful_votes': 0,
                'review_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'generated_at': datetime.now().isoformat(),
                'language': request.target_language,
                'persona': request.customer_persona,
                'style': request.review_style,
                'generation_method': 'gpt4_fallback',
                'ai_quality_score': 0.7  # Estimated score for fallback
            }
            
        except Exception as e:
            print(f"Fallback generation error: {str(e)}")
            return self._fallback_generation(request)
    
    def _fallback_generation(self, request: ReviewRequest) -> Dict:
        """Ultimate fallback using template-based generation"""
        from review_generator import generate_review
        
        # Convert request to legacy format
        legacy_product = {
            'id': request.product_id,
            'title': request.product_title,
            'body_html': request.product_description,
            'handle': request.product_title.lower().replace(' ', '-')
        }
        
        # Generate using existing system
        legacy_review = generate_review(legacy_product, existing_reviews=0)
        
        # Add AI metadata
        legacy_review['generation_method'] = 'template_fallback'
        legacy_review['ai_quality_score'] = 0.6  # Baseline score for template generation
        legacy_review['persona'] = request.customer_persona
        legacy_review['style'] = request.review_style
        
        return legacy_review

def create_ai_review_request(product: Dict, target_language: str = 'en', 
                           target_rating: int = 5, review_style: str = 'authentic',
                           customer_persona: str = 'millennial') -> ReviewRequest:
    """Create an AI review request from product data"""
    
    # Extract product images
    images = []
    if product.get('images'):
        images = [img.get('src', '') for img in product['images'] if img.get('src')]
    
    # Clean product description
    description = product.get('body_html', '')
    if description:
        # Strip HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        description = description.strip()
    
    return ReviewRequest(
        product_id=str(product.get('id', '')),
        product_title=product.get('title', ''),
        product_description=description,
        product_images=images,
        target_language=target_language,
        target_rating=target_rating,
        review_style=review_style,
        customer_persona=customer_persona,
        market_context={}
    )

# Integration function for existing codebase
def generate_ai_enhanced_review(product: Dict, existing_reviews: int = 0) -> Dict:
    """
    Enhanced review generation function that integrates with existing codebase
    Falls back to template-based generation if AI is unavailable
    """
    
    # Determine target language and persona based on existing logic
    languages = ['en', 'de', 'es', 'fr', 'it', 'pl', 'cs']
    target_language = random.choice(languages)
    
    personas = ['gen_z', 'millennial', 'gen_x']
    weights = [0.4, 0.4, 0.2]  # Bias towards younger demographics
    customer_persona = random.choices(personas, weights=weights)[0]
    
    # Rating distribution (matching existing logic)
    rating_distribution = [5, 5, 5, 5, 5, 5, 4, 4, 4, 3]
    target_rating = random.choice(rating_distribution)
    
    review_styles = ['authentic', 'enthusiastic', 'detailed', 'casual']
    review_style = random.choice(review_styles)
    
    # Create AI request
    ai_request = create_ai_review_request(
        product=product,
        target_language=target_language,
        target_rating=target_rating,
        review_style=review_style,
        customer_persona=customer_persona
    )
    
    # Generate with AI
    ai_generator = AIReviewGenerator()
    ai_review = ai_generator.generate_ai_review(ai_request)
    
    # Convert to format expected by existing codebase
    return {
        'author': ai_review.get('author_name', 'Anonymous'),
        'email': f"{ai_review.get('author_name', 'user').lower().replace(' ', '')}@example.com",
        'location': ai_review.get('author_location', 'Unknown'),
        'title': ai_review.get('title', ''),
        'content': ai_review.get('content', ''),
        'date': ai_review.get('review_date', datetime.now().strftime('%Y-%m-%d')),
        'rating': ai_review.get('rating', 5),
        'verified': 'Yes' if ai_review.get('verified_purchase', True) else 'No',
        'language': ai_review.get('language', target_language),
        'generation_method': ai_review.get('generation_method', 'ai_enhanced'),
        'ai_quality_score': ai_review.get('ai_quality_score', 0.8),
        'persona': ai_review.get('persona', customer_persona),
        'style': ai_review.get('style', review_style)
    }