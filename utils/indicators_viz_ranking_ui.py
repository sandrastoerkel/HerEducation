"""
UI rendering functions for country ranking visualization in HerAtlas Indicators.

This module provides the user interface components and main ranking function
with comprehensive multilingual support.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Any

from .indicators_viz_core import VisualizationConfig, ChangeType, DEFAULT_CHART_HEIGHT
from .indicators_viz_ranking_core import (
    render_ranking_chart, create_progress_ranking, create_regress_ranking, create_netto_ranking,
    split_netto_ranking, calculate_filtered_country_results, get_countries_with_changes,
    get_country_changes_by_year
)
from .indicators_viz_multilingual import get_text


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_ranking_filter_options(
    indikator_liste: List[str],
    regionen: Dict[str, List[str]],
    language: str = "DE"
) -> tuple[Optional[str], Optional[str]]:
    """
    Render filter options for country ranking.
    
    Args:
        indikator_liste: List of available indicators
        regionen: Dictionary of regions and their countries
        language: Language code for localization
    
    Returns:
        Tuple of (selected_indicator, selected_region) or (None, None)
    """
    st.markdown(f"### {get_text('filter_options_header', language)}")
    
    filter_cols = st.columns([1, 1])
    
    with filter_cols[0]:
        st.markdown('<div class="indicator-filter-container">', unsafe_allow_html=True)
        st.markdown(f"#### {get_text('filter_by_indicator', language)}")
        filter_by_indicator = st.checkbox(get_text("filter_by_indicator_checkbox", language), value=False)
        filter_indicator = None
        if filter_by_indicator:
            filter_indicator = st.selectbox(get_text("select_indicator", language), indikator_liste)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with filter_cols[1]:
        st.markdown('<div class="indicator-filter-container">', unsafe_allow_html=True)
        st.markdown(f"#### {get_text('filter_by_region', language)}")
        filter_by_region = st.checkbox(get_text("filter_by_region_checkbox", language), value=False)
        filter_region = None
        if filter_by_region:
            filter_region = st.selectbox(get_text("select_region", language), list(regionen.keys()))
        st.markdown('</div>', unsafe_allow_html=True)
    
    return filter_indicator, filter_region


def render_ranking_info(language: str = "DE") -> None:
    """
    Render information about ranking analysis.
    
    Args:
        language: Language code for localization
    """
    st.info(get_text("ranking_info", language))


def render_progress_tab(
    filtered_progress: Dict[str, Dict[str, Any]],
    filtered_details: Dict[str, List[Dict[str, Any]]],
    config: VisualizationConfig
) -> None:
    """
    Render the progress ranking tab.
    
    Args:
        filtered_progress: Filtered country progress data
        filtered_details: Filtered country details data
        config: Visualization configuration
    """
    st.markdown(f"## {get_text('progress_ranking_header', config.language)}")
    
    # Create progress ranking
    progress_ranking = create_progress_ranking(filtered_progress)
    
    if progress_ranking:
        # Bar chart for top countries with most progress
        top_progress_countries = progress_ranking[:10]  # TOP_COUNTRIES_LIMIT
        
        fig_progress = render_ranking_chart(top_progress_countries, 'progress', config)
        st.plotly_chart(fig_progress, use_container_width=True)
        
        # Detailed view of top progress
        st.markdown(f"### {get_text('progress_details_header', config.language)}")
        
        for i, country_entry in enumerate(top_progress_countries):
            country = country_entry.land
            with st.expander(f"{i+1}. {country} - {country_entry.fortschritte} {get_text('progress', config.language)} ({get_text('score', config.language)}: {country_entry.score})"):
                if country in filtered_details:
                    # Only show progress
                    progress_items = [item for item in filtered_details[country] if item['Typ'] == ChangeType.PROGRESS]
                    
                    if progress_items:
                        for item in progress_items:
                            st.markdown(f"""
                            <div class="change-item change-item-positive">
                                <strong>{get_text('indicator', config.language)}:</strong> {item['Indikator']}<br>
                                <strong>{get_text('year_label', config.language)}:</strong> {item['Jahr']}<br>
                                <strong>{get_text('change', config.language)}:</strong> {get_text('from_to', config.language, item['Von'], item['Zu'])} ({get_text('score_value', config.language, '+' + str(item['Score']))})
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(get_text("no_detailed_progress", config.language))
                else:
                    st.info(get_text("no_detailed_data", config.language))
    else:
        st.info(get_text("no_progress_found", config.language))


