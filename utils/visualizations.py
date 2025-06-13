"""
Main visualizations module for HerAtlas Indicators analysis with multilingual support.

This module serves as the main entry point for all visualization functions,
importing from specialized sub-modules and providing backward compatibility
with the original API while adding comprehensive multilingual support.

NEW MODULAR STRUCTURE:
- indicators_viz_multilingual.py: Text constants and localization helpers
- indicators_viz_core.py: Core data models and processing functions  
- indicators_viz_regional.py: Regional distribution visualizations
- indicators_viz_timeline.py: Timeline development visualizations
- indicators_viz_ranking_core.py: Core ranking functions and charts
- indicators_viz_ranking_ui.py: UI components for ranking displays
"""

# =============================================================================
# IMPORTS FROM SUB-MODULES
# =============================================================================

# Core functionality
from .indicators_viz_core import (
    # Data models
    IndicatorStatus, ChangeType, RegionalStats, ProgressItem, CountryProgress, 
    RankingEntry, VisualizationConfig,
    
    # Constants
    COLORS, DEFAULT_CHART_HEIGHT, TALL_CHART_HEIGHT, COMPACT_CHART_HEIGHT, 
    RANKING_CHART_HEIGHT, BASELINE_YEAR, TOP_COUNTRIES_LIMIT, TOP_INDICATORS_LIMIT,
    
    # Core processing functions
    calculate_current_data_for_year, calculate_regional_statistics, prepare_timeline_data,
    filter_country_results_by_criteria, calculate_global_development_data,
    calculate_progress_by_indicator,
    
    # Legacy compatibility
    get_current_data_for_year
)

# Multilingual support
from .indicators_viz_multilingual import (
    TEXTS, get_text, get_status_labels, get_legend_labels, get_progress_regress_labels
)

# Regional distribution
from .indicators_viz_regional import (
    render_regional_distribution_chart, render_data_processing_info, 
    render_regional_details, show_regional_distribution
)

# Timeline development  
from .indicators_viz_timeline import (
    render_timeline_chart, render_progress_regress_chart, render_global_development_chart,
    render_top_indicators_chart, render_weighted_score_explanation, render_progress_details,
    show_timeline, show_global_development, show_time_development
)

# Country ranking
from .indicators_viz_ranking_core import (
    render_ranking_chart, create_progress_ranking, create_regress_ranking, 
    create_netto_ranking, split_netto_ranking, calculate_filtered_country_results,
    get_countries_with_changes, get_country_changes_by_year
)

from .indicators_viz_ranking_ui import (
    render_ranking_filter_options, render_ranking_info, render_progress_tab,
    render_regress_tab, render_netto_tab, render_country_details_section,
    show_country_ranking
)


# =============================================================================
# BACKWARD COMPATIBILITY IMPORTS
# =============================================================================

# Import pandas and other dependencies for backward compatibility
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# MAIN API FUNCTIONS (WITH MULTILINGUAL SUPPORT)
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
    
    This is the main API function that external modules should use.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        selected_indicator: Selected indicator
        selected_year: Selected year
        regionen: Dictionary with regional assignment of countries
        language: Language code ("DE" or "EN")
    """
    # Import from regional module to avoid circular imports
    from .indicators_viz_regional import show_regional_distribution as _show_regional_distribution
    _show_regional_distribution(df_for_maps, selected_indicator, selected_year, regionen, language)


def show_time_development(
    df_for_maps: pd.DataFrame, 
    selected_indicator: str, 
    indikator_liste: List[str], 
    calculate_progress: Callable,
    language: str = "DE"
) -> None:
    """
    Show time development of an indicator with multilingual support.
    
    This is the main API function that external modules should use.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        selected_indicator: Selected indicator
        indikator_liste: List of indicators
        calculate_progress: Function to calculate progress and regress
        language: Language code ("DE" or "EN")
    """
    # Import from timeline module to avoid circular imports
    from .indicators_viz_timeline import show_time_development as _show_time_development
    _show_time_development(df_for_maps, selected_indicator, indikator_liste, calculate_progress, language)


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
    
    This is the main API function that external modules should use.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        indikator_liste: List of indicators
        regionen: Dictionary with regional assignment of countries
        calculate_progress: Function to calculate progress and regress
        calculate_change_score: Function to calculate change scores
        calculate_weighted_country_progress: Function to calculate weighted country progress
        language: Language code ("DE" or "EN")
    """
    # Import from ranking UI module to avoid circular imports
    from .indicators_viz_ranking_ui import show_country_ranking as _show_country_ranking
    _show_country_ranking(
        df_for_maps, indikator_liste, regionen, calculate_progress, 
        calculate_change_score, calculate_weighted_country_progress, language
    )


