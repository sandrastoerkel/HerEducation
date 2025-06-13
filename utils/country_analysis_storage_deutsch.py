"""
🎯 COUNTRY ANALYSIS STORAGE DEUTSCH - Enterprise Storage System
Modernisierte Storage-Lösung für deutsche Kommentaranalyse mit Smart Labels Integration
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

class StorageConstants:
    """Zentrale Konstanten für Storage-System"""
    
    # Verzeichnisse
    RESULTS_DIR = "saved_results"
    COUNTRY_ANALYSIS_SUBDIR = "country_analysis"
    
    # Datei-Extensions
    CSV_EXTENSION = ".csv"
    JSON_EXTENSION = ".json"
    PICKLE_EXTENSION = ".pkl"
    
    # CSV-Spalten
    SMART_LABELS_COLUMN = "smart_topic_labels"
    COUNTRY_COLUMN = "detected_country"
    ANALYSIS_SOURCE_COLUMN = "analysis_source"
    EXPORT_TIMESTAMP_COLUMN = "export_timestamp"
    
    # Metadaten-Keys
    SMART_LABELS_KEY = "smart_labels"
    TOPIC_LABELS_KEY = "topic_labels"
    COMBINED_LABELS_KEY = "combined_topic_labels"
    
    # Session State Keys (Deutsch)
    SESSION_COMBINED_LABELS = "combined_topic_labels"
    SESSION_CUSTOM_LABELS = "custom_topic_labels"
    SESSION_TOPIC_LABELS = "topic_labels"
    
    # Logging
    LOGGER_NAME = "country_storage_deutsch"


class ExportFormat(Enum):
    """Verfügbare Export-Formate"""
    CSV_ONLY = "csv_only"
    CSV_WITH_METADATA = "csv_with_metadata"
    FULL_EXPORT = "full_export"


class CountryDetectionMethod(Enum):
    """Methoden zur Länder-Erkennung"""
    FILENAME_BASED = "filename"
    METADATA_BASED = "metadata"
    MANUAL = "manual"
    FALLBACK = "fallback"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class SmartLabelsInfo:
    """Informationen über Smart Labels"""
    labels_dict: Dict[int, str]
    total_topics: int
    labeling_method: str
    extraction_timestamp: datetime
    session_state_available: bool = False
    
    @property
    def has_labels(self) -> bool:
        """Prüft ob Labels vorhanden sind"""
        return bool(self.labels_dict) and self.total_topics > 0


@dataclass
class CountryAnalysisExportConfig:
    """Konfiguration für Country Analysis Export"""
    include_smart_labels: bool = True
    include_country_detection: bool = True
    include_metadata_columns: bool = True
    export_format: ExportFormat = ExportFormat.CSV_WITH_METADATA
    add_timestamp: bool = True
    validate_data: bool = True
    
    # Länder-Erkennung
    country_detection_method: CountryDetectionMethod = CountryDetectionMethod.FILENAME_BASED
    fallback_country: str = "Deutschland"
    
    # Datei-Optionen
    create_subdirectory: bool = True
    preserve_original_data: bool = True


@dataclass
class ExportResult:
    """Ergebnis eines Export-Vorgangs"""
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
        """Zusammenfassung des Exports"""
        if self.success:
            return f"✅ Export erfolgreich: {self.exported_rows} Zeilen, {len(self.added_columns)} neue Spalten"
        else:
            return f"❌ Export fehlgeschlagen: {self.error_message}"


# =============================================================================
# SPECIALIZED COMPONENTS
# =============================================================================

class SmartLabelsExtractor:
    """Extrahiert Smart Labels aus Session State und Zusatzdaten"""
    
    def __init__(self):
        self.logger = logging.getLogger(StorageConstants.LOGGER_NAME)
    
    def extract_from_session_state(self) -> SmartLabelsInfo:
        """Extrahiert Smart Labels aus Streamlit Session State
        
        Returns:
            SmartLabelsInfo-Objekt
        """
        try:
            labels_dict = {}
            labeling_method = "unknown"
            session_available = False
            
            # Priorisierte Reihenfolge der Session State Keys
            session_keys = [
                StorageConstants.SESSION_COMBINED_LABELS,
                StorageConstants.SESSION_CUSTOM_LABELS,
                StorageConstants.SESSION_TOPIC_LABELS
            ]
            
            for key in session_keys:
                if hasattr(st.session_state, key):
                    session_data = getattr(st.session_state, key)
                    if session_data and isinstance(session_data, dict):
                        labels_dict = session_data
                        labeling_method = f"session_state_{key}"
                        session_available = True
                        self.logger.info(f"Smart Labels aus Session State extrahiert: {key}")
                        break
            
            return SmartLabelsInfo(
                labels_dict=labels_dict,
                total_topics=len(labels_dict),
                labeling_method=labeling_method,
                extraction_timestamp=datetime.now(),
                session_state_available=session_available
            )
            
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren der Smart Labels: {e}")
            return SmartLabelsInfo(
                labels_dict={},
                total_topics=0,
                labeling_method="error",
                extraction_timestamp=datetime.now()
            )
    
    def extract_from_additional_data(self, additional_data: Dict[str, Any]) -> SmartLabelsInfo:
        """Extrahiert Smart Labels aus zusätzlichen Analysedaten
        
        Args:
            additional_data: Zusätzliche Daten aus der Analyse
            
        Returns:
            SmartLabelsInfo-Objekt
        """
        try:
            labels_dict = {}
            labeling_method = "additional_data"
            
            # Suche nach Labels in zusätzlichen Daten
            if StorageConstants.SMART_LABELS_KEY in additional_data:
                labels_dict = additional_data[StorageConstants.SMART_LABELS_KEY]
            elif StorageConstants.TOPIC_LABELS_KEY in additional_data:
                labels_dict = additional_data[StorageConstants.TOPIC_LABELS_KEY]
            elif StorageConstants.COMBINED_LABELS_KEY in additional_data:
                labels_dict = additional_data[StorageConstants.COMBINED_LABELS_KEY]
            
            return SmartLabelsInfo(
                labels_dict=labels_dict if isinstance(labels_dict, dict) else {},
                total_topics=len(labels_dict) if isinstance(labels_dict, dict) else 0,
                labeling_method=labeling_method,
                extraction_timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren aus zusätzlichen Daten: {e}")
            return SmartLabelsInfo(
                labels_dict={},
                total_topics=0,
                labeling_method="error",
                extraction_timestamp=datetime.now()
            )


class CountryDetector:
    """Erkennt Länder aus Dateinamen und Metadaten"""
    
    def __init__(self):
        self.logger = logging.getLogger(StorageConstants.LOGGER_NAME)
        
        # Deutsche Länder-Pattern
        self.country_patterns = {
            'Deutschland': [
                'deutsch', 'germany', 'german', 'berlin', 'münchen', 'hamburg',
                'de_', '_de', 'ard', 'zdf', 'rtl', 'lanz', 'hart_aber_fair'
            ],
            'Österreich': [
                'österreich', 'austria', 'austrian', 'wien', 'salzburg',
                'at_', '_at', 'orf'
            ],
            'Schweiz': [
                'schweiz', 'switzerland', 'swiss', 'zürich', 'bern',
                'ch_', '_ch', 'srf'
            ],
            'USA': [
                'usa', 'america', 'american', 'united_states', 'washington',
                'us_', '_us'
            ],
            'Vereinigtes Königreich': [
                'uk', 'britain', 'british', 'england', 'london',
                'gb_', '_gb', 'bbc'
            ]
        }
    
    def detect_country(
        self,
        filename: str,
        config: CountryAnalysisExportConfig,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, CountryDetectionMethod]:
        """Erkennt Land basierend auf Dateiname und Metadaten
        
        Args:
            filename: Dateiname
            config: Export-Konfiguration
            metadata: Optionale Metadaten
            
        Returns:
            Tuple von (erkanntes_land, erkennungs_methode)
        """
        try:
            filename_lower = filename.lower()
            
            # Dateiname-basierte Erkennung
            if config.country_detection_method == CountryDetectionMethod.FILENAME_BASED:
                for country, patterns in self.country_patterns.items():
                    for pattern in patterns:
                        if pattern in filename_lower:
                            self.logger.info(f"Land erkannt aus Dateiname: {country} (Pattern: {pattern})")
                            return country, CountryDetectionMethod.FILENAME_BASED
            
            # Metadaten-basierte Erkennung
            if (config.country_detection_method == CountryDetectionMethod.METADATA_BASED 
                and metadata):
                
                metadata_text = str(metadata).lower()
                for country, patterns in self.country_patterns.items():
                    for pattern in patterns:
                        if pattern in metadata_text:
                            self.logger.info(f"Land erkannt aus Metadaten: {country}")
                            return country, CountryDetectionMethod.METADATA_BASED
            
            # Fallback
            self.logger.warning(f"Kein Land erkannt, Fallback zu: {config.fallback_country}")
            return config.fallback_country, CountryDetectionMethod.FALLBACK
            
        except Exception as e:
            self.logger.error(f"Fehler bei Länder-Erkennung: {e}")
            return config.fallback_country, CountryDetectionMethod.FALLBACK


class DataValidator:
    """Validiert Daten vor dem Export"""
    
    def __init__(self):
        self.logger = logging.getLogger(StorageConstants.LOGGER_NAME)
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validiert DataFrame für Country Analysis Export
        
        Args:
            df: Zu validaterender DataFrame
            
        Returns:
            Tuple von (ist_valid, warning_liste)
        """
        warnings = []
        is_valid = True
        
        try:
            # Basis-Validierungen
            if df.empty:
                warnings.append("DataFrame ist leer")
                is_valid = False
                return is_valid, warnings
            
            # Erforderliche Spalten prüfen
            required_columns = ['topic', 'dominant_emotion', 'sentiment']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                warnings.append(f"Fehlende Spalten für Country Analysis: {missing_columns}")
                # Nicht als invalid markieren, da Country Analysis auch ohne funktionieren kann
            
            # Topic-Spalte validieren
            if 'topic' in df.columns:
                topic_stats = df['topic'].describe()
                if topic_stats['count'] == 0:
                    warnings.append("Keine gültigen Topic-Zuordnungen gefunden")
                elif topic_stats['count'] < len(df) * 0.5:
                    warnings.append(f"Nur {topic_stats['count']}/{len(df)} Kommentare haben Topic-Zuordnungen")
            
            # Emotion-Spalte validieren
            if 'dominant_emotion' in df.columns:
                emotion_null_count = df['dominant_emotion'].isnull().sum()
                if emotion_null_count > len(df) * 0.1:
                    warnings.append(f"{emotion_null_count} Kommentare haben keine Emotion-Zuordnung")
            
            # Sentiment-Spalte validieren
            if 'sentiment' in df.columns:
                sentiment_null_count = df['sentiment'].isnull().sum()
                if sentiment_null_count > len(df) * 0.1:
                    warnings.append(f"{sentiment_null_count} Kommentare haben keine Sentiment-Zuordnung")
            
            self.logger.info(f"DataFrame validiert: {len(warnings)} Warnungen")
            return is_valid, warnings
            
        except Exception as e:
            self.logger.error(f"Fehler bei DataFrame-Validierung: {e}")
            warnings.append(f"Validierungsfehler: {str(e)}")
            return False, warnings
    
    def validate_smart_labels(self, smart_labels_info: SmartLabelsInfo, df: pd.DataFrame) -> List[str]:
        """Validiert Smart Labels gegen DataFrame
        
        Args:
            smart_labels_info: Smart Labels Informationen
            df: DataFrame mit Topic-Daten
            
        Returns:
            Liste von Warnungen
        """
        warnings = []
        
        try:
            if not smart_labels_info.has_labels:
                warnings.append("Keine Smart Labels verfügbar")
                return warnings
            
            if 'topic' not in df.columns:
                warnings.append("Keine Topic-Spalte im DataFrame für Smart Labels")
                return warnings
            
            # Prüfe Topic-Coverage
            df_topics = set(df['topic'].dropna().astype(int))
            label_topics = set(smart_labels_info.labels_dict.keys())
            
            missing_labels = df_topics - label_topics
            if missing_labels:
                warnings.append(f"Smart Labels fehlen für Topics: {sorted(missing_labels)}")
            
            unused_labels = label_topics - df_topics
            if unused_labels:
                warnings.append(f"Ungenutzte Smart Labels für Topics: {sorted(unused_labels)}")
            
            coverage = len(label_topics & df_topics) / len(df_topics) if df_topics else 0
            if coverage < 0.8:
                warnings.append(f"Smart Labels decken nur {coverage:.1%} der Topics ab")
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"Fehler bei Smart Labels Validierung: {e}")
            warnings.append(f"Smart Labels Validierungsfehler: {str(e)}")
            return warnings


