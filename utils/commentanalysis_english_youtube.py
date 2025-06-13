import streamlit as st
import re
import traceback
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class DisplayMode(Enum):
    """Display modes for YouTube video information"""
    COMPACT = "compact"
    DETAILED = "detailed"
    EMBEDDED = "embedded"
    INFO_ONLY = "info_only"


class ExtractionPattern(Enum):
    """Available patterns for video ID extraction"""
    STANDARD = "standard"  # _([a-zA-Z0-9_-]{11})_
    ALTERNATIVE = "alternative"  # _([a-zA-Z0-9_-]{11})
    FILENAME_PREFIX = "filename_prefix"  # ^([a-zA-Z0-9_-]{11})_
    URL_EXTRACT = "url_extract"  # Full URL patterns


class VideoQuality(Enum):
    """Video embed quality options"""
    HD = "hd720"
    STANDARD = "sd480"
    LOW = "sd360"
    AUTO = "auto"


@dataclass
class YouTubeConfig:
    """Configuration for YouTube API and display settings"""
    quiet_mode: bool = True
    no_warnings: bool = True
    extract_flat: bool = False
    max_description_length: int = 300
    embed_width: int = 560
    embed_height: int = 315
    default_quality: VideoQuality = VideoQuality.HD
    enable_autoplay: bool = False
    enable_controls: bool = True
    timeout_seconds: int = 30


