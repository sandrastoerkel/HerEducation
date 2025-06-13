"""
🎯 COUNTRY ANALYSIS STORAGE ENGLISH - Enterprise Storage System
Modernized Storage Solution for English Comment Analysis with Smart Labels Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import pickle
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback

# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class StorageConstantsEnglish:
    """Central Constants for English Storage System"""
    
    # Directories
    RESULTS_DIR = "saved_results_english"
    COUNTRY_ANALYSIS_SUBDIR = "country_analysis"
    
    # File Extensions
    CSV_EXTENSION = ".csv"
    JSON_EXTENSION = ".json"
    PICKLE_EXTENSION = ".pkl"
    
    # CSV Columns
    SMART_LABELS_COLUMN = "smart_topic_labels"
    COUNTRY_COLUMN = "detected_country"
    ANALYSIS_SOURCE_COLUMN = "analysis_source"
    EXPORT_TIMESTAMP_COLUMN = "export_timestamp"
    
    # Metadata Keys
    SMART_LABELS_KEY = "smart_labels"
    TOPIC_LABELS_KEY = "topic_labels"
    COMBINED_LABELS_KEY = "combined_topic_labels"
    
    # Session State Keys (English)
    SESSION_COMBINED_LABELS = "combined_topic_labels"
    SESSION_CUSTOM_LABELS = "custom_topic_labels"
    SESSION_TOPIC_LABELS = "topic_labels"
    
    # Logging
    LOGGER_NAME = "country_storage_english"


class ExportFormatEnglish(Enum):
    """Available Export Formats"""
    CSV_ONLY = "csv_only"
    CSV_WITH_METADATA = "csv_with_metadata"
    FULL_EXPORT = "full_export"


class CountryDetectionMethodEnglish(Enum):
    """Country Detection Methods"""
    FILENAME_BASED = "filename"
    METADATA_BASED = "metadata"
    MANUAL = "manual"
    FALLBACK = "fallback"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class SmartLabelsInfoEnglish:
    """Information about Smart Labels"""
    labels_dict: Dict[int, str]
    total_topics: int
    labeling_method: str
    extraction_timestamp: datetime
    session_state_available: bool = False
    
    @property
    def has_labels(self) -> bool:
        """Check if labels are available"""
        return bool(self.labels_dict) and self.total_topics > 0


@dataclass
class CountryAnalysisExportConfigEnglish:
    """Configuration for Country Analysis Export"""
    include_smart_labels: bool = True
    include_country_detection: bool = True
    include_metadata_columns: bool = True
    export_format: ExportFormatEnglish = ExportFormatEnglish.CSV_WITH_METADATA
    add_timestamp: bool = True
    validate_data: bool = True
    
    # Country Detection
    country_detection_method: CountryDetectionMethodEnglish = CountryDetectionMethodEnglish.FILENAME_BASED
    fallback_country: str = "International (English)"
    
    # File Options
    create_subdirectory: bool = True
    preserve_original_data: bool = True


@dataclass
class ExportResultEnglish:
    """Result of an Export Operation"""
    success: bool
    file_path: Optional[Path]
    exported_rows: int
    added_columns: List[str]
    smart_labels_added: int
    country_detected: Optional[str]
    export_timestamp: datetime
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    @property
    def summary(self) -> str:
        """Export Summary"""
        if self.success:
            return f"✅ Export successful: {self.exported_rows} rows, {len(self.added_columns)} new columns"
        else:
            return f"❌ Export failed: {self.error_message}"


# =============================================================================
# SPECIALIZED COMPONENTS
# =============================================================================

class SmartLabelsExtractorEnglish:
    """Extracts Smart Labels from Session State and Additional Data"""
    
    def __init__(self):
        self.logger = logging.getLogger(StorageConstantsEnglish.LOGGER_NAME)
    
    def extract_from_session_state(self) -> SmartLabelsInfoEnglish:
        """Extracts Smart Labels from Streamlit Session State
        
        Returns:
            SmartLabelsInfoEnglish object
        """
        try:
            labels_dict = {}
            labeling_method = "unknown"
            session_available = False
            
            # Prioritized order of Session State keys
            session_keys = [
                StorageConstantsEnglish.SESSION_COMBINED_LABELS,
                StorageConstantsEnglish.SESSION_CUSTOM_LABELS,
                StorageConstantsEnglish.SESSION_TOPIC_LABELS
            ]
            
            for key in session_keys:
                if hasattr(st.session_state, key):
                    session_data = getattr(st.session_state, key)
                    if session_data and isinstance(session_data, dict):
                        labels_dict = session_data
                        labeling_method = f"session_state_{key}"
                        session_available = True
                        self.logger.info(f"Smart Labels extracted from Session State: {key}")
                        break
            
            return SmartLabelsInfoEnglish(
                labels_dict=labels_dict,
                total_topics=len(labels_dict),
                labeling_method=labeling_method,
                extraction_timestamp=datetime.now(),
                session_state_available=session_available
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting Smart Labels: {e}")
            return SmartLabelsInfoEnglish(
                labels_dict={},
                total_topics=0,
                labeling_method="error",
                extraction_timestamp=datetime.now()
            )
    
    def extract_from_additional_data(self, additional_data: Dict[str, Any]) -> SmartLabelsInfoEnglish:
        """Extracts Smart Labels from additional analysis data
        
        Args:
            additional_data: Additional data from analysis
            
        Returns:
            SmartLabelsInfoEnglish object
        """
        try:
            labels_dict = {}
            labeling_method = "additional_data"
            
            # Search for labels in additional data
            if StorageConstantsEnglish.SMART_LABELS_KEY in additional_data:
                labels_dict = additional_data[StorageConstantsEnglish.SMART_LABELS_KEY]
            elif StorageConstantsEnglish.TOPIC_LABELS_KEY in additional_data:
                labels_dict = additional_data[StorageConstantsEnglish.TOPIC_LABELS_KEY]
            elif StorageConstantsEnglish.COMBINED_LABELS_KEY in additional_data:
                labels_dict = additional_data[StorageConstantsEnglish.COMBINED_LABELS_KEY]
            
            return SmartLabelsInfoEnglish(
                labels_dict=labels_dict if isinstance(labels_dict, dict) else {},
                total_topics=len(labels_dict) if isinstance(labels_dict, dict) else 0,
                labeling_method=labeling_method,
                extraction_timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting from additional data: {e}")
            return SmartLabelsInfoEnglish(
                labels_dict={},
                total_topics=0,
                labeling_method="error",
                extraction_timestamp=datetime.now()
            )


class CountryDetectorEnglish:
    """Detects Countries from Filenames and Metadata"""
    
    def __init__(self):
        self.logger = logging.getLogger(StorageConstantsEnglish.LOGGER_NAME)
        
        # English Country Patterns (expanded for global coverage)
        self.country_patterns = {
            'United States': [
                'usa', 'america', 'american', 'united_states', 'washington', 'new_york',
                'us_', '_us', 'cnn', 'fox', 'nbc', 'abc', 'cbs'
            ],
            'United Kingdom': [
                'uk', 'britain', 'british', 'england', 'london', 'scotland', 'wales',
                'gb_', '_gb', 'bbc', 'itv', 'channel4'
            ],
            'Canada': [
                'canada', 'canadian', 'toronto', 'vancouver', 'montreal', 'ottawa',
                'ca_', '_ca', 'cbc', 'ctv'
            ],
            'Australia': [
                'australia', 'australian', 'sydney', 'melbourne', 'brisbane', 'perth',
                'au_', '_au', 'abc_au', 'sbs'
            ],
            'New Zealand': [
                'new_zealand', 'newzealand', 'nz', 'auckland', 'wellington',
                'nz_', '_nz'
            ],
            'Germany': [
                'germany', 'german', 'deutschland', 'deutsch', 'berlin', 'munich',
                'de_', '_de', 'dw', 'ard', 'zdf'
            ],
            'France': [
                'france', 'french', 'paris', 'lyon', 'marseille',
                'fr_', '_fr', 'france24', 'tf1'
            ],
            'Spain': [
                'spain', 'spanish', 'madrid', 'barcelona', 'espana',
                'es_', '_es', 'rtve'
            ],
            'Italy': [
                'italy', 'italian', 'rome', 'milan', 'italia',
                'it_', '_it', 'rai'
            ],
            'Netherlands': [
                'netherlands', 'dutch', 'amsterdam', 'holland',
                'nl_', '_nl', 'nos'
            ],
            'India': [
                'india', 'indian', 'mumbai', 'delhi', 'bangalore', 'kolkata',
                'in_', '_in', 'ndtv', 'times_now'
            ],
            'Japan': [
                'japan', 'japanese', 'tokyo', 'osaka', 'kyoto',
                'jp_', '_jp', 'nhk', 'tbs'
            ],
            'South Korea': [
                'korea', 'korean', 'south_korea', 'seoul', 'busan',
                'kr_', '_kr', 'kbs', 'mbc'
            ],
            'China': [
                'china', 'chinese', 'beijing', 'shanghai', 'guangzhou',
                'cn_', '_cn', 'cgtn', 'xinhua'
            ],
            'Singapore': [
                'singapore', 'singaporean', 'sg_', '_sg'
            ],
            'Malaysia': [
                'malaysia', 'malaysian', 'kuala_lumpur', 'penang', 'johor',
                'my_', '_my'
            ],
            'Philippines': [
                'philippines', 'filipino', 'manila', 'cebu',
                'ph_', '_ph', 'abs_cbn', 'gma'
            ],
            'Thailand': [
                'thailand', 'thai', 'bangkok', 'phuket',
                'th_', '_th'
            ],
            'Indonesia': [
                'indonesia', 'indonesian', 'jakarta', 'bali',
                'id_', '_id'
            ],
            'Brazil': [
                'brazil', 'brazilian', 'sao_paulo', 'rio', 'brasilia',
                'br_', '_br', 'globo'
            ],
            'Mexico': [
                'mexico', 'mexican', 'mexico_city', 'guadalajara',
                'mx_', '_mx', 'televisa'
            ],
            'Argentina': [
                'argentina', 'argentinian', 'buenos_aires', 'cordoba',
                'ar_', '_ar'
            ],
            'South Africa': [
                'south_africa', 'southafrican', 'johannesburg', 'cape_town',
                'za_', '_za', 'sabc'
            ],
            'Nigeria': [
                'nigeria', 'nigerian', 'lagos', 'abuja',
                'ng_', '_ng'
            ],
            'Kenya': [
                'kenya', 'kenyan', 'nairobi', 'mombasa',
                'ke_', '_ke'
            ],
            'Egypt': [
                'egypt', 'egyptian', 'cairo', 'alexandria',
                'eg_', '_eg'
            ],
            'Israel': [
                'israel', 'israeli', 'jerusalem', 'tel_aviv',
                'il_', '_il'
            ],
            'Turkey': [
                'turkey', 'turkish', 'ankara', 'istanbul',
                'tr_', '_tr', 'trt'
            ],
            'Russia': [
                'russia', 'russian', 'moscow', 'st_petersburg',
                'ru_', '_ru', 'rt', 'sputnik'
            ],
            'Ukraine': [
                'ukraine', 'ukrainian', 'kyiv', 'kiev', 'odessa',
                'ua_', '_ua'
            ],
            'Poland': [
                'poland', 'polish', 'warsaw', 'krakow',
                'pl_', '_pl'
            ],
            'Sweden': [
                'sweden', 'swedish', 'stockholm', 'gothenburg',
                'se_', '_se', 'svt'
            ],
            'Norway': [
                'norway', 'norwegian', 'oslo', 'bergen',
                'no_', '_no', 'nrk'
            ],
            'Denmark': [
                'denmark', 'danish', 'copenhagen', 'aarhus',
                'dk_', '_dk', 'dr'
            ],
            'Finland': [
                'finland', 'finnish', 'helsinki', 'tampere',
                'fi_', '_fi', 'yle'
            ]
        }
    
    def detect_country(
        self,
        filename: str,
        config: CountryAnalysisExportConfigEnglish,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, CountryDetectionMethodEnglish]:
        """Detects country based on filename and metadata
        
        Args:
            filename: Filename
            config: Export configuration
            metadata: Optional metadata
            
        Returns:
            Tuple of (detected_country, detection_method)
        """
        try:
            filename_lower = filename.lower()
            
            # Filename-based detection
            if config.country_detection_method == CountryDetectionMethodEnglish.FILENAME_BASED:
                # Score-based detection for better accuracy
                country_scores = {}
                
                for country, patterns in self.country_patterns.items():
                    score = 0
                    for pattern in patterns:
                        if pattern in filename_lower:
                            # Different scoring based on pattern type
                            if pattern.endswith('_') or pattern.startswith('_'):
                                score += 3  # Country codes get higher score
                            elif pattern in ['usa', 'uk', 'cnn', 'bbc', 'abc']:
                                score += 2  # Major identifiers get medium score
                            else:
                                score += 1  # Regular patterns get base score
                
                if country_scores:
                    best_country = max(country_scores.keys(), key=lambda k: country_scores[k])
                    self.logger.info(f"Country detected from filename: {best_country} (Score: {country_scores[best_country]})")
                    return best_country, CountryDetectionMethodEnglish.FILENAME_BASED
            
            # Metadata-based detection
            if (config.country_detection_method == CountryDetectionMethodEnglish.METADATA_BASED 
                and metadata):
                
                metadata_text = str(metadata).lower()
                for country, patterns in self.country_patterns.items():
                    for pattern in patterns:
                        if pattern in metadata_text:
                            self.logger.info(f"Country detected from metadata: {country}")
                            return country, CountryDetectionMethodEnglish.METADATA_BASED
            
            # Fallback
            self.logger.warning(f"No country detected, fallback to: {config.fallback_country}")
            return config.fallback_country, CountryDetectionMethodEnglish.FALLBACK
            
        except Exception as e:
            self.logger.error(f"Error in country detection: {e}")
            return config.fallback_country, CountryDetectionMethodEnglish.FALLBACK


class DataValidatorEnglish:
    """Validates Data before Export"""
    
    def __init__(self):
        self.logger = logging.getLogger(StorageConstantsEnglish.LOGGER_NAME)
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validates DataFrame for Country Analysis Export
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, warnings_list)
        """
        warnings = []
        is_valid = True
        
        try:
            # Basic validations
            if df.empty:
                warnings.append("DataFrame is empty")
                is_valid = False
                return is_valid, warnings
            
            # Check required columns
            required_columns = ['topic', 'dominant_emotion', 'sentiment']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                warnings.append(f"Missing columns for Country Analysis: {missing_columns}")
                # Don't mark as invalid since Country Analysis can work without some columns
            
            # Validate topic column
            if 'topic' in df.columns:
                topic_stats = df['topic'].describe()
                if topic_stats['count'] == 0:
                    warnings.append("No valid topic assignments found")
                elif topic_stats['count'] < len(df) * 0.5:
                    warnings.append(f"Only {topic_stats['count']}/{len(df)} comments have topic assignments")
            
            # Validate emotion column
            if 'dominant_emotion' in df.columns:
                emotion_null_count = df['dominant_emotion'].isnull().sum()
                if emotion_null_count > len(df) * 0.1:
                    warnings.append(f"{emotion_null_count} comments have no emotion assignment")
            
            # Validate sentiment column
            if 'sentiment' in df.columns:
                sentiment_null_count = df['sentiment'].isnull().sum()
                if sentiment_null_count > len(df) * 0.1:
                    warnings.append(f"{sentiment_null_count} comments have no sentiment assignment")
            
            self.logger.info(f"DataFrame validated: {len(warnings)} warnings")
            return is_valid, warnings
            
        except Exception as e:
            self.logger.error(f"Error in DataFrame validation: {e}")
            warnings.append(f"Validation error: {str(e)}")
            return False, warnings
    
    def validate_smart_labels(self, smart_labels_info: SmartLabelsInfoEnglish, df: pd.DataFrame) -> List[str]:
        """Validates Smart Labels against DataFrame
        
        Args:
            smart_labels_info: Smart Labels information
            df: DataFrame with topic data
            
        Returns:
            List of warnings
        """
        warnings = []
        
        try:
            if not smart_labels_info.has_labels:
                warnings.append("No Smart Labels available")
                return warnings
            
            if 'topic' not in df.columns:
                warnings.append("No topic column in DataFrame for Smart Labels")
                return warnings
            
            # Check topic coverage
            df_topics = set(df['topic'].dropna().astype(int))
            label_topics = set(smart_labels_info.labels_dict.keys())
            
            missing_labels = df_topics - label_topics
            if missing_labels:
                warnings.append(f"Smart Labels missing for topics: {sorted(missing_labels)}")
            
            unused_labels = label_topics - df_topics
            if unused_labels:
                warnings.append(f"Unused Smart Labels for topics: {sorted(unused_labels)}")
            
            coverage = len(label_topics & df_topics) / len(df_topics) if df_topics else 0
            if coverage < 0.8:
                warnings.append(f"Smart Labels cover only {coverage:.1%} of topics")
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"Error in Smart Labels validation: {e}")
            warnings.append(f"Smart Labels validation error: {str(e)}")
            return warnings


