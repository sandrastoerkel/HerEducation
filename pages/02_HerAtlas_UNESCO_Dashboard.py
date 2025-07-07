"""
HerEducation - UNESCO HerAtlas Dashboard
Modernisierte Version mit modularer Architektur + Language Switch

VORHER: 700+ Zeilen, Code-Duplikation
NACHHER: Saubere Struktur, wiederverwendbare Komponenten + Mehrsprachigkeit
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Imports - bestehende Utils bleiben erhalten
from utils.indicators import get_indicators_sections
from utils.shared_components import display_standard_footer

# === SPRACHSYSTEM IMPORTIEREN ===
from utils.language_switcher_config import init_language, get_text, t
from utils.language_switcher_ui import language_switcher

# ===== KONFIGURATION =====
class DashboardConfig:
    """Zentrale Konfiguration für das UNESCO Dashboard"""
    
    # Daten-Pfade (mehrere Fallbacks für Robustheit)
    DATA_PATHS = [
        'heraltas1_updated.csv',
        'data/heraltas1_updated.csv', 
        '../data/heraltas1_updated.csv',
        Path(__file__).parent.parent / 'data' / 'heraltas1_updated.csv'
    ]
    
    # Farb-Mapping für Ergebnisse
    COLOR_MAP = {
        "Yes": [0, 200, 0, 160],
        "No": [200, 0, 0, 160], 
        "Partially": [255, 165, 0, 160],
        "Other": [120, 120, 120, 100],
        "Unknown": [150, 150, 150, 100],
    }
    
    # Karten-Konfiguration
    MAP_STYLE = 'mapbox://styles/mapbox/satellite-streets-v11'
    MAP_HEIGHT = 600
    SCATTER_RADIUS = 70000

# ===== DATEN-FUNKTIONEN =====
@st.cache_data
def load_unesco_data() -> pd.DataFrame:
    """
    Lädt UNESCO-Bildungsdaten mit Fallback-Pfaden
    
    Returns:
        DataFrame mit UNESCO-Daten oder leeres DataFrame bei Fehler
    """
    try:
        # Versuche verschiedene Pfade
        for path in DashboardConfig.DATA_PATHS:
            try:
                df = pd.read_csv(path)
                # Spalten umbenennen für bessere Lesbarkeit
                df = df.rename(columns={
                    'Countries (ISO2)': 'ISO2',
                    'Countries': 'Land',
                    'Year': 'Jahr', 
                    'Indicators': 'Indikator',
                    'Result': 'Ergebnis',
                    'Analysis [EN]': 'Analyse',
                    'latitude': 'Breitengrad',
                    'longitude': 'Längengrad'
                })
                return df
            except FileNotFoundError:
                continue
        
        # Wenn alle Pfade fehlschlagen
        if st.session_state.language == "DE":
            st.error("Die Datei 'heraltas1_updated.csv' konnte nicht gefunden werden.")
        else:
            st.error("The file 'heraltas1_updated.csv' could not be found.")
        return pd.DataFrame()
        
    except Exception as e:
        if st.session_state.language == "DE":
            st.error(f"Fehler beim Laden der Daten: {e}")
        else:
            st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def process_data_with_forward_fill(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verarbeitet Daten mit Forward-Fill-Logik für Zeitreihen
    
    Args:
        df: Rohdaten DataFrame
        
    Returns:
        Verarbeitetes DataFrame mit Forward-Fill
    """
    if df.empty:
        return df
        
    country_indicator_pairs = df[['Land', 'Indikator']].drop_duplicates()
    all_years = sorted(df['Jahr'].unique())
    result_rows = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (_, row) in enumerate(country_indicator_pairs.iterrows()):
        country = row['Land']
        indicator = row['Indikator']
        
        entries = df[(df['Land'] == country) & (df['Indikator'] == indicator)].sort_values('Jahr')
        
        if entries.empty:
            continue
            
        last_valid_entry = None
        
        for year in all_years:
            current_entries = entries[entries['Jahr'] == year]
            
            if not current_entries.empty:
                result_rows.append(current_entries.iloc[0].to_dict())
                last_valid_entry = current_entries.iloc[0].to_dict()
            elif last_valid_entry is not None and year > last_valid_entry['Jahr']:
                new_entry = last_valid_entry.copy()
                new_entry['Jahr'] = year
                result_rows.append(new_entry)
        
        # Progress Update
        progress = (i + 1) / len(country_indicator_pairs)
        progress_bar.progress(min(progress, 1.0))
        
        if i % 50 == 0:  # Update status every 50 iterations
            if st.session_state.language == "DE":
                status_text.text(f"Verarbeite {country} - {indicator}")
            else:
                status_text.text(f"Processing {country} - {indicator}")
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(result_rows) if result_rows else df.copy()