@dataclass
class VideoInfo:
    """Structured video information data"""
    video_id: str
    title: str = "Title not available"
    views: Union[int, str] = "Views not available"
    publish_date: str = "Date not available"
    duration: Union[int, str] = "Duration not available"
    author: str = "Author not available"
    description: str = "Description not available"
    thumbnail_url: str = ""
    channel_id: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    retrieval_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert VideoInfo to dictionary format"""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "views": self.views,
            "publish_date": self.publish_date,
            "duration": self.duration,
            "author": self.author,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "channel_id": self.channel_id,
            "category": self.category,
            "tags": self.tags,
            "retrieval_timestamp": self.retrieval_timestamp
        }


@dataclass 
class ExtractionResult:
    """Result of video ID extraction process"""
    video_id: Optional[str]
    pattern_used: Optional[ExtractionPattern]
    confidence: float  # 0.0 to 1.0
    source_filename: str
    extraction_timestamp: datetime = field(default_factory=datetime.now)


class YouTubeConstants:
    """Constants for YouTube integration"""
    
    # URL patterns
    YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="
    YOUTUBE_EMBED_URL = "https://www.youtube.com/embed/"
    
    # Regex patterns for video ID extraction
    PATTERNS = {
        ExtractionPattern.STANDARD: r'_([a-zA-Z0-9_-]{11})_',
        ExtractionPattern.ALTERNATIVE: r'_([a-zA-Z0-9_-]{11})',
        ExtractionPattern.FILENAME_PREFIX: r'^([a-zA-Z0-9_-]{11})_',
        ExtractionPattern.URL_EXTRACT: r'(?:v=|\/)([a-zA-Z0-9_-]{11})'
    }
    
    # YouTube ID validation pattern
    YOUTUBE_ID_PATTERN = r'^[a-zA-Z0-9_-]{11}$'
    
    # Error messages
    ERROR_MESSAGES = {
        "no_yt_dlp": "yt-dlp not installed. YouTube information cannot be retrieved.",
        "fetch_failed": "Couldn't fetch YouTube data",
        "invalid_id": "Invalid YouTube video ID format",
        "no_video_found": "Could not retrieve information from YouTube.",
        "timeout": "Request timed out while fetching video information"
    }
    
    # UI messages
    UI_MESSAGES = {
        "video_id_found": "🎬 YouTube Video ID: {}",
        "fetching_info": "Fetching information from YouTube video...",
        "show_hide_desc": "Show/hide full description",
        "download_info": "Download video information as CSV",
        "video_info_title": "YouTube Video Information",
        "general_info": "General Information",
        "description_section": "Description"
    }
    
    # Date format
    YOUTUBE_DATE_FORMAT = "%Y%m%d"
    DISPLAY_DATE_FORMAT = "%Y-%m-%d"
    
    # Iframe permissions
    IFRAME_PERMISSIONS = [
        "accelerometer", "autoplay", "clipboard-write", 
        "encrypted-media", "gyroscope", "picture-in-picture"
    ]


class FormatUtils:
    """Utility functions for formatting video information"""
    
    @staticmethod
    def format_duration(seconds: Union[int, str]) -> str:
        """
        Format duration in seconds to HH:MM:SS or MM:SS
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if not isinstance(seconds, int):
            return str(seconds)
        
        if seconds <= 0:
            return "00:00"
            
        minutes, secs = divmod(seconds, 60)
        hours, mins = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            return f"{mins:02d}:{secs:02d}"
    
    @staticmethod
    def format_views(views: Union[int, str]) -> str:
        """
        Format view count with proper thousand separators
        
        Args:
            views: View count (integer or string)
            
        Returns:
            Formatted view count string with commas
        """
        if isinstance(views, int):
            if views >= 1_000_000_000:
                return f"{views / 1_000_000_000:.1f}B"
            elif views >= 1_000_000:
                return f"{views / 1_000_000:.1f}M"
            elif views >= 1_000:
                return f"{views / 1_000:.1f}K"
            else:
                return f"{views:,}"
        else:
            return str(views)
    
    @staticmethod
    def format_publish_date(date_str: str) -> str:
        """
        Format YouTube publish date from YYYYMMDD to YYYY-MM-DD
        
        Args:
            date_str: Date string in YYYYMMDD format
            
        Returns:
            Formatted date string
        """
        if isinstance(date_str, str) and len(date_str) == 8 and date_str.isdigit():
            try:
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            except (ValueError, IndexError):
                return date_str
        return str(date_str)
    
    @staticmethod
    def truncate_description(description: str, max_length: int = 300) -> Tuple[str, bool]:
        """
        Truncate description text to specified length
        
        Args:
            description: Original description text
            max_length: Maximum length for truncation
            
        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        if not isinstance(description, str):
            return str(description), False
            
        if len(description) <= max_length:
            return description, False
            
        # Find a good break point (end of sentence or word)
        truncated = description[:max_length]
        
        # Try to break at sentence end
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        sentence_end = max(last_period, last_exclamation, last_question)
        
        if sentence_end > max_length * 0.7:  # If sentence end is reasonably close
            return description[:sentence_end + 1], True
        
        # Otherwise break at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # If word boundary is reasonably close
            return description[:last_space] + "...", True
        
        return truncated + "...", True


class VideoIDExtractor:
    """Advanced video ID extraction with multiple pattern matching"""
    
    def __init__(self, config: YouTubeConfig):
        self.config = config
    
    def extract_video_id(self, filename: str) -> ExtractionResult:
        """
        Extract YouTube video ID from filename using multiple patterns
        
        Args:
            filename: Filename to extract video ID from
            
        Returns:
            ExtractionResult with video ID and metadata
        """
        filename = str(filename)
        
        # Try patterns in order of confidence
        for pattern_type in [ExtractionPattern.STANDARD, ExtractionPattern.ALTERNATIVE, 
                           ExtractionPattern.FILENAME_PREFIX]:
            result = self._try_pattern(filename, pattern_type)
            if result.video_id:
                return result
        
        # No match found
        return ExtractionResult(
            video_id=None,
            pattern_used=None,
            confidence=0.0,
            source_filename=filename
        )
    
    def _try_pattern(self, filename: str, pattern_type: ExtractionPattern) -> ExtractionResult:
        """
        Try a specific pattern for video ID extraction
        
        Args:
            filename: Filename to test
            pattern_type: Pattern type to use
            
        Returns:
            ExtractionResult with match information
        """
        pattern = YouTubeConstants.PATTERNS[pattern_type]
        match = re.search(pattern, filename)
        
        if match:
            video_id = match.group(1)
            
            # Validate video ID format
            if self._validate_video_id(video_id):
                confidence = self._calculate_confidence(filename, video_id, pattern_type)
                return ExtractionResult(
                    video_id=video_id,
                    pattern_used=pattern_type,
                    confidence=confidence,
                    source_filename=filename
                )
        
        return ExtractionResult(
            video_id=None,
            pattern_used=pattern_type,
            confidence=0.0,
            source_filename=filename
        )
    
    def _validate_video_id(self, video_id: str) -> bool:
        """
        Validate YouTube video ID format
        
        Args:
            video_id: Video ID to validate
            
        Returns:
            True if valid YouTube video ID format
        """
        return bool(re.match(YouTubeConstants.YOUTUBE_ID_PATTERN, video_id))
    
    def _calculate_confidence(self, filename: str, video_id: str, pattern_type: ExtractionPattern) -> float:
        """
        Calculate confidence score for extraction
        
        Args:
            filename: Source filename
            video_id: Extracted video ID
            pattern_type: Pattern used for extraction
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = {
            ExtractionPattern.STANDARD: 0.95,
            ExtractionPattern.ALTERNATIVE: 0.85,
            ExtractionPattern.FILENAME_PREFIX: 0.75,
            ExtractionPattern.URL_EXTRACT: 0.90
        }.get(pattern_type, 0.5)
        
        # Adjust based on filename characteristics
        if "_" in filename and video_id in filename:
            base_confidence += 0.05
        
        if filename.lower().endswith('.csv'):
            base_confidence += 0.02
            
        return min(base_confidence, 1.0)


