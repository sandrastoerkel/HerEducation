"""
Modernisiertes Style Management System für HerEducation
Enterprise-Level CSS-Verwaltung mit Theme-System und modularen Komponenten

Autor: Sandra Störkel - HerEducation
Version: 2.0 - Modernisiert mit bewährten Patterns
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Tuple
from enum import Enum
import logging
from abc import ABC, abstractmethod

# ===== KONSTANTEN =====
class StyleConstants:
    """Zentrale Style-Konstanten"""
    
    # Container & Layout
    MAX_WIDTH = 1200
    DEFAULT_BORDER_RADIUS = 8
    SMALL_BORDER_RADIUS = 5
    CARD_BORDER_RADIUS = 8
    
    # Spacing (in rem/px)
    SPACING_TINY = 0.25   # 4px
    SPACING_SMALL = 0.5   # 8px
    SPACING_MEDIUM = 1.0  # 16px
    SPACING_LARGE = 1.5   # 24px
    SPACING_XLARGE = 2.0  # 32px
    
    # Font Sizes (in rem)
    FONT_SIZE_SMALL = 0.875   # 14px
    FONT_SIZE_NORMAL = 1.0    # 16px
    FONT_SIZE_LARGE = 1.25    # 20px
    FONT_SIZE_XLARGE = 1.5    # 24px
    
    # Box Shadow
    SHADOW_LIGHT = "0 2px 5px rgba(0,0,0,0.1)"
    SHADOW_MEDIUM = "2px 2px 5px rgba(0,0,0,0.1)"
    SHADOW_STRONG = "0 4px 10px rgba(0,0,0,0.15)"
    
    # Element Sizes
    RANK_CIRCLE_SIZE = 40
    SECTION_CIRCLE_SIZE = 28
    LEGEND_COLOR_SIZE = 20
    STATUS_BAR_HEIGHT = 24

# ===== FARBSYSTEM =====
@dataclass
class ColorPalette:
    """Strukturierte Farbpalette"""
    
    # Primäre Farben
    primary_blue: str = "#1E3A8A"
    primary_blue_light: str = "#2563EB"
    accent_pink: str = "#FF69B4"  # hotpink standardisiert
    
    # Grayscale
    white: str = "#FFFFFF"
    light_gray: str = "#F5F5F5"
    medium_gray: str = "#F3F4F6"
    border_gray: str = "#E5E7EB"
    text_gray: str = "#4B5563"
    dark_gray: str = "#6B7280"
    
    # Status-Farben
    success_green: str = "#50C878"  # rgba(80, 200, 120, 1.0)
    warning_orange: str = "#FFA500"  # rgba(255, 165, 0, 1.0)
    danger_red: str = "#C80000"     # rgba(200, 0, 0, 1.0)
    
    # Transparente Varianten
    success_light: str = "rgba(80, 200, 120, 0.1)"
    warning_light: str = "rgba(255, 165, 0, 0.1)"
    danger_light: str = "rgba(200, 0, 0, 0.1)"
    
    # Status Bar Farben (semi-transparent)
    success_bar: str = "rgba(80, 200, 120, 0.8)"
    warning_bar: str = "rgba(255, 165, 0, 0.8)"
    danger_bar: str = "rgba(200, 0, 0, 0.8)"
    
    def get_gradient(self, color1: str, color2: str, direction: str = "90deg") -> str:
        """Erstellt CSS-Gradient"""
        return f"linear-gradient({direction}, {color1} 0%, {color2} 100%)"
    
    def get_rgba(self, hex_color: str, alpha: float) -> str:
        """Konvertiert Hex zu RGBA"""
        # Einfache Hex zu RGB Konvertierung
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        return hex_color

# ===== THEMES =====
class ThemeType(Enum):
    """Verfügbare Theme-Typen"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    COLORBLIND_FRIENDLY = "colorblind_friendly"

