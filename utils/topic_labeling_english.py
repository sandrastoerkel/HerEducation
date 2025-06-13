import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class TopicLabelingEnglishConstants:
    """Central constants for English Topic-Labeling"""
    
    # Number of top words per topic
    DEFAULT_TOP_WORDS = 10
    MAX_TOPIC_WORDS = 20
    MIN_TOPIC_WORDS = 5
    
    # Default labels
    OUTLIER_LABEL = "Other Topics"
    UNKNOWN_LABEL = "Unknown Topic"
    GENERIC_SECONDARY = "Topics"
    
    # DataFrame columns
    TOPIC_COLUMN = "topic"
    TOPIC_LABEL_COLUMN = "topic_label"
    
    # Logging
    LOGGER_NAME = "topic_labeling_english"


class EnglishTermCategory(Enum):
    """Categories for English term prioritization"""
    IMPORTANT = "important"
    COMMON_NOUNS = "common_nouns"
    GENERIC = "generic"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class EnglishTopicInfo:
    """Information about a single topic"""
    topic_id: int
    words: List[Tuple[str, float]]
    count: int
    label: Optional[str] = None


@dataclass
class EnglishLabelGenerationConfig:
    """Configuration for English label generation"""
    n_top_words: int = TopicLabelingEnglishConstants.DEFAULT_TOP_WORDS
    use_important_terms: bool = True
    use_common_nouns: bool = True
    separator: str = " & "
    capitalize_terms: bool = True
    
    # English term lists (configurable and extended)
    important_terms: List[str] = field(default_factory=lambda: [
        "AI", "ChatGPT", "GPT", "School", "Teacher", "Education", "Politics", 
        "Media", "Technology", "Tech", "Expert", "Intelligence", "Digital",
        "Math", "Internet", "Knowledge", "Discussion", "Government",
        "Data", "Science", "Computer", "Moral", "Freedom",
        "Youth", "Children", "Time", "Language", "Integration", "Understanding",
        "Criticism", "Arguments", "Ideas", "Grammar", "Human", "Humanity",
        "Learning", "Student", "University", "College", "Research", "Study",
        "Algorithm", "Machine", "Automation", "Robot", "Future", "Innovation",
        "Society", "Social", "Culture", "Ethics", "Philosophy", "Psychology",
        "Communication", "Information", "News", "Analysis", "Opinion", "Debate",
        "Algorithm", "Programming", "Coding", "Software", "Hardware", "Network",
        "Internet", "Web", "Platform", "App", "Application", "System",
        "Database", "Cloud", "Security", "Privacy", "Blockchain", "Cryptocurrency"
    ])
    
    common_nouns: List[str] = field(default_factory=lambda: [
        "Media", "Teacher", "Technology", "Government", "System", "Digital", 
        "Arguments", "Terms", "Freedom", "Problems", "Knowledge", "Jobs", 
        "Integration", "Criticism", "Time", "People", "Competence", "Performance", 
        "Computer", "Understanding", "Guests", "Seconds", "Friends", "Grammar", 
        "Machines", "Judgment", "Analysis", "Students", "Learning", "Education",
        "Research", "Study", "Communication", "Information", "Society", "Culture",
        "Ethics", "Innovation", "Future", "Discussion", "Debate", "Opinion",
        "Content", "Platform", "Network", "Community", "Experience", "Process",
        "Method", "Approach", "Strategy", "Solution", "Challenge", "Opportunity",
        "Development", "Progress", "Growth", "Change", "Transformation", "Impact"
    ])


@dataclass
class EnglishTopicLabelingResults:
    """Results of English topic label generation"""
    labels: Dict[int, str]
    processed_topics: int
    skipped_topics: int
    config_used: EnglishLabelGenerationConfig
    processing_time: Optional[float] = None


# =============================================================================
# SPECIALIZED COMPONENTS
# =============================================================================