class VideoInfoFetcher:
    """Handles YouTube API integration and video information retrieval"""
    
    def __init__(self, config: YouTubeConfig):
        self.config = config
        self.yt_dlp_available = self._check_yt_dlp_availability()
    
    def _check_yt_dlp_availability(self) -> bool:
        """Check if yt-dlp is available for import"""
        try:
            import yt_dlp
            return True
        except ImportError:
            return False
    
    def fetch_video_info(self, video_id: str) -> Optional[VideoInfo]:
        """
        Fetch comprehensive video information from YouTube
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            VideoInfo object or None if fetch failed
        """
        if not self.yt_dlp_available:
            st.warning(YouTubeConstants.ERROR_MESSAGES["no_yt_dlp"])
            return None
        
        if not video_id:
            return None
        
        try:
            from yt_dlp import YoutubeDL
            
            url = f"{YouTubeConstants.YOUTUBE_BASE_URL}{video_id}"
            ydl_opts = self._get_yt_dlp_options()
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._process_video_info(video_id, info)
                
        except Exception as e:
            st.warning(f"{YouTubeConstants.ERROR_MESSAGES['fetch_failed']}: {e}")
            return None
    
    def _get_yt_dlp_options(self) -> Dict[str, Any]:
        """Get yt-dlp configuration options"""
        return {
            'quiet': self.config.quiet_mode,
            'no_warnings': self.config.no_warnings,
            'extract_flat': self.config.extract_flat,
            'socket_timeout': self.config.timeout_seconds
        }
    
    def _process_video_info(self, video_id: str, raw_info: Dict[str, Any]) -> VideoInfo:
        """
        Process raw yt-dlp info into structured VideoInfo
        
        Args:
            video_id: YouTube video ID
            raw_info: Raw information from yt-dlp
            
        Returns:
            Processed VideoInfo object
        """
        publish_date = raw_info.get('upload_date', 'Date not available')
        if isinstance(publish_date, str):
            publish_date = FormatUtils.format_publish_date(publish_date)
        
        return VideoInfo(
            video_id=video_id,
            title=raw_info.get('title', 'Title not available'),
            views=raw_info.get('view_count', 'Views not available'),
            publish_date=publish_date,
            duration=raw_info.get('duration', 'Duration not available'),
            author=raw_info.get('uploader', 'Author not available'),
            description=raw_info.get('description', 'Description not available'),
            thumbnail_url=raw_info.get('thumbnail', ''),
            channel_id=raw_info.get('channel_id', ''),
            category=raw_info.get('category', ''),
            tags=raw_info.get('tags', []) or []
        )


