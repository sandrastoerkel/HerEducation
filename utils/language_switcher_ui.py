"""
UI-Komponenten für das Sprachschalter-System
Enthält alle visuellen Elemente und Page-Setup-Funktionen
"""

import streamlit as st
from utils.language_switcher_config import init_language, get_text, t, LANGUAGES

def language_switcher():
    """
    Erstellt den Sprachschalter in der Sidebar
    
    Features:
    - Radio Buttons mit Flaggen-Emojis
    - Automatisches Session State Management
    - Sofortiger Sprachwechsel mit st.rerun()
    """
    with st.sidebar:
        st.markdown("---")
        
        # Sprachauswahl mit Radio Buttons
        selected_language = st.radio(
            get_text("language_select"),
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="language_selector"
        )
        
        # Update Session State wenn sich die Sprache ändert
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()

def setup_standard_page_with_language(page_name, icon, title_key=None):
    """
    Erweiterte Version von setup_standard_page mit Sprachunterstützung
    
    Args:
        page_name: Technischer Name der Seite
        icon: Emoji-Icon für die Seite
        title_key: Übersetzungsschlüssel für den Titel (optional)
    
    Features:
    - Automatische Sprach-Initialisierung
    - Sprachschalter in Sidebar
    - Copyright-Footer in Sidebar
    - Übersetzter Seitentitel
    """
    # Sprache initialisieren  
    init_language()
    
    # Page Config (falls noch nicht gesetzt)
    try:
        st.set_page_config(
            page_title=f"{page_name} | HerEducation",
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except:
        pass  # Config bereits gesetzt
    
    # Sprachschalter in Sidebar
    language_switcher()
    
    # Sidebar-Copyright (bestehender Stil beibehalten)
    display_sidebar_copyright()
    
    # Titel mit Übersetzung (falls title_key angegeben)
    if title_key:
        actual_title = t(title_key, page_name)
        st.title(f"{icon} {actual_title}")

def display_sidebar_copyright():
    """
    Zeigt das Copyright in der Sidebar an
    (Bestehender Stil aus shared_components.py)
    """
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

def display_language_info():
    """
    Zeigt Debug-Informationen zur aktuellen Sprache
    (Nützlich für Entwicklung und Debugging)
    """
    with st.expander("🔧 Language Switcher Debug Info", expanded=False):
        st.write(f"**{t('current_language', 'Aktuelle Sprache')}:** {st.session_state.language}")
        st.write(f"**{t('available_languages', 'Verfügbare Sprachen')}:** {list(LANGUAGES.keys())}")
        st.write(f"**{t('session_state_keys', 'Session State Keys')}:** {list(st.session_state.keys())}")

def create_language_aware_tabs(tab_config):
    """
    Erstellt Tabs mit sprachabhängigen Namen
    
    Args:
        tab_config: Dictionary mit Struktur:
        {
            "tab1": {"de": "Deutscher Name", "en": "English Name"},
            "tab2": {"de": "Zweiter Tab", "en": "Second Tab"}
        }
    
    Returns:
        Streamlit tabs object
        
    Example:
        tab_config = {
            "sentiment": {"de": "Sentiment-Analyse", "en": "Sentiment Analysis"},
            "topics": {"de": "Themen-Analyse", "en": "Topic Analysis"}
        }
        tabs = create_language_aware_tabs(tab_config)
    """
    # FIX: Konsistente Sprachverwendung mit Großbuchstaben
    current_lang = st.session_state.language  # "DE" oder "EN"
    
    tab_names = []
    for tab_key, translations in tab_config.items():
        if current_lang == "DE":
            tab_names.append(translations.get("de", tab_key))
        else:  # EN
            tab_names.append(translations.get("en", tab_key))
    
    return st.tabs(tab_names)

def language_aware_selectbox(label_key, options, key=None, help_key=None):
    """
    Erstellt eine Selectbox mit übersetztem Label
    
    Args:
        label_key: Übersetzungsschlüssel für das Label
        options: Liste der Optionen
        key: Streamlit key
        help_key: Übersetzungsschlüssel für Help-Text (optional)
    
    Returns:
        Selected option
    """
    label = get_text(label_key)
    help_text = get_text(help_key) if help_key else None
    
    return st.selectbox(
        label=label,
        options=options,
        key=key,
        help=help_text
    )

def language_aware_button(label_key, key=None, help_key=None, type="primary"):
    """
    Erstellt einen Button mit übersetztem Label
    
    Args:
        label_key: Übersetzungsschlüssel für das Label
        key: Streamlit key
        help_key: Übersetzungsschlüssel für Help-Text (optional)
        type: Button-Typ ("primary", "secondary")
    
    Returns:
        Button state (True/False)
    """
    label = get_text(label_key)
    help_text = get_text(help_key) if help_key else None
    
    return st.button(
        label=label,
        key=key,
        help=help_text,
        type=type
    )

def language_aware_file_uploader(label_key, type=None, help_key=None, key=None):
    """
    Erstellt einen File Uploader mit übersetztem Label
    
    Args:
        label_key: Übersetzungsschlüssel für das Label
        type: Erlaubte Dateitypen
        help_key: Übersetzungsschlüssel für Help-Text (optional)
        key: Streamlit key
    
    Returns:
        Uploaded file object
    """
    label = get_text(label_key)
    help_text = get_text(help_key) if help_key else None
    
    return st.file_uploader(
        label=label,
        type=type,
        help=help_text,
        key=key
    )

def display_main_footer():
    """
    Zeigt den Haupt-Footer mit Übersetzungen an
    (Für main.py und andere Hauptseiten)
    """
    st.markdown(f"""
    <div class="copyright-footer">
        <p>© 2025 <span class="author-name">Sandra Störkel</span> | <span class="app-title">{t('app_title')} Platform</span></p>
        <p>Entwickelt mit 💫 für eine bessere Bildungswelt | UNESCO & YouTube Social Analytics</p>
    </div>
    """, unsafe_allow_html=True)