class CountryAnalysisExporter:
    """Exportiert Daten für Country Analysis"""
    
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.logger = logging.getLogger(StorageConstants.LOGGER_NAME)
    
    def export_dataframe(
        self,
        df: pd.DataFrame,
        filename: str,
        smart_labels_info: SmartLabelsInfo,
        config: CountryAnalysisExportConfig,
        country: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExportResult:
        """Exportiert DataFrame mit Smart Labels für Country Analysis
        
        Args:
            df: Zu exportierender DataFrame
            filename: Ursprünglicher Dateiname
            smart_labels_info: Smart Labels Informationen
            config: Export-Konfiguration
            country: Erkanntes Land
            metadata: Optionale Metadaten
            
        Returns:
            ExportResult-Objekt
        """
        try:
            export_df = df.copy()
            added_columns = []
            warnings = []
            
            # Smart Labels hinzufügen
            if config.include_smart_labels and smart_labels_info.has_labels:
                if 'topic' in export_df.columns:
                    export_df[StorageConstants.SMART_LABELS_COLUMN] = (
                        export_df['topic'].map(smart_labels_info.labels_dict)
                    )
                    added_columns.append(StorageConstants.SMART_LABELS_COLUMN)
                    self.logger.info(f"Smart Labels Spalte hinzugefügt: {len(smart_labels_info.labels_dict)} Labels")
                else:
                    warnings.append("Keine Topic-Spalte für Smart Labels verfügbar")
            
            # Country Detection hinzufügen
            if config.include_country_detection:
                export_df[StorageConstants.COUNTRY_COLUMN] = country
                added_columns.append(StorageConstants.COUNTRY_COLUMN)
            
            # Metadaten-Spalten hinzufügen
            if config.include_metadata_columns:
                export_df[StorageConstants.ANALYSIS_SOURCE_COLUMN] = filename
                added_columns.append(StorageConstants.ANALYSIS_SOURCE_COLUMN)
                
                if config.add_timestamp:
                    export_df[StorageConstants.EXPORT_TIMESTAMP_COLUMN] = datetime.now().isoformat()
                    added_columns.append(StorageConstants.EXPORT_TIMESTAMP_COLUMN)
            
            # Verzeichnis erstellen
            target_dir = self.results_dir
            if config.create_subdirectory:
                target_dir = self.results_dir / StorageConstants.COUNTRY_ANALYSIS_SUBDIR
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Dateiname generieren
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(filename).stem
            export_filename = f"{base_name}_country_analysis_{timestamp}{StorageConstants.CSV_EXTENSION}"
            export_path = target_dir / export_filename
            
            # Exportieren
            export_df.to_csv(export_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Country Analysis Export erfolgreich: {export_path}")
            
            return ExportResult(
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
            error_msg = f"Export fehlgeschlagen: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return ExportResult(
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

class CountryAnalysisStorageDeutsch:
    """Zentraler Manager für deutsche Country Analysis Storage-Operationen"""
    
    def __init__(self, results_dir: Optional[Union[str, Path]] = None):
        """Initialisiert den Storage Manager
        
        Args:
            results_dir: Optionales Ergebnisverzeichnis (default: saved_results)
        """
        self.results_dir = Path(results_dir or StorageConstants.RESULTS_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Komponenten initialisieren
        self.smart_labels_extractor = SmartLabelsExtractor()
        self.country_detector = CountryDetector()
        self.data_validator = DataValidator()
        self.exporter = CountryAnalysisExporter(self.results_dir)
        
        self.logger = logging.getLogger(StorageConstants.LOGGER_NAME)
        
        # Logging konfigurieren
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
        config: Optional[CountryAnalysisExportConfig] = None
    ) -> ExportResult:
        """Exportiert DataFrame mit Smart Labels für Country Analysis
        
        Args:
            df: Zu exportierender DataFrame
            filename: Ursprünglicher Dateiname
            additional_data: Zusätzliche Analysedaten
            config: Optionale Export-Konfiguration
            
        Returns:
            ExportResult-Objekt
        """
        if config is None:
            config = CountryAnalysisExportConfig()
        
        try:
            self.logger.info(f"Starte Country Analysis Export für: {filename}")
            
            # Daten validieren
            if config.validate_data:
                is_valid, validation_warnings = self.data_validator.validate_dataframe(df)
                if not is_valid:
                    return ExportResult(
                        success=False,
                        file_path=None,
                        exported_rows=0,
                        added_columns=[],
                        smart_labels_added=0,
                        country_detected=None,
                        export_timestamp=datetime.now(),
                        error_message="DataFrame-Validierung fehlgeschlagen",
                        warnings=validation_warnings
                    )
            
            # Smart Labels extrahieren
            smart_labels_info = self.smart_labels_extractor.extract_from_session_state()
            
            # Fallback zu additional_data wenn Session State leer
            if not smart_labels_info.has_labels and additional_data:
                smart_labels_info = self.smart_labels_extractor.extract_from_additional_data(additional_data)
            
            # Smart Labels validieren
            if config.include_smart_labels:
                label_warnings = self.data_validator.validate_smart_labels(smart_labels_info, df)
                if label_warnings:
                    self.logger.warning(f"Smart Labels Warnungen: {label_warnings}")
            
            # Land erkennen
            country, detection_method = self.country_detector.detect_country(
                filename, config, additional_data
            )
            
            # Exportieren
            result = self.exporter.export_dataframe(
                df, filename, smart_labels_info, config, country, additional_data
            )
            
            if result.success:
                self.logger.info(f"Country Analysis Export erfolgreich: {result.summary}")
            else:
                self.logger.error(f"Country Analysis Export fehlgeschlagen: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Unerwarteter Fehler beim Country Analysis Export: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return ExportResult(
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
        """Gibt verfügbare Country Analysis Dateien zurück
        
        Returns:
            Liste von Analyse-Informationen
        """
        try:
            country_dir = self.results_dir / StorageConstants.COUNTRY_ANALYSIS_SUBDIR
            if not country_dir.exists():
                return []
            
            analyses = []
            for csv_file in country_dir.glob(f"*_country_analysis_*{StorageConstants.CSV_EXTENSION}"):
                try:
                    # Basis-Informationen extrahieren
                    file_info = {
                        'filename': csv_file.name,
                        'path': str(csv_file),
                        'size': csv_file.stat().st_size,
                        'modified': datetime.fromtimestamp(csv_file.stat().st_mtime),
                        'country': 'Deutschland'  # Default für deutsche Analysen
                    }
                    
                    # Versuche zusätzliche Informationen aus CSV zu extrahieren
                    try:
                        df_sample = pd.read_csv(csv_file, nrows=1)
                        file_info['columns'] = list(df_sample.columns)
                        file_info['has_smart_labels'] = StorageConstants.SMART_LABELS_COLUMN in df_sample.columns
                        file_info['has_country_info'] = StorageConstants.COUNTRY_COLUMN in df_sample.columns
                        
                        # Extrahiere Land falls verfügbar
                        if StorageConstants.COUNTRY_COLUMN in df_sample.columns:
                            file_info['country'] = df_sample[StorageConstants.COUNTRY_COLUMN].iloc[0]
                        
                    except Exception as e:
                        self.logger.warning(f"Konnte CSV nicht analysieren {csv_file.name}: {e}")
                        file_info['has_smart_labels'] = False
                        file_info['has_country_info'] = False
                    
                    analyses.append(file_info)
                    
                except Exception as e:
                    self.logger.warning(f"Fehler beim Verarbeiten der Datei {csv_file}: {e}")
                    continue
            
            # Sortiere nach Änderungsdatum (neueste zuerst)
            analyses.sort(key=lambda x: x['modified'], reverse=True)
            
            self.logger.info(f"Gefundene Country Analysis Dateien: {len(analyses)}")
            return analyses
            
        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der Country Analysis Dateien: {e}")
            return []
    
    def create_export_config(
        self,
        include_smart_labels: bool = True,
        include_country_detection: bool = True,
        fallback_country: str = "Deutschland",
        **kwargs
    ) -> CountryAnalysisExportConfig:
        """Factory-Methode für Export-Konfiguration
        
        Args:
            include_smart_labels: Smart Labels einschließen
            include_country_detection: Länder-Erkennung einschließen
            fallback_country: Fallback-Land
            **kwargs: Weitere Konfigurationsoptionen
            
        Returns:
            CountryAnalysisExportConfig-Objekt
        """
        return CountryAnalysisExportConfig(
            include_smart_labels=include_smart_labels,
            include_country_detection=include_country_detection,
            fallback_country=fallback_country,
            **kwargs
        )


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_country_analysis_export_config() -> CountryAnalysisExportConfig:
    """Rendert UI für Country Analysis Export-Konfiguration"""
    st.subheader("🌍 Country Analysis Export Einstellungen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_smart_labels = st.checkbox(
            "Smart Labels einschließen", 
            value=True,
            help="Fügt Smart Topic Labels zur Export-CSV hinzu"
        )
        
        include_country_detection = st.checkbox(
            "Länder-Erkennung aktivieren",
            value=True,
            help="Erkennt und fügt Land basierend auf Dateiname hinzu"
        )
        
        add_timestamp = st.checkbox(
            "Export-Zeitstempel hinzufügen",
            value=True
        )
    
    with col2:
        fallback_country = st.selectbox(
            "Fallback-Land:",
            options=["Deutschland", "Österreich", "Schweiz", "International (Deutsch)"],
            index=0
        )
        
        export_format = st.selectbox(
            "Export-Format:",
            options=[fmt.value for fmt in ExportFormat],
            index=1,  # CSV_WITH_METADATA
            format_func=lambda x: {
                "csv_only": "Nur CSV",
                "csv_with_metadata": "CSV mit Metadaten",
                "full_export": "Vollständiger Export"
            }.get(x, x)
        )
        
        create_subdirectory = st.checkbox(
            "Unterverzeichnis erstellen",
            value=True,
            help="Erstellt Unterverzeichnis 'country_analysis'"
        )
    
    return CountryAnalysisExportConfig(
        include_smart_labels=include_smart_labels,
        include_country_detection=include_country_detection,
        add_timestamp=add_timestamp,
        fallback_country=fallback_country,
        export_format=ExportFormat(export_format),
        create_subdirectory=create_subdirectory
    )


def render_export_result(result: ExportResult) -> None:
    """Rendert Export-Ergebnis"""
    if result.success:
        st.success(result.summary)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Exportierte Zeilen", result.exported_rows)
        
        with col2:
            st.metric("Neue Spalten", len(result.added_columns))
        
        with col3:
            st.metric("Smart Labels", result.smart_labels_added)
        
        if result.file_path:
            st.info(f"📁 Gespeichert unter: `{result.file_path}`")
        
        if result.country_detected:
            st.info(f"🌍 Erkanntes Land: **{result.country_detected}**")
        
        if result.added_columns:
            st.write("**Hinzugefügte Spalten:**")
            for col in result.added_columns:
                st.write(f"- `{col}`")
        
        if result.warnings:
            st.warning("⚠️ Warnungen:")
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

def export_for_country_analysis(
    df: pd.DataFrame,
    filename: str,
    additional_data: Optional[Dict[str, Any]] = None,
    results_dir: Optional[str] = None
) -> bool:
    """Convenience-Funktion für Country Analysis Export
    
    Args:
        df: Zu exportierender DataFrame
        filename: Dateiname
        additional_data: Zusätzliche Daten
        results_dir: Ergebnisverzeichnis
        
    Returns:
        True wenn erfolgreich
    """
    storage = CountryAnalysisStorageDeutsch(results_dir)
    result = storage.export_with_smart_labels(df, filename, additional_data)
    return result.success


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Main Manager
    'CountryAnalysisStorageDeutsch',
    
    # Data Models
    'SmartLabelsInfo',
    'CountryAnalysisExportConfig', 
    'ExportResult',
    
    # Enums
    'ExportFormat',
    'CountryDetectionMethod',
    
    # Components
    'SmartLabelsExtractor',
    'CountryDetector',
    'DataValidator',
    'CountryAnalysisExporter',
    
    # UI Functions
    'render_country_analysis_export_config',
    'render_export_result',
    
    # Convenience Functions
    'export_for_country_analysis',
    
    # Constants
    'StorageConstants'
]