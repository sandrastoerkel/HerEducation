"""
Multilingual text constants and helper functions for HerAtlas Indicators visualization.

This module provides all text constants in German and English for consistent 
multilingual support across all indicator visualization functions.
"""

from typing import Dict, Any

# =============================================================================
# MULTILINGUAL TEXT CONSTANTS
# =============================================================================

TEXTS = {
    "DE": {
        # Status labels
        "status_yes": "Ja",
        "status_partially": "Teilweise", 
        "status_no": "Nein",
        
        # Progress/Regress labels
        "progress": "Fortschritte",
        "regress": "Rückschritte",
        "fortschritt": "Fortschritt",
        "rueckschritt": "Rückschritt",
        
        # Chart titles
        "regional_distribution_title": "Regionale Verteilung für \"{}\" ({})",
        "timeline_title": "Zeitliche Entwicklung für \"{}\"",
        "progress_regress_title": "Anzahl der Fortschritte und Rückschritte",
        "global_development_title": "Globale Entwicklung aller Bildungsindikatoren über die Zeit",
        "country_ranking_progress_title": "Top 10 Länder mit den meisten Fortschritten",
        "country_ranking_regress_title": "Länder mit den meisten Rückschritten",
        "country_ranking_netto_title": "Länder nach Netto-Veränderung",
        "top_indicators_title": "Top 5 Indikatoren mit den meisten Fortschritten",
        "positive_netto_title": "Länder mit positiver Netto-Veränderung",
        "negative_netto_title": "Länder mit negativer Netto-Veränderung",
        "country_details_title": "Details zu einem Land",
        "changes_by_year_title": "Veränderungen nach Jahr",
        
        # Axis labels
        "region_label": "Region",
        "percent_label": "Prozent (%)",
        "year_label": "Jahr",
        "count_label": "Anzahl der Länder",
        "indicator_label": "Indikator",
        "number_label": "Anzahl",
        "score_label": "Anzahl / Score",
        "changes_label": "Anzahl der Veränderungen",
        "countries_label": "Länder",
        
        # Headers and subheaders
        "timeline_development_header": "Entwicklung über Zeit",
        "global_development_header": "Globale Entwicklung aller Indikatoren",
        "progress_ranking_header": "Top-Länder mit den meisten Fortschritten",
        "regress_ranking_header": "Länder mit den meisten Rückschritten",
        "netto_ranking_header": "Länder nach Netto-Veränderung",
        "progress_details_header": "Details zu den Fortschritten",
        "regress_details_header": "Details zu den Rückschritten",
        "top_indicators_header": "Top-Indikatoren nach Fortschritten",
        "regional_details_header": "Detailansicht nach Regionen",
        
        # Filter labels
        "filter_options_header": "Filteroptionen",
        "filter_by_indicator": "Nach Indikator filtern",
        "filter_by_region": "Nach Region filtern",
        "filter_by_indicator_checkbox": "Nach spezifischem Indikator filtern",
        "filter_by_region_checkbox": "Nach spezifischer Region filtern",
        "select_indicator": "Indikator auswählen",
        "select_region": "Region auswählen",
        "select_country": "Land auswählen",
        
        # Info messages
        "data_processing_info": """**Hinweis zur Datenverarbeitung:**
Die Daten aus dem Jahr 2019 dienen als Grundstatus (Baseline) für alle Indikatoren. In den darauffolgenden 
Jahren wurden nur Veränderungen erfasst. Die hier dargestellten Daten berücksichtigen diese Logik - wenn für ein 
Land in einem Jahr kein neuer Status erfasst wurde, wird der letzte bekannte Status verwendet.""",
        
        "ranking_info": """**Hinweis zur Datenauswertung:**
Diese Analyse zeigt, welche Länder zwischen 2019 und 2025 die größten Fortschritte oder Rückschritte 
in Bezug auf Bildungsindikatoren gemacht haben. Als Grundannahme gilt, dass der Status von 2019 als Baseline dient 
und in den folgenden Jahren nur Veränderungen erfasst wurden.

Ein Fortschritt wird gezählt, wenn ein Land seinen Status von "Nein" zu "Teilweise", von "Nein" zu "Ja" oder 
von "Teilweise" zu "Ja" verbessert hat. Ein Rückschritt wird gezählt, wenn sich der Status in die entgegengesetzte 
Richtung verändert hat.

Der Score berücksichtigt die Gewichtung der Veränderungen: Ein vollständiger Wechsel (Nein→Ja oder Ja→Nein) 
zählt doppelt so viel wie ein teilweiser Wechsel.""",
        
        "weighted_score_explanation": """**Hinweis zum gewichteten Score:**

Der gewichtete Score ist ein Bewertungssystem, das die Qualität und Bedeutung der Fortschritte differenzierter erfasst als nur die reine Anzahl:

- Ein kompletter Fortschritt (von "Nein" zu "Ja") erhält 2 Punkte, da dies die bedeutendste Verbesserung darstellt
- Ein teilweiser Fortschritt (von "Nein" zu "Teilweise" oder von "Teilweise" zu "Ja") erhält 1 Punkt
- Bei Rückschritten wird analog verfahren: Ein vollständiger Rückschritt (von "Ja" zu "Nein") gibt -2 Punkte und ein teilweiser Rückschritt -1 Punkt

Durch dieses Bewertungssystem erhalten Länder, die bedeutsamere Fortschritte gemacht haben, einen höheren Score als Länder mit der gleichen Anzahl kleinerer Fortschritte. Dies ermöglicht ein nuancierteres Ranking, das nicht nur die Häufigkeit, sondern auch die Qualität der Verbesserungen berücksichtigt.""",
        
        # Warning and info messages
        "no_data_available": "Keine Daten verfügbar für {}.",
        "no_timeline_data": "Keine zeitlichen Daten verfügbar für den Indikator '{}'.",
        "no_progress_found": "Keine Länder mit Fortschritten gefunden.",
        "no_regress_found": "Keine Länder mit Rückschritten gefunden.",
        "no_netto_changes": "Keine Länder mit Netto-Veränderungen gefunden.",
        "no_positive_netto": "Keine Länder mit positiver Netto-Veränderung gefunden.",
        "no_negative_netto": "Keine Länder mit negativer Netto-Veränderung gefunden.",
        "no_countries_with_changes": "Keine Länder mit Veränderungen gefunden.",
        "no_detailed_data": "Keine detaillierten Daten verfügbar.",
        "no_detailed_progress": "Keine detaillierten Fortschrittsdaten verfügbar.",
        "no_detailed_regress": "Keine detaillierten Rückschrittsdaten verfügbar.",
        "no_detailed_progress_regress": "Keine detaillierten Fortschritte oder Rückschritte gefunden.",
        
        # Metrics labels
        "total_countries": "Gesamtländer",
        "net_count": "Netto Anzahl",
        "score": "Score",
        "change": "Veränderung",
        "indicator": "Indikator",
        "from_to": "{} → {}",
        "score_value": "Score: {}",
        "year_summary": "Jahr {} - {} Fortschritte, {} Rückschritte",
        
        # Expandable sections
        "region_detail_view": "{} - Detailansicht",
        "countries_with_yes": "Länder mit 'Ja'-Status:",
        "countries_with_partially": "Länder mit 'Teilweise'-Status:",
        "countries_with_no": "Länder mit 'Nein'-Status:",
        "no_countries_found": "Keine Länder gefunden.",
        
        # Tabs
        "tab_progress": "Fortschritte",
        "tab_regress": "Rückschritte", 
        "tab_netto": "Netto-Veränderung"
    },
    
    "EN": {
        # Status labels
        "status_yes": "Yes",
        "status_partially": "Partially",
        "status_no": "No",
        
        # Progress/Regress labels
        "progress": "Progress",
        "regress": "Regress",
        "fortschritt": "Progress",
        "rueckschritt": "Regress",
        
        # Chart titles
        "regional_distribution_title": "Regional Distribution for \"{}\" ({})",
        "timeline_title": "Timeline Development for \"{}\"",
        "progress_regress_title": "Number of Progress and Regress",
        "global_development_title": "Global Development of All Education Indicators Over Time",
        "country_ranking_progress_title": "Top 10 Countries with Most Progress",
        "country_ranking_regress_title": "Countries with Most Regress",
        "country_ranking_netto_title": "Countries by Net Change",
        "top_indicators_title": "Top 5 Indicators with Most Progress",
        "positive_netto_title": "Countries with Positive Net Change",
        "negative_netto_title": "Countries with Negative Net Change",
        "country_details_title": "Details for a Country",
        "changes_by_year_title": "Changes by Year",
        
        # Axis labels
        "region_label": "Region",
        "percent_label": "Percent (%)",
        "year_label": "Year",
        "count_label": "Number of Countries",
        "indicator_label": "Indicator",
        "number_label": "Number",
        "score_label": "Number / Score",
        "changes_label": "Number of Changes",
        "countries_label": "Countries",
        
        # Headers and subheaders
        "timeline_development_header": "Development Over Time",
        "global_development_header": "Global Development of All Indicators",
        "progress_ranking_header": "Top Countries with Most Progress",
        "regress_ranking_header": "Countries with Most Regress",
        "netto_ranking_header": "Countries by Net Change",
        "progress_details_header": "Details on Progress",
        "regress_details_header": "Details on Regress",
        "top_indicators_header": "Top Indicators by Progress",
        "regional_details_header": "Detailed View by Regions",
        
        # Filter labels
        "filter_options_header": "Filter Options",
        "filter_by_indicator": "Filter by Indicator",
        "filter_by_region": "Filter by Region",
        "filter_by_indicator_checkbox": "Filter by specific indicator",
        "filter_by_region_checkbox": "Filter by specific region",
        "select_indicator": "Select indicator",
        "select_region": "Select region",
        "select_country": "Select country",
        
        # Info messages
        "data_processing_info": """**Note on Data Processing:**
The data from 2019 serves as the baseline status for all indicators. In subsequent years, only changes were recorded. 
The data presented here takes this logic into account - if no new status was recorded for a country in a year, 
the last known status is used.""",
        
        "ranking_info": """**Note on Data Analysis:**
This analysis shows which countries made the greatest progress or regress regarding education indicators between 2019 and 2025. 
The basic assumption is that the status from 2019 serves as baseline and only changes were recorded in subsequent years.

Progress is counted when a country improved its status from "No" to "Partially", from "No" to "Yes" or 
from "Partially" to "Yes". Regress is counted when the status changed in the opposite direction.

The score considers the weighting of changes: A complete change (No→Yes or Yes→No) counts twice as much as a partial change.""",
        
        "weighted_score_explanation": """**Note on Weighted Score:**

The weighted score is an evaluation system that captures the quality and significance of progress more differentiated than just the pure number:

- A complete progress (from "No" to "Yes") receives 2 points, as this represents the most significant improvement
- A partial progress (from "No" to "Partially" or from "Partially" to "Yes") receives 1 point
- For regress, the same logic applies: A complete regress (from "Yes" to "No") gives -2 points and a partial regress -1 point

Through this evaluation system, countries that made more significant progress receive a higher score than countries with the same number of smaller progress steps. This enables a more nuanced ranking that considers not only frequency but also the quality of improvements.""",
        
        # Warning and info messages
        "no_data_available": "No data available for {}.",
        "no_timeline_data": "No timeline data available for indicator '{}'.",
        "no_progress_found": "No countries with progress found.",
        "no_regress_found": "No countries with regress found.",
        "no_netto_changes": "No countries with net changes found.",
        "no_positive_netto": "No countries with positive net change found.",
        "no_negative_netto": "No countries with negative net change found.",
        "no_countries_with_changes": "No countries with changes found.",
        "no_detailed_data": "No detailed data available.",
        "no_detailed_progress": "No detailed progress data available.",
        "no_detailed_regress": "No detailed regress data available.",
        "no_detailed_progress_regress": "No detailed progress or regress found.",
        
        # Metrics labels
        "total_countries": "Total Countries",
        "net_count": "Net Count",
        "score": "Score",
        "change": "Change",
        "indicator": "Indicator",
        "from_to": "{} → {}",
        "score_value": "Score: {}",
        "year_summary": "Year {} - {} Progress, {} Regress",
        
        # Expandable sections
        "region_detail_view": "{} - Detail View",
        "countries_with_yes": "Countries with 'Yes' Status:",
        "countries_with_partially": "Countries with 'Partially' Status:",
        "countries_with_no": "Countries with 'No' Status:",
        "no_countries_found": "No countries found.",
        
        # Tabs
        "tab_progress": "Progress",
        "tab_regress": "Regress",
        "tab_netto": "Net Change"
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_text(key: str, language: str = "DE", *args) -> str:
    """
    Get localized text for a given key.
    
    Args:
        key: Text key to look up
        language: Language code ("DE" or "EN")
        *args: Arguments for string formatting
    
    Returns:
        Localized text string
    """
    try:
        text = TEXTS[language].get(key, key)
        if args:
            return text.format(*args)
        return text
    except (KeyError, ValueError):
        return key


def get_status_labels(language: str = "DE") -> Dict[str, str]:
    """
    Get status labels for the specified language.
    
    Args:
        language: Language code ("DE" or "EN")
    
    Returns:
        Dictionary mapping status values to localized labels
    """
    return {
        "Yes": get_text("status_yes", language),
        "Partially": get_text("status_partially", language),
        "No": get_text("status_no", language)
    }


def get_legend_labels(language: str = "DE") -> Dict[str, str]:
    """
    Get legend labels for charts.
    
    Args:
        language: Language code ("DE" or "EN")
    
    Returns:
        Dictionary with legend labels
    """
    return get_status_labels(language)


def get_progress_regress_labels(language: str = "DE") -> Dict[str, str]:
    """
    Get progress and regress labels.
    
    Args:
        language: Language code ("DE" or "EN")
    
    Returns:
        Dictionary with progress/regress labels
    """
    return {
        "progress": get_text("progress", language),
        "regress": get_text("regress", language)
    }