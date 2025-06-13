"""
Enterprise-level English comment analysis file handler module.

This module provides comprehensive file handling functionality for English comment analysis
with enterprise architecture, type safety, robust error handling, and advanced file processing.
"""

import streamlit as st
import pandas as pd
import re
from pathlib import Path
import traceback
from io import BytesIO
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import logging
import time

# =============================================================================
# ENTERPRISE CONSTANTS
# =============================================================================

class EnglishFileHandlerConstants:
    """Constants for English file handler operations."""
    
    # File Processing
    MAX_PREVIEW_ROWS = 5
    MAX_PREVIEW_CHARS = 100
    MAX_FILE_SIZE_MB = 100
    CHUNK_SIZE = 8192
    
    # Text Processing
    MIN_WORD_LENGTH = 2
    MAX_COMMENT_LENGTH = 10000
    
    # File Extensions
    SUPPORTED_CSV_EXTENSIONS = ['.csv']
    SUPPORTED_JSON_EXTENSIONS = ['.json', '.jsonl']
    ALL_SUPPORTED_EXTENSIONS = SUPPORTED_CSV_EXTENSIONS + SUPPORTED_JSON_EXTENSIONS
    
    # Directory Names
    DEFAULT_DATA_DIR = "CommentAnalysis_Data"
    FALLBACK_DIR = "Desktop"
    
    # Column Names
    POSSIBLE_TEXT_COLUMNS = [
        'text', 'comment', 'kommentar', 'content',
        'Text', 'Comment', 'Kommentar', 'Content',
        'comment_text', 'message', 'body'
    ]
    
    # YouTube Patterns
    YOUTUBE_ID_PATTERNS = [
        r'_([a-zA-Z0-9_-]{11})_',  # Standard pattern with underscores
        r'_([a-zA-Z0-9_-]{11})',   # Alternative pattern
        r'([a-zA-Z0-9_-]{11})'     # Fallback pattern
    ]
    
    # Processing
    BATCH_SIZE = 1000
    PROGRESS_UPDATE_INTERVAL = 100

# =============================================================================
# ENTERPRISE ENUMS
# =============================================================================

class FileType(Enum):
    """Supported file types for comment analysis."""
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    UNKNOWN = "unknown"

class ProcessingStatus(Enum):
    """Status indicators for file processing operations."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"
    CANCELLED = "cancelled"

class CleaningLevel(Enum):
    """Text cleaning intensity levels."""
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"

class LanguageDetectionMode(Enum):
    """Language detection modes."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    DISABLED = "disabled"

# =============================================================================
# ENTERPRISE DATACLASSES
# =============================================================================

@dataclass
class EnglishFileHandlerConfig:
    """Configuration for English file handler operations."""
    
    data_dir: Optional[Path] = None
    max_file_size_mb: float = EnglishFileHandlerConstants.MAX_FILE_SIZE_MB
    chunk_size: int = EnglishFileHandlerConstants.CHUNK_SIZE
    cleaning_level: CleaningLevel = CleaningLevel.STANDARD
    language_detection_mode: LanguageDetectionMode = LanguageDetectionMode.AUTOMATIC
    enable_nltk_processing: bool = True
    min_word_length: int = EnglishFileHandlerConstants.MIN_WORD_LENGTH
    max_comment_length: int = EnglishFileHandlerConstants.MAX_COMMENT_LENGTH
    batch_size: int = EnglishFileHandlerConstants.BATCH_SIZE
    enable_progress_tracking: bool = True
    fallback_to_desktop: bool = True
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.data_dir is None:
            self.data_dir = Path.home() / EnglishFileHandlerConstants.DEFAULT_DATA_DIR

