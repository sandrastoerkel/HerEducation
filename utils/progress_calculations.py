"""
Enterprise-level progress calculations module.

This module provides comprehensive progress and regression calculation functionality
for indicators with enterprise architecture, type safety, and advanced analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class ProgressCalculationConstants:
    """Central constants for progress calculations"""
    
    # Base year and time settings
    BASE_YEAR = 2019
    DEFAULT_CURRENT_YEAR = 2025
    MIN_VALID_YEAR = 2000
    MAX_VALID_YEAR = 2030
    
    # Scoring system
    MAJOR_PROGRESS_SCORE = 2      # No -> Yes
    MINOR_PROGRESS_SCORE = 1      # No -> Partially, Partially -> Yes
    MINOR_REGRESS_SCORE = -1      # Yes -> Partially, Partially -> No
    MAJOR_REGRESS_SCORE = -2      # Yes -> No
    NO_CHANGE_SCORE = 0
    
    # Data validation
    MIN_COUNTRIES_FOR_ANALYSIS = 1
    MIN_YEARS_FOR_TREND = 2
    
    # Visualization
    CHART_HEIGHT = 500
    CHART_HEIGHT_LARGE = 600
    CHART_HEIGHT_SMALL = 300
    
    # Performance
    MAX_INDICATORS_BATCH = 100
    MAX_COUNTRIES_BATCH = 500
    
    # Logging
    LOGGER_NAME = "progress_calculations"


class IndicatorStatus(str, Enum):
    """Status values for indicators"""
    NO = "No"
    PARTIALLY = "Partially"
    YES = "Yes"
    UNKNOWN = "Unknown"


class ChangeType(str, Enum):
    """Types of changes in indicator status"""
    PROGRESS = "Fortschritt"
    REGRESS = "Rückschritt"
    NO_CHANGE = "Keine Änderung"


class AnalysisMode(Enum):
    """Analysis modes for different use cases"""
    SIMPLE = "simple"
    WEIGHTED = "weighted"
    COMPREHENSIVE = "comprehensive"


class ProgressDirection(Enum):
    """Direction of progress for better analytics"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# =============================================================================
# VISUALIZATION CONFIGURATION
# =============================================================================

class ProgressVisualizationConfig:
    """Configuration for progress visualization"""
    
    STATUS_COLORS = {
        IndicatorStatus.YES: '#4CAF50',        # Green
        IndicatorStatus.PARTIALLY: '#FF9800',   # Orange
        IndicatorStatus.NO: '#F44336',          # Red
        IndicatorStatus.UNKNOWN: '#9E9E9E'      # Gray
    }
    
    CHANGE_COLORS = {
        ChangeType.PROGRESS: '#4CAF50',         # Green
        ChangeType.REGRESS: '#F44336',          # Red
        ChangeType.NO_CHANGE: '#9E9E9E'         # Gray
    }
    
    DIRECTION_COLORS = {
        ProgressDirection.POSITIVE: '#4CAF50',   # Green
        ProgressDirection.NEGATIVE: '#F44336',   # Red
        ProgressDirection.NEUTRAL: '#9E9E9E'     # Gray
    }


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ProgressCalculationConfig:
    """Configuration for progress calculations"""
    base_year: int = ProgressCalculationConstants.BASE_YEAR
    current_year: Optional[int] = None
    analysis_mode: AnalysisMode = AnalysisMode.COMPREHENSIVE
    include_partial_changes: bool = True
    weight_major_changes: bool = True
    min_countries_threshold: int = ProgressCalculationConstants.MIN_COUNTRIES_FOR_ANALYSIS
    
    def __post_init__(self):
        """Validate and set defaults"""
        if self.current_year is None:
            self.current_year = ProgressCalculationConstants.DEFAULT_CURRENT_YEAR
        
        # Validate year ranges
        if not (ProgressCalculationConstants.MIN_VALID_YEAR <= self.base_year <= ProgressCalculationConstants.MAX_VALID_YEAR):
            self.base_year = ProgressCalculationConstants.BASE_YEAR
        
        if not (ProgressCalculationConstants.MIN_VALID_YEAR <= self.current_year <= ProgressCalculationConstants.MAX_VALID_YEAR):
            self.current_year = ProgressCalculationConstants.DEFAULT_CURRENT_YEAR
    
    def validate(self) -> bool:
        """Validate configuration"""
        return (
            self.base_year < self.current_year and
            self.min_countries_threshold >= 1
        )


