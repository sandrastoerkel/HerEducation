"""
🌍 GLOBAL DISCOURSE ANALYSIS - Enterprise Cross-Country Analysis System
Modernized country comparison analysis with Enhanced Smart Labels Integration & Automatic Country Detection

*** ENHANCED VERSION with interactive world map ***

This module enables comprehensive analysis and comparison of 
discourses between different countries based on previously saved 
comment analyses with Smart Topic Labels.

*** ENHANCED with improved theme search + world map ***
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import logging
import traceback
import json

# *** UTILS IMPORTS ***
from utils.global_discourse_models import (
    GlobalAnalysisConstants, AnalysisType, CountryData, AnalysisFile
)
from utils.global_discourse_data_loader import CountryDataLoader, CountryDataAggregator
from utils.global_discourse_analyzer import CountryAnalyzer
from utils.global_discourse_visualizer import CountryVisualizer
from utils.global_discourse_theme_search_visualizer import render_enhanced_theme_search_interface
from utils.global_discourse_ui import (
    render_file_selection_interface, setup_page
)
from utils.global_discourse_country_detector import (
    render_country_detection_debug
)
# *** NEW WORLD MAP INTEGRATION ***
from utils.global_discourse_world_map import (
    GlobalDiscourseWorldMap, integrate_world_map_in_sentiment_tab
)

# =============================================================================
# MAIN MANAGER CLASS
# =============================================================================

class GlobalDiscourseAnalysisManager:
    """Central manager for global discourse analysis with Enhanced Theme Search & World Map"""
    
    def __init__(self):
        """Initializes the manager with all components"""
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
        
        # Initialize components
        self.data_loader = CountryDataLoader()  # *** WITH COUNTRY DETECTOR ***
        self.data_aggregator = CountryDataAggregator()
        self.analyzer = CountryAnalyzer()
        self.visualizer = CountryVisualizer()
        # *** NEW WORLD MAP COMPONENT ***
        self.world_map = GlobalDiscourseWorldMap()
        
        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def get_available_analyses(self) -> List[AnalysisFile]:
        """Returns all available Country Analysis files"""
        return self.data_loader.get_available_analysis_files()
    
    def load_country_data(self, selected_files: Optional[List[str]] = None) -> Dict[str, CountryData]:
        """Loads and aggregates Country data"""
        analysis_files = self.get_available_analyses()
        return self.data_aggregator.aggregate_country_data(analysis_files, selected_files)
    
    def create_comparison(
        self,
        country_data: Dict[str, CountryData],
        analysis_type: AnalysisType = AnalysisType.SENTIMENT_COMPARISON
    ) -> 'ComparisonResult':
        """Creates comprehensive country comparison"""
        return self.analyzer.create_comparison_result(country_data, analysis_type)
    
    def render_country_detection_interface(self) -> None:
        """Renders enhanced Country Detection Interface in Sidebar"""
        st.sidebar.subheader("🌍 Country Detection")
        
        st.sidebar.info("""
        **🚀 Automatic Country Detection**
        
        The system automatically recognizes 50+ countries from filenames based on:
        • Keywords (e.g. "germany", "usa")
        • City names
        • Media outlets
        • Alternative names
        """)
        
        if st.sidebar.button("🔧 Country Detection Debug"):
            render_country_detection_debug(self.data_loader.country_detector)
        
        if st.sidebar.button("🗑️ Clear Cache"):
            self.data_loader.country_detector.clear_cache()
            st.sidebar.success("Country Cache cleared")
            st.rerun()
        
        # Show cache statistics
        stats = self.data_loader.country_detector.get_country_statistics()
        if stats:
            st.sidebar.write("**Cached Countries:**")
            for country, count in stats.items():
                st.sidebar.write(f"• {country}: {count}")
        else:
            st.sidebar.write("*No countries in cache yet*")
        
        # Additional info
        st.sidebar.markdown("---")
        st.sidebar.write("**🎯 New Features v2.1:**")
        st.sidebar.write("• 🗺️ Interactive World Map")
        st.sidebar.write("• 🎭 Predefined Theme Sets")
        st.sidebar.write("• 💬 Complete Sample Comments")
        st.sidebar.write("• 🏆 Country Rankings")
        st.sidebar.write("• 📊 Extended Sentiment Scores")
    
    def render_analysis_tabs(self, country_data: Dict[str, CountryData]) -> None:
        """Renders the 5 main analysis tabs including Enhanced Theme Search & World Map"""
        if not country_data:
            st.warning("No country data available for analysis")
            return
        
        # *** ENHANCED TAB TITLES WITH WORLD MAP HINT ***
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🗺️ Sentiment & World Map",  # *** UPDATED ***
            "🏷️ Topic Comparison", 
            "😊 Emotion Analysis",
            "🔍 Advanced Insights",
            "🎯 Enhanced Theme Search"
        ])
        
        # *** TAB 1: SENTIMENT ANALYSIS WITH WORLD MAP ***
        with tab1:
            st.subheader("🗺️ Cross-Country Sentiment Analysis with interactive world map")
            
            # *** WORLD MAP INTEGRATION WITH SUB-TABS ***
            map_tab, chart_tab = st.tabs(["🗺️ Interactive World Map", "📊 Sentiment Comparison Charts"])
            
            with map_tab:
                if len(country_data) == 0:
                    st.warning("No country data available for world map")
                else:
                    # Info box
                    st.info(f"""
                    **🌍 Interactive World Map of Global Discourses**
                    
                    • **{len(country_data)} Countries** are being analyzed
                    • **Sentiment Colors**: 🟢 Positive | 🟡 Neutral | 🔴 Negative
                    • **Hover Details**: Top Topics and Emotions per Country
                    • **Click Navigation** (planned) for detailed country analysis
                    """)
                    
                    # Create world map
                    self.world_map.create_interactive_world_map(country_data)
            
            with chart_tab:
                # Existing sentiment charts
                comparison = self.analyzer.create_comparison_result(
                    country_data, AnalysisType.SENTIMENT_COMPARISON
                )
                
                self.visualizer.render_sentiment_comparison_chart(comparison.sentiment_comparison)
                
                # *** EXTENDED SENTIMENT STATISTICS ***
                st.subheader("📈 Detailed Sentiment Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sentiment score comparison
                    st.write("**🏆 Sentiment Score Ranking:**")
                    sentiment_scores = []
                    
                    for country, data in country_data.items():
                        total = data.total_comments
                        pos_pct = data.sentiment_percentages.get('positive', 0)
                        neg_pct = data.sentiment_percentages.get('negative', 0)
                        neu_pct = data.sentiment_percentages.get('neutral', 0)
                        score = pos_pct - neg_pct  # Sentiment Score
                        
                        sentiment_scores.append({
                            'Country': country,
                            'Score': f"{score:+.1f}",
                            'Positive': f"{pos_pct:.1f}%",
                            'Neutral': f"{neu_pct:.1f}%", 
                            'Negative': f"{neg_pct:.1f}%",
                            'Comments': total
                        })
                    
                    # Sort by score
                    sentiment_scores.sort(key=lambda x: float(x['Score']), reverse=True)
                    sentiment_df = pd.DataFrame(sentiment_scores)
                    st.dataframe(sentiment_df, use_container_width=True)
                
                with col2:
                    # Country comparison metrics
                    st.write("**🌍 Country Comparison Metrics:**")
                    
                    total_countries = len(country_data)
                    total_comments = sum(data.total_comments for data in country_data.values())
                    avg_comments = total_comments / total_countries if total_countries > 0 else 0
                    
                    # Top discussion country
                    most_comments_country = max(country_data.items(), key=lambda x: x[1].total_comments)
                    
                    metrics_data = [
                        {"Metric": "Countries analyzed", "Value": f"{total_countries}"},
                        {"Metric": "Total comments", "Value": f"{total_comments:,}"},
                        {"Metric": "⌀ Comments/Country", "Value": f"{avg_comments:.0f}"},
                        {"Metric": "Most active country", "Value": f"{most_comments_country[0]} ({most_comments_country[1].total_comments:,})"},
                    ]
                    
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                
                # Extended sentiment insights
                st.subheader("💡 Sentiment Insights")
                
                # Automatic insights
                insights = []
                
                # Identify positive/negative countries
                positive_countries = []
                negative_countries = []
                
                for country, data in country_data.items():
                    pos_pct = data.sentiment_percentages.get('positive', 0)
                    neg_pct = data.sentiment_percentages.get('negative', 0)
                    
                    if pos_pct > neg_pct + 15:  # Clearly positive
                        positive_countries.append(f"{country} ({pos_pct:.1f}% positive)")
                    elif neg_pct > pos_pct + 15:  # Clearly negative
                        negative_countries.append(f"{country} ({neg_pct:.1f}% negative)")
                
                if positive_countries:
                    insights.append(f"🟢 **Predominantly positive discussions:** {', '.join(positive_countries)}")
                
                if negative_countries:
                    insights.append(f"🔴 **Predominantly negative discussions:** {', '.join(negative_countries)}")
                
                # Language-based insights
                language_groups = {}
                for country, data in country_data.items():
                    lang = data.language
                    if lang not in language_groups:
                        language_groups[lang] = []
                    language_groups[lang].append(country)
                
                if len(language_groups) > 1:
                    lang_info = []
                    for lang, countries in language_groups.items():
                        lang_info.append(f"{lang.upper()}: {', '.join(countries)}")
                    insights.append(f"🗣️ **Language Grouping:** {' | '.join(lang_info)}")
                
                # Show insights
                for insight in insights:
                    st.info(insight)
                
                if not insights:
                    st.info("🤖 Perform analyses with more countries for automatic insights")
        
        # Tab 2: Topic Analysis (COMPLETE)
        with tab2:
            st.subheader("🏷️ Cross-Country Topic Analysis with Smart Labels")
            
            st.info("""
            **🧠 Smart Labels Integration:**
            This analysis uses Smart Labels from your original analyses and provides 
            meaningful and contextual topic categorization compared to raw topic modeling keywords.
            """)
            
            self.visualizer.render_topic_comparison_chart(country_data)
            
            # Topic statistics EXTENDED
            st.subheader("📈 Top Topics per Country")
            
            # Global topic overview
            all_topics = {}
            for country, data in country_data.items():
                for topic, count in data.topic_distribution.items():
                    if topic not in all_topics:
                        all_topics[topic] = 0
                    all_topics[topic] += count
            
            if all_topics:
                st.subheader("🌍 Global Topic Overview")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**🔥 Top Topics Global:**")
                    global_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:10]
                    global_topic_data = []
                    for i, (topic, count) in enumerate(global_topics, 1):
                        total_global = sum(all_topics.values())
                        percentage = (count / total_global) * 100 if total_global > 0 else 0
                        global_topic_data.append({
                            'Rank': i,
                            'Topic': topic,
                            'Comments': count,
                            'Share': f"{percentage:.1f}%"
                        })
                    
                    global_topics_df = pd.DataFrame(global_topic_data)
                    st.dataframe(global_topics_df, use_container_width=True)
                
                with col2:
                    st.write("**📊 Topic Distribution by Countries:**")
                    if len(country_data) > 1:
                        # Unique topics per country
                        unique_topics_data = []
                        for country, data in country_data.items():
                            unique_count = len(data.topic_distribution)
                            total_comments = data.total_comments
                            unique_topics_data.append({
                                'Country': country,
                                'Unique Topics': unique_count,
                                'Comments': total_comments,
                                'Topics/1000': f"{(unique_count/total_comments*1000):.1f}" if total_comments > 0 else "0"
                            })
                        
                        unique_df = pd.DataFrame(unique_topics_data)
                        st.dataframe(unique_df, use_container_width=True)
            
            # Detailed country topics
            for country, data in country_data.items():
                with st.expander(f"🌍 {country} - Top Topics (Smart Labels)", expanded=False):
                    if data.top_topics:
                        topic_stats = []
                        for i, (topic, count) in enumerate(data.top_topics[:15], 1):
                            percentage = data.topic_percentages.get(topic, 0)
                            topic_stats.append({
                                'Rank': i,
                                'Smart Label': topic,
                                'Comments': count,
                                'Share': f"{percentage:.1f}%"
                            })
                        
                        topic_df = pd.DataFrame(topic_stats)
                        st.dataframe(topic_df, use_container_width=True)
                        
                        # Additional topic metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Unique Topics", len(data.topic_distribution))
                        
                        with col2:
                            top_topic_pct = data.topic_percentages.get(data.top_topics[0][0], 0) if data.top_topics else 0
                            st.metric("Top Topic Share", f"{top_topic_pct:.1f}%")
                        
                        with col3:
                            # Topic diversity (how evenly distributed are the topics)
                            topic_values = list(data.topic_percentages.values())
                            if topic_values:
                                import numpy as np
                                topic_std = np.std(topic_values)
                                st.metric("Topic Diversity", f"{topic_std:.1f}")
                            else:
                                st.metric("Topic Diversity", "N/A")
                    else:
                        st.warning("No topic data available")
        
        # Tab 3: Emotion Analysis (COMPLETE)
        with tab3:
            st.subheader("😊 Cross-Country Emotion Analysis")
            
            # Global emotion overview
            all_emotions = {}
            for country, data in country_data.items():
                for emotion, count in data.emotion_distribution.items():
                    if emotion not in all_emotions:
                        all_emotions[emotion] = 0
                    all_emotions[emotion] += count
            
            if all_emotions:
                st.subheader("🌍 Global Emotion Overview")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Emotion ranking
                    st.write("**😊 Global Emotion Ranking:**")
                    emotion_ranking = sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)
                    
                    emotion_data = []
                    total_emotions = sum(all_emotions.values())
                    
                    for i, (emotion, count) in enumerate(emotion_ranking, 1):
                        percentage = (count / total_emotions) * 100 if total_emotions > 0 else 0
                        emoji = self._get_emotion_emoji(emotion)
                        emotion_data.append({
                            'Rank': i,
                            'Emotion': f"{emoji} {emotion}",
                            'Comments': count,
                            'Share': f"{percentage:.1f}%"
                        })
                    
                    emotion_df = pd.DataFrame(emotion_data)
                    st.dataframe(emotion_df, use_container_width=True)
                
                with col2:
                    # Emotion categories
                    st.write("**📊 Emotion Categories:**")
                    
                    positive_emotions = ['joy', 'love', 'surprise']
                    negative_emotions = ['anger', 'sadness', 'fear', 'disgust']
                    neutral_emotions = ['neutral', 'none of them']
                    
                    positive_count = sum(all_emotions.get(e, 0) for e in positive_emotions)
                    negative_count = sum(all_emotions.get(e, 0) for e in negative_emotions)
                    neutral_count = sum(all_emotions.get(e, 0) for e in neutral_emotions)
                    
                    category_data = [
                        {"Category": "😊 Positive", "Comments": positive_count, "Share": f"{(positive_count/total_emotions*100):.1f}%" if total_emotions > 0 else "0%"},
                        {"Category": "😞 Negative", "Comments": negative_count, "Share": f"{(negative_count/total_emotions*100):.1f}%" if total_emotions > 0 else "0%"},
                        {"Category": "😐 Neutral", "Comments": neutral_count, "Share": f"{(neutral_count/total_emotions*100):.1f}%" if total_emotions > 0 else "0%"}
                    ]
                    
                    category_df = pd.DataFrame(category_data)
                    st.dataframe(category_df, use_container_width=True, hide_index=True)
            
            # Emotion-per-topic for each country
            st.subheader("📊 Emotions per Topic by Countries")
            
            for country, data in country_data.items():
                st.write(f"### 🌍 {country} - Emotions per Topic")
                self.visualizer.render_emotion_topic_matrix(data, country)
                
                # Additional emotion statistics
                if data.emotion_distribution:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        dominant_emotion = data.dominant_emotion
                        emoji = self._get_emotion_emoji(dominant_emotion)
                        st.metric("Dominant Emotion", f"{emoji} {dominant_emotion}")
                    
                    with col2:
                        emotion_count = len(data.emotion_distribution)
                        st.metric("Different Emotions", emotion_count)
                    
                    with col3:
                        # Emotion intensity (how strong is the dominant emotion)
                        if data.emotion_percentages:
                            max_emotion_pct = max(data.emotion_percentages.values())
                            st.metric("Emotion Intensity", f"{max_emotion_pct:.1f}%")
                
                st.markdown("---")
        
        # Tab 4: Advanced Insights (COMPLETE)
        with tab4:
            st.subheader("🔍 Advanced Cross-Country Insights")
            
            comparison = self.analyzer.create_comparison_result(country_data)
            
            # Overview metrics
            self.visualizer.render_country_overview_metrics(country_data)
            
            # EXTENDED INSIGHTS
            st.subheader("💡 Automatic Cross-Country Insights")
            
            # Show insights
            if comparison.insights:
                for insight in comparison.insights:
                    st.info(insight)
            
            # ADDITIONAL EXTENDED INSIGHTS
            additional_insights = self._generate_additional_insights(country_data)
            for insight in additional_insights:
                st.info(insight)
            
            # Topic similarity
            if len(country_data) > 1:
                st.subheader("🤝 Topic Similarity between Countries")
                
                similarity_data = []
                countries = list(country_data.keys())
                
                for i, country1 in enumerate(countries):
                    for j, country2 in enumerate(countries):
                        if i < j:
                            similarity = comparison.topic_similarity_matrix.get(country1, {}).get(country2, 0)
                            similarity_data.append({
                                'Country 1': country1,
                                'Country 2': country2,
                                'Similarity': f"{similarity:.3f}",
                                'Similarity Level': self._get_similarity_level(similarity)
                            })
                
                if similarity_data:
                    similarity_df = pd.DataFrame(similarity_data)
                    st.dataframe(similarity_df, use_container_width=True)
                    
                    # Similarity insights
                    most_similar = max(similarity_data, key=lambda x: float(x['Similarity']))
                    least_similar = min(similarity_data, key=lambda x: float(x['Similarity']))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.success(f"🤝 **Most Similar Countries:** {most_similar['Country 1']} ↔ {most_similar['Country 2']} ({most_similar['Similarity']})")
                    
                    with col2:
                        st.warning(f"🔄 **Most Different Countries:** {least_similar['Country 1']} ↔ {least_similar['Country 2']} ({least_similar['Similarity']})")
            
            # Cross-Language Analysis (if multiple languages)
            languages = set(data.language for data in country_data.values())
            if len(languages) > 1:
                st.subheader("🗣️ Cross-Language Analysis")
                
                lang_analysis = {}
                for country, data in country_data.items():
                    lang = data.language
                    if lang not in lang_analysis:
                        lang_analysis[lang] = {
                            'countries': [],
                            'total_comments': 0,
                            'avg_sentiment_score': 0,
                            'dominant_topics': {},
                            'dominant_emotions': {}
                        }
                    
                    lang_analysis[lang]['countries'].append(country)
                    lang_analysis[lang]['total_comments'] += data.total_comments
                    
                    # Calculate sentiment score
                    pos_pct = data.sentiment_percentages.get('positive', 0)
                    neg_pct = data.sentiment_percentages.get('negative', 0)
                    sentiment_score = pos_pct - neg_pct
                    lang_analysis[lang]['avg_sentiment_score'] += sentiment_score
                    
                    # Collect top topics
                    if data.top_topics:
                        top_topic = data.top_topics[0][0]
                        if top_topic not in lang_analysis[lang]['dominant_topics']:
                            lang_analysis[lang]['dominant_topics'][top_topic] = 0
                        lang_analysis[lang]['dominant_topics'][top_topic] += 1
                    
                    # Collect emotions
                    if data.emotion_distribution:
                        dominant_emotion = data.dominant_emotion
                        if dominant_emotion not in lang_analysis[lang]['dominant_emotions']:
                            lang_analysis[lang]['dominant_emotions'][dominant_emotion] = 0
                        lang_analysis[lang]['dominant_emotions'][dominant_emotion] += 1
                
                # Calculate averages
                for lang, analysis in lang_analysis.items():
                    country_count = len(analysis['countries'])
                    analysis['avg_sentiment_score'] /= country_count
                
                # Language comparison table
                lang_comparison = []
                for lang, analysis in lang_analysis.items():
                    most_common_topic = max(analysis['dominant_topics'].items(), key=lambda x: x[1])[0] if analysis['dominant_topics'] else "N/A"
                    most_common_emotion = max(analysis['dominant_emotions'].items(), key=lambda x: x[1])[0] if analysis['dominant_emotions'] else "N/A"
                    
                    lang_comparison.append({
                        'Language': lang.upper(),
                        'Countries': ', '.join(analysis['countries']),
                        'Comments': f"{analysis['total_comments']:,}",
                        'Ø Sentiment': f"{analysis['avg_sentiment_score']:+.1f}",
                        'Top Topic': most_common_topic,
                        'Top Emotion': most_common_emotion
                    })
                
                lang_df = pd.DataFrame(lang_comparison)
                st.dataframe(lang_df, use_container_width=True)
        
        # Tab 5: ENHANCED THEME SEARCH TAB (COMPLETELY UNCHANGED)
        with tab5:
            st.markdown("""
            ### 🚀 Enhanced Theme Search - Next Level Analysis
            
            **New Features:**
            • 🎭 **8 predefined theme categories** with curated keyword sets
            • 📊 **Extended sentiment scores** and emotion categorization  
            • 🏆 **Country rankings** and automatic insights
            • 💬 **Sample comments** with emojis and metadata
            • 🎯 **Engagement scores** and average comment lengths
            • ⚖️ **Country comparisons** with statistical ratios
            """)
            
            render_enhanced_theme_search_interface(country_data, self.data_loader)
    
    def _get_emotion_emoji(self, emotion: str) -> str:
        """Returns emoji for emotion"""
        emojis = {
            'joy': '😄',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'disgust': '🤢',
            'surprise': '😲',
            'love': '❤️',
            'neutral': '😐',
            'none of them': '😐'
        }
        return emojis.get(emotion.lower(), '❓')
    
    def _get_similarity_level(self, similarity: float) -> str:
        """Returns similarity level"""
        if similarity >= 0.8:
            return "🟢 Very high"
        elif similarity >= 0.6:
            return "🟡 High"
        elif similarity >= 0.4:
            return "🟠 Medium"
        elif similarity >= 0.2:
            return "🔴 Low"
        else:
            return "⚫ Very low"
    
    def _generate_additional_insights(self, country_data: Dict[str, CountryData]) -> List[str]:
        """Generates additional extended insights"""
        insights = []
        
        if len(country_data) < 2:
            return insights
        
        # Comment volume insights
        comment_counts = [(country, data.total_comments) for country, data in country_data.items()]
        comment_counts.sort(key=lambda x: x[1], reverse=True)
        
        highest_volume = comment_counts[0]
        lowest_volume = comment_counts[-1]
        
        if highest_volume[1] > 0 and lowest_volume[1] > 0:
            volume_ratio = highest_volume[1] / lowest_volume[1]
            if volume_ratio > 5:
                # ✅ ENGLISCH (vorher deutsch):
                insights.append(f"📊 **Large Discussion Differences:** {highest_volume[0]} has {volume_ratio:.1f}x more comments than {lowest_volume[0]}")
        
        # Topic diversity insights
        topic_diversities = []
        for country, data in country_data.items():
            unique_topics = len(data.topic_distribution)
            comments = data.total_comments
            if comments > 0:
                diversity_score = unique_topics / comments * 1000  # Topics per 1000 comments
                topic_diversities.append((country, diversity_score, unique_topics))
        
        if topic_diversities:
            topic_diversities.sort(key=lambda x: x[1], reverse=True)
            most_diverse = topic_diversities[0]
            least_diverse = topic_diversities[-1]
            
            # ✅ ENGLISCH (vorher deutsch):
            insights.append(f"🎭 **Topic Diversity:** {most_diverse[0]} has the most diverse discussions ({most_diverse[2]} topics), {least_diverse[0]} the most focused ({least_diverse[2]} topics)")
        
        # Emotion insights
        emotion_patterns = {}
        for country, data in country_data.items():
            if data.emotion_distribution:
                dominant_emotion = data.dominant_emotion
                if dominant_emotion not in emotion_patterns:
                    emotion_patterns[dominant_emotion] = []
                emotion_patterns[dominant_emotion].append(country)
        
        # Find emotion clusters
        for emotion, countries in emotion_patterns.items():
            if len(countries) > 1:
                emoji = self._get_emotion_emoji(emotion)
                # ✅ ENGLISCH (vorher deutsch):
                insights.append(f"{emoji} **Shared Emotion '{emotion}':** {', '.join(countries)} show similar emotional patterns")
        
        return insights


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main function of Enhanced Global Discourse Analysis with World Map"""
    setup_page()
    
    # *** ENHANCED HEADER WITH WORLD MAP FEATURE ***
    st.markdown("""
    ### 🚀 Version 2.1 - Enhanced Theme Search + Interactive World Map
    
    **New Features in this version:**
    - 🗺️ **Interactive World Map** with sentiment colors and detailed hover tooltips
    - 🎭 Predefined theme categories (Education, Gender, Technology, etc.)
    - 📊 Extended emotion categorization and sentiment scores
    - 🏆 Automatic country rankings and insights
    - 💬 Sample comments with emojis and metadata
    - 🎯 Engagement scores and extended metrics
    """)
    
    # Initialize manager
    manager = GlobalDiscourseAnalysisManager()
    
    # *** ENHANCED COUNTRY DETECTION INTERFACE ***
    manager.render_country_detection_interface()
    
    try:
        # Load available analyses
        with st.spinner("Loading available Country Analysis files..."):
            analysis_files = manager.get_available_analyses()
        
        if not analysis_files:
            st.error("No Country Analysis files found!")
            st.info("""
            **First Steps:**
            1. Perform comment analyses (German or English)
            2. Create Smart Topic Labels in the Topic Analysis
            3. Save with "🌍 Save for Country Analysis"
            4. Return to this page
            
            **Enhanced Features require:**
            • Smart Topic Labels in the original analyses
            • Emotion analysis data
            • At least 2 different countries for comparisons
            • **NEW:** World map visualization works from 1 country
            """)
            return
        
        # *** ENHANCED FILE SELECTION WITH COUNTRY DETECTION ***
        selected_files = render_file_selection_interface(analysis_files)
        
        if not selected_files:
            st.warning("Please select at least one file for comparison.")
            return
        
        if len(selected_files) == 1:
            st.info("💡 With only one country you can use the world map and Enhanced Theme Search!")
        
        # Load and aggregate data
        with st.spinner("Loading and aggregating country data..."):
            country_data = manager.load_country_data(selected_files)
        
        if not country_data:
            st.error("No valid country data could be loaded.")
            return
        
        # Check minimum requirements
        valid_countries = {
            country: data for country, data in country_data.items()
            if data.total_comments >= GlobalAnalysisConstants.MIN_COMMENTS_PER_COUNTRY
        }
        
        if not valid_countries:
            st.error(f"No countries with at least {GlobalAnalysisConstants.MIN_COMMENTS_PER_COUNTRY} comments found.")
            return
        
        # Warning for filtered countries
        if len(valid_countries) < len(country_data):
            filtered_countries = set(country_data.keys()) - set(valid_countries.keys())
            st.warning(f"Countries with too few comments excluded: {', '.join(filtered_countries)}")
        
        # *** ENHANCED SUCCESS MESSAGE WITH WORLD MAP INFO ***
        total_comments = sum(data.total_comments for data in valid_countries.values())
        languages = len(set(data.language for data in valid_countries.values()))
        
        # Check world map compatibility
        from utils.global_discourse_world_map import WorldMapConstants
        countries_with_coords = len([c for c in valid_countries.keys() 
                                   if c in WorldMapConstants.COUNTRY_COORDINATES])
        
        st.success(f"""
        ✅ **Enhanced Analysis with World Map ready!** 
        
        📊 **{len(valid_countries)} Countries** with **{total_comments:,} Comments**
        🌍 **{languages} Language(s)** available
        🗺️ **{countries_with_coords} of {len(valid_countries)} Countries** available on world map
        🎯 **Enhanced Theme Search** with 8 predefined categories active
        """)
        
        # *** WORLD MAP COMPATIBILITY CHECK ***
        if countries_with_coords < len(valid_countries):
            missing_coords = [c for c in valid_countries.keys() 
                            if c not in WorldMapConstants.COUNTRY_COORDINATES]
            st.info(f"💡 Countries without world map coordinates: {', '.join(missing_coords)} (can be added manually)")
        
        # ENHANCED Main analysis interface
        manager.render_analysis_tabs(valid_countries)
        
        # Enhanced export options (extended)
        st.markdown("---")
        st.subheader("💾 Enhanced Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Detailed Comparison Report"):
                comparison = manager.create_comparison(valid_countries)
                
                enhanced_report = {
                    "analysis_info": {
                        "version": "Enhanced v2.1 with World Map",
                        "countries": comparison.countries,
                        "total_comments": comparison.total_comments,
                        "languages": list(set(data.language for data in valid_countries.values())),
                        "analysis_date": datetime.now().isoformat(),
                        "world_map_compatible": countries_with_coords
                    },
                    "insights": comparison.insights,
                    "country_statistics": {
                        country: {
                            "comments": data.total_comments,
                            "top_sentiment": data.dominant_sentiment,
                            "top_emotion": data.dominant_emotion,
                            "unique_topics": len(data.topic_distribution),
                            "has_coordinates": country in WorldMapConstants.COUNTRY_COORDINATES
                        }
                        for country, data in valid_countries.items()
                    }
                }
                
                st.success("Enhanced Report with World Map info generated!")
                st.json(enhanced_report)
        
        with col2:
            if st.button("🎯 Theme Search Capabilities Export"):
                theme_capabilities = {
                    "available_themes": [
                        "Education & Learning",
                        "Gender & Equality", 
                        "Technology & AI",
                        "Environment & Climate",
                        "Politics & Society",
                        "Economy & Work",
                        "Health & Medicine",
                        "Culture & Media"
                    ],
                    "enhanced_features": [
                        "Emotion categorization",
                        "Sentiment scoring",
                        "Country rankings", 
                        "Sample comments with metadata",
                        "Engagement scoring",
                        "Statistical comparisons",
                        "Interactive world map",
                        "Geographic sentiment visualization"
                    ],
                    "countries_ready": list(valid_countries.keys()),
                    "world_map_ready": countries_with_coords,
                    "export_date": datetime.now().isoformat()
                }
                
                st.success("Theme Capabilities with World Map info exported!")
                st.json(theme_capabilities)
        
        with col3:
            if st.button("🗺️ World Map Data Export"):
                world_map_data = {
                    "supported_countries": list(WorldMapConstants.COUNTRY_COORDINATES.keys()),
                    "analyzed_countries": list(valid_countries.keys()),
                    "map_compatible_countries": [
                        c for c in valid_countries.keys() 
                        if c in WorldMapConstants.COUNTRY_COORDINATES
                    ],
                    "sentiment_distribution": {
                        country: data.dominant_sentiment 
                        for country, data in valid_countries.items()
                    },
                    "export_info": {
                        "total_supported": len(WorldMapConstants.COUNTRY_COORDINATES),
                        "currently_analyzed": len(valid_countries),
                        "map_coverage": f"{countries_with_coords/len(valid_countries)*100:.1f}%" if valid_countries else "0%"
                    }
                }
                
                st.success("World Map data exported!")
                st.json(world_map_data)
        
        # Enhanced debug information (with world map info)
        with st.expander("🔧 Enhanced Debug Information with World Map Status", expanded=False):
            debug_info = {
                "system_info": {
                    "available_files": len(analysis_files),
                    "selected_files": len(selected_files),
                    "loaded_countries": list(valid_countries.keys()),
                    "total_comments": total_comments,
                    "languages": list(set(data.language for data in valid_countries.values()))
                },
                "enhanced_features": {
                    "country_detection_enabled": True,
                    "enhanced_theme_search": True,
                    "emotion_categorization": True,
                    "sample_comments": True,
                    "country_rankings": True,
                    "world_map_integration": True
                },
                "world_map_status": {
                    "total_supported_countries": len(WorldMapConstants.COUNTRY_COORDINATES),
                    "analyzed_countries_with_coords": countries_with_coords,
                    "coverage_percentage": f"{countries_with_coords/len(valid_countries)*100:.1f}%" if valid_countries else "0%",
                    "missing_coordinates": [
                        c for c in valid_countries.keys() 
                        if c not in WorldMapConstants.COUNTRY_COORDINATES
                    ]
                },
                "data_quality": {
                    "countries_with_smart_labels": sum(
                        1 for data in valid_countries.values() 
                        if any(f.has_smart_labels for f in data.analysis_files)
                    ),
                    "countries_with_emotions": sum(
                        1 for data in valid_countries.values()
                        if data.emotion_distribution
                    ),
                    "average_comments_per_country": total_comments / len(valid_countries)
                }
            }
            
            st.json(debug_info)
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error("Please check your Country Analysis files and try again.")
        
        # Enhanced debug traceback
        with st.expander("🐛 Technical Details (Enhanced Debug)", expanded=False):
            st.code(traceback.format_exc())
            
            st.write("**Possible Solutions:**")
            st.write("• Make sure Smart Labels are present in the original analyses")
            st.write("• Check if emotion analysis was performed")
            st.write("• Check file paths and permissions")
            st.write("• Restart the application")
            st.write("• For world map issues: Check if PyDeck is installed (`pip install pydeck`)")


# =============================================================================
# EXECUTION
# =============================================================================

if __name__ == "__main__":
    main()
else:
    # Executed when imported as Streamlit page
    main()