@dataclass
class FileInfo:
    """Information about a processed file."""
    
    path: Path
    name: str
    size_bytes: int
    file_type: FileType
    youtube_id: Optional[str] = None
    encoding: str = "utf-8"
    line_count: Optional[int] = None
    processing_time: Optional[float] = None
    
    @property
    def size_mb(self) -> float:
        """File size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def display_name(self) -> str:
        """Display-friendly file name."""
        return f"{self.name} ({self.size_mb:.1f}MB)"

@dataclass
class ProcessingResult:
    """Result of file processing operation."""
    
    status: ProcessingStatus
    data: Optional[pd.DataFrame] = None
    text_column: Optional[str] = None
    message: str = ""
    error_details: Optional[str] = None
    processing_time: float = 0.0
    rows_processed: int = 0
    rows_cleaned: int = 0
    english_comments_count: int = 0
    
    @property
    def success(self) -> bool:
        """Whether the processing was successful."""
        return self.status == ProcessingStatus.SUCCESS
    
    @property
    def has_data(self) -> bool:
        """Whether the result contains valid data."""
        return self.data is not None and not self.data.empty

@dataclass
class TextCleaningResult:
    """Result of text cleaning operation."""
    
    original_text: str
    cleaned_text: str
    removed_urls: int = 0
    removed_special_chars: int = 0
    removed_numbers: int = 0
    removed_short_words: int = 0
    processing_time: float = 0.0
    
    @property
    def cleaning_ratio(self) -> float:
        """Ratio of cleaned text length to original."""
        if not self.original_text:
            return 0.0
        return len(self.cleaned_text) / len(self.original_text)

@dataclass
class EnglishFileHandlerResults:
    """Comprehensive results from file handler operations."""
    
    file_info: FileInfo
    processing_result: ProcessingResult
    preview_data: Optional[pd.DataFrame] = None
    cleaning_stats: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.cleaning_stats is None:
            self.cleaning_stats = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}

# =============================================================================
# ENTERPRISE COMPONENTS
# =============================================================================

class EnglishFileValidator:
    """Validates files and file operations for English comment analysis."""
    
    def __init__(self, config: EnglishFileHandlerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_file_path(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate a file path for accessibility and format.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, f"File does not exist: {path}"
            
            if not path.is_file():
                return False, f"Path is not a file: {path}"
            
            if path.stat().st_size == 0:
                return False, f"File is empty: {path}"
            
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                return False, f"File too large: {size_mb:.1f}MB (max: {self.config.max_file_size_mb}MB)"
            
            if path.suffix.lower() not in EnglishFileHandlerConstants.ALL_SUPPORTED_EXTENSIONS:
                return False, f"Unsupported file type: {path.suffix}"
            
            return True, "File validation successful"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_dataframe(self, df: pd.DataFrame, text_column: str) -> Tuple[bool, str]:
        """
        Validate a DataFrame for comment analysis.
        
        Args:
            df: DataFrame to validate
            text_column: Name of text column
            
        Returns:
            Tuple of (is_valid, message)
        """
        if df.empty:
            return False, "DataFrame is empty"
        
        if text_column not in df.columns:
            return False, f"Text column '{text_column}' not found in DataFrame"
        
        non_null_count = df[text_column].notna().sum()
        if non_null_count == 0:
            return False, f"No valid text data in column '{text_column}'"
        
        return True, f"DataFrame validation successful ({len(df)} rows, {non_null_count} with text)"
    
    def get_file_info(self, file_path: Union[str, Path]) -> FileInfo:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to analyze
            
        Returns:
            FileInfo object
        """
        path = Path(file_path)
        file_type = self._detect_file_type(path)
        youtube_id = self._extract_youtube_id(path.name)
        
        return FileInfo(
            path=path,
            name=path.name,
            size_bytes=path.stat().st_size,
            file_type=file_type,
            youtube_id=youtube_id
        )
    
    def _detect_file_type(self, path: Path) -> FileType:
        """Detect file type from extension."""
        suffix = path.suffix.lower()
        if suffix == '.csv':
            return FileType.CSV
        elif suffix == '.json':
            return FileType.JSON
        elif suffix == '.jsonl':
            return FileType.JSONL
        else:
            return FileType.UNKNOWN
    
    def _extract_youtube_id(self, filename: str) -> Optional[str]:
        """Extract YouTube video ID from filename."""
        for pattern in EnglishFileHandlerConstants.YOUTUBE_ID_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        return None