@dataclass
class StatusChange:
    """Represents a single status change event"""
    country: str
    indicator: str
    year: int
    from_status: IndicatorStatus
    to_status: IndicatorStatus
    change_type: ChangeType
    score: int
    
    @property
    def is_progress(self) -> bool:
        """Check if this change represents progress"""
        return self.change_type == ChangeType.PROGRESS
    
    @property
    def is_regress(self) -> bool:
        """Check if this change represents regression"""
        return self.change_type == ChangeType.REGRESS
    
    @property
    def is_major_change(self) -> bool:
        """Check if this is a major change (score magnitude >= 2)"""
        return abs(self.score) >= 2


@dataclass
class CountryProgress:
    """Progress statistics for a single country"""
    country: str
    progress_count: int = 0
    regress_count: int = 0
    total_score: int = 0
    major_progress_count: int = 0
    major_regress_count: int = 0
    minor_progress_count: int = 0
    minor_regress_count: int = 0
    changes: List[StatusChange] = field(default_factory=list)
    
    @property
    def net_progress(self) -> int:
        """Calculate net progress (progress - regress)"""
        return self.progress_count - self.regress_count
    
    @property
    def total_changes(self) -> int:
        """Calculate total number of changes"""
        return self.progress_count + self.regress_count
    
    @property
    def progress_ratio(self) -> float:
        """Calculate ratio of progress to total changes"""
        if self.total_changes == 0:
            return 0.0
        return self.progress_count / self.total_changes
    
    @property
    def performance_category(self) -> ProgressDirection:
        """Categorize overall performance"""
        if self.net_progress > 0:
            return ProgressDirection.POSITIVE
        elif self.net_progress < 0:
            return ProgressDirection.NEGATIVE
        else:
            return ProgressDirection.NEUTRAL


@dataclass
class IndicatorProgress:
    """Progress statistics for a single indicator"""
    indicator: str
    progress_count: int = 0
    regress_count: int = 0
    total_score: int = 0
    countries_with_progress: Set[str] = field(default_factory=set)
    countries_with_regress: Set[str] = field(default_factory=set)
    changes: List[StatusChange] = field(default_factory=list)
    
    @property
    def net_progress(self) -> int:
        """Calculate net progress"""
        return self.progress_count - self.regress_count
    
    @property
    def countries_affected(self) -> int:
        """Number of countries with any changes"""
        return len(self.countries_with_progress | self.countries_with_regress)


