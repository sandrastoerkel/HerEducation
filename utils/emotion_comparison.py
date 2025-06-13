import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import logging

from utils.emotion_detection import (
    EMOTION_LABEL_MAP, EMOTION_COLORS, 
    get_emotion_keywords, split_text_into_sentences, 
    analyze_sentence_structure
)

# =====================================================================================
# CONSTANTS
# =====================================================================================

# Visualization Constants
DEFAULT_CHART_HEIGHT = 500
SMALL_CHART_HEIGHT = 300
PREVIEW_LENGTH = 100

# Color Schemes
MODEL_COLOR = "#1976D2"
LINGUISTIC_COLOR = "#388E3C"
WEIGHTED_COLOR = "#7B1FA2"

COLOR_DISCRETE_MAP = {
    "Modell": MODEL_COLOR,
    "Linguistisch": LINGUISTIC_COLOR,
    "Gewichtet": WEIGHTED_COLOR
}

# Default Weights
DEFAULT_MODEL_WEIGHT = 0.7
DEFAULT_LINGUISTIC_WEIGHT = 0.3

# Evaluation Criteria Colors
EVALUATION_COLORS = {
    "Sehr gut": "background-color: #D5F5E3",
    "Gut": "background-color: #D5F5E3; opacity: 0.7",
    "Mittel": "background-color: #FCF3CF",
    "Begrenzt": "background-color: #FADBD8; opacity: 0.7",
    "Niedrig": "background-color: #FADBD8",
    "Einfach": "background-color: #D5F5E3",
    "Aufwändig": "background-color: #FADBD8"
}

# =====================================================================================
# CONFIGURATION
# =====================================================================================

@dataclass
class EmotionComparisonConfig:
    """Configuration for emotion comparison analysis."""
    model_weight: float = DEFAULT_MODEL_WEIGHT
    linguistic_weight: float = DEFAULT_LINGUISTIC_WEIGHT
    preview_length: int = PREVIEW_LENGTH
    chart_height: int = DEFAULT_CHART_HEIGHT
    small_chart_height: int = SMALL_CHART_HEIGHT
    
    @property
    def total_weight(self) -> float:
        """Ensure weights sum to 1.0."""
        return self.model_weight + self.linguistic_weight
    
    @property
    def normalized_model_weight(self) -> float:
        """Get normalized model weight."""
        return self.model_weight / self.total_weight if self.total_weight > 0 else 0.5
    
    @property
    def normalized_linguistic_weight(self) -> float:
        """Get normalized linguistic weight."""
        return self.linguistic_weight / self.total_weight if self.total_weight > 0 else 0.5

# =====================================================================================
# DATA PROCESSING FUNCTIONS
# =====================================================================================

def calculate_emotion_counts(df: pd.DataFrame, emotion_columns: List[str]) -> List[Dict[str, Any]]:
    """
    Calculate emotion counts for model and linguistic approaches.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion column names
        
    Returns:
        List of dictionaries with comparison data
    """
    comparison_data = []
    
    try:
        for emotion in emotion_columns:
            # Nur verarbeiten wenn die Spalte existiert
            if emotion not in df.columns:
                continue
                
            # Model-based detection
            model_count = len(df[df[emotion] > 0.5])
            
            # Linguistic detection
            ling_col = f"{emotion}_linguistic"
            ling_count = len(df[df[ling_col] > 0.5]) if ling_col in df.columns else 0
            
            comparison_data.extend([
                {"Emotion": emotion, "Methode": "Modell", "Anzahl": model_count},
                {"Emotion": emotion, "Methode": "Linguistisch", "Anzahl": ling_count}
            ])
            
    except Exception as e:
        logging.error(f"Error calculating emotion counts: {e}")
        
    return comparison_data

