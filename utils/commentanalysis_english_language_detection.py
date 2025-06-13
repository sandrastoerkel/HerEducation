"""
Enterprise-level English language detection module.

This module provides comprehensive language detection functionality for comment analysis
with enterprise architecture, ML integration, advanced statistics, and robust error handling.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import logging
import time
import numpy as np
from collections import Counter

# =============================================================================
# ENTERPRISE CONSTANTS
# =============================================================================

class LanguageDetectionConstants:
    """Constants for language detection operations."""
    
    # Detection Parameters
    MIN_TEXT_LENGTH = 10
    MAX_TEXT_LENGTH = 5000
    DEFAULT_CONFIDENCE_THRESHOLD = 0.8
    BATCH_SIZE = 100
    
    # Statistics
    MAX_LANGUAGES_IN_PIE = 5
    MAX_LANGUAGES_IN_STATS = 10
    PROGRESS_UPDATE_INTERVAL = 50
    
    # Visualization
    DEFAULT_PIE_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    # Performance
    CACHE_SIZE = 1000
    DETECTION_TIMEOUT = 5.0
    
    # UI Configuration
    DEFAULT_FILTER_ENABLED = True
    DEFAULT_SHOW_STATISTICS = True
    DEFAULT_SHOW_VISUALIZATION = True

class SupportedLanguages:
    """Comprehensive language code to name mapping."""
    
    LANGUAGE_NAMES = {
        # Major Languages
        'en': 'English',
        'de': 'German',
        'fr': 'French',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'zh': 'Chinese',
        'hi': 'Hindi',
        'tr': 'Turkish',
        'nl': 'Dutch',
        
        # European Languages
        'sv': 'Swedish',
        'no': 'Norwegian',
        'da': 'Danish',
        'pl': 'Polish',
        'cs': 'Czech',
        'sk': 'Slovak',
        'fi': 'Finnish',
        'hu': 'Hungarian',
        'ro': 'Romanian',
        'bg': 'Bulgarian',
        'hr': 'Croatian',
        'sr': 'Serbian',
        'sl': 'Slovenian',
        'et': 'Estonian',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'uk': 'Ukrainian',
        'el': 'Greek',
        'he': 'Hebrew',
        'mt': 'Maltese',
        'is': 'Icelandic',
        'ga': 'Irish',
        'cy': 'Welsh',
        'eu': 'Basque',
        'ca': 'Catalan',
        'gl': 'Galician',
        
        # Middle Eastern & South Asian
        'fa': 'Persian',
        'ur': 'Urdu',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'kn': 'Kannada',
        'or': 'Oriya',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'si': 'Sinhala',
        
        # East & Southeast Asian
        'my': 'Burmese',
        'km': 'Khmer',
        'lo': 'Lao',
        'vi': 'Vietnamese',
        'th': 'Thai',
        'id': 'Indonesian',
        'ms': 'Malay',
        'tl': 'Filipino',
        
        # African Languages
        'sw': 'Swahili',
        'am': 'Amharic',
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'ha': 'Hausa',
        'zu': 'Zulu',
        'af': 'Afrikaans',
        'xh': 'Xhosa',
        'st': 'Sesotho',
        'tn': 'Setswana',
        
        # Additional Languages
        'sq': 'Albanian',
        'hy': 'Armenian',
        'az': 'Azerbaijani',
        'be': 'Belarusian',
        'bs': 'Bosnian',
        'mk': 'Macedonian',
        'me': 'Montenegrin',
        'kk': 'Kazakh',
        'ky': 'Kyrgyz',
        'mn': 'Mongolian',
        'tg': 'Tajik',
        'tk': 'Turkmen',
        'uz': 'Uzbek'
    }
    
    # Language categories for analysis
    MAJOR_LANGUAGES = ['en', 'de', 'fr', 'es', 'it', 'pt', 'ru', 'ar', 'ja', 'ko', 'zh', 'hi']
    EUROPEAN_LANGUAGES = ['en', 'de', 'fr', 'es', 'it', 'pt', 'ru', 'nl', 'sv', 'no', 'da', 'pl', 'cs', 'sk', 'fi', 'hu', 'ro', 'bg', 'hr', 'sr', 'sl', 'et', 'lv', 'lt', 'uk', 'el']
    ASIAN_LANGUAGES = ['ja', 'ko', 'zh', 'hi', 'ar', 'fa', 'ur', 'bn', 'ta', 'te', 'ml', 'kn', 'vi', 'th', 'id', 'ms']
    
# =============================================================================
# ENTERPRISE ENUMS
# =============================================================================

class DetectionMode(Enum):
    """Language detection modes."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    DISABLED = "disabled"

