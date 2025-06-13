# =======================================================================================
# FILE: global_discourse_theme_search_visualizer.py
# =======================================================================================

"""
🌍 GLOBAL DISCOURSE THEME SEARCH VISUALIZER - Charts & UI Interface
Visualizations and UI interface for enhanced theme-based country analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict, Counter
import logging
import re

# Local imports
from .global_discourse_models import GlobalAnalysisConstants, CountryData
from .global_discourse_data_loader import CountryDataLoader
from .global_discourse_theme_search_models import (
    ThemeCategory, THEME_KEYWORDS, THEME_COLORS, DEFAULT_CHART_HEIGHT, COMPACT_CHART_HEIGHT,
    EnhancedThemeSearchResult, EnhancedCountryThemeResult
)
from .global_discourse_theme_search_analyzer import EnhancedThemeSearchAnalyzer

# =============================================================================
# ENHANCED THEME SEARCH VISUALIZER
# =============================================================================

class EnhancedThemeSearchVisualizer:
    """Enhanced visualizations for theme-based search"""
    
    def __init__(self):
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
    
    def render_enhanced_theme_overview(self, result: EnhancedThemeSearchResult) -> None:
        """Renders enhanced overview"""
        if not result.success:
            st.warning(f"No comments found for {result.theme_category.value}.")
            return
        
        st.subheader(f"🎯 {result.theme_category.value} - Global Analysis")
        
        # Enhanced metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Comments", f"{result.total_matching_comments:,}")
        
        with col2:
            st.metric("Countries", len(result.countries_found))
        
        with col3:
            if result.most_discussed_country:
                count = result.country_results[result.most_discussed_country].matching_comments_count
                st.metric("Top Country", f"{result.most_discussed_country} ({count})")
        
        with col4:
            if result.global_sentiment_distribution:
                dominant = max(result.global_sentiment_distribution.items(), key=lambda x: x[1])
                st.metric("Global Sentiment", f"{dominant[0]} ({dominant[1]:.1f}%)")
        
        with col5:
            avg_comments = result.average_comments_per_country
            st.metric("Ø per Country", f"{avg_comments:.1f}")
        
        # Key insights
        if result.key_insights:
            st.subheader("💡 Key Insights")
            for insight in result.key_insights:
                st.info(insight)
        
        # Country comparisons
        if result.country_comparisons:
            st.subheader("⚖️ Country Comparisons")
            for comparison in result.country_comparisons:
                st.write(f"• {comparison}")
    
    def render_search_debug_info(self, result: EnhancedThemeSearchResult) -> None:
        """Renders debug information for search - NO EXPANDER"""
        
        if not hasattr(result, 'debug_info'):
            return
        
        st.subheader("🔧 Search Debug Information")
        st.write("**🔍 What was searched in each country?**")
        
        debug_data = []
        for country, info in result.debug_info.items():
            has_matches = country in result.country_results
            match_count = result.country_results[country].matching_comments_count if has_matches else 0
            
            debug_data.append({
                'Country': country,
                'Files': info['files_processed'],
                'Total Rows': f"{info['total_rows']:,}",
                'Found': match_count,
                'Hit Rate': f"{(match_count/info['total_rows']*100):.2f}%" if info['total_rows'] > 0 else "0%",
                'Status': '✅ Found' if match_count > 0 else '❌ Nothing found'
            })
        
        debug_df = pd.DataFrame(debug_data)
        st.dataframe(debug_df, use_container_width=True)
        
        # Detailed keyword debug info - WITHOUT EXPANDER
        st.write("**🎯 Keyword Hits per Country:**")
        
        for country, info in result.debug_info.items():
            if 'keyword_matches' in info and any(info['keyword_matches'].values()):
                st.write(f"**🌍 {country} - Keyword Details:**")
                keyword_data = []
                for keyword, count in info['keyword_matches'].items():
                    keyword_data.append({
                        'Keyword': keyword,
                        'Hits': count,
                        'Found': '✅' if count > 0 else '❌'
                    })
                
                keyword_df = pd.DataFrame(keyword_data)
                st.dataframe(keyword_df, use_container_width=True)
            
            # Show errors if any
            if info['search_errors']:
                st.warning(f"⚠️ Errors in {country}:")
                for error in info['search_errors']:
                    st.write(f"• {error}")
        
        # Summary
        st.write("**📊 Search Summary:**")
        
        total_files = sum(info['files_processed'] for info in result.debug_info.values())
        total_rows = sum(info['total_rows'] for info in result.debug_info.values())
        countries_with_data = len([info for info in result.debug_info.values() if info['total_rows'] > 0])
        countries_with_matches = len(result.countries_found)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Files Searched", total_files)
        
        with col2:
            st.metric("Rows Searched", f"{total_rows:,}")
        
        with col3:
            st.metric("Countries with Data", countries_with_data)
        
        with col4:
            st.metric("Countries with Matches", countries_with_matches)
        
        # Recommendations if little was found
        if countries_with_matches == 1:
            st.warning("⚠️ **Only one country has matches!** Possible reasons:")
            st.write("• Keywords are too specific for one language/culture")
            st.write("• Smart labels were created differently")
            st.write("• Topic is discussed differently in other countries")
            st.write("• Datasets from other countries are smaller")
            
            st.info("💡 **Recommendations:**")
            st.write("• Try broader/more general keywords")
            st.write("• Enable both Smart Labels and comment search")
            st.write("• Check debug info for keyword-specific hits")
        
        elif countries_with_matches == 0:
            st.error("❌ **No matches found!** Possible reasons:")
            st.write("• Keywords don't match the data")
            st.write("• Smart labels don't contain these terms")
            st.write("• Topic is discussed with different terms")
            
            st.info("💡 **Recommendations:**")
            st.write("• Look at original analyses to see what Smart Labels are available")
            st.write("• Try Custom Keywords with terms from your data")
            st.write("• Use broader search terms")
    
    def render_found_comments_verification(self, result: EnhancedThemeSearchResult) -> None:
        """Renders verification section with found comments - NO NESTED EXPANDERS"""
        if not result.country_results:
            return
        
        st.subheader("✅ Found Comments for Verification")
        
        st.info(f"""
        **📝 Verification:** Here you can see concrete examples of found comments 
        for the theme "{result.theme_category.value}" with keywords: {', '.join(result.keywords_used)}
        
        ✅ **All comments are shown in full length - no truncation!**
        """)
        
        # Option to show all found comments
        show_all_comments = st.checkbox(
            f"Show all {result.total_matching_comments} found comments (not just samples)",
            help="Warning: With many comments this can slow down the page"
        )
        
        # Collect all sample comments or all comments
        if show_all_comments:
            # Load all comments for complete verification
            st.warning(f"⚠️ Loading all {result.total_matching_comments} comments - this may take a moment...")
            all_samples = self._load_all_matching_comments(result)
        else:
            # Only sample comments
            all_samples = []
            for country, country_result in result.country_results.items():
                for comment in country_result.sample_comments:
                    comment_with_country = comment.copy()
                    comment_with_country['country'] = country
                    all_samples.append(comment_with_country)
        
        if not all_samples:
            st.warning("No sample comments available for verification")
            return
        
        # Info about displayed comments
        if show_all_comments:
            st.success(f"📊 Showing {len(all_samples)} comments for complete verification")
        else:
            st.info(f"📊 Showing {len(all_samples)} sample comments (from {result.total_matching_comments} found)")
            st.caption("💡 Enable 'Show all comments' for complete verification")
        
        # Group by sentiment for better overview
        sentiment_groups = {'positive': [], 'neutral': [], 'negative': []}
        for comment in all_samples:
            sentiment = comment['sentiment'].lower()
            if sentiment in sentiment_groups:
                sentiment_groups[sentiment].append(comment)
        
        # TABS INSTEAD OF EXPANDER for sentiment groups!
        sentiment_tabs = []
        sentiment_labels = []
        
        for sentiment, comments in sentiment_groups.items():
            if comments:
                sentiment_emoji = self._get_sentiment_emoji(sentiment)
                sentiment_labels.append(f"{sentiment_emoji} {sentiment.title()} ({len(comments)})")
                sentiment_tabs.append(comments)
        
        if sentiment_tabs:
            tabs = st.tabs(sentiment_labels)
            
            for tab_idx, (sentiment, comments) in enumerate(
                [(k, v) for k, v in sentiment_groups.items() if v]
            ):
                with tabs[tab_idx]:
                    
                    # Limit display for very many comments
                    display_count = len(comments)
                    max_display = 50 if show_all_comments else 10
                    
                    if display_count > max_display:
                        comments_to_show = comments[:max_display]
                        show_more_info = f" (showing {max_display} of {display_count})"
                    else:
                        comments_to_show = comments
                        show_more_info = ""
                    
                    if show_more_info:
                        st.info(f"Showing {len(comments_to_show)} of {display_count} comments")
                    
                    # Performance warning for many comments
                    if len(comments_to_show) > 20:
                        st.info(f"⚡ Showing {len(comments_to_show)} comments - loading may take a moment")
                    
                    # Show comments
                    for i, comment in enumerate(comments_to_show, 1):
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            # Comment in full length with keyword highlighting
                            highlighted_text = self._highlight_keywords_in_text(
                                comment['text'],  # *** FULL TEXT ***
                                result.keywords_used
                            )
                            
                            # Structured display with complete text
                            st.markdown(f"**Comment {i}:**")
                            
                            # Text in container for better readability
                            with st.container():
                                st.markdown(highlighted_text)
                            
                            # Metadata below
                            st.caption(f"🌍 **{comment['country']}** | 🏷️ **{comment['smart_label']}** | "
                                     f"{comment['sentiment_emoji']} **{comment['sentiment']}** | "
                                     f"{comment['emotion_emoji']} **{comment['emotion']}**")
                        
                        with col2:
                            # Additional info
                            st.metric("Characters", f"{comment['length']}")
                        
                        st.divider()
                    
                    # Info if not all comments are shown
                    if display_count > max_display:
                        st.info(f"💡 {display_count - max_display} more {sentiment} comments available. "
                               f"{'Increase limit' if not show_all_comments else 'Already maximum display'}")
        
        # Statistics about found keywords
        self._render_keyword_verification_stats(result)
    
    def _load_all_matching_comments(self, result: EnhancedThemeSearchResult) -> List[Dict[str, Any]]:
        """Loads all found comments for complete verification"""
        all_comments = []
        
        # Since we can't directly access country_data,
        # we load comments via a simpler method
        st.info("💡 Complete comment verification: This function loads all found comments from all analyzed files.")
        
        # For now return sample comments with a warning
        # In a complete implementation one would reload the files here
        sample_comments = []
        for country, country_result in result.country_results.items():
            for comment in country_result.sample_comments:
                comment_with_country = comment.copy()
                comment_with_country['country'] = country
                sample_comments.append(comment_with_country)
        
        st.warning(f"Note: Showing {len(sample_comments)} sample comments. For all {result.total_matching_comments} comments would require extended database query.")
        
        return sample_comments
    
    def _highlight_keywords_in_text(self, text: str, keywords: List[str]) -> str:
        """Highlights keywords in text"""
        highlighted_text = text
        
        for keyword in keywords:
            # Case-insensitive highlighting
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_text = pattern.sub(f"**:red[{keyword.upper()}]**", highlighted_text)
        
        return highlighted_text
    
    def _render_keyword_verification_stats(self, result: EnhancedThemeSearchResult) -> None:
        """Renders keyword verification statistics - WITHOUT EXPANDER"""
        st.subheader("🔍 Keyword Verification")
        
        # Collect keyword statistics from COMPLETE texts
        keyword_stats = {}
        for country, country_result in result.country_results.items():
            for comment in country_result.sample_comments:
                full_text = comment['text']  # *** FULL TEXT ***
                text_lower = full_text.lower()
                for keyword in result.keywords_used:
                    if keyword.lower() in text_lower:
                        if keyword not in keyword_stats:
                            keyword_stats[keyword] = {'total': 0, 'countries': set(), 'sample_texts': []}
                        keyword_stats[keyword]['total'] += 1
                        keyword_stats[keyword]['countries'].add(country)
                        # Store some sample texts for verification
                        if len(keyword_stats[keyword]['sample_texts']) < 3:
                            keyword_stats[keyword]['sample_texts'].append({
                                'text': full_text,  # *** FULL TEXT ***
                                'country': country
                            })
        
        if keyword_stats:
            st.write("**Found Keywords in Sample Comments:**")
            
            # Create DataFrame for better display
            stats_data = []
            for keyword, stats in sorted(keyword_stats.items(), key=lambda x: x[1]['total'], reverse=True):
                stats_data.append({
                    'Keyword': f"**{keyword}**",
                    'Hits': stats['total'],
                    'Countries': len(stats['countries']),
                    'Country List': ', '.join(sorted(stats['countries']))
                })
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True)
            
            # Sample texts for keyword verification - WITHOUT EXPANDER
            st.write("**🔍 Keyword Examples for Verification:**")
            
            # Show only top 5 keywords with examples
            top_keywords = sorted(keyword_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
            
            for keyword, stats in top_keywords:
                if stats['sample_texts']:
                    st.write(f"**Examples for '{keyword}' ({stats['total']} hits):**")
                    
                    for i, sample in enumerate(stats['sample_texts'], 1):
                        st.write(f"**Example {i} from {sample['country']}:**")
                        
                        # Highlight only this one keyword in complete text
                        highlighted = self._highlight_keywords_in_text(
                            sample['text'], 
                            [keyword]
                        )
                        
                        with st.container():
                            st.markdown(highlighted)
                        st.divider()
        else:
            st.warning("No keywords found in sample comments")
    
    def render_enhanced_sentiment_analysis(self, result: EnhancedThemeSearchResult) -> None:
        """Renders enhanced sentiment analysis"""
        if not result.country_results:
            return
        
        st.subheader("📊 Sentiment Analysis by Countries")
        
        # Sentiment comparison chart
        chart_data = []
        
        for country, country_result in result.country_results.items():
            for sentiment, percentage in country_result.sentiment_percentages.items():
                chart_data.append({
                    'Country': country,
                    'Sentiment': sentiment,
                    'Percent': percentage,
                    'Count': country_result.sentiment_distribution.get(sentiment, 0),
                    'Total': country_result.matching_comments_count
                })
        
        if chart_data:
            chart_df = pd.DataFrame(chart_data)
            
            fig = px.bar(
                chart_df,
                x='Country',
                y='Percent',
                color='Sentiment',
                color_discrete_map=GlobalAnalysisConstants.SENTIMENT_COLORS,
                title=f'Sentiment on "{result.theme_category.value}" by Countries',
                labels={'Percent': 'Share (%)', 'Country': 'Country'},
                hover_data=['Count', 'Total']
            )
            
            fig.update_layout(
                xaxis={'categoryorder': 'total descending'},
                showlegend=True,
                height=DEFAULT_CHART_HEIGHT
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment score ranking
        sentiment_scores = []
        for country, result_data in result.country_results.items():
            if result_data.emotion_statistics:
                sentiment_scores.append({
                    'Country': country,
                    'Sentiment Score': f"{result_data.emotion_statistics.sentiment_score:.1f}",
                    'Positive %': f"{result_data.emotion_statistics.positive_ratio:.1%}",
                    'Negative %': f"{result_data.emotion_statistics.negative_ratio:.1%}",
                    'Comments': result_data.matching_comments_count
                })
        
        if sentiment_scores:
            st.subheader("🏆 Sentiment Score Ranking")
            sentiment_df = pd.DataFrame(sentiment_scores)
            st.dataframe(sentiment_df, use_container_width=True)
    
    def render_enhanced_emotion_analysis(self, result: EnhancedThemeSearchResult) -> None:
        """Renders enhanced emotion analysis"""
        if not result.country_results:
            return
        
        st.subheader("😊 Emotion Analysis by Countries")
        
        # Emotion heatmap
        countries = list(result.country_results.keys())
        all_emotions = set()
        
        for country_result in result.country_results.values():
            all_emotions.update(country_result.emotion_distribution.keys())
        
        all_emotions = sorted(list(all_emotions))
        
        if all_emotions and countries:
            heatmap_data = []
            
            for emotion in all_emotions:
                row = []
                for country in countries:
                    percentage = result.country_results[country].emotion_percentages.get(emotion, 0)
                    row.append(percentage)
                heatmap_data.append(row)
            
            if heatmap_data:
                fig = go.Figure(data=go.Heatmap(
                    z=heatmap_data,
                    x=countries,
                    y=all_emotions,
                    colorscale='RdYlBu_r',
                    showscale=True,
                    colorbar=dict(title="Percent (%)")
                ))
                
                fig.update_layout(
                    title=f'Emotional Reactions to "{result.theme_category.value}"',
                    xaxis_title='Country',
                    yaxis_title='Emotion',
                    height=COMPACT_CHART_HEIGHT
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def render_enhanced_country_details(self, result: EnhancedThemeSearchResult) -> None:
        """Renders enhanced country details"""
        if not result.country_results:
            return
        
        st.subheader("🌍 Detailed Country Analysis")
        
        # Sort by comment count
        sorted_countries = sorted(
            result.country_results.items(),
            key=lambda x: x[1].matching_comments_count,
            reverse=True
        )
        
        for country, country_result in sorted_countries:
            with st.expander(
                f"🌍 {country} - {country_result.matching_comments_count} Comments "
                f"(Engagement: {country_result.engagement_score:.0f}%)",
                expanded=False
            ):
                
                # Metrics for this country
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Comments", country_result.matching_comments_count)
                
                with col2:
                    if country_result.emotion_statistics:
                        score = country_result.emotion_statistics.sentiment_score
                        st.metric("Sentiment Score", f"{score:.1f}")
                
                with col3:
                    st.metric("Smart Labels", country_result.unique_smart_labels_count)
                
                with col4:
                    avg_length = country_result.average_comment_length
                    st.metric("Ø Length", f"{avg_length:.0f} characters")
                
                # Detailed distributions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Sentiment Distribution:**")
                    for sentiment, percentage in country_result.sentiment_percentages.items():
                        count = country_result.sentiment_distribution[sentiment]
                        emoji = self._get_sentiment_emoji(sentiment)
                        st.write(f"{emoji} {sentiment}: {percentage:.1f}% ({count})")
                
                with col2:
                    st.write("**Top Emotions:**")
                    sorted_emotions = sorted(
                        country_result.emotion_percentages.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for emotion, percentage in sorted_emotions[:5]:
                        count = country_result.emotion_distribution[emotion]
                        emoji = self._get_emotion_emoji(emotion)
                        st.write(f"{emoji} {emotion}: {percentage:.1f}% ({count})")
                
                # Top Smart Labels
                if country_result.top_smart_labels:
                    st.write("**Top Smart Labels:**")
                    for label, count in country_result.top_smart_labels[:5]:
                        st.write(f"🏷️ {label}: {count} comments")
                
                # Featured comment verification
                if country_result.sample_comments:
                    st.write("**📝 Comment Examples for Verification:**")
                    
                    for i, comment in enumerate(country_result.sample_comments, 1):
                        # Container for better structure
                        with st.container():
                            st.markdown(f"**Example {i}:**")
                            
                            # Keyword highlighting in COMPLETE text
                            highlighted_text = self._highlight_keywords_in_text(
                                comment['text'],  # *** FULL TEXT WITHOUT TRUNCATION ***
                                country_result.keywords_used
                            )
                            
                            # Complete text in own container
                            st.markdown("📖 **Complete Comment:**")
                            st.markdown(highlighted_text)
                            
                            # Metadata compactly below
                            st.caption(f"{comment['sentiment_emoji']} **{comment['sentiment']}** | "
                                     f"{comment['emotion_emoji']} **{comment['emotion']}** | "
                                     f"🏷️ **{comment['smart_label']}** | "
                                     f"📏 **{comment['length']} characters**")
                            
                            st.divider()
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Emoji for sentiment"""
        emojis = {'positive': '😊', 'negative': '😞', 'neutral': '😐'}
        return emojis.get(sentiment.lower(), '❓')
    
    def _get_emotion_emoji(self, emotion: str) -> str:
        """Emoji for emotion"""
        emojis = {
            'joy': '😄', 'sadness': '😢', 'anger': '😠',
            'fear': '😨', 'disgust': '🤢', 'surprise': '😲',
            'love': '❤️', 'neutral': '😐'
        }
        return emojis.get(emotion.lower(), '❓')


