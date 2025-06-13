import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

# =============================================================================
# KONSTANTEN UND KONFIGURATION
# =============================================================================

class TopicLabelingConstants:
    """Zentrale Konstanten für Topic-Labeling"""
    
    # Anzahl der Top-Wörter pro Topic
    DEFAULT_TOP_WORDS = 10
    MAX_TOPIC_WORDS = 20
    MIN_TOPIC_WORDS = 5
    
    # Standard-Labels
    OUTLIER_LABEL = "Sonstige Themen"
    UNKNOWN_LABEL = "Unbekanntes Thema"
    GENERIC_SECONDARY = "Themen"
    
    # DataFrame-Spalten
    TOPIC_COLUMN = "topic"
    TOPIC_LABEL_COLUMN = "topic_label"
    
    # Logging
    LOGGER_NAME = "topic_labeling"


class TermCategory(Enum):
    """Kategorien für Term-Priorisierung"""
    IMPORTANT = "important"
    COMMON_NOUNS = "common_nouns"
    GENERIC = "generic"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class TopicInfo:
    """Informationen über ein einzelnes Topic"""
    topic_id: int
    words: List[Tuple[str, float]]
    count: int
    label: Optional[str] = None


@dataclass
class LabelGenerationConfig:
    """Konfiguration für Label-Generierung"""
    n_top_words: int = TopicLabelingConstants.DEFAULT_TOP_WORDS
    use_important_terms: bool = True
    use_common_nouns: bool = True
    separator: str = " & "
    capitalize_terms: bool = True
    
    # Term-Listen (konfigurierbar)
    important_terms: List[str] = field(default_factory=lambda: [
        "Lobo", "KI", "ChatGPT", "Schule", "Lehrer", "Bildung", "Politik", 
        "Medien", "Technik", "Experten", "Intelligenz", "Digitalisierung",
        "Mathe", "Internet", "Wissen", "Kompetenz", "Diskussion", "Regierung",
        "Precht", "Data", "Science", "Informatik", "Moral", "Freiheit",
        "Jugend", "Kinder", "Zeit", "Sprache", "Integration", "Verstehen",
        "Lanz", "Kritik", "Argumente", "Ideen", "Grammatik", "Menschsein"
    ])
    
    common_nouns: List[str] = field(default_factory=lambda: [
        "Medien", "Lehrer", "Witz", "Menschsein", "Technik", "Regierung", 
        "Bildungssystem", "Digitalisierung", "Argumente", "Fachbegriffe", 
        "Freiheit", "Probleme", "Wissen", "Jobs", "Integration", "Kritik", 
        "Zeit", "Personen", "Kompetenz", "Auftritt", "Informatik", 
        "Verständnis", "Gäste", "Sekunden", "Freunde", "Grammatik", 
        "Maschinen", "Urteilsvermögen", "Verständnis"
    ])


@dataclass
class TopicLabelingResults:
    """Ergebnisse der Topic-Label-Generierung"""
    labels: Dict[int, str]
    processed_topics: int
    skipped_topics: int
    config_used: LabelGenerationConfig
    processing_time: Optional[float] = None


# =============================================================================
# SPEZIALISIERTE KOMPONENTEN
# =============================================================================