# =============================================================================
# ADDITIONAL HELPER FUNCTIONS FOR EXTERNAL USE
# =============================================================================

def get_visualization_config(language: str = "DE", **kwargs) -> VisualizationConfig:
    """
    Create a visualization configuration with language support.
    
    Args:
        language: Language code ("DE" or "EN") 
        **kwargs: Additional configuration parameters
    
    Returns:
        VisualizationConfig object with specified language
    """
    return VisualizationConfig(language=language, **kwargs)


def get_localized_status_labels(language: str = "DE") -> Dict[str, str]:
    """
    Get localized status labels for the specified language.
    
    Args:
        language: Language code ("DE" or "EN")
    
    Returns:
        Dictionary mapping status values to localized labels
    """
    return get_status_labels(language)


def get_localized_text(key: str, language: str = "DE", *args) -> str:
    """
    Get localized text for a given key.
    
    Args:
        key: Text key to look up
        language: Language code ("DE" or "EN")
        *args: Arguments for string formatting
    
    Returns:
        Localized text string
    """
    return get_text(key, language, *args)


# =============================================================================
# LEGACY SUPPORT FUNCTIONS
# =============================================================================

# These functions maintain backward compatibility with the old API

def render_data_processing_info() -> None:
    """Legacy function - now supports German only for backward compatibility."""
    render_data_processing_info("DE")


def render_weighted_score_explanation() -> None:
    """Legacy function - now supports German only for backward compatibility."""
    render_weighted_score_explanation("DE")


# =============================================================================
# MODULE METADATA
# =============================================================================

__version__ = "2.0.0"
__author__ = "HerEducation Project"
__description__ = "Multilingual visualization module for education indicators analysis"

# List of modules in the visualization system
__submodules__ = [
    "indicators_viz_multilingual",
    "indicators_viz_core", 
    "indicators_viz_regional",
    "indicators_viz_timeline",
    "indicators_viz_ranking_core",
    "indicators_viz_ranking_ui"
]

# Main API functions
__api_functions__ = [
    "show_regional_distribution",
    "show_time_development", 
    "show_country_ranking"
]

# Supported languages
__supported_languages__ = ["DE", "EN"]

# Export main functions for external use
__all__ = [
    # Main API functions
    "show_regional_distribution",
    "show_time_development",
    "show_country_ranking",
    
    # Helper functions
    "get_visualization_config",
    "get_localized_status_labels", 
    "get_localized_text",
    
    # Core data models (for advanced users)
    "VisualizationConfig",
    "IndicatorStatus",
    "ChangeType",
    
    # Legacy compatibility
    "get_current_data_for_year",
    "render_data_processing_info",
    "render_weighted_score_explanation"
]


# =============================================================================
# MODULE INITIALIZATION MESSAGE
# =============================================================================

def _print_module_info():
    """Print module information when imported (for development)."""
    if __name__ != "__main__":  # Only print in development
        print(f"📊 HerAtlas Indicators Visualization System v{__version__}")
        print(f"📁 Modular structure with {len(__submodules__)} sub-modules")
        print(f"🌍 Multilingual support: {', '.join(__supported_languages__)}")
        print(f"🔧 Main API functions: {len(__api_functions__)} available")

# Uncomment for development debugging:
# _print_module_info()