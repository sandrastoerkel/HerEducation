import streamlit as st
import nltk
from typing import Optional, Tuple


class DependencyConstants:
    """Constants for dependency checking"""
    
    # Package names
    BERTOPIC_PACKAGE = "bertopic"
    SENTENCE_TRANSFORMERS_PACKAGE = "sentence_transformers"
    NLTK_PACKAGE = "nltk"
    
    # NLTK corpus
    STOPWORDS_CORPUS = "stopwords"
    
    # Error messages
    BERTOPIC_WARNING = """
    BERTopic ist nicht installiert. Führe folgende Befehle aus, um es zu installieren:
    ```
    pip install bertopic sentence-transformers
    pip install hdbscan umap-learn nltk wordcloud
    ```
    Die Themen-Analyse wird deaktiviert, aber die Sentiment-Analyse funktioniert weiterhin.
    """


# Globale Variable für Backward Compatibility
BERTOPIC_AVAILABLE: bool = False


def _check_bertopic_availability() -> bool:
    """
    Check if BERTopic and related packages are available
    
    Returns:
        True if BERTopic is available and functional
    """
    # Nur pruefen, ob die Pakete installiert sind – NICHT importieren.
    # Der Import von bertopic/sentence_transformers laedt torch, umap und numba und
    # kostete bei jedem Seitenaufruf Zeit und Arbeitsspeicher. Der echte Import
    # passiert erst in models/model_loader*.py, wenn eine Live-Analyse startet.
    from importlib.util import find_spec
    try:
        return find_spec("bertopic") is not None and find_spec("sentence_transformers") is not None
    except (ImportError, ValueError):
        return False


def _ensure_nltk_stopwords() -> bool:
    """
    Ensure NLTK stopwords are available, download if necessary
    
    Returns:
        True if stopwords are available
    """
    try:
        # Check if stopwords are already available
        nltk.data.find(f'corpora/{DependencyConstants.STOPWORDS_CORPUS}')
        return True
    except LookupError:
        # Download stopwords if not found
        try:
            nltk.download(DependencyConstants.STOPWORDS_CORPUS, quiet=True)
            from nltk.corpus import stopwords
            return True
        except Exception:
            return False


def _initialize_dependencies() -> None:
    """Initialize and check all dependencies"""
    global BERTOPIC_AVAILABLE
    
    # Check BERTopic availability
    BERTOPIC_AVAILABLE = _check_bertopic_availability()
    
    if not BERTOPIC_AVAILABLE:
        st.warning(DependencyConstants.BERTOPIC_WARNING)
    
    # Ensure NLTK stopwords are available
    _ensure_nltk_stopwords()


def is_bertopic_available() -> bool:
    """
    Public function to check BERTopic availability
    
    Returns:
        True if BERTopic is available for use
    """
    global BERTOPIC_AVAILABLE
    return BERTOPIC_AVAILABLE


def get_dependency_status() -> Tuple[bool, bool]:
    """
    Get status of major dependencies
    
    Returns:
        Tuple of (bertopic_available, nltk_available)
    """
    bertopic_status = _check_bertopic_availability()
    nltk_status = _ensure_nltk_stopwords()
    
    return bertopic_status, nltk_status


def display_dependency_info() -> None:
    """Display dependency information in Streamlit"""
    bertopic_status, nltk_status = get_dependency_status()
    
    st.subheader("📦 Dependency Status")
    
    # BERTopic status
    if bertopic_status:
        st.success("✅ BERTopic: Available")
    else:
        st.error("❌ BERTopic: Not available")
        st.markdown(DependencyConstants.BERTOPIC_WARNING)
    
    # NLTK status
    if nltk_status:
        st.success("✅ NLTK: Available")
    else:
        st.error("❌ NLTK: Error loading stopwords")


# Initialize dependencies on import (for backward compatibility)
_initialize_dependencies()