def group_result(row: pd.Series) -> Optional[str]:
    """
    Gruppiert Ergebnisse in Kategorien
    
    Args:
        row: DataFrame-Zeile
        
    Returns:
        Gruppierte Kategorie oder None
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

# ===== UI-KOMPONENTEN =====
def display_header():
    """Zeigt Header und Einführung an - Mit Übersetzungen"""
    st.title(t("unesco_dashboard_title", "HerAtlas Unesco Dashboard"))
    
    if st.session_state.language == "DE":
        st.markdown("""
        Diese interaktive Anwendung ermöglicht die Analyse des rechtlichen Rahmens und der Bildungspolitik in 196 Ländern weltweit.
        Die Daten umfassen verschiedene Bildungsindikatoren wie internationale Bildungsabkommen, verfassungsrechtliche Verankerung
        des Rechts auf Bildung, Schulpflicht und mehr.

        **Daten:** HerAtlas UNESCO | **Visualisierungen:** Sandra Störkel
        """)
    else:
        st.markdown("""
        This interactive application enables analysis of the legal framework and education policy in 196 countries worldwide.
        The data includes various education indicators such as international education agreements, constitutional anchoring
        of the right to education, compulsory education and more.

        **Data:** HerAtlas UNESCO | **Visualizations:** Sandra Störkel
        """)

def display_data_processing_info():
    """Info-Box zur Datenverarbeitung - Mit Übersetzungen"""
    if st.session_state.language == "DE":
        with st.expander("ℹ️ Informationen zur Datenverarbeitung", expanded=False):
            st.info("""
            **Hinweis zur Datenverarbeitung:**
            
            Die Daten aus dem Jahr 2019 dienen als Grundstatus für alle Indikatoren. 
            In den darauffolgenden Jahren wurden nur Veränderungen erfasst.
            
            Für die Anzeige bedeutet das:
            - Für 2019 werden die Originaldaten angezeigt
            - Für spätere Jahre werden für jedes Land und jeden Indikator die aktuellsten verfügbaren Daten angezeigt
            - Wenn ein Indikator in einem Jahr nicht erwähnt wird, gilt der zuletzt erfasste Status weiterhin
            """)
    else:
        with st.expander("ℹ️ Data Processing Information", expanded=False):
            st.info("""
            **Note on Data Processing:**
            
            The data from 2019 serves as the basic status for all indicators. 
            In subsequent years, only changes were recorded.
            
            For the display this means:
            - For 2019, the original data is displayed
            - For later years, the most current available data is displayed for each country and indicator
            - If an indicator is not mentioned in a year, the last recorded status continues to apply
            """)

def display_indicators_overview(df: pd.DataFrame):
    """
    Zeigt Übersicht der Bildungsindikatoren - Mit Übersetzungen
    
    Args:
        df: Filtered DataFrame für Maps
    """
    st.header(t("education_indicators", "Vorhandene Bildungsindikatoren"))
    
    try:
        abschnitte = get_indicators_sections()
        available_years = sorted(df['Jahr'].dropna().unique())
        current_year = available_years[-1] if available_years else 2019
        
        # DEBUG: Zeige die tatsächlichen Abschnittstitel
        # st.write("DEBUG - Gefundene Abschnitte:", list(abschnitte.keys()))
        
        for abschnitt_titel, indikatoren in abschnitte.items():
            # Direkte Übersetzungslogik basierend auf bekannten Mustern
            if st.session_state.language == "EN":
                # Übersetze die häufigsten deutschen Abschnittstitel
                if "Zugang" in abschnitt_titel and "Pflicht" in abschnitt_titel:
                    translated_title = "Access and Compulsory Education"
                elif "Rechtlicher Schutz" in abschnitt_titel or "Gleichbehandlung" in abschnitt_titel:
                    translated_title = "Legal Protection & Equal Treatment"
                elif "Internationale" in abschnitt_titel and "Verpflichtungen" in abschnitt_titel:
                    translated_title = "International Obligations"
                elif "Altersgrenzen" in abschnitt_titel or "Kohärenz" in abschnitt_titel:
                    translated_title = "Age Limits & Legal System Coherence"
                else:
                    # Fallback: versuche grundlegende Übersetzungen
                    translated_title = abschnitt_titel.replace("Bildung", "Education")
                    translated_title = translated_title.replace("Rechte", "Rights")
                    translated_title = translated_title.replace("Schutz", "Protection")
                    translated_title = translated_title.replace("Gleichbehandlung", "Equal Treatment")
                    translated_title = translated_title.replace("Internationale", "International")
                    translated_title = translated_title.replace("Verpflichtungen", "Obligations")
                    translated_title = translated_title.replace("Altersgrenzen", "Age Limits")
                    translated_title = translated_title.replace("Rechtssystem", "Legal System")
                    translated_title = translated_title.replace("Kohärenz", "Coherence")
                    translated_title = translated_title.replace("Zugang", "Access")
                    translated_title = translated_title.replace("Pflicht", "Compulsory")
            else:
                # Deutsche Version - Original beibehalten
                translated_title = abschnitt_titel
            
            with st.expander(translated_title, expanded=False):
                for i, (en_title, de_title, beschreibung) in enumerate(indikatoren):
                    # Titel basierend auf Sprache wählen
                    if st.session_state.language == "DE":
                        title = de_title if de_title else en_title
                        description = beschreibung
                    else:
                        title = en_title
                        # Für Englisch verwenden wir den deutschen Beschreibungstext, 
                        # da keine englischen Beschreibungen verfügbar sind
                        description = beschreibung
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #2563EB; background-color: rgba(37, 99, 235, 0.05);">
                        <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px;">{i+1}. {title}</div>
                        <div style="font-size: 0.95em; line-height: 1.4;">{description}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
    except Exception as e:
        if st.session_state.language == "DE":
            st.warning(f"Indikatoren konnten nicht geladen werden: {e}")
        else:
            st.warning(f"Indicators could not be loaded: {e}")

def create_world_map(df: pd.DataFrame, selected_indicator: str, selected_year: int) -> None:
    """
    Erstellt interaktive Weltkarte - Mit Übersetzungen
    
    Args:
        df: DataFrame mit Daten
        selected_indicator: Ausgewählter Indikator
        selected_year: Ausgewähltes Jahr
    """
    st.subheader(f"🗺️ {t('world_map', 'Weltkarte: Ergebnisse pro Land')}")
    
    # Daten für Karte filtern
    indicator_df = df[
        (df['Indikator'] == selected_indicator) &
        df['Breitengrad'].notna() &
        df['Längengrad'].notna() &
        df['Ergebnis'].notna()
    ]
    
    filtered = indicator_df[indicator_df['Jahr'] == selected_year]
    
    if filtered.empty:
        if st.session_state.language == "DE":
            st.warning("Keine Daten für die ausgewählte Kombination verfügbar.")
        else:
            st.warning("No data available for the selected combination.")
        return
    
    # Länderauswahl (optional)
    länder_liste = sorted(filtered['Land'].dropna().unique())
    if st.session_state.language == "DE":
        select_label = "🌍 Land auswählen (optional)"
        all_option = "Alle anzeigen"
    else:
        select_label = "🌍 Select country (optional)"
        all_option = "Show all"
        
    selected_country = st.selectbox(
        select_label, 
        [all_option] + länder_liste
    )
    
    if selected_country != all_option and selected_country != "Alle anzeigen":
        filtered = filtered[filtered['Land'] == selected_country]
    
    # Karten-Daten vorbereiten
    map_df = filtered[['Land', 'Breitengrad', 'Längengrad', 'Ergebnis', 'Analyse', 'Result_Grouped']].drop_duplicates()
    map_df["color"] = map_df["Result_Grouped"].apply(
        lambda r: DashboardConfig.COLOR_MAP.get(r, [120, 120, 120, 100])
    )

    # PyDeck Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[Längengrad, Breitengrad]',
        get_color='color',
        get_radius=DashboardConfig.SCATTER_RADIUS,
        pickable=True
    )

    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1)

    # Tooltip Text basierend auf Sprache
    if st.session_state.language == "DE":
        tooltip = {
            "html": """
                <div style='max-width: 400px; white-space: normal;'>
                    <b>Land:</b> {Land}<br>
                    <b>Ergebnis:</b> {Ergebnis}<br>
                    <b>Analyse:</b><br><span style='font-style: italic;'>{Analyse}</span>
                </div>
            """,
            "style": {"backgroundColor": "rgba(255, 255, 255, 0.95)", "color": "#000000", "fontSize": "12px"}
        }
    else:
        tooltip = {
            "html": """
                <div style='max-width: 400px; white-space: normal;'>
                    <b>Country:</b> {Land}<br>
                    <b>Result:</b> {Ergebnis}<br>
                    <b>Analysis:</b><br><span style='font-style: italic;'>{Analyse}</span>
                </div>
            """,
            "style": {"backgroundColor": "rgba(255, 255, 255, 0.95)", "color": "#000000", "fontSize": "12px"}
        }
    
    # Karte anzeigen
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer], 
            initial_view_state=view_state, 
            tooltip=tooltip,
            height=DashboardConfig.MAP_HEIGHT,
            map_style=DashboardConfig.MAP_STYLE
        ), 
        use_container_width=True
    )
    
    # Legende
    display_map_legend()

def display_map_legend():
    """Zeigt Karten-Legende an"""
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 20px 0; background-color: #f8f9fa; padding: 10px; border-radius: 8px;">
        <div style="display: flex; align-items: center; margin: 0 15px;">
            <div style="width: 20px; height: 20px; border-radius: 4px; margin-right: 8px; background-color: rgba(0, 200, 0, 0.8);"></div>
            <span>Yes</span>
        </div>
        <div style="display: flex; align-items: center; margin: 0 15px;">
            <div style="width: 20px; height: 20px; border-radius: 4px; margin-right: 8px; background-color: rgba(200, 0, 0, 0.8);"></div>
            <span>No</span>
        </div>
        <div style="display: flex; align-items: center; margin: 0 15px;">
            <div style="width: 20px; height: 20px; border-radius: 4px; margin-right: 8px; background-color: rgba(255, 165, 0, 0.8);"></div>
            <span>Partially</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_statistics(filtered: pd.DataFrame):
    """
    Zeigt Statistiken für gefilterte Daten - Mit Übersetzungen
    
    Args:
        filtered: Gefilterte Daten
    """
    if filtered.empty:
        return
        
    st.subheader(t("summary", "Zusammenfassung"))
    
    # Ergebnis-Verteilung
    result_counts = filtered['Result_Grouped'].value_counts()
    
    # Metriken
    cols = st.columns(len(result_counts) if len(result_counts) <= 4 else 4)
    
    for i, (result, count) in enumerate(result_counts.items()):
        with cols[i % 4]:
            if st.session_state.language == "DE":
                result_text = result if result is not None else "Keine Angabe"
            else:
                result_text = result if result is not None else "No data"
            percentage = f"{count/len(filtered)*100:.1f}%"
            st.metric(label=result_text, value=count, delta=percentage)
    
    # Pie Chart
    st.subheader(t("result_distribution", "Verteilung der Ergebnisse"))
    
    fig = px.pie(
        names=result_counts.index.fillna("Keine Angabe" if st.session_state.language == "DE" else "No data"),
        values=result_counts.values,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    
    st.plotly_chart(fig, use_container_width=True)

# ===== TAB-FUNKTIONEN =====
def display_overview_tab(df: pd.DataFrame, indikator_liste: List[str], available_years: List[int]):
    """Tab 1: Übersicht mit Karte und Statistiken - Mit Übersetzungen"""
    if st.session_state.language == "DE":
        st.header("Globaler Überblick")
    else:
        st.header("Global Overview")
    
    # Auswahl-Kontrollen
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.language == "DE":
            st.markdown("### 📘 Indikator auswählen")
            label = "Indikator"
        else:
            st.markdown("### 📘 Select Indicator")
            label = "Indicator"
        selected_indicator = st.selectbox(label, indikator_liste, label_visibility="collapsed")
    with col2:
        if st.session_state.language == "DE":
            st.markdown("### 📅 Jahr auswählen")
            label = "Jahr"
        else:
            st.markdown("### 📅 Select Year")
            label = "Year"
        selected_year = st.selectbox(label, available_years, label_visibility="collapsed")
    
    # Karte erstellen
    create_world_map(df, selected_indicator, selected_year)
    
    # Statistiken anzeigen
    filtered_data = df[
        (df['Indikator'] == selected_indicator) & 
        (df['Jahr'] == selected_year)
    ]
    display_statistics(filtered_data)
    
    return selected_indicator, selected_year

def display_comparison_tab(df: pd.DataFrame, selected_year: int, selected_indicator: str):
    """Tab 2: Ländervergleich - Mit Übersetzungen"""
    if st.session_state.language == "DE":
        st.header("Ländervergleich")
        select_label = 'Länder für Vergleich auswählen'
        info_text = "Wählen Sie mindestens zwei Länder aus, um einen Vergleich anzuzeigen."
        comparison_title = f"Vergleich für das Jahr {selected_year}"
        detail_title = f"Detailansicht: {selected_indicator}"
        analysis_label = "**Analyse:**"
        no_analysis = 'Keine Analyse verfügbar'
    else:
        st.header("Country Comparison")
        select_label = 'Select countries for comparison'
        info_text = "Select at least two countries to display a comparison."
        comparison_title = f"Comparison for year {selected_year}"
        detail_title = f"Detail view: {selected_indicator}"
        analysis_label = "**Analysis:**"
        no_analysis = 'No analysis available'
    
    all_countries = sorted(df['Land'].unique().tolist())
    selected_countries = st.multiselect(
        select_label, 
        all_countries, 
        default=all_countries[:3] if len(all_countries) >= 3 else all_countries
    )
    
    if len(selected_countries) < 2:
        st.info(info_text)
        return
    
    # Vergleichsdaten
    comparison_df = df[
        (df['Jahr'] == selected_year) & 
        (df['Land'].isin(selected_countries))
    ]
    
    # Pivot-Tabelle
    pivot_df = comparison_df.pivot(index='Indikator', columns='Land', values='Ergebnis')
    
    st.subheader(comparison_title)
    st.dataframe(pivot_df, use_container_width=True, height=600)
    
    # Detailansicht für ausgewählten Indikator
    st.subheader(detail_title)
    
    indicator_df = comparison_df[comparison_df['Indikator'] == selected_indicator]
    
    for _, row in indicator_df.iterrows():
        if st.session_state.language == "DE":
            result_text = row['Ergebnis'] if pd.notna(row['Ergebnis']) else 'Keine Angabe'
        else:
            result_text = row['Ergebnis'] if pd.notna(row['Ergebnis']) else 'No data'
        with st.expander(f"{row['Land']} - {result_text}"):
            analysis_text = row['Analyse'] if pd.notna(row['Analyse']) else no_analysis
            st.markdown(f"{analysis_label} {analysis_text}")

def display_data_table_tab(df: pd.DataFrame, selected_year: int, selected_indicator: str):
    """Tab 3: Datentabelle mit Filtern - Mit Übersetzungen"""
    if st.session_state.language == "DE":
        st.header("Datentabelle")
        st.subheader("Gefilterte Daten")
        year_label = "Jahr für Tabelle auswählen"
        indicator_label = "Indikator für Tabelle auswählen"
        search_label = "Land suchen:"
        count_label = "Anzahl der Einträge:"
        download_label = "Download als CSV"
        no_data_warning = "Keine Daten für die gewählten Filter gefunden."
    else:
        st.header("Data Table")
        st.subheader("Filtered Data")
        year_label = "Select year for table"
        indicator_label = "Select indicator for table"
        search_label = "Search country:"
        count_label = "Number of entries:"
        download_label = "Download as CSV"
        no_data_warning = "No data found for the selected filters."
    
    years = sorted(df['Jahr'].unique().tolist())
    indicators = sorted(list(set(df['Indikator'].unique().tolist())))
    
    # Filter-Kontrollen
    col1, col2 = st.columns(2)
    with col1:
        filtered_year = st.selectbox(
            year_label, 
            years, 
            index=years.index(selected_year) if selected_year in years else 0
        )
    with col2:
        filtered_indicator = st.selectbox(
            indicator_label, 
            indicators, 
            index=indicators.index(selected_indicator) if selected_indicator in indicators else 0
        )
    
    # Ländersuchfeld
    search_country = st.text_input(search_label, "")
    
    # Daten filtern
    filtered_df = df[
        (df['Jahr'] == filtered_year) & 
        (df['Indikator'] == filtered_indicator)
    ]
    
    if search_country:
        filtered_df = filtered_df[
            filtered_df['Land'].str.contains(search_country, case=False, na=False)
        ]
    
    # Ergebnisse anzeigen
    st.info(f"{count_label} {len(filtered_df)}")
    
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Land', 'Jahr', 'Indikator', 'Ergebnis', 'Analyse']],
            use_container_width=True,
            height=500
        )
        
        # Download-Button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        filename = f"bildungsatlas_{filtered_year}_{filtered_indicator.replace(' ', '_')}.csv"
        st.download_button(
            label=download_label,
            data=csv,
            file_name=filename,
            mime="text/csv"
        )
    else:
        st.warning(no_data_warning)

# ===== HAUPT-ANWENDUNG =====
def main():
    """Hauptfunktion der UNESCO Dashboard Page - Mit Sprachsystem"""
    
    # === SPRACHSYSTEM SETUP ===
    init_language()
    language_switcher()
    
    # === DEBUG: VERSIONEN ANZEIGEN - TEMPORÄR ===
    st.sidebar.error(f"🔍 DEBUG - Streamlit: {st.__version__}")
    st.sidebar.error(f"🔍 DEBUG - PyDeck: {pdk.__version__}")
    
    # Header anzeigen
    display_header()
    
    # Daten laden
    if st.session_state.language == "DE":
        spinner_text = "Lade UNESCO-Daten..."
        error_text = "Keine Daten verfügbar. Bitte überprüfen Sie die Datei-Pfade."
        processing_text = 'Verarbeite Daten... (Dies kann einen Moment dauern)'
    else:
        spinner_text = "Loading UNESCO data..."
        error_text = "No data available. Please check the file paths."
        processing_text = 'Processing data... (This may take a moment)'
    
    with st.spinner(spinner_text):
        raw_df = load_unesco_data()
    
    if raw_df.empty:
        st.error(error_text)
        return
    
    # Datenverarbeitung
    display_data_processing_info()
    
    with st.spinner(processing_text):
        df = process_data_with_forward_fill(raw_df)
    
    # Daten für Analyse vorbereiten
    df_all = df.copy()
    
    # Filter und Gruppierung
    df = df_all[~(
        ((df_all['Indikator'] == 'General comments') | (df_all['Indikator'] == 'Data last update')) &
        (df_all['Ergebnis'].astype(str).str.lower() == 'yes')
    )]
    
    df['Result_Grouped'] = df.apply(group_result, axis=1)
    df_all['Result_Grouped'] = df_all.apply(group_result, axis=1)
    
    df_filtered_for_maps = df[~df['Indikator'].isin(['General comments', 'Data last update'])]
    
    # Listen für UI vorbereiten
    indikator_liste = sorted(list(set(df_all['Indikator'].dropna().unique())))
    available_years = sorted(df_all['Jahr'].dropna().unique())
    
    # Indikatoren-Übersicht
    display_indicators_overview(df_filtered_for_maps)
    
    # Tab-Interface MIT ÜBERSETZUNGEN
    if st.session_state.language == "DE":
        tab_names = ["Übersicht", "Ländervergleich", "Datentabelle"]
    else:
        tab_names = ["Overview", "Country Comparison", "Data Table"]
    
    tab1, tab2, tab3 = st.tabs(tab_names)
    
    with tab1:
        selected_indicator, selected_year = display_overview_tab(
            df_filtered_for_maps, indikator_liste, available_years
        )
    
    with tab2:
        display_comparison_tab(df, selected_year, selected_indicator)
    
    with tab3:
        display_data_table_tab(df, selected_year, selected_indicator)
    
    # Footer
    st.markdown("---")
    if st.session_state.language == "DE":
        st.markdown("""
        <div style="text-align: center">
            <p>© 2025 Globaler Bildungsatlas Dashboard | Datenstand: April 2025</p>
            <p><small>Hinweis: Die Daten werden automatisch fortgeschrieben: 2019 dient als Grundlage und spätere Jahre zeigen nur Änderungen an.</small></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center">
            <p>© 2025 Global Education Atlas Dashboard | Data as of: April 2025</p>
            <p><small>Note: Data is automatically updated: 2019 serves as the baseline and later years show only changes.</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Standard-Footer
    display_standard_footer()

# ===== AUSFÜHRUNG =====
if __name__ == "__main__":
    main()
else:
    main()