@dataclass
class ProgressCalculationResults:
    """Complete results of progress calculation analysis"""
    config: ProgressCalculationConfig
    country_results: Dict[str, CountryProgress]
    indicator_results: Dict[str, IndicatorProgress]
    total_progress_count: int
    total_regress_count: int
    total_score: int
    processing_time: float
    countries_analyzed: int
    indicators_analyzed: int
    changes_found: int
    success: bool = True
    error_message: Optional[str] = None
    
    @property
    def net_global_progress(self) -> int:
        """Calculate global net progress"""
        return self.total_progress_count - self.total_regress_count
    
    @property
    def global_progress_ratio(self) -> float:
        """Calculate global progress ratio"""
        total_changes = self.total_progress_count + self.total_regress_count
        if total_changes == 0:
            return 0.0
        return self.total_progress_count / total_changes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for easy access"""
        return {
            "total_progress": self.total_progress_count,
            "total_regress": self.total_regress_count,
            "net_progress": self.net_global_progress,
            "total_score": self.total_score,
            "countries_analyzed": self.countries_analyzed,
            "indicators_analyzed": self.indicators_analyzed,
            "changes_found": self.changes_found,
            "processing_time": self.processing_time,
            "success": self.success
        }


# =============================================================================
# SPECIALIZED COMPONENTS
# =============================================================================

class StatusAnalyzer:
    """Analyzes status changes and determines change types"""
    
    def __init__(self, config: ProgressCalculationConfig):
        self.config = config
        self.logger = logging.getLogger(ProgressCalculationConstants.LOGGER_NAME)
    
    def analyze_status_change(
        self, 
        from_status: str, 
        to_status: str
    ) -> Tuple[ChangeType, int]:
        """
        Analyze a status change and determine type and score
        
        Args:
            from_status: Original status
            to_status: New status
            
        Returns:
            Tuple of (change_type, score)
        """
        try:
            # Convert to enum values
            from_enum = IndicatorStatus(from_status)
            to_enum = IndicatorStatus(to_status)
            
            # No change
            if from_enum == to_enum:
                return ChangeType.NO_CHANGE, ProgressCalculationConstants.NO_CHANGE_SCORE
            
            # Progress cases
            if self._is_progress(from_enum, to_enum):
                score = self._calculate_progress_score(from_enum, to_enum)
                return ChangeType.PROGRESS, score
            
            # Regress cases
            if self._is_regress(from_enum, to_enum):
                score = self._calculate_regress_score(from_enum, to_enum)
                return ChangeType.REGRESS, score
            
            # Unknown transition
            self.logger.warning(f"Unknown status transition: {from_status} -> {to_status}")
            return ChangeType.NO_CHANGE, ProgressCalculationConstants.NO_CHANGE_SCORE
            
        except ValueError as e:
            self.logger.error(f"Invalid status values: {from_status}, {to_status} - {e}")
            return ChangeType.NO_CHANGE, ProgressCalculationConstants.NO_CHANGE_SCORE
    
    def _is_progress(self, from_status: IndicatorStatus, to_status: IndicatorStatus) -> bool:
        """Check if transition represents progress"""
        return (
            (from_status == IndicatorStatus.NO and to_status == IndicatorStatus.YES) or
            (from_status == IndicatorStatus.NO and to_status == IndicatorStatus.PARTIALLY) or
            (from_status == IndicatorStatus.PARTIALLY and to_status == IndicatorStatus.YES)
        )
    
    def _is_regress(self, from_status: IndicatorStatus, to_status: IndicatorStatus) -> bool:
        """Check if transition represents regression"""
        return (
            (from_status == IndicatorStatus.YES and to_status == IndicatorStatus.NO) or
            (from_status == IndicatorStatus.YES and to_status == IndicatorStatus.PARTIALLY) or
            (from_status == IndicatorStatus.PARTIALLY and to_status == IndicatorStatus.NO)
        )
    
    def _calculate_progress_score(self, from_status: IndicatorStatus, to_status: IndicatorStatus) -> int:
        """Calculate score for progress"""
        if from_status == IndicatorStatus.NO and to_status == IndicatorStatus.YES:
            return ProgressCalculationConstants.MAJOR_PROGRESS_SCORE
        else:
            return ProgressCalculationConstants.MINOR_PROGRESS_SCORE
    
    def _calculate_regress_score(self, from_status: IndicatorStatus, to_status: IndicatorStatus) -> int:
        """Calculate score for regression"""
        if from_status == IndicatorStatus.YES and to_status == IndicatorStatus.NO:
            return ProgressCalculationConstants.MAJOR_REGRESS_SCORE
        else:
            return ProgressCalculationConstants.MINOR_REGRESS_SCORE


class DataValidator:
    """Validates input data for progress calculations"""
    
    def __init__(self, config: ProgressCalculationConfig):
        self.config = config
        self.logger = logging.getLogger(ProgressCalculationConstants.LOGGER_NAME)
    
    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Validate input DataFrame structure and content
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required columns
            required_columns = ['Land', 'Indikator', 'Jahr', 'Result_Grouped']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Check data types and content
            if df.empty:
                self.logger.warning("DataFrame is empty")
                return False
            
            # Validate year column
            year_col = df['Jahr']
            if not pd.api.types.is_numeric_dtype(year_col):
                self.logger.error("Year column must be numeric")
                return False
            
            # Check year range
            min_year = year_col.min()
            max_year = year_col.max()
            
            if min_year < ProgressCalculationConstants.MIN_VALID_YEAR or max_year > ProgressCalculationConstants.MAX_VALID_YEAR:
                self.logger.warning(f"Year range unusual: {min_year} - {max_year}")
            
            # Validate status values
            valid_statuses = {status.value for status in IndicatorStatus}
            invalid_statuses = set(df['Result_Grouped'].unique()) - valid_statuses
            
            if invalid_statuses:
                self.logger.warning(f"Found invalid status values: {invalid_statuses}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"DataFrame validation error: {e}")
            return False
    
    def validate_indicator_list(self, indicators: List[str], df: pd.DataFrame) -> List[str]:
        """
        Validate and filter indicator list
        
        Args:
            indicators: List of indicators to validate
            df: DataFrame to check against
            
        Returns:
            List of valid indicators
        """
        try:
            if not indicators:
                self.logger.warning("Empty indicator list provided")
                return []
            
            available_indicators = set(df['Indikator'].unique())
            valid_indicators = [ind for ind in indicators if ind in available_indicators]
            invalid_indicators = [ind for ind in indicators if ind not in available_indicators]
            
            if invalid_indicators:
                self.logger.warning(f"Invalid indicators removed: {invalid_indicators}")
            
            if len(valid_indicators) == 0:
                self.logger.error("No valid indicators found")
            
            return valid_indicators
            
        except Exception as e:
            self.logger.error(f"Indicator validation error: {e}")
            return []


class ProgressAnalyzer:
    """Analyzes progress for individual indicators"""
    
    def __init__(self, config: ProgressCalculationConfig):
        self.config = config
        self.status_analyzer = StatusAnalyzer(config)
        self.logger = logging.getLogger(ProgressCalculationConstants.LOGGER_NAME)
    
    def analyze_indicator_progress(
        self, 
        df: pd.DataFrame, 
        indicator_name: str
    ) -> IndicatorProgress:
        """
        Analyze progress for a single indicator
        
        Args:
            df: DataFrame with data
            indicator_name: Name of indicator to analyze
            
        Returns:
            IndicatorProgress object with results
        """
        try:
            # Filter data for this indicator
            indicator_data = df[df['Indikator'] == indicator_name].copy()
            
            if indicator_data.empty:
                self.logger.warning(f"No data found for indicator: {indicator_name}")
                return IndicatorProgress(indicator=indicator_name)
            
            progress = IndicatorProgress(indicator=indicator_name)
            
            # Analyze each country
            countries = indicator_data['Land'].unique()
            
            for country in countries:
                country_data = indicator_data[indicator_data['Land'] == country].sort_values('Jahr')
                
                # Find base year data
                base_data = country_data[country_data['Jahr'] == self.config.base_year]
                if base_data.empty:
                    continue
                
                base_status = base_data.iloc[0]['Result_Grouped']
                
                # Analyze changes in subsequent years
                for _, row in country_data[country_data['Jahr'] > self.config.base_year].iterrows():
                    current_year = row['Jahr']
                    current_status = row['Result_Grouped']
                    
                    # Find previous status
                    prev_data = country_data[country_data['Jahr'] < current_year].iloc[-1]
                    prev_status = prev_data['Result_Grouped']
                    
                    # Analyze change
                    change_type, score = self.status_analyzer.analyze_status_change(
                        prev_status, current_status
                    )
                    
                    if change_type != ChangeType.NO_CHANGE:
                        # Create status change
                        change = StatusChange(
                            country=country,
                            indicator=indicator_name,
                            year=current_year,
                            from_status=IndicatorStatus(prev_status),
                            to_status=IndicatorStatus(current_status),
                            change_type=change_type,
                            score=score
                        )
                        
                        progress.changes.append(change)
                        
                        # Update counts
                        if change.is_progress:
                            progress.progress_count += 1
                            progress.countries_with_progress.add(country)
                        elif change.is_regress:
                            progress.regress_count += 1
                            progress.countries_with_regress.add(country)
                        
                        progress.total_score += score
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Error analyzing indicator {indicator_name}: {e}")
            return IndicatorProgress(indicator=indicator_name)


class CountryAnalyzer:
    """Analyzes progress for individual countries"""
    
    def __init__(self, config: ProgressCalculationConfig):
        self.config = config
        self.logger = logging.getLogger(ProgressCalculationConstants.LOGGER_NAME)
    
    def analyze_country_progress(
        self, 
        changes: List[StatusChange], 
        country: str
    ) -> CountryProgress:
        """
        Analyze progress for a single country
        
        Args:
            changes: List of status changes for this country
            country: Country name
            
        Returns:
            CountryProgress object with results
        """
        try:
            progress = CountryProgress(country=country)
            
            for change in changes:
                if change.country != country:
                    continue
                
                progress.changes.append(change)
                progress.total_score += change.score
                
                if change.is_progress:
                    progress.progress_count += 1
                    if change.is_major_change:
                        progress.major_progress_count += 1
                    else:
                        progress.minor_progress_count += 1
                        
                elif change.is_regress:
                    progress.regress_count += 1
                    if change.is_major_change:
                        progress.major_regress_count += 1
                    else:
                        progress.minor_regress_count += 1
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Error analyzing country {country}: {e}")
            return CountryProgress(country=country)


# =============================================================================
# MANAGER CLASS
# =============================================================================

class ProgressCalculationManager:
    """Enterprise manager for progress calculations"""
    
    def __init__(self, config: Optional[ProgressCalculationConfig] = None):
        self.config = config or ProgressCalculationConfig()
        
        if not self.config.validate():
            raise ValueError("Invalid configuration parameters")
        
        # Initialize components
        self.validator = DataValidator(self.config)
        self.progress_analyzer = ProgressAnalyzer(self.config)
        self.country_analyzer = CountryAnalyzer(self.config)
        
        self.logger = logging.getLogger(ProgressCalculationConstants.LOGGER_NAME)
    
    def analyze_comprehensive_progress(
        self, 
        df: pd.DataFrame, 
        indicators: List[str]
    ) -> ProgressCalculationResults:
        """
        Perform comprehensive progress analysis
        
        Args:
            df: DataFrame with indicator data
            indicators: List of indicators to analyze
            
        Returns:
            ProgressCalculationResults with complete analysis
        """
        import time
        start_time = time.time()
        
        try:
            # Validate inputs
            if not self.validator.validate_dataframe(df):
                return self._create_error_result("Invalid DataFrame", time.time() - start_time)
            
            valid_indicators = self.validator.validate_indicator_list(indicators, df)
            if not valid_indicators:
                return self._create_error_result("No valid indicators", time.time() - start_time)
            
            # Initialize results
            country_results = {}
            indicator_results = {}
            all_changes = []
            
            # Analyze each indicator
            for indicator in valid_indicators:
                indicator_progress = self.progress_analyzer.analyze_indicator_progress(df, indicator)
                indicator_results[indicator] = indicator_progress
                all_changes.extend(indicator_progress.changes)
            
            # Analyze countries
            countries = set(change.country for change in all_changes)
            for country in countries:
                country_changes = [change for change in all_changes if change.country == country]
                country_progress = self.country_analyzer.analyze_country_progress(country_changes, country)
                country_results[country] = country_progress
            
            # Calculate totals
            total_progress = sum(ind.progress_count for ind in indicator_results.values())
            total_regress = sum(ind.regress_count for ind in indicator_results.values())
            total_score = sum(ind.total_score for ind in indicator_results.values())
            
            processing_time = time.time() - start_time
            
            return ProgressCalculationResults(
                config=self.config,
                country_results=country_results,
                indicator_results=indicator_results,
                total_progress_count=total_progress,
                total_regress_count=total_regress,
                total_score=total_score,
                processing_time=processing_time,
                countries_analyzed=len(countries),
                indicators_analyzed=len(valid_indicators),
                changes_found=len(all_changes),
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return self._create_error_result(str(e), time.time() - start_time)
    
    def _create_error_result(self, error_message: str, processing_time: float) -> ProgressCalculationResults:
        """Create error result object"""
        return ProgressCalculationResults(
            config=self.config,
            country_results={},
            indicator_results={},
            total_progress_count=0,
            total_regress_count=0,
            total_score=0,
            processing_time=processing_time,
            countries_analyzed=0,
            indicators_analyzed=0,
            changes_found=0,
            success=False,
            error_message=error_message
        )


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_progress_calculation_config() -> ProgressCalculationConfig:
    """Render progress calculation configuration UI"""
    st.subheader("⚙️ Progress Calculation Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        base_year = st.number_input(
            "Base Year",
            min_value=ProgressCalculationConstants.MIN_VALID_YEAR,
            max_value=ProgressCalculationConstants.MAX_VALID_YEAR,
            value=ProgressCalculationConstants.BASE_YEAR,
            help="Starting year for progress calculations"
        )
        
        current_year = st.number_input(
            "Current Year",
            min_value=base_year + 1,
            max_value=ProgressCalculationConstants.MAX_VALID_YEAR,
            value=ProgressCalculationConstants.DEFAULT_CURRENT_YEAR,
            help="End year for progress calculations"
        )
        
        analysis_mode = st.selectbox(
            "Analysis Mode",
            options=[mode.value for mode in AnalysisMode],
            index=2,  # Comprehensive
            help="Level of analysis detail"
        )
    
    with col2:
        include_partial = st.checkbox(
            "Include Partial Changes", 
            value=True,
            help="Include transitions involving 'Partially' status"
        )
        
        weight_major = st.checkbox(
            "Weight Major Changes", 
            value=True,
            help="Give higher scores to major transitions (No<->Yes)"
        )
        
        min_countries = st.number_input(
            "Minimum Countries",
            min_value=1,
            max_value=100,
            value=ProgressCalculationConstants.MIN_COUNTRIES_FOR_ANALYSIS,
            help="Minimum countries required for analysis"
        )
    
    return ProgressCalculationConfig(
        base_year=int(base_year),
        current_year=int(current_year),
        analysis_mode=AnalysisMode(analysis_mode),
        include_partial_changes=include_partial,
        weight_major_changes=weight_major,
        min_countries_threshold=int(min_countries)
    )


def render_progress_results_overview(results: ProgressCalculationResults) -> None:
    """Render overview of progress calculation results"""
    st.subheader("📊 Progress Analysis Overview")
    
    if not results.success:
        st.error(f"Analysis failed: {results.error_message}")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Progress", results.total_progress_count)
    
    with col2:
        st.metric("Total Regress", results.total_regress_count)
    
    with col3:
        st.metric("Net Progress", results.net_global_progress)
    
    with col4:
        st.metric("Total Score", results.total_score)
    
    # Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("Countries", results.countries_analyzed)
    
    with col6:
        st.metric("Indicators", results.indicators_analyzed)
    
    with col7:
        st.metric("Changes Found", results.changes_found)
    
    with col8:
        st.metric("Processing Time", f"{results.processing_time:.3f}s")


def render_country_progress_chart(results: ProgressCalculationResults) -> None:
    """Render country progress visualization"""
    st.subheader("🌍 Progress by Country")
    
    if not results.country_results:
        st.info("No country data available for visualization.")
        return
    
    # Prepare data for visualization
    country_data = []
    for country, progress in results.country_results.items():
        country_data.append({
            'Country': country,
            'Progress': progress.progress_count,
            'Regress': progress.regress_count,
            'Net Progress': progress.net_progress,
            'Total Score': progress.total_score,
            'Progress Ratio': progress.progress_ratio
        })
    
    country_df = pd.DataFrame(country_data)
    
    # Sort by net progress
    country_df = country_df.sort_values('Net Progress', ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        country_df,
        x='Net Progress',
        y='Country',
        color='Net Progress',
        color_continuous_scale=['red', 'yellow', 'green'],
        title='Net Progress by Country',
        labels={'Net Progress': 'Net Progress (Progress - Regress)'}
    )
    
    fig.update_layout(
        height=max(ProgressCalculationConstants.CHART_HEIGHT, len(country_df) * 25),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_indicator_progress_chart(results: ProgressCalculationResults) -> None:
    """Render indicator progress visualization"""
    st.subheader("📈 Progress by Indicator")
    
    if not results.indicator_results:
        st.info("No indicator data available for visualization.")
        return
    
    # Prepare data
    indicator_data = []
    for indicator, progress in results.indicator_results.items():
        indicator_data.append({
            'Indicator': indicator,
            'Progress': progress.progress_count,
            'Regress': progress.regress_count,
            'Net Progress': progress.net_progress,
            'Countries Affected': progress.countries_affected
        })
    
    indicator_df = pd.DataFrame(indicator_data)
    
    # Create grouped bar chart
    fig = px.bar(
        indicator_df,
        x='Indicator',
        y=['Progress', 'Regress'],
        barmode='group',
        color_discrete_map={
            'Progress': ProgressVisualizationConfig.CHANGE_COLORS[ChangeType.PROGRESS],
            'Regress': ProgressVisualizationConfig.CHANGE_COLORS[ChangeType.REGRESS]
        },
        title='Progress vs Regress by Indicator'
    )
    
    fig.update_layout(
        height=ProgressCalculationConstants.CHART_HEIGHT,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_progress_trends_chart(results: ProgressCalculationResults) -> None:
    """Render progress trends over time"""
    st.subheader("📅 Progress Trends Over Time")
    
    # Collect all changes
    all_changes = []
    for indicator_progress in results.indicator_results.values():
        all_changes.extend(indicator_progress.changes)
    
    if not all_changes:
        st.info("No trend data available.")
        return
    
    # Group by year and change type
    trend_data = []
    years = sorted(set(change.year for change in all_changes))
    
    for year in years:
        year_changes = [change for change in all_changes if change.year == year]
        progress_count = sum(1 for change in year_changes if change.is_progress)
        regress_count = sum(1 for change in year_changes if change.is_regress)
        
        trend_data.extend([
            {'Year': year, 'Type': 'Progress', 'Count': progress_count},
            {'Year': year, 'Type': 'Regress', 'Count': regress_count}
        ])
    
    trend_df = pd.DataFrame(trend_data)
    
    # Create line chart
    fig = px.line(
        trend_df,
        x='Year',
        y='Count',
        color='Type',
        markers=True,
        color_discrete_map={
            'Progress': ProgressVisualizationConfig.CHANGE_COLORS[ChangeType.PROGRESS],
            'Regress': ProgressVisualizationConfig.CHANGE_COLORS[ChangeType.REGRESS]
        },
        title='Progress and Regress Trends Over Time'
    )
    
    fig.update_layout(height=ProgressCalculationConstants.CHART_HEIGHT)
    
    st.plotly_chart(fig, use_container_width=True)


def render_detailed_results_tables(results: ProgressCalculationResults) -> None:
    """Render detailed results in tables"""
    
    # Country details
    if results.country_results:
        with st.expander("📋 Detailed Country Results", expanded=False):
            country_data = []
            for country, progress in results.country_results.items():
                country_data.append({
                    'Country': country,
                    'Progress': progress.progress_count,
                    'Regress': progress.regress_count,
                    'Net': progress.net_progress,
                    'Score': progress.total_score,
                    'Major Progress': progress.major_progress_count,
                    'Major Regress': progress.major_regress_count,
                    'Progress Ratio': f"{progress.progress_ratio:.2%}"
                })
            
            country_df = pd.DataFrame(country_data)
            st.dataframe(country_df.sort_values('Net', ascending=False))
    
    # Indicator details
    if results.indicator_results:
        with st.expander("📊 Detailed Indicator Results", expanded=False):
            indicator_data = []
            for indicator, progress in results.indicator_results.items():
                indicator_data.append({
                    'Indicator': indicator,
                    'Progress': progress.progress_count,
                    'Regress': progress.regress_count,
                    'Net': progress.net_progress,
                    'Score': progress.total_score,
                    'Countries': progress.countries_affected
                })
            
            indicator_df = pd.DataFrame(indicator_data)
            st.dataframe(indicator_df.sort_values('Net', ascending=False))


# =============================================================================
# BACKWARD COMPATIBILITY - LEGACY API
# =============================================================================

def calculate_progress(df_for_maps, indicator_name, year=None):
    """
    LEGACY FUNCTION: Calculate progress and regress for an indicator
    
    Args:
        df_for_maps: The filtered DataFrame with data
        indicator_name: The name of the indicator
        year: The year for calculation (optional)
    
    Returns:
        tuple: (progress_count, regress_count, progress_list)
    """
    config = ProgressCalculationConfig()
    if year is not None:
        config.current_year = year
    
    manager = ProgressCalculationManager(config)
    results = manager.analyze_comprehensive_progress(df_for_maps, [indicator_name])
    
    if not results.success:
        return 0, 0, []
    
    indicator_result = results.indicator_results.get(indicator_name)
    if not indicator_result:
        return 0, 0, []
    
    # Convert to legacy format
    progress_list = []
    for change in indicator_result.changes:
        progress_list.append({
            'Land': change.country,
            'Typ': change.change_type.value,
            'Jahr': change.year,
            'Von': change.from_status.value,
            'Zu': change.to_status.value,
            'Indikator': change.indicator
        })
    
    return indicator_result.progress_count, indicator_result.regress_count, progress_list


def calculate_change_score(from_status, to_status):
    """
    LEGACY FUNCTION: Calculate score for a status change
    
    Args:
        from_status: The original status
        to_status: The target status
    
    Returns:
        int: The score value of the change
    """
    config = ProgressCalculationConfig()
    analyzer = StatusAnalyzer(config)
    _, score = analyzer.analyze_status_change(from_status, to_status)
    return score


def calculate_country_progress(df_for_maps, indikator_liste):
    """
    LEGACY FUNCTION: Calculate all progress and regress per country
    
    Args:
        df_for_maps: The filtered DataFrame with data
        indikator_liste: The list of indicators
    
    Returns:
        tuple: (Dict with progress/regress per country, Dict with change details)
    """
    manager = ProgressCalculationManager()
    results = manager.analyze_comprehensive_progress(df_for_maps, indikator_liste)
    
    if not results.success:
        return {}, {}
    
    # Convert to legacy format
    country_progress = {}
    country_details = {}
    
    for country, progress in results.country_results.items():
        country_progress[country] = {
            'Fortschritt': progress.progress_count,
            'Rückschritt': progress.regress_count,
            'Netto': progress.net_progress
        }
        
        # Convert changes to legacy format
        country_details[country] = []
        for change in progress.changes:
            country_details[country].append({
                'Land': change.country,
                'Typ': change.change_type.value,
                'Jahr': change.year,
                'Von': change.from_status.value,
                'Zu': change.to_status.value,
                'Indikator': change.indicator
            })
    
    return country_progress, country_details


def calculate_weighted_country_progress(df_for_maps, indikator_liste):
    """
    LEGACY FUNCTION: Calculate weighted progress and regress per country
    
    Args:
        df_for_maps: The filtered DataFrame with data
        indikator_liste: The list of indicators
    
    Returns:
        tuple: (Dict with weighted progress/regress per country, Dict with details)
    """
    manager = ProgressCalculationManager()
    results = manager.analyze_comprehensive_progress(df_for_maps, indikator_liste)
    
    if not results.success:
        return {}, {}
    
    # Convert to legacy format
    country_progress = {}
    country_details = {}
    
    for country, progress in results.country_results.items():
        country_progress[country] = {
            'Fortschritt': progress.progress_count,
            'Rückschritt': progress.regress_count,
            'Score': progress.total_score
        }
        
        # Convert changes to legacy format with scores
        country_details[country] = []
        for change in progress.changes:
            change_dict = {
                'Land': change.country,
                'Typ': change.change_type.value,
                'Jahr': change.year,
                'Von': change.from_status.value,
                'Zu': change.to_status.value,
                'Indikator': change.indicator,
                'Score': change.score
            }
            country_details[country].append(change_dict)
    
    return country_progress, country_details


# =============================================================================
# EXTENDED API
# =============================================================================

def create_progress_calculation_manager(
    config: Optional[ProgressCalculationConfig] = None
) -> ProgressCalculationManager:
    """Factory function for ProgressCalculationManager"""
    return ProgressCalculationManager(config)


def create_progress_calculation_config(**kwargs) -> ProgressCalculationConfig:
    """Factory function for creating custom configuration"""
    return ProgressCalculationConfig(**kwargs)


def analyze_progress_with_ui(
    df: pd.DataFrame, 
    indicators: List[str]
) -> ProgressCalculationResults:
    """
    Analyze progress with UI configuration
    
    Args:
        df: DataFrame with indicator data
        indicators: List of indicators to analyze
        
    Returns:
        ProgressCalculationResults
    """
    # Render configuration UI
    config = render_progress_calculation_config()
    
    # Perform analysis
    manager = ProgressCalculationManager(config)
    results = manager.analyze_comprehensive_progress(df, indicators)
    
    # Render results
    render_progress_results_overview(results)
    render_country_progress_chart(results)
    render_indicator_progress_chart(results)
    render_progress_trends_chart(results)
    render_detailed_results_tables(results)
    
    return results


def get_progress_visualization_config() -> ProgressVisualizationConfig:
    """Get visualization configuration"""
    return ProgressVisualizationConfig()


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Main API Functions (Backward Compatible)
    'calculate_progress',
    'calculate_change_score',
    'calculate_country_progress',
    'calculate_weighted_country_progress',
    
    # New Enterprise Classes and Functions
    'ProgressCalculationManager',
    'ProgressCalculationConfig',
    'ProgressCalculationResults',
    'StatusChange',
    'CountryProgress',
    'IndicatorProgress',
    'create_progress_calculation_manager',
    'create_progress_calculation_config',
    'analyze_progress_with_ui',
    
    # Constants and Enums
    'ProgressCalculationConstants',
    'IndicatorStatus',
    'ChangeType',
    'AnalysisMode',
    'ProgressDirection'
]