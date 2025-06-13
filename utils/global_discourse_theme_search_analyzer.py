"""
🌍 GLOBAL DISCOURSE THEME SEARCH ANALYZER - Enhanced Search Logic
Advanced search logic for theme-based country analysis with debug features
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict, Counter
import logging
import re

# Local imports
from .global_discourse_models import GlobalAnalysisConstants, CountryData
from .global_discourse_data_loader import CountryDataLoader
from .global_discourse_theme_search_models import (
    ThemeCategory, SentimentCategory, EmotionCategory,
    THEME_KEYWORDS, EMOTION_CATEGORIES, MAX_SAMPLE_COMMENTS,
    EnhancedEmotionStatistics, EnhancedCountryThemeResult, EnhancedThemeSearchResult
)

# =============================================================================
# ENHANCED THEME SEARCH ANALYZER
# =============================================================================

class EnhancedThemeSearchAnalyzer:
    """Advanced analysis for specific themes across countries"""
    
    def __init__(self, country_data: Dict[str, CountryData], data_loader: CountryDataLoader):
        self.country_data = country_data
        self.data_loader = data_loader
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
    
    def search_theme_across_countries(
        self,
        theme_category: ThemeCategory,
        custom_keywords: Optional[List[str]] = None,
        search_in_smart_labels: bool = True,
        search_in_comments: bool = True,
        max_samples_per_country: int = MAX_SAMPLE_COMMENTS
    ) -> EnhancedThemeSearchResult:
        """Enhanced theme search across all countries with debug info"""
        
        # Determine keywords
        if custom_keywords:
            keywords = [kw.strip().lower() for kw in custom_keywords if kw.strip()]
        else:
            keywords = THEME_KEYWORDS.get(theme_category, [])
        
        if not keywords:
            return EnhancedThemeSearchResult(
                theme_category=theme_category,
                keywords_used=[],
                countries_found=[],
                total_matching_comments=0
            )
        
        self.logger.info(f"Enhanced search for {theme_category}: {keywords}")
        
        result = EnhancedThemeSearchResult(
            theme_category=theme_category,
            keywords_used=keywords,
            countries_found=[],
            total_matching_comments=0
        )
        
        # DEBUG: Track what happens in each country
        debug_info = {}
        
        # Search in each country
        for country, country_data in self.country_data.items():
            debug_info[country] = {
                'files_processed': 0,
                'total_rows': 0,
                'matching_rows': 0,
                'search_errors': []
            }
            
            country_result = self._enhanced_search_in_country_with_debug(
                country,
                country_data,
                theme_category,
                keywords,
                search_in_smart_labels,
                search_in_comments,
                max_samples_per_country,
                debug_info[country]
            )
            
            if country_result.matching_comments_count > 0:
                result.country_results[country] = country_result
                result.countries_found.append(country)
                result.total_matching_comments += country_result.matching_comments_count
        
        # DEBUG INFO: Log what was found
        self.logger.info(f"Search results: {len(result.countries_found)} countries found")
        for country, info in debug_info.items():
            self.logger.info(f"{country}: {info['files_processed']} files, {info['total_rows']} rows, {info['matching_rows']} matches")
        
        # Store debug info for UI
        result.debug_info = debug_info
        
        # Enhanced global statistics
        self._calculate_enhanced_global_statistics(result)
        
        # Generate insights
        self._generate_enhanced_insights(result)
        
        self.logger.info(f"Enhanced search completed: {result.total_matching_comments} comments across {len(result.countries_found)} countries")
        
        return result
    
    def _enhanced_search_in_country_with_debug(
        self,
        country: str,
        country_data: CountryData,
        theme_category: ThemeCategory,
        keywords: List[str],
        search_in_smart_labels: bool,
        search_in_comments: bool,
        max_samples: int,
        debug_info: Dict
    ) -> EnhancedCountryThemeResult:
        """Enhanced search in one country with debug tracking"""
        
        country_result = EnhancedCountryThemeResult(
            country=country,
            theme_category=theme_category,
            keywords_used=keywords,
            matching_comments_count=0
        )
        
        matching_rows = []
        
        # Load all CSV data for this country
        for analysis_file in country_data.analysis_files:
            debug_info['files_processed'] += 1
            
            try:
                df = self.data_loader.load_csv_data(analysis_file.file_path)
                if df is None or df.empty:
                    debug_info['search_errors'].append(f"Empty/None DataFrame: {analysis_file.filename}")
                    continue
                
                debug_info['total_rows'] += len(df)
                
                # DEBUG: Check available columns
                available_columns = df.columns.tolist()
                self.logger.info(f"Available columns in {country} - {analysis_file.filename}: {available_columns}")
                
                # Enhanced search with better error handling
                matching_mask = self._find_matching_rows_enhanced_with_debug(
                    df, keywords, search_in_smart_labels, search_in_comments, debug_info
                )
                matching_df = df[matching_mask]
                
                debug_info['matching_rows'] += len(matching_df)
                
                if not matching_df.empty:
                    matching_rows.append(matching_df)
                    self.logger.info(f"Found {len(matching_df)} matches in {country} - {analysis_file.filename}")
                else:
                    self.logger.info(f"No matches in {country} - {analysis_file.filename}")
                    
            except Exception as e:
                error_msg = f"Error in {analysis_file.filename}: {str(e)}"
                debug_info['search_errors'].append(error_msg)
                self.logger.warning(error_msg)
                continue
        
        if not matching_rows:
            self.logger.warning(f"No matching rows found for {country}")
            return country_result
        
        # Combine all data
        combined_df = pd.concat(matching_rows, ignore_index=True)
        country_result.matching_comments_count = len(combined_df)
        
        self.logger.info(f"Total matches for {country}: {country_result.matching_comments_count}")
        
        # Enhanced sentiment analysis
        self._analyze_enhanced_sentiment(combined_df, country_result)
        
        # Enhanced emotion analysis
        self._analyze_enhanced_emotions(combined_df, country_result)
        
        # Smart labels analysis
        self._analyze_smart_labels(combined_df, country_result)
        
        # Sample comments with more details
        self._extract_enhanced_sample_comments(combined_df, country_result, max_samples)
        
        # Additional metrics
        self._calculate_additional_metrics(combined_df, country_result)
        
        return country_result
    
    def _find_matching_rows_enhanced_with_debug(
        self,
        df: pd.DataFrame,
        keywords: List[str],
        search_in_smart_labels: bool,
        search_in_comments: bool,
        debug_info: Dict
    ) -> pd.Series:
        """Enhanced row search with debug info and more robust search"""
        
        mask = pd.Series([False] * len(df), index=df.index)
        keyword_matches = {keyword: 0 for keyword in keywords}
        
        # Enhanced search in Smart Labels
        if search_in_smart_labels and GlobalAnalysisConstants.SMART_LABELS_COLUMN in df.columns:
            smart_labels_col = df[GlobalAnalysisConstants.SMART_LABELS_COLUMN].fillna('')
            
            for keyword in keywords:
                # Both exact and partial matches
                exact_match = smart_labels_col.str.contains(
                    f'\\b{re.escape(keyword)}\\b', case=False, na=False, regex=True
                )
                partial_match = smart_labels_col.str.contains(
                    re.escape(keyword), case=False, na=False, regex=True
                )
                
                keyword_mask = exact_match | partial_match
                keyword_matches[keyword] += keyword_mask.sum()
                mask |= keyword_mask
        
        # Enhanced search in comments
        if search_in_comments and GlobalAnalysisConstants.TEXT_COLUMN in df.columns:
            text_col = df[GlobalAnalysisConstants.TEXT_COLUMN].fillna('')
            
            for keyword in keywords:
                # Both exact and partial matches
                exact_match = text_col.str.contains(
                    f'\\b{re.escape(keyword)}\\b', case=False, na=False, regex=True
                )
                partial_match = text_col.str.contains(
                    re.escape(keyword), case=False, na=False, regex=True
                )
                
                keyword_mask = exact_match | partial_match
                keyword_matches[keyword] += keyword_mask.sum()
                mask |= keyword_mask
        
        # DEBUG: Store keyword matches
        debug_info['keyword_matches'] = keyword_matches
        
        return mask
    
    def _analyze_enhanced_sentiment(self, df: pd.DataFrame, result: EnhancedCountryThemeResult) -> None:
        """Enhanced sentiment analysis"""
        if GlobalAnalysisConstants.SENTIMENT_COLUMN in df.columns:
            sentiment_counts = df[GlobalAnalysisConstants.SENTIMENT_COLUMN].value_counts()
            result.sentiment_distribution = sentiment_counts.to_dict()
            
            total = len(df)
            result.sentiment_percentages = {
                sentiment: (count / total) * 100
                for sentiment, count in sentiment_counts.items()
            }
    
    def _analyze_enhanced_emotions(self, df: pd.DataFrame, result: EnhancedCountryThemeResult) -> None:
        """Enhanced emotion analysis"""
        if GlobalAnalysisConstants.EMOTION_COLUMN in df.columns:
            emotion_counts = df[GlobalAnalysisConstants.EMOTION_COLUMN].value_counts()
            result.emotion_distribution = emotion_counts.to_dict()
            
            total = len(df)
            result.emotion_percentages = {
                emotion: (count / total) * 100
                for emotion, count in emotion_counts.items()
            }
            
            # Calculate emotion statistics
            result.emotion_statistics = self._calculate_emotion_statistics_enhanced(df)
    
    def _calculate_emotion_statistics_enhanced(self, df: pd.DataFrame) -> EnhancedEmotionStatistics:
        """Calculates enhanced emotion statistics"""
        if df.empty:
            return EnhancedEmotionStatistics(
                total_comments=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                emotion_distribution={},
                dominant_emotion="unknown"
            )
        
        total = len(df)
        emotion_distribution = (df[GlobalAnalysisConstants.EMOTION_COLUMN].value_counts(normalize=True) * 100).to_dict()
        
        # Categorize emotions
        positive_count = sum(
            len(df[df[GlobalAnalysisConstants.EMOTION_COLUMN].isin(emotions)])
            for emotions in [EMOTION_CATEGORIES[EmotionCategory.POSITIVE]]
        )
        
        negative_count = sum(
            len(df[df[GlobalAnalysisConstants.EMOTION_COLUMN].isin(emotions)])
            for emotions in [EMOTION_CATEGORIES[EmotionCategory.NEGATIVE]]
        )
        
        neutral_count = sum(
            len(df[df[GlobalAnalysisConstants.EMOTION_COLUMN].isin(emotions)])
            for emotions in [EMOTION_CATEGORIES[EmotionCategory.NEUTRAL]]
        )
        
        dominant_emotion = df[GlobalAnalysisConstants.EMOTION_COLUMN].value_counts().index[0] if not df.empty else "unknown"
        
        return EnhancedEmotionStatistics(
            total_comments=total,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            emotion_distribution=emotion_distribution,
            dominant_emotion=dominant_emotion
        )
    
    def _analyze_smart_labels(self, df: pd.DataFrame, result: EnhancedCountryThemeResult) -> None:
        """Analyzes Smart Labels"""
        if GlobalAnalysisConstants.SMART_LABELS_COLUMN in df.columns:
            smart_labels = df[GlobalAnalysisConstants.SMART_LABELS_COLUMN].dropna()
            result.related_smart_labels = list(smart_labels.unique())
            
            # Top Smart Labels
            label_counts = smart_labels.value_counts()
            result.top_smart_labels = list(label_counts.head(10).items())
            result.unique_smart_labels_count = len(result.related_smart_labels)
    
    def _extract_enhanced_sample_comments(
        self,
        df: pd.DataFrame,
        result: EnhancedCountryThemeResult,
        max_samples: int
    ) -> None:
        """Extracts enhanced sample comments in FULL LENGTH"""
        if df.empty:
            return
        
        sample_df = df.sample(n=min(max_samples, len(df)))
        
        for _, row in sample_df.iterrows():
            full_text = str(row.get(GlobalAnalysisConstants.TEXT_COLUMN, ''))
            
            sample = {
                'text': full_text,  # *** FULL LENGTH - NO TRUNCATION! ***
                'text_preview': full_text[:150] + "..." if len(full_text) > 150 else full_text,  # Only for previews
                'sentiment': row.get(GlobalAnalysisConstants.SENTIMENT_COLUMN, 'unknown'),
                'emotion': row.get(GlobalAnalysisConstants.EMOTION_COLUMN, 'unknown'),
                'smart_label': row.get(GlobalAnalysisConstants.SMART_LABELS_COLUMN, 'No label'),
                'length': len(full_text),
                'sentiment_emoji': self._get_sentiment_emoji(row.get(GlobalAnalysisConstants.SENTIMENT_COLUMN, '')),
                'emotion_emoji': self._get_emotion_emoji(row.get(GlobalAnalysisConstants.EMOTION_COLUMN, ''))
            }
            result.sample_comments.append(sample)
    
    def _calculate_additional_metrics(self, df: pd.DataFrame, result: EnhancedCountryThemeResult) -> None:
        """Calculates additional metrics"""
        if GlobalAnalysisConstants.TEXT_COLUMN in df.columns:
            text_lengths = df[GlobalAnalysisConstants.TEXT_COLUMN].fillna('').str.len()
            result.average_comment_length = text_lengths.mean()
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Returns emoji for sentiment"""
        sentiment_emojis = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        }
        return sentiment_emojis.get(sentiment.lower(), '❓')
    
    def _get_emotion_emoji(self, emotion: str) -> str:
        """Returns emoji for emotion"""
        emotion_emojis = {
            'joy': '😄',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'disgust': '🤢',
            'surprise': '😲',
            'love': '❤️',
            'neutral': '😐'
        }
        return emotion_emojis.get(emotion.lower(), '❓')
    
    def _calculate_enhanced_global_statistics(self, result: EnhancedThemeSearchResult) -> None:
        """Calculates enhanced global statistics"""
        if not result.country_results:
            return
        
        # Global sentiment/emotion distribution
        global_sentiment_counts = defaultdict(int)
        global_emotion_counts = defaultdict(int)
        
        for country_result in result.country_results.values():
            for sentiment, count in country_result.sentiment_distribution.items():
                global_sentiment_counts[sentiment] += count
            
            for emotion, count in country_result.emotion_distribution.items():
                global_emotion_counts[emotion] += count
        
        # Convert to percentages
        total = result.total_matching_comments
        if total > 0:
            result.global_sentiment_distribution = {
                sentiment: (count / total) * 100
                for sentiment, count in global_sentiment_counts.items()
            }
            
            result.global_emotion_distribution = {
                emotion: (count / total) * 100
                for emotion, count in global_emotion_counts.items()
            }
        
        # Calculate rankings
        if result.country_results:
            # Country with most discussions
            result.most_discussed_country = max(
                result.country_results.keys(),
                key=lambda country: result.country_results[country].matching_comments_count
            )
            
            # Countries with most positive/negative sentiment
            countries_with_sentiment = {
                country: res.emotion_statistics.sentiment_score
                for country, res in result.country_results.items()
                if res.emotion_statistics
            }
            
            if countries_with_sentiment:
                result.most_positive_country = max(countries_with_sentiment.items(), key=lambda x: x[1])[0]
                result.most_negative_country = min(countries_with_sentiment.items(), key=lambda x: x[1])[0]
    
    def _generate_enhanced_insights(self, result: EnhancedThemeSearchResult) -> None:
        """Generates enhanced insights"""
        insights = []
        comparisons = []
        
        if not result.country_results:
            return
        
        # Discussion insights
        if result.most_discussed_country:
            most_count = result.country_results[result.most_discussed_country].matching_comments_count
            insights.append(f"🏆 {result.most_discussed_country} leads the discussion with {most_count} comments")
        
        # Sentiment insights
        if result.most_positive_country and result.most_negative_country:
            insights.append(f"😊 Most positive sentiment: {result.most_positive_country}")
            insights.append(f"😞 Most negative sentiment: {result.most_negative_country}")
        
        # Engagement insights
        avg_comments = result.average_comments_per_country
        if avg_comments > 0:
            insights.append(f"📊 Average {avg_comments:.1f} comments per country")
        
        # Country comparisons
        sorted_countries = sorted(
            result.country_results.items(),
            key=lambda x: x[1].matching_comments_count,
            reverse=True
        )
        
        if len(sorted_countries) >= 2:
            top_country = sorted_countries[0]
            second_country = sorted_countries[1]
            
            ratio = top_country[1].matching_comments_count / second_country[1].matching_comments_count
            comparisons.append(
                f"{top_country[0]} has {ratio:.1f}x more discussions than {second_country[0]}"
            )
        
        result.key_insights = insights
        result.country_comparisons = comparisons


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'EnhancedThemeSearchAnalyzer'
]