class TermAnalyzer:
    """Analysiert und kategorisiert Terms für Label-Generierung"""
    
    def __init__(self, config: LabelGenerationConfig):
        self.config = config
        self.logger = logging.getLogger(TopicLabelingConstants.LOGGER_NAME)
    
    def find_primary_term(self, words: List[str]) -> Optional[str]:
        """Findet den primären Term basierend auf wichtigen Begriffen
        
        Args:
            words: Liste der Topic-Wörter
            
        Returns:
            Primärer Begriff oder None
        """
        try:
            if not self.config.use_important_terms:
                return None
                
            words_lower = [w.lower() for w in words]
            
            for term in self.config.important_terms:
                if term.lower() in words_lower:
                    return self._format_term(term)
                    
            return None
            
        except Exception as e:
            self.logger.warning(f"Fehler bei primärer Term-Suche: {e}")
            return None
    
    def find_secondary_term(self, words: List[str], primary_term: str) -> Optional[str]:
        """Findet den sekundären Term für das Label
        
        Args:
            words: Liste der Topic-Wörter
            primary_term: Bereits gewählter primärer Term
            
        Returns:
            Sekundärer Begriff oder None
        """
        try:
            all_priority_terms = []
            
            if self.config.use_common_nouns:
                all_priority_terms.extend(self.config.common_nouns)
            if self.config.use_important_terms:
                all_priority_terms.extend(self.config.important_terms)
            
            # Suche in Prioritäts-Terms
            for word in words:
                formatted_word = self._format_term(word)
                if (formatted_word != primary_term and 
                    formatted_word in all_priority_terms):
                    return formatted_word
            
            # Fallback: Nächstes verfügbares Wort
            for word in words:
                formatted_word = self._format_term(word)
                if formatted_word != primary_term:
                    return formatted_word
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Fehler bei sekundärer Term-Suche: {e}")
            return None
    
    def _format_term(self, term: str) -> str:
        """Formatiert einen Term nach Konfiguration"""
        return term.capitalize() if self.config.capitalize_terms else term


class LabelGenerator:
    """Generiert Topic-Labels basierend auf Term-Analyse"""
    
    def __init__(self, config: LabelGenerationConfig):
        self.config = config
        self.term_analyzer = TermAnalyzer(config)
        self.logger = logging.getLogger(TopicLabelingConstants.LOGGER_NAME)
    
    def generate_label_for_topic(self, topic_info: TopicInfo) -> str:
        """Generiert ein Label für ein einzelnes Topic
        
        Args:
            topic_info: Topic-Informationen
            
        Returns:
            Generiertes Label
        """
        try:
            if not topic_info.words:
                return f"Thema {topic_info.topic_id}"
            
            # Extrahiere Wörter (ohne Gewichte)
            words = [word for word, _ in topic_info.words[:self.config.n_top_words]]
            
            # Finde primären Term
            primary_term = self.term_analyzer.find_primary_term(words)
            if primary_term is None:
                primary_term = self.term_analyzer._format_term(words[0])
            
            # Finde sekundären Term
            secondary_term = self.term_analyzer.find_secondary_term(words, primary_term)
            if secondary_term is None:
                secondary_term = TopicLabelingConstants.GENERIC_SECONDARY
            
            return f"{primary_term}{self.config.separator}{secondary_term}"
            
        except Exception as e:
            self.logger.error(f"Fehler bei Label-Generierung für Topic {topic_info.topic_id}: {e}")
            return f"Thema {topic_info.topic_id}"


class TopicInfoExtractor:
    """Extrahiert Topic-Informationen aus BERTopic-Modellen"""
    
    def __init__(self):
        self.logger = logging.getLogger(TopicLabelingConstants.LOGGER_NAME)
    
    def extract_topic_infos(
        self, 
        topic_model: Any, 
        n_topics: Optional[int] = None
    ) -> List[TopicInfo]:
        """Extrahiert Topic-Informationen aus BERTopic-Modell
        
        Args:
            topic_model: BERTopic-Modell
            n_topics: Maximale Anzahl Topics (None für alle)
            
        Returns:
            Liste der Topic-Informationen
        """
        try:
            topic_info_df = topic_model.get_topic_info()
            sorted_topics = topic_info_df.sort_values(by="Count", ascending=False)
            
            # Filtere Outlier-Topic (-1) raus
            valid_topics = sorted_topics[sorted_topics["Topic"] != -1]
            
            if n_topics is not None:
                valid_topics = valid_topics.head(n_topics)
            
            topic_infos = []
            
            for _, row in valid_topics.iterrows():
                topic_id = int(row["Topic"])
                count = int(row["Count"])
                
                # Hole Top-Wörter für das Topic
                top_words = topic_model.get_topic(topic_id)
                
                topic_info = TopicInfo(
                    topic_id=topic_id,
                    words=top_words if top_words else [],
                    count=count
                )
                
                topic_infos.append(topic_info)
            
            return topic_infos
            
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren der Topic-Informationen: {e}")
            return []