class FilteringStrategy(Enum):
    """Strategies for language filtering."""
    STRICT = "strict"          # Only exact matches
    LENIENT = "lenient"        # Allow similar languages
    CONFIDENCE_BASED = "confidence_based"  # Use confidence thresholds

class VisualizationStyle(Enum):
    """Visualization style options."""
    PIE_CHART = "pie_chart"
    BAR_CHART = "bar_chart"
    DONUT_CHART = "donut_chart"
    HORIZONTAL_BAR = "horizontal_bar"

class LanguageCategory(Enum):
    """Language category classifications."""
    MAJOR = "major"
    EUROPEAN = "european"
    ASIAN = "asian"
    AFRICAN = "african"
    OTHER = "other"

# =============================================================================
# ENTERPRISE DATACLASSES
# =============================================================================

@dataclass
class LanguageDetectionConfig:
    """Configuration for language detection operations."""
    
    min_text_length: int = LanguageDetectionConstants.MIN_TEXT_LENGTH
    max_text_length: int = LanguageDetectionConstants.MAX_TEXT_LENGTH
    confidence_threshold: float = LanguageDetectionConstants.DEFAULT_CONFIDENCE_THRESHOLD
    detection_mode: DetectionMode = DetectionMode.AUTOMATIC
    filtering_strategy: FilteringStrategy = FilteringStrategy.STRICT
    target_language: str = "en"
    enable_batch_processing: bool = True
    batch_size: int = LanguageDetectionConstants.BATCH_SIZE
    enable_caching: bool = True
    cache_size: int = LanguageDetectionConstants.CACHE_SIZE
    detection_timeout: float = LanguageDetectionConstants.DETECTION_TIMEOUT
    
    # UI Configuration
    show_progress: bool = True
    show_statistics: bool = LanguageDetectionConstants.DEFAULT_SHOW_STATISTICS
    show_visualization: bool = LanguageDetectionConstants.DEFAULT_SHOW_VISUALIZATION
    visualization_style: VisualizationStyle = VisualizationStyle.PIE_CHART
    max_languages_display: int = LanguageDetectionConstants.MAX_LANGUAGES_IN_STATS
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        if self.min_text_length < 1:
            raise ValueError("Minimum text length must be positive")

@dataclass
class LanguageDetectionResult:
    """Result of language detection for a single text."""
    
    text: str
    detected_language: Optional[str]
    confidence: float
    processing_time: float
    error_message: Optional[str] = None
    is_reliable: bool = True
    alternative_languages: List[Tuple[str, float]] = field(default_factory=list)
    
    @property
    def language_name(self) -> str:
        """Human-readable language name."""
        if self.detected_language:
            return SupportedLanguages.LANGUAGE_NAMES.get(
                self.detected_language, 
                f'Unknown ({self.detected_language})'
            )
        return "Unknown"
    
    @property
    def is_english(self) -> bool:
        """Whether the detected language is English."""
        return self.detected_language == 'en'
    
    @property
    def meets_confidence_threshold(self) -> bool:
        """Whether the confidence meets the threshold."""
        return self.confidence >= 0.8  # Default threshold

@dataclass
class LanguageStatistics:
    """Statistical information about language detection results."""
    
    total_texts: int
    successful_detections: int
    failed_detections: int
    language_counts: Dict[str, int]
    language_percentages: Dict[str, float]
    confidence_stats: Dict[str, float]  # mean, std, min, max
    processing_time_total: float
    processing_time_average: float
    most_common_language: Optional[str] = None
    least_common_language: Optional[str] = None
    
    def __post_init__(self):
        """Calculate derived statistics."""
        if self.language_counts:
            # Most and least common languages
            sorted_langs = sorted(self.language_counts.items(), key=lambda x: x[1], reverse=True)
            self.most_common_language = sorted_langs[0][0] if sorted_langs else None
            self.least_common_language = sorted_langs[-1][0] if sorted_langs else None
    
    @property
    def success_rate(self) -> float:
        """Success rate of language detection."""
        if self.total_texts == 0:
            return 0.0
        return (self.successful_detections / self.total_texts) * 100
    
    @property
    def language_diversity(self) -> int:
        """Number of different languages detected."""
        return len(self.language_counts)

