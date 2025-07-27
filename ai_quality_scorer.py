"""
AI Quality Scoring System - Phase 6A Implementation
Advanced quality assessment for generated reviews using multiple ML techniques
"""
import os
import json
import re
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import random

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for a review"""
    overall_score: float
    authenticity_score: float
    readability_score: float
    language_consistency_score: float
    sentiment_appropriateness_score: float
    content_depth_score: float
    uniqueness_score: float
    demographic_alignment_score: float
    commercial_value_score: float
    
    # Detailed breakdowns
    metrics_breakdown: Dict
    recommendations: List[str]
    flagged_issues: List[str]
    generation_metadata: Dict

class ReviewQualityScorer:
    """Advanced AI-powered review quality assessment system"""
    
    def __init__(self):
        self.quality_standards = self._load_quality_standards()
        self.language_models = self._initialize_language_models()
        self.similarity_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.review_history = []  # For similarity checking
        
    def _load_quality_standards(self) -> Dict:
        """Load quality standards and thresholds"""
        return {
            'min_length': {
                'title': 3,
                'content': 20
            },
            'max_length': {
                'title': 100,
                'content': 1000
            },
            'authenticity_indicators': {
                'personal_pronouns': ['I', 'my', 'me', 'ich', 'mein', 'yo', 'mi', 'je', 'mon', 'io', 'mio'],
                'experience_words': ['bought', 'purchased', 'ordered', 'received', 'gekauft', 'bestellt', 'compré', 'acheté', 'comprato'],
                'emotion_words': ['love', 'like', 'happy', 'satisfied', 'disappointed', 'liebe', 'mag', 'glücklich', 'zufrieden']
            },
            'red_flags': {
                'excessive_caps': r'[A-Z]{4,}',
                'excessive_punctuation': r'[!?]{3,}',
                'excessive_emojis': r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]{4,}',
                'repetitive_phrases': r'(.{10,})\1{2,}',
                'placeholder_text': r'\[.*\]|TODO|PLACEHOLDER'
            },
            'rating_sentiment_correlation': {
                1: (-1.0, -0.5),
                2: (-0.5, -0.1),
                3: (-0.1, 0.2),
                4: (0.2, 0.6),
                5: (0.6, 1.0)
            }
        }
    
    def _initialize_language_models(self) -> Dict:
        """Initialize language-specific models and patterns"""
        return {
            'readability_formulas': {
                'en': 'flesch_kincaid',
                'de': 'flesch_reading_ease',
                'es': 'fernandez_huerta',
                'fr': 'flesch_reading_ease',
                'it': 'flesch_reading_ease'
            },
            'common_patterns': {
                'en': {
                    'authentic_starters': ['I bought', 'Just received', 'Ordered this', 'Got this', 'Perfect for'],
                    'natural_transitions': ['Overall', 'However', 'Also', 'Additionally', 'The only thing'],
                    'authentic_closers': ['Would recommend', 'Worth the money', 'Happy with purchase', 'Will buy again']
                },
                'de': {
                    'authentic_starters': ['Habe gekauft', 'Gerade erhalten', 'Bestellt', 'Super für'],
                    'natural_transitions': ['Insgesamt', 'Jedoch', 'Auch', 'Zusätzlich', 'Das einzige'],
                    'authentic_closers': ['Kann empfehlen', 'Preis wert', 'Zufrieden', 'Kaufe wieder']
                }
            }
        }
    
    def assess_review_quality(self, review: Dict, product_context: Dict = None, 
                            historical_reviews: List[Dict] = None) -> QualityMetrics:
        """
        Comprehensive quality assessment of a review
        
        Args:
            review: Review data dictionary
            product_context: Product information for context-aware scoring
            historical_reviews: Previous reviews for similarity checking
        
        Returns:
            QualityMetrics object with detailed assessment
        """
        
        # Extract review components
        title = review.get('title', '')
        content = review.get('content', '')
        rating = review.get('rating', 5)
        language = review.get('language', 'en')
        author = review.get('author', '')
        location = review.get('location', '')
        
        # Initialize metrics
        metrics = {
            'authenticity': self._assess_authenticity(title, content, language, rating),
            'readability': self._assess_readability(content, language),
            'language_consistency': self._assess_language_consistency(review),
            'sentiment_appropriateness': self._assess_sentiment_appropriateness(content, rating, language),
            'content_depth': self._assess_content_depth(content, title, product_context),
            'uniqueness': self._assess_uniqueness(content, historical_reviews),
            'demographic_alignment': self._assess_demographic_alignment(review, product_context),
            'commercial_value': self._assess_commercial_value(review, product_context)
        }
        
        # Calculate overall score
        weights = {
            'authenticity': 0.25,
            'readability': 0.15,
            'language_consistency': 0.15,
            'sentiment_appropriateness': 0.15,
            'content_depth': 0.10,
            'uniqueness': 0.10,
            'demographic_alignment': 0.05,
            'commercial_value': 0.05
        }
        
        overall_score = sum(metrics[key] * weights[key] for key in weights)
        
        # Generate recommendations and flag issues
        recommendations = self._generate_recommendations(metrics, review)
        flagged_issues = self._identify_issues(metrics, review)
        
        # Create quality metrics object
        quality_metrics = QualityMetrics(
            overall_score=overall_score,
            authenticity_score=metrics['authenticity'],
            readability_score=metrics['readability'],
            language_consistency_score=metrics['language_consistency'],
            sentiment_appropriateness_score=metrics['sentiment_appropriateness'],
            content_depth_score=metrics['content_depth'],
            uniqueness_score=metrics['uniqueness'],
            demographic_alignment_score=metrics['demographic_alignment'],
            commercial_value_score=metrics['commercial_value'],
            metrics_breakdown=metrics,
            recommendations=recommendations,
            flagged_issues=flagged_issues,
            generation_metadata={
                'assessed_at': datetime.now().isoformat(),
                'scorer_version': '1.0',
                'review_id': review.get('id', 'unknown')
            }
        )
        
        return quality_metrics
    
    def _assess_authenticity(self, title: str, content: str, language: str, rating: int) -> float:
        """Assess how authentic and human-like the review appears"""
        score = 1.0
        text = f"{title} {content}".lower()
        
        # Check for personal indicators
        personal_indicators = self.quality_standards['authenticity_indicators']['personal_pronouns']
        personal_count = sum(1 for indicator in personal_indicators if indicator.lower() in text)
        if personal_count == 0:
            score -= 0.2
        elif personal_count > 5:
            score -= 0.1  # Too many personal pronouns can seem fake
        
        # Check for experience words
        experience_words = self.quality_standards['authenticity_indicators']['experience_words']
        experience_count = sum(1 for word in experience_words if word.lower() in text)
        if experience_count == 0:
            score -= 0.15
        
        # Check for emotional language
        emotion_words = self.quality_standards['authenticity_indicators']['emotion_words']
        emotion_count = sum(1 for word in emotion_words if word.lower() in text)
        if emotion_count == 0:
            score -= 0.1
        
        # Check for red flags
        for flag_name, pattern in self.quality_standards['red_flags'].items():
            if re.search(pattern, content, re.IGNORECASE):
                if flag_name == 'excessive_caps':
                    score -= 0.2
                elif flag_name == 'excessive_punctuation':
                    score -= 0.15
                elif flag_name == 'repetitive_phrases':
                    score -= 0.3
                elif flag_name == 'placeholder_text':
                    score -= 0.5
        
        # Length appropriateness
        content_length = len(content)
        if content_length < 20:
            score -= 0.1
        elif content_length > 500:
            score -= 0.05
        
        # Natural sentence structure (basic check)
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if avg_sentence_length < 3 or avg_sentence_length > 30:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _assess_readability(self, content: str, language: str) -> float:
        """Assess readability and clarity of the review"""
        if not content or len(content) < 10:
            return 0.1
        
        # Basic readability metrics
        words = content.split()
        sentences = content.split('.')
        
        if len(sentences) == 0:
            return 0.2
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = self._estimate_syllables(words)
        
        # Simplified Flesch-Kincaid-like calculation
        readability_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale (assume 0-100 input range)
        normalized_score = max(0, min(100, readability_score)) / 100
        
        # Adjust for optimal reading level (60-80 is good for reviews)
        if 60 <= readability_score <= 80:
            return 1.0
        elif 40 <= readability_score <= 90:
            return 0.8
        else:
            return 0.5
    
    def _estimate_syllables(self, words: List[str]) -> float:
        """Estimate average syllables per word"""
        total_syllables = 0
        for word in words:
            # Simple syllable estimation
            vowels = 'aeiouy'
            syllables = len([char for char in word.lower() if char in vowels])
            if syllables == 0:
                syllables = 1
            total_syllables += syllables
        
        return total_syllables / max(len(words), 1)
    
    def _assess_language_consistency(self, review: Dict) -> float:
        """Assess consistency of language usage throughout the review"""
        content = review.get('content', '')
        title = review.get('title', '')
        location = review.get('location', '')
        target_language = review.get('language', 'en')
        
        if not content:
            return 0.0
        
        # Use TextBlob for language detection
        try:
            full_text = f"{title} {content}"
            blob = TextBlob(full_text)
            detected_language = blob.detect_language()
            
            # Map common language codes
            lang_mapping = {
                'en': 'en', 'de': 'de', 'es': 'es', 'fr': 'fr', 
                'it': 'it', 'pl': 'pl', 'cs': 'cs', 'pt': 'pt'
            }
            
            target_code = lang_mapping.get(target_language, target_language)
            
            if detected_language == target_code:
                return 1.0
            else:
                # Partial credit for similar languages
                similar_langs = {
                    'en': ['en'],
                    'de': ['de', 'nl'],
                    'es': ['es', 'pt', 'ca'],
                    'fr': ['fr'],
                    'it': ['it', 'es'],
                    'pl': ['pl', 'cs', 'sk'],
                    'cs': ['cs', 'sk', 'pl']
                }
                
                if detected_language in similar_langs.get(target_code, []):
                    return 0.7
                else:
                    return 0.3
                    
        except Exception:
            # If detection fails, use heuristics
            return self._heuristic_language_check(content, target_language)
    
    def _heuristic_language_check(self, content: str, target_language: str) -> float:
        """Fallback language consistency check using heuristics"""
        # Simple character-based heuristics
        language_indicators = {
            'de': ['ä', 'ö', 'ü', 'ß', 'ist', 'und', 'der', 'die', 'das'],
            'es': ['ñ', 'é', 'í', 'ó', 'ú', 'el', 'la', 'es', 'en', 'con'],
            'fr': ['à', 'é', 'è', 'ç', 'le', 'la', 'est', 'dans', 'avec'],
            'it': ['è', 'ì', 'ò', 'ù', 'il', 'la', 'è', 'con', 'per'],
            'pl': ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż', 'jest', 'nie', 'to'],
            'cs': ['č', 'ř', 'š', 'ž', 'ý', 'ě', 'ú', 'ů', 'je', 'se', 'na']
        }
        
        indicators = language_indicators.get(target_language, [])
        if not indicators:
            return 0.5  # Unknown language
        
        content_lower = content.lower()
        matches = sum(1 for indicator in indicators if indicator in content_lower)
        
        # Score based on indicator presence
        if matches >= 3:
            return 1.0
        elif matches >= 1:
            return 0.7
        else:
            return 0.3
    
    def _assess_sentiment_appropriateness(self, content: str, rating: int, language: str) -> float:
        """Assess if sentiment matches the rating"""
        if not content:
            return 0.0
        
        try:
            blob = TextBlob(content)
            sentiment = blob.sentiment.polarity  # -1 to 1
            
            # Expected sentiment ranges for each rating
            expected_ranges = self.quality_standards['rating_sentiment_correlation']
            expected_min, expected_max = expected_ranges.get(rating, (0.0, 1.0))
            
            # Check if sentiment is within expected range
            if expected_min <= sentiment <= expected_max:
                return 1.0
            else:
                # Calculate distance from expected range
                if sentiment < expected_min:
                    distance = expected_min - sentiment
                else:
                    distance = sentiment - expected_max
                
                # Score decreases with distance
                score = max(0.0, 1.0 - (distance * 2))
                return score
                
        except Exception:
            # If sentiment analysis fails, use keyword-based approach
            return self._keyword_sentiment_check(content, rating)
    
    def _keyword_sentiment_check(self, content: str, rating: int) -> float:
        """Fallback sentiment check using keywords"""
        positive_words = ['great', 'excellent', 'amazing', 'perfect', 'love', 'awesome', 
                         'fantastic', 'wonderful', 'outstanding', 'brilliant']
        negative_words = ['terrible', 'awful', 'horrible', 'disappointing', 'waste', 
                         'poor', 'bad', 'worst', 'useless', 'regret']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        # Simple sentiment score
        if positive_count > negative_count and rating >= 4:
            return 1.0
        elif negative_count > positive_count and rating <= 2:
            return 1.0
        elif positive_count == negative_count and rating == 3:
            return 1.0
        else:
            return 0.5
    
    def _assess_content_depth(self, content: str, title: str, product_context: Dict = None) -> float:
        """Assess the depth and informativeness of the review content"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Length appropriateness
        content_length = len(content)
        if 50 <= content_length <= 300:
            score += 0.3
        elif 20 <= content_length <= 500:
            score += 0.2
        else:
            score += 0.1
        
        # Information categories covered
        info_categories = {
            'quality': ['quality', 'material', 'build', 'construction', 'fabric', 'durable'],
            'appearance': ['looks', 'color', 'style', 'design', 'attractive', 'beautiful'],
            'fit': ['fits', 'size', 'comfortable', 'tight', 'loose', 'perfect fit'],
            'value': ['price', 'value', 'worth', 'money', 'expensive', 'cheap', 'affordable'],
            'experience': ['delivery', 'shipping', 'packaging', 'arrived', 'ordered', 'bought']
        }
        
        content_lower = content.lower()
        categories_covered = 0
        for category, keywords in info_categories.items():
            if any(keyword in content_lower for keyword in keywords):
                categories_covered += 1
        
        # Score based on coverage
        score += (categories_covered / len(info_categories)) * 0.4
        
        # Specific details (numbers, specific mentions)
        detail_patterns = [
            r'\d+\s*(day|week|month|year)',  # Time references
            r'\d+\s*(inch|cm|size|xl|large|small)',  # Size references
            r'\$\d+',  # Price mentions
            r'\d+\s*star',  # Star ratings
            r'(exactly|perfectly|slightly|much|very)\s+\w+'  # Qualitative modifiers
        ]
        
        detail_count = sum(1 for pattern in detail_patterns 
                          if re.search(pattern, content_lower))
        score += min(0.3, detail_count * 0.1)
        
        return min(1.0, score)
    
    def _assess_uniqueness(self, content: str, historical_reviews: List[Dict] = None) -> float:
        """Assess uniqueness compared to historical reviews"""
        if not content or not historical_reviews:
            return 1.0  # Assume unique if no comparison data
        
        # Use TF-IDF similarity
        try:
            historical_content = [review.get('content', '') for review in historical_reviews[-100:]]  # Last 100 reviews
            historical_content = [c for c in historical_content if c]  # Filter empty content
            
            if not historical_content:
                return 1.0
            
            all_content = historical_content + [content]
            tfidf_matrix = self.similarity_vectorizer.fit_transform(all_content)
            
            # Calculate similarity with historical reviews
            new_review_vector = tfidf_matrix[-1]
            historical_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(new_review_vector, historical_vectors).flatten()
            max_similarity = np.max(similarities) if len(similarities) > 0 else 0.0
            
            # Score based on uniqueness (lower similarity = higher uniqueness)
            uniqueness_score = 1.0 - max_similarity
            
            return max(0.0, min(1.0, uniqueness_score))
            
        except Exception:
            # Fallback: simple text comparison
            return self._simple_uniqueness_check(content, historical_reviews)
    
    def _simple_uniqueness_check(self, content: str, historical_reviews: List[Dict]) -> float:
        """Simple uniqueness check without ML"""
        if not historical_reviews:
            return 1.0
        
        content_words = set(content.lower().split())
        similarities = []
        
        for review in historical_reviews[-50:]:  # Check last 50 reviews
            historical_content = review.get('content', '')
            if not historical_content:
                continue
            
            historical_words = set(historical_content.lower().split())
            if len(content_words) == 0 or len(historical_words) == 0:
                continue
            
            # Jaccard similarity
            intersection = content_words.intersection(historical_words)
            union = content_words.union(historical_words)
            similarity = len(intersection) / len(union)
            similarities.append(similarity)
        
        if not similarities:
            return 1.0
        
        max_similarity = max(similarities)
        return 1.0 - max_similarity
    
    def _assess_demographic_alignment(self, review: Dict, product_context: Dict = None) -> float:
        """Assess if review style matches expected demographic"""
        # This is a simplified implementation
        # In a full system, this would use more sophisticated demographic analysis
        
        content = review.get('content', '')
        persona = review.get('persona', 'millennial')
        language = review.get('language', 'en')
        
        if not content:
            return 0.5
        
        # Basic style indicators
        style_indicators = {
            'gen_z': {
                'casual_language': ['omg', 'tbh', 'ngl', 'lowkey', 'highkey', 'literally', 'obsessed'],
                'informal_grammar': True,
                'emoji_usage': True,
                'abbreviations': ['ur', 'bc', 'rn', 'fr']
            },
            'millennial': {
                'detailed_reviews': True,
                'value_conscious': ['worth', 'value', 'price', 'investment'],
                'experience_focused': ['experience', 'quality', 'recommend'],
                'moderate_formality': True
            },
            'gen_x': {
                'practical_focus': ['practical', 'functional', 'durable', 'reliable'],
                'quality_emphasis': ['quality', 'craftsmanship', 'materials'],
                'formal_language': True
            }
        }
        
        indicators = style_indicators.get(persona, style_indicators['millennial'])
        content_lower = content.lower()
        
        score = 0.5  # Base score
        
        # Check for presence of demographic indicators
        for indicator_type, keywords in indicators.items():
            if isinstance(keywords, list):
                if any(keyword in content_lower for keyword in keywords):
                    score += 0.1
            elif isinstance(keywords, bool) and keywords:
                # Style checks that require boolean evaluation
                if indicator_type == 'informal_grammar' and any(c in content for c in ['!!', '??']):
                    score += 0.1
                elif indicator_type == 'emoji_usage' and re.search(r'[\U0001F600-\U0001F64F]', content):
                    score += 0.1
                elif indicator_type == 'formal_language' and not re.search(r'[!]{2,}', content):
                    score += 0.1
        
        return min(1.0, score)
    
    def _assess_commercial_value(self, review: Dict, product_context: Dict = None) -> float:
        """Assess the commercial value and persuasiveness of the review"""
        content = review.get('content', '')
        title = review.get('title', '')
        rating = review.get('rating', 5)
        
        if not content:
            return 0.0
        
        score = 0.0
        
        # Persuasive elements
        persuasive_elements = {
            'social_proof': ['recommend', 'everyone', 'friends', 'family', 'colleagues'],
            'specific_benefits': ['comfortable', 'stylish', 'durable', 'versatile', 'perfect'],
            'usage_scenarios': ['work', 'party', 'casual', 'everyday', 'special occasion'],
            'comparison': ['better than', 'compared to', 'unlike', 'superior'],
            'call_to_action': ['buy', 'get', 'purchase', 'try', 'consider']
        }
        
        content_lower = content.lower()
        for element_type, keywords in persuasive_elements.items():
            if any(keyword in content_lower for keyword in keywords):
                score += 0.15
        
        # Balanced perspective (mentions both pros and potential cons)
        has_minor_criticism = any(word in content_lower for word in 
                                ['however', 'but', 'only issue', 'wish', 'could be better'])
        if has_minor_criticism and rating >= 4:
            score += 0.2  # Balanced reviews are more trustworthy
        
        # Clear value proposition
        value_indicators = ['worth', 'value', 'price', 'investment', 'money', 'affordable']
        if any(indicator in content_lower for indicator in value_indicators):
            score += 0.15
        
        return min(1.0, score)
    
    def _generate_recommendations(self, metrics: Dict, review: Dict) -> List[str]:
        """Generate improvement recommendations based on metrics"""
        recommendations = []
        
        if metrics['authenticity'] < 0.7:
            recommendations.append("Add more personal experience details and emotional language")
        
        if metrics['readability'] < 0.6:
            recommendations.append("Simplify sentence structure and use clearer language")
        
        if metrics['content_depth'] < 0.6:
            recommendations.append("Include more specific details about quality, fit, and value")
        
        if metrics['uniqueness'] < 0.7:
            recommendations.append("Use more unique phrasing to avoid similarity with existing reviews")
        
        if metrics['sentiment_appropriateness'] < 0.7:
            recommendations.append("Align emotional tone better with the star rating")
        
        if metrics['commercial_value'] < 0.6:
            recommendations.append("Include more persuasive elements and usage scenarios")
        
        return recommendations
    
    def _identify_issues(self, metrics: Dict, review: Dict) -> List[str]:
        """Identify specific issues with the review"""
        issues = []
        content = review.get('content', '')
        
        # Check for critical issues
        if metrics['authenticity'] < 0.5:
            issues.append("CRITICAL: Review appears artificial or template-based")
        
        if metrics['language_consistency'] < 0.5:
            issues.append("WARNING: Language inconsistency detected")
        
        if metrics['uniqueness'] < 0.4:
            issues.append("WARNING: High similarity to existing reviews")
        
        # Check for specific problems
        if len(content) < 20:
            issues.append("Content too short for meaningful review")
        
        if re.search(r'[A-Z]{5,}', content):
            issues.append("Excessive use of capital letters")
        
        if re.search(r'[!?]{4,}', content):
            issues.append("Excessive punctuation usage")
        
        return issues