# =============================================================================
# MANAGER-KLASSE
# =============================================================================

class TopicLabelManager:
    """Zentraler Manager für Topic-Labeling-Operationen"""
    
    def __init__(self, config: Optional[LabelGenerationConfig] = None):
        self.config = config or LabelGenerationConfig()
        self.extractor = TopicInfoExtractor()
        self.generator = LabelGenerator(self.config)
        self.logger = logging.getLogger(TopicLabelingConstants.LOGGER_NAME)
    
    def generate_smart_labels(
        self, 
        topic_model: Any, 
        n_topics: Optional[int] = None
    ) -> TopicLabelingResults:
        """Generiert intelligente Topic-Labels
        
        Args:
            topic_model: BERTopic-Modell
            n_topics: Maximale Anzahl Topics
            
        Returns:
            Ergebnisse der Label-Generierung
        """
        import time
        start_time = time.time()
        
        try:
            # Extrahiere Topic-Informationen
            topic_infos = self.extractor.extract_topic_infos(topic_model, n_topics)
            
            labels = {}
            processed_topics = 0
            skipped_topics = 0
            
            # Behandle Outlier-Topic separat
            labels[-1] = TopicLabelingConstants.OUTLIER_LABEL
            
            # Generiere Labels für alle Topics
            for topic_info in topic_infos:
                try:
                    label = self.generator.generate_label_for_topic(topic_info)
                    labels[topic_info.topic_id] = label
                    processed_topics += 1
                    
                except Exception as e:
                    self.logger.warning(f"Überspringe Topic {topic_info.topic_id}: {e}")
                    skipped_topics += 1
            
            processing_time = time.time() - start_time
            
            return TopicLabelingResults(
                labels=labels,
                processed_topics=processed_topics,
                skipped_topics=skipped_topics,
                config_used=self.config,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Fehler bei Label-Generierung: {e}")
            return TopicLabelingResults(
                labels={-1: TopicLabelingConstants.OUTLIER_LABEL},
                processed_topics=0,
                skipped_topics=0,
                config_used=self.config
            )
    
    def apply_labels_to_dataframe(
        self, 
        df: pd.DataFrame, 
        topic_labels: Dict[int, str]
    ) -> pd.DataFrame:
        """Wendet Topic-Labels auf DataFrame an
        
        Args:
            df: DataFrame mit Kommentaren
            topic_labels: Dictionary mit Topic-Labels
            
        Returns:
            DataFrame mit Topic-Labels
        """
        try:
            df_copy = df.copy()
            
            if TopicLabelingConstants.TOPIC_COLUMN in df_copy.columns:
                df_copy[TopicLabelingConstants.TOPIC_LABEL_COLUMN] = (
                    df_copy[TopicLabelingConstants.TOPIC_COLUMN]
                    .map(lambda x: topic_labels.get(x, TopicLabelingConstants.UNKNOWN_LABEL))
                )
            else:
                self.logger.warning(f"Spalte '{TopicLabelingConstants.TOPIC_COLUMN}' nicht im DataFrame gefunden")
                df_copy[TopicLabelingConstants.TOPIC_LABEL_COLUMN] = TopicLabelingConstants.UNKNOWN_LABEL
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden der Labels: {e}")
            df_copy = df.copy()
            df_copy[TopicLabelingConstants.TOPIC_LABEL_COLUMN] = TopicLabelingConstants.UNKNOWN_LABEL
            return df_copy


# =============================================================================
# UI-KOMPONENTEN
# =============================================================================

def render_topic_labeling_config() -> LabelGenerationConfig:
    """Rendert Konfiguration für Topic-Labeling"""
    st.subheader("🏷️ Topic-Labeling Konfiguration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_top_words = st.slider(
            "Anzahl Top-Wörter pro Topic",
            min_value=TopicLabelingConstants.MIN_TOPIC_WORDS,
            max_value=TopicLabelingConstants.MAX_TOPIC_WORDS,
            value=TopicLabelingConstants.DEFAULT_TOP_WORDS
        )
        
        use_important_terms = st.checkbox("Wichtige Begriffe priorisieren", value=True)
        use_common_nouns = st.checkbox("Häufige Substantive verwenden", value=True)
    
    with col2:
        separator = st.text_input("Label-Trenner", value=" & ")
        capitalize_terms = st.checkbox("Begriffe großschreiben", value=True)
    
    return LabelGenerationConfig(
        n_top_words=n_top_words,
        use_important_terms=use_important_terms,
        use_common_nouns=use_common_nouns,
        separator=separator,
        capitalize_terms=capitalize_terms
    )


def render_topic_labeling_results(results: TopicLabelingResults) -> None:
    """Rendert Ergebnisse der Topic-Label-Generierung"""
    st.subheader("📊 Label-Generierung Ergebnisse")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Verarbeitete Topics", results.processed_topics)
    
    with col2:
        st.metric("Übersprungene Topics", results.skipped_topics)
    
    with col3:
        if results.processing_time:
            st.metric("Verarbeitungszeit", f"{results.processing_time:.2f}s")
    
    # Zeige generierte Labels
    if results.labels:
        st.subheader("🏷️ Generierte Labels")
        
        # Sortiere nach Topic-ID (aber -1 zuerst)
        sorted_items = sorted(
            results.labels.items(),
            key=lambda x: (x[0] if x[0] != -1 else float('-inf'))
        )
        
        for topic_id, label in sorted_items:
            if topic_id == -1:
                st.info(f"**Topic {topic_id}:** {label}")
            else:
                st.write(f"**Topic {topic_id}:** {label}")


# =============================================================================
# BACKWARD COMPATIBILITY - ALTE API
# =============================================================================

def generate_smart_topic_labels(topic_model, n_topics=None):
    """
    BACKWARD COMPATIBILITY: Erzeugt intelligentere Topic-Labels
    
    Args:
        topic_model: Das BERTopic-Modell
        n_topics: Anzahl der Topics (falls None, werden alle verwendet)
        
    Returns:
        Dictionary mit Topic-IDs und Labels
    """
    manager = TopicLabelManager()
    results = manager.generate_smart_labels(topic_model, n_topics)
    return results.labels


def apply_topic_labels(df, topic_labels):
    """
    BACKWARD COMPATIBILITY: Wendet Topic-Labels auf den DataFrame an
    
    Args:
        df: DataFrame mit den Kommentaren
        topic_labels: Dictionary mit Topic-IDs und Labels
        
    Returns:
        DataFrame mit einer zusätzlichen Spalte 'topic_label'
    """
    manager = TopicLabelManager()
    return manager.apply_labels_to_dataframe(df, topic_labels)


# =============================================================================
# ERWEITERTE API
# =============================================================================

def create_topic_label_manager(config: Optional[LabelGenerationConfig] = None) -> TopicLabelManager:
    """Factory-Funktion für TopicLabelManager"""
    return TopicLabelManager(config)


def create_custom_labeling_config(
    important_terms: Optional[List[str]] = None,
    common_nouns: Optional[List[str]] = None,
    **kwargs
) -> LabelGenerationConfig:
    """Erstellt benutzerdefinierte Labeling-Konfiguration"""
    config = LabelGenerationConfig(**kwargs)
    
    if important_terms is not None:
        config.important_terms = important_terms
    
    if common_nouns is not None:
        config.common_nouns = common_nouns
    
    return config