class VideoInfoRenderer:
    """Handles video information display and UI rendering"""
    
    def __init__(self, config: YouTubeConfig):
        self.config = config
    
    def display_video_info(self, video_id: str, video_info: Optional[VideoInfo] = None, 
                          display_mode: DisplayMode = DisplayMode.DETAILED) -> None:
        """
        Display comprehensive YouTube video information
        
        Args:
            video_id: YouTube video ID
            video_info: VideoInfo object (if None, will fetch)
            display_mode: Display mode for information
        """
        if not video_id:
            return
        
        # Display video ID confirmation
        st.success(YouTubeConstants.UI_MESSAGES["video_id_found"].format(video_id))
        
        # Create expandable section
        with st.expander(YouTubeConstants.UI_MESSAGES["video_info_title"], expanded=True):
            if display_mode in [DisplayMode.DETAILED, DisplayMode.EMBEDDED]:
                self._render_embedded_video(video_id)
            
            if video_info:
                self._render_video_information(video_info, display_mode)
            else:
                st.info("Video information not available.")
    
    def _render_embedded_video(self, video_id: str) -> None:
        """Render embedded YouTube video player"""
        st.subheader("YouTube Video")
        
        permissions = "; ".join(YouTubeConstants.IFRAME_PERMISSIONS)
        embed_url = f"{YouTubeConstants.YOUTUBE_EMBED_URL}{video_id}"
        
        # Add quality and autoplay parameters if configured
        params = []
        if not self.config.enable_autoplay:
            params.append("autoplay=0")
        if not self.config.enable_controls:
            params.append("controls=0")
            
        if params:
            embed_url += "?" + "&".join(params)
        
        iframe_html = f"""
        <iframe width="{self.config.embed_width}" height="{self.config.embed_height}" 
        src="{embed_url}" frameborder="0" allow="{permissions}" allowfullscreen></iframe>
        """
        
        st.markdown(iframe_html, unsafe_allow_html=True)
    
    def _render_video_information(self, video_info: VideoInfo, display_mode: DisplayMode) -> None:
        """
        Render video information in specified display mode
        
        Args:
            video_info: VideoInfo object with video data
            display_mode: How to display the information
        """
        if display_mode == DisplayMode.COMPACT:
            self._render_compact_info(video_info)
        else:
            self._render_detailed_info(video_info)
        
        # Add download option
        self._render_download_option(video_info)
    
    def _render_compact_info(self, video_info: VideoInfo) -> None:
        """Render video information in compact format"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Title:** {video_info.title}")
            st.markdown(f"**Author:** {video_info.author}")
        
        with col2:
            st.markdown(f"**Views:** {FormatUtils.format_views(video_info.views)}")
            st.markdown(f"**Duration:** {FormatUtils.format_duration(video_info.duration)}")
    
    def _render_detailed_info(self, video_info: VideoInfo) -> None:
        """Render video information in detailed format"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {YouTubeConstants.UI_MESSAGES['general_info']}")
            st.markdown(f"**Title:** {video_info.title}")
            st.markdown(f"**Author:** {video_info.author}")
            st.markdown(f"**Views:** {FormatUtils.format_views(video_info.views)}")
            st.markdown(f"**Published on:** {video_info.publish_date}")
            st.markdown(f"**Duration:** {FormatUtils.format_duration(video_info.duration)}")
            
            # Additional info if available
            if video_info.category:
                st.markdown(f"**Category:** {video_info.category}")
            if video_info.tags:
                tags_display = ", ".join(video_info.tags[:5])  # Show first 5 tags
                if len(video_info.tags) > 5:
                    tags_display += f" (+{len(video_info.tags) - 5} more)"
                st.markdown(f"**Tags:** {tags_display}")
        
        with col2:
            st.markdown(f"### {YouTubeConstants.UI_MESSAGES['description_section']}")
            self._render_description(video_info)
    
    def _render_description(self, video_info: VideoInfo) -> None:
        """Render video description with truncation and toggle"""
        description = video_info.description
        truncated_desc, was_truncated = FormatUtils.truncate_description(
            description, self.config.max_description_length
        )
        
        st.markdown(truncated_desc)
        
        if was_truncated:
            # Use session state for toggle
            toggle_key = f"show_full_description_{video_info.video_id}"
            if toggle_key not in st.session_state:
                st.session_state[toggle_key] = False
            
            if st.button(YouTubeConstants.UI_MESSAGES["show_hide_desc"], 
                        key=f"desc_button_{video_info.video_id}"):
                st.session_state[toggle_key] = not st.session_state[toggle_key]
            
            if st.session_state[toggle_key]:
                st.markdown("---")
                st.markdown(description)
    
    def _render_download_option(self, video_info: VideoInfo) -> None:
        """Render download option for video information"""
        video_df = pd.DataFrame([video_info.to_dict()])
        csv_data = video_df.to_csv(index=False)
        
        st.download_button(
            label=YouTubeConstants.UI_MESSAGES["download_info"],
            data=csv_data,
            file_name=f"{video_info.video_id}_info.csv",
            mime="text/csv"
        )