def batch_assess_reviews(reviews: List[Dict], product_context: Dict = None) -> List[QualityMetrics]:
    """Assess quality for a batch of reviews"""
    scorer = ReviewQualityScorer()
    results = []
    
    for i, review in enumerate(reviews):
        # Use previous reviews for uniqueness assessment
        historical_reviews = reviews[:i] if i > 0 else []
        quality_metrics = scorer.assess_review_quality(
            review, 
            product_context=product_context,
            historical_reviews=historical_reviews
        )
        results.append(quality_metrics)
    
    return results

def get_quality_summary(quality_metrics_list: List[QualityMetrics]) -> Dict:
    """Generate summary statistics for a batch of quality assessments"""
    if not quality_metrics_list:
        return {}
    
    scores = [qm.overall_score for qm in quality_metrics_list]
    authenticity_scores = [qm.authenticity_score for qm in quality_metrics_list]
    
    return {
        'total_reviews': len(quality_metrics_list),
        'average_quality': np.mean(scores),
        'quality_std': np.std(scores),
        'high_quality_count': sum(1 for score in scores if score >= 0.8),
        'low_quality_count': sum(1 for score in scores if score < 0.6),
        'average_authenticity': np.mean(authenticity_scores),
        'quality_distribution': {
            'excellent': sum(1 for score in scores if score >= 0.9),
            'good': sum(1 for score in scores if 0.8 <= score < 0.9),
            'average': sum(1 for score in scores if 0.6 <= score < 0.8),
            'poor': sum(1 for score in scores if score < 0.6)
        },
        'common_issues': _get_common_issues(quality_metrics_list),
        'top_recommendations': _get_top_recommendations(quality_metrics_list)
    }