@dataclass
class Theme:
    """Theme-Definition"""
    name: str
    colors: ColorPalette
    description: str = ""
    
    def get_css_variables(self) -> str:
        """Generiert CSS Custom Properties für das Theme"""
        return f"""
        :root {{
            --primary-blue: {self.colors.primary_blue};
            --primary-blue-light: {self.colors.primary_blue_light};
            --accent-pink: {self.colors.accent_pink};
            --white: {self.colors.white};
            --light-gray: {self.colors.light_gray};
            --medium-gray: {self.colors.medium_gray};
            --border-gray: {self.colors.border_gray};
            --text-gray: {self.colors.text_gray};
            --success-green: {self.colors.success_green};
            --warning-orange: {self.colors.warning_orange};
            --danger-red: {self.colors.danger_red};
        }}
        """

class ThemeFactory:
    """Factory für verschiedene Themes"""
    
    @staticmethod
    def create_light_theme() -> Theme:
        """Standard Light Theme"""
        return Theme(
            name="HerEducation Light",
            colors=ColorPalette(),
            description="Standard helles Theme mit blauen Akzenten"
        )
    
    @staticmethod
    def create_dark_theme() -> Theme:
        """Dark Theme"""
        colors = ColorPalette(
            primary_blue="#3B82F6",
            primary_blue_light="#60A5FA",
            light_gray="#1F2937",
            medium_gray="#374151",
            border_gray="#4B5563",
            text_gray="#D1D5DB",
            white="#111827"
        )
        return Theme(
            name="HerEducation Dark",
            colors=colors,
            description="Dunkles Theme für bessere Lesbarkeit bei wenig Licht"
        )
    
    @staticmethod
    def create_high_contrast_theme() -> Theme:
        """High Contrast Theme für Barrierefreiheit"""
        colors = ColorPalette(
            primary_blue="#000080",
            primary_blue_light="#0000CD",
            success_green="#008000",
            danger_red="#800000",
            text_gray="#000000",
            border_gray="#000000"
        )
        return Theme(
            name="High Contrast",
            colors=colors,
            description="Hochkontrast-Theme für bessere Zugänglichkeit"
        )

