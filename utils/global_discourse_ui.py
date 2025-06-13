# =======================================================================================
# FILE: global_discourse_ui.py
# =======================================================================================

"""
🌍 GLOBAL DISCOURSE UI - User Interface Components
UI components for global discourse analysis
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from collections import defaultdict, Counter

# Local imports
from .global_discourse_models import AnalysisFile
from .global_discourse_country_detector import render_country_detection_debug

# =============================================================================
# UI COMPONENTS WITH COUNTRY DETECTION
# =============================================================================

def render_country_detection_status(analysis_files: List[AnalysisFile]) -> None:
    """Shows status of automatic country detection"""
    
    if not analysis_files:
        return
    
    st.subheader("🌍 Automatic Country Detection")
    
    # Group by detection status
    auto_detected = []
    needs_manual = []
    
    for file in analysis_files:
        if file.country == "Unknown":
            needs_manual.append(file)
        else:
            auto_detected.append(file)
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Automatically detected", len(auto_detected))
    
    with col2:
        st.metric("Manual required", len(needs_manual))
    
    with col3:
        unique_countries = len(set(f.country for f in auto_detected if f.country != "Unknown"))
        st.metric("Detected countries", unique_countries)
    
    # Show details
    if auto_detected:
        with st.expander("✅ Automatically detected countries", expanded=False):
            country_counts = {}
            for file in auto_detected:
                country_counts[file.country] = country_counts.get(file.country, 0) + 1
            
            for country, count in sorted(country_counts.items()):
                st.write(f"🌍 **{country}**: {count} analysis/analyses")
    
    if needs_manual:
        st.warning(f"⚠️ {len(needs_manual)} files require manual country assignment")
        
        with st.expander("🤔 Manual assignment required", expanded=True):
            for file in needs_manual:
                st.write(f"📁 `{file.filename}`")
                st.info("This file could not be automatically assigned to a country. Use the Country Detection Interface in the sidebar.")


def render_file_selection_interface(analysis_files: List[AnalysisFile]) -> List[str]:
    """Renders interface for file selection with Country Detection info"""
    st.subheader("📁 Available Country Analysis Files")
    
    if not analysis_files:
        st.warning("No Country Analysis files found!")
        st.info("""
        **How to create Country Analysis files:**
        1. Go to a comment analysis (German or English)
        2. Perform a complete analysis (incl. Topic Labeling)
        3. Click "🌍 Save for Country Analysis"
        4. Return to this page
        """)
        return []
    
    # Country Detection Status
    render_country_detection_status(analysis_files)
    
    # Group by country
    files_by_country = defaultdict(list)
    for file in analysis_files:
        files_by_country[file.country].append(file)
    
    # Show overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Available countries", len(files_by_country))
        st.metric("Total files", len(analysis_files))
    
    with col2:
        total_comments = sum(file.row_count or 0 for file in analysis_files)
        languages = len(set(file.language for file in analysis_files))
        st.metric("Total comments", f"{total_comments:,}")
        st.metric("Languages", languages)
    
    # File selection
    st.subheader("🎯 Select Analyses for Comparison")
    
    selected_files = []
    
    for country, country_files in files_by_country.items():
        # Skip unknown countries from selection
        if country == "Unknown":
            continue
            
        with st.expander(f"🌍 {country} ({len(country_files)} files)", expanded=True):
            
            for file in country_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    is_selected = st.checkbox(
                        f"{file.source_analysis or file.filename[:50]}",
                        key=f"file_{file.filename}",
                        value=True  # Select all by default
                    )
                    
                    if is_selected:
                        selected_files.append(file.filename)
                
                with col2:
                    if file.row_count:
                        st.write(f"📊 {file.row_count:,}")
                
                with col3:
                    if file.has_smart_labels:
                        st.write("🏷️ ✅")
                    else:
                        st.write("🏷️ ❌")
    
    if selected_files:
        st.success(f"✅ {len(selected_files)} files selected for comparison")
    else:
        st.warning("⚠️ No files selected")
    
    return selected_files


def setup_page():
    """Sets up the page"""
    st.set_page_config(
        page_title="Global Discourse Analysis",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🌍 Global Discourse Analysis")
    st.markdown("""
    **Enterprise Cross-Country Discourse Comparison with automatic country detection**
    
    This analysis enables comparison of comment discourses between different countries 
    based on previously performed analyses with Smart Topic Labels.
    
    🚀 **NEW:** Automatic country detection from filenames (50+ countries supported)
    """)


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'render_country_detection_status',
    'render_file_selection_interface',
    'setup_page'
]