class CountryAnalysisExporterEnglish:
    """Exports Data for Country Analysis"""
    
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.logger = logging.getLogger(StorageConstantsEnglish.LOGGER_NAME)
    
    def export_dataframe(
        self,
        df: pd.DataFrame,
        filename: str,
        smart_labels_info: SmartLabelsInfoEnglish,
        config: CountryAnalysisExportConfigEnglish,
        country: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExportResultEnglish:
        """Exports DataFrame with Smart Labels for Country Analysis
        
        Args:
            df: DataFrame to export
            filename: Original filename
            smart_labels_info: Smart Labels information
            config: Export configuration
            country: Detected country
            metadata: Optional metadata
            
        Returns:
            ExportResultEnglish object
        """
        try:
            export_df = df.copy()
            added_columns = []
            warnings = []
            
            # Add Smart Labels
            if config.include_smart_labels and smart_labels_info.has_labels:
                if 'topic' in export_df.columns:
                    export_df[StorageConstantsEnglish.SMART_LABELS_COLUMN] = (
                        export_df['topic'].map(smart_labels_info.labels_dict)
                    )
                    added_columns.append(StorageConstantsEnglish.SMART_LABELS_COLUMN)
                    self.logger.info(f"Smart Labels column added: {len(smart_labels_info.labels_dict)} labels")
                else:
                    warnings.append("No topic column available for Smart Labels")
            
            # Add Country Detection
            if config.include_country_detection:
                export_df[StorageConstantsEnglish.COUNTRY_COLUMN] = country
                added_columns.append(StorageConstantsEnglish.COUNTRY_COLUMN)
            
            # Add metadata columns
            if config.include_metadata_columns:
                export_df[StorageConstantsEnglish.ANALYSIS_SOURCE_COLUMN] = filename
                added_columns.append(StorageConstantsEnglish.ANALYSIS_SOURCE_COLUMN)
                
                if config.add_timestamp:
                    export_df[StorageConstantsEnglish.EXPORT_TIMESTAMP_COLUMN] = datetime.now().isoformat()
                    added_columns.append(StorageConstantsEnglish.EXPORT_TIMESTAMP_COLUMN)
            
            # Create target directory
            target_dir = self.results_dir
            if config.create_subdirectory:
                target_dir = self.results_dir / StorageConstantsEnglish.COUNTRY_ANALYSIS_SUBDIR
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(filename).stem
            export_filename = f"{base_name}_country_analysis_{timestamp}{StorageConstantsEnglish.CSV_EXTENSION}"
            export_path = target_dir / export_filename
            
            # Export
            export_df.to_csv(export_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Country Analysis Export successful: {export_path}")
            
            return ExportResultEnglish(
                success=True,
                file_path=export_path,
                exported_rows=len(export_df),
                added_columns=added_columns,
                smart_labels_added=len(smart_labels_info.labels_dict),
                country_detected=country,
                export_timestamp=datetime.now(),
                warnings=warnings
            )
            
        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return ExportResultEnglish(
                success=False,
                file_path=None,
                exported_rows=0,
                added_columns=[],
                smart_labels_added=0,
                country_detected=country,
                export_timestamp=datetime.now(),
                error_message=error_msg
            )


# =============================================================================
# MAIN MANAGER CLASS
# =============================================================================

class CountryAnalysisStorageEnglish:
    """Central Manager for English Country Analysis Storage Operations"""
    
    def __init__(self, results_dir: Optional[Union[str, Path]] = None):
        """Initializes the Storage Manager
        
        Args:
            results_dir: Optional results directory (default: saved_results_english)
        """
        self.results_dir = Path(results_dir or StorageConstantsEnglish.RESULTS_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.smart_labels_extractor = SmartLabelsExtractorEnglish()
        self.country_detector = CountryDetectorEnglish()
        self.data_validator = DataValidatorEnglish()
        self.exporter = CountryAnalysisExporterEnglish(self.results_dir)
        
        self.logger = logging.getLogger(StorageConstantsEnglish.LOGGER_NAME)
        
        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def export_with_smart_labels(
        self,
        df: pd.DataFrame,
        filename: str,
        additional_data: Optional[Dict[str, Any]] = None,
        config: Optional[CountryAnalysisExportConfigEnglish] = None
    ) -> ExportResultEnglish:
        """Exports DataFrame with Smart Labels for Country Analysis
        
        Args:
            df: DataFrame to export
            filename: Original filename
            additional_data: Additional analysis data
            config: Optional export configuration
            
        Returns:
            ExportResultEnglish object
        """
        if config is None:
            config = CountryAnalysisExportConfigEnglish()
        
        try:
            self.logger.info(f"Starting Country Analysis Export for: {filename}")
            
            # Validate data
            if config.validate_data:
                is_valid, validation_warnings = self.data_validator.validate_dataframe(df)
                if not is_valid:
                    return ExportResultEnglish(
                        success=False,
                        file_path=None,
                        exported_rows=0,
                        added_columns=[],
                        smart_labels_added=0,
                        country_detected=None,
                        export_timestamp=datetime.now(),
                        error_message="DataFrame validation failed",
                        warnings=validation_warnings
                    )
            
            # Extract Smart Labels
            smart_labels_info = self.smart_labels_extractor.extract_from_session_state()
            
            # Fallback to additional_data if Session State is empty
            if not smart_labels_info.has_labels and additional_data:
                smart_labels_info = self.smart_labels_extractor.extract_from_additional_data(additional_data)
            
            # Validate Smart Labels
            if config.include_smart_labels:
                label_warnings = self.data_validator.validate_smart_labels(smart_labels_info, df)
                if label_warnings:
                    self.logger.warning(f"Smart Labels warnings: {label_warnings}")
            
            # Detect country
            country, detection_method = self.country_detector.detect_country(
                filename, config, additional_data
            )
            
            # Export
            result = self.exporter.export_dataframe(
                df, filename, smart_labels_info, config, country, additional_data
            )
            
            if result.success:
                self.logger.info(f"Country Analysis Export successful: {result.summary}")
            else:
                self.logger.error(f"Country Analysis Export failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in Country Analysis Export: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return ExportResultEnglish(
                success=False,
                file_path=None,
                exported_rows=0,
                added_columns=[],
                smart_labels_added=0,
                country_detected=None,
                export_timestamp=datetime.now(),
                error_message=error_msg
            )
    
    def get_available_country_analyses(self) -> List[Dict[str, Any]]:
        """Returns available Country Analysis files
        
        Returns:
            List of analysis information
        """
        try:
            country_dir = self.results_dir / StorageConstantsEnglish.COUNTRY_ANALYSIS_SUBDIR
            if not country_dir.exists():
                return []
            
            analyses = []
            for csv_file in country_dir.glob(f"*_country_analysis_*{StorageConstantsEnglish.CSV_EXTENSION}"):
                try:
                    # Extract basic information
                    file_info = {
                        'filename': csv_file.name,
                        'path': str(csv_file),
                        'size': csv_file.stat().st_size,
                        'modified': datetime.fromtimestamp(csv_file.stat().st_mtime),
                        'country': 'International (English)'  # Default for English analyses
                    }
                    
                    # Try to extract additional information from CSV
                    try:
                        df_sample = pd.read_csv(csv_file, nrows=1)
                        file_info['columns'] = list(df_sample.columns)
                        file_info['has_smart_labels'] = StorageConstantsEnglish.SMART_LABELS_COLUMN in df_sample.columns
                        file_info['has_country_info'] = StorageConstantsEnglish.COUNTRY_COLUMN in df_sample.columns
                        
                        # Extract country if available
                        if StorageConstantsEnglish.COUNTRY_COLUMN in df_sample.columns:
                            file_info['country'] = df_sample[StorageConstantsEnglish.COUNTRY_COLUMN].iloc[0]
                        
                    except Exception as e:
                        self.logger.warning(f"Could not analyze CSV {csv_file.name}: {e}")
                        file_info['has_smart_labels'] = False
                        file_info['has_country_info'] = False
                    
                    analyses.append(file_info)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing file {csv_file}: {e}")
                    continue
            
            # Sort by modification date (newest first)
            analyses.sort(key=lambda x: x['modified'], reverse=True)
            
            self.logger.info(f"Found Country Analysis files: {len(analyses)}")
            return analyses
            
        except Exception as e:
            self.logger.error(f"Error listing Country Analysis files: {e}")
            return []
    
    def create_export_config(
        self,
        include_smart_labels: bool = True,
        include_country_detection: bool = True,
        fallback_country: str = "International (English)",
        **kwargs
    ) -> CountryAnalysisExportConfigEnglish:
        """Factory method for export configuration
        
        Args:
            include_smart_labels: Include Smart Labels
            include_country_detection: Include country detection
            fallback_country: Fallback country
            **kwargs: Additional configuration options
            
        Returns:
            CountryAnalysisExportConfigEnglish object
        """
        return CountryAnalysisExportConfigEnglish(
            include_smart_labels=include_smart_labels,
            include_country_detection=include_country_detection,
            fallback_country=fallback_country,
            **kwargs
        )


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_country_analysis_export_config_english() -> CountryAnalysisExportConfigEnglish:
    """Renders UI for Country Analysis Export Configuration"""
    st.subheader("🌍 Country Analysis Export Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_smart_labels = st.checkbox(
            "Include Smart Labels", 
            value=True,
            help="Adds Smart Topic Labels to export CSV"
        )
        
        include_country_detection = st.checkbox(
            "Enable Country Detection",
            value=True,
            help="Detects and adds country based on filename"
        )
        
        add_timestamp = st.checkbox(
            "Add Export Timestamp",
            value=True
        )
    
    with col2:
        fallback_country = st.selectbox(
            "Fallback Country:",
            options=[
                "International (English)", "United States", "United Kingdom", 
                "Canada", "Australia", "New Zealand", "India", "Singapore"
            ],
            index=0
        )
        
        export_format = st.selectbox(
            "Export Format:",
            options=[fmt.value for fmt in ExportFormatEnglish],
            index=1,  # CSV_WITH_METADATA
            format_func=lambda x: {
                "csv_only": "CSV Only",
                "csv_with_metadata": "CSV with Metadata",
                "full_export": "Full Export"
            }.get(x, x)
        )
        
        create_subdirectory = st.checkbox(
            "Create Subdirectory",
            value=True,
            help="Creates 'country_analysis' subdirectory"
        )
    
    return CountryAnalysisExportConfigEnglish(
        include_smart_labels=include_smart_labels,
        include_country_detection=include_country_detection,
        add_timestamp=add_timestamp,
        fallback_country=fallback_country,
        export_format=ExportFormatEnglish(export_format),
        create_subdirectory=create_subdirectory
    )


def render_export_result_english(result: ExportResultEnglish) -> None:
    """Renders Export Result"""
    if result.success:
        st.success(result.summary)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Exported Rows", result.exported_rows)
        
        with col2:
            st.metric("New Columns", len(result.added_columns))
        
        with col3:
            st.metric("Smart Labels", result.smart_labels_added)
        
        if result.file_path:
            st.info(f"📁 Saved to: `{result.file_path}`")
        
        if result.country_detected:
            st.info(f"🌍 Detected Country: **{result.country_detected}**")
        
        if result.added_columns:
            st.write("**Added Columns:**")
            for col in result.added_columns:
                st.write(f"- `{col}`")
        
        if result.warnings:
            st.warning("⚠️ Warnings:")
            for warning in result.warnings:
                st.write(f"- {warning}")
    
    else:
        st.error(result.summary)
        if result.warnings:
            for warning in result.warnings:
                st.warning(warning)


# =============================================================================
# BACKWARD COMPATIBILITY & CONVENIENCE FUNCTIONS
# =============================================================================

def export_for_country_analysis_english(
    df: pd.DataFrame,
    filename: str,
    additional_data: Optional[Dict[str, Any]] = None,
    results_dir: Optional[str] = None
) -> bool:
    """Convenience function for Country Analysis Export
    
    Args:
        df: DataFrame to export
        filename: Filename
        additional_data: Additional data
        results_dir: Results directory
        
    Returns:
        True if successful
    """
    storage = CountryAnalysisStorageEnglish(results_dir)
    result = storage.export_with_smart_labels(df, filename, additional_data)
    return result.success


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Main Manager
    'CountryAnalysisStorageEnglish',
    
    # Data Models
    'SmartLabelsInfoEnglish',
    'CountryAnalysisExportConfigEnglish', 
    'ExportResultEnglish',
    
    # Enums
    'ExportFormatEnglish',
    'CountryDetectionMethodEnglish',
    
    # Components
    'SmartLabelsExtractorEnglish',
    'CountryDetectorEnglish',
    'DataValidatorEnglish',
    'CountryAnalysisExporterEnglish',
    
    # UI Functions
    'render_country_analysis_export_config_english',
    'render_export_result_english',
    
    # Convenience Functions
    'export_for_country_analysis_english',
    
    # Constants
    'StorageConstantsEnglish'
]