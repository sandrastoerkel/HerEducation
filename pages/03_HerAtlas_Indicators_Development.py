"""
HerEducation - Indikatoren & Entwicklung
Modernisierte Version mit vollständiger Sprachunterstützung

Diese Page verwendet jetzt die neue modulare Visualisierungs-Struktur mit 
vollständiger Mehrsprachigkeit für alle Charts und UI-Elemente.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from typing import Dict, List

# Bestehende Utils-Imports (bleiben unverändert!)
from utils.styles import set_styles
from utils.data_loader import load_data
from utils.indicators import get_indicators_sections
from utils.progress_calculations import (
    calculate_progress, 
    calculate_change_score, 
    calculate_country_progress, 
    calculate_weighted_country_progress
)

# NEUE MODULARE VISUALISIERUNG - Mit vollständiger Sprachunterstützung
from utils.visualizations import (
    show_regional_distribution, 
    show_time_development,
    show_country_ranking
)

# Shared components für CSS-Duplikation
from utils.shared_components import display_standard_footer

# === SPRACHSYSTEM IMPORTIEREN ===
from utils.language_switcher_config import init_language, get_text, t
from utils.language_switcher_ui import language_switcher

# ===== KONFIGURATION =====
class IndicatorsConfig:
    """Konfiguration für die Indikatoren-Seite"""
    
    # Regionen-Definition (aus der originalen Datei übernommen)
    REGIONEN = {
        "Afrika": [
            "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroon", 
            "Central African Republic", "Chad", "Comoros", "Congo", "Côte d'Ivoire", "Democratic Republic of the Congo",
            "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", 
            "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", 
            "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", 
            "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone", 
            "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda", 
            "Zambia", "Zimbabwe"
        ],
        
        "Asien": [
            "Afghanistan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "China", "India", 
            "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", 
            "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", 
            "Oman", "Pakistan", "Palestine", "Philippines", "Qatar", "Saudi Arabia", "Singapore", 
            "South Korea", "Sri Lanka", "Syria", "Taiwan", "Tajikistan", "Thailand", "Timor-Leste", 
            "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"
        ],
        
        "Europa": [
            "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina", 
            "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", 
            "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", 
            "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", 
            "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", 
            "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom", "Vatican City"
        ],
        
        "Nordamerika": [
            "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica", "Cuba", 
            "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", 
            "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Saint Kitts and Nevis", 
            "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago", "United States"
        ],
        
        "Südamerika": [
            "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", 
            "Peru", "Suriname", "Uruguay", "Venezuela"
        ],
        
        "Ozeanien": [
            "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Zealand", 
            "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"
        ]
    }

def group_result(row: pd.Series) -> str:
    """
    Gruppiert Ergebnisse in standardisierte Kategorien
    
    Args:
        row: DataFrame-Zeile
        
    Returns:
        Gruppierte Kategorie
    """
    if row['Indikator'] in ['General comments', 'Data last update']:
        return 'Other'
    
    result_lower = str(row['Ergebnis']).lower() if pd.notna(row['Ergebnis']) else ""
    
    if 'partially' in result_lower or 'reservations' in result_lower:
        return 'Partially'
    elif 'yes' in result_lower:
        return 'Yes'
    elif 'no' in result_lower or 'discriminatory' in result_lower or 'corporal punishment' in result_lower:
        return 'No'
    else:
        return None

def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Bereitet Daten für die Analyse vor
    
    Args:
        df: Rohdaten
        
    Returns:
        Tuple aus (gefilterte_daten, karten_daten, indikator_liste)
    """
    # Filter irrelevante Indikatoren
    df_filtered = df[~(
        ((df['Indikator'] == 'General comments') | (df['Indikator'] == 'Data last update')) &
        (df['Ergebnis'].astype(str).str.lower() == 'yes')
    )]

    # Gruppierung anwenden
    df_filtered['Result_Grouped'] = df_filtered.apply(group_result, axis=1)
    
    # Daten für Karten vorbereiten
    df_for_maps = df_filtered[~df_filtered['Indikator'].isin(['General comments', 'Data last update'])]

    # Indikator-Liste erstellen (ohne irrelevante)
    indikator_liste = sorted(list(set(df['Indikator'].dropna().unique())))
    indikator_liste = [
        ind for ind in indikator_liste 
        if ind not in ["General comments", "Data last update"]
    ]

    return df_filtered, df_for_maps, indikator_liste

