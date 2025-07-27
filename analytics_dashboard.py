"""
Performance Analytics Dashboard - Phase 3A Implementation
Comprehensive analytics and insights for review generation performance
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
from collections import defaultdict, Counter
import statistics

@dataclass
class DashboardMetrics:
    """Core metrics for the analytics dashboard"""
    total_reviews_generated: int
    reviews_by_platform: Dict[str, int]
    quality_scores: Dict[str, float]
    language_distribution: Dict[str, int]
    rating_distribution: Dict[int, int]
    generation_methods: Dict[str, int]
    performance_trends: Dict[str, List[Any]]
    top_products: List[Dict]
    error_rates: Dict[str, float]
    user_engagement: Dict[str, Any]

class AnalyticsDashboard:
    """Comprehensive analytics dashboard for review generation system"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for analytics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                product_title TEXT,
                review_id TEXT,
                generation_method TEXT,
                ai_enabled BOOLEAN,
                ai_quality_score REAL,
                language TEXT,
                rating INTEGER,
                content_length INTEGER,
                platform TEXT,
                created_at TIMESTAMP,
                authenticity_score REAL,
                readability_score REAL,
                uniqueness_score REAL,
                commercial_value_score REAL,
                user_session_id TEXT,
                generation_time_ms INTEGER,
                error_occurred BOOLEAN,
                error_message TEXT
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                metric_category TEXT,
                recorded_at TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_type TEXT,
                session_start TIMESTAMP,
                session_end TIMESTAMP,
                reviews_generated INTEGER,
                platforms_used TEXT,
                features_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_review_generation(self, review_data: Dict, generation_metadata: Dict):
        """Log a review generation event for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reviews_analytics (
                product_id, product_title, review_id, generation_method, ai_enabled,
                ai_quality_score, language, rating, content_length, platform,
                created_at, authenticity_score, readability_score, uniqueness_score,
                commercial_value_score, user_session_id, generation_time_ms,
                error_occurred, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            generation_metadata.get('product_id'),
            generation_metadata.get('product_title'),
            generation_metadata.get('review_id', ''),
            review_data.get('generation_method', 'unknown'),
            review_data.get('ai_enabled', False),
            review_data.get('ai_quality_score', 0.0),
            review_data.get('language', 'en'),
            review_data.get('rating', 5),
            len(review_data.get('content', '')),
            generation_metadata.get('platform', 'unknown'),
            datetime.now().isoformat(),
            generation_metadata.get('authenticity_score', 0.0),
            generation_metadata.get('readability_score', 0.0),
            generation_metadata.get('uniqueness_score', 0.0),
            generation_metadata.get('commercial_value_score', 0.0),
            generation_metadata.get('session_id', ''),
            generation_metadata.get('generation_time_ms', 0),
            generation_metadata.get('error_occurred', False),
            generation_metadata.get('error_message', '')
        ))
        
        conn.commit()
        conn.close()
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             category: str = 'general', metadata: Dict = None):
        """Log a performance metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics (metric_name, metric_value, metric_category, recorded_at, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            metric_name,
            value,
            category,
            datetime.now().isoformat(),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def log_user_session(self, session_data: Dict):
        """Log user session data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions (
                session_id, user_type, session_start, session_end,
                reviews_generated, platforms_used, features_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data.get('session_id'),
            session_data.get('user_type', 'unknown'),
            session_data.get('session_start'),
            session_data.get('session_end'),
            session_data.get('reviews_generated', 0),
            json.dumps(session_data.get('platforms_used', [])),
            json.dumps(session_data.get('features_used', []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_dashboard_metrics(self, days: int = 30) -> DashboardMetrics:
        """Get comprehensive dashboard metrics for the specified period"""
        start_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute('''
            SELECT COUNT(*) FROM reviews_analytics 
            WHERE created_at >= ?
        ''', (start_date.isoformat(),))
        total_reviews = cursor.fetchone()[0]
        
        # Reviews by platform
        cursor.execute('''
            SELECT platform, COUNT(*) FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY platform
        ''', (start_date.isoformat(),))
        reviews_by_platform = dict(cursor.fetchall())
        
        # Quality scores
        cursor.execute('''
            SELECT 
                AVG(ai_quality_score),
                AVG(authenticity_score),
                AVG(readability_score),
                AVG(uniqueness_score),
                AVG(commercial_value_score)
            FROM reviews_analytics 
            WHERE created_at >= ? AND ai_quality_score > 0
        ''', (start_date.isoformat(),))
        quality_data = cursor.fetchone()
        quality_scores = {
            'overall': quality_data[0] or 0.0,
            'authenticity': quality_data[1] or 0.0,
            'readability': quality_data[2] or 0.0,
            'uniqueness': quality_data[3] or 0.0,
            'commercial_value': quality_data[4] or 0.0
        }
        
        # Language distribution
        cursor.execute('''
            SELECT language, COUNT(*) FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY language
        ''', (start_date.isoformat(),))
        language_distribution = dict(cursor.fetchall())
        
        # Rating distribution
        cursor.execute('''
            SELECT rating, COUNT(*) FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY rating
        ''', (start_date.isoformat(),))
        rating_distribution = dict(cursor.fetchall())
        
        # Generation methods
        cursor.execute('''
            SELECT generation_method, COUNT(*) FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY generation_method
        ''', (start_date.isoformat(),))
        generation_methods = dict(cursor.fetchall())
        
        # Performance trends (daily aggregates)
        performance_trends = self._get_performance_trends(cursor, start_date, days)
        
        # Top products
        cursor.execute('''
            SELECT product_title, COUNT(*) as review_count, AVG(ai_quality_score) as avg_quality
            FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY product_id, product_title
            ORDER BY review_count DESC
            LIMIT 10
        ''', (start_date.isoformat(),))
        top_products = [
            {'title': row[0], 'review_count': row[1], 'avg_quality': row[2] or 0.0}
            for row in cursor.fetchall()
        ]
        
        # Error rates
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as errors,
                COUNT(*) as total,
                generation_method
            FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY generation_method
        ''', (start_date.isoformat(),))
        error_data = cursor.fetchall()
        error_rates = {
            row[2]: (row[0] / row[1] * 100) if row[1] > 0 else 0.0
            for row in error_data
        }
        
        # User engagement
        user_engagement = self._get_user_engagement_metrics(cursor, start_date)
        
        conn.close()
        
        return DashboardMetrics(
            total_reviews_generated=total_reviews,
            reviews_by_platform=reviews_by_platform,
            quality_scores=quality_scores,
            language_distribution=language_distribution,
            rating_distribution=rating_distribution,
            generation_methods=generation_methods,
            performance_trends=performance_trends,
            top_products=top_products,
            error_rates=error_rates,
            user_engagement=user_engagement
        )
    
    def _get_performance_trends(self, cursor, start_date: datetime, days: int) -> Dict[str, List[Any]]:
        """Get performance trends over time"""
        trends = {
            'daily_reviews': [],
            'daily_quality_avg': [],
            'daily_errors': [],
            'ai_usage_percentage': []
        }
        
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            # Daily review count
            cursor.execute('''
                SELECT COUNT(*) FROM reviews_analytics 
                WHERE created_at >= ? AND created_at < ?
            ''', (day_start.isoformat(), day_end.isoformat()))
            daily_count = cursor.fetchone()[0]
            
            # Daily quality average
            cursor.execute('''
                SELECT AVG(ai_quality_score) FROM reviews_analytics 
                WHERE created_at >= ? AND created_at < ? AND ai_quality_score > 0
            ''', (day_start.isoformat(), day_end.isoformat()))
            daily_quality = cursor.fetchone()[0] or 0.0
            
            # Daily error count
            cursor.execute('''
                SELECT COUNT(*) FROM reviews_analytics 
                WHERE created_at >= ? AND created_at < ? AND error_occurred = 1
            ''', (day_start.isoformat(), day_end.isoformat()))
            daily_errors = cursor.fetchone()[0]
            
            # AI usage percentage
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN ai_enabled THEN 1 ELSE 0 END) as ai_count,
                    COUNT(*) as total_count
                FROM reviews_analytics 
                WHERE created_at >= ? AND created_at < ?
            ''', (day_start.isoformat(), day_end.isoformat()))
            ai_data = cursor.fetchone()
            ai_percentage = (ai_data[0] / ai_data[1] * 100) if ai_data[1] > 0 else 0.0
            
            trends['daily_reviews'].append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': daily_count
            })
            trends['daily_quality_avg'].append({
                'date': day_start.strftime('%Y-%m-%d'),
                'quality': daily_quality
            })
            trends['daily_errors'].append({
                'date': day_start.strftime('%Y-%m-%d'),
                'errors': daily_errors
            })
            trends['ai_usage_percentage'].append({
                'date': day_start.strftime('%Y-%m-%d'),
                'percentage': ai_percentage
            })
        
        return trends
    
    def _get_user_engagement_metrics(self, cursor, start_date: datetime) -> Dict[str, Any]:
        """Get user engagement metrics"""
        # Session metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                AVG(reviews_generated) as avg_reviews_per_session,
                AVG(JULIANDAY(session_end) - JULIANDAY(session_start)) * 24 * 60 as avg_session_minutes
            FROM user_sessions 
            WHERE session_start >= ?
        ''', (start_date.isoformat(),))
        session_data = cursor.fetchone()
        
        # Feature usage
        cursor.execute('''
            SELECT features_used FROM user_sessions 
            WHERE session_start >= ? AND features_used IS NOT NULL
        ''', (start_date.isoformat(),))
        feature_data = cursor.fetchall()
        
        feature_usage = Counter()
        for row in feature_data:
            try:
                features = json.loads(row[0])
                feature_usage.update(features)
            except:
                continue
        
        return {
            'total_sessions': session_data[0] or 0,
            'avg_reviews_per_session': session_data[1] or 0.0,
            'avg_session_minutes': session_data[2] or 0.0,
            'feature_usage': dict(feature_usage.most_common(10))
        }
    
    def get_quality_insights(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed quality insights and recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        start_date = datetime.now() - timedelta(days=days)
        
        # Quality distribution
        cursor.execute('''
            SELECT ai_quality_score FROM reviews_analytics 
            WHERE created_at >= ? AND ai_quality_score > 0
        ''', (start_date.isoformat(),))
        quality_scores = [row[0] for row in cursor.fetchall()]
        
        # Language-specific quality
        cursor.execute('''
            SELECT language, AVG(ai_quality_score), COUNT(*) 
            FROM reviews_analytics 
            WHERE created_at >= ? AND ai_quality_score > 0
            GROUP BY language
        ''', (start_date.isoformat(),))
        language_quality = {
            row[0]: {'avg_quality': row[1], 'count': row[2]}
            for row in cursor.fetchall()
        }
        
        # Method comparison
        cursor.execute('''
            SELECT generation_method, AVG(ai_quality_score), COUNT(*) 
            FROM reviews_analytics 
            WHERE created_at >= ? AND ai_quality_score > 0
            GROUP BY generation_method
        ''', (start_date.isoformat(),))
        method_quality = {
            row[0]: {'avg_quality': row[1], 'count': row[2]}
            for row in cursor.fetchall()
        }
        
        conn.close()
        
        # Statistical analysis
        insights = {
            'quality_statistics': {
                'mean': statistics.mean(quality_scores) if quality_scores else 0.0,
                'median': statistics.median(quality_scores) if quality_scores else 0.0,
                'std_dev': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0.0,
                'min': min(quality_scores) if quality_scores else 0.0,
                'max': max(quality_scores) if quality_scores else 0.0
            },
            'quality_distribution': {
                'excellent': sum(1 for score in quality_scores if score >= 0.9),
                'good': sum(1 for score in quality_scores if 0.8 <= score < 0.9),
                'average': sum(1 for score in quality_scores if 0.6 <= score < 0.8),
                'poor': sum(1 for score in quality_scores if score < 0.6)
            },
            'language_performance': language_quality,
            'method_performance': method_quality,
            'recommendations': self._generate_quality_recommendations(
                quality_scores, language_quality, method_quality
            )
        }
        
        return insights
    
    def _generate_quality_recommendations(self, quality_scores: List[float], 
                                        language_quality: Dict, 
                                        method_quality: Dict) -> List[str]:
        """Generate actionable recommendations based on quality analysis"""
        recommendations = []
        
        if not quality_scores:
            return ["No quality data available for analysis"]
        
        avg_quality = statistics.mean(quality_scores)
        
        # Overall quality recommendations
        if avg_quality < 0.7:
            recommendations.append("Overall quality is below target. Consider increasing AI quality thresholds.")
        
        # Language-specific recommendations
        worst_language = min(language_quality.items(), key=lambda x: x[1]['avg_quality'])
        best_language = max(language_quality.items(), key=lambda x: x[1]['avg_quality'])
        
        if worst_language[1]['avg_quality'] < 0.6:
            recommendations.append(f"Quality for {worst_language[0]} language is low. Review language-specific templates.")
        
        if len(language_quality) > 1 and (best_language[1]['avg_quality'] - worst_language[1]['avg_quality']) > 0.3:
            recommendations.append("Significant quality gap between languages. Consider standardizing approaches.")
        
        # Method-specific recommendations
        if 'ai_enhanced' in method_quality and 'template_based' in method_quality:
            ai_quality = method_quality['ai_enhanced']['avg_quality']
            template_quality = method_quality['template_based']['avg_quality']
            
            if ai_quality > template_quality + 0.1:
                recommendations.append("AI-enhanced reviews show higher quality. Consider increasing AI usage.")
            elif template_quality > ai_quality + 0.1:
                recommendations.append("Template-based reviews outperforming AI. Review AI prompts and settings.")
        
        # Distribution recommendations
        poor_percentage = sum(1 for score in quality_scores if score < 0.6) / len(quality_scores) * 100
        if poor_percentage > 20:
            recommendations.append(f"{poor_percentage:.1f}% of reviews are poor quality. Implement stricter filtering.")
        
        return recommendations
    
    def get_platform_performance(self, days: int = 30) -> Dict[str, Any]:
        """Get platform-specific performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                platform,
                COUNT(*) as total_reviews,
                AVG(ai_quality_score) as avg_quality,
                AVG(generation_time_ms) as avg_generation_time,
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as error_count
            FROM reviews_analytics 
            WHERE created_at >= ?
            GROUP BY platform
        ''', (start_date.isoformat(),))
        
        platform_data = {}
        for row in cursor.fetchall():
            platform_data[row[0]] = {
                'total_reviews': row[1],
                'avg_quality': row[2] or 0.0,
                'avg_generation_time_ms': row[3] or 0.0,
                'error_count': row[4],
                'error_rate': (row[4] / row[1] * 100) if row[1] > 0 else 0.0
            }
        
        conn.close()
        return platform_data
    
    def export_analytics_data(self, days: int = 30, format: str = 'json') -> str:
        """Export analytics data for external analysis"""
        metrics = self.get_dashboard_metrics(days)
        quality_insights = self.get_quality_insights(days)
        platform_performance = self.get_platform_performance(days)
        
        export_data = {
            'export_metadata': {
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'format': format
            },
            'dashboard_metrics': asdict(metrics),
            'quality_insights': quality_insights,
            'platform_performance': platform_performance
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2, default=str)
        else:
            # Could add CSV, Excel export here
            return json.dumps(export_data, default=str)

def create_sample_analytics_data():
    """Create sample analytics data for testing"""
    dashboard = AnalyticsDashboard()
    
    # Sample review generations
    sample_reviews = [
        {
            'generation_method': 'ai_enhanced',
            'ai_enabled': True,
            'ai_quality_score': 0.85,
            'language': 'en',
            'rating': 5,
            'content': 'This is a great product with excellent quality and fast delivery.'
        },
        {
            'generation_method': 'template_based',
            'ai_enabled': False,
            'ai_quality_score': 0.72,
            'language': 'de',
            'rating': 4,
            'content': 'Gute Qualität, bin zufrieden mit dem Kauf.'
        },
        {
            'generation_method': 'ai_enhanced',
            'ai_enabled': True,
            'ai_quality_score': 0.91,
            'language': 'es',
            'rating': 5,
            'content': 'Excelente producto, superó mis expectativas completamente.'
        }
    ]
    
    for i, review in enumerate(sample_reviews):
        dashboard.log_review_generation(
            review_data=review,
            generation_metadata={
                'product_id': f'sample_product_{i}',
                'product_title': f'Sample Product {i}',
                'platform': 'shopify',
                'session_id': 'sample_session',
                'generation_time_ms': 1500 + i * 200,
                'authenticity_score': 0.8 + i * 0.05,
                'readability_score': 0.75 + i * 0.1,
                'uniqueness_score': 0.85 - i * 0.05,
                'commercial_value_score': 0.77 + i * 0.08
            }
        )
    
    return "Sample analytics data created successfully"

# Integration with existing Flask app
def add_analytics_endpoints(app):
    """Add analytics endpoints to Flask app"""
    
    @app.route('/api/analytics/dashboard')
    def analytics_dashboard():
        """Get dashboard metrics"""
        days = int(request.args.get('days', 30))
        dashboard = AnalyticsDashboard()
        metrics = dashboard.get_dashboard_metrics(days)
        return jsonify(asdict(metrics))
    
    @app.route('/api/analytics/quality-insights')
    def quality_insights():
        """Get quality insights"""
        days = int(request.args.get('days', 30))
        dashboard = AnalyticsDashboard()
        insights = dashboard.get_quality_insights(days)
        return jsonify(insights)
    
    @app.route('/api/analytics/platform-performance')
    def platform_performance():
        """Get platform performance metrics"""
        days = int(request.args.get('days', 30))
        dashboard = AnalyticsDashboard()
        performance = dashboard.get_platform_performance(days)
        return jsonify(performance)
    
    @app.route('/api/analytics/export')
    def export_analytics():
        """Export analytics data"""
        days = int(request.args.get('days', 30))
        format_type = request.args.get('format', 'json')
        dashboard = AnalyticsDashboard()
        
        export_data = dashboard.export_analytics_data(days, format_type)
        
        if format_type == 'json':
            return jsonify(json.loads(export_data))
        else:
            return export_data, 200, {'Content-Type': 'text/plain'}
    
    return app