class YouTubeConfigManager:
    """Manages YouTube integration configuration"""
    
    @staticmethod
    def create_default_config() -> YouTubeConfig:
        """Create default YouTube configuration"""
        return YouTubeConfig()
    
    @staticmethod
    def create_minimal_config() -> YouTubeConfig:
        """Create minimal configuration for basic usage"""
        return YouTubeConfig(
            max_description_length=150,
            embed_width=400,
            embed_height=225,
            enable_autoplay=False,
            enable_controls=True
        )
    
    @staticmethod
    def create_debug_config() -> YouTubeConfig:
        """Create configuration optimized for debugging"""
        return YouTubeConfig(
            quiet_mode=False,
            no_warnings=False,
            timeout_seconds=60,
            max_description_length=500
        )


class YouTubeManager:
    """
    Enterprise YouTube Manager for Comment Analysis
    
    Provides complete YouTube integration with video information retrieval,
    display capabilities, and advanced video ID extraction
    """
    
    def __init__(self, config: Optional[YouTubeConfig] = None):
        """
        Initialize YouTube Manager with configuration
        
        Args:
            config: YouTube configuration, uses default if None
        """
        self.config = config or YouTubeConfigManager.create_default_config()
        self.video_fetcher = VideoInfoFetcher(self.config)
        self.video_renderer = VideoInfoRenderer(self.config)
        self.id_extractor = VideoIDExtractor(self.config)
        self.format_utils = FormatUtils()
    
    def get_video_info(self, video_id: str) -> Optional[VideoInfo]:
        """
        Get comprehensive video information
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            VideoInfo object or None if retrieval failed
        """
        return self.video_fetcher.fetch_video_info(video_id)
    
    def display_youtube_info(self, video_id: str, display_mode: DisplayMode = DisplayMode.DETAILED) -> None:
        """
        Display YouTube video information with embedded player
        
        Args:
            video_id: YouTube video ID
            display_mode: How to display the information
        """
        if not video_id:
            return
        
        # Fetch video information
        with st.spinner(YouTubeConstants.UI_MESSAGES["fetching_info"]):
            video_info = self.get_video_info(video_id)
        
        # Display information
        self.video_renderer.display_video_info(video_id, video_info, display_mode)
    
    def extract_video_id(self, filename: str) -> ExtractionResult:
        """
        Extract YouTube video ID from filename
        
        Args:
            filename: Filename to extract video ID from
            
        Returns:
            ExtractionResult with extraction details
        """
        return self.id_extractor.extract_video_id(filename)
    
    def format_duration(self, seconds: Union[int, str]) -> str:
        """Format video duration"""
        return self.format_utils.format_duration(seconds)
    
    def format_views(self, views: Union[int, str]) -> str:
        """Format view count"""
        return self.format_utils.format_views(views)
    
    def is_available(self) -> bool:
        """Check if YouTube functionality is available"""
        return self.video_fetcher.yt_dlp_available
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Recreate components with new config
        self.video_fetcher = VideoInfoFetcher(self.config)
        self.video_renderer = VideoInfoRenderer(self.config)
        self.id_extractor = VideoIDExtractor(self.config)


