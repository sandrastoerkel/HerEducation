"""
Geteilte UI-Komponenten für HerEducation App
Eliminiert Code-Duplikation zwischen Pages

Autor: Sandra Störkel  
"""

import streamlit as st
from pathlib import Path

class AppConfig:
    """Zentrale App-Konfiguration"""
    
    # Basis-Verzeichnisse
    BASE_DIR = Path(__file__).parent.parent  # HerEducation-Hauptverzeichnis
    IMAGES_DIR = BASE_DIR / "images"
    
    # Design-Konstanten
    PRIMARY_COLOR = "#FF6B98"
    AUTHOR_NAME = "Sandra Störkel"
    PROJECT_NAME = "HerEducation 2025"
    COPYRIGHT_YEAR = "2025"

class SharedStyles:
    """
    Zentrale CSS-Styles - Einmal definiert, überall verwendbar!
    
    VORHER: 60 Zeilen CSS in jeder Page wiederholt
    NACHHER: Einmal hier, import überall
    """
    
    @staticmethod
    def get_sidebar_copyright():
        """Copyright für Sidebar - verwendet in allen Pages"""
        return f"""
        <style>
        .sidebar-copyright-fixed-bottom {{
            position: fixed;
            bottom: 10px;
            left: 10px;
            right: 10px;
            max-width: 224px;
            padding: 15px 10px;
            margin: 10px 0;
            background: rgba(255, 107, 152, 0.1);
            border-left: 3px solid {AppConfig.PRIMARY_COLOR};
            border-radius: 8px;
            text-align: center;
            font-size: 0.75rem;
            z-index: 999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .sidebar-copyright-fixed-bottom .author {{
            color: {AppConfig.PRIMARY_COLOR};
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 3px;
        }}

        .sidebar-copyright-fixed-bottom .project {{
            color: #666666;
            font-size: 0.65rem;
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            padding-bottom: 80px;
        }}
        </style>

        <div class="sidebar-copyright-fixed-bottom">
            <div class="author">© {AppConfig.AUTHOR_NAME}</div>
            <div class="project">{AppConfig.PROJECT_NAME}</div>
        </div>
        """
    
    @staticmethod
    def get_page_styles():
        """Standard-Styles für Page-Inhalte"""
        return f"""
        <style>
        .title-text {{
            color: {AppConfig.PRIMARY_COLOR};
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }}
        .subtitle-text {{
            color: {AppConfig.PRIMARY_COLOR};
            font-size: 2.5rem;
            font-weight: bold;
            margin-top: 3rem;
            margin-bottom: 1rem;
        }}
        .normal-text {{
            font-size: 1.1rem;
            line-height: 1.5;
        }}
        .source {{
            font-size: 0.9rem;
            font-style: italic;
            color: #666666;
            margin-top: 1rem;
            border-left: 3px solid {AppConfig.PRIMARY_COLOR};
            padding-left: 10px;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }}
        .copyright-footer {{
            margin-top: 50px;
            padding: 20px 0;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666666;
            font-size: 0.9rem;
            background-color: #f8f9fa;
        }}
        .author-name {{
            color: {AppConfig.PRIMARY_COLOR};
            font-weight: 500;
        }}
        </style>
        """
    
    @staticmethod
    def get_main_footer():
        """Haupt-Footer für alle Pages"""
        return f"""
        <div class="copyright-footer">
            <p>© {AppConfig.COPYRIGHT_YEAR} <span class="author-name">{AppConfig.AUTHOR_NAME}</span> | HerEducation Platform</p>
            <p>Entwickelt für Bildungsgleichberechtigung weltweit</p>
        </div>
        """

class SharedComponents:
    """
    Wiederverwendbare UI-Komponenten
    """
    
    @staticmethod
    def setup_page_config(page_title: str, page_icon: str = "🌍"):
        """
        Standard Page-Konfiguration für alle Pages
        
        Args:
            page_title: Titel der Seite
            page_icon: Icon für die Seite (optional)
        """
        try:
            st.set_page_config(
                page_title=page_title,
                page_icon=page_icon,
                layout="wide"
            )
        except Exception as e:
            st.error(f"Fehler beim Setzen der Seitenkonfiguration: {str(e)}")
    
    @staticmethod
    def setup_sidebar():
        """Standard-Sidebar-Setup für alle Pages"""
        st.sidebar.write("")  # Aktiviert Sidebar
        st.sidebar.markdown(SharedStyles.get_sidebar_copyright(), unsafe_allow_html=True)
    
    @staticmethod
    def apply_page_styles():
        """Wendet Standard-Styles auf Page an"""
        st.markdown(SharedStyles.get_page_styles(), unsafe_allow_html=True)
    
    @staticmethod
    def display_footer():
        """Zeigt Standard-Footer an"""
        st.markdown(SharedStyles.get_main_footer(), unsafe_allow_html=True)
    
    @staticmethod
    def get_image_path(filename: str) -> Path:
        """
        Gibt den korrekten Pfad für Bilder zurück
        
        Args:
            filename: Name der Bilddatei
            
        Returns:
            Path zum Bild
        """
        return AppConfig.IMAGES_DIR / filename

# ===== CONVENIENCE FUNCTIONS =====
def setup_standard_page(page_title: str, page_icon: str = "🌍"):
    """
    All-in-One Setup für eine Standard-Page
    
    Ersetzt 4 Funktionsaufrufe durch einen!
    
    Args:
        page_title: Titel der Seite
        page_icon: Icon der Seite
    """
    SharedComponents.setup_page_config(page_title, page_icon)
    SharedComponents.setup_sidebar()
    SharedComponents.apply_page_styles()

def display_standard_footer():
    """Zeigt Standard-Footer an"""
    SharedComponents.display_footer()

def get_image(filename: str) -> str:
    """
    Shortcut für Bild-Pfad
    
    Args:
        filename: Bildname
        
    Returns:
        String-Pfad zum Bild
    """
    return str(SharedComponents.get_image_path(filename))