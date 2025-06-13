"""
HerEducation - YouTube Analyzer
Modernized version with relative paths and modular architecture

CRITICAL REPAIR: Absolute paths → Relative paths
AFTER: Modular structure, portable paths, clean architecture

✅ REPAIRS v2.0:
- Added dropdown for single audio file selection
- Robust CSV parser for comment analysis
- Enhanced audio file display with video IDs
"""

import streamlit as st
import os
import pandas as pd
from pathlib import Path
import sys
import importlib.util
import tempfile
import plotly.express as px
import re
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Optional, List, Dict, Any, Tuple
import csv
import chardet
import logging
import shutil

# Shared components for CSS deduplication
from utils.shared_components import setup_standard_page, display_standard_footer

# ===== PAGE SETUP =====
st.set_page_config(
    page_title="4_YouTube_Analyzer",
    page_icon="🎬",
    layout="wide"
)

# Setup Sidebar (shared components instead of 70+ lines of CSS)
st.sidebar.write("")
st.sidebar.markdown("""
<style>
.sidebar-copyright-fixed-bottom {
    position: fixed;
    bottom: 10px;
    left: 10px;
    right: 10px;
    max-width: 224px;
    padding: 15px 10px;
    margin: 10px 0;
    background: rgba(255, 107, 152, 0.1);
    border-left: 3px solid #FF6B98;
    border-radius: 8px;
    text-align: center;
    font-size: 0.75rem;
    z-index: 999;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sidebar-copyright-fixed-bottom .author {
    color: #FF6B98;
    font-weight: 600;
    font-size: 0.8rem;
    margin-bottom: 3px;
}

.sidebar-copyright-fixed-bottom .project {
    color: #666666;
    font-size: 0.65rem;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 80px;
}
</style>

<div class="sidebar-copyright-fixed-bottom">
    <div class="author">© Sandra Störkel</div>
    <div class="project">HerEducation 2025</div>
</div>
""", unsafe_allow_html=True)

# ===== CONFIGURATION =====
class YouTubeAnalyzerConfig:
    """Central configuration for YouTube Analyzer"""
    
    # ===== PATHS (RELATIVE!) =====
    BASE_DIR = Path(__file__).parent.parent  # HerEducation main directory
    UTILS_DIR = BASE_DIR / "utils"
    DATA_DIR = BASE_DIR / "data"
    AUDIO_DIR = DATA_DIR / "audio"
    TRANSCRIPT_DIR = DATA_DIR / "transcripts"
    COMMENTS_DIR = DATA_DIR / "comments"
    
    # Utils modules
    UTILS_MODULES = {
        "downloader": "youtube_downloader.py",
        "transcriber": "transcriber.py", 
        "comment_saver": "comment_saver_improved.py",
        "comment_saver_fallback": "comment_saver.py"
    }
    
    # Default settings
    DEFAULT_SEARCH_QUERY = "Markus Lanz Education"
    DEFAULT_KEYWORDS = ["Education", "Teacher", "School", "Study", "Learning"]
    MAX_RESULTS_RANGE = (10, 200, 100, 10)  # min, max, default, step
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Creates all necessary directories"""
        for dir_path in [cls.DATA_DIR, cls.AUDIO_DIR, cls.TRANSCRIPT_DIR, cls.COMMENTS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

# ===== ROBUST CSV READING FUNCTIONS =====
def read_youtube_comments_csv_robust(csv_file_path: str) -> Optional[pd.DataFrame]:
    """
    Robust CSV reader function for YouTube comments
    Handles common CSV parsing issues
    """
    
    # Various reading strategies in order of preference
    strategies = [
        # Strategy 1: Standard pandas with error handling
        {"name": "Standard", "params": {"encoding": "utf-8-sig", "on_bad_lines": "skip"}},
        
        # Strategy 2: With quotechar and escapechar
        {"name": "Quoted", "params": {
            "encoding": "utf-8-sig", 
            "on_bad_lines": "skip",
            "quotechar": '"',
            "escapechar": '\\'
        }},
        
        # Strategy 3: With different separator detection
        {"name": "Auto-detect", "params": {
            "encoding": "utf-8-sig",
            "on_bad_lines": "skip",
            "sep": None,  # Auto-detect
            "engine": "python"
        }},
        
        # Strategy 4: Very robust settings
        {"name": "Robust", "params": {
            "encoding": "utf-8-sig",
            "on_bad_lines": "skip",
            "quoting": csv.QUOTE_ALL,
            "engine": "python",
            "skipinitialspace": True
        }},
        
        # Strategy 5: With encoding detection
        {"name": "Encoding-detect", "params": {
            "on_bad_lines": "skip",
            "quoting": csv.QUOTE_MINIMAL,
            "engine": "python"
        }}
    ]
    
    for i, strategy in enumerate(strategies, 1):
        try:
            st.write(f"🔄 Trying reading strategy {i}: {strategy['name']}")
            
            params = strategy["params"].copy()
            
            # Special handling for encoding detection
            if strategy["name"] == "Encoding-detect":
                # Auto-detect encoding
                with open(csv_file_path, 'rb') as f:
                    raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    params["encoding"] = detected.get("encoding", "utf-8")
                    st.write(f"   📊 Detected encoding: {params['encoding']}")
            
            # Read CSV
            df = pd.read_csv(csv_file_path, **params)
            
            # Validation
            if df.empty:
                st.warning(f"⚠️ Strategy {i} resulted in empty data")
                continue
                
            if len(df.columns) < 3:  # Expected at least author, text, time
                st.warning(f"⚠️ Strategy {i} resulted in too few columns: {len(df.columns)}")
                continue
            
            st.success(f"✅ Success with strategy {i}: {strategy['name']}")
            st.info(f"📊 Loaded data: {len(df)} rows, {len(df.columns)} columns")
            st.info(f"📋 Columns: {', '.join(df.columns.tolist())}")
            
            return clean_and_validate_dataframe(df)
            
        except Exception as e:
            st.warning(f"⚠️ Strategy {i} failed: {str(e)}")
            continue
    
    # If all strategies fail, try raw text analysis
    st.error("❌ All CSV reading strategies failed. Trying raw data analysis...")
    return analyze_csv_file_structure(csv_file_path)

def clean_and_validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and validates the loaded DataFrame
    """
    
    # Column mapping for different formats
    column_mappings = {
        # Standard youtube-comment-downloader format
        'cid': 'comment_id',
        'votes': 'likes_count',
        
        # Alternative formats
        'vote': 'likes_count',
        'like': 'likes_count',
        'likes': 'likes_count',
        'id': 'comment_id',
        'comment': 'text',
        'content': 'text',
        'message': 'text'
    }
    
    # Rename columns if possible
    for old_name, new_name in column_mappings.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    # Add missing important columns
    if 'author' not in df.columns:
        df['author'] = 'Unknown'
    
    if 'text' not in df.columns and 'comment' in df.columns:
        df['text'] = df['comment']
    elif 'text' not in df.columns:
        df['text'] = 'No text available'
    
    if 'likes_count' not in df.columns:
        df['likes_count'] = 0
    
    if 'time' not in df.columns:
        df['time'] = 'Unknown'
    
    # Clean data types
    try:
        if 'likes_count' in df.columns:
            df['likes_count'] = pd.to_numeric(df['likes_count'], errors='coerce').fillna(0).astype(int)
    except:
        pass
    
    # Clean text columns
    for col in ['text', 'author']:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna('Unknown')
    
    # Remove empty rows
    df = df.dropna(subset=['text'])
    df = df[df['text'].str.strip() != '']
    
    return df