def calculate_weighted_scores(df: pd.DataFrame, emotion_columns: List[str], 
                            config: EmotionComparisonConfig) -> List[Dict[str, Any]]:
    """
    Calculate weighted scores for all approaches.
    
    Args:
        df: DataFrame with emotion data
        emotion_columns: List of emotion column names
        config: Configuration object
        
    Returns:
        List of dictionaries with score data
    """
    all_scores = []
    
    try:
        for emotion in emotion_columns:
            # Nur verarbeiten wenn beide Spalten existieren
            if emotion not in df.columns:
                continue
                
            ling_col = f"{emotion}_linguistic"
            if ling_col not in df.columns:
                # Nur Modell-Score hinzufügen wenn linguistic fehlt
                avg_model = df[emotion].mean()
                all_scores.append({"Emotion": emotion, "Score": avg_model, "Typ": "Modell"})
                continue
                
            avg_model = df[emotion].mean()
            avg_ling = df[ling_col].mean()
            avg_weighted = (avg_model * config.normalized_model_weight + 
                          avg_ling * config.normalized_linguistic_weight)
            
            all_scores.extend([
                {"Emotion": emotion, "Score": avg_weighted, "Typ": "Gewichtet"},
                {"Emotion": emotion, "Score": avg_model, "Typ": "Modell"},
                {"Emotion": emotion, "Score": avg_ling, "Typ": "Linguistisch"}
            ])
                
    except Exception as e:
        logging.error(f"Error calculating weighted scores: {e}")
        
    return all_scores

def calculate_example_scores(df: pd.DataFrame, example_idx: int, 
                           emotion_columns: List[str], 
                           config: EmotionComparisonConfig) -> List[Dict[str, Any]]:
    """
    Calculate scores for a specific example comment.
    
    Args:
        df: DataFrame with emotion data
        example_idx: Index of the example comment
        emotion_columns: List of emotion column names
        config: Configuration object
        
    Returns:
        List of dictionaries with example score data
    """
    example_data = []
    
    try:
        for emotion in emotion_columns:
            # Nur verarbeiten wenn die Spalte existiert
            if emotion not in df.columns:
                continue
                
            model_score = df.loc[example_idx, emotion]
            
            ling_col = f"{emotion}_linguistic"
            if ling_col not in df.columns:
                # Nur Modell-Score hinzufügen wenn linguistic fehlt
                example_data.append({"Emotion": emotion, "Methode": "Modell", "Score": model_score})
                continue
                
            ling_score = df.loc[example_idx, ling_col]
            weighted_score = (model_score * config.normalized_model_weight + 
                            ling_score * config.normalized_linguistic_weight)
            
            example_data.extend([
                {"Emotion": emotion, "Methode": "Modell", "Score": model_score},
                {"Emotion": emotion, "Methode": "Linguistisch", "Score": ling_score},
                {"Emotion": emotion, "Methode": "Gewichtet", "Score": weighted_score}
            ])
                
    except Exception as e:
        logging.error(f"Error calculating example scores: {e}")
        
    return example_data

def get_comment_previews(df: pd.DataFrame, preview_length: int = PREVIEW_LENGTH) -> Dict[str, int]:
    """
    Create comment previews for selection.
    
    Args:
        df: DataFrame with comments
        preview_length: Length of preview text
        
    Returns:
        Dictionary mapping previews to indices
    """
    try:
        if "clean_text" not in df.columns or len(df) == 0:
            return {}
            
        sample_comments = df["clean_text"].values
        comment_previews = [
            f"{comment[:preview_length]}..." if len(comment) > preview_length else comment 
            for comment in sample_comments
        ]
        
        return {preview: idx for preview, idx in zip(comment_previews, range(len(df)))}
        
    except Exception as e:
        logging.error(f"Error creating comment previews: {e}")
        return {}

# =====================================================================================
# VISUALIZATION FUNCTIONS
# =====================================================================================

def render_main_comparison_chart(comparison_df: pd.DataFrame) -> None:
    """Render the main comparison chart between model and linguistic approaches."""
    try:
        fig = px.bar(
            comparison_df,
            x="Emotion",
            y="Anzahl",
            color="Methode",
            barmode="group",
            color_discrete_map=COLOR_DISCRETE_MAP,
            title="Vergleich: Modell vs. Linguistische Erkennung"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Anzahl der Erkennungen',
            legend_title='Methode',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="comparison_main_chart")
        
    except Exception as e:
        logging.error(f"Error rendering main comparison chart: {e}")
        st.error("Fehler beim Erstellen des Hauptvergleichscharts.")