# Backward Compatibility Layer
class CommentAnalysisYouTube:
    """
    Legacy class for backward compatibility
    
    Maintains the same API as the original implementation while
    internally using the new enterprise architecture
    """
    
    def __init__(self):
        """Initialize with legacy compatibility"""
        self.youtube_manager = YouTubeManager()
        self.yt_dlp_available = self.youtube_manager.is_available()
        
        # Legacy warning for missing yt-dlp
        if not self.yt_dlp_available:
            st.warning("yt-dlp not installed. YouTube information cannot be retrieved.")
    
    def get_video_info(self, video_id):
        """Legacy method for video info retrieval"""
        video_info = self.youtube_manager.get_video_info(video_id)
        if video_info:
            # Convert to legacy dictionary format
            return video_info.to_dict()
        return None
    
    def format_duration(self, seconds):
        """Legacy method for duration formatting"""
        return self.youtube_manager.format_duration(seconds)
    
    def format_views(self, views):
        """Legacy method for view formatting"""
        return self.youtube_manager.format_views(views)
    
    def display_youtube_info(self, video_id):
        """Legacy method for video info display"""
        self.youtube_manager.display_youtube_info(video_id, DisplayMode.DETAILED)
    
    def extract_video_id(self, filename):
        """Legacy method for video ID extraction"""
        result = self.youtube_manager.extract_video_id(filename)
        return result.video_id  # Return only the video ID for legacy compatibility


# Factory functions for easy instantiation
def create_youtube_manager(mode: str = "default") -> YouTubeManager:
    """
    Factory function to create YouTube Manager with specific configuration
    
    Args:
        mode: Configuration mode ('default', 'minimal', 'debug')
        
    Returns:
        Configured YouTubeManager instance
    """
    if mode == "minimal":
        config = YouTubeConfigManager.create_minimal_config()
    elif mode == "debug":
        config = YouTubeConfigManager.create_debug_config()
    else:
        config = YouTubeConfigManager.create_default_config()
    
    return YouTubeManager(config)


def get_youtube_analyzer() -> CommentAnalysisYouTube:
    """
    Quick start function for legacy code compatibility
    
    Returns:
        CommentAnalysisYouTube instance for backward compatibility
    """
    return CommentAnalysisYouTube()


# Advanced usage examples for documentation
def example_usage():
    """Example usage patterns for the YouTube integration system"""
    
    # Enterprise usage with custom configuration
    config = YouTubeConfig(
        max_description_length=500,
        embed_width=800,
        embed_height=450,
        enable_autoplay=False
    )
    
    youtube_manager = YouTubeManager(config)
    
    # Extract video ID with detailed results
    extraction_result = youtube_manager.extract_video_id("20240618_87TYPn6gbwA_video.csv")
    if extraction_result.video_id:
        st.write(f"Found video ID: {extraction_result.video_id}")
        st.write(f"Confidence: {extraction_result.confidence:.2%}")
        
        # Display video information
        youtube_manager.display_youtube_info(extraction_result.video_id, DisplayMode.DETAILED)
    
    # Legacy compatibility usage
    legacy_analyzer = CommentAnalysisYouTube()
    video_id = legacy_analyzer.extract_video_id("filename_87TYPn6gbwA_title.csv")
    if video_id:
        legacy_analyzer.display_youtube_info(video_id)