def render_regress_tab(
    filtered_progress: Dict[str, Dict[str, Any]],
    filtered_details: Dict[str, List[Dict[str, Any]]],
    config: VisualizationConfig
) -> None:
    """
    Render the regress ranking tab.
    
    Args:
        filtered_progress: Filtered country progress data
        filtered_details: Filtered country details data
        config: Visualization configuration
    """
    st.markdown(f"## {get_text('regress_ranking_header', config.language)}")
    
    # Create regress ranking
    regress_ranking = create_regress_ranking(filtered_progress)
    
    if regress_ranking:
        # Bar chart for top countries with regress
        top_regress_countries = regress_ranking[:10]  # TOP_COUNTRIES_LIMIT
        
        fig_regress = render_ranking_chart(top_regress_countries, 'regress', config)
        st.plotly_chart(fig_regress, use_container_width=True)
        
        # Detailed view of regress
        st.markdown(f"### {get_text('regress_details_header', config.language)}")
        
        for i, country_entry in enumerate(top_regress_countries):
            country = country_entry.land
            with st.expander(f"{i+1}. {country} - {country_entry.rueckschritte} {get_text('regress', config.language)} ({get_text('score', config.language)}: {country_entry.score})"):
                if country in filtered_details:
                    # Only show regress
                    regress_items = [item for item in filtered_details[country] if item['Typ'] == ChangeType.REGRESS]
                    
                    if regress_items:
                        for item in regress_items:
                            st.markdown(f"""
                            <div class="change-item change-item-negative">
                                <strong>{get_text('indicator', config.language)}:</strong> {item['Indikator']}<br>
                                <strong>{get_text('year_label', config.language)}:</strong> {item['Jahr']}<br>
                                <strong>{get_text('change', config.language)}:</strong> {get_text('from_to', config.language, item['Von'], item['Zu'])} ({get_text('score_value', config.language, str(item['Score']))})
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(get_text("no_detailed_regress", config.language))
                else:
                    st.info(get_text("no_detailed_data", config.language))
    else:
        st.info(get_text("no_regress_found", config.language))


def render_netto_tab(
    filtered_progress: Dict[str, Dict[str, Any]],
    filtered_details: Dict[str, List[Dict[str, Any]]],
    config: VisualizationConfig
) -> None:
    """
    Render the net change ranking tab.
    
    Args:
        filtered_progress: Filtered country progress data
        filtered_details: Filtered country details data
        config: Visualization configuration
    """
    st.markdown(f"## {get_text('netto_ranking_header', config.language)}")
    
    # Create netto ranking
    netto_ranking = create_netto_ranking(filtered_progress)
    
    if netto_ranking:
        # Split into positive and negative changes
        positive_countries, negative_countries_sorted = split_netto_ranking(netto_ranking)
        
        # Upper half: Positive changes
        st.markdown(f"### {get_text('positive_netto_title', config.language)}")
        
        if positive_countries:
            config_positive = VisualizationConfig(chart_height=DEFAULT_CHART_HEIGHT, language=config.language)
            fig_top_netto = render_ranking_chart(positive_countries, 'netto', config_positive)
            st.plotly_chart(fig_top_netto, use_container_width=True)
        else:
            st.info(get_text("no_positive_netto", config.language))
        
        # Lower half: Negative changes
        st.markdown(f"### {get_text('negative_netto_title', config.language)}")
        
        if negative_countries_sorted:
            config_negative = VisualizationConfig(chart_height=DEFAULT_CHART_HEIGHT, language=config.language)
            fig_bottom_netto = render_ranking_chart(negative_countries_sorted, 'netto', config_negative)
            st.plotly_chart(fig_bottom_netto, use_container_width=True)
        else:
            st.info(get_text("no_negative_netto", config.language))
        
        # Detailed changes for a selected country
        render_country_details_section(filtered_progress, filtered_details, config)
        
    else:
        st.info(get_text("no_netto_changes", config.language))


def render_country_details_section(
    filtered_progress: Dict[str, Dict[str, Any]],
    filtered_details: Dict[str, List[Dict[str, Any]]],
    config: VisualizationConfig
) -> None:
    """
    Render detailed changes for a selected country.
    
    Args:
        filtered_progress: Filtered country progress data
        filtered_details: Filtered country details data
        config: Visualization configuration
    """
    st.markdown(f"### {get_text('country_details_title', config.language)}")
    
    # List of all countries with changes
    countries_with_changes = get_countries_with_changes(filtered_progress)
    
    if countries_with_changes:
        selected_country = st.selectbox(get_text("select_country", config.language), countries_with_changes)
        
        if selected_country in filtered_details:
            country_data = filtered_progress[selected_country]
            changes = filtered_details[selected_country]
            
            # Statistics for selected country
            cols = st.columns(4)
            with cols[0]:
                st.metric(get_text("progress", config.language), country_data['Fortschritt'])
            with cols[1]:
                st.metric(get_text("regress", config.language), country_data['Rückschritt'])
            with cols[2]:
                netto = country_data['Fortschritt'] - country_data['Rückschritt']
                st.metric(get_text("net_count", config.language), netto)
            with cols[3]:
                st.metric(get_text("score", config.language), country_data['Score'])
            
            # Group changes by year
            changes_by_year = get_country_changes_by_year(changes)
            
            # Display changes by year
            st.markdown(f"#### {get_text('changes_by_year_title', config.language)}")
            
            for year in sorted(changes_by_year.keys()):
                year_data = changes_by_year[year]
                
                with st.expander(get_text("year_summary", config.language, year, len(year_data['Fortschritte']), len(year_data['Rückschritte']))):
                    # Display progress
                    if year_data['Fortschritte']:
                        st.markdown(f"##### {get_text('progress', config.language)}")
                        for item in year_data['Fortschritte']:
                            st.markdown(f"""
                            <div class="change-item change-item-positive">
                                <strong>{get_text('indicator', config.language)}:</strong> {item['Indikator']}<br>
                                <strong>{get_text('change', config.language)}:</strong> {get_text('from_to', config.language, item['Von'], item['Zu'])} ({get_text('score_value', config.language, '+' + str(item['Score']))})
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Display regress
                    if year_data['Rückschritte']:
                        st.markdown(f"##### {get_text('regress', config.language)}")
                        for item in year_data['Rückschritte']:
                            st.markdown(f"""
                            <div class="change-item change-item-negative">
                                <strong>{get_text('indicator', config.language)}:</strong> {item['Indikator']}<br>
                                <strong>{get_text('change', config.language)}:</strong> {get_text('from_to', config.language, item['Von'], item['Zu'])} ({get_text('score_value', config.language, str(item['Score']))})
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info(get_text("no_detailed_data", config.language, selected_country))
    else:
        st.info(get_text("no_countries_with_changes", config.language))


# =============================================================================
# MAIN API FUNCTION
# =============================================================================

def show_country_ranking(
    df_for_maps: pd.DataFrame, 
    indikator_liste: List[str], 
    regionen: Dict[str, List[str]], 
    calculate_progress: Callable, 
    calculate_change_score: Callable, 
    calculate_weighted_country_progress: Callable,
    language: str = "DE"
) -> None:
    """
    Show country ranking based on progress and regress with multilingual support.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        indikator_liste: List of indicators
        regionen: Dictionary with regional assignment of countries
        calculate_progress: Function to calculate progress and regress
        calculate_change_score: Function to calculate change scores
        calculate_weighted_country_progress: Function to calculate weighted country progress
        language: Language code for localization
    """
    st.subheader(get_text("country_ranking_progress_title", language).replace("Top 10 ", "").replace("Top-", ""))
    
    # Information about data analysis
    render_ranking_info(language)
    
    # Filter options for country ranking
    filter_indicator, filter_region = render_ranking_filter_options(indikator_liste, regionen, language)
    
    # Calculate and filter country results
    filtered_progress, filtered_details = calculate_filtered_country_results(
        df_for_maps, indikator_liste, regionen, calculate_weighted_country_progress,
        filter_indicator, filter_region, calculate_progress, calculate_change_score
    )
    
    # Create configuration
    config = VisualizationConfig(language=language)
    
    # Tabs for different ranking views
    tab_names = [
        get_text("tab_progress", language),
        get_text("tab_regress", language),
        get_text("tab_netto", language)
    ]
    ranking_tabs = st.tabs(tab_names)
    
    # Tab for Progress
    with ranking_tabs[0]:
        render_progress_tab(filtered_progress, filtered_details, config)
    
    # Tab for Regress
    with ranking_tabs[1]:
        render_regress_tab(filtered_progress, filtered_details, config)
    
    # Tab for Net Change
    with ranking_tabs[2]:
        render_netto_tab(filtered_progress, filtered_details, config)