@dataclass
class FilteringResult:
    """Result of language filtering operation."""
    
    original_count: int
    filtered_count: int
    target_language_count: int
    statistics: LanguageStatistics
    processing_time: float
    
    @property
    def filter_ratio(self) -> float:
        """Ratio of filtered to original texts."""
        if self.original_count == 0:
            return 0.0
        return (self.filtered_count / self.original_count) * 100
    
    @property
    def target_ratio(self) -> float:
        """Ratio of target language to original texts."""
        if self.original_count == 0:
            return 0.0
        return (self.target_language_count / self.original_count) * 100

@dataclass
class LanguageDetectionResults:
    """Comprehensive results from language detection operations."""
    
    detection_results: List[LanguageDetectionResult]
    statistics: LanguageStatistics
    filtering_result: Optional[FilteringResult] = None
    config: Optional[LanguageDetectionConfig] = None
    
    def __post_init__(self):
        """Initialize derived properties."""
        if not hasattr(self, '_processed'):
            self._processed = True

# =============================================================================
# ENTERPRISE COMPONENTS
# =============================================================================

class LanguageDetectionEngine:
    """Core language detection engine with ML integration."""
    
    def __init__(self, config: LanguageDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cache = {} if config.enable_caching else None
        self._langdetect_available = self._check_langdetect()
    
    def _check_langdetect(self) -> bool:
        """Check if langdetect is available."""
        try:
            import langdetect
            return True
        except ImportError:
            self.logger.warning("langdetect not available - language detection disabled")
            return False
    
    def detect_single(self, text: str) -> LanguageDetectionResult:
        """
        Detect language for a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetectionResult
        """
        start_time = time.time()
        
        # Input validation
        if not self._langdetect_available:
            return LanguageDetectionResult(
                text=text,
                detected_language=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message="langdetect not available",
                is_reliable=False
            )
        
        if pd.isna(text) or text is None or str(text).strip() == "":
            return LanguageDetectionResult(
                text=text,
                detected_language=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message="Empty or null text",
                is_reliable=False
            )
        
        text = str(text).strip()
        
        # Check cache
        if self._cache and text in self._cache:
            cached_result = self._cache[text]
            cached_result.processing_time = time.time() - start_time  # Update timing
            return cached_result
        
        # Length validation
        if len(text) < self.config.min_text_length:
            result = LanguageDetectionResult(
                text=text,
                detected_language=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message=f"Text too short (min: {self.config.min_text_length})",
                is_reliable=False
            )
        elif len(text) > self.config.max_text_length:
            # Truncate text for detection
            truncated_text = text[:self.config.max_text_length]
            result = self._perform_detection(truncated_text, start_time)
        else:
            result = self._perform_detection(text, start_time)
        
        # Cache result
        if self._cache and len(self._cache) < self.config.cache_size:
            self._cache[text] = result
        
        return result
    
    def _perform_detection(self, text: str, start_time: float) -> LanguageDetectionResult:
        """Perform actual language detection."""
        try:
            from langdetect import detect, detect_langs
            
            # Basic detection
            detected_lang = detect(text)
            
            # Get confidence scores for multiple languages
            lang_probs = detect_langs(text)
            confidence = 0.0
            alternatives = []
            
            for lang_prob in lang_probs:
                if lang_prob.lang == detected_lang:
                    confidence = lang_prob.prob
                else:
                    alternatives.append((lang_prob.lang, lang_prob.prob))
            
            # Sort alternatives by probability
            alternatives.sort(key=lambda x: x[1], reverse=True)
            
            return LanguageDetectionResult(
                text=text,
                detected_language=detected_lang,
                confidence=confidence,
                processing_time=time.time() - start_time,
                alternative_languages=alternatives[:3],  # Top 3 alternatives
                is_reliable=confidence >= self.config.confidence_threshold
            )
            
        except Exception as e:
            return LanguageDetectionResult(
                text=text,
                detected_language=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message=str(e),
                is_reliable=False
            )
    
    def detect_batch(self, texts: List[str]) -> List[LanguageDetectionResult]:
        """
        Detect languages for a batch of texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of LanguageDetectionResult
        """
        results = []
        
        for i, text in enumerate(texts):
            result = self.detect_single(text)
            results.append(result)
            
            # Progress logging
            if i % LanguageDetectionConstants.PROGRESS_UPDATE_INTERVAL == 0:
                self.logger.debug(f"Processed {i + 1}/{len(texts)} texts")
        
        return results

class LanguageStatisticsCalculator:
    """Calculates comprehensive statistics for language detection results."""
    
    def __init__(self, config: LanguageDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def calculate_statistics(self, results: List[LanguageDetectionResult]) -> LanguageStatistics:
        """
        Calculate comprehensive statistics from detection results.
        
        Args:
            results: List of detection results
            
        Returns:
            LanguageStatistics object
        """
        if not results:
            return LanguageStatistics(
                total_texts=0,
                successful_detections=0,
                failed_detections=0,
                language_counts={},
                language_percentages={},
                confidence_stats={},
                processing_time_total=0.0,
                processing_time_average=0.0
            )
        
        # Basic counts
        total_texts = len(results)
        successful_detections = sum(1 for r in results if r.detected_language is not None)
        failed_detections = total_texts - successful_detections
        
        # Language counts
        language_counts = Counter()
        for result in results:
            if result.detected_language:
                language_counts[result.detected_language] += 1
        
        # Language percentages
        language_percentages = {
            lang: (count / total_texts) * 100
            for lang, count in language_counts.items()
        }
        
        # Confidence statistics
        confidences = [r.confidence for r in results if r.detected_language is not None]
        confidence_stats = {}
        if confidences:
            confidence_stats = {
                'mean': np.mean(confidences),
                'std': np.std(confidences),
                'min': np.min(confidences),
                'max': np.max(confidences),
                'median': np.median(confidences)
            }
        
        # Processing time statistics
        processing_times = [r.processing_time for r in results]
        processing_time_total = sum(processing_times)
        processing_time_average = processing_time_total / total_texts if total_texts > 0 else 0.0
        
        return LanguageStatistics(
            total_texts=total_texts,
            successful_detections=successful_detections,
            failed_detections=failed_detections,
            language_counts=dict(language_counts),
            language_percentages=language_percentages,
            confidence_stats=confidence_stats,
            processing_time_total=processing_time_total,
            processing_time_average=processing_time_average
        )

class LanguageFilter:
    """Filters texts based on detected languages."""
    
    def __init__(self, config: LanguageDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def filter_by_language(
        self, 
        df: pd.DataFrame, 
        text_column: str, 
        detection_results: List[LanguageDetectionResult],
        target_language: str = "en"
    ) -> Tuple[pd.DataFrame, FilteringResult]:
        """
        Filter DataFrame by target language.
        
        Args:
            df: DataFrame to filter
            text_column: Column containing text
            detection_results: Language detection results
            target_language: Target language code
            
        Returns:
            Tuple of (filtered_df, filtering_result)
        """
        start_time = time.time()
        
        # Add detection results to DataFrame
        df_copy = df.copy()
        df_copy['detected_language'] = [r.detected_language for r in detection_results]
        df_copy['language_confidence'] = [r.confidence for r in detection_results]
        df_copy['is_reliable'] = [r.is_reliable for r in detection_results]
        
        # Apply filtering strategy
        if self.config.filtering_strategy == FilteringStrategy.STRICT:
            filtered_df = df_copy[df_copy['detected_language'] == target_language].copy()
        elif self.config.filtering_strategy == FilteringStrategy.CONFIDENCE_BASED:
            filtered_df = df_copy[
                (df_copy['detected_language'] == target_language) & 
                (df_copy['language_confidence'] >= self.config.confidence_threshold)
            ].copy()
        else:  # LENIENT
            # Could include similar languages or lower confidence matches
            filtered_df = df_copy[df_copy['detected_language'] == target_language].copy()
        
        # Calculate statistics
        stats_calc = LanguageStatisticsCalculator(self.config)
        statistics = stats_calc.calculate_statistics(detection_results)
        
        # Create filtering result
        filtering_result = FilteringResult(
            original_count=len(df),
            filtered_count=len(df) - len(filtered_df),
            target_language_count=len(filtered_df),
            statistics=statistics,
            processing_time=time.time() - start_time
        )
        
        # Reset index and clean up
        filtered_df = filtered_df.reset_index(drop=True)
        # Remove temporary columns
        filtered_df = filtered_df.drop(['detected_language', 'language_confidence', 'is_reliable'], axis=1, errors='ignore')
        
        return filtered_df, filtering_result

class LanguageValidator:
    """Validates language detection operations and results."""
    
    def __init__(self, config: LanguageDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_dataframe(self, df: pd.DataFrame, text_column: str) -> Tuple[bool, str]:
        """
        Validate DataFrame for language detection.
        
        Args:
            df: DataFrame to validate
            text_column: Text column name
            
        Returns:
            Tuple of (is_valid, message)
        """
        if df.empty:
            return False, "DataFrame is empty"
        
        if text_column not in df.columns:
            return False, f"Text column '{text_column}' not found"
        
        non_null_count = df[text_column].notna().sum()
        if non_null_count == 0:
            return False, f"No valid text data in column '{text_column}'"
        
        # Check text lengths
        text_lengths = df[text_column].astype(str).str.len()
        valid_length_count = ((text_lengths >= self.config.min_text_length) & 
                            (text_lengths <= self.config.max_text_length)).sum()
        
        if valid_length_count == 0:
            return False, f"No texts meet length requirements ({self.config.min_text_length}-{self.config.max_text_length} chars)"
        
        return True, f"Validation successful ({non_null_count} texts, {valid_length_count} meet length requirements)"
    
    def validate_config(self, config: LanguageDetectionConfig) -> Tuple[bool, str]:
        """Validate configuration parameters."""
        try:
            # This will trigger validation in __post_init__
            LanguageDetectionConfig(**config.__dict__)
            return True, "Configuration is valid"
        except ValueError as e:
            return False, str(e)

# =============================================================================
# ENTERPRISE MANAGER
# =============================================================================

class LanguageDetectionManager:
    """
    Enterprise-level manager for language detection operations.
    
    This manager orchestrates all language detection operations with enterprise-grade
    architecture, comprehensive error handling, and advanced ML integration.
    """
    
    def __init__(self, config: Optional[LanguageDetectionConfig] = None):
        """
        Initialize the language detection manager.
        
        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or LanguageDetectionConfig()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.detection_engine = LanguageDetectionEngine(self.config)
        self.statistics_calculator = LanguageStatisticsCalculator(self.config)
        self.language_filter = LanguageFilter(self.config)
        self.validator = LanguageValidator(self.config)
        
        self.logger.info("LanguageDetectionManager initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the manager."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def detect_languages(self, texts: Union[str, List[str]]) -> LanguageDetectionResults:
        """
        Detect languages for one or more texts.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            LanguageDetectionResults object
        """
        # Normalize input
        if isinstance(texts, str):
            text_list = [texts]
        else:
            text_list = texts
        
        # Perform detection
        detection_results = self.detection_engine.detect_batch(text_list)
        
        # Calculate statistics
        statistics = self.statistics_calculator.calculate_statistics(detection_results)
        
        return LanguageDetectionResults(
            detection_results=detection_results,
            statistics=statistics,
            config=self.config
        )
    
    def filter_english_comments(
        self, 
        df: pd.DataFrame, 
        text_column: str,
        show_ui: bool = True
    ) -> Tuple[pd.DataFrame, LanguageDetectionResults]:
        """
        Filter DataFrame to only English comments with comprehensive analysis.
        
        Args:
            df: DataFrame with comments
            text_column: Column containing text
            show_ui: Whether to show Streamlit UI
            
        Returns:
            Tuple of (filtered_df, detection_results)
        """
        # Validate input
        is_valid, validation_message = self.validator.validate_dataframe(df, text_column)
        if not is_valid:
            raise ValueError(validation_message)
        
        # Extract texts
        texts = df[text_column].tolist()
        
        # Perform language detection
        if show_ui and self.config.show_progress:
            with st.spinner("Detecting comment languages..."):
                progress_bar = st.progress(0)
                detection_results = []
                
                for i, text in enumerate(texts):
                    result = self.detection_engine.detect_single(text)
                    detection_results.append(result)
                    progress_bar.progress((i + 1) / len(texts))
        else:
            detection_results = self.detection_engine.detect_batch(texts)
        
        # Calculate statistics
        statistics = self.statistics_calculator.calculate_statistics(detection_results)
        
        # Filter by language
        filtered_df, filtering_result = self.language_filter.filter_by_language(
            df, text_column, detection_results, self.config.target_language
        )
        
        # Create comprehensive results
        results = LanguageDetectionResults(
            detection_results=detection_results,
            statistics=statistics,
            filtering_result=filtering_result,
            config=self.config
        )
        
        return filtered_df, results
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get human-readable language name.
        
        Args:
            lang_code: Language code
            
        Returns:
            Human-readable language name
        """
        return SupportedLanguages.LANGUAGE_NAMES.get(
            lang_code, 
            f'Unknown ({lang_code})'
        )
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages."""
        return SupportedLanguages.LANGUAGE_NAMES.copy()

# =============================================================================
# UI COMPONENTS - ENTERPRISE STREAMLIT INTEGRATION
# =============================================================================

def render_language_filtering_ui(manager: LanguageDetectionManager) -> LanguageDetectionConfig:
    """
    Render language filtering configuration UI.
    
    Args:
        manager: Language detection manager
        
    Returns:
        Updated configuration
    """
    st.subheader("🌍 Language Detection & Filtering")
    
    config = manager.config
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Detection settings
        st.write("**Detection Settings:**")
        
        detection_mode = st.selectbox(
            "Detection Mode:",
            options=[mode.value for mode in DetectionMode],
            index=list(DetectionMode).index(config.detection_mode),
            help="How to perform language detection"
        )
        config.detection_mode = DetectionMode(detection_mode)
        
        if config.detection_mode != DetectionMode.DISABLED:
            config.confidence_threshold = st.slider(
                "Confidence Threshold:",
                min_value=0.0,
                max_value=1.0,
                value=config.confidence_threshold,
                step=0.05,
                help="Minimum confidence for reliable detection"
            )
            
            config.min_text_length = st.number_input(
                "Minimum Text Length:",
                min_value=1,
                max_value=100,
                value=config.min_text_length,
                help="Minimum characters for reliable detection"
            )
    
    with col2:
        # Filtering settings
        st.write("**Filtering Settings:**")
        
        filtering_strategy = st.selectbox(
            "Filtering Strategy:",
            options=[strategy.value for strategy in FilteringStrategy],
            index=list(FilteringStrategy).index(config.filtering_strategy),
            help="How strict to be when filtering languages"
        )
        config.filtering_strategy = FilteringStrategy(filtering_strategy)
        
        config.target_language = st.selectbox(
            "Target Language:",
            options=['en', 'de', 'fr', 'es', 'it', 'pt', 'ru'],
            index=0,
            format_func=lambda x: f"{manager.get_language_name(x)} ({x})",
            help="Language to filter for"
        )
        
        # UI options
        config.show_statistics = st.checkbox(
            "Show Statistics",
            value=config.show_statistics,
            help="Display language statistics"
        )
        
        config.show_visualization = st.checkbox(
            "Show Visualization",
            value=config.show_visualization,
            help="Display language distribution charts"
        )
    
    return config

def render_language_statistics(
    results: LanguageDetectionResults,
    manager: LanguageDetectionManager
) -> None:
    """
    Render comprehensive language statistics.
    
    Args:
        results: Detection results
        manager: Language detection manager
    """
    if not results.statistics:
        return
    
    stats = results.statistics
    
    st.subheader("📊 Language Detection Statistics")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Texts", stats.total_texts)
    with col2:
        st.metric("Successful Detections", stats.successful_detections, 
                 f"{stats.success_rate:.1f}%")
    with col3:
        st.metric("Languages Found", stats.language_diversity)
    with col4:
        if stats.processing_time_average:
            st.metric("Avg. Processing Time", f"{stats.processing_time_average*1000:.1f}ms")
    
    # Language breakdown
    if stats.language_counts:
        st.write("### 🔸 Language Distribution")
        
        # Create display data
        lang_data = []
        for lang, count in sorted(stats.language_counts.items(), key=lambda x: x[1], reverse=True):
            lang_name = manager.get_language_name(lang)
            percentage = stats.language_percentages.get(lang, 0)
            lang_data.append({
                'Language': f"{lang_name} ({lang})",
                'Count': count,
                'Percentage': f"{percentage:.1f}%"
            })
        
        # Show top languages
        display_count = min(len(lang_data), manager.config.max_languages_display)
        st.dataframe(
            pd.DataFrame(lang_data[:display_count]),
            use_container_width=True,
            hide_index=True
        )
    
    # Confidence statistics
    if stats.confidence_stats:
        st.write("### 📈 Confidence Statistics")
        conf_col1, conf_col2, conf_col3 = st.columns(3)
        
        with conf_col1:
            st.metric("Mean Confidence", f"{stats.confidence_stats['mean']:.3f}")
        with conf_col2:
            st.metric("Min Confidence", f"{stats.confidence_stats['min']:.3f}")
        with conf_col3:
            st.metric("Max Confidence", f"{stats.confidence_stats['max']:.3f}")

def render_language_visualization(
    results: LanguageDetectionResults,
    manager: LanguageDetectionManager
) -> None:
    """
    Render language distribution visualizations.
    
    Args:
        results: Detection results
        manager: Language detection manager
    """
    if not results.statistics or not results.statistics.language_counts:
        return
    
    st.subheader("📊 Language Distribution Visualization")
    
    # Prepare data
    lang_counts = results.statistics.language_counts
    top_languages = dict(sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:LanguageDetectionConstants.MAX_LANGUAGES_IN_PIE])
    
    viz_data = []
    for lang, count in top_languages.items():
        lang_name = manager.get_language_name(lang)
        viz_data.append({'Language': lang_name, 'Count': count, 'Code': lang})
    
    if not viz_data:
        return
    
    viz_df = pd.DataFrame(viz_data)
    
    # Create visualization based on config
    if manager.config.visualization_style == VisualizationStyle.PIE_CHART:
        fig = px.pie(
            viz_df, 
            values='Count', 
            names='Language',
            title='Language Distribution',
            color_discrete_sequence=LanguageDetectionConstants.DEFAULT_PIE_COLORS
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
    elif manager.config.visualization_style == VisualizationStyle.BAR_CHART:
        fig = px.bar(
            viz_df.sort_values('Count', ascending=True),
            x='Count',
            y='Language',
            title='Language Distribution',
            orientation='h',
            color='Count',
            color_continuous_scale='viridis'
        )
        
    elif manager.config.visualization_style == VisualizationStyle.DONUT_CHART:
        fig = px.pie(
            viz_df,
            values='Count',
            names='Language',
            title='Language Distribution',
            hole=0.4,
            color_discrete_sequence=LanguageDetectionConstants.DEFAULT_PIE_COLORS
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
    else:  # HORIZONTAL_BAR
        fig = px.bar(
            viz_df,
            x='Language',
            y='Count',
            title='Language Distribution',
            color='Count',
            color_continuous_scale='plasma'
        )
    
    fig.update_layout(
        showlegend=True if manager.config.visualization_style in [VisualizationStyle.PIE_CHART, VisualizationStyle.DONUT_CHART] else False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_filtering_results(
    filtering_result: FilteringResult,
    manager: LanguageDetectionManager
) -> None:
    """
    Render filtering results summary.
    
    Args:
        filtering_result: Filtering result object
        manager: Language detection manager
    """
    st.subheader("🔍 Filtering Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Original Comments", filtering_result.original_count)
    with col2:
        target_lang_name = manager.get_language_name(manager.config.target_language)
        st.metric(f"{target_lang_name} Comments", filtering_result.target_language_count,
                 f"{filtering_result.target_ratio:.1f}%")
    with col3:
        st.metric("Filtered Out", filtering_result.filtered_count,
                 f"{filtering_result.filter_ratio:.1f}%")
    
    # Status indicators
    if filtering_result.target_language_count < 10:
        st.warning(f"⚠️ Only {filtering_result.target_language_count} {manager.get_language_name(manager.config.target_language)} comments found. Analysis results may be unreliable.")
    elif filtering_result.target_ratio < 50:
        st.info(f"ℹ️ {manager.get_language_name(manager.config.target_language)} comments represent {filtering_result.target_ratio:.1f}% of total comments.")
    else:
        st.success(f"✅ Good language filtering results: {filtering_result.target_ratio:.1f}% {manager.get_language_name(manager.config.target_language)} comments.")

# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_language_detection_manager(
    target_language: str = "en",
    confidence_threshold: float = 0.8,
    **kwargs
) -> LanguageDetectionManager:
    """
    Factory function to create a language detection manager.
    
    Args:
        target_language: Target language code
        confidence_threshold: Confidence threshold
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured LanguageDetectionManager
    """
    config = LanguageDetectionConfig(
        target_language=target_language,
        confidence_threshold=confidence_threshold,
        **kwargs
    )
    return LanguageDetectionManager(config)

def create_custom_detection_config(**kwargs) -> LanguageDetectionConfig:
    """
    Factory function to create custom detection configuration.
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        LanguageDetectionConfig object
    """
    return LanguageDetectionConfig(**kwargs)

# =============================================================================
# BACKWARD COMPATIBILITY - LEGACY API
# =============================================================================

def detect_language(text):
    """
    LEGACY: Detect language of a text (backward compatibility).
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code or None
    """
    manager = create_language_detection_manager()
    results = manager.detect_languages([text])
    if results.detection_results:
        return results.detection_results[0].detected_language
    return None

def get_language_name(lang_code):
    """
    LEGACY: Get language name from code (backward compatibility).
    
    Args:
        lang_code: Language code
        
    Returns:
        Human-readable language name
    """
    return SupportedLanguages.LANGUAGE_NAMES.get(
        lang_code, 
        f'Unknown ({lang_code})'
    )

def filter_english_comments(df, text_column):
    """
    LEGACY: Filter DataFrame to English comments (backward compatibility).
    
    Args:
        df: DataFrame with comments
        text_column: Column containing text
        
    Returns:
        Filtered DataFrame
    """
    try:
        # Check if langdetect is available
        from langdetect import detect
        langdetect_available = True
    except ImportError:
        langdetect_available = False
        st.warning("🔄 Language filtering not available. All comments will be analyzed.")
        st.info("💡 To enable language filtering, install: `pip install langdetect`")
        return df
    
    # Show UI for filtering option
    st.write("### 🌍 Language Filtering")
    filter_language = st.checkbox("Only analyze English comments", value=True)
    
    if not filter_language:
        st.info("Language filtering disabled. All comments will be analyzed.")
        return df
    
    # Create manager and perform filtering
    manager = create_language_detection_manager()
    
    try:
        filtered_df, results = manager.filter_english_comments(df, text_column, show_ui=True)
        
        # Show results using legacy UI (simplified)
        if results.statistics and results.statistics.language_counts:
            st.write("### Detected Languages:")
            
            col1, col2 = st.columns(2)
            with col1:
                lang_counts = results.statistics.language_counts
                for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    percentage = (count / results.statistics.total_texts) * 100
                    lang_name = get_language_name(lang)
                    st.write(f"🔸 **{lang_name} ({lang})**: {count} comments ({percentage:.1f}%)")
            
            with col2:
                # Simple pie chart for legacy compatibility
                try:
                    import plotly.express as px
                    
                    pie_data = []
                    for lang, count in list(lang_counts.items())[:5]:
                        pie_data.append({'Language': get_language_name(lang), 'Count': count})
                    
                    if pie_data:
                        pie_df = pd.DataFrame(pie_data)
                        fig = px.pie(pie_df, values='Count', names='Language', 
                                   title='Top 5 Languages in Comments')
                        st.plotly_chart(fig, use_container_width=True)
                except ImportError:
                    pass
        
        # Show filtering results
        if results.filtering_result:
            fr = results.filtering_result
            st.success(f"🔍 **Language filtering completed:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Original", f"{fr.original_count} comments")
            with col2:
                st.metric("English", f"{fr.target_language_count} comments", 
                         f"{fr.target_ratio:.1f}%")
            with col3:
                st.metric("Filtered", f"{fr.filtered_count} comments", 
                         f"{fr.filter_ratio:.1f}%")
            
            # Warning for too few English comments
            if fr.target_language_count < 10:
                st.warning(f"⚠️ Only {fr.target_language_count} English comments found. Analysis results may be unreliable.")
        
        return filtered_df
        
    except Exception as e:
        st.error(f"Language filtering failed: {str(e)}")
        st.info("Proceeding with all comments...")
        return df

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_usage():
    """Example of how to use the enterprise language detection system."""
    
    # Create configuration
    config = LanguageDetectionConfig(
        target_language="en",
        confidence_threshold=0.8,
        show_statistics=True,
        show_visualization=True,
        visualization_style=VisualizationStyle.PIE_CHART
    )
    
    # Create manager
    manager = LanguageDetectionManager(config)
    
    # In Streamlit app:
    if 'language_manager' not in st.session_state:
        st.session_state.language_manager = manager
    
    # Example usage with DataFrame
    sample_data = {
        'comment': [
            "This is a great video!",
            "Das ist ein tolles Video!",
            "C'est une excellente vidéo!",
            "¡Este es un gran video!",
            "Questo è un grande video!"
        ]
    }
    df = pd.DataFrame(sample_data)
    
    # Use UI components
    config = render_language_filtering_ui(manager)
    
    # Perform detection and filtering
    filtered_df, results = manager.filter_english_comments(df, 'comment')
    
    # Render results
    render_language_statistics(results, manager)
    render_language_visualization(results, manager)
    
    if results.filtering_result:
        render_filtering_results(results.filtering_result, manager)

if __name__ == "__main__":
    example_usage()