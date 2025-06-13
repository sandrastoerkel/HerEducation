"""
Regional distribution visualization functions for HerAtlas Indicators.

This module provides functions for creating and displaying regional distribution
charts and detailed regional breakdowns with multilingual support.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List

from .indicators_viz_core import (
    RegionalStats, VisualizationConfig, IndicatorStatus,
    calculate_current_data_for_year, calculate_regional_statistics,
    DEFAULT_CHART_HEIGHT, TALL_CHART_HEIGHT
)
from .indicators_viz_multilingual import get_text, get_legend_labels


# =============================================================================
# CHART RENDERING FUNCTIONS
# =============================================================================

def render_regional_distribution_chart(
    regional_stats: Dict[str, RegionalStats],
    indicator_name: str,
    year: int,
    config: VisualizationConfig = None
) -> go.Figure:
    """
    Create regional distribution bar chart.
    
    Args:
        regional_stats: Regional statistics dictionary
        indicator_name: Name of the indicator
        year: Year for the chart title
        config: Visualization configuration
    
    Returns:
        Plotly figure object
    """
    if config is None:
        config = VisualizationConfig()
    
    # Get localized labels
    legend_labels = get_legend_labels(config.language)
    
    # Prepare data for chart
    regions = list(regional_stats.keys())
    yes_percentages = [regional_stats[r].yes_percent for r in regions]
    partially_percentages = [regional_stats[r].partially_percent for r in regions]
    no_percentages = [regional_stats[r].no_percent for r in regions]
    
    # Create stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=legend_labels['Yes'],
        x=regions,
        y=yes_percentages,
        marker_color=config.color_scheme[IndicatorStatus.YES],
        text=[f"{p:.1f}%" for p in yes_percentages] if config.show_percentages else None,
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name=legend_labels['Partially'],
        x=regions,
        y=partially_percentages,
        marker_color=config.color_scheme[IndicatorStatus.PARTIALLY],
        text=[f"{p:.1f}%" for p in partially_percentages] if config.show_percentages else None,
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name=legend_labels['No'],
        x=regions,
        y=no_percentages,
        marker_color=config.color_scheme[IndicatorStatus.NO],
        text=[f"{p:.1f}%" for p in no_percentages] if config.show_percentages else None,
        textposition='auto'
    ))
    
    fig.update_layout(
        title=get_text("regional_distribution_title", config.language, indicator_name, year),
        xaxis_title=get_text("region_label", config.language),
        yaxis_title=get_text("percent_label", config.language),
        barmode='stack',
        height=config.chart_height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_data_processing_info(language: str = "DE") -> None:
    """
    Render information about data processing logic.
    
    Args:
        language: Language code for localization
    """
    st.info(get_text("data_processing_info", language))


def render_regional_details(
    regional_data: pd.DataFrame,
    regionen: Dict[str, List[str]],
    language: str = "DE"
) -> None:
    """
    Render detailed regional breakdown with expandable sections.
    
    Args:
        regional_data: DataFrame with regional data
        regionen: Dictionary mapping regions to countries
        language: Language code for localization
    """
    st.subheader(get_text("regional_details_header", language))
    
    # Get localized status labels
    legend_labels = get_legend_labels(language)
    
    for region, countries in regionen.items():
        with st.expander(get_text("region_detail_view", language, region)):
            region_df = regional_data[regional_data['Land'].isin(countries)]
            
            if not region_df.empty:
                # Calculate statistics for the region
                total = len(region_df)
                yes = len(region_df[region_df['Result_Grouped'] == IndicatorStatus.YES])
                partially = len(region_df[region_df['Result_Grouped'] == IndicatorStatus.PARTIALLY])
                no = len(region_df[region_df['Result_Grouped'] == IndicatorStatus.NO])
                
                # Display statistics
                stat_cols = st.columns(4)
                with stat_cols[0]:
                    st.metric(get_text("total_countries", language), total)
                with stat_cols[1]:
                    st.metric(legend_labels['Yes'], yes, f"{yes/total*100:.1f}%" if total > 0 else "0%")
                with stat_cols[2]:
                    st.metric(legend_labels['Partially'], partially, f"{partially/total*100:.1f}%" if total > 0 else "0%")
                with stat_cols[3]:
                    st.metric(legend_labels['No'], no, f"{no/total*100:.1f}%" if total > 0 else "0%")
                
                # Country lists by status
                yes_countries = region_df[region_df['Result_Grouped'] == IndicatorStatus.YES]['Land'].tolist()
                partially_countries = region_df[region_df['Result_Grouped'] == IndicatorStatus.PARTIALLY]['Land'].tolist()
                no_countries = region_df[region_df['Result_Grouped'] == IndicatorStatus.NO]['Land'].tolist()
                
                st.markdown(f"##### {get_text('countries_with_yes', language)}")
                st.markdown(", ".join(sorted(yes_countries)) if yes_countries else get_text("no_countries_found", language))
                
                st.markdown(f"##### {get_text('countries_with_partially', language)}")
                st.markdown(", ".join(sorted(partially_countries)) if partially_countries else get_text("no_countries_found", language))
                
                st.markdown(f"##### {get_text('countries_with_no', language)}")
                st.markdown(", ".join(sorted(no_countries)) if no_countries else get_text("no_countries_found", language))
            else:
                st.info(get_text("no_data_available", language, region))


# =============================================================================
# MAIN API FUNCTION
# =============================================================================

def show_regional_distribution(
    df_for_maps: pd.DataFrame, 
    selected_indicator: str, 
    selected_year: int, 
    regionen: Dict[str, List[str]],
    language: str = "DE" 
) -> None:
    """
    Show regional distribution of an indicator with multilingual support.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        selected_indicator: Selected indicator
        selected_year: Selected year
        regionen: Dictionary with regional assignment of countries
        language: Language code for localization
    """
    # Render information about data processing
    render_data_processing_info(language)
    
    # Calculate data for selected indicator and year
    regional_data = calculate_current_data_for_year(df_for_maps, selected_indicator, selected_year)
    
    if regional_data.empty:
        st.warning(get_text("no_data_available", language, f"{selected_indicator} ({selected_year})"))
        return
    
    # Calculate regional statistics
    regional_stats = calculate_regional_statistics(regional_data, regionen)
    
    # Create and display chart
    config = VisualizationConfig(chart_height=TALL_CHART_HEIGHT, language=language)
    fig = render_regional_distribution_chart(regional_stats, selected_indicator, selected_year, config)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display detailed regional breakdown
    render_regional_details(regional_data, regionen, language)