# ===== UI-KOMPONENTEN (MIT ÜBERSETZUNGEN) =====
def display_header():
    """Zeigt Header und Einführung - Mit Übersetzungen"""
    st.title(t("indicators_title", "Indikatoren & Entwicklung"))
    
    if st.session_state.language == "DE":
        st.markdown("""
        Diese Seite bietet detaillierte Informationen zu allen Bildungsindikatoren und zeigt deren Entwicklung über die Zeit.
        Sie können die globale Verbreitung verschiedener Bildungsstandards analysieren und regionale Unterschiede erkennen.
        Besonders wichtig ist die Beobachtung von Fortschritten und Rückschritten bei der Implementierung bildungsrelevanter Gesetze und Richtlinien.
        """)
    else:
        st.markdown("""
        This page provides detailed information on all education indicators and shows their development over time.
        You can analyze the global distribution of various education standards and identify regional differences.
        Particularly important is monitoring progress and setbacks in the implementation of education-relevant laws and guidelines.
        """)

def create_indicator_controls(df: pd.DataFrame, indikator_liste: List[str]) -> tuple[str, int]:
    """
    Erstellt Auswahl-Kontrollen für Indikator und Jahr - Mit Übersetzungen
    
    Args:
        df: DataFrame mit Daten
        indikator_liste: Liste verfügbarer Indikatoren
        
    Returns:
        Tuple aus (selected_indicator, selected_year)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.language == "DE":
            st.markdown('<div style="font-weight: bold; margin-bottom: 10px;">📘 Indikator auswählen</div>', unsafe_allow_html=True)
            label = "Indikator"
        else:
            st.markdown('<div style="font-weight: bold; margin-bottom: 10px;">📘 Select Indicator</div>', unsafe_allow_html=True)
            label = "Indicator"
        selected_indicator = st.selectbox(label, indikator_liste, label_visibility="collapsed")
    
    # Indikator-spezifische Jahre ermitteln
    indicator_df = df[
        (df['Indikator'] == selected_indicator) &
        df['Breitengrad'].notna() &
        df['Längengrad'].notna() &
        df['Ergebnis'].notna()
    ]
    
    available_years = sorted(indicator_df['Jahr'].dropna().unique())
    
    with col2:
        if st.session_state.language == "DE":
            st.markdown('<div style="font-weight: bold; margin-bottom: 10px;">📅 Jahr auswählen</div>', unsafe_allow_html=True)
            label = "Jahr"
        else:
            st.markdown('<div style="font-weight: bold; margin-bottom: 10px;">📅 Select Year</div>', unsafe_allow_html=True)
            label = "Year"
        default_index = len(available_years) - 1 if available_years else 0
        selected_year = st.selectbox(label, available_years, index=default_index, label_visibility="collapsed")
    
    return selected_indicator, selected_year

def display_data_analysis_tabs(df_for_maps: pd.DataFrame, selected_indicator: str, indikator_liste: List[str]):
    """
    Zeigt die Haupt-Analyse-Tabs - NEUE MODULARE VISUALISIERUNG mit vollständiger Sprachunterstützung
    
    Args:
        df_for_maps: Gefilterte Daten für Karten
        selected_indicator: Ausgewählter Indikator
        indikator_liste: Liste aller Indikatoren
    """
    if st.session_state.language == "DE":
        st.header(f"📊 Datenanalyse: {selected_indicator}")
        tab_names = ["Länderranking 2019-2025", "Regionale Verteilung", "Entwicklung über Zeit"]
    else:
        st.header(f"📊 Data Analysis: {selected_indicator}")
        tab_names = ["Country Ranking 2019-2025", "Regional Distribution", "Development over Time"]
    
    # Tabs erstellen
    data_tabs = st.tabs(tab_names)
    
    # Tab 1: Länderranking - NEUE MODULARE VISUALISIERUNG
    with data_tabs[0]:
        if st.session_state.language == "DE":
            st.subheader("🏆 Länderranking nach Bildungsfortschritt")
            st.markdown("**Hinweis:** Dieses Ranking basiert auf der Anzahl erfüllter Bildungsstandards und deren Entwicklung über Zeit.")
        else:
            st.subheader("🏆 Country Ranking by Educational Progress")
            st.markdown("**Note:** This ranking is based on the number of fulfilled educational standards and their development over time.")
        
        # NEUE MODULARE utils-Funktion mit language Parameter
        show_country_ranking(
            df_for_maps, 
            indikator_liste, 
            IndicatorsConfig.REGIONEN, 
            calculate_progress, 
            calculate_change_score, 
            calculate_weighted_country_progress,
            language=st.session_state.language
        )
    
    # Tab 2: Regionale Verteilung - NEUE MODULARE VISUALISIERUNG
    with data_tabs[1]:
        if st.session_state.language == "DE":
            st.subheader("🌍 Regionale Verteilung der Bildungsstandards")
            st.markdown("**Analyse:** Vergleich der Bildungsfortschritte zwischen verschiedenen Weltregionen.")
        else:
            st.subheader("🌍 Regional Distribution of Education Standards")
            st.markdown("**Analysis:** Comparison of educational progress between different world regions.")
        
        # NEUE MODULARE utils-Funktion mit language Parameter
        current_year = df_for_maps['Jahr'].max() if not df_for_maps.empty else 2025
        show_regional_distribution(
            df_for_maps, 
            selected_indicator, 
            current_year, 
            IndicatorsConfig.REGIONEN,
            language=st.session_state.language
        )
    
    # Tab 3: Zeitentwicklung - NEUE MODULARE VISUALISIERUNG
    with data_tabs[2]:
        if st.session_state.language == "DE":
            st.subheader("📈 Entwicklung über Zeit")
            st.markdown("**Zeitreihenanalyse:** Verfolgung der Veränderungen bei Bildungsstandards von 2019 bis 2025.")
        else:
            st.subheader("📈 Development over Time")
            st.markdown("**Time Series Analysis:** Tracking changes in education standards from 2019 to 2025.")
        
        # NEUE MODULARE utils-Funktion mit language Parameter
        show_time_development(
            df_for_maps, 
            selected_indicator, 
            indikator_liste, 
            calculate_progress,
            language=st.session_state.language
        )

# ===== HAUPT-ANWENDUNG =====
def main():
    """Hauptfunktion der Indikatoren-Entwicklung Page - Mit vollständiger Sprachunterstützung"""
    
    # === SPRACHSYSTEM SETUP ===
    init_language()
    language_switcher()
    
    # Setup Sidebar Copyright (bestehender Code beibehalten)
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
    
    # Styles anwenden (bestehende utils function)
    set_styles()
    
    # Header anzeigen
    display_header()
    
    # Daten laden (bestehende utils function) - Mit Übersetzungen
    if st.session_state.language == "DE":
        spinner_text = "Lade Bildungsdaten..."
        error_text = "Die Daten konnten nicht geladen werden. Bitte überprüfen Sie die Datei 'heraltas1_updated.csv'."
        warning_text = "Keine gültigen Indikatoren gefunden."
    else:
        spinner_text = "Loading education data..."
        error_text = "The data could not be loaded. Please check the file 'heraltas1_updated.csv'."
        warning_text = "No valid indicators found."
    
    with st.spinner(spinner_text):
        df = load_data()
    
    if df.empty:
        st.error(error_text)
        return
    
    # Daten vorbereiten
    df_filtered, df_for_maps, indikator_liste = prepare_data(df)
    
    if not indikator_liste:
        st.warning(warning_text)
        return
    
    # Auswahl-Kontrollen
    selected_indicator, selected_year = create_indicator_controls(df, indikator_liste)
    
    # Analyse-Tabs anzeigen - NEUE MODULARE VISUALISIERUNG
    display_data_analysis_tabs(df_for_maps, selected_indicator, indikator_liste)
    
    # Standard-Footer (shared component)
    display_standard_footer()

# ===== AUSFÜHRUNG =====
if __name__ == "__main__":
    main()
else:
    main()