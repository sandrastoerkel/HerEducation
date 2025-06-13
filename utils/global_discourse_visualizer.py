# =======================================================================================
# FILE: global_discourse_visualizer.py
# =======================================================================================

"""
🌍 GLOBAL DISCOURSE VISUALIZER - Charts & Visual Analytics
Creates visualizations for country comparisons with Plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from collections import defaultdict
import logging

# Local imports
from .global_discourse_models import (
    GlobalAnalysisConstants, CountryData, VisualizationConfig
)

# =============================================================================
# COUNTRY VISUALIZER
# =============================================================================

class CountryVisualizer:
    """Creates visualizations for country comparisons"""
    
    def __init__(self):
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
    
    def render_sentiment_comparison_chart(
        self,
        comparison_data: Dict[str, Dict[str, float]],
        config: Optional[VisualizationConfig] = None
    ) -> None:
        """Renders sentiment comparison chart"""
        if config is None:
            config = VisualizationConfig()
        
        try:
            # Prepare data for Plotly
            chart_data = []
            
            for country, sentiments in comparison_data.items():
                for sentiment, percentage in sentiments.items():
                    chart_data.append({
                        'Country': country,
                        'Sentiment': sentiment,
                        'Percentage': percentage
                    })
            
            if not chart_data:
                st.warning("No sentiment data available for comparison")
                return
            
            chart_df = pd.DataFrame(chart_data)
            
            # Plotly Chart
            fig = px.bar(
                chart_df,
                x='Country',
                y='Percentage',
                color='Sentiment',
                color_discrete_map=GlobalAnalysisConstants.SENTIMENT_COLORS,
                title='Sentiment Distribution by Countries',
                labels={'Percentage': 'Share (%)', 'Country': 'Country'},
                height=config.height
            )
            
            fig.update_layout(
                xaxis={'categoryorder': 'total descending'},
                showlegend=True,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            self.logger.error(f"Error rendering sentiment chart: {e}")
            st.error("Error creating sentiment visualization")
    
    def render_topic_comparison_chart(
        self,
        country_data: Dict[str, CountryData],
        max_topics: int = GlobalAnalysisConstants.TOP_TOPICS_DISPLAY,
        config: Optional[VisualizationConfig] = None
    ) -> None:
        """Renders topic comparison chart with Smart Labels"""
        if config is None:
            config = VisualizationConfig()
        
        try:
            # Collect all topics and their frequencies
            all_topics = set()
            for data in country_data.values():
                all_topics.update(data.topic_distribution.keys())
            
            # Limit to top topics
            topic_totals = defaultdict(int)
            for data in country_data.values():
                for topic, count in data.topic_distribution.items():
                    topic_totals[topic] += count
            
            top_topics = sorted(topic_totals.items(), key=lambda x: x[1], reverse=True)[:max_topics]
            selected_topics = [topic for topic, _ in top_topics]
            
            # Create heatmap data
            heatmap_data = []
            countries = list(country_data.keys())
            
            for topic in selected_topics:
                row = []
                for country in countries:
                    count = country_data[country].topic_distribution.get(topic, 0)
                    row.append(count)
                heatmap_data.append(row)
            
            if not heatmap_data:
                st.warning("No topic data available for comparison")
                return
            
            # Plotly Heatmap
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=countries,
                y=selected_topics,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Number of Comments")
            ))
            
            fig.update_layout(
                title='Smart Labels Distribution by Countries',
                xaxis_title='Country',
                yaxis_title='Topic (Smart Label)',
                height=max(config.height, len(selected_topics) * 25),
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            self.logger.error(f"Error rendering topic chart: {e}")
            st.error("Error creating topic visualization")
    
    def render_emotion_topic_matrix(
        self,
        country_data: CountryData,
        country_name: str,
        max_topics: int = 10,
        config: Optional[VisualizationConfig] = None
    ) -> None:
        """Renders emotion-per-topic matrix like in the screenshots"""
        if config is None:
            config = VisualizationConfig()
        
        try:
            if not country_data.topic_emotion_matrix:
                st.warning(f"No topic-emotion data available for {country_name}")
                return
            
            # Top topics for this country
            top_topics = sorted(
                country_data.topic_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:max_topics]
            
            # Prepare emotion data for chart
            emotion_data = []
            all_emotions = set()
            
            for topic, _ in top_topics:
                if topic in country_data.topic_emotion_matrix:
                    topic_emotions = country_data.topic_emotion_matrix[topic]
                    total_topic_comments = sum(topic_emotions.values())
                    
                    for emotion, count in topic_emotions.items():
                        percentage = (count / total_topic_comments * 100) if total_topic_comments > 0 else 0
                        emotion_data.append({
                            'Topic': topic,
                            'Emotion': emotion,
                            'Count': count,
                            'Percentage': percentage
                        })
                        all_emotions.add(emotion)
            
            if not emotion_data:
                st.warning(f"No processable emotion-topic data for {country_name}")
                return
            
            emotion_df = pd.DataFrame(emotion_data)
            
            # Plotly Stacked Bar Chart (like in screenshots)
            fig = px.bar(
                emotion_df,
                x='Topic',
                y='Percentage',
                color='Emotion',
                color_discrete_map=GlobalAnalysisConstants.EMOTION_COLORS,
                title=f'Emotional Reactions by Topics in {country_name}',
                labels={'Percentage': 'Share (%)', 'Topic': 'Topic (Smart Label)'},
                height=config.height
            )
            
            fig.update_layout(
                xaxis_tickangle=-45,
                xaxis={'categoryorder': 'total descending'},
                showlegend=True,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            self.logger.error(f"Error rendering emotion-topic matrix: {e}")
            st.error(f"Error creating emotion visualization for {country_name}")
    
    def render_country_overview_metrics(self, country_data: Dict[str, CountryData]) -> None:
        """Renders overview metrics for all countries"""
        try:
            st.subheader("📊 Country Overview")
            
            # Create overview table
            overview_data = []
            
            for country, data in country_data.items():
                overview_data.append({
                    'Country': country,
                    'Comments': f"{data.total_comments:,}",
                    'Language': data.language.upper(),
                    'Analyses': len(data.analysis_files),
                    'Top Topic': data.top_topics[0][0] if data.top_topics else "N/A",
                    'Dominant Sentiment': data.dominant_sentiment.title(),
                    'Dominant Emotion': data.dominant_emotion.title()
                })
            
            overview_df = pd.DataFrame(overview_data)
            st.dataframe(overview_df, use_container_width=True)
            
            # Quick metrics
            total_comments = sum(data.total_comments for data in country_data.values())
            total_files = sum(len(data.analysis_files) for data in country_data.values())
            languages = len(set(data.language for data in country_data.values()))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Countries", len(country_data))
            
            with col2:
                st.metric("Total Comments", f"{total_comments:,}")
            
            with col3:
                st.metric("Analyses", total_files)
            
            with col4:
                st.metric("Languages", languages)
            
        except Exception as e:
            self.logger.error(f"Error rendering overview metrics: {e}")
            st.error("Error creating overview")


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'CountryVisualizer'
]