def analyze_csv_file_structure(csv_file_path: str) -> Optional[pd.DataFrame]:
    """
    Analyzes CSV file structure when parsing fails
    """
    try:
        st.subheader("🔍 CSV File Structure Analysis")
        
        # Read first lines as text
        with open(csv_file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            lines = f.readlines()[:10]
        
        st.write("📄 **First lines of file:**")
        for i, line in enumerate(lines[:5]):
            st.code(f"Line {i+1}: {line.strip()}")
        
        # Analyze separators
        first_line = lines[0] if lines else ""
        separators = [',', ';', '\t', '|']
        separator_counts = {sep: first_line.count(sep) for sep in separators}
        likely_separator = max(separator_counts, key=separator_counts.get)
        
        st.write(f"🔍 **Likely separator:** `{likely_separator}` ({separator_counts[likely_separator]} occurrences)")
        
        # Try with detected separator
        try:
            df = pd.read_csv(csv_file_path, 
                           sep=likely_separator, 
                           encoding='utf-8-sig',
                           on_bad_lines='skip',
                           engine='python')
            
            if not df.empty:
                st.success(f"✅ Success with separator '{likely_separator}'")
                return clean_and_validate_dataframe(df)
        except Exception as e:
            st.error(f"❌ Failed even with detected separator: {e}")
        
        # As last resort: manual line parsing
        return manual_csv_parsing(csv_file_path, lines)
        
    except Exception as e:
        st.error(f"❌ Structure analysis failed: {e}")
        return None

def manual_csv_parsing(csv_file_path: str, lines: list) -> Optional[pd.DataFrame]:
    """
    Manual parsing as last resort
    """
    try:
        st.write("🛠️ **Trying manual parsing...**")
        
        # Create simple comment structure
        comments_data = []
        
        for i, line in enumerate(lines[1:], 2):  # Skip header
            try:
                # Simplified parsing - take first 4 parts as basis
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    comment_data = {
                        'comment_id': parts[0] if len(parts) > 0 else f'comment_{i}',
                        'author': parts[1] if len(parts) > 1 else 'Unknown',
                        'text': ','.join(parts[2:]) if len(parts) > 2 else 'No text',  # Rest as text
                        'likes_count': 0,
                        'time': 'Unknown'
                    }
                    comments_data.append(comment_data)
            except:
                continue
        
        if comments_data:
            df = pd.DataFrame(comments_data)
            st.success(f"✅ Manual parsing successful: {len(df)} comments")
            return df
        else:
            st.error("❌ Manual parsing yielded no data")
            return None
            
    except Exception as e:
        st.error(f"❌ Manual parsing failed: {e}")
        return None

# ===== VIDEO ID EXTRACTION =====
def extract_video_id_from_filename(filename: str) -> Optional[str]:
    """
    Extracts video ID from MP3 filename
    Format: date_videoID_title.mp3
    Example: 2019-06-08_UdKPYVpsiX8_Education is nothing for Models - TV total.mp3
    """
    try:
        # Remove .mp3 extension
        base_name = filename.replace('.mp3', '')
        # Split by underscores
        parts = base_name.split('_')
        
        if len(parts) >= 2:
            # Video ID is the second part (index 1)
            video_id = parts[1]
            return video_id
        else:
            st.warning(f"⚠️ Filename has unexpected format: {filename}")
            return None
    except Exception as e:
        st.error(f"❌ Error extracting video ID from {filename}: {e}")
        return None

def download_comments_for_single_video(video_id: str, filename: str, comment_saver_module: Any) -> None:
    """Downloads comments for a single video"""
    
    save_all_comments = get_function_from_module(comment_saver_module, 'save_all_comments')
    
    if not save_all_comments:
        st.error("The function for saving comments is not available.")
        return
    
    with st.status(f"Downloading comments for {filename}...", expanded=True) as status:
        try:
            st.write(f"📺 Video ID: {video_id}")
            st.write(f"📁 File: {filename}")
            
            # Check if comments already exist
            base_name = filename.replace('.mp3', '')
            comment_file = YouTubeAnalyzerConfig.COMMENTS_DIR / f"{base_name}.csv"
            
            if comment_file.exists() and comment_file.stat().st_size > 0:
                st.info(f"✅ Comments already available: {comment_file.name}")
                status.update(label="Comments already available!", state="complete")
                return
            
            # Create temporary audio directory with only this file
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_audio_dir = Path(temp_dir) / "audio"
                temp_audio_dir.mkdir()
                
                # Copy the specific audio file
                source_file = YouTubeAnalyzerConfig.AUDIO_DIR / filename
                temp_file = temp_audio_dir / filename
                shutil.copy2(source_file, temp_file)
                
                # Download comments for this one file
                created_files = save_all_comments(
                    str(temp_audio_dir), 
                    str(YouTubeAnalyzerConfig.COMMENTS_DIR)
                )
                
                if created_files:
                    st.success(f"✅ Comments successfully downloaded!")
                    for file in created_files:
                        st.write(f"📁 Created: {os.path.basename(file)}")
                else:
                    st.warning("⚠️ No comments found or downloaded.")
            
            status.update(label="Comment download completed!", state="complete")
            
        except Exception as e:
            st.error(f"❌ Error downloading comments: {str(e)}")
            status.update(label="Comment download failed!", state="error")

# ===== DYNAMIC IMPORT (SIMPLIFIED & ROBUST) =====
class ModuleImporter:
    """Simplified and robust module importer"""
    
    def __init__(self):
        self.loaded_modules = {}
        self.missing_modules = []
    
    def import_module(self, module_name: str, file_name: str) -> Optional[Any]:
        """
        Safely imports a module
        
        Args:
            module_name: Name of the module
            file_name: Filename of the module
            
        Returns:
            Imported module or None
        """
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        file_path = YouTubeAnalyzerConfig.UTILS_DIR / file_name
        
        try:
            if file_path.exists():
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.loaded_modules[module_name] = module
                return module
            else:
                self.missing_modules.append(module_name)
                return None
        except Exception as e:
            st.warning(f"Error importing {module_name}: {e}")
            self.missing_modules.append(module_name)
            return None
    
    def import_all_modules(self) -> Dict[str, Any]:
        """Imports all required modules"""
        results = {}
        
        # YouTube Downloader
        downloader = self.import_module("downloader", YouTubeAnalyzerConfig.UTILS_MODULES["downloader"])
        results["downloader"] = downloader
        
        # Transcriber
        transcriber = self.import_module("transcriber", YouTubeAnalyzerConfig.UTILS_MODULES["transcriber"])
        results["transcriber"] = transcriber
        
        # Comment Saver (with fallback)
        comment_saver = self.import_module("comment_saver", YouTubeAnalyzerConfig.UTILS_MODULES["comment_saver"])
        if not comment_saver:
            comment_saver = self.import_module("comment_saver", YouTubeAnalyzerConfig.UTILS_MODULES["comment_saver_fallback"])
        results["comment_saver"] = comment_saver
        
        return results
    
    def get_missing_modules(self) -> List[str]:
        """Returns list of missing modules"""
        return self.missing_modules

# ===== HELPER FUNCTIONS =====
def get_function_from_module(module: Any, function_name: str) -> Optional[callable]:
    """
    Safely extracts a function from a module
    
    Args:
        module: Imported module
        function_name: Name of the function
        
    Returns:
        Function or None
    """
    if module and hasattr(module, function_name):
        return getattr(module, function_name)
    return None

def check_whisper_installation() -> bool:
    """Checks if Whisper is installed"""
    try:
        import whisper
        return True
    except ImportError:
        return False

def display_missing_modules_warning(missing_modules: List[str]) -> None:
    """Shows warning for missing modules"""
    if missing_modules:
        module_names = {
            "downloader": "YouTube Downloader",
            "transcriber": "YouTube Transcriber", 
            "comment_saver": "YouTube Comment Saver"
        }
        
        readable_names = [module_names.get(m, m) for m in missing_modules]
        st.warning(f"The following modules could not be found: {', '.join(readable_names)}. Some features may be limited.")

# ===== STYLING =====
def apply_youtube_styles():
    """Applies YouTube-specific styles"""
    st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        h4 {
            color: #9834eb;
        }
        .card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .status-card {
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success-card {
            background-color: rgba(0, 180, 0, 0.1);
            border-left: 4px solid #00b400;
        }
        .warning-card {
            background-color: rgba(255, 165, 0, 0.1);
            border-left: 4px solid orange;
        }
        .error-card {
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 4px solid red;
        }
    </style>
    """, unsafe_allow_html=True)

# ===== TAB FUNCTIONS =====
def display_video_download_tab(modules: Dict[str, Any]) -> None:
    """Tab 1: Download Videos"""
    st.header("📥 Download Videos")
    
    st.markdown("""
    <div class="card">
        This function enables downloading YouTube videos as MP3 files.
        You can either search for videos with specific keywords or directly enter a YouTube URL.
    </div>
    """, unsafe_allow_html=True)
    
    downloader_module = modules.get("downloader")
    if not downloader_module:
        st.error("The YouTube Downloader module could not be found. This function is not available.")
        return
    
    # Extract functions from module
    search_and_download_videos = get_function_from_module(downloader_module, 'search_and_download_videos')
    search_and_download_lanz_bildung = get_function_from_module(downloader_module, 'search_and_download_lanz_bildung')
    download_video_by_url = get_function_from_module(downloader_module, 'download_video_by_url')
    
    # Cookie upload
    display_cookie_upload_section()
    
    # Download tabs
    download_tab1, download_tab2 = st.tabs(["Search by Topics", "Enter Video URL"])
    
    with download_tab1:
        display_search_download_section(search_and_download_videos, search_and_download_lanz_bildung)
    
    with download_tab2:
        display_url_download_section(download_video_by_url)
    
    # Display existing files
    display_existing_audio_files_enhanced()

def display_cookie_upload_section() -> None:
    """Cookie upload section"""
    st.subheader("Cookie File (Optional)")
    uploaded_cookie = st.file_uploader("Upload cookie file for YouTube (optional)", type="txt")
    
    if uploaded_cookie is not None:
        cookie_path = "cookies.txt"
        with open(cookie_path, "wb") as f:
            f.write(uploaded_cookie.getvalue())
        st.success(f"Cookie file saved as {cookie_path}")

def display_search_download_section(search_func: Optional[callable], lanz_func: Optional[callable]) -> None:
    """Search and download section"""
    st.subheader("Search for Videos")
    
    # Input fields
    search_query = st.text_input(
        "Search query:", 
        value=YouTubeAnalyzerConfig.DEFAULT_SEARCH_QUERY,
        help="Enter a search query for YouTube."
    )
    
    with st.expander("Adjust search settings", expanded=True):
        positive_keywords = st.text_area(
            "Positive keywords (one word per line):",
            value="\n".join(YouTubeAnalyzerConfig.DEFAULT_KEYWORDS),
            help="Videos must contain at least one of these words in the title."
        ).strip().split('\n')
        
        min_val, max_val, default_val, step_val = YouTubeAnalyzerConfig.MAX_RESULTS_RANGE
        max_results = st.slider(
            "Maximum number of search results:", 
            min_value=min_val, max_value=max_val, value=default_val, step=step_val
        )
    
    # Download button
    if st.button("🔎 Search and Download", use_container_width=True):
        execute_search_download(search_query, positive_keywords, max_results, search_func, lanz_func)

def execute_search_download(search_query: str, keywords: List[str], max_results: int, 
                          search_func: Optional[callable], lanz_func: Optional[callable]) -> None:
    """Executes search and download"""
    with st.status("Searching and downloading videos...", expanded=True) as status:
        st.write(f"Searching for videos with query: {search_query}")
        st.write(f"Keywords: {', '.join(keywords)}")
        
        try:
            downloaded_files = []
            
            if search_func:
                downloaded_files = search_func(
                    query=search_query,
                    output_dir=str(YouTubeAnalyzerConfig.AUDIO_DIR),
                    positive_keywords=keywords,
                    max_results=max_results
                )
            elif lanz_func and "markus lanz" in search_query.lower():
                downloaded_files = lanz_func(
                    output_dir=str(YouTubeAnalyzerConfig.AUDIO_DIR),
                    positive_keywords=keywords
                )
            else:
                st.error("No suitable download function found.")
                status.update(label="Download failed!", state="error")
                return
            
            if downloaded_files:
                st.success(f"{len(downloaded_files)} videos were successfully downloaded!")
                for file in downloaded_files:
                    st.write(f"- {os.path.basename(file)}")
            else:
                st.warning("No matching videos were found or downloaded.")
            
            status.update(label="Download completed!", state="complete")
            
        except Exception as e:
            st.error(f"Error downloading: {str(e)}")
            status.update(label="Download failed!", state="error")

def display_url_download_section(download_func: Optional[callable]) -> None:
    """URL download section"""
    st.subheader("Download video by URL")
    video_url = st.text_input("YouTube video URL:", help="Enter the complete URL of a YouTube video.")
    
    if st.button("📥 Download Video", use_container_width=True):
        if not video_url:
            st.warning("Please enter a YouTube URL.")
            return
        
        if not download_func:
            st.error("The function for downloading by URL is not available.")
            return
        
        execute_url_download(video_url, download_func)

def execute_url_download(video_url: str, download_func: callable) -> None:
    """Executes URL download"""
    with st.status("Downloading video...", expanded=True) as status:
        try:
            downloaded_file = download_func(
                url=video_url,
                output_dir=str(YouTubeAnalyzerConfig.AUDIO_DIR)
            )
            
            if downloaded_file:
                st.success(f"Video successfully downloaded: {os.path.basename(downloaded_file)}")
            else:
                st.warning("The video could not be downloaded.")
            
            status.update(label="Download completed!", state="complete")
            
        except Exception as e:
            st.error(f"Error downloading: {str(e)}")
            status.update(label="Download failed!", state="error")

def display_existing_audio_files_enhanced() -> None:
    """Enhanced display of existing audio files with video IDs"""
    st.subheader("Existing Audio Files")
    audio_files = list(YouTubeAnalyzerConfig.AUDIO_DIR.glob("*.mp3"))
    
    if audio_files:
        # Enhanced table with video IDs
        audio_data = []
        for f in audio_files:
            video_id = extract_video_id_from_filename(f.name)
            
            # Check if comments exist
            base_name = f.name.replace('.mp3', '')
            comment_file = YouTubeAnalyzerConfig.COMMENTS_DIR / f"{base_name}.csv"
            comments_status = "✅ Available" if comment_file.exists() else "⏳ Missing"
            
            audio_data.append({
                "Filename": f.name,
                "Video ID": video_id or "❌ Unknown",
                "Size (MB)": round(f.stat().st_size / (1024 * 1024), 2),
                "Date": pd.to_datetime(f.stat().st_mtime, unit='s').strftime('%Y-%m-%d %H:%M'),
                "Comments": comments_status
            })
        
        audio_df = pd.DataFrame(audio_data)
        st.dataframe(audio_df.sort_values("Date", ascending=False), use_container_width=True)
        
        # Audio player
        st.subheader("Play Audio")
        selected_audio = st.selectbox("Select an audio file to play:", options=[f.name for f in audio_files])
        audio_path = YouTubeAnalyzerConfig.AUDIO_DIR / selected_audio
        st.audio(str(audio_path), format="audio/mp3")
    else:
        st.info("No audio files available. Download videos first.")

def display_transcription_tab(modules: Dict[str, Any]) -> None:
    """Tab 2: Transcribe Audio"""
    st.header("🔊 Transcribe Audio")
    
    st.markdown("""
    <div class="card">
        This function transcribes MP3 files using the Whisper model and saves the transcripts as TXT and CSV.
        The transcripts are saved in the 'data/transcripts' folder.
        <br><br>
        <strong>Note:</strong> Transcription may take some time depending on the length of the audio file.
    </div>
    """, unsafe_allow_html=True)
    
    transcriber_module = modules.get("transcriber")
    if not transcriber_module:
        st.error("The Transcriber module could not be found. This function is not available.")
        return
    
    # Whisper check
    whisper_installed = check_whisper_installation()
    if not whisper_installed:
        st.warning("""
        The Whisper package is not installed. Install it with:
        ```
        pip install openai-whisper
        ```
        """)
        return
    
    # Extract functions
    transcribe_audio = get_function_from_module(transcriber_module, 'transcribe_audio')
    transcribe_all_audios = get_function_from_module(transcriber_module, 'transcribe_all_audios')
    
    audio_files = list(YouTubeAnalyzerConfig.AUDIO_DIR.glob("*.mp3"))
    
    if not audio_files:
        st.warning("No audio files found. Download videos first.")
        return
    
    # Single transcription
    display_single_transcription_section(audio_files, transcribe_audio)
    
    # Batch transcription
    display_batch_transcription_section(audio_files, transcribe_all_audios)
    
    # Show existing transcripts
    display_existing_transcripts()

def display_single_transcription_section(audio_files: List[Path], transcribe_func: Optional[callable]) -> None:
    """Single transcription section"""
    st.subheader("Transcribe single file")
    selected_audio = st.selectbox("Select audio file:", options=[f.name for f in audio_files])
    
    if st.button("🔊 Transcribe selected file", use_container_width=True):
        if not transcribe_func:
            st.error("The transcription function is not available.")
            return
        
        execute_single_transcription(selected_audio, transcribe_func)

def execute_single_transcription(selected_audio: str, transcribe_func: callable) -> None:
    """Executes single transcription"""
    with st.status("Transcription running... (This may take several minutes)", expanded=True) as status:
        audio_path = YouTubeAnalyzerConfig.AUDIO_DIR / selected_audio
        st.write(f"Transcribing: {selected_audio}")
        
        try:
            csv_path = transcribe_func(str(audio_path), str(YouTubeAnalyzerConfig.TRANSCRIPT_DIR))
            st.success(f"Transcription successful! Saved as: {os.path.basename(csv_path)}")
            
            # Transcript preview
            txt_path = os.path.splitext(csv_path)[0] + ".txt"
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
                
                st.subheader("Transcript Preview:")
                preview_text = transcript_text[:1000] + "..." if len(transcript_text) > 1000 else transcript_text
                st.text_area("Transcript Preview", value=preview_text, height=200)
            
            status.update(label="Transcription completed!", state="complete")
            
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")
            status.update(label="Transcription failed!", state="error")

def display_batch_transcription_section(audio_files: List[Path], transcribe_all_func: Optional[callable]) -> None:
    """Batch transcription section"""
    st.subheader("Transcribe all files")
    st.warning("⚠️ Warning: This can be very time-consuming, depending on the number and length of audio files.")
    
    if st.button("🔊 Transcribe all audio files", use_container_width=True):
        if not transcribe_all_func:
            st.error("The batch transcription function is not available.")
            return
        
        execute_batch_transcription(audio_files, transcribe_all_func)

def execute_batch_transcription(audio_files: List[Path], transcribe_all_func: callable) -> None:
    """Executes batch transcription"""
    with st.status("Batch transcription running...", expanded=True) as status:
        try:
            st.write(f"Transcribing {len(audio_files)} audio files...")
            transcribed_files = transcribe_all_func(
                str(YouTubeAnalyzerConfig.AUDIO_DIR), 
                str(YouTubeAnalyzerConfig.TRANSCRIPT_DIR)
            )
            st.success(f"{len(transcribed_files)} audio files were transcribed!")
            status.update(label="Batch transcription completed!", state="complete")
            
        except Exception as e:
            st.error(f"Error during batch transcription: {str(e)}")
            status.update(label="Batch transcription failed!", state="error")

def display_existing_transcripts() -> None:
    """Shows existing transcripts"""
    st.subheader("Existing Transcripts")
    transcript_files = list(YouTubeAnalyzerConfig.TRANSCRIPT_DIR.glob("*.txt"))
    
    if transcript_files:
        # Table
        transcript_df = pd.DataFrame({
            "Filename": [f.name for f in transcript_files],
            "Size (KB)": [round(f.stat().st_size / 1024, 2) for f in transcript_files],
            "Date": [pd.to_datetime(f.stat().st_mtime, unit='s').strftime('%Y-%m-%d %H:%M') for f in transcript_files]
        })
        st.dataframe(transcript_df.sort_values("Date", ascending=False), use_container_width=True)
        
        # Transcript viewer
        display_transcript_viewer(transcript_files)
    else:
        st.info("No transcripts available. Transcribe audio files first.")

def display_transcript_viewer(transcript_files: List[Path]) -> None:
    """Transcript viewer"""
    st.subheader("View transcript")
    selected_transcript = st.selectbox("Select a transcript to view:", options=[f.name for f in transcript_files])
    
    try:
        with open(YouTubeAnalyzerConfig.TRANSCRIPT_DIR / selected_transcript, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        
        st.markdown("### Transcript Content")
        st.text_area("Transcript", value=transcript_content, height=300)
        
        # Download button
        st.download_button(
            label="Download transcript",
            data=transcript_content,
            file_name=selected_transcript,
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"Error reading transcript: {str(e)}")

def extract_video_id_from_url(url):
    """
    Extracts video ID from YouTube URL
    
    Args:
        url: YouTube URL
        
    Returns:
        str: Video ID or None
    """
    import re
    
    # Various YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def download_comments_from_url(url, comment_saver_module):
    """
    Downloads comments for a YouTube URL
    
    Args:
        url: YouTube URL
        comment_saver_module: Comment saver module
        
    Returns:
        tuple: (success, message, file_path)
    """
    # Extract video ID
    video_id = extract_video_id_from_url(url)
    if not video_id:
        return False, "❌ No valid YouTube URL or video ID could not be extracted.", None
    
    st.info(f"📺 Extracted video ID: {video_id}")
    
    # Get video metadata (for correct filename)
    try:
        import subprocess
        import sys
        import json
        from datetime import datetime
        
        # Get metadata with yt-dlp
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--dump-json",
            "--no-download",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            metadata = json.loads(result.stdout)
            video_title = metadata.get('title', 'Unknown_Title')
            upload_date = metadata.get('upload_date', '')
            
            st.success(f"✅ Video found: {video_title}")
            
            # Format date
            if upload_date and len(upload_date) == 8:  # YYYYMMDD
                formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            else:
                formatted_date = datetime.now().strftime('%Y-%m-%d')
            
        else:
            st.warning("⚠️ Could not load video metadata - using fallback")
            video_title = "Unknown_Title"
            formatted_date = datetime.now().strftime('%Y-%m-%d')
            
    except Exception as e:
        st.warning(f"⚠️ Metadata error: {e} - using fallback")
        video_title = "Unknown_Title"
        formatted_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create safe filename
    def sanitize_title(title):
        import re
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        sanitized = re.sub(r'[^\w\s\-_.,()[\]{}]', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_. ')
        return sanitized[:100] if sanitized else "Unknown_Title"
    
    clean_title = sanitize_title(video_title)
    
    # Create correct CSV filename
    csv_filename = f"{formatted_date}_{video_id}_{clean_title}.csv"
    output_file = YouTubeAnalyzerConfig.COMMENTS_DIR / csv_filename
    
    st.info(f"📁 Target file: {csv_filename}")
    
    # Check if already exists
    if output_file.exists() and output_file.stat().st_size > 0:
        return True, f"✅ Comments already available: {csv_filename}", str(output_file)
    
    # Download comments
    try:
        # Temporary JSON file
        temp_output = YouTubeAnalyzerConfig.COMMENTS_DIR / f"temp_{video_id}.json"
        
        cmd = [
            "youtube-comment-downloader",
            "--youtubeid", video_id,
            "--output", str(temp_output),
            "--limit", "1000"
        ]
        
        st.info(f"🔧 Downloading comments...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if temp_output.exists() and temp_output.stat().st_size > 0:
            # Convert JSON to CSV
            comments_data = []
            
            with open(temp_output, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            comment = json.loads(line)
                            
                            comment_data = {
                                'comment_id': comment.get('cid', ''),
                                'author': comment.get('author', ''),
                                'time': comment.get('time_parsed', comment.get('time', '')),
                                'likes_count': comment.get('votes', 0),
                                'text': comment.get('text', ''),
                                'parent_id': comment.get('parent', ''),
                                'video_id': video_id
                            }
                            comments_data.append(comment_data)
                            
                        except json.JSONDecodeError:
                            continue
            
            if comments_data:
                # Create DataFrame and save
                import pandas as pd
                df = pd.DataFrame(comments_data)
                
                # Data cleaning
                df['likes_count'] = pd.to_numeric(df['likes_count'], errors='coerce').fillna(0).astype(int)
                df = df[df['text'].str.strip() != ''].copy()
                df['parent_id'] = df['parent_id'].fillna('').astype(str)
                df = df.sort_values('likes_count', ascending=False)
                
                # Save
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                
                # Delete temporary file
                temp_output.unlink()
                
                return True, f"✅ {len(df)} comments successfully downloaded!", str(output_file)
            else:
                return False, "⚠️ No valid comments found.", None
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            return False, f"❌ Comment download failed: {error_msg}", None
            
    except subprocess.TimeoutExpired:
        return False, "⏰ Timeout while downloading comments.", None
    except Exception as e:
        return False, f"❌ Error downloading: {str(e)}", None

def display_comments_tab(modules: Dict[str, Any]) -> None:
    """Tab 3: Save Comments - ENHANCED VERSION with URL input"""
    st.header("💬 Save Comments")
    
    st.markdown("""
    <div class="card">
        This function downloads YouTube comments and saves them as CSV files in the 'data/comments' folder.
        The comments contain additional information like author, timestamp, likes and more.
        <br><br>
        <strong>Note:</strong> This requires the 'youtube-comment-downloader' tool.
        <br><br>
        <strong>Installation:</strong> Install youtube-comment-downloader with:
        <code>pip install youtube-comment-downloader</code>
    </div>
    """, unsafe_allow_html=True)
    
    comment_saver_module = modules.get("comment_saver")
    if not comment_saver_module:
        st.error("The Comment Saver module could not be found. This function is not available.")
        return
    
    # ===== TAB SYSTEM =====
    tab1, tab2 = st.tabs(["📁 From MP3 Files", "🔗 From YouTube URL"])
    
    # ===== TAB 1: FROM MP3 FILES (EXISTING FUNCTIONALITY) =====
    with tab1:
        st.subheader("Comments from existing MP3 files")
        st.markdown("This option extracts video IDs from your downloaded MP3 files and downloads the corresponding comments.")
        
        display_comment_download_section_enhanced(comment_saver_module)
    
    # ===== TAB 2: FROM YOUTUBE URL (NEW FUNCTIONALITY) =====
    with tab2:
        st.subheader("Comments from YouTube URL")
        st.markdown("Simply enter a YouTube URL to download the comments - even without having the video as MP3 first!")
        
        # URL input
        youtube_url = st.text_input(
            "Enter YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Enter the complete YouTube URL"
        )
        
        # Examples
        with st.expander("📋 Supported URL formats", expanded=False):
            st.markdown("""
            **All these formats work:**
            - `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
            - `https://youtu.be/dQw4w9WgXcQ`
            - `https://www.youtube.com/embed/dQw4w9WgXcQ`
            - `https://youtube.com/watch?v=dQw4w9WgXcQ&t=30s`
            """)
        
        # URL validation and preview
        if youtube_url:
            video_id = extract_video_id_from_url(youtube_url)
            if video_id:
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ **Valid URL detected**")
                    st.info(f"📺 **Video ID:** {video_id}")
                with col2:
                    # Check if comments already exist
                    existing_files = list(YouTubeAnalyzerConfig.COMMENTS_DIR.glob(f"*{video_id}*.csv"))
                    if existing_files:
                        st.success("✅ **Comments already available**")
                        st.write(f"📁 {existing_files[0].name}")
                    else:
                        st.warning("⏳ **Comments not yet downloaded**")
            else:
                st.error("❌ **Invalid YouTube URL**")
                st.write("Please use a valid YouTube URL.")
        
        # Download button
        if st.button("💬 Download comments from URL", use_container_width=True, disabled=not youtube_url):
            if not youtube_url:
                st.error("Please enter a YouTube URL.")
            elif not extract_video_id_from_url(youtube_url):
                st.error("Invalid YouTube URL. Please check the format.")
            else:
                with st.status("Downloading comments...", expanded=True) as status:
                    success, message, filepath = download_comments_from_url(youtube_url, comment_saver_module)
                    
                    if success:
                        st.success(message)
                        if filepath:
                            st.write(f"📁 File created: {os.path.basename(filepath)}")
                        status.update(label="✅ Comment download successful!", state="complete")
                    else:
                        st.error(message)
                        status.update(label="❌ Comment download failed!", state="error")
    
    # ===== DISPLAY EXISTING COMMENTS =====
    st.divider()
    display_existing_comments(comment_saver_module)

def display_comment_download_section_enhanced(comment_saver_module: Any) -> None:
    """Comment download section - ENHANCED VERSION with dropdown"""
    audio_files = list(YouTubeAnalyzerConfig.AUDIO_DIR.glob("*.mp3"))
    
    if not audio_files:
        st.warning("No audio files found. Download videos first.")
        return
    
    st.subheader("Download comments")
    st.markdown("""
    **How it works:**
    1. The app extracts YouTube video IDs from the filenames of MP3 files
    2. For each video ID, comments are downloaded with youtube-comment-downloader
    3. Comments are processed and saved as CSV with additional columns
    """)
    
    # ===== NEW SECTION: SELECT SINGLE FILE =====
    st.subheader("🎯 Select single file")
    
    # Dropdown for audio file selection
    audio_file_options = [f.name for f in audio_files]
    selected_audio_file = st.selectbox(
        "Select an audio file for comment download:",
        options=audio_file_options,
        help="Choose the MP3 file for which you want to download comments.",
        key="single_audio_file_selector"
    )
    
    # Info about selected file
    if selected_audio_file:
        video_id = extract_video_id_from_filename(selected_audio_file)
        if video_id:
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📺 **Video ID:** {video_id}")
            with col2:
                # Check if comments already exist
                base_name = selected_audio_file.replace('.mp3', '')
                comment_file = YouTubeAnalyzerConfig.COMMENTS_DIR / f"{base_name}.csv"
                if comment_file.exists():
                    st.success("✅ **Comments already available**")
                else:
                    st.warning("⏳ **Comments not yet downloaded**")
        else:
            st.error("❌ Could not extract video ID")
    
    # Download button for single file
    if st.button("💬 Download comments for selected file", use_container_width=True):
        if not selected_audio_file:
            st.error("Please select an audio file.")
            return
        
        video_id = extract_video_id_from_filename(selected_audio_file)
        if not video_id:
            st.error("Could not extract video ID from filename.")
            return
        
        download_comments_for_single_video(video_id, selected_audio_file, comment_saver_module)
    
    # ===== DIVIDER =====
    st.divider()
    
    # ===== EXISTING SECTION: ALL FILES =====
    st.subheader("🔄 All files at once")
    st.markdown("**For advanced users:** Downloads comments for all found MP3 files.")
    
    save_all_comments = get_function_from_module(comment_saver_module, 'save_all_comments')
    
    if st.button("💬 Download comments for all videos", use_container_width=True):
        if not save_all_comments:
            st.error("The function for saving comments is not available.")
            return
        
        execute_comment_download(audio_files, save_all_comments)

def execute_comment_download(audio_files: List[Path], save_all_comments: callable) -> None:
    """Executes comment download"""
    with st.status("Downloading comments...", expanded=True) as status:
        try:
            st.write(f"Searching for comments for {len(audio_files)} video(s)...")
            
            created_files = save_all_comments(
                str(YouTubeAnalyzerConfig.AUDIO_DIR), 
                str(YouTubeAnalyzerConfig.COMMENTS_DIR)
            )
            
            if created_files:
                st.success(f"{len(created_files)} comment files were successfully created or were already available!")
                for file in created_files:
                    st.write(f"- {os.path.basename(file)}")
            else:
                st.warning("No comments were found or downloaded.")
            
            status.update(label="Comment download completed!", state="complete")
            
        except Exception as e:
            st.error(f"Error downloading comments: {str(e)}")
            status.update(label="Comment download failed!", state="error")

def display_existing_comments(comment_saver_module: Any) -> None:
    """Shows existing comments"""
    st.subheader("Existing Comment Files")
    comment_files = list(YouTubeAnalyzerConfig.COMMENTS_DIR.glob("*.csv"))
    
    if comment_files:
        # Table
        comment_df = pd.DataFrame({
            "Filename": [f.name for f in comment_files],
            "Size (KB)": [round(f.stat().st_size / 1024, 2) for f in comment_files],
            "Date": [pd.to_datetime(f.stat().st_mtime, unit='s').strftime('%Y-%m-%d %H:%M') for f in comment_files]
        })
        st.dataframe(comment_df.sort_values("Date", ascending=False), use_container_width=True)
        
        # Comment viewer and analysis
        display_comment_viewer_and_analysis_robust(comment_files, comment_saver_module)
    else:
        st.info("No comment files available. Download comments first.")

def display_comment_viewer_and_analysis_robust(comment_files: List[Path], comment_saver_module: Any) -> None:
    """Robust comment viewer and analysis - REPAIRED VERSION"""
    st.subheader("Comment Preview and Analysis")
    selected_comment_file = st.selectbox("Select a comment file:", options=[f.name for f in comment_files])
    
    if not selected_comment_file:
        return
    
    csv_file_path = str(YouTubeAnalyzerConfig.COMMENTS_DIR / selected_comment_file)
    
    # USE ROBUST CSV READING FUNCTION
    with st.spinner("Loading comments with robust parser..."):
        df = read_youtube_comments_csv_robust(csv_file_path)
    
    if df is None or df.empty:
        st.error("❌ Could not load comment file or file is empty.")
        return
    
    # Successfully loaded - normal display
    st.success(f"✅ Comments successfully loaded: **{len(df)} comments**")
    
    # Select columns for display
    available_columns = df.columns.tolist()
    display_columns = []
    
    # Preferred columns in order
    preferred_columns = ['author', 'time', 'likes_count', 'text', 'comment_id']
    
    for col in preferred_columns:
        if col in available_columns:
            display_columns.append(col)
    
    # Add remaining columns
    for col in available_columns:
        if col not in display_columns:
            display_columns.append(col)
    
    # Display comments
    st.markdown("### 📋 Comment Data")
    if display_columns:
        display_df = df[display_columns].head(50)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.dataframe(df.head(50), use_container_width=True)
    
    # Extended analysis
    display_comment_analysis_robust(df)
    
    # Download button
    try:
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_buffer.seek(0)
        
        st.download_button(
            label="📥 Download cleaned comments as CSV",
            data=csv_buffer,
            file_name=f"cleaned_{selected_comment_file}",
            mime="text/csv"
        )
    except Exception as e:
        st.warning(f"⚠️ Download button could not be created: {e}")

def display_comment_analysis_robust(df: pd.DataFrame) -> None:
    """Robust comment analysis"""
    st.subheader("📊 Comment Analysis")
    
    try:
        # Basic statistics directly from DataFrame
        total_comments = len(df)
        
        # Calculate statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Comments", total_comments)
            
            if 'text' in df.columns:
                avg_length = df['text'].str.len().mean()
                st.metric("Average Length", f"{int(avg_length)} characters" if not pd.isna(avg_length) else "Unknown")
        
        with col2:
            if 'likes_count' in df.columns:
                total_likes = df['likes_count'].sum()
                avg_likes = df['likes_count'].mean()
                st.metric("Total Likes", int(total_likes))
                st.metric("Average Likes", f"{avg_likes:.1f}")
        
        with col3:
            if 'author' in df.columns:
                unique_authors = df['author'].nunique()
                st.metric("Unique Authors", unique_authors)
        
        # Top commenters
        if 'author' in df.columns:
            st.subheader("👥 Top Commenters")
            top_commenters = df['author'].value_counts().head(5)
            st.dataframe(top_commenters.reset_index().rename(columns={'author': 'Number of Comments', 'count': 'Count'}))
        
        # Most liked comment
        if 'likes_count' in df.columns and df['likes_count'].max() > 0:
            st.subheader("🏆 Most Liked Comment")
            most_liked_idx = df['likes_count'].idxmax()
            most_liked = df.loc[most_liked_idx]
            
            st.markdown(f"**Author:** {most_liked.get('author', 'Unknown')}")
            st.markdown(f"**Likes:** {most_liked.get('likes_count', 0)}")
            if 'text' in df.columns:
                st.text_area("Comment Text", value=str(most_liked.get('text', '')), height=100, key="most_liked_comment")
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        st.info("ℹ️ Showing available columns for debug:")
        st.write("Available columns:", df.columns.tolist())
        st.write("DataFrame shape:", df.shape)

# ===== MAIN APPLICATION =====
def main():
    """Main function of the YouTube Analyzer page"""
    
    # Apply styles
    apply_youtube_styles()
    
    # Header
    st.title("🎬 YouTube Tools")
    st.markdown("""
    These tools enable downloading, transcribing, and saving YouTube comments.
    Select one of the available functions below.
    """)
    
    # Create directories
    YouTubeAnalyzerConfig.ensure_directories()
    
    # Import modules
    with st.spinner("Loading YouTube modules..."):
        importer = ModuleImporter()
        modules = importer.import_all_modules()
        missing_modules = importer.get_missing_modules()
    
    # Warning for missing modules
    display_missing_modules_warning(missing_modules)
    
    # Tab interface
    tab1, tab2, tab3 = st.tabs([
        "📥 Download Videos", 
        "🔊 Transcribe Audio", 
        "💬 Save Comments"
    ])
    
    with tab1:
        display_video_download_tab(modules)
    
    with tab2:
        display_transcription_tab(modules)
    
    with tab3:
        display_comments_tab(modules)
    
    # Footer
    display_standard_footer()

# ===== EXECUTION =====
if __name__ == "__main__":
    main()
else:
    main()