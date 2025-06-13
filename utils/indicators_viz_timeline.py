"""
Timeline development visualization functions for HerAtlas Indicators.

This module provides functions for creating timeline charts, progress/regress analysis,
and global development visualizations with multilingual support.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Callable

from .indicators_viz_core import (
    ProgressItem, VisualizationConfig, IndicatorStatus, ChangeType,
    prepare_timeline_data, calculate_global_development_data, calculate_progress_by_indicator,
    DEFAULT_CHART_HEIGHT, TALL_CHART_HEIGHT, COMPACT_CHART_HEIGHT, TOP_INDICATORS_LIMIT
)
from .indicators_viz_multilingual import get_text, get_legend_labels, get_progress_regress_labels


# =============================================================================
# CHART RENDERING FUNCTIONS
# =============================================================================

def render_timeline_chart(
    years: List[int],
    yes_data: List[float],
    partially_data: List[float],
    no_data: List[float],
    indicator_name: str,
    config: VisualizationConfig = None
) -> go.Figure:
    """
    Create timeline chart for indicator development.
    
    Args:
        years: List of years
        yes_data: Percentages for "Yes" status
        partially_data: Percentages for "Partially" status  
        no_data: Percentages for "No" status
        indicator_name: Name of the indicator
        config: Visualization configuration
    
    Returns:
        Plotly figure object
    """
    if config is None:
        config = VisualizationConfig()
    
    # Get localized labels
    legend_labels = get_legend_labels(config.language)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=yes_data,
        mode='lines+markers',
        name=legend_labels['Yes'],
        line=dict(color=config.color_scheme[IndicatorStatus.YES], width=3),
        marker=dict(size=8, symbol='circle')
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=partially_data,
        mode='lines+markers',
        name=legend_labels['Partially'],
        line=dict(color=config.color_scheme[IndicatorStatus.PARTIALLY], width=3),
        marker=dict(size=8, symbol='square')
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=no_data,
        mode='lines+markers',
        name=legend_labels['No'],
        line=dict(color=config.color_scheme[IndicatorStatus.NO], width=3),
        marker=dict(size=8, symbol='diamond')
    ))
    
    fig.update_layout(
        title=get_text("timeline_title", config.language, indicator_name),
        xaxis_title=get_text("year_label", config.language),
        yaxis_title=get_text("percent_label", config.language),
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=config.chart_height
    )
    
    return fig


def render_progress_regress_chart(
    progress_count: int,
    regress_count: int,
    config: VisualizationConfig = None
) -> go.Figure:
    """
    Create chart showing progress and regress counts.
    
    Args:
        progress_count: Number of progress items
        regress_count: Number of regress items
        config: Visualization configuration
    
    Returns:
        Plotly figure object
    """
    if config is None:
        config = VisualizationConfig()
    
    # Get localized labels
    progress_regress_labels = get_progress_regress_labels(config.language)
    
    fig = go.Figure(data=[
        go.Bar(
            name=progress_regress_labels['progress'],
            x=[progress_regress_labels['progress']],
            y=[progress_count],
            marker_color=config.color_scheme['progress'],
            text=[progress_count],
            textposition='auto'
        ),
        go.Bar(
            name=progress_regress_labels['regress'],
            x=[progress_regress_labels['regress']],
            y=[regress_count],
            marker_color=config.color_scheme['regress'],
            text=[regress_count],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=get_text("progress_regress_title", config.language),
        yaxis_title=get_text("count_label", config.language),
        height=COMPACT_CHART_HEIGHT
    )
    
    return fig


def render_global_development_chart(
    year_labels: List[str],
    global_progress: List[int],
    global_regress: List[int],
    config: VisualizationConfig = None
) -> go.Figure:
    """
    Create global development chart across all indicators.
    
    Args:
        year_labels: List of year labels
        global_progress: Progress counts by year
        global_regress: Regress counts by year
        config: Visualization configuration
    
    Returns:
        Plotly figure object
    """
    if config is None:
        config = VisualizationConfig()
    
    # Get localized labels
    progress_regress_labels = get_progress_regress_labels(config.language)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=progress_regress_labels['progress'],
        x=year_labels,
        y=global_progress,
        marker_color=config.color_scheme['progress'],
        text=global_progress,
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name=progress_regress_labels['regress'],
        x=year_labels,
        y=global_regress,
        marker_color=config.color_scheme['regress'],
        text=global_regress,
        textposition='auto'
    ))
    
    fig.update_layout(
        title=get_text("global_development_title", config.language),
        xaxis_title=get_text("year_label", config.language),
        yaxis_title=get_text("changes_label", config.language),
        barmode='group',
        height=config.chart_height
    )
    
    return fig


def render_top_indicators_chart(
    progress_by_indicator: List[Dict],
    config: VisualizationConfig = None
) -> go.Figure:
    """
    Create chart showing top indicators with most progress.
    
    Args:
        progress_by_indicator: List of indicator progress statistics
        config: Visualization configuration
    
    Returns:
        Plotly figure object
    """
    if config is None:
        config = VisualizationConfig()
    
    # Get localized labels
    progress_regress_labels = get_progress_regress_labels(config.language)
    
    # Get top indicators
    top_indicators = [ind['Indikator'] for ind in progress_by_indicator[:TOP_INDICATORS_LIMIT]]
    top_progress = [ind['Fortschritte'] for ind in progress_by_indicator[:TOP_INDICATORS_LIMIT]]
    top_regress = [ind['Rückschritte'] for ind in progress_by_indicator[:TOP_INDICATORS_LIMIT]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=progress_regress_labels['progress'],
        x=top_indicators,
        y=top_progress,
        marker_color=config.color_scheme['progress'],
        text=top_progress,
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name=progress_regress_labels['regress'],
        x=top_indicators,
        y=top_regress,
        marker_color=config.color_scheme['regress'],
        text=top_regress,
        textposition='auto'
    ))
    
    fig.update_layout(
        title=get_text("top_indicators_title", config.language),
        xaxis_title=get_text("indicator_label", config.language),
        yaxis_title=get_text("number_label", config.language),
        xaxis={'categoryorder':'total descending'},
        barmode='group',
        height=TALL_CHART_HEIGHT
    )
    
    return fig


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================

def render_weighted_score_explanation(language: str = "DE") -> None:
    """
    Render explanation of weighted scoring system.
    
    Args:
        language: Language code for localization
    """
    st.markdown(get_text("weighted_score_explanation", language))


def render_progress_details(
    progress_list: List[ProgressItem],
    language: str = "DE"
) -> None:
    """
    Render detailed progress and regress information.
    
    Args:
        progress_list: List of progress items to display
        language: Language code for localization
    """
    if not progress_list:
        st.info(get_text("no_detailed_progress_regress", language))
        return
    
    st.subheader(get_text("progress_details_header", language))
    
    # Group by progress and regress
    fortschritte = [p for p in progress_list if p.typ == ChangeType.PROGRESS]
    rueckschritte = [p for p in progress_list if p.typ == ChangeType.REGRESS]
    
    # Display progress
    if fortschritte:
        st.markdown('<div class="development-category">📈 ' + get_text("progress", language) + '</div>', unsafe_allow_html=True)
        for item in fortschritte:
            st.markdown(f"""
            <div class="development-card">
                <h4>{item.land}</h4>
                <p>{get_text("year_label", language)} {item.jahr}: {get_text("from_to", language, item.von, item.zu)}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Display regress
    if rueckschritte:
        st.markdown('<div class="development-category">📉 ' + get_text("regress", language) + '</div>', unsafe_allow_html=True)
        for item in rueckschritte:
            st.markdown(f"""
            <div class="development-card">
                <h4>{item.land}</h4>
                <p>{get_text("year_label", language)} {item.jahr}: {get_text("from_to", language, item.von, item.zu)}</p>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def show_timeline(
    df_for_maps: pd.DataFrame, 
    indicator_name: str, 
    calculate_progress: Callable,
    language: str = "DE"
) -> None:
    """
    Visualize timeline development of an indicator.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        indicator_name: Name of the indicator
        calculate_progress: Function to calculate progress and regress
        language: Language code for localization
    """
    # Get data for selected indicator
    time_data = df_for_maps[df_for_maps['Indikator'] == indicator_name]
    
    if time_data.empty:
        st.info(get_text("no_timeline_data", language, indicator_name))
        return
    
    # Prepare timeline data
    years, yes_data, partially_data, no_data = prepare_timeline_data(time_data)
    
    # Create and display timeline chart
    config = VisualizationConfig(language=language)
    fig = render_timeline_chart(years, yes_data, partially_data, no_data, indicator_name, config)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed progress and regress
    progress_count, regress_count, progress_list = calculate_progress(df_for_maps, indicator_name)
    
    # Progress and regress chart
    if progress_count > 0 or regress_count > 0:
        fig_progress = render_progress_regress_chart(progress_count, regress_count, config)
        st.plotly_chart(fig_progress, use_container_width=True)

        # Explanation of weighted score
        render_weighted_score_explanation(language)
        
        # Detailed list of progress and regress
        if progress_list:
            # Convert to ProgressItem objects for consistent handling
            progress_items = []
            for item in progress_list:
                progress_items.append(ProgressItem(
                    land=item['Land'],
                    indikator=item.get('Indikator', indicator_name),
                    jahr=item['Jahr'],
                    von=item['Von'],
                    zu=item['Zu'],
                    typ=item['Typ']
                ))
            
            render_progress_details(progress_items, language)
        else:
            st.info(get_text("no_detailed_progress_regress", language))


def show_global_development(
    df_for_maps: pd.DataFrame, 
    indikator_liste: List[str], 
    calculate_progress: Callable,
    language: str = "DE"
) -> None:
    """
    Show global development of all indicators.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        indikator_liste: List of indicators
        calculate_progress: Function to calculate progress and regress
        language: Language code for localization
    """
    st.markdown(f"### {get_text('global_development_header', language)}")
    
    # Calculate global development data
    year_labels, global_progress, global_regress = calculate_global_development_data(df_for_maps, indikator_liste)
    
    # Create global progress chart
    config = VisualizationConfig(language=language)
    fig_global = render_global_development_chart(year_labels, global_progress, global_regress, config)
    st.plotly_chart(fig_global, use_container_width=True)
    
    # Calculate progress by indicator
    progress_by_indicator = calculate_progress_by_indicator(df_for_maps, indikator_liste, calculate_progress)
    
    # Top indicators with most progress
    st.markdown(f"### {get_text('top_indicators_header', language)}")
    
    fig_top = render_top_indicators_chart(progress_by_indicator, config)
    st.plotly_chart(fig_top, use_container_width=True)


def show_time_development(
    df_for_maps: pd.DataFrame, 
    selected_indicator: str, 
    indikator_liste: List[str], 
    calculate_progress: Callable,
    language: str = "DE"
) -> None:
    """
    Show time development of an indicator with multilingual support.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        selected_indicator: Selected indicator
        indikator_liste: List of indicators
        calculate_progress: Function to calculate progress and regress
        language: Language code for localization
    """
    st.subheader(get_text("timeline_development_header", language))
    
    # Timeline development of selected indicator
    show_timeline(df_for_maps, selected_indicator, calculate_progress, language)
    
    # Global development of all indicators
    show_global_development(df_for_maps, indikator_liste, calculate_progress, language)