# ===== STYLE KOMPONENTEN =====
class StyleComponent(ABC):
    """Abstract Base Class für Style-Komponenten"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
        self.colors = theme.colors
    
    @abstractmethod
    def generate_css(self) -> str:
        """Generiert CSS für diese Komponente"""
        pass

class BaseLayoutStyles(StyleComponent):
    """Grundlegende Layout-Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .main {{
            background-color: {self.colors.light_gray};
        }}
        .stApp {{
            max-width: {StyleConstants.MAX_WIDTH}px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: {self.colors.primary_blue};
        }}
        """

class CardStyles(StyleComponent):
    """Card-basierte UI-Komponenten"""
    
    def generate_css(self) -> str:
        return f"""
        .metric-card {{
            background-color: {self.colors.white};
            border-radius: {StyleConstants.SMALL_BORDER_RADIUS}px;
            padding: {StyleConstants.SPACING_MEDIUM}rem;
            box-shadow: {StyleConstants.SHADOW_MEDIUM};
        }}
        
        .indicator-section {{
            border: 1px solid {self.colors.border_gray};
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px;
            padding: {StyleConstants.SPACING_LARGE}rem;
            margin-bottom: {StyleConstants.SPACING_LARGE}rem;
            background-color: {self.colors.white};
        }}
        
        .timeline-container {{
            margin-top: {StyleConstants.SPACING_LARGE}rem;
            padding: {StyleConstants.SPACING_LARGE}rem;
            background-color: {self.colors.white};
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px;
            box-shadow: {StyleConstants.SHADOW_LIGHT};
        }}
        
        .country-rank-card {{
            background-color: {self.colors.white};
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px;
            padding: {StyleConstants.SPACING_MEDIUM}rem;
            margin-bottom: {StyleConstants.SPACING_MEDIUM}rem;
            box-shadow: {StyleConstants.SHADOW_LIGHT};
            display: flex;
            align-items: center;
        }}
        
        .development-card {{
            border-left: 4px solid {self.colors.primary_blue};
            padding: {StyleConstants.SPACING_SMALL}rem {StyleConstants.SPACING_MEDIUM}rem;
            margin: {StyleConstants.SPACING_MEDIUM}rem 0;
            background-color: #f8f9fa;
            border-radius: 0 {StyleConstants.SMALL_BORDER_RADIUS}px {StyleConstants.SMALL_BORDER_RADIUS}px 0;
        }}
        
        .development-card h4 {{
            margin: 0 0 {StyleConstants.SPACING_SMALL}rem 0;
            color: {self.colors.primary_blue};
        }}
        """

class IndicatorStyles(StyleComponent):
    """Indikator-spezifische Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .indicator-title {{
            color: {self.colors.accent_pink};
            font-size: {StyleConstants.FONT_SIZE_LARGE}rem;
            font-weight: 600;
            margin-bottom: {StyleConstants.SPACING_SMALL}rem;
        }}
        
        .indicator-subtitle {{
            color: {self.colors.text_gray};
            font-size: {StyleConstants.FONT_SIZE_NORMAL}rem;
            margin-bottom: {StyleConstants.SPACING_MEDIUM}rem;
        }}
        
        .indicator-description {{
            margin-bottom: {StyleConstants.SPACING_LARGE}rem;
        }}
        
        .indicator-filter-container {{
            background-color: {self.colors.white};
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px;
            padding: {StyleConstants.SPACING_MEDIUM}rem;
            margin-bottom: {StyleConstants.SPACING_LARGE}rem;
            box-shadow: {StyleConstants.SHADOW_LIGHT};
        }}
        """

class StatusBarStyles(StyleComponent):
    """Status-Bar und Progress-Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .status-bar-container {{
            margin: {StyleConstants.SPACING_MEDIUM}rem 0;
        }}
        
        .status-bar {{
            display: flex;
            width: 100%;
            height: {StyleConstants.STATUS_BAR_HEIGHT}px;
            border-radius: {StyleConstants.SMALL_BORDER_RADIUS}px;
            overflow: hidden;
            margin-bottom: {StyleConstants.SPACING_SMALL}rem;
        }}
        
        .yes-segment {{
            background-color: {self.colors.success_bar};
            display: flex;
            justify-content: center;
            align-items: center;
            color: {self.colors.white};
            min-width: 30px;
            font-weight: bold;
        }}
        
        .partially-segment {{
            background-color: {self.colors.warning_bar};
            display: flex;
            justify-content: center;
            align-items: center;
            color: {self.colors.white};
            min-width: 30px;
            font-weight: bold;
        }}
        
        .no-segment {{
            background-color: {self.colors.danger_bar};
            display: flex;
            justify-content: center;
            align-items: center;
            color: {self.colors.white};
            min-width: 30px;
            font-weight: bold;
        }}
        
        .progress-positive {{
            color: {self.colors.success_green};
            font-weight: bold;
        }}
        
        .progress-negative {{
            color: {self.colors.danger_red};
            font-weight: bold;
        }}
        
        .progress-neutral {{
            color: {self.colors.text_gray};
        }}
        """

class SectionStyles(StyleComponent):
    """Section-Header und Navigation-Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .section-header {{
            background-color: {self.colors.medium_gray};
            padding: {StyleConstants.SPACING_SMALL}rem {StyleConstants.SPACING_MEDIUM}rem;
            border-radius: {StyleConstants.SMALL_BORDER_RADIUS + 1}px;
            margin-bottom: {StyleConstants.SPACING_MEDIUM}rem;
            display: flex;
            align-items: center;
            cursor: pointer;
        }}
        
        .section-number {{
            background-color: {self.colors.dark_gray};
            color: {self.colors.white};
            border-radius: 50%;
            width: {StyleConstants.SECTION_CIRCLE_SIZE}px;
            height: {StyleConstants.SECTION_CIRCLE_SIZE}px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: {StyleConstants.SPACING_SMALL}rem;
        }}
        
        .section-title {{
            font-weight: 600;
            color: {self.colors.primary_blue};
        }}
        
        .development-category {{
            font-weight: bold;
            margin: {StyleConstants.SPACING_XLARGE}rem 0 {StyleConstants.SPACING_SMALL}rem 0;
            padding-bottom: {StyleConstants.SPACING_TINY}rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        """

class SidebarStyles(StyleComponent):
    """Sidebar und Filter-Styles"""
    
    def generate_css(self) -> str:
        gradient = self.colors.get_gradient(self.colors.primary_blue, self.colors.primary_blue_light)
        return f"""
        .sidebar-header {{
            color: {self.colors.white};
            background: {gradient};
            padding: {StyleConstants.SPACING_SMALL + 0.25}rem {StyleConstants.SPACING_MEDIUM}rem;
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px;
            margin-bottom: {StyleConstants.SPACING_LARGE}rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            box-shadow: {StyleConstants.SHADOW_LIGHT};
        }}
        
        .filter-section {{
            background-color: {self.colors.white};
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px;
            padding: {StyleConstants.SPACING_MEDIUM}rem;
            margin-bottom: {StyleConstants.SPACING_LARGE}rem;
            box-shadow: {StyleConstants.SHADOW_LIGHT};
            border-left: 3px solid {self.colors.primary_blue_light};
        }}
        
        .filter-label {{
            font-weight: bold;
            margin-bottom: {StyleConstants.SPACING_SMALL}rem;
            color: {self.colors.primary_blue};
            display: flex;
            align-items: center;
        }}
        """

class ScoreStyles(StyleComponent):
    """Score und Ranking-Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .rank-number {{
            font-size: {StyleConstants.FONT_SIZE_XLARGE}rem;
            font-weight: bold;
            width: {StyleConstants.RANK_CIRCLE_SIZE}px;
            height: {StyleConstants.RANK_CIRCLE_SIZE}px;
            line-height: {StyleConstants.RANK_CIRCLE_SIZE}px;
            text-align: center;
            color: {self.colors.white};
            background-color: {self.colors.primary_blue};
            border-radius: 50%;
            margin-right: {StyleConstants.SPACING_MEDIUM}rem;
        }}
        
        .country-name {{
            font-size: {StyleConstants.FONT_SIZE_LARGE}rem;
            font-weight: bold;
            color: {self.colors.primary_blue};
            flex-grow: 1;
        }}
        
        .score-positive {{
            font-size: {StyleConstants.FONT_SIZE_LARGE}rem;
            font-weight: bold;
            color: {self.colors.success_green};
            padding: {StyleConstants.SPACING_TINY}rem {StyleConstants.SPACING_SMALL}rem;
            border-radius: 4px;
            background-color: {self.colors.success_light};
        }}
        
        .score-negative {{
            font-size: {StyleConstants.FONT_SIZE_LARGE}rem;
            font-weight: bold;
            color: {self.colors.danger_red};
            padding: {StyleConstants.SPACING_TINY}rem {StyleConstants.SPACING_SMALL}rem;
            border-radius: 4px;
            background-color: {self.colors.danger_light};
        }}
        
        .country-detail-header {{
            background-color: {self.colors.medium_gray};
            padding: {StyleConstants.SPACING_SMALL}rem {StyleConstants.SPACING_MEDIUM}rem;
            border-radius: {StyleConstants.DEFAULT_BORDER_RADIUS}px {StyleConstants.DEFAULT_BORDER_RADIUS}px 0 0;
            border-bottom: 2px solid {self.colors.border_gray};
            margin-bottom: {StyleConstants.SPACING_MEDIUM}rem;
        }}
        """

class ChangeIndicatorStyles(StyleComponent):
    """Change-Indicator und Item-Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .change-item {{
            padding: {StyleConstants.SPACING_SMALL}rem {StyleConstants.SPACING_MEDIUM}rem;
            margin-bottom: {StyleConstants.SPACING_SMALL}rem;
            border-left: 3px solid;
            background-color: #f8f9fa;
        }}
        
        .change-item-positive {{
            border-left-color: {self.colors.success_green};
        }}
        
        .change-item-negative {{
            border-left-color: {self.colors.danger_red};
        }}
        """

class LegendStyles(StyleComponent):
    """Legend und Color-Indicator-Styles"""
    
    def generate_css(self) -> str:
        return f"""
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: {StyleConstants.SPACING_SMALL}rem;
        }}
        
        .legend-color {{
            width: {StyleConstants.LEGEND_COLOR_SIZE}px;
            height: {StyleConstants.LEGEND_COLOR_SIZE}px;
            border-radius: 4px;
            margin-right: {StyleConstants.SPACING_SMALL}rem;
        }}
        
        .yes-color {{
            background-color: {self.colors.success_bar};
        }}
        
        .no-color {{
            background-color: {self.colors.danger_bar};
        }}
        
        .partially-color {{
            background-color: {self.colors.warning_bar};
        }}
        """

# ===== STYLE MANAGER =====
@dataclass
class StyleConfig:
    """Konfiguration für Style-System"""
    theme_type: ThemeType = ThemeType.LIGHT
    custom_theme: Optional[Theme] = None
    enable_animations: bool = True
    enable_responsive: bool = True
    include_custom_properties: bool = True
    minify_css: bool = False

class StyleManager:
    """Zentraler Style Manager"""
    
    def __init__(self, config: StyleConfig = None):
        self.config = config or StyleConfig()
        self.logger = logging.getLogger(__name__)
        self._theme = self._initialize_theme()
        self._components = self._initialize_components()
    
    def _initialize_theme(self) -> Theme:
        """Initialisiert das Theme basierend auf Konfiguration"""
        if self.config.custom_theme:
            return self.config.custom_theme
        
        theme_map = {
            ThemeType.LIGHT: ThemeFactory.create_light_theme,
            ThemeType.DARK: ThemeFactory.create_dark_theme,
            ThemeType.HIGH_CONTRAST: ThemeFactory.create_high_contrast_theme,
            ThemeType.COLORBLIND_FRIENDLY: ThemeFactory.create_light_theme  # Fallback
        }
        
        factory_method = theme_map.get(self.config.theme_type, ThemeFactory.create_light_theme)
        theme = factory_method()
        self.logger.info(f"Theme initialisiert: {theme.name}")
        return theme
    
    def _initialize_components(self) -> List[StyleComponent]:
        """Initialisiert alle Style-Komponenten"""
        return [
            BaseLayoutStyles(self._theme),
            CardStyles(self._theme),
            IndicatorStyles(self._theme),
            StatusBarStyles(self._theme),
            SectionStyles(self._theme),
            SidebarStyles(self._theme),
            ScoreStyles(self._theme),
            ChangeIndicatorStyles(self._theme),
            LegendStyles(self._theme)
        ]
    
    def generate_complete_css(self) -> str:
        """Generiert vollständiges CSS für alle Komponenten"""
        css_parts = []
        
        # CSS Custom Properties (wenn aktiviert)
        if self.config.include_custom_properties:
            css_parts.append(self._theme.get_css_variables())
        
        # Komponenten-CSS
        for component in self._components:
            try:
                component_css = component.generate_css()
                css_parts.append(component_css)
            except Exception as e:
                self.logger.error(f"Fehler beim Generieren von CSS für {component.__class__.__name__}: {e}")
        
        complete_css = "\n".join(css_parts)
        
        # CSS Minifizierung (einfach)
        if self.config.minify_css:
            complete_css = self._minify_css(complete_css)
        
        return complete_css
    
    def _minify_css(self, css: str) -> str:
        """Einfache CSS-Minifizierung"""
        # Entferne überflüssige Leerzeichen und Zeilenwechsel
        import re
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r';\s*}', '}', css)
        css = re.sub(r'{\s*', '{', css)
        css = re.sub(r'}\s*', '}', css)
        return css.strip()
    
    def get_theme(self) -> Theme:
        """Gibt das aktuelle Theme zurück"""
        return self._theme
    
    def set_theme(self, theme: Union[Theme, ThemeType]) -> None:
        """Setzt ein neues Theme"""
        if isinstance(theme, ThemeType):
            self.config.theme_type = theme
            self._theme = self._initialize_theme()
        else:
            self._theme = theme
            self.config.custom_theme = theme
        
        # Komponenten neu initialisieren
        self._components = self._initialize_components()
        self.logger.info(f"Theme geändert zu: {self._theme.name}")
    
    def get_available_themes(self) -> List[Tuple[ThemeType, str]]:
        """Gibt verfügbare Themes zurück"""
        return [
            (ThemeType.LIGHT, "Standard Hell"),
            (ThemeType.DARK, "Dunkel"),
            (ThemeType.HIGH_CONTRAST, "Hoher Kontrast"),
            (ThemeType.COLORBLIND_FRIENDLY, "Farbenblind-freundlich")
        ]

# ===== STREAMLIT INTEGRATION =====
class StreamlitStyleApplicator:
    """Wendet Styles auf Streamlit an"""
    
    def __init__(self, style_manager: StyleManager):
        self.style_manager = style_manager
        self.logger = logging.getLogger(__name__)
    
    def apply_styles(self, unsafe_allow_html: bool = True) -> None:
        """Wendet alle Styles auf Streamlit an"""
        try:
            css = self.style_manager.generate_complete_css()
            
            # CSS in Streamlit einbetten
            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=unsafe_allow_html
            )
            
            self.logger.info("Styles erfolgreich angewendet")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden der Styles: {e}")
            
            # Fallback auf Standard-Styles
            if unsafe_allow_html:
                st.error("Fehler beim Laden der Styles. Verwende Standard-Design.")

# ===== BACKWARD-COMPATIBLE FUNCTIONS =====
def set_styles() -> None:
    """
    Backward-compatible Hauptfunktion
    Wendet Standard Light Theme an
    """
    config = StyleConfig(theme_type=ThemeType.LIGHT)
    manager = StyleManager(config)
    applicator = StreamlitStyleApplicator(manager)
    applicator.apply_styles()

# ===== ERWEITERTE API =====
def apply_theme(theme_type: ThemeType = ThemeType.LIGHT, config: StyleConfig = None) -> None:
    """
    Wendet ein spezifisches Theme an
    
    Args:
        theme_type: Gewünschtes Theme
        config: Optionale Style-Konfiguration
    """
    if config is None:
        config = StyleConfig(theme_type=theme_type)
    else:
        config.theme_type = theme_type
    
    manager = StyleManager(config)
    applicator = StreamlitStyleApplicator(manager)
    applicator.apply_styles()

def create_custom_theme(name: str, colors: ColorPalette, description: str = "") -> Theme:
    """
    Erstellt ein benutzerdefiniertes Theme
    
    Args:
        name: Name des Themes
        colors: Farbpalette
        description: Beschreibung des Themes
        
    Returns:
        Theme: Erstelltes Theme
    """
    return Theme(name=name, colors=colors, description=description)

def get_style_manager(config: StyleConfig = None) -> StyleManager:
    """
    Gibt einen Style Manager zurück für erweiterte Verwendung
    
    Args:
        config: Style-Konfiguration
        
    Returns:
        StyleManager: Konfigurierter Style Manager
    """
    return StyleManager(config)

def get_color_palette() -> ColorPalette:
    """Gibt die Standard-Farbpalette zurück"""
    return ColorPalette()

