"""
Core ranking visualization functions for HerAtlas Indicators.

This module provides the core ranking calculation and chart rendering functions
for country ranking analysis with multilingual support.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Callable

from .indicators_viz_core import (
    RankingEntry, VisualizationConfig, ChangeType,
    filter_country_results_by_criteria, RANKING_CHART_HEIGHT, DEFAULT_CHART_HEIGHT, TOP_COUNTRIES_LIMIT
)
from .indicators_viz_multilingual import get_text, get_progress_regress_labels


# =============================================================================
# RANKING CHART RENDERING FUNCTIONS
# =============================================================================

def render_ranking_chart(
    ranking_data: List[RankingEntry],
    chart_type: str,
    config: VisualizationConfig = None
) -> go.Figure:
    """
    Create ranking chart for countries.
    
    Args:
        ranking_data: List of ranking entries
        chart_type: Type of chart ('progress', 'regress', 'netto')
        config: Visualization configuration
    
    Returns:
        Plotly figure object
    """
    if config is None:
        config = VisualizationConfig()
    
    if not ranking_data:
        return go.Figure()
    
    fig = go.Figure()
    
    countries = [entry.land for entry in ranking_data]
    
    if chart_type == 'progress':
        values = [entry.fortschritte for entry in ranking_data]
        scores = [entry.score for entry in ranking_data]
        title = get_text("country_ranking_progress_title", config.language)
        primary_color = config.color_scheme['progress']
        secondary_color = config.color_scheme['progress_alt']
        
        progress_regress_labels = get_progress_regress_labels(config.language)
        
        fig.add_trace(go.Bar(
            y=countries,
            x=values,
            orientation='h',
            marker_color=primary_color,
            name=f'{get_text("number_label", config.language)} {progress_regress_labels["progress"]}'
        ))
        
        fig.add_trace(go.Bar(
            y=countries,
            x=scores,
            orientation='h',
            marker_color=secondary_color,
            name=get_text("score", config.language)
        ))
        
    elif chart_type == 'regress':
        values = [entry.rueckschritte for entry in ranking_data]
        scores = [entry.score for entry in ranking_data]
        title = get_text("country_ranking_regress_title", config.language)
        primary_color = config.color_scheme['regress']
        secondary_color = config.color_scheme['regress_alt']
        
        progress_regress_labels = get_progress_regress_labels(config.language)
        
        fig.add_trace(go.Bar(
            y=countries,
            x=values,
            orientation='h',
            marker_color=primary_color,
            name=f'{get_text("number_label", config.language)} {progress_regress_labels["regress"]}'
        ))
        
        fig.add_trace(go.Bar(
            y=countries,
            x=scores,
            orientation='h',
            marker_color=secondary_color,
            name=get_text("score", config.language)
        ))
        
    elif chart_type == 'netto':
        scores = [entry.score for entry in ranking_data]
        title = get_text("country_ranking_netto_title", config.language)
        
        # Use different colors for positive and negative scores
        colors = []
        for score in scores:
            if score >= 0:
                colors.append(config.color_scheme['progress'])
            else:
                colors.append(config.color_scheme['regress'])
        
        fig.add_trace(go.Bar(
            y=countries,
            x=scores,
            orientation='h',
            marker_color=colors,
            name=get_text("score", config.language)
        ))
    
    fig.update_layout(
        title=title,
        yaxis={'categoryorder': 'total ascending' if chart_type != 'netto' else 'total descending'},
        xaxis_title=get_text("score_label", config.language),
        barmode='group',
        height=RANKING_CHART_HEIGHT
    )
    
    return fig


# =============================================================================
# RANKING DATA PROCESSING FUNCTIONS
# =============================================================================

def create_progress_ranking(
    filtered_progress: Dict[str, Dict[str, Any]]
) -> List[RankingEntry]:
    """
    Create ranking by progress count.
    
    Args:
        filtered_progress: Filtered country progress data
    
    Returns:
        List of ranking entries sorted by progress
    """
    progress_ranking = []
    for country, data in filtered_progress.items():
        if data['Fortschritt'] > 0:
            progress_ranking.append(RankingEntry(
                land=country,
                fortschritte=data['Fortschritt'],
                rueckschritte=data['Rückschritt'],
                score=data['Score']
            ))
    
    # Sort by score (descending)
    progress_ranking.sort(key=lambda x: x.score, reverse=True)
    return progress_ranking


def create_regress_ranking(
    filtered_progress: Dict[str, Dict[str, Any]]
) -> List[RankingEntry]:
    """
    Create ranking by regress count.
    
    Args:
        filtered_progress: Filtered country progress data
    
    Returns:
        List of ranking entries sorted by regress
    """
    regress_ranking = []
    for country, data in filtered_progress.items():
        if data['Rückschritt'] > 0:
            regress_ranking.append(RankingEntry(
                land=country,
                fortschritte=data['Fortschritt'],
                rueckschritte=data['Rückschritt'],
                score=abs(data['Score']) if data['Score'] < 0 else 0  # Absolute value of negative score
            ))
    
    # Sort by score (descending)
    regress_ranking.sort(key=lambda x: x.score, reverse=True)
    return regress_ranking


def create_netto_ranking(
    filtered_progress: Dict[str, Dict[str, Any]]
) -> List[RankingEntry]:
    """
    Create ranking by net change.
    
    Args:
        filtered_progress: Filtered country progress data
    
    Returns:
        List of ranking entries sorted by net score
    """
    netto_ranking = []
    for country, data in filtered_progress.items():
        if data['Fortschritt'] > 0 or data['Rückschritt'] > 0:
            netto_ranking.append(RankingEntry(
                land=country,
                fortschritte=data['Fortschritt'],
                rueckschritte=data['Rückschritt'],
                score=data['Score'],
                netto_anzahl=data['Fortschritt'] - data['Rückschritt']
            ))
    
    # Sort by score (descending)
    netto_ranking.sort(key=lambda x: x.score, reverse=True)
    return netto_ranking


def split_netto_ranking(
    netto_ranking: List[RankingEntry]
) -> tuple[List[RankingEntry], List[RankingEntry]]:
    """
    Split netto ranking into positive and negative changes.
    
    Args:
        netto_ranking: List of netto ranking entries
    
    Returns:
        Tuple of (positive_countries, negative_countries)
    """
    positive_countries = [c for c in netto_ranking if c.score > 0][:TOP_COUNTRIES_LIMIT]
    negative_countries = [c for c in netto_ranking if c.score < 0][-TOP_COUNTRIES_LIMIT:]
    
    # For negative countries, reverse sort for better display
    negative_countries_sorted = sorted(negative_countries, key=lambda x: x.score)
    
    return positive_countries, negative_countries_sorted


def calculate_filtered_country_results(
    df_for_maps: pd.DataFrame,
    indikator_liste: List[str],
    regionen: Dict[str, List[str]],
    calculate_weighted_country_progress_func: Callable,
    filter_indicator: Optional[str] = None,
    filter_region: Optional[str] = None,
    calculate_progress_func: Optional[Callable] = None,
    calculate_change_score_func: Optional[Callable] = None
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Calculate and filter country results based on selected criteria.
    
    Args:
        df_for_maps: DataFrame with data
        indikator_liste: List of indicators
        regionen: Dictionary of regions
        calculate_weighted_country_progress_func: Function to calculate weighted progress
        filter_indicator: Optional indicator filter
        filter_region: Optional region filter
        calculate_progress_func: Optional progress calculation function
        calculate_change_score_func: Optional change score calculation function
    
    Returns:
        Tuple of (filtered_progress, filtered_details)
    """
    # Calculate country results
    country_progress, country_details = calculate_weighted_country_progress_func(df_for_maps, indikator_liste)
    
    # Apply filters if any are selected
    if filter_indicator or filter_region:
        if calculate_progress_func and calculate_change_score_func:
            filtered_progress, filtered_details = filter_country_results_by_criteria(
                country_progress, country_details, filter_indicator, filter_region, 
                regionen, df_for_maps, calculate_progress_func, calculate_change_score_func
            )
        else:
            # Simple region filtering without recalculation
            filtered_progress = country_progress.copy()
            filtered_details = country_details.copy()
            
            if filter_region:
                region_countries = regionen[filter_region]
                filtered_progress = {country: data for country, data in filtered_progress.items() 
                                   if country in region_countries}
                filtered_details = {country: details for country, details in filtered_details.items() 
                                  if country in region_countries}
    else:
        filtered_progress = country_progress
        filtered_details = country_details
    
    return filtered_progress, filtered_details


def get_countries_with_changes(
    filtered_progress: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Get list of countries that have changes (progress or regress).
    
    Args:
        filtered_progress: Filtered country progress data
    
    Returns:
        Sorted list of country names with changes
    """
    return sorted([
        country for country, data in filtered_progress.items() 
        if data['Fortschritt'] > 0 or data['Rückschritt'] > 0
    ])


def get_country_changes_by_year(
    changes: List[Dict[str, Any]]
) -> Dict[int, Dict[str, List[Dict[str, Any]]]]:
    """
    Group country changes by year.
    
    Args:
        changes: List of change items for a country
    
    Returns:
        Dictionary mapping years to changes grouped by type
    """
    changes_by_year = {}
    for item in changes:
        year = item['Jahr']
        if year not in changes_by_year:
            changes_by_year[year] = {'Fortschritte': [], 'Rückschritte': []}
        
        if item['Typ'] == ChangeType.PROGRESS:
            changes_by_year[year]['Fortschritte'].append(item)
        elif item['Typ'] == ChangeType.REGRESS:
            changes_by_year[year]['Rückschritte'].append(item)
    
    return changes_by_year