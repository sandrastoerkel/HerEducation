"""
Core functions and data models for HerAtlas Indicators visualization.

This module provides the fundamental data structures, enums, and core processing 
functions used across all indicator visualization components.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class IndicatorStatus(str, Enum):
    """Standard indicator status values."""
    YES = "Yes"
    PARTIALLY = "Partially"
    NO = "No"


class ChangeType(str, Enum):
    """Types of status changes."""
    PROGRESS = "Fortschritt"
    REGRESS = "Rückschritt"


# Color schemes for consistent visualization
COLORS = {
    IndicatorStatus.YES: 'rgba(80, 200, 120, 0.8)',
    IndicatorStatus.PARTIALLY: 'rgba(255, 165, 0, 0.8)', 
    IndicatorStatus.NO: 'rgba(200, 0, 0, 0.8)',
    'progress': 'rgba(80, 200, 120, 0.8)',
    'regress': 'rgba(200, 0, 0, 0.8)',
    'progress_alt': 'rgba(50, 150, 80, 0.6)',
    'regress_alt': 'rgba(150, 0, 0, 0.6)'
}

# Chart configuration
DEFAULT_CHART_HEIGHT = 400
TALL_CHART_HEIGHT = 500
COMPACT_CHART_HEIGHT = 300
RANKING_CHART_HEIGHT = 500

# Data processing constants
BASELINE_YEAR = 2019
TOP_COUNTRIES_LIMIT = 10
TOP_INDICATORS_LIMIT = 5


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class RegionalStats:
    """Statistics for a specific region."""
    total: int
    yes: int
    partially: int
    no: int
    yes_percent: float
    partially_percent: float
    no_percent: float


@dataclass
class ProgressItem:
    """Represents a single progress or regress item."""
    land: str
    indikator: str
    jahr: int
    von: str  # from status
    zu: str   # to status
    typ: str  # ChangeType
    score: int = 0


@dataclass
class CountryProgress:
    """Progress statistics for a country."""
    fortschritt: int
    rueckschritt: int
    score: int


@dataclass
class RankingEntry:
    """Entry for country ranking displays."""
    land: str
    fortschritte: int
    rueckschritte: int
    score: int
    netto_anzahl: int = 0


@dataclass
class VisualizationConfig:
    """Configuration for visualization rendering."""
    chart_height: int = DEFAULT_CHART_HEIGHT
    show_percentages: bool = True
    use_container_width: bool = True
    color_scheme: Dict[str, str] = None
    language: str = "DE"
    
    def __post_init__(self):
        if self.color_scheme is None:
            self.color_scheme = COLORS


# =============================================================================
# CORE DATA PROCESSING FUNCTIONS
# =============================================================================

def calculate_current_data_for_year(
    df_for_maps: pd.DataFrame, 
    indicator_name: str, 
    target_year: int
) -> pd.DataFrame:
    """
    Calculate current status for each indicator/country based on baseline and subsequent changes.
    
    Args:
        df_for_maps: Filtered DataFrame with the data
        indicator_name: Name of the indicator
        target_year: Target year for calculation
    
    Returns:
        DataFrame with current status for each country
    """
    # Filter data for selected indicator
    indicator_data = df_for_maps[df_for_maps['Indikator'] == indicator_name].copy()
    
    if indicator_data.empty:
        return pd.DataFrame()
    
    # Determine countries and years
    all_countries = indicator_data['Land'].unique()
    all_years = sorted(indicator_data['Jahr'].unique())
    
    # If target year is not in data
    if target_year not in all_years:
        return pd.DataFrame()
    
    # Prepare result data
    result_data = []
    
    # Calculate data for each country
    for country in all_countries:
        country_data = indicator_data[indicator_data['Land'] == country].sort_values('Jahr')
        
        # Get baseline from 2019
        baseline_data = country_data[country_data['Jahr'] == BASELINE_YEAR]
        if baseline_data.empty:
            continue  # Skip if no baseline for this country
        
        # Track latest status for each year up to target year
        latest_status = baseline_data.iloc[0].copy()
        
        # Only consider changes after baseline up to target year
        changes_after_baseline = country_data[
            (country_data['Jahr'] > BASELINE_YEAR) & 
            (country_data['Jahr'] <= target_year)
        ]
        
        for _, row in changes_after_baseline.iterrows():
            # Update status
            latest_status = row
        
        # Update year for result display
        latest_status_dict = latest_status.to_dict()
        latest_status_dict['Jahr'] = target_year
        
        result_data.append(latest_status_dict)
    
    # Create result DataFrame
    return pd.DataFrame(result_data) if result_data else pd.DataFrame()


def calculate_regional_statistics(
    regional_data: pd.DataFrame, 
    regionen: Dict[str, List[str]]
) -> Dict[str, RegionalStats]:
    """
    Calculate regional statistics from country data.
    
    Args:
        regional_data: DataFrame with country data
        regionen: Dictionary mapping regions to country lists
    
    Returns:
        Dictionary mapping region names to RegionalStats objects
    """
    regional_stats = {}
    
    for region, countries in regionen.items():
        region_df = regional_data[regional_data['Land'].isin(countries)]
        total = len(region_df)
        
        if total > 0:
            yes = len(region_df[region_df['Result_Grouped'] == IndicatorStatus.YES])
            partially = len(region_df[region_df['Result_Grouped'] == IndicatorStatus.PARTIALLY])
            no = len(region_df[region_df['Result_Grouped'] == IndicatorStatus.NO])
            
            regional_stats[region] = RegionalStats(
                total=total,
                yes=yes,
                partially=partially,
                no=no,
                yes_percent=yes / total * 100,
                partially_percent=partially / total * 100,
                no_percent=no / total * 100
            )
        else:
            regional_stats[region] = RegionalStats(
                total=0, yes=0, partially=0, no=0,
                yes_percent=0, partially_percent=0, no_percent=0
            )
    
    return regional_stats


def prepare_timeline_data(
    time_data: pd.DataFrame
) -> Tuple[List[int], List[float], List[float], List[float]]:
    """
    Prepare data for timeline visualization.
    
    Args:
        time_data: Time series data for an indicator
    
    Returns:
        Tuple of (years, yes_percentages, partially_percentages, no_percentages)
    """
    years = sorted(time_data['Jahr'].unique())
    yes_data = []
    partially_data = []
    no_data = []
    
    for year in years:
        year_data = time_data[time_data['Jahr'] == year]
        total = len(year_data)
        
        if total > 0:
            yes_count = len(year_data[year_data['Result_Grouped'] == IndicatorStatus.YES])
            partially_count = len(year_data[year_data['Result_Grouped'] == IndicatorStatus.PARTIALLY])
            no_count = len(year_data[year_data['Result_Grouped'] == IndicatorStatus.NO])
            
            yes_data.append(yes_count / total * 100)
            partially_data.append(partially_count / total * 100)
            no_data.append(no_count / total * 100)
        else:
            yes_data.append(0)
            partially_data.append(0)
            no_data.append(0)
    
    return years, yes_data, partially_data, no_data


def filter_country_results_by_criteria(
    country_progress: Dict[str, Dict[str, Any]],
    country_details: Dict[str, List[Dict[str, Any]]],
    filter_indicator: Optional[str],
    filter_region: Optional[str],
    regionen: Dict[str, List[str]],
    df_for_maps: pd.DataFrame,
    calculate_progress_func,
    calculate_change_score_func
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Filter country results based on selected criteria.
    
    Args:
        country_progress: Original country progress data
        country_details: Original country details data
        filter_indicator: Selected indicator filter (None if no filter)
        filter_region: Selected region filter (None if no filter)
        regionen: Dictionary mapping regions to countries
        df_for_maps: DataFrame with data
        calculate_progress_func: Function to calculate progress
        calculate_change_score_func: Function to calculate change scores
    
    Returns:
        Tuple of (filtered_progress, filtered_details)
    """
    filtered_progress = country_progress.copy()
    filtered_details = country_details.copy()
    
    # Filter by indicator if selected
    if filter_indicator:
        # Calculate new data only for selected indicator
        filtered_progress = {}
        filtered_details = {}
        
        # Calculate progress and regress for each indicator
        _, _, progress_list = calculate_progress_func(df_for_maps, filter_indicator)
        
        for item in progress_list:
            country = item['Land']
            change_type = item['Typ']
            from_status = item['Von']
            to_status = item['Zu']
            
            # Calculate score value of change
            score = calculate_change_score_func(from_status, to_status)
            
            # Initialize country in dictionary if not present
            if country not in filtered_progress:
                filtered_progress[country] = {
                    'Fortschritt': 0,
                    'Rückschritt': 0,
                    'Score': 0
                }
                filtered_details[country] = []
            
            # Count progress or regress and update score value
            if score > 0:
                filtered_progress[country]['Fortschritt'] += 1
                filtered_progress[country]['Score'] += score
            elif score < 0:
                filtered_progress[country]['Rückschritt'] += 1
                filtered_progress[country]['Score'] += score
            
            # Store details of change
            item['Score'] = score
            filtered_details[country].append(item)
    
    # Filter by region if selected
    if filter_region:
        region_countries = regionen[filter_region]
        
        # Keep only countries from selected region
        filtered_progress = {country: data for country, data in filtered_progress.items() 
                           if country in region_countries}
        filtered_details = {country: details for country, details in filtered_details.items() 
                          if country in region_countries}
    
    return filtered_progress, filtered_details


