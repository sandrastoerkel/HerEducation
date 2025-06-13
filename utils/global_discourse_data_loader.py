"""
🌍 GLOBAL DISCOURSE DATA LOADER - CSV Loading & Country Detection
Lädt und validiert Country Analysis CSV-Dateien mit automatischer Länder-Erkennung
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import logging
from collections import defaultdict

# Local imports
from .global_discourse_models import GlobalAnalysisConstants, AnalysisFile, CountryData
from .global_discourse_country_detector import create_enhanced_country_detector

# =============================================================================
# DATA LOADER WITH COUNTRY DETECTION
# =============================================================================

class CountryDataLoader:
    """Lädt und validiert Country Analysis CSV-Dateien mit automatischer Länder-Erkennung"""
    
    def __init__(self):
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
        self.german_dir = Path(GlobalAnalysisConstants.GERMAN_RESULTS_DIR)
        self.english_dir = Path(GlobalAnalysisConstants.ENGLISH_RESULTS_DIR)
        
        # *** COUNTRY DETECTOR INTEGRATION ***
        self.country_detector = create_enhanced_country_detector()
        self.logger.info("Country Detector initialisiert für automatische Länder-Erkennung")
    
    def get_available_analysis_files(self) -> List[AnalysisFile]:
        """Findet alle verfügbaren Country Analysis Dateien mit automatischer Länder-Erkennung
        
        Returns:
            Liste von AnalysisFile-Objekten
        """
        analysis_files = []
        
        # Deutsche Analysen
        if self.german_dir.exists():
            for csv_file in self.german_dir.glob("*_country_analysis_*.csv"):
                try:
                    file_info = self._extract_file_info(csv_file, "de")
                    if file_info:
                        analysis_files.append(file_info)
                except Exception as e:
                    self.logger.warning(f"Fehler beim Verarbeiten der deutschen Datei {csv_file}: {e}")
        
        # Englische Analysen
        if self.english_dir.exists():
            for csv_file in self.english_dir.glob("*_country_analysis_*.csv"):
                try:
                    file_info = self._extract_file_info(csv_file, "en")
                    if file_info:
                        analysis_files.append(file_info)
                except Exception as e:
                    self.logger.warning(f"Fehler beim Verarbeiten der englischen Datei {csv_file}: {e}")
        
        # Sortiere nach Datum (neueste zuerst)
        analysis_files.sort(key=lambda x: x.analysis_date, reverse=True)
        
        self.logger.info(f"Gefundene Analysis-Dateien: {len(analysis_files)}")
        return analysis_files
    
    def _extract_file_info(self, csv_file: Path, language: str) -> Optional[AnalysisFile]:
        """Extrahiert Informationen aus einer CSV-Datei mit automatischer Länder-Erkennung
        
        Args:
            csv_file: Pfad zur CSV-Datei
            language: Sprache der Analyse (de/en)
            
        Returns:
            AnalysisFile-Objekt oder None
        """
        try:
            # Basis-Informationen
            stat = csv_file.stat()
            
            # Versuche Datum aus Dateiname zu extrahieren
            name_parts = csv_file.stem.split("_")
            analysis_date = datetime.fromtimestamp(stat.st_mtime)  # Fallback
            
            # Bessere Datums-Extraktion aus Timestamp im Dateinamen
            for i, part in enumerate(name_parts):
                if "country_analysis" in part and i + 1 < len(name_parts):
                    timestamp_part = name_parts[i + 1]
                    try:
                        analysis_date = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
                        break
                    except ValueError:
                        continue
            
            # Prüfe CSV-Struktur
            try:
                df_sample = pd.read_csv(csv_file, nrows=1)
                has_smart_labels = GlobalAnalysisConstants.SMART_LABELS_COLUMN in df_sample.columns
                row_count = len(pd.read_csv(csv_file))
                
                # Extrahiere Source
                source_analysis = None
                if GlobalAnalysisConstants.ANALYSIS_SOURCE_COLUMN in df_sample.columns:
                    source_analysis = df_sample[GlobalAnalysisConstants.ANALYSIS_SOURCE_COLUMN].iloc[0]
                
            except Exception as e:
                self.logger.warning(f"Konnte CSV nicht analysieren {csv_file}: {e}")
                has_smart_labels = False
                row_count = None
                source_analysis = None
            
            # *** AUTOMATISCHE LÄNDER-ERKENNUNG ***
            detection_result = self.country_detector.detect_country_from_filename(
                csv_file.name, 
                language, 
                str(csv_file)
            )
            
            country = detection_result.country
            
            # Log der Erkennung
            if detection_result.confidence >= 0.7:
                self.logger.info(f"🌍 Auto-detected {country} for {csv_file.name} (confidence: {detection_result.confidence:.2f})")
            elif detection_result.confidence > 0:
                self.logger.warning(f"⚠️ Low confidence detection for {csv_file.name}: {country} (confidence: {detection_result.confidence:.2f})")
            else:
                self.logger.warning(f"❓ Unknown country for {csv_file.name}, needs manual assignment")
            
            return AnalysisFile(
                file_path=csv_file,
                filename=csv_file.name,
                country=country,
                language=language,
                analysis_date=analysis_date,
                file_size=stat.st_size,
                row_count=row_count,
                has_smart_labels=has_smart_labels,
                source_analysis=source_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren der Datei-Info {csv_file}: {e}")
            return None
    
    def load_csv_data(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Lädt CSV-Daten mit Validierung
        
        Args:
            file_path: Pfad zur CSV-Datei
            
        Returns:
            DataFrame oder None bei Fehler
        """
        try:
            df = pd.read_csv(file_path)
            
            # Basis-Validierung
            required_columns = [
                GlobalAnalysisConstants.COUNTRY_COLUMN,
                GlobalAnalysisConstants.SENTIMENT_COLUMN
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.warning(f"Fehlende Spalten in {file_path.name}: {missing_columns}")
            
            # Smart Labels Validierung
            if GlobalAnalysisConstants.SMART_LABELS_COLUMN not in df.columns:
                self.logger.warning(f"Keine Smart Labels in {file_path.name}")
            
            self.logger.info(f"CSV geladen: {file_path.name} - {len(df)} Zeilen")
            return df
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der CSV {file_path}: {e}")
            return None


# =============================================================================
# DATA AGGREGATOR
# =============================================================================

class CountryDataAggregator:
    """Aggregiert Daten nach Ländern"""
    
    def __init__(self):
        self.logger = logging.getLogger(GlobalAnalysisConstants.LOGGER_NAME)
    
    def aggregate_country_data(
        self,
        analysis_files: List[AnalysisFile],
        selected_files: Optional[List[str]] = None
    ) -> Dict[str, CountryData]:
        """Aggregiert Daten nach Ländern
        
        Args:
            analysis_files: Liste aller verfügbaren Dateien
            selected_files: Optional Liste der zu verwendenden Dateinamen
            
        Returns:
            Dictionary mit Country-Daten nach Land
        """
        country_data = {}
        loader = CountryDataLoader()
        
        # Filtere gewählte Dateien
        files_to_process = analysis_files
        if selected_files:
            files_to_process = [f for f in analysis_files if f.filename in selected_files]
        
        for analysis_file in files_to_process:
            try:
                # Lade CSV-Daten
                df = loader.load_csv_data(analysis_file.file_path)
                if df is None or df.empty:
                    continue
                
                country = analysis_file.country
                
                # Initialisiere Country-Daten falls neu
                if country not in country_data:
                    country_data[country] = CountryData(
                        country=country,
                        language=analysis_file.language,
                        total_comments=0,
                        analysis_files=[]
                    )
                
                # Füge Datei hinzu
                country_data[country].analysis_files.append(analysis_file)
                country_data[country].total_comments += len(df)
                
                # Aggregiere Sentiment-Daten
                if GlobalAnalysisConstants.SENTIMENT_COLUMN in df.columns:
                    sentiment_counts = df[GlobalAnalysisConstants.SENTIMENT_COLUMN].value_counts()
                    for sentiment, count in sentiment_counts.items():
                        if sentiment in country_data[country].sentiment_distribution:
                            country_data[country].sentiment_distribution[sentiment] += count
                        else:
                            country_data[country].sentiment_distribution[sentiment] = count
                
                # Aggregiere Topic-Daten (Smart Labels)
                if GlobalAnalysisConstants.SMART_LABELS_COLUMN in df.columns:
                    topic_counts = df[GlobalAnalysisConstants.SMART_LABELS_COLUMN].dropna().value_counts()
                    for topic, count in topic_counts.items():
                        if topic in country_data[country].topic_distribution:
                            country_data[country].topic_distribution[topic] += count
                        else:
                            country_data[country].topic_distribution[topic] = count
                
                # Aggregiere Emotion-Daten
                if GlobalAnalysisConstants.EMOTION_COLUMN in df.columns:
                    emotion_counts = df[GlobalAnalysisConstants.EMOTION_COLUMN].value_counts()
                    for emotion, count in emotion_counts.items():
                        if emotion in country_data[country].emotion_distribution:
                            country_data[country].emotion_distribution[emotion] += count
                        else:
                            country_data[country].emotion_distribution[emotion] = count
                
                # Topic-Emotion Matrix
                if (GlobalAnalysisConstants.SMART_LABELS_COLUMN in df.columns and 
                    GlobalAnalysisConstants.EMOTION_COLUMN in df.columns):
                    self._aggregate_topic_emotion_matrix(
                        df, country_data[country], 
                        GlobalAnalysisConstants.SMART_LABELS_COLUMN,
                        GlobalAnalysisConstants.EMOTION_COLUMN
                    )
                
                # Topic-Sentiment Matrix
                if (GlobalAnalysisConstants.SMART_LABELS_COLUMN in df.columns and 
                    GlobalAnalysisConstants.SENTIMENT_COLUMN in df.columns):
                    self._aggregate_topic_sentiment_matrix(
                        df, country_data[country],
                        GlobalAnalysisConstants.SMART_LABELS_COLUMN,
                        GlobalAnalysisConstants.SENTIMENT_COLUMN
                    )
                
                # Metadaten
                country_data[country].analysis_sources.add(analysis_file.source_analysis or analysis_file.filename)
                
            except Exception as e:
                self.logger.error(f"Fehler beim Aggregieren der Daten für {analysis_file.filename}: {e}")
                continue
        
        # Berechne Prozentsätze
        for country, data in country_data.items():
            self._calculate_percentages(data)
        
        # Filtere Länder mit zu wenigen Kommentaren
        country_data = {
            country: data for country, data in country_data.items()
            if data.total_comments >= GlobalAnalysisConstants.MIN_COMMENTS_PER_COUNTRY
        }
        
        self.logger.info(f"Aggregierte Daten für {len(country_data)} Länder")
        return country_data
    
    def _aggregate_topic_emotion_matrix(
        self,
        df: pd.DataFrame,
        country_data: CountryData,
        topic_col: str,
        emotion_col: str
    ) -> None:
        """Aggregiert Topic-Emotion-Kombinationen"""
        for _, row in df.dropna(subset=[topic_col, emotion_col]).iterrows():
            topic = row[topic_col]
            emotion = row[emotion_col]
            
            if topic not in country_data.topic_emotion_matrix:
                country_data.topic_emotion_matrix[topic] = defaultdict(int)
            
            country_data.topic_emotion_matrix[topic][emotion] += 1
    
    def _aggregate_topic_sentiment_matrix(
        self,
        df: pd.DataFrame,
        country_data: CountryData,
        topic_col: str,
        sentiment_col: str
    ) -> None:
        """Aggregiert Topic-Sentiment-Kombinationen"""
        for _, row in df.dropna(subset=[topic_col, sentiment_col]).iterrows():
            topic = row[topic_col]
            sentiment = row[sentiment_col]
            
            if topic not in country_data.topic_sentiment_matrix:
                country_data.topic_sentiment_matrix[topic] = defaultdict(int)
            
            country_data.topic_sentiment_matrix[topic][sentiment] += 1
    
    def _calculate_percentages(self, country_data: CountryData) -> None:
        """Berechnet Prozentsätze für alle Distributionen"""
        total = country_data.total_comments
        
        if total > 0:
            # Sentiment Prozentsätze
            for sentiment, count in country_data.sentiment_distribution.items():
                country_data.sentiment_percentages[sentiment] = (count / total) * 100
            
            # Topic Prozentsätze
            for topic, count in country_data.topic_distribution.items():
                country_data.topic_percentages[topic] = (count / total) * 100
            
            # Emotion Prozentsätze
            for emotion, count in country_data.emotion_distribution.items():
                country_data.emotion_percentages[emotion] = (count / total) * 100


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'CountryDataLoader',
    'CountryDataAggregator'
]