def render_keyword_treemap() -> None:
    """Render keyword treemap visualization."""
    try:
        emotion_keywords = get_emotion_keywords()
        keyword_data = []
        
        for emotion, words in emotion_keywords.items():
            for word in words[:10]:  # First 10 words for clarity
                keyword_data.append({"Emotion": emotion, "Wort": word})
        
        if not keyword_data:
            st.warning("Keine Emotionswörter für die Visualisierung verfügbar.")
            return
            
        keyword_df = pd.DataFrame(keyword_data)
        
        fig = px.treemap(
            keyword_df,
            path=[px.Constant("Emotionen"), "Emotion", "Wort"],
            color="Emotion",
            color_discrete_map=EMOTION_COLORS,
            title="Emotionale Schlüsselwörter für linguistische Analyse"
        )
        
        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="keyword_treemap")
        
    except Exception as e:
        logging.error(f"Error rendering keyword treemap: {e}")
        st.error("Fehler beim Erstellen der Keyword-Visualisierung.")

def render_weighted_approach_chart(all_scores_df: pd.DataFrame) -> None:
    """Render weighted approach comparison chart."""
    try:
        fig = px.line(
            all_scores_df, 
            x="Emotion", 
            y="Score", 
            color="Typ",
            markers=True,
            color_discrete_map={
                "Gewichtet": WEIGHTED_COLOR, 
                "Modell": MODEL_COLOR, 
                "Linguistisch": LINGUISTIC_COLOR
            },
            title="Gewichteter Kombinationsansatz im Vergleich"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Durchschnittlicher Score',
            legend_title='Methode',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="weighted_approach")
        
    except Exception as e:
        logging.error(f"Error rendering weighted approach chart: {e}")
        st.error("Fehler beim Erstellen des gewichteten Vergleichscharts.")

def render_example_analysis_chart(example_df: pd.DataFrame) -> None:
    """Render example analysis chart."""
    try:
        fig = px.bar(
            example_df,
            x="Emotion",
            y="Score",
            color="Methode",
            barmode="group",
            color_discrete_map=COLOR_DISCRETE_MAP,
            title="Emotionsscores für den Beispielkommentar"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Score',
            legend_title='Methode',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="example_analysis")
        
    except Exception as e:
        logging.error(f"Error rendering example analysis chart: {e}")
        st.error("Fehler beim Erstellen des Beispielanalysecharts.")

def render_sentence_structure_chart(structure: Dict[str, bool], sentence_idx: int) -> None:
    """Render sentence structure analysis chart."""
    try:
        structure_data = [
            {"Merkmal": key.replace("_present", ""), "Wert": 1} 
            for key, value in structure.items() if value
        ]
        
        if not structure_data:
            st.write("Keine besonderen Strukturmerkmale erkannt.")
            return
            
        structure_df = pd.DataFrame(structure_data)
        
        fig = px.bar(
            structure_df,
            x="Merkmal",
            y="Wert",
            color="Merkmal",
            title=f"Satzstruktur - Satz {sentence_idx + 1}",
            height=SMALL_CHART_HEIGHT
        )
        
        fig.update_layout(
            showlegend=False,
            yaxis=dict(showticklabels=False, title=""),
            xaxis_title=""
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"sentence_structure_{sentence_idx}")
        
    except Exception as e:
        logging.error(f"Error rendering sentence structure chart: {e}")
        st.error("Fehler beim Erstellen des Satzstrukturcharts.")

def render_adjusted_weights_chart(adjusted_df: pd.DataFrame, model_weight: float, 
                                linguistic_weight: float) -> None:
    """Render adjusted weights comparison chart."""
    try:
        fig = px.bar(
            adjusted_df,
            x="Emotion",
            y="Score",
            color="Gewichtung",
            barmode="group",
            title=f"Vergleich der Gewichtungen für den Beispielkommentar"
        )
        
        fig.update_layout(
            xaxis_title='Emotion',
            yaxis_title='Score',
            height=DEFAULT_CHART_HEIGHT
        )
        
        st.plotly_chart(fig, use_container_width=True, key="adjusted_weights")
        
    except Exception as e:
        logging.error(f"Error rendering adjusted weights chart: {e}")
        st.error("Fehler beim Erstellen des Gewichtungsvergleichscharts.")

# =====================================================================================
# CONTENT RENDERING FUNCTIONS
# =====================================================================================

