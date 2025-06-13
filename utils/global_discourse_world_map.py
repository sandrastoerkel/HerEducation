# =======================================================================================
# FILE: global_discourse_world_map.py
# =======================================================================================

"""
🌍 GLOBAL DISCOURSE WORLD MAP - Interactive World Map Visualization
Interactive world map for global discourse analysis with sentiment colors and hover details
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from typing import Dict, List, Optional, Tuple, Any
import logging

# Local imports
from .global_discourse_models import GlobalAnalysisConstants, CountryData

# =============================================================================
# WORLD MAP CONSTANTS
# =============================================================================

class WorldMapConstants:
    """Constants for world map visualization"""
    
    # Map configuration
    MAP_STYLE = 'mapbox://styles/mapbox/satellite-streets-v11'
    MAP_HEIGHT = 600
    SCATTER_RADIUS = 100000
    
    # Sentiment colors for map (RGBA)
    SENTIMENT_COLORS = {
        'positive': [46, 139, 87, 200],      # Sea Green
        'neutral': [255, 215, 0, 200],       # Gold
        'negative': [220, 20, 60, 200],      # Crimson
        'unknown': [128, 128, 128, 150]      # Gray
    }
    
    # Country coordinates (capitals/centers)
    COUNTRY_COORDINATES = {
        # DACH Region
        "Germany": {"latitude": 52.5200, "longitude": 13.4050},
        "Austria": {"latitude": 48.2082, "longitude": 16.3738},
        "Switzerland": {"latitude": 46.9480, "longitude": 7.4474},
        
        # North America
        "United States": {"latitude": 38.9072, "longitude": -77.0369},
        "Canada": {"latitude": 45.4215, "longitude": -75.6972},
        
        # United Kingdom & Ireland
        "United Kingdom": {"latitude": 51.5074, "longitude": -0.1278},
        "Ireland": {"latitude": 53.3498, "longitude": -6.2603},
        
        # Oceania
        "Australia": {"latitude": -35.2809, "longitude": 149.1300},
        "New Zealand": {"latitude": -41.2865, "longitude": 174.7762},
        
        # South Asia
        "India": {"latitude": 28.6139, "longitude": 77.2090},
        "Pakistan": {"latitude": 33.6844, "longitude": 73.0479},
        "Bangladesh": {"latitude": 23.8103, "longitude": 90.4125},
        "Sri Lanka": {"latitude": 6.9271, "longitude": 79.8612},
        
        # East Asia
        "China": {"latitude": 39.9042, "longitude": 116.4074},
        "Japan": {"latitude": 35.6762, "longitude": 139.6503},
        "South Korea": {"latitude": 37.5665, "longitude": 126.9780},
        
        # Southeast Asia
        "Thailand": {"latitude": 13.7563, "longitude": 100.5018},
        "Vietnam": {"latitude": 21.0285, "longitude": 105.8542},
        "Philippines": {"latitude": 14.5995, "longitude": 120.9842},
        "Indonesia": {"latitude": -6.2088, "longitude": 106.8456},
        "Malaysia": {"latitude": 3.1390, "longitude": 101.6869},
        "Singapore": {"latitude": 1.3521, "longitude": 103.8198},
        
        # Europe
        "France": {"latitude": 48.8566, "longitude": 2.3522},
        "Spain": {"latitude": 40.4168, "longitude": -3.7038},
        "Italy": {"latitude": 41.9028, "longitude": 12.4964},
        "Netherlands": {"latitude": 52.3676, "longitude": 4.9041},
        "Poland": {"latitude": 52.2297, "longitude": 21.0122},
        "Sweden": {"latitude": 59.3293, "longitude": 18.0686},
        "Norway": {"latitude": 59.9139, "longitude": 10.7522},
        "Denmark": {"latitude": 55.6761, "longitude": 12.5683},
        "Finland": {"latitude": 60.1699, "longitude": 24.9384},
        
        # Latin America
        "Brazil": {"latitude": -15.8267, "longitude": -47.9218},
        "Mexico": {"latitude": 19.4326, "longitude": -99.1332},
        "Argentina": {"latitude": -34.6118, "longitude": -58.3960},
        
        # Africa
        "South Africa": {"latitude": -25.7479, "longitude": 28.2293},
        "Nigeria": {"latitude": 9.0765, "longitude": 7.3986},
        "Egypt": {"latitude": 30.0444, "longitude": 31.2357},
        
        # Middle East
        "Israel": {"latitude": 31.7683, "longitude": 35.2137},
        "Turkey": {"latitude": 39.9334, "longitude": 32.8597},
        
        # Eastern Europe
        "Russia": {"latitude": 55.7558, "longitude": 37.6176},
        "Ukraine": {"latitude": 50.4501, "longitude": 30.5234}
    }


# =============================================================================
# WORLD MAP VISUALIZER
# =============================================================================

class GlobalDiscourseWorldMap:
    """Creates interactive world map for global discourse analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
    
    def create_interactive_world_map(
        self,
        country_data: Dict[str, CountryData],
        selected_country: Optional[str] = None
    ) -> None:
        """Creates interactive world map with sentiment colors and topic hover"""
        
        st.subheader("🗺️ Global Discourse World Map")
        st.caption("Countries colored by dominant sentiment. Hover over a point for details.")
        
        # Country filter
        countries_list = list(country_data.keys())
        if selected_country:
            if selected_country in countries_list:
                filtered_countries = {selected_country: country_data[selected_country]}
            else:
                st.warning(f"Country '{selected_country}' not found in available data.")
                return
        else:
            # Optional: Country selection dropdown
            col1, col2 = st.columns([3, 1])
            with col2:
                show_single = st.selectbox(
                    "🌍 Focus on Country",
                    ["Show all countries"] + sorted(countries_list),
                    key="world_map_country_filter"
                )
            
            if show_single != "Show all countries":
                filtered_countries = {show_single: country_data[show_single]}
            else:
                filtered_countries = country_data
        
        # Prepare map data
        map_data = self._prepare_map_data(filtered_countries)
        
        if map_data.empty:
            st.warning("No countries with valid coordinates found.")
            return
        
        # Create PyDeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position='[longitude, latitude]',
            get_color='color',
            get_radius=WorldMapConstants.SCATTER_RADIUS,
            pickable=True,
            auto_highlight=True
        )
        
        # View State (world center)
        view_state = pdk.ViewState(
            latitude=20,
            longitude=0,
            zoom=1.5,
            pitch=0
        )
        
        # Extended tooltip information
        tooltip = {
            "html": """
                <div style='max-width: 500px; white-space: normal; background: rgba(255,255,255,0.95); 
                           padding: 15px; border-radius: 8px; border: 1px solid #ddd;'>
                    <h3 style='margin: 0 0 10px 0; color: #2E86C1;'>🌍 {country}</h3>
                    
                    <div style='margin-bottom: 10px;'>
                        <strong>📊 Total:</strong> {total_comments:,} comments<br>
                        <strong>🗣️ Language:</strong> {language}<br>
                        <strong>📈 Sentiment:</strong> {dominant_sentiment_emoji} {dominant_sentiment}
                    </div>
                    
                    <div style='margin-bottom: 10px;'>
                        <strong style='color: #E74C3C;'>🔥 Top Topics:</strong><br>
                        {top_topics}
                    </div>
                    
                    <div style='margin-bottom: 10px;'>
                        <strong style='color: #8E44AD;'>😊 Top Emotions:</strong><br>
                        {top_emotions}
                    </div>
                    
                    <div style='font-size: 12px; color: #7F8C8D; border-top: 1px solid #eee; padding-top: 8px; margin-top: 8px;'>
                        💡 Click on the country for detailed analysis
                    </div>
                </div>
            """,
            "style": {
                "backgroundColor": "transparent",
                "border": "none"
            }
        }
        
        # Render map
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
                height=WorldMapConstants.MAP_HEIGHT,
                map_style=WorldMapConstants.MAP_STYLE
            ),
            use_container_width=True
        )
        
        # Legend
        self._render_map_legend()
        
        # Map statistics
        self._render_map_statistics(map_data, filtered_countries)
    
    def _prepare_map_data(self, country_data: Dict[str, CountryData]) -> pd.DataFrame:
        """Prepares data for the world map"""
        map_rows = []
        
        for country, data in country_data.items():
            # Get coordinates
            coords = WorldMapConstants.COUNTRY_COORDINATES.get(country)
            if not coords:
                self.logger.warning(f"No coordinates available for {country}")
                continue
            
            # Determine dominant sentiment
            dominant_sentiment = data.dominant_sentiment if data.sentiment_distribution else 'unknown'
            
            # Sentiment color
            color = WorldMapConstants.SENTIMENT_COLORS.get(dominant_sentiment, 
                                                          WorldMapConstants.SENTIMENT_COLORS['unknown'])
            
            # Format top topics (for tooltip)
            top_topics_formatted = ""
            if data.top_topics:
                for i, (topic, count) in enumerate(data.top_topics[:5], 1):
                    percentage = data.topic_percentages.get(topic, 0)
                    top_topics_formatted += f"• {topic} ({percentage:.1f}%)<br>"
            else:
                top_topics_formatted = "• No topic data available"
            
            # Format top emotions
            top_emotions_formatted = ""
            if data.emotion_distribution:
                sorted_emotions = sorted(
                    data.emotion_percentages.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                for emotion, percentage in sorted_emotions:
                    count = data.emotion_distribution[emotion]
                    emoji = self._get_emotion_emoji(emotion)
                    top_emotions_formatted += f"• {emoji} {emotion} ({percentage:.1f}%)<br>"
            else:
                top_emotions_formatted = "• No emotion data available"
            
            # Sentiment emoji
            sentiment_emoji = self._get_sentiment_emoji(dominant_sentiment)
            
            map_rows.append({
                'country': country,
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'color': color,
                'total_comments': data.total_comments,
                'language': data.language.upper(),
                'dominant_sentiment': dominant_sentiment.title(),
                'dominant_sentiment_emoji': sentiment_emoji,
                'top_topics': top_topics_formatted,
                'top_emotions': top_emotions_formatted
            })
        
        return pd.DataFrame(map_rows)
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Returns emoji for sentiment"""
        emojis = {
            'positive': '😊',
            'negative': '😞', 
            'neutral': '😐',
            'unknown': '❓'
        }
        return emojis.get(sentiment.lower(), '❓')
    
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
    
    def _render_map_legend(self) -> None:
        """Renders map legend"""
        st.markdown("""
        <div style="display: flex; justify-content: center; margin: 20px 0; 
                    background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
            <div style="display: flex; align-items: center; margin: 0 20px;">
                <div style="width: 20px; height: 20px; border-radius: 50%; margin-right: 8px; 
                           background-color: rgb(46, 139, 87);"></div>
                <span><strong>😊 Positive</strong></span>
            </div>
            <div style="display: flex; align-items: center; margin: 0 20px;">
                <div style="width: 20px; height: 20px; border-radius: 50%; margin-right: 8px; 
                           background-color: rgb(255, 215, 0);"></div>
                <span><strong>😐 Neutral</strong></span>
            </div>
            <div style="display: flex; align-items: center; margin: 0 20px;">
                <div style="width: 20px; height: 20px; border-radius: 50%; margin-right: 8px; 
                           background-color: rgb(220, 20, 60);"></div>
                <span><strong>😞 Negative</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_map_statistics(self, map_data: pd.DataFrame, country_data: Dict[str, CountryData]) -> None:
        """Renders map statistics"""
        if map_data.empty:
            return
        
        st.subheader("📊 World Map Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Countries on Map", len(map_data))
        
        with col2:
            total_comments = sum(data.total_comments for data in country_data.values())
            st.metric("Total Comments", f"{total_comments:,}")
        
        with col3:
            # Sentiment distribution
            sentiment_counts = map_data['dominant_sentiment'].value_counts()
            most_common_sentiment = sentiment_counts.index[0] if not sentiment_counts.empty else "N/A"
            st.metric("Most Common Sentiment", most_common_sentiment)
        
        with col4:
            languages = len(set(data.language for data in country_data.values()))
            st.metric("Languages", languages)
        
        # Detailed statistics
        if len(map_data) > 1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🌍 Countries by Sentiment:**")
                sentiment_df = map_data.groupby('dominant_sentiment').agg({
                    'country': 'count',
                    'total_comments': 'sum'
                }).rename(columns={'country': 'Number of Countries', 'total_comments': 'Total Comments'})
                st.dataframe(sentiment_df, use_container_width=True)
            
            with col2:
                st.write("**📊 Top Countries by Comments:**")
                top_countries = map_data.nlargest(5, 'total_comments')[['country', 'total_comments', 'dominant_sentiment']]
                top_countries = top_countries.rename(columns={
                    'country': 'Country',
                    'total_comments': 'Comments', 
                    'dominant_sentiment': 'Sentiment'
                })
                st.dataframe(top_countries, use_container_width=True)


# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

def integrate_world_map_in_sentiment_tab(country_data: Dict[str, CountryData]) -> None:
    """Integrates world map in the sentiment comparison tab"""
    
    # Create sub-tabs for better organization
    map_tab, chart_tab = st.tabs(["🗺️ World Map", "📊 Comparison Charts"])
    
    with map_tab:
        if len(country_data) == 0:
            st.warning("No country data available for world map")
            return
        
        # Info box
        st.info(f"""
        **🌍 Interactive World Map of Global Discourses**
        
        • **{len(country_data)} Countries** are displayed
        • **Colors** represent the dominant sentiment
        • **Hover** over points for detailed information
        • **Click** (planned) for country-specific analysis
        """)
        
        # Create world map
        world_map = GlobalDiscourseWorldMap()
        world_map.create_interactive_world_map(country_data)
    
    with chart_tab:
        # Here the existing sentiment charts go
        st.write("**📊 Here the existing sentiment comparison charts will be displayed**")
        st.info("This section will contain the existing Plotly charts from the sentiment tab")


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'GlobalDiscourseWorldMap',
    'WorldMapConstants',
    'integrate_world_map_in_sentiment_tab'
]