"""
🌍 GLOBAL DISCOURSE ANALYZER - Business Logic & Country Comparison
Analysiert und vergleicht Länder-Daten für Cross-Country Insights
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
import logging

# Local imports
from .global_discourse_models import (
    GlobalAnalysisConstants, AnalysisType, CountryData, ComparisonResult
)

# =============================================================================
# COUNTRY ANALYZER
# =============================================================================

class CountryAnalyzer:
    """Analysiert und vergleicht Länder-Daten"""
    
    def __init__(self):
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
    
    def create_comparison_result(
        self,
        country_data: Dict[str, CountryData],
        analysis_type: AnalysisType = AnalysisType.SENTIMENT_COMPARISON
    ) -> ComparisonResult:
        """Erstellt umfassenden Länder-Vergleich
        
        Args:
            country_data: Dictionary mit Länder-Daten
            analysis_type: Typ der Analyse
            
        Returns:
            ComparisonResult mit allen Vergleichsdaten
        """
        countries = list(country_data.keys())
        total_comments = sum(data.total_comments for data in country_data.values())
        languages = {data.language for data in country_data.values()}
        
        # Datum-Range bestimmen
        all_dates = []
        for data in country_data.values():
            for file in data.analysis_files:
                all_dates.append(file.analysis_date)
        
        date_range = (min(all_dates), max(all_dates)) if all_dates else (datetime.now(), datetime.now())
        
        result = ComparisonResult(
            countries=countries,
            analysis_type=analysis_type,
            country_data=country_data,
            total_comments=total_comments,
            date_range=date_range,
            languages=languages
        )
        
        # Sentiment-Vergleich
        result.sentiment_comparison = self._analyze_sentiment_comparison(country_data)
        
        # Topic-Vergleich
        result.common_topics, result.unique_topics_per_country = self._analyze_topic_overlap(country_data)
        result.topic_similarity_matrix = self._calculate_topic_similarity(country_data)
        
        # Emotion-Vergleich
        result.emotion_comparison = self._analyze_emotion_comparison(country_data)
        
        # Insights generieren
        result.insights = self._generate_insights(result)
        
        return result
    
    def _analyze_sentiment_comparison(self, country_data: Dict[str, CountryData]) -> Dict[str, Dict[str, float]]:
        """Analysiert Sentiment-Unterschiede zwischen Ländern"""
        comparison = {}
        
        for country, data in country_data.items():
            comparison[country] = data.sentiment_percentages.copy()
        
        return comparison
    
    def _analyze_topic_overlap(self, country_data: Dict[str, CountryData]) -> Tuple[List[str], Dict[str, List[str]]]:
        """Analysiert Topic-Überschneidungen zwischen Ländern"""
        all_topics = set()
        country_topics = {}
        
        for country, data in country_data.items():
            topics = set(data.topic_distribution.keys())
            all_topics.update(topics)
            country_topics[country] = topics
        
        # Gemeinsame Topics
        common_topics = set.intersection(*country_topics.values()) if country_topics else set()
        
        # Einzigartige Topics pro Land
        unique_topics = {}
        for country, topics in country_topics.items():
            other_countries_topics = set.union(*[t for c, t in country_topics.items() if c != country])
            unique_topics[country] = list(topics - other_countries_topics)
        
        return list(common_topics), unique_topics
    
    def _calculate_topic_similarity(self, country_data: Dict[str, CountryData]) -> Dict[str, Dict[str, float]]:
        """Berechnet Topic-Ähnlichkeit zwischen Ländern"""
        countries = list(country_data.keys())
        similarity_matrix = {country: {} for country in countries}
        
        for i, country1 in enumerate(countries):
            for j, country2 in enumerate(countries):
                if i <= j:
                    similarity = self._calculate_cosine_similarity(
                        country_data[country1].topic_percentages,
                        country_data[country2].topic_percentages
                    )
                    similarity_matrix[country1][country2] = similarity
                    similarity_matrix[country2][country1] = similarity
        
        return similarity_matrix
    
    def _calculate_cosine_similarity(self, dict1: Dict[str, float], dict2: Dict[str, float]) -> float:
        """Berechnet Cosinus-Ähnlichkeit zwischen zwei Verteilungen"""
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        vec1 = [dict1.get(key, 0) for key in all_keys]
        vec2 = [dict2.get(key, 0) for key in all_keys]
        
        # Cosinus-Ähnlichkeit
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _analyze_emotion_comparison(self, country_data: Dict[str, CountryData]) -> Dict[str, Dict[str, float]]:
        """Analysiert Emotion-Unterschiede zwischen Ländern"""
        comparison = {}
        
        for country, data in country_data.items():
            comparison[country] = data.emotion_percentages.copy()
        
        return comparison
    
    def _generate_insights(self, result: ComparisonResult) -> List[str]:
        """Generates automatic insights"""
        insights = []
        
        # Sentiment Insights
        if result.sentiment_comparison:
            positive_countries = []
            negative_countries = []
            
            for country, sentiments in result.sentiment_comparison.items():
                pos_pct = sentiments.get('positive', 0)
                neg_pct = sentiments.get('negative', 0)
                
                if pos_pct > neg_pct + 10:
                    # ❌ VORHER: f"{country} ({pos_pct:.1f}% positiv)"
                    positive_countries.append(f"{country} ({pos_pct:.1f}% positive)")  # ✅ ENGLISCH
                elif neg_pct > pos_pct + 10:
                    # ❌ VORHER: f"{country} ({neg_pct:.1f}% negativ)"
                    negative_countries.append(f"{country} ({neg_pct:.1f}% negative)")  # ✅ ENGLISCH
            
            if positive_countries:
                # ❌ VORHER: f"🟢 Überwiegend positive Diskussionen: {', '.join(positive_countries)}"
                insights.append(f"🟢 Predominantly positive discussions: {', '.join(positive_countries)}")  # ✅ ENGLISCH
            if negative_countries:
                # ❌ VORHER: f"🔴 Überwiegend negative Diskussionen: {', '.join(negative_countries)}"
                insights.append(f"🔴 Predominantly negative discussions: {', '.join(negative_countries)}")  # ✅ ENGLISCH
        
        # Topic Insights
        if len(result.common_topics) > 0:
            # ❌ VORHER: f"🤝 {len(result.common_topics)} gemeinsame Themen in allen Ländern"
            insights.append(f"🤝 {len(result.common_topics)} common topics across all countries")  # ✅ ENGLISCH
        
        # Further insights...
        total_insights = len([country for country in result.countries])
        # ❌ VORHER: f"📊 Analyse umfasst {total_insights} Länder mit {result.total_comments:,} Kommentaren"
        insights.append(f"📊 Analysis covers {total_insights} countries with {result.total_comments:,} comments")  # ✅ ENGLISCH
        
        return insights   


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'CountryAnalyzer'
]