def calculate_global_development_data(
    df_for_maps: pd.DataFrame, 
    indikator_liste: List[str]
) -> Tuple[List[str], List[int], List[int]]:
    """
    Calculate global development data across all indicators.
    
    Args:
        df_for_maps: DataFrame with data
        indikator_liste: List of indicators
    
    Returns:
        Tuple of (year_labels, global_progress, global_regress)
    """
    # Calculate global development for all indicators
    all_indicators_data = df_for_maps.copy()
    years = sorted(all_indicators_data['Jahr'].unique())
    
    # Initialize arrays for years
    global_progress = []
    global_regress = []
    year_labels = []
    
    # For all indicators and countries, determine status for each year
    complete_status = {}  # {(Land, Indikator): {Jahr: Status}}
    
    # For each indicator
    for indicator in indikator_liste:
        indicator_data = all_indicators_data[all_indicators_data['Indikator'] == indicator]
        
        # For each country that has data for this indicator
        for country in indicator_data['Land'].unique():
            country_data = indicator_data[indicator_data['Land'] == country].sort_values('Jahr')
            
            # Initialize status for each year
            if (country, indicator) not in complete_status:
                complete_status[(country, indicator)] = {}
            
            # Determine base status from 2019
            base_year_data = country_data[country_data['Jahr'] == BASELINE_YEAR]
            if base_year_data.empty:
                continue  # Skip if no base status available
            
            base_status = base_year_data.iloc[0]['Result_Grouped']
            
            # Set base status from 2019 for all years
            for year in years:
                complete_status[(country, indicator)][year] = base_status
            
            # Consider changes in later years
            for _, row in country_data[country_data['Jahr'] > BASELINE_YEAR].iterrows():
                year = row['Jahr']
                new_status = row['Result_Grouped']
                complete_status[(country, indicator)][year] = new_status
    
    # Calculate progress and regress for each year
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        year_labels.append(str(curr_year))
        
        year_progress = 0
        year_regress = 0
        
        # For each country and indicator count status changes
        for key in complete_status:
            country, indicator = key
            if prev_year in complete_status[key] and curr_year in complete_status[key]:
                prev_status = complete_status[key][prev_year]
                curr_status = complete_status[key][curr_year]
                
                # Progress
                if (prev_status == IndicatorStatus.NO and curr_status == IndicatorStatus.YES) or \
                   (prev_status == IndicatorStatus.NO and curr_status == IndicatorStatus.PARTIALLY) or \
                   (prev_status == IndicatorStatus.PARTIALLY and curr_status == IndicatorStatus.YES):
                    year_progress += 1
                
                # Regress
                elif (prev_status == IndicatorStatus.YES and curr_status == IndicatorStatus.NO) or \
                     (prev_status == IndicatorStatus.YES and curr_status == IndicatorStatus.PARTIALLY) or \
                     (prev_status == IndicatorStatus.PARTIALLY and curr_status == IndicatorStatus.NO):
                    year_regress += 1
        
        global_progress.append(year_progress)
        global_regress.append(year_regress)
    
    return year_labels, global_progress, global_regress