class EnglishTermAnalyzer:
    """Analyzes and categorizes English terms for label generation"""
    
    def __init__(self, config: EnglishLabelGenerationConfig):
        self.config = config
        self.logger = logging.getLogger(TopicLabelingEnglishConstants.LOGGER_NAME)
    
    def find_primary_term(self, words: List[str]) -> Optional[str]:
        """Finds primary term based on important English terms
        
        Args:
            words: List of topic words
            
        Returns:
            Primary term or None
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
            self.logger.warning(f"Error in primary term search: {e}")
            return None
    
    def find_secondary_term(self, words: List[str], primary_term: str) -> Optional[str]:
        """Finds secondary term for the label
        
        Args:
            words: List of topic words
            primary_term: Already chosen primary term
            
        Returns:
            Secondary term or None
        """
        try:
            all_priority_terms = []
            
            if self.config.use_common_nouns:
                all_priority_terms.extend(self.config.common_nouns)
            if self.config.use_important_terms:
                all_priority_terms.extend(self.config.important_terms)
            
            # Search in priority terms
            for word in words:
                formatted_word = self._format_term(word)
                if (formatted_word != primary_term and 
                    formatted_word in all_priority_terms):
                    return formatted_word
            
            # Fallback: Next available word
            for word in words:
                formatted_word = self._format_term(word)
                if formatted_word != primary_term:
                    return formatted_word
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error in secondary term search: {e}")
            return None
    
    def _format_term(self, term: str) -> str:
        """Formats a term according to configuration"""
        return term.capitalize() if self.config.capitalize_terms else term


class EnglishLabelGenerator:
    """Generates English topic labels based on term analysis"""
    
    def __init__(self, config: EnglishLabelGenerationConfig):
        self.config = config
        self.term_analyzer = EnglishTermAnalyzer(config)
        self.logger = logging.getLogger(TopicLabelingEnglishConstants.LOGGER_NAME)
    
    def generate_label_for_topic(self, topic_info: EnglishTopicInfo) -> str:
        """Generates a label for a single topic
        
        Args:
            topic_info: Topic information
            
        Returns:
            Generated label
        """
        try:
            if not topic_info.words:
                return f"Topic {topic_info.topic_id}"
            
            # Extract words (without weights)
            words = [word for word, _ in topic_info.words[:self.config.n_top_words]]
            
            # Find primary term
            primary_term = self.term_analyzer.find_primary_term(words)
            if primary_term is None:
                primary_term = self.term_analyzer._format_term(words[0])
            
            # Find secondary term
            secondary_term = self.term_analyzer.find_secondary_term(words, primary_term)
            if secondary_term is None:
                secondary_term = TopicLabelingEnglishConstants.GENERIC_SECONDARY
            
            return f"{primary_term}{self.config.separator}{secondary_term}"
            
        except Exception as e:
            self.logger.error(f"Error generating label for topic {topic_info.topic_id}: {e}")
            return f"Topic {topic_info.topic_id}"


class EnglishTopicInfoExtractor:
    """Extracts topic information from BERTopic models"""
    
    def __init__(self):
        self.logger = logging.getLogger(TopicLabelingEnglishConstants.LOGGER_NAME)
    
    def extract_topic_infos(
        self, 
        topic_model: Any, 
        n_topics: Optional[int] = None
    ) -> List[EnglishTopicInfo]:
        """Extracts topic information from BERTopic model
        
        Args:
            topic_model: BERTopic model
            n_topics: Maximum number of topics (None for all)
            
        Returns:
            List of topic information
        """
        try:
            topic_info_df = topic_model.get_topic_info()
            sorted_topics = topic_info_df.sort_values(by="Count", ascending=False)
            
            # Filter out outlier topic (-1)
            valid_topics = sorted_topics[sorted_topics["Topic"] != -1]
            
            if n_topics is not None:
                valid_topics = valid_topics.head(n_topics)
            
            topic_infos = []
            
            for _, row in valid_topics.iterrows():
                topic_id = int(row["Topic"])
                count = int(row["Count"])
                
                # Get top words for the topic
                top_words = topic_model.get_topic(topic_id)
                
                topic_info = EnglishTopicInfo(
                    topic_id=topic_id,
                    words=top_words if top_words else [],
                    count=count
                )
                
                topic_infos.append(topic_info)
            
            return topic_infos
            
        except Exception as e:
            self.logger.error(f"Error extracting topic information: {e}")
            return []


# =============================================================================
# MANAGER CLASS
# =============================================================================

class EnglishTopicLabelManager:
    """Central manager for English topic labeling operations"""
    
    def __init__(self, config: Optional[EnglishLabelGenerationConfig] = None):
        self.config = config or EnglishLabelGenerationConfig()
        self.extractor = EnglishTopicInfoExtractor()
        self.generator = EnglishLabelGenerator(self.config)
        self.logger = logging.getLogger(TopicLabelingEnglishConstants.LOGGER_NAME)
    
    def generate_smart_labels(
        self, 
        topic_model: Any, 
        n_topics: Optional[int] = None
    ) -> EnglishTopicLabelingResults:
        """Generates smart English topic labels
        
        Args:
            topic_model: BERTopic model
            n_topics: Maximum number of topics
            
        Returns:
            Results of label generation
        """
        import time
        start_time = time.time()
        
        try:
            # Extract topic information
            topic_infos = self.extractor.extract_topic_infos(topic_model, n_topics)
            
            labels = {}
            processed_topics = 0
            skipped_topics = 0
            
            # Handle outlier topic separately
            labels[-1] = TopicLabelingEnglishConstants.OUTLIER_LABEL
            
            # Generate labels for all topics
            for topic_info in topic_infos:
                try:
                    label = self.generator.generate_label_for_topic(topic_info)
                    labels[topic_info.topic_id] = label
                    processed_topics += 1
                    
                except Exception as e:
                    self.logger.warning(f"Skipping topic {topic_info.topic_id}: {e}")
                    skipped_topics += 1
            
            processing_time = time.time() - start_time
            
            return EnglishTopicLabelingResults(
                labels=labels,
                processed_topics=processed_topics,
                skipped_topics=skipped_topics,
                config_used=self.config,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Error in label generation: {e}")
            return EnglishTopicLabelingResults(
                labels={-1: TopicLabelingEnglishConstants.OUTLIER_LABEL},
                processed_topics=0,
                skipped_topics=0,
                config_used=self.config
            )
    
    def apply_labels_to_dataframe(
        self, 
        df: pd.DataFrame, 
        topic_labels: Dict[int, str]
    ) -> pd.DataFrame:
        """Applies topic labels to DataFrame
        
        Args:
            df: DataFrame with comments
            topic_labels: Dictionary with topic labels
            
        Returns:
            DataFrame with topic labels
        """
        try:
            df_copy = df.copy()
            
            if TopicLabelingEnglishConstants.TOPIC_COLUMN in df_copy.columns:
                df_copy[TopicLabelingEnglishConstants.TOPIC_LABEL_COLUMN] = (
                    df_copy[TopicLabelingEnglishConstants.TOPIC_COLUMN]
                    .map(lambda x: topic_labels.get(x, TopicLabelingEnglishConstants.UNKNOWN_LABEL))
                )
            else:
                self.logger.warning(f"Column '{TopicLabelingEnglishConstants.TOPIC_COLUMN}' not found in DataFrame")
                df_copy[TopicLabelingEnglishConstants.TOPIC_LABEL_COLUMN] = TopicLabelingEnglishConstants.UNKNOWN_LABEL
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"Error applying labels: {e}")
            df_copy = df.copy()
            df_copy[TopicLabelingEnglishConstants.TOPIC_LABEL_COLUMN] = TopicLabelingEnglishConstants.UNKNOWN_LABEL
            return df_copy


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_english_topic_labeling_config() -> EnglishLabelGenerationConfig:
    """Renders configuration for English topic labeling"""
    st.subheader("🏷️ English Topic Labeling Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_top_words = st.slider(
            "Number of top words per topic",
            min_value=TopicLabelingEnglishConstants.MIN_TOPIC_WORDS,
            max_value=TopicLabelingEnglishConstants.MAX_TOPIC_WORDS,
            value=TopicLabelingEnglishConstants.DEFAULT_TOP_WORDS
        )
        
        use_important_terms = st.checkbox("Prioritize important terms", value=True)
        use_common_nouns = st.checkbox("Use common nouns", value=True)
    
    with col2:
        separator = st.text_input("Label separator", value=" & ")
        capitalize_terms = st.checkbox("Capitalize terms", value=True)
    
    return EnglishLabelGenerationConfig(
        n_top_words=n_top_words,
        use_important_terms=use_important_terms,
        use_common_nouns=use_common_nouns,
        separator=separator,
        capitalize_terms=capitalize_terms
    )


def render_english_topic_labeling_results(results: EnglishTopicLabelingResults) -> None:
    """Renders results of English topic label generation"""
    st.subheader("📊 English Label Generation Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Processed Topics", results.processed_topics)
    
    with col2:
        st.metric("Skipped Topics", results.skipped_topics)
    
    with col3:
        if results.processing_time:
            st.metric("Processing Time", f"{results.processing_time:.2f}s")
    
    # Show generated labels
    if results.labels:
        st.subheader("🏷️ Generated English Labels")
        
        # Sort by topic ID (but -1 first)
        sorted_items = sorted(
            results.labels.items(),
            key=lambda x: (x[0] if x[0] != -1 else float('-inf'))
        )
        
        for topic_id, label in sorted_items:
            if topic_id == -1:
                st.info(f"**Topic {topic_id}:** {label}")
            else:
                st.write(f"**Topic {topic_id}:** {label}")


def render_english_term_statistics(config: EnglishLabelGenerationConfig) -> None:
    """Renders statistics about English terms configuration"""
    st.subheader("📈 English Terms Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Important Terms", 
            len(config.important_terms),
            help="Terms that get priority in label generation"
        )
    
    with col2:
        st.metric(
            "Common Nouns", 
            len(config.common_nouns),
            help="Terms suitable as secondary parts of labels"
        )
    
    with col3:
        total_unique = len(set(config.important_terms + config.common_nouns))
        st.metric(
            "Total Unique Terms", 
            total_unique,
            help="Total number of unique terms in vocabulary"
        )
    
    # Show term overlap analysis
    if st.checkbox("Show term overlap analysis"):
        important_set = set(config.important_terms)
        common_set = set(config.common_nouns)
        overlap = important_set.intersection(common_set)
        
        st.write(f"**Terms appearing in both lists:** {len(overlap)}")
        if overlap:
            st.write(", ".join(sorted(overlap)))


# =============================================================================
# BACKWARD COMPATIBILITY - OLD API
# =============================================================================

def generate_smart_topic_labels(topic_model, n_topics=None):
    """
    BACKWARD COMPATIBILITY: Generates smarter English topic labels
    
    Args:
        topic_model: The BERTopic model
        n_topics: Number of topics (if None, all will be used)
        
    Returns:
        Dictionary with topic IDs and labels
    """
    manager = EnglishTopicLabelManager()
    results = manager.generate_smart_labels(topic_model, n_topics)
    return results.labels


def apply_topic_labels(df, topic_labels):
    """
    BACKWARD COMPATIBILITY: Applies topic labels to the DataFrame
    
    Args:
        df: DataFrame with comments
        topic_labels: Dictionary with topic IDs and labels
        
    Returns:
        DataFrame with additional 'topic_label' column
    """
    manager = EnglishTopicLabelManager()
    return manager.apply_labels_to_dataframe(df, topic_labels)


# =============================================================================
# EXTENDED API
# =============================================================================

def create_english_topic_label_manager(
    config: Optional[EnglishLabelGenerationConfig] = None
) -> EnglishTopicLabelManager:
    """Factory function for EnglishTopicLabelManager"""
    return EnglishTopicLabelManager(config)


def create_custom_english_labeling_config(
    important_terms: Optional[List[str]] = None,
    common_nouns: Optional[List[str]] = None,
    **kwargs
) -> EnglishLabelGenerationConfig:
    """Creates custom English labeling configuration"""
    config = EnglishLabelGenerationConfig(**kwargs)
    
    if important_terms is not None:
        config.important_terms = important_terms
    
    if common_nouns is not None:
        config.common_nouns = common_nouns
    
    return config


def get_default_english_terms() -> Tuple[List[str], List[str]]:
    """Returns default English important terms and common nouns"""
    config = EnglishLabelGenerationConfig()
    return config.important_terms, config.common_nouns


def merge_english_term_vocabularies(*configs: EnglishLabelGenerationConfig) -> EnglishLabelGenerationConfig:
    """Merges multiple English term vocabularies into one configuration"""
    all_important = []
    all_common = []
    
    for config in configs:
        all_important.extend(config.important_terms)
        all_common.extend(config.common_nouns)
    
    # Remove duplicates while preserving order
    unique_important = list(dict.fromkeys(all_important))
    unique_common = list(dict.fromkeys(all_common))
    
    return EnglishLabelGenerationConfig(
        important_terms=unique_important,
        common_nouns=unique_common
    )