"""
Modernisierter Data Loader für HerEducation
Strukturiertes und konfigurierbares Laden von Bildungsdaten

Autor: Sandra Störkel - HerEducation
Version: 2.0 - Modernisiert mit bewährten Patterns
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Tuple
import logging
from enum import Enum

# ===== KONSTANTEN =====
class DataLoaderConstants:
    """Zentrale Konstanten für Data Loader"""
    
    # Standard-Dateiname
    DEFAULT_CSV_FILENAME = "heraltas1_updated.csv"
    
    # Verzeichnis-Namen
    DATA_DIR_NAME = "data"
    
    # Encoding-Optionen
    DEFAULT_ENCODING = "utf-8"
    FALLBACK_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    
    # Validierung
    MIN_REQUIRED_ROWS = 1
    REQUIRED_COLUMNS_THRESHOLD = 3  # Mindestanzahl Spalten für valide Daten
    
    # Cache-Parameter
    DEFAULT_CACHE_TTL = 3600  # 1 Stunde in Sekunden

class DataColumns:
    """Standard-Spaltennamen für verschiedene Datenquellen"""
    
    # Original-Spaltennamen (Input)
    ORIGINAL_COLUMNS = {
        "countries_iso2": "Countries (ISO2)",
        "countries": "Countries", 
        "year": "Year",
        "indicators": "Indicators",
        "result": "Result",
        "analysis_en": "Analysis [EN]",
        "latitude": "latitude",
        "longitude": "longitude"
    }
    
    # Deutsche Spaltennamen (Output)
    GERMAN_COLUMNS = {
        "countries_iso2": "ISO2",
        "countries": "Land",
        "year": "Jahr", 
        "indicators": "Indikator",
        "result": "Ergebnis",
        "analysis_en": "Analyse",
        "latitude": "Breitengrad",
        "longitude": "Längengrad"
    }
    
    # Englische Spaltennamen (Output)
    ENGLISH_COLUMNS = {
        "countries_iso2": "ISO2",
        "countries": "Country",
        "year": "Year",
        "indicators": "Indicator", 
        "result": "Result",
        "analysis_en": "Analysis",
        "latitude": "Latitude",
        "longitude": "Longitude"
    }

# ===== ENUMS =====
class DataLanguage(Enum):
    """Unterstützte Sprachen für Spaltennamen"""
    GERMAN = "de"
    ENGLISH = "en"
    ORIGINAL = "original"

class DataLoadStatus(Enum):
    """Status des Datenlade-Vorgangs"""
    SUCCESS = "success"
    FILE_NOT_FOUND = "file_not_found"
    INVALID_DATA = "invalid_data"
    ENCODING_ERROR = "encoding_error"
    UNKNOWN_ERROR = "unknown_error"

# ===== DATACLASSES =====
@dataclass
class DataLoaderConfig:
    """Konfiguration für den Data Loader"""
    
    # Datei-Konfiguration
    filename: str = DataLoaderConstants.DEFAULT_CSV_FILENAME
    custom_paths: List[Union[str, Path]] = field(default_factory=list)
    encoding: str = DataLoaderConstants.DEFAULT_ENCODING
    
    # Spalten-Konfiguration
    language: DataLanguage = DataLanguage.GERMAN
    custom_column_mapping: Optional[Dict[str, str]] = None
    
    # Cache-Konfiguration
    use_cache: bool = True
    cache_ttl: int = DataLoaderConstants.DEFAULT_CACHE_TTL
    cache_key_suffix: str = ""
    
    # Validierung
    validate_data: bool = True
    min_rows: int = DataLoaderConstants.MIN_REQUIRED_ROWS
    required_columns: List[str] = field(default_factory=list)
    
    # Error Handling
    show_errors_in_ui: bool = True
    raise_on_error: bool = False
    
    @property
    def cache_key(self) -> str:
        """Generiert einen eindeutigen Cache-Key"""
        key_parts = [
            self.filename,
            self.language.value,
            str(hash(tuple(self.custom_paths) if self.custom_paths else ())),
            self.cache_key_suffix
        ]
        return "data_loader_" + "_".join(filter(None, key_parts))

@dataclass 
class DataLoadResult:
    """Ergebnis eines Datenlade-Vorgangs"""
    status: DataLoadStatus
    data: pd.DataFrame
    message: str = ""
    file_path: Optional[Path] = None
    encoding_used: Optional[str] = None
    columns_mapped: bool = False
    
    @property
    def is_success(self) -> bool:
        """Prüft ob das Laden erfolgreich war"""
        return self.status == DataLoadStatus.SUCCESS and not self.data.empty
    
    @property
    def row_count(self) -> int:
        """Anzahl der geladenen Zeilen"""
        return len(self.data)
    
    @property
    def column_count(self) -> int:
        """Anzahl der Spalten"""
        return len(self.data.columns)

# ===== SPEZIALISIERTE KOMPONENTEN =====
class PathResolver:
    """Löst Dateipfade mit verschiedenen Fallback-Strategien auf"""
    
    def __init__(self, config: DataLoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_search_paths(self) -> List[Path]:
        """Erstellt Liste der zu durchsuchenden Pfade"""
        paths = []
        
        # Custom Paths zuerst
        for custom_path in self.config.custom_paths:
            paths.append(Path(custom_path))
        
        # Standard-Pfade
        filename = self.config.filename
        standard_paths = [
            # Aktuelles Verzeichnis
            Path(filename),
            
            # Data-Verzeichnis
            Path(DataLoaderConstants.DATA_DIR_NAME) / filename,
            
            # Parent Data-Verzeichnis
            Path("..") / DataLoaderConstants.DATA_DIR_NAME / filename,
            
            # Absoluter Pfad basierend auf Script-Location
            Path(__file__).parent.parent / DataLoaderConstants.DATA_DIR_NAME / filename,
            
            # Script-Verzeichnis
            Path(__file__).parent / filename,
        ]
        
        paths.extend(standard_paths)
        return paths
    
    def resolve_file_path(self) -> Optional[Path]:
        """Findet den ersten existierenden Dateipfad"""
        search_paths = self.get_search_paths()
        
        for path in search_paths:
            try:
                if path.exists() and path.is_file():
                    self.logger.info(f"Datei gefunden: {path}")
                    return path
            except Exception as e:
                self.logger.debug(f"Fehler beim Prüfen von {path}: {e}")
                continue
        
        self.logger.error(f"Datei '{self.config.filename}' in keinem der Pfade gefunden: {[str(p) for p in search_paths]}")
        return None

class DataValidator:
    """Validiert geladene Daten"""
    
    def __init__(self, config: DataLoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validiert ein DataFrame
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not self.config.validate_data:
            return True, ""
        
        # Prüfe ob DataFrame leer ist
        if df.empty:
            return False, "Das geladene DataFrame ist leer"
        
        # Prüfe Mindestanzahl Zeilen
        if len(df) < self.config.min_rows:
            return False, f"Zu wenige Zeilen: {len(df)} < {self.config.min_rows}"
        
        # Prüfe Mindestanzahl Spalten
        if len(df.columns) < DataLoaderConstants.REQUIRED_COLUMNS_THRESHOLD:
            return False, f"Zu wenige Spalten: {len(df.columns)} < {DataLoaderConstants.REQUIRED_COLUMNS_THRESHOLD}"
        
        # Prüfe erforderliche Spalten
        if self.config.required_columns:
            missing_columns = set(self.config.required_columns) - set(df.columns)
            if missing_columns:
                return False, f"Fehlende erforderliche Spalten: {missing_columns}"
        
        self.logger.info(f"Datenvalidierung erfolgreich: {len(df)} Zeilen, {len(df.columns)} Spalten")
        return True, ""

class ColumnMapper:
    """Behandelt Spalten-Mapping für verschiedene Sprachen"""
    
    def __init__(self, config: DataLoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_column_mapping(self) -> Dict[str, str]:
        """Erstellt das Spalten-Mapping basierend auf Konfiguration"""
        
        # Custom Mapping hat Priorität
        if self.config.custom_column_mapping:
            return self.config.custom_column_mapping
        
        # Standard-Mappings basierend auf Sprache
        if self.config.language == DataLanguage.GERMAN:
            return self._create_mapping(DataColumns.GERMAN_COLUMNS)
        elif self.config.language == DataLanguage.ENGLISH:
            return self._create_mapping(DataColumns.ENGLISH_COLUMNS)
        else:
            return {}  # Kein Mapping für ORIGINAL
    
    def _create_mapping(self, target_columns: Dict[str, str]) -> Dict[str, str]:
        """Erstellt Mapping von Original- zu Ziel-Spaltennamen"""
        mapping = {}
        for key, target_name in target_columns.items():
            original_name = DataColumns.ORIGINAL_COLUMNS.get(key)
            if original_name:
                mapping[original_name] = target_name
        return mapping
    
    def apply_column_mapping(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
        """
        Wendet Spalten-Mapping auf DataFrame an
        
        Returns:
            Tuple[pd.DataFrame, bool]: (mapped_df, mapping_applied)
        """
        mapping = self.get_column_mapping()
        
        if not mapping:
            return df, False
        
        # Nur verfügbare Spalten mappen
        available_mapping = {old: new for old, new in mapping.items() if old in df.columns}
        
        if available_mapping:
            df_mapped = df.rename(columns=available_mapping)
            self.logger.info(f"Spalten umbenannt: {list(available_mapping.keys())} -> {list(available_mapping.values())}")
            return df_mapped, True
        
        return df, False

class CSVReader:
    """Robuster CSV-Reader mit Encoding-Fallbacks"""
    
    def __init__(self, config: DataLoaderConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def read_csv_robust(self, file_path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str], str]:
        """
        Liest CSV mit verschiedenen Encoding-Strategien
        
        Returns:
            Tuple[Optional[pd.DataFrame], Optional[str], str]: (dataframe, encoding_used, error_message)
        """
        encodings_to_try = [self.config.encoding] + DataLoaderConstants.FALLBACK_ENCODINGS
        # Entferne Duplikate aber behalte Reihenfolge
        seen = set()
        encodings_to_try = [x for x in encodings_to_try if not (x in seen or seen.add(x))]
        
        for encoding in encodings_to_try:
            try:
                self.logger.debug(f"Versuche CSV zu lesen mit Encoding: {encoding}")
                df = pd.read_csv(file_path, encoding=encoding)
                self.logger.info(f"CSV erfolgreich gelesen mit Encoding: {encoding}")
                return df, encoding, ""
            except UnicodeDecodeError as e:
                self.logger.debug(f"Encoding {encoding} fehlgeschlagen: {e}")
                continue
            except Exception as e:
                error_msg = f"Fehler beim Lesen mit {encoding}: {e}"
                self.logger.error(error_msg)
                return None, None, error_msg
        
        error_msg = f"CSV konnte mit keinem Encoding gelesen werden: {encodings_to_try}"
        self.logger.error(error_msg)
        return None, None, error_msg

# ===== HAUPTKLASSE =====
class EducationDataLoader:
    """Modernisierter Data Loader für Bildungsdaten"""
    
    def __init__(self, config: DataLoaderConfig = None):
        self.config = config or DataLoaderConfig()
        self.logger = logging.getLogger(__name__)
        
        # Komponenten initialisieren
        self.path_resolver = PathResolver(self.config)
        self.validator = DataValidator(self.config)
        self.column_mapper = ColumnMapper(self.config)
        self.csv_reader = CSVReader(self.config)
    
    def load_data(self) -> DataLoadResult:
        """
        Lädt Daten mit vollständiger Fehlerbehandlung und Validierung
        
        Returns:
            DataLoadResult: Strukturiertes Ergebnis des Ladevorgangs
        """
        try:
            # 1. Dateipfad auflösen
            file_path = self.path_resolver.resolve_file_path()
            if not file_path:
                return DataLoadResult(
                    status=DataLoadStatus.FILE_NOT_FOUND,
                    data=pd.DataFrame(),
                    message=f"Datei '{self.config.filename}' nicht gefunden"
                )
            
            # 2. CSV lesen
            df, encoding_used, error_msg = self.csv_reader.read_csv_robust(file_path)
            if df is None:
                return DataLoadResult(
                    status=DataLoadStatus.ENCODING_ERROR,
                    data=pd.DataFrame(),
                    message=error_msg,
                    file_path=file_path
                )
            
            # 3. Daten validieren
            is_valid, validation_error = self.validator.validate_dataframe(df)
            if not is_valid:
                return DataLoadResult(
                    status=DataLoadStatus.INVALID_DATA,
                    data=df,
                    message=f"Datenvalidierung fehlgeschlagen: {validation_error}",
                    file_path=file_path,
                    encoding_used=encoding_used
                )
            
            # 4. Spalten mappen
            df_mapped, columns_mapped = self.column_mapper.apply_column_mapping(df)
            
            # 5. Erfolgreiches Ergebnis
            return DataLoadResult(
                status=DataLoadStatus.SUCCESS,
                data=df_mapped,
                message=f"Daten erfolgreich geladen: {len(df_mapped)} Zeilen, {len(df_mapped.columns)} Spalten",
                file_path=file_path,
                encoding_used=encoding_used,
                columns_mapped=columns_mapped
            )
            
        except Exception as e:
            error_msg = f"Unerwarteter Fehler: {e}"
            self.logger.error(error_msg, exc_info=True)
            
            return DataLoadResult(
                status=DataLoadStatus.UNKNOWN_ERROR,
                data=pd.DataFrame(),
                message=error_msg
            )
    
    def get_file_info(self) -> Dict[str, Union[str, bool, int]]:
        """Gibt Informationen über die zu ladende Datei zurück"""
        file_path = self.path_resolver.resolve_file_path()
        
        if not file_path:
            return {
                "file_found": False,
                "filename": self.config.filename,
                "search_paths": [str(p) for p in self.path_resolver.get_search_paths()]
            }
        
        try:
            stat = file_path.stat()
            return {
                "file_found": True,
                "filename": self.config.filename,
                "full_path": str(file_path),
                "file_size_bytes": stat.st_size,
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "last_modified": stat.st_mtime
            }
        except Exception as e:
            return {
                "file_found": True,
                "filename": self.config.filename,
                "full_path": str(file_path),
                "error": str(e)
            }

# ===== CACHED LOADER =====
class CachedEducationDataLoader:
    """Cached Version des Data Loaders für Streamlit"""
    
    @staticmethod
    @st.cache_data(ttl=DataLoaderConstants.DEFAULT_CACHE_TTL)
    def _cached_load_data(config_dict: Dict) -> DataLoadResult:
        """Interne gecachte Lade-Funktion"""
        # Konfiguration aus Dict rekonstruieren
        config = DataLoaderConfig(**config_dict)
        loader = EducationDataLoader(config)
        return loader.load_data()
    
    @classmethod
    def load_data_cached(cls, config: DataLoaderConfig = None) -> DataLoadResult:
        """
        Lädt Daten mit Streamlit-Cache
        
        Args:
            config: Konfiguration für den Data Loader
            
        Returns:
            DataLoadResult: Cached Ergebnis des Ladevorgangs
        """
        if config is None:
            config = DataLoaderConfig()
        
        # Konfiguration zu Dict für Cache-Kompatibilität
        config_dict = {
            "filename": config.filename,
            "custom_paths": [str(p) for p in config.custom_paths],
            "encoding": config.encoding,
            "language": config.language,
            "custom_column_mapping": config.custom_column_mapping,
            "use_cache": config.use_cache,
            "cache_ttl": config.cache_ttl,
            "cache_key_suffix": config.cache_key_suffix,
            "validate_data": config.validate_data,
            "min_rows": config.min_rows,
            "required_columns": config.required_columns,
            "show_errors_in_ui": config.show_errors_in_ui,
            "raise_on_error": config.raise_on_error
        }
        
        return cls._cached_load_data(config_dict)

# ===== BACKWARD-COMPATIBLE FUNCTIONS =====
@st.cache_data(ttl=DataLoaderConstants.DEFAULT_CACHE_TTL)
def load_data() -> pd.DataFrame:
    """
    Backward-compatible Hauptfunktion
    
    Returns:
        pd.DataFrame: Der geladene und aufbereitete Datensatz
    """
    config = DataLoaderConfig(
        show_errors_in_ui=True,
        validate_data=True
    )
    
    result = CachedEducationDataLoader.load_data_cached(config)
    
    # Error Handling für UI
    if not result.is_success:
        if config.show_errors_in_ui:
            if result.status == DataLoadStatus.FILE_NOT_FOUND:
                st.error("Die Datei 'heraltas1_updated.csv' konnte nicht gefunden werden.")
            else:
                st.error(f"Fehler beim Laden der Daten: {result.message}")
        
        return pd.DataFrame()
    
    return result.data

# ===== ERWEITERTE API =====
def load_data_advanced(config: DataLoaderConfig = None) -> DataLoadResult:
    """
    Erweiterte API für strukturierte Datenlade-Ergebnisse
    
    Args:
        config: Konfiguration für den Data Loader
        
    Returns:
        DataLoadResult: Vollständiges Ergebnis mit Status und Metadaten
    """
    return CachedEducationDataLoader.load_data_cached(config)

def create_data_loader_config(**kwargs) -> DataLoaderConfig:
    """
    Hilfsfunktion zum Erstellen einer DataLoaderConfig
    
    Args:
        **kwargs: Konfigurationsparameter
        
    Returns:
        DataLoaderConfig: Erstellte Konfiguration
    """
    return DataLoaderConfig(**kwargs)

def get_available_languages() -> List[str]:
    """Gibt verfügbare Sprachoptionen zurück"""
    return [lang.value for lang in DataLanguage]

# ===== BEISPIEL-NUTZUNG =====
if __name__ == "__main__":
    # Backward-compatible Nutzung
    print("=== Backward-Compatible API ===")
    df = load_data()
    print(f"Geladene Daten: {len(df)} Zeilen, {len(df.columns)} Spalten")
    
    # Erweiterte API
    print("\n=== Erweiterte API ===")
    
    # Standard-Konfiguration
    result = load_data_advanced()
    print(f"Status: {result.status.value}")
    print(f"Daten: {result.row_count} Zeilen, {result.column_count} Spalten")
    
    # Custom-Konfiguration
    config = create_data_loader_config(
        language=DataLanguage.ENGLISH,
        validate_data=True,
        show_errors_in_ui=False
    )
    
    result_en = load_data_advanced(config)
    print(f"Englisch: {result_en.status.value}")
    if result_en.is_success:
        print(f"Spalten: {list(result_en.data.columns)}")