def calculate_progress_by_indicator(
    df_for_maps: pd.DataFrame,
    indikator_liste: List[str],
    calculate_progress_func
) -> List[Dict[str, Any]]:
    """
    Calculate progress statistics by indicator.
    
    Args:
        df_for_maps: DataFrame with data
        indikator_liste: List of indicators
        calculate_progress_func: Function to calculate progress
    
    Returns:
        List of dictionaries with indicator progress statistics
    """
    progress_by_indicator = []
    
    for indicator in indikator_liste:
        progress_count, regress_count, _ = calculate_progress_func(df_for_maps, indicator)
        progress_by_indicator.append({
            'Indikator': indicator,
            'Fortschritte': progress_count,
            'Rückschritte': regress_count,
            'Netto': progress_count - regress_count
        })
    
    # Sort by net progress
    progress_by_indicator.sort(key=lambda x: x['Netto'], reverse=True)
    
    return progress_by_indicator


# =============================================================================
# LEGACY COMPATIBILITY FUNCTION
# =============================================================================

def get_current_data_for_year(df_for_maps: pd.DataFrame, indicator_name: str, target_year: int) -> pd.DataFrame:
    """
    Legacy function name for backward compatibility.
    
    Args:
        df_for_maps: Filtered DataFrame with data
        indicator_name: Name of the indicator
        target_year: Target year for calculation
    
    Returns:
        DataFrame with current status for each country
    """
    return calculate_current_data_for_year(df_for_maps, indicator_name, target_year)