def render_introduction() -> None:
    """Render introduction section."""
    st.subheader("Emotionsmodell-Vergleich: KI-Modell vs. Linguistische Analyse")
    
    st.markdown("""
    Dieser Tab vergleicht zwei Ansätze zur Emotionserkennung in Texten:
    
    1. **Modellbasierte Emotionserkennung**: Nutzt das vortrainierte `RoBERTa`-Modell (`visegradmedia-emotion/Emotion_RoBERTa_german6_v7`), das auf deutschen Texten für die Erkennung von sechs Emotionen trainiert wurde.
    
    2. **Linguistische Emotionserkennung**: Ein regelbasierter Ansatz, der Schlüsselwörter, Satzstrukturen, Negationen und Verstärkungswörter analysiert.
    
    Die App kombiniert beide Ansätze mit einer **gewichteten Kombination (70% Modell, 30% Linguistisch)** für präzisere Ergebnisse.
    """)

def render_approach_details() -> None:
    """Render detailed information about both approaches."""
    st.write("## 2. Funktionsweise der Erkennungsansätze")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Modellbasierte Emotionserkennung
        
        - **Modell**: `visegradmedia-emotion/Emotion_RoBERTa_german6_v7`
        - **Architektur**: RoBERTa (Robustly Optimized BERT)
        - **Training**: Feinabgestimmt auf deutsche Texte
        - **Emotionen**: 6 Kategorien
        - **Gewichtung**: 70% im Gesamtergebnis
        
        #### Vorteile:
        - Kontextverständnis durch Deep Learning
        - Erkennt implizite Emotionen
        - Berücksichtigt Satzsemantik
        - Weniger anfällig für einzelne Wörter
        """)
    
    with col2:
        st.markdown("""
        ### Linguistische Emotionserkennung
        
        - **Ansatz**: Regelbasierte Textanalyse
        - **Methodik**: Wortlisten + Satzstrukturanalyse
        - **Schwerpunkt**: Explizite Emotionsausdrücke
        - **Besonderheiten**: Berücksichtigt Negationen, Verstärkungen
        - **Gewichtung**: 30% im Gesamtergebnis
        
        #### Vorteile:
        - Transparenter Prozess
        - Berücksichtigt sprachliche Eigenheiten
        - Erkennt Satzstrukturen (Fragen, Ausrufe)
        - Explizite Negationserkennung
        """)
    
    # Emotionskonzepte erklären
    st.write("### 🎯 Emotionskonzepte verstehen")
    
    st.markdown("""
    **Wichtige Unterscheidung der Emotionskategorien:**
    
    | **Kategorie** | **Bedeutung** | **Beispiel** |
    |---------------|---------------|--------------|
    | **"neutral"** | 🔵 *Echte Emotion: Sachlichkeit, emotionale Neutralität* | *"Das Meeting findet um 14:00 statt."* |
    | **"none of them"** | ⚪ *Nicht-Einordnung: Keine der anderen Emotionen* | *"Hmm, schwer zu sagen..."* |
    | **"surprise"** | 😮 *Grundemotion: Überraschung, Erstaunen* | *"Wow, das hätte ich nicht erwartet!"* |
    
    **→ "Neutral" ist eine eigenständige, wertvolle Emotionskategorie, nicht nur Abwesenheit von Emotion!**
    """)

def render_weighted_combination_explanation() -> None:
    """Render explanation of weighted combination approach."""
    st.write("## 4. Gewichteter Kombinationsansatz (70% Modell + 30% Linguistisch)")
    
    st.markdown("""
    Die App kombiniert beide Erkennungsansätze zu einem Gesamtergebnis:
    
    ```python
    gewichteter_score = modell_score * 0.7 + linguistisch_score * 0.3
    ```
    
    Dies führt zu robusteren Ergebnissen durch:
    - Nutzung der Stärken beider Ansätze
    - Ausgleich der jeweiligen Schwächen
    - Bessere Erkennung von impliziten und expliziten Emotionen
    """)

def render_comparison_table() -> None:
    """Render comparison table of approaches."""
    st.write("## 6. Vergleich: Vor- und Nachteile der Ansätze")
    
    comparison_data = {
        "Kriterium": [
            "Kontextverständnis", "Negationserkennung", "Implizite Emotionen", 
            "Explizite Emotionen", "Transparenz", "Trainingsaufwand",
            "Anpassbarkeit", "Sprachspezifische Nuancen", "Rechenaufwand", "Emotionsübergänge"
        ],
        "Modell": [
            "Sehr gut", "Gut", "Sehr gut", "Gut", "Niedrig (Black Box)",
            "Hoch", "Aufwändig", "Modellabhängig", "Hoch", "Mittel"
        ],
        "Linguistisch": [
            "Begrenzt", "Sehr gut", "Begrenzt", "Sehr gut", "Hoch (Regelbasiert)",
            "Niedrig", "Einfach", "Sehr gut", "Niedrig", "Gut"
        ],
        "Kombiniert": [
            "Sehr gut", "Sehr gut", "Sehr gut", "Sehr gut", "Mittel",
            "Mittel", "Mittel", "Sehr gut", "Mittel", "Sehr gut"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    
    def color_values(val):
        """Apply color coding to comparison values."""
        return EVALUATION_COLORS.get(val, "")
    
    st.dataframe(
        comparison_df.style.applymap(
            color_values, 
            subset=["Modell", "Linguistisch", "Kombiniert"]
        )
    )

def render_conclusion() -> None:
    """Render conclusion section."""
    st.write("## 8. Fazit")
    st.markdown("""
    Die Kombination beider Ansätze bietet signifikante Vorteile:
    
    - **Erhöhte Genauigkeit**: Durch Kombination der Stärken beider Methoden.
    - **Bessere Robustheit**: Linguistische Analyse fängt Schwächen des Modells auf und umgekehrt.
    - **Transparenz und Kontext**: Verbindet die Transparenz regelbasierter Systeme mit der Kontextfähigkeit von Deep Learning.
    - **Differenzierte Analyseergebnisse**: Ermöglicht detailliertere Einblicke in emotionale Strukturen.
    
    Die optimale Gewichtung ist anwendungsspezifisch und kann experimentell ermittelt werden. Für diese App wurde eine Standardgewichtung von 70% Modell und 30% linguistische Analyse gewählt, diese kann jedoch angepasst werden, um bessere Ergebnisse für spezifische Anwendungsfälle zu erzielen.
    """)

# =====================================================================================
# SECTION HANDLERS
# =====================================================================================

def handle_main_comparison(df: pd.DataFrame, emotion_columns: List[str]) -> None:
    """Handle main comparison section."""
    st.write("## 1. Vergleich der Erkennungsansätze")
    
    try:
        comparison_data = calculate_emotion_counts(df, emotion_columns)
        if not comparison_data:
            st.warning("Keine Vergleichsdaten verfügbar.")
            return
            
        comparison_df = pd.DataFrame(comparison_data)
        render_main_comparison_chart(comparison_df)
        
    except Exception as e:
        logging.error(f"Error in main comparison section: {e}")
        st.error("Fehler beim Erstellen des Hauptvergleichs.")

def handle_weighted_approach(df: pd.DataFrame, emotion_columns: List[str], 
                           config: EmotionComparisonConfig) -> None:
    """Handle weighted approach section."""
    render_weighted_combination_explanation()
    
    try:
        all_scores_data = calculate_weighted_scores(df, emotion_columns, config)
        if not all_scores_data:
            st.warning("Keine Gewichtungsdaten verfügbar.")
            return
            
        all_scores_df = pd.DataFrame(all_scores_data)
        render_weighted_approach_chart(all_scores_df)
        
    except Exception as e:
        logging.error(f"Error in weighted approach section: {e}")
        st.error("Fehler beim Erstellen der gewichteten Analyse.")

def handle_example_analysis(df: pd.DataFrame, emotion_columns: List[str], 
                          config: EmotionComparisonConfig) -> Optional[int]:
    """Handle example analysis section."""
    st.write("## 5. Beispielanalyse eines Kommentars")
    
    try:
        comment_options = get_comment_previews(df, config.preview_length)
        if not comment_options:
            st.warning("Keine Kommentare für die Beispielanalyse verfügbar.")
            return None
            
        selected_preview = st.selectbox(
            "Wähle einen Kommentar für die Analyse aus:",
            options=list(comment_options.keys()),
            key="comment_selection"
        )
        
        example_idx = comment_options[selected_preview]
        example_comment = df.loc[example_idx, "clean_text"]
        
        st.subheader("Beispielkommentar")
        st.info(example_comment)
        
        st.subheader("Emotionsanalyse")
        
        example_data = calculate_example_scores(df, example_idx, emotion_columns, config)
        if not example_data:
            st.warning("Keine Beispieldaten verfügbar.")
            return example_idx
            
        example_df = pd.DataFrame(example_data)
        render_example_analysis_chart(example_df)
        
        # Display dominant emotion
        if "dominant_emotion" in df.columns:
            dominant_emotion = df.loc[example_idx, "dominant_emotion"]
            st.success(f"Die dominante Emotion für diesen Kommentar ist: **{dominant_emotion}**")
        
        # Detailed linguistic analysis
        handle_linguistic_analysis_details(example_comment)
        
        return example_idx
        
    except Exception as e:
        logging.error(f"Error in example analysis section: {e}")
        st.error("Fehler bei der Beispielanalyse.")
        return None

def handle_linguistic_analysis_details(example_comment: str) -> None:
    """Handle detailed linguistic analysis section."""
    st.subheader("Linguistische Analysedetails")
    
    try:
        sentences = split_text_into_sentences(example_comment)
        
        if not sentences:
            st.write("Keine Sätze für die Analyse gefunden.")
            return
            
        for i, sentence in enumerate(sentences):
            st.write(f"**Satz {i+1}:** {sentence}")
            
            structure = analyze_sentence_structure(sentence)
            render_sentence_structure_chart(structure, i)
            
    except Exception as e:
        logging.error(f"Error in linguistic analysis details: {e}")
        st.error("Fehler bei der linguistischen Detailanalyse.")

def handle_weight_adjustment(df: pd.DataFrame, emotion_columns: List[str], 
                           example_idx: Optional[int]) -> None:
    """Handle weight adjustment section."""
    st.write("## 7. Gewichtung anpassen")
    st.write("Sie können experimentieren, wie sich verschiedene Gewichtungen der beiden Ansätze auf die Ergebnisse auswirken:")
    
    try:
        model_weight = st.slider(
            "Gewichtung des KI-Modells",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_MODEL_WEIGHT,
            step=0.05,
            key="model_weight_slider"
        )
        
        linguistic_weight = 1.0 - model_weight
        
        st.write(f"Aktuelle Gewichtung: **{model_weight:.0%} Modell**, **{linguistic_weight:.0%} Linguistisch**")
        
        st.info("""
        Um diese Gewichtung in der gesamten App zu verwenden, müssten Sie die Gewichtungsfaktoren in der Datei `emotion_analysis.py` entsprechend anpassen.
        
        Aktuell wird die Gewichtung nur in dieser Visualisierung geändert, nicht in der tatsächlichen Analyse.
        """)
        
        # Show impact of adjusted weighting if example is available
        if example_idx is not None:
            handle_adjusted_weighting_impact(df, emotion_columns, example_idx, model_weight, linguistic_weight)
            
    except Exception as e:
        logging.error(f"Error in weight adjustment section: {e}")
        st.error("Fehler bei der Gewichtungsanpassung.")

def handle_adjusted_weighting_impact(df: pd.DataFrame, emotion_columns: List[str], 
                                   example_idx: int, model_weight: float, 
                                   linguistic_weight: float) -> None:
    """Handle adjusted weighting impact visualization."""
    st.write("### Auswirkung der angepassten Gewichtung auf den Beispielkommentar")
    
    try:
        adjusted_example_data = []
        new_weighted_scores = {}
        
        for emotion in emotion_columns:
            if emotion in df.columns and f"{emotion}_linguistic" in df.columns:
                model_score = df.loc[example_idx, emotion]
                ling_score = df.loc[example_idx, f"{emotion}_linguistic"]
                
                new_weighted_score = model_score * model_weight + ling_score * linguistic_weight
                new_weighted_scores[emotion] = new_weighted_score
                
                adjusted_example_data.extend([
                    {
                        "Emotion": emotion,
                        "Score": new_weighted_score,
                        "Gewichtung": f"{model_weight:.0%} Modell, {linguistic_weight:.0%} Linguistisch"
                    },
                    {
                        "Emotion": emotion,
                        "Score": model_score * DEFAULT_MODEL_WEIGHT + ling_score * DEFAULT_LINGUISTIC_WEIGHT,
                        "Gewichtung": "70% Modell, 30% Linguistisch (Standard)"
                    }
                ])
        
        if adjusted_example_data:
            adjusted_df = pd.DataFrame(adjusted_example_data)
            render_adjusted_weights_chart(adjusted_df, model_weight, linguistic_weight)
            
            # Compare dominant emotions
            if new_weighted_scores and "dominant_emotion" in df.columns:
                new_dominant_emotion = max(new_weighted_scores.items(), key=lambda x: x[1])[0]
                old_dominant_emotion = df.loc[example_idx, "dominant_emotion"]
                
                if new_dominant_emotion != old_dominant_emotion:
                    st.warning(f"""
                    Mit der neuen Gewichtung ändert sich die dominante Emotion von **{old_dominant_emotion}** zu **{new_dominant_emotion}**!
                    
                    Dies zeigt, wie stark die Gewichtung das Endergebnis beeinflussen kann.
                    """)
                else:
                    st.success(f"""
                    Die dominante Emotion **{new_dominant_emotion}** bleibt auch mit der neuen Gewichtung gleich.
                    
                    Die Emotion ist in diesem Fall robust gegenüber Änderungen in der Gewichtung.
                    """)
        
    except Exception as e:
        logging.error(f"Error in adjusted weighting impact: {e}")
        st.error("Fehler bei der Gewichtungsauswirkungsanalyse.")

# =====================================================================================
# MAIN API FUNCTION
# =====================================================================================

# =====================================================================================
# UTILITY FUNCTIONS
# =====================================================================================

def detect_available_emotions(df: pd.DataFrame) -> List[str]:
    """
    Automatically detect available emotion columns in DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        List of available emotion column names
        
    Note:
        Unterscheidet zwischen verschiedenen Emotionskonzepten:
        - "neutral" = Echte Emotion (emotionale Neutralität, sachlicher Inhalt)
        - "none of them" = Nicht-Einordnung (keine der anderen Emotionen trifft zu)
        - "surprise" = Grundemotion (Überraschung, Erstaunen)
        
        Beide Konzepte sind valid und werden automatisch erkannt.
    """
    # Common emotion names to check for
    # Kategorien nach Bedeutung sortiert:
    
    # 1. Hauptemotionen (Ekman's Basisemotionen)
    basic_emotions = ['anger', 'fear', 'disgust', 'sadness', 'joy', 'surprise']
    
    # 2. Neutrale Emotionen (echte emotionale Zustände)
    neutral_emotions = ['neutral']  # Sachlich, emotionslos, ausgewogen
    
    # 3. Nicht-Einordnung (technische Kategorien)
    non_classification = ['none of them']  # Keine der anderen Emotionen
    
    # 4. Erweiterte Emotionen
    extended_emotions = ['happiness', 'love', 'contempt']
    
    possible_emotions = basic_emotions + neutral_emotions + non_classification + extended_emotions
    
    # Find emotions that exist as columns in the DataFrame
    available_emotions = [emotion for emotion in possible_emotions if emotion in df.columns]
    
    # If none found, try to find any column that could be an emotion
    if not available_emotions:
        # Look for columns that have corresponding linguistic columns
        potential_emotions = []
        for col in df.columns:
            if f"{col}_linguistic" in df.columns:
                potential_emotions.append(col)
        available_emotions = potential_emotions
    
    return available_emotions

def display_emotion_comparison(df: pd.DataFrame, emotion_classifier: Any) -> None:
    """
    Zeigt einen detaillierten Vergleich zwischen modellbasierter und linguistischer Emotionserkennung
    
    Args:
        df: DataFrame mit den Kommentaren und Emotionsdaten
        emotion_classifier: Das Emotions-Erkennungsmodell
    """
    try:
        # Configuration
        config = EmotionComparisonConfig()
        
        # Dynamic emotion detection - use what's actually available
        emotion_columns = detect_available_emotions(df)
        expected_emotions = list(EMOTION_LABEL_MAP.values())
        
        # Debug info für Entwicklung - zeige verfügbare Spalten
        with st.expander("🔍 Debug Info - DataFrame Spalten", expanded=False):
            st.write(f"**Erkannte Emotions-Spalten ({len(emotion_columns)}):** {emotion_columns}")
            st.write(f"**Erwartete Emotions-Spalten:** {expected_emotions}")
            
            missing_from_expected = [e for e in expected_emotions if e not in emotion_columns]
            additional_found = [e for e in emotion_columns if e not in expected_emotions]
            
            if missing_from_expected:
                st.write(f"**Fehlende erwartete Emotionen:** {missing_from_expected}")
            if additional_found:
                st.write(f"**Zusätzlich gefundene Emotionen:** {additional_found}")
            
            st.write(f"**DataFrame Shape:** {df.shape}")
            st.write(f"**Alle DataFrame Spalten:** {list(df.columns)}")
        
        # Validierung
        if not emotion_columns:
            st.error("❌ Keine Emotionsdaten im DataFrame gefunden!")
            st.info("💡 **Tipp:** Stellen Sie sicher, dass der DataFrame Spalten wie 'anger', 'joy', etc. enthält.")
            return
        
        if len(df) == 0:
            st.warning("Keine Daten für die Analyse verfügbar.")
            return
        
        # Informative Meldung über gefundene Emotionen
        if len(emotion_columns) != len(expected_emotions):
            st.info(f"""
            ℹ️ **Emotionsdaten-Info:**
            
            **Gefundene Emotionen ({len(emotion_columns)}):** {', '.join(emotion_columns)}
            
            **Hinweis:** Die Analyse arbeitet mit den verfügbaren Emotionsspalten. 
            Unterschiede zu erwarteten Emotionen sind normal und beeinträchtigen die Funktionalität nicht.
            """)
            
            # Spezielle Erklärung für "neutral" vs "none of them"
            if 'neutral' in emotion_columns and 'none of them' not in emotion_columns:
                st.success("""
                ✅ **Erkanntes 7-Emotionen-System mit "neutral":**
                
                Ihr System verwendet eine **erweiterte Emotionsklassifikation** mit "neutral" als **eigenständiger Emotion**.
                
                - **"neutral"** = Sachlicher, emotionsloser Inhalt (z.B. "Das Wetter ist 20°C")
                - **Nicht "none of them"** = Bedeutung: "Keine der anderen Emotionen" (technische Nicht-Einordnung)
                
                **Das ist eine hochwertige, differenzierte Emotionserkennung!** 🎯
                """)
        else:
            st.success(f"✅ **Alle Emotionsdaten verfügbar:** {', '.join(emotion_columns)}")
        
        # Prüfe ob linguistische Daten verfügbar sind
        linguistic_columns = [f"{emotion}_linguistic" for emotion in emotion_columns]
        has_linguistic_data = any(col in df.columns for col in linguistic_columns)
        available_linguistic = [col for col in linguistic_columns if col in df.columns]
        
        if not has_linguistic_data:
            st.warning("""
            ⚠️ **Wichtiger Hinweis:** Keine linguistischen Emotionsdaten gefunden!
            
            Der Vergleich wird nur mit den verfügbaren Modelldaten durchgeführt.
            Für den vollständigen Vergleich sollten auch die `*_linguistic` Spalten vorhanden sein.
            """)
        else:
            st.success(f"✅ **Linguistische Daten verfügbar:** {len(available_linguistic)} von {len(emotion_columns)} Emotionen")

        
        # Render sections
        render_introduction()
        
        handle_main_comparison(df, emotion_columns)
        
        render_approach_details()
        
        st.write("## 3. Emotionale Wortlisten für linguistische Analyse")
        st.write("Die linguistische Analyse verwendet umfangreiche Wortlisten für jede Emotion (hier gekürzt dargestellt):")
        render_keyword_treemap()
        
        handle_weighted_approach(df, emotion_columns, config)
        
        example_idx = handle_example_analysis(df, emotion_columns, config)
        
        render_comparison_table()
        
        handle_weight_adjustment(df, emotion_columns, example_idx)
        
        render_conclusion()
        
    except Exception as e:
        logging.error(f"Error in display_emotion_comparison: {e}")
        st.error("Ein unerwarteter Fehler ist bei der Emotionsvergleichsanalyse aufgetreten.")
        st.error(f"Details: {str(e)}")

# =====================================================================================
# BACKWARDS COMPATIBILITY
# =====================================================================================

# Export main function for backwards compatibility
__all__ = ['display_emotion_comparison']