class EnglishCSVProcessor:
    """Specialized processor for CSV file handling."""
    
    def __init__(self, config: EnglishFileHandlerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_csv_content(self, file_content: str) -> pd.DataFrame:
        """
        Process CSV content with robust parsing.
        
        Args:
            file_content: Raw CSV content
            
        Returns:
            Processed DataFrame
        """
        start_time = time.time()
        
        try:
            lines = file_content.strip().split('\n')
            cleaned_data = []
            
            for line_index, line in enumerate(lines):
                if line_index % EnglishFileHandlerConstants.PROGRESS_UPDATE_INTERVAL == 0:
                    self.logger.debug(f"Processing line {line_index + 1}/{len(lines)}")
                
                # Robust CSV parsing
                fields = self._parse_csv_line(line)
                
                # Extract comment (assuming second column)
                comment = fields[1] if len(fields) > 1 else ""
                
                if comment.strip():  # Only add non-empty comments
                    cleaned_data.append({
                        'comment_text': comment.strip(),
                        'original_line': line_index + 1,
                        'field_count': len(fields)
                    })
            
            processing_time = time.time() - start_time
            self.logger.info(f"CSV processing completed in {processing_time:.2f}s")
            
            return pd.DataFrame(cleaned_data)
            
        except Exception as e:
            self.logger.error(f"CSV processing error: {str(e)}")
            return pd.DataFrame(columns=['comment_text', 'original_line', 'field_count'])
    
    def _parse_csv_line(self, line: str) -> List[str]:
        """
        Parse a single CSV line with proper quote handling.
        
        Args:
            line: CSV line to parse
            
        Returns:
            List of field values
        """
        fields = []
        current_field = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                fields.append(current_field)
                current_field = ""
            else:
                current_field += char
        
        fields.append(current_field)
        return fields

class EnglishTextCleaner:
    """Advanced text cleaning for English comments."""
    
    def __init__(self, config: EnglishFileHandlerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """Initialize NLTK resources if enabled."""
        self.stop_words = set()
        
        if self.config.enable_nltk_processing:
            try:
                import nltk
                from nltk.corpus import stopwords
                
                # Ensure stopwords are downloaded
                try:
                    nltk.data.find('corpora/stopwords')
                except LookupError:
                    nltk.download('stopwords', quiet=True)
                
                self.stop_words = set(stopwords.words('english'))
                self.logger.info("NLTK stopwords initialized successfully")
                
            except ImportError:
                self.logger.warning("NLTK not available, using basic text cleaning")
            except Exception as e:
                self.logger.warning(f"NLTK initialization failed: {str(e)}")
    
    def clean_text(self, text: Any) -> str:
        """
        Clean text with configurable intensity.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text string
        """
        if pd.isna(text) or text is None or text == "":
            return ""
        
        text = str(text)
        
        # Apply cleaning based on level
        if self.config.cleaning_level == CleaningLevel.BASIC:
            return self._basic_cleaning(text)
        elif self.config.cleaning_level == CleaningLevel.STANDARD:
            return self._standard_cleaning(text)
        else:  # AGGRESSIVE
            return self._aggressive_cleaning(text)
    
    def _basic_cleaning(self, text: str) -> str:
        """Basic text cleaning."""
        # Just lowercase and strip
        return text.lower().strip()
    
    def _standard_cleaning(self, text: str) -> str:
        """Standard text cleaning with URL and basic filtering."""
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'www\S+', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Filter short words
        words = [word for word in text.split() 
                if len(word) >= self.config.min_word_length]
        
        return ' '.join(words)
    
    def _aggressive_cleaning(self, text: str) -> str:
        """Aggressive text cleaning with stopword removal."""
        # Start with standard cleaning
        text = self._standard_cleaning(text)
        
        # Remove stopwords if available
        if self.stop_words:
            words = [word for word in text.split() 
                    if word not in self.stop_words and len(word) >= self.config.min_word_length]
        else:
            words = [word for word in text.split() 
                    if len(word) >= self.config.min_word_length]
        
        return ' '.join(words)
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Clean a batch of texts efficiently.
        
        Args:
            texts: List of texts to clean
            
        Returns:
            List of cleaned texts
        """
        return [self.clean_text(text) for text in texts]

class EnglishPathManager:
    """Manages file paths and directory operations."""
    
    def __init__(self, config: EnglishFileHandlerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_directories()
    
    def _initialize_directories(self):
        """Initialize and create necessary directories."""
        try:
            self.config.data_dir.mkdir(exist_ok=True, parents=True)
            self.logger.info(f"Data directory initialized: {self.config.data_dir}")
        except Exception as e:
            self.logger.error(f"Error creating data directory: {e}")
            
            if self.config.fallback_to_desktop:
                fallback_dir = Path.home() / EnglishFileHandlerConstants.FALLBACK_DIR / EnglishFileHandlerConstants.DEFAULT_DATA_DIR
                try:
                    fallback_dir.mkdir(exist_ok=True, parents=True)
                    self.config.data_dir = fallback_dir
                    self.logger.warning(f"Using fallback directory: {fallback_dir}")
                except Exception as fallback_error:
                    self.logger.error(f"Fallback directory creation failed: {fallback_error}")
    
    def get_csv_files(self) -> List[Path]:
        """
        Get all CSV files from the data directory.
        
        Returns:
            List of CSV file paths
        """
        if not self.config.data_dir.exists():
            return []
        
        try:
            csv_files = list(self.config.data_dir.glob("*.csv"))
            self.logger.info(f"Found {len(csv_files)} CSV files in {self.config.data_dir}")
            return csv_files
        except Exception as e:
            self.logger.error(f"Error listing CSV files: {e}")
            return []
    
    def load_file_as_bytes(self, file_path: Path) -> Optional[BytesIO]:
        """
        Load a file as BytesIO object.
        
        Args:
            file_path: Path to load
            
        Returns:
            BytesIO object or None if error
        """
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            processed_file = BytesIO(file_content)
            processed_file.name = file_path.name
            
            self.logger.info(f"File loaded successfully: {file_path.name}")
            return processed_file
            
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return None

class EnglishDataPreprocessor:
    """Preprocesses data for English comment analysis."""
    
    def __init__(self, config: EnglishFileHandlerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def detect_text_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Automatically detect the text column in a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Name of detected text column or None
        """
        for col in EnglishFileHandlerConstants.POSSIBLE_TEXT_COLUMNS:
            if col in df.columns:
                # Verify it contains meaningful text data
                sample_size = min(10, len(df))
                sample_data = df[col].dropna().head(sample_size)
                
                if len(sample_data) > 0:
                    avg_length = sample_data.astype(str).str.len().mean()
                    if avg_length > 10:  # Reasonable text length
                        self.logger.info(f"Detected text column: {col}")
                        return col
        
        return None
    
    def apply_language_filtering(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Apply English language filtering if available.
        
        Args:
            df: DataFrame to filter
            text_column: Name of text column
            
        Returns:
            Filtered DataFrame
        """
        if self.config.language_detection_mode == LanguageDetectionMode.DISABLED:
            return df
        
        try:
            from utils.commentanalysis_english_language_detection import filter_english_comments
            filtered_df = filter_english_comments(df, text_column)
            self.logger.info(f"Language filtering: {len(df)} → {len(filtered_df)} English comments")
            return filtered_df
        except ImportError:
            self.logger.warning("Language detection module not available")
            return df
        except Exception as e:
            self.logger.error(f"Language filtering error: {e}")
            return df
    
    def create_preview(self, df: pd.DataFrame, max_rows: int = None, max_chars: int = None) -> pd.DataFrame:
        """
        Create a preview of the DataFrame.
        
        Args:
            df: DataFrame to preview
            max_rows: Maximum rows to show
            max_chars: Maximum characters per cell
            
        Returns:
            Preview DataFrame
        """
        if max_rows is None:
            max_rows = EnglishFileHandlerConstants.MAX_PREVIEW_ROWS
        if max_chars is None:
            max_chars = EnglishFileHandlerConstants.MAX_PREVIEW_CHARS
        
        preview_df = df.head(max_rows).copy()
        
        # Truncate long text columns
        for col in preview_df.columns:
            if preview_df[col].dtype == 'object':
                preview_df[col] = preview_df[col].apply(
                    lambda x: (str(x)[:max_chars] + '...' 
                             if isinstance(x, str) and len(str(x)) > max_chars 
                             else x)
                )
        
        return preview_df

# =============================================================================
# ENTERPRISE MANAGER
# =============================================================================

class EnglishFileHandlerManager:
    """
    Enterprise-level manager for English comment file handling operations.
    
    This manager orchestrates all file handling operations with enterprise-grade
    architecture, comprehensive error handling, and advanced processing capabilities.
    """
    
    def __init__(self, config: Optional[EnglishFileHandlerConfig] = None):
        """
        Initialize the English file handler manager.
        
        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or EnglishFileHandlerConfig()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.validator = EnglishFileValidator(self.config)
        self.csv_processor = EnglishCSVProcessor(self.config)
        self.text_cleaner = EnglishTextCleaner(self.config)
        self.path_manager = EnglishPathManager(self.config)
        self.preprocessor = EnglishDataPreprocessor(self.config)
        
        self.logger.info("EnglishFileHandlerManager initialized successfully")
    
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
    
    def process_uploaded_file(self, uploaded_file: Any) -> ProcessingResult:
        """
        Process an uploaded file with comprehensive error handling.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            ProcessingResult with data and metadata
        """
        start_time = time.time()
        
        try:
            # Determine file type
            file_type = self._get_file_type(uploaded_file.name)
            
            if file_type == FileType.CSV:
                return self._process_csv_file(uploaded_file, start_time)
            elif file_type in [FileType.JSON, FileType.JSONL]:
                return self._process_json_file(uploaded_file, start_time)
            else:
                return ProcessingResult(
                    status=ProcessingStatus.ERROR,
                    message=f"Unsupported file type: {uploaded_file.name}",
                    processing_time=time.time() - start_time
                )
                
        except Exception as e:
            self.logger.error(f"File processing error: {str(e)}")
            return ProcessingResult(
                status=ProcessingStatus.ERROR,
                message="File processing failed",
                error_details=str(e),
                processing_time=time.time() - start_time
            )
    
    def _process_csv_file(self, uploaded_file: Any, start_time: float) -> ProcessingResult:
        """Process CSV file."""
        try:
            file_content = uploaded_file.getvalue().decode('utf-8')
            df = self.csv_processor.process_csv_content(file_content)
            
            if df.empty:
                return ProcessingResult(
                    status=ProcessingStatus.ERROR,
                    message="No valid comments found in CSV file",
                    processing_time=time.time() - start_time
                )
            
            text_column = 'comment_text'
            
            # Apply language filtering
            df = self.preprocessor.apply_language_filtering(df, text_column)
            
            # Validate result
            is_valid, validation_message = self.validator.validate_dataframe(df, text_column)
            if not is_valid:
                return ProcessingResult(
                    status=ProcessingStatus.ERROR,
                    message=validation_message,
                    processing_time=time.time() - start_time
                )
            
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data=df,
                text_column=text_column,
                message=f"Successfully processed {len(df)} CSV comments",
                processing_time=time.time() - start_time,
                rows_processed=len(df),
                english_comments_count=len(df)
            )
            
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.ERROR,
                message="CSV processing failed",
                error_details=str(e),
                processing_time=time.time() - start_time
            )
    
    def _process_json_file(self, uploaded_file: Any, start_time: float) -> ProcessingResult:
        """Process JSON file."""
        try:
            df = pd.read_json(uploaded_file, lines=True)
            
            # Detect text column
            text_column = self.preprocessor.detect_text_column(df)
            if text_column is None:
                return ProcessingResult(
                    status=ProcessingStatus.ERROR,
                    message="No recognized text column found in JSON file",
                    processing_time=time.time() - start_time
                )
            
            # Apply language filtering
            df = self.preprocessor.apply_language_filtering(df, text_column)
            
            # Validate result
            is_valid, validation_message = self.validator.validate_dataframe(df, text_column)
            if not is_valid:
                return ProcessingResult(
                    status=ProcessingStatus.ERROR,
                    message=validation_message,
                    processing_time=time.time() - start_time
                )
            
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data=df,
                text_column=text_column,
                message=f"Successfully processed {len(df)} JSON comments",
                processing_time=time.time() - start_time,
                rows_processed=len(df),
                english_comments_count=len(df)
            )
            
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.ERROR,
                message="JSON processing failed",
                error_details=str(e),
                processing_time=time.time() - start_time
            )
    
    def process_file_from_path(self, file_path: Union[str, Path]) -> ProcessingResult:
        """
        Process a file from a given path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            ProcessingResult with data and metadata
        """
        # Validate file path
        is_valid, validation_message = self.validator.validate_file_path(file_path)
        if not is_valid:
            return ProcessingResult(
                status=ProcessingStatus.ERROR,
                message=validation_message
            )
        
        # Load file as bytes
        bytes_file = self.path_manager.load_file_as_bytes(Path(file_path))
        if bytes_file is None:
            return ProcessingResult(
                status=ProcessingStatus.ERROR,
                message=f"Failed to load file: {file_path}"
            )
        
        # Process as uploaded file
        return self.process_uploaded_file(bytes_file)
    
    def apply_text_cleaning(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Apply text cleaning to a DataFrame column.
        
        Args:
            df: DataFrame to process
            text_column: Column name to clean
            
        Returns:
            DataFrame with clean_text column added
        """
        start_time = time.time()
        
        try:
            df = df.copy()
            df['clean_text'] = df[text_column].apply(self.text_cleaner.clean_text)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Text cleaning completed in {processing_time:.2f}s")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Text cleaning error: {str(e)}")
            return df
    
    def get_available_files(self) -> List[FileInfo]:
        """
        Get information about available files in the data directory.
        
        Returns:
            List of FileInfo objects
        """
        csv_files = self.path_manager.get_csv_files()
        file_infos = []
        
        for file_path in csv_files:
            try:
                file_info = self.validator.get_file_info(file_path)
                file_infos.append(file_info)
            except Exception as e:
                self.logger.warning(f"Could not get info for file {file_path}: {e}")
        
        return file_infos
    
    def create_file_preview(self, df: pd.DataFrame, max_rows: int = None, max_chars: int = None) -> pd.DataFrame:
        """
        Create a preview of the DataFrame.
        
        Args:
            df: DataFrame to preview
            max_rows: Maximum rows to show
            max_chars: Maximum characters per cell
            
        Returns:
            Preview DataFrame
        """
        return self.preprocessor.create_preview(df, max_rows, max_chars)
    
    def _get_file_type(self, filename: str) -> FileType:
        """Get file type from filename."""
        suffix = Path(filename).suffix.lower()
        if suffix == '.csv':
            return FileType.CSV
        elif suffix == '.json':
            return FileType.JSON
        elif suffix == '.jsonl':
            return FileType.JSONL
        else:
            return FileType.UNKNOWN

# =============================================================================
# UI COMPONENTS - ENTERPRISE STREAMLIT INTEGRATION
# =============================================================================

def render_file_selection_ui(manager: EnglishFileHandlerManager) -> Optional[Any]:
    """
    Render file selection UI with enterprise features.
    
    Args:
        manager: File handler manager instance
        
    Returns:
        Selected file or None
    """
    st.subheader("📁 File Selection")
    
    # Get available files
    available_files = manager.get_available_files()
    selected_file = None
    
    # Option 1: Select from data folder
    if available_files:
        st.write("### 📂 Select from Data Folder")
        
        file_options = {f"{info.display_name}": info for info in available_files}
        selected_display_name = st.selectbox(
            f"Select file from folder '{manager.config.data_dir}':",
            options=list(file_options.keys())
        )
        
        if selected_display_name and st.button("🔍 Analyze Selected File"):
            selected_info = file_options[selected_display_name]
            bytes_file = manager.path_manager.load_file_as_bytes(selected_info.path)
            if bytes_file:
                selected_file = bytes_file
                st.success(f"Selected: {selected_info.name}")
    
    # Option 2: Upload file
    st.write("### 📤 Upload File")
    uploaded_file = st.file_uploader(
        "Upload CSV or JSON file with comments:",
        type=EnglishFileHandlerConstants.ALL_SUPPORTED_EXTENSIONS
    )
    
    if uploaded_file is not None:
        selected_file = uploaded_file
        st.info(f"Uploaded: {uploaded_file.name}")
    
    return selected_file

def render_processing_results(result: ProcessingResult) -> None:
    """
    Render processing results with comprehensive information.
    
    Args:
        result: Processing result to display
    """
    if result.status == ProcessingStatus.SUCCESS:
        st.success(f"✅ {result.message}")
        
        # Show processing metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows Processed", result.rows_processed)
        with col2:
            st.metric("Processing Time", f"{result.processing_time:.2f}s")
        with col3:
            st.metric("English Comments", result.english_comments_count)
            
    elif result.status == ProcessingStatus.ERROR:
        st.error(f"❌ {result.message}")
        if result.error_details:
            with st.expander("Error Details"):
                st.code(result.error_details)
    else:
        st.warning(f"⚠️ {result.message}")

def render_data_preview(manager: EnglishFileHandlerManager, df: pd.DataFrame, text_column: str) -> None:
    """
    Render data preview with enterprise features.
    
    Args:
        manager: File handler manager
        df: DataFrame to preview
        text_column: Name of text column
    """
    st.subheader("👀 Data Preview")
    
    # Create preview
    preview_df = manager.create_file_preview(df)
    
    # Show basic stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Comments", len(df))
    with col2:
        non_empty = df[text_column].notna().sum()
        st.metric("Non-Empty Comments", non_empty)
    with col3:
        avg_length = df[text_column].astype(str).str.len().mean()
        st.metric("Avg. Comment Length", f"{avg_length:.0f}")
    
    # Show preview table
    st.dataframe(preview_df, use_container_width=True)

def render_text_cleaning_options(manager: EnglishFileHandlerManager) -> EnglishFileHandlerConfig:
    """
    Render text cleaning configuration options.
    
    Args:
        manager: File handler manager
        
    Returns:
        Updated configuration
    """
    st.subheader("🧹 Text Cleaning Options")
    
    config = manager.config
    
    col1, col2 = st.columns(2)
    
    with col1:
        cleaning_level = st.selectbox(
            "Cleaning Level:",
            options=[level.value for level in CleaningLevel],
            index=list(CleaningLevel).index(config.cleaning_level),
            help="Basic: minimal cleaning, Standard: remove URLs/special chars, Aggressive: + stopword removal"
        )
        config.cleaning_level = CleaningLevel(cleaning_level)
        
        config.enable_nltk_processing = st.checkbox(
            "Enable NLTK Processing",
            value=config.enable_nltk_processing,
            help="Use NLTK for advanced text processing (stopword removal, etc.)"
        )
    
    with col2:
        config.min_word_length = st.slider(
            "Minimum Word Length:",
            min_value=1,
            max_value=5,
            value=config.min_word_length,
            help="Words shorter than this will be removed"
        )
        
        language_mode = st.selectbox(
            "Language Detection:",
            options=[mode.value for mode in LanguageDetectionMode],
            index=list(LanguageDetectionMode).index(config.language_detection_mode),
            help="How to handle language detection for English comments"
        )
        config.language_detection_mode = LanguageDetectionMode(language_mode)
    
    return config

# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_english_file_handler(data_dir: Optional[Path] = None, **kwargs) -> EnglishFileHandlerManager:
    """
    Factory function to create an English file handler manager.
    
    Args:
        data_dir: Data directory path
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured EnglishFileHandlerManager
    """
    config = EnglishFileHandlerConfig(data_dir=data_dir, **kwargs)
    return EnglishFileHandlerManager(config)

def create_custom_config(**kwargs) -> EnglishFileHandlerConfig:
    """
    Factory function to create custom configuration.
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        EnglishFileHandlerConfig object
    """
    return EnglishFileHandlerConfig(**kwargs)

# =============================================================================
# BACKWARD COMPATIBILITY - LEGACY API
# =============================================================================

class CommentAnalysisFileHandler:
    """
    LEGACY: Original class interface for backward compatibility.
    
    This class maintains the original API while using the new enterprise
    architecture internally.
    """
    
    def __init__(self, data_dir):
        """Initialize with data directory (legacy API)."""
        self.manager = create_english_file_handler(data_dir=Path(data_dir))
        self.data_dir = self.manager.config.data_dir
    
    def get_files_from_data_folder(self):
        """Legacy: Get CSV files from data folder."""
        file_infos = self.manager.get_available_files()
        return [str(info.path) for info in file_infos]
    
    def clean_csv_data(self, file_content):
        """Legacy: Clean CSV data."""
        df = self.manager.csv_processor.process_csv_content(file_content)
        return df
    
    def clean_text(self, text):
        """Legacy: Clean individual text."""
        return self.manager.text_cleaner.clean_text(text)
    
    def load_and_clean_data(self, uploaded_file):
        """Legacy: Load and clean uploaded file."""
        result = self.manager.process_uploaded_file(uploaded_file)
        if result.success:
            return result.data, result.text_column
        else:
            st.error(result.message)
            return pd.DataFrame(), None
    
    def load_file_from_path(self, file_path):
        """Legacy: Load file from path."""
        return self.manager.path_manager.load_file_as_bytes(Path(file_path))
    
    def extract_video_id(self, filename):
        """Legacy: Extract YouTube video ID from filename (no file access needed)."""
        return self.manager.validator._extract_youtube_id(filename)
    
    def display_file_selection_ui(self):
        """Legacy: Display file selection UI."""
        return render_file_selection_ui(self.manager)
    
    def apply_text_cleaning(self, df, text_column):
        """Legacy: Apply text cleaning to DataFrame."""
        return self.manager.apply_text_cleaning(df, text_column)
    
    def show_file_info(self, filename):
        """Legacy: Show file information."""
        st.write(f"🔄 Processing file: **{filename}**")
    
    def get_preview(self, df, max_rows=5, max_chars=100):
        """Legacy: Get data preview."""
        return self.manager.create_file_preview(df, max_rows, max_chars)

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_usage():
    """Example of how to use the enterprise file handler."""
    
    # Create configuration
    config = EnglishFileHandlerConfig(
        cleaning_level=CleaningLevel.STANDARD,
        enable_nltk_processing=True,
        language_detection_mode=LanguageDetectionMode.AUTOMATIC
    )
    
    # Create manager
    manager = EnglishFileHandlerManager(config)
    
    # In Streamlit app:
    if 'file_handler_manager' not in st.session_state:
        st.session_state.file_handler_manager = manager
    
    # Use UI components
    selected_file = render_file_selection_ui(manager)
    
    if selected_file:
        result = manager.process_uploaded_file(selected_file)
        render_processing_results(result)
        
        if result.success:
            render_data_preview(manager, result.data, result.text_column)
            
            # Apply text cleaning
            cleaned_df = manager.apply_text_cleaning(result.data, result.text_column)
            st.success("Text cleaning applied successfully!")

if __name__ == "__main__":
    example_usage()