def _get_common_issues(quality_metrics_list: List[QualityMetrics]) -> List[Tuple[str, int]]:
    """Get most common issues across reviews"""
    issue_counts = {}
    for qm in quality_metrics_list:
        for issue in qm.flagged_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    
    return sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

def _get_top_recommendations(quality_metrics_list: List[QualityMetrics]) -> List[Tuple[str, int]]:
    """Get most common recommendations across reviews"""
    rec_counts = {}
    for qm in quality_metrics_list:
        for rec in qm.recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
    
    return sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:5]

# Integration with existing review generation
def assess_generated_reviews(reviews: List[Dict], product: Dict = None) -> Dict:
    """
    Assess quality of generated reviews and return comprehensive report
    
    Args:
        reviews: List of generated reviews
        product: Product context for assessment
    
    Returns:
        Dictionary with quality assessment results
    """
    
    quality_results = batch_assess_reviews(reviews, product_context=product)
    summary = get_quality_summary(quality_results)
    
    # Add detailed results
    detailed_results = []
    for i, (review, quality) in enumerate(zip(reviews, quality_results)):
        detailed_results.append({
            'review_index': i,
            'review_content': review.get('content', '')[:100] + '...',
            'overall_score': quality.overall_score,
            'authenticity_score': quality.authenticity_score,
            'readability_score': quality.readability_score,
            'uniqueness_score': quality.uniqueness_score,
            'issues': quality.flagged_issues,
            'recommendations': quality.recommendations[:3]  # Top 3 recommendations
        })
    
    return {
        'summary': summary,
        'detailed_results': detailed_results,
        'assessment_metadata': {
            'assessed_at': datetime.now().isoformat(),
            'total_reviews_assessed': len(reviews),
            'scorer_version': '1.0'
        }
    }