# =============================================================================
# ENHANCED UI INTERFACE
# =============================================================================

def render_enhanced_theme_search_interface(
    country_data: Dict[str, CountryData],
    data_loader: CountryDataLoader
) -> None:
    """Renders the enhanced theme search interface"""
    
    st.subheader("🎯 Enhanced Theme-based Country Analysis")
    
    st.markdown("""
    **Analyze specific themes across all countries with enhanced insights.**
    
    Select predefined themes or create your own search criteria for detailed
    cross-country comparisons with sentiment and emotion analysis.
    """)
    
    # Theme selection interface
    st.subheader("🎭 Theme Selection")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Predefined theme buttons
        st.write("**Predefined Themes:**")
        
        theme_cols = st.columns(3)
        selected_theme = None
        
        predefined_themes = [
            ThemeCategory.EDUCATION,
            ThemeCategory.GENDER, 
            ThemeCategory.TECHNOLOGY,
            ThemeCategory.ENVIRONMENT,
            ThemeCategory.POLITICS,
            ThemeCategory.ECONOMY
        ]
        
        for i, theme in enumerate(predefined_themes):
            with theme_cols[i % 3]:
                if st.button(
                    f"🎯 {theme.value}",
                    key=f"theme_{theme.name}",
                    use_container_width=True
                ):
                    selected_theme = theme
        
        # Custom theme option
        st.write("**Or custom search terms:**")
        custom_keywords_input = st.text_input(
            "Custom search terms (comma-separated):",
            placeholder="e.g. artificial intelligence, automation, future",
            help="Enter custom search terms, separated by commas"
        )
    
    with col2:
        st.write("**Search Options:**")
        search_in_labels = st.checkbox("Search in Smart Labels", value=True)
        search_in_comments = st.checkbox("Search in comment texts", value=True)
        
        max_samples = st.slider("Sample comments per country", 1, 10, 5)
    
    # Analysis button
    analyze_button = st.button("🔍 Start Enhanced Analysis", type="primary")
    
    # Perform analysis
    if analyze_button:
        if selected_theme:
            # Predefined theme
            theme_category = selected_theme
            custom_keywords = None
        elif custom_keywords_input.strip():
            # Custom keywords
            theme_category = ThemeCategory.CUSTOM
            custom_keywords = [kw.strip() for kw in custom_keywords_input.split(",") if kw.strip()]
        else:
            st.error("Please select a theme or enter custom search terms.")
            return
        
        if not search_in_labels and not search_in_comments:
            st.error("Please select at least one search option.")
            return
        
        # Perform enhanced analysis
        with st.spinner(f"Performing enhanced analysis for '{theme_category.value}'..."):
            analyzer = EnhancedThemeSearchAnalyzer(country_data, data_loader)
            result = analyzer.search_theme_across_countries(
                theme_category=theme_category,
                custom_keywords=custom_keywords,
                search_in_smart_labels=search_in_labels,
                search_in_comments=search_in_comments,
                max_samples_per_country=max_samples
            )
        
        # Show results
        if result.success:
            visualizer = EnhancedThemeSearchVisualizer()
            
            # Enhanced overview
            visualizer.render_enhanced_theme_overview(result)
            
            # *** DEBUG SECTION FOR QUALITY CONTROL ***
            visualizer.render_search_debug_info(result)
            
            # *** VERIFICATION SECTION ***
            visualizer.render_found_comments_verification(result)
            
            # Enhanced sentiment analysis
            visualizer.render_enhanced_sentiment_analysis(result)
            
            # Enhanced emotion analysis
            visualizer.render_enhanced_emotion_analysis(result)
            
            # Detailed country analysis
            visualizer.render_enhanced_country_details(result)
            
        else:
            st.warning(f"No comments found for '{theme_category.value}'.")
            
            # Show debug info even when no matches
            if hasattr(result, 'debug_info'):
                visualizer = EnhancedThemeSearchVisualizer()
                visualizer.render_search_debug_info(result)
            
            st.info("**Improvement Suggestions:**")
            st.write("• Use different search terms")
            st.write("• Try less specific terms")
            st.write("• Check search options")
            st.write("• Look at debug info for details")
            st.write("• Check if Smart Labels are present in original analyses")
    
    # Show available theme examples
    if not analyze_button:
        st.subheader("💡 Example Themes with Search Terms")
        
        example_cols = st.columns(2)
        
        with example_cols[0]:
            for theme in [ThemeCategory.EDUCATION, ThemeCategory.TECHNOLOGY, ThemeCategory.ENVIRONMENT]:
                with st.expander(f"🎯 {theme.value}", expanded=False):
                    keywords = THEME_KEYWORDS.get(theme, [])
                    st.write("**Search Terms:**")
                    st.write(", ".join(keywords[:10]))
                    if len(keywords) > 10:
                        st.write(f"... and {len(keywords) - 10} more")
        
        with example_cols[1]:
            for theme in [ThemeCategory.GENDER, ThemeCategory.POLITICS, ThemeCategory.ECONOMY]:
                with st.expander(f"🎯 {theme.value}", expanded=False):
                    keywords = THEME_KEYWORDS.get(theme, [])
                    st.write("**Search Terms:**")
                    st.write(", ".join(keywords[:10]))
                    if len(keywords) > 10:
                        st.write(f"... and {len(keywords) - 10} more")


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'EnhancedThemeSearchVisualizer',
    'render_enhanced_theme_search_interface'
]