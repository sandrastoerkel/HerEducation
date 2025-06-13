import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import plotly.express as px


class UIMode(Enum):
    """UI display modes for different analysis types"""
    BASIC = "basic"
    ADVANCED = "advanced"
    DEBUG = "debug"


class TabType(Enum):
    """Available tab types for analysis display"""
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    TOPIC = "topic"
    COMPARISON = "comparison"
    SPECIAL = "special"


class LayoutType(Enum):
    """Available layout configurations"""
    WIDE = "wide"
    CENTERED = "centered"
    SIDEBAR = "sidebar"


@dataclass
class UIConfig:
    """Configuration for UI components and styling"""
    page_title: str = "Comment Analysis (English)"
    page_icon: str = "🗣️"
    layout: LayoutType = LayoutType.WIDE
    theme_color_primary: str = "#FF6B98"
    theme_color_secondary: str = "#0ea5e9"
    theme_color_success: str = "#22c55e"
    sidebar_width: int = 224
    footer_enabled: bool = True
    debug_enabled: bool = True


@dataclass
class MetricsData:
    """Data structure for analysis metrics"""
    total_comments: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float


@dataclass
class TabConfiguration:
    """Configuration for analysis tabs"""
    tab_type: TabType
    title: str
    icon: str
    enabled: bool = True
    requires_data: Optional[str] = None


class UIConstants:
    """Constants for UI strings and configuration"""
    
    # Page configuration
    PAGE_TITLE = "Comment Analysis (English)"
    PAGE_ICON = "🗣️"
    
    # Headers and titles
    MAIN_TITLE = "📝 Comment Analysis (English)"
    
    # Descriptions
    MAIN_DESCRIPTION = """
    This page enables comprehensive analysis of **English comments only** regarding:
    - 💭 **Sentiment** (positive/negative/neutral)
    - 😊 **Emotions** (joy, sadness, anger, fear, etc.)
    - 🏷️ **Topics** and key concepts
    
    📌 **Note**: This analysis is specifically designed for English text. Comments in other languages will be automatically filtered out.
    
    Select a CSV file from the data folder to start the analysis.
    """
    
    # Model information
    SENTIMENT_MODEL_INFO = {
        "title": "🤖 Sentiment Analysis Model",
        "model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "type": "RoBERTa model fine-tuned for English sentiment analysis",
        "purpose": "Categorizes comments as positive, neutral, or negative",
        "implementation": "Uses Hugging Face pipeline for sentiment analysis",
        "training_data": "Trained on ~124M tweets with robust performance on social media text",
        "confidence": "Indicates the model's certainty in its prediction (0-1, where 1 means highest confidence)"
    }
    
    EMOTION_MODEL_INFO = {
        "title": "😊 Emotion Analysis Model",
        "model": "j-hartmann/emotion-english-distilroberta-base",
        "type": "DistilRoBERTa model fine-tuned for English emotion detection",
        "purpose": "Detects six emotional states in comments",
        "emotions": ["Anger", "Fear", "Disgust", "Joy", "Sadness", "Surprise"],
        "implementation": "Uses text classification pipeline with emotion labels",
        "performance": "Optimized for social media and informal text",
        "confidence": "Shows the probability of the detected emotion (0-1, higher values = more certain prediction)"
    }
    
    TOPIC_MODEL_INFO = {
        "title": "🏷️ Topic Analysis Model",
        "model": "BERTopic with all-MiniLM-L6-v2 embedding model",
        "type": "Topic clustering model with English-optimized embeddings",
        "purpose": "Identifies topics and themes in the comments",
        "components": ["Sentence Transformers for embeddings", "HDBSCAN for clustering", "Custom topic labeling (Smart Labels)", "c-TF-IDF for topic representation"],
        "performance": "Optimized for English text with high-quality, coherent topics",
        "confidence": "Based on document distance to topic center (lower distance = higher topic membership)"
    }
    
    # Copyright information
    AUTHOR_NAME = "Sandra Störkel"
    PROJECT_NAME = "HerEducation"
    YEAR = "2025"
    FOOTER_SUBTITLE = "Entwickelt für Bildungsgleichberechtigung weltweit"
    
    # Debug section
    DEBUG_TITLE = "🔧 Debug & Consistency Test"
    SAVED_ANALYSES_TITLE = "📁 Saved Analyses"
    
    # Tab titles
    TAB_TITLES = {
        TabType.SENTIMENT: "📊 Sentiment Analysis",
        TabType.EMOTION: "😊 Emotion Analysis",
        TabType.TOPIC: "🏷️ Topic Analysis",
        TabType.COMPARISON: "⚖️ Emotion Model Comparison",
        TabType.SPECIAL: "🔍 Special Analyses"
    }
    
    # Metrics labels
    METRICS_LABELS = {
        "positive": "Positive",
        "neutral": "Neutral", 
        "negative": "Negative"
    }


class HeaderRenderer:
    """Manages header display and page configuration"""
    
    def __init__(self, config: UIConfig):
        self.config = config
    
    def setup_page_config(self) -> None:
        """Set up the Streamlit page configuration"""
        try:
            st.set_page_config(
                page_title=self.config.page_title,
                page_icon=self.config.page_icon,
                layout=self.config.layout.value
            )
        except Exception:
            # Page config might already be set, which is fine
            pass
    
    def display_main_header(self) -> None:
        """Display the main page header and description"""
        st.title(UIConstants.MAIN_TITLE)
        st.markdown(UIConstants.MAIN_DESCRIPTION)
    
    def display_model_info(self, model_type: str) -> None:
        """
        Display information about the models used in the analysis
        
        Args:
            model_type: Type of model ('sentiment', 'emotion', or 'topic')
        """
        if model_type == "sentiment":
            self._render_sentiment_model_info()
        elif model_type == "emotion":
            self._render_emotion_model_info()
        elif model_type == "topic":
            self._render_topic_model_info()
    
    def _render_sentiment_model_info(self) -> None:
        """Render sentiment model information"""
        info = UIConstants.SENTIMENT_MODEL_INFO
        st.markdown(f"""
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 4px solid {self.config.theme_color_secondary}; margin-bottom: 20px;">
            <h4 style="color: #0369a1; margin-top: 0;">{info['title']}</h4>
            <ul style="margin-bottom: 0; color: #475569;">
                <li><strong>Model:</strong> {info['model']}</li>
                <li><strong>Type:</strong> {info['type']}</li>
                <li><strong>Purpose:</strong> {info['purpose']}</li>
                <li><strong>Implementation:</strong> {info['implementation']}</li>
                <li><strong>Training Data:</strong> {info['training_data']}</li>
                <li><strong>Confidence:</strong> {info['confidence']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_emotion_model_info(self) -> None:
        """Render emotion model information"""
        info = UIConstants.EMOTION_MODEL_INFO
        emotions_list = "".join([f"<li>{emotion}</li>" for emotion in info['emotions']])
        
        st.markdown(f"""
        <div style="background-color: #fdf4ff; padding: 15px; border-radius: 10px; border-left: 4px solid #d946ef; margin-bottom: 20px;">
            <h4 style="color: #a21caf; margin-top: 0;">{info['title']}</h4>
            <ul style="margin-bottom: 0; color: #475569;">
                <li><strong>Model:</strong> {info['model']}</li>
                <li><strong>Type:</strong> {info['type']}</li>
                <li><strong>Purpose:</strong> {info['purpose']}:
                    <ul style="margin-top: 5px;">
                        {emotions_list}
                    </ul>
                </li>
                <li><strong>Implementation:</strong> {info['implementation']}</li>
                <li><strong>Performance:</strong> {info['performance']}</li>
                <li><strong>Confidence:</strong> {info['confidence']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_topic_model_info(self) -> None:
        """Render topic model information"""
        info = UIConstants.TOPIC_MODEL_INFO
        components_list = "".join([f"<li>{comp}</li>" for comp in info['components']])
        
        st.markdown(f"""
        <div style="background-color: #f0fdf4; padding: 15px; border-radius: 10px; border-left: 4px solid {self.config.theme_color_success}; margin-bottom: 20px;">
            <h4 style="color: #16a34a; margin-top: 0;">{info['title']}</h4>
            <ul style="margin-bottom: 0; color: #475569;">
                <li><strong>Model:</strong> {info['model']}</li>
                <li><strong>Type:</strong> {info['type']}</li>
                <li><strong>Purpose:</strong> {info['purpose']}</li>
                <li><strong>Implementation:</strong> Uses:
                    <ul style="margin-top: 5px;">
                        {components_list}
                    </ul>
                </li>
                <li><strong>Performance:</strong> {info['performance']}</li>
                <li><strong>Confidence:</strong> {info['confidence']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


class SidebarManager:
    """Manages sidebar components and layout"""
    
    def __init__(self, config: UIConfig):
        self.config = config
    
    def setup_sidebar_copyright(self) -> None:
        """Set up the copyright notice in the sidebar"""
        st.sidebar.write("")
        
        # Generate copyright HTML with theme colors
        copyright_html = self._generate_copyright_html()
        st.sidebar.markdown(copyright_html, unsafe_allow_html=True)
    
    def _generate_copyright_html(self) -> str:
        """Generate copyright HTML with styling"""
        return f"""
        <style>
        .sidebar-copyright-fixed-bottom {{
            position: fixed;
            bottom: 10px;
            left: 10px;
            right: 10px;
            max-width: {self.config.sidebar_width}px;
            padding: 15px 10px;
            margin: 10px 0;
            background: rgba(255, 107, 152, 0.1);
            border-left: 3px solid {self.config.theme_color_primary};
            border-radius: 8px;
            text-align: center;
            font-size: 0.75rem;
            z-index: 999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .sidebar-copyright-fixed-bottom .author {{
            color: {self.config.theme_color_primary};
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 3px;
        }}
        
        .sidebar-copyright-fixed-bottom .project {{
            color: #666666;
            font-size: 0.65rem;
        }}
        
        /* Make space for the copyright in the navigation */
        section[data-testid="stSidebar"] > div:first-child {{
            padding-bottom: 80px;
        }}
        </style>
        
        <div class="sidebar-copyright-fixed-bottom">
            <div class="author">© {UIConstants.AUTHOR_NAME}</div>
            <div class="project">{UIConstants.PROJECT_NAME} {UIConstants.YEAR}</div>
        </div>
        """
    
    def display_footer_copyright(self) -> None:
        """Display copyright footer at the bottom of the page"""
        if not self.config.footer_enabled:
            return
            
        st.markdown(f"""
        <style>
        /* Professional Copyright Footer */
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
            color: {self.config.theme_color_primary};
            font-weight: 500;
        }}
        </style>
        
        <div class="copyright-footer">
            <p>© {UIConstants.YEAR} <span class="author-name">{UIConstants.AUTHOR_NAME}</span> | {UIConstants.PROJECT_NAME} Platform</p>
            <p>{UIConstants.FOOTER_SUBTITLE}</p>
        </div>
        """, unsafe_allow_html=True)


class MetricsCalculator:
    """Calculates and displays analysis metrics"""
    
    @staticmethod
    def calculate_sentiment_metrics(df: pd.DataFrame) -> Optional[MetricsData]:
        """
        Calculate sentiment metrics from DataFrame
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            MetricsData object or None if no sentiment data
        """
        if 'sentiment' not in df.columns or df.empty:
            return None
        
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        
        positive_count = sentiment_counts.get('positive', 0)
        neutral_count = sentiment_counts.get('neutral', 0)
        negative_count = sentiment_counts.get('negative', 0)
        
        return MetricsData(
            total_comments=total,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            positive_percentage=(positive_count / total) * 100 if total > 0 else 0,
            neutral_percentage=(neutral_count / total) * 100 if total > 0 else 0,
            negative_percentage=(negative_count / total) * 100 if total > 0 else 0
        )
    
    @staticmethod
    def display_sentiment_metrics(metrics: MetricsData) -> None:
        """
        Display sentiment metrics in columns
        
        Args:
            metrics: MetricsData object with calculated metrics
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                UIConstants.METRICS_LABELS["positive"],
                f"{metrics.positive_count}",
                f"{metrics.positive_percentage:.1f}%"
            )
        
        with col2:
            st.metric(
                UIConstants.METRICS_LABELS["neutral"],
                f"{metrics.neutral_count}",
                f"{metrics.neutral_percentage:.1f}%"
            )
        
        with col3:
            st.metric(
                UIConstants.METRICS_LABELS["negative"],
                f"{metrics.negative_count}",
                f"{metrics.negative_percentage:.1f}%"
            )


class TabManager:
    """Manages tab creation and configuration"""
    
    def __init__(self, config: UIConfig):
        self.config = config
    
    def determine_available_tabs(self, df: pd.DataFrame, available_modules: Dict[str, bool]) -> List[TabConfiguration]:
        """
        Determine which tabs should be available based on data and modules
        
        Args:
            df: DataFrame with analysis results
            available_modules: Dictionary of available analysis modules
            
        Returns:
            List of TabConfiguration objects
        """
        tabs = []
        
        # Sentiment Analysis is always available
        tabs.append(TabConfiguration(
            tab_type=TabType.SENTIMENT,
            title=UIConstants.TAB_TITLES[TabType.SENTIMENT],
            icon="📊",
            enabled=True
        ))
        
        # Topic Analysis
        if 'topic' in df.columns and available_modules.get('topic_analysis', False):
            tabs.append(TabConfiguration(
                tab_type=TabType.TOPIC,
                title=UIConstants.TAB_TITLES[TabType.TOPIC],
                icon="🏷️",
                enabled=True,
                requires_data='topic'
            ))
        
        # Emotion Analysis
        if 'dominant_emotion' in df.columns and available_modules.get('emotion_analysis', False):
            tabs.append(TabConfiguration(
                tab_type=TabType.EMOTION,
                title=UIConstants.TAB_TITLES[TabType.EMOTION],
                icon="😊",
                enabled=True,
                requires_data='dominant_emotion'
            ))
            
            # Emotion Comparison
            if available_modules.get('emotion_comparison', False):
                tabs.append(TabConfiguration(
                    tab_type=TabType.COMPARISON,
                    title=UIConstants.TAB_TITLES[TabType.COMPARISON],
                    icon="⚖️",
                    enabled=True,
                    requires_data='dominant_emotion'
                ))
        
        # Special Analysis
        if 'topic' in df.columns and available_modules.get('special_analysis', False):
            tabs.append(TabConfiguration(
                tab_type=TabType.SPECIAL,
                title=UIConstants.TAB_TITLES[TabType.SPECIAL],
                icon="🔍",
                enabled=True,
                requires_data='topic'
            ))
        
        return tabs
    
    def create_analysis_tabs(self, tab_configs: List[TabConfiguration]) -> List[Any]:
        """
        Create Streamlit tabs based on configuration
        
        Args:
            tab_configs: List of TabConfiguration objects
            
        Returns:
            List of tab objects
        """
        if len(tab_configs) > 1:
            tab_titles = [config.title for config in tab_configs if config.enabled]
            return st.tabs(tab_titles)
        else:
            return [st.container()]


class DebugValidator:
    """Handles debug functionality and system validation"""
    
    def __init__(self, config: UIConfig):
        self.config = config
    
    def show_debug_section(self, persistence_manager: Any, results_dir: Path) -> None:
        """
        Show debug section with file system information and consistency tests
        
        Args:
            persistence_manager: Instance of CommentAnalysisPersistence
            results_dir: Path object for results directory
        """
        if not self.config.debug_enabled:
            return
            
        with st.expander(UIConstants.DEBUG_TITLE):
            self._run_consistency_test(persistence_manager)
            self._show_directory_info(results_dir)
            self._show_file_listing(results_dir)
    
    def _run_consistency_test(self, persistence_manager: Any) -> None:
        """Run consistency test on persistence manager"""
        try:
            persistence_manager.test_save_load_consistency()
        except Exception as e:
            st.error(f"Consistency test failed: {e}")
    
    def _show_directory_info(self, results_dir: Path) -> None:
        """Show current directory information"""
        st.info(f"Current save directory: {results_dir}")
    
    def _show_file_listing(self, results_dir: Path) -> None:
        """Show file listing for debug purposes"""
        if st.button("Show all files in save directory"):
            try:
                all_files = list(results_dir.glob("*"))
                st.write(f"Found files ({len(all_files)}):")
                for file in sorted(all_files):
                    size = file.stat().st_size if file.is_file() else "DIR"
                    st.text(f"  {file.name} ({size} bytes)")
            except Exception as e:
                st.error(f"Error listing files: {e}")
    
    def display_saved_analyses_section(self, persistence_manager: Any) -> Optional[str]:
        """
        Display section with saved analyses
        
        Args:
            persistence_manager: Instance of CommentAnalysisPersistence
            
        Returns:
            Selected filename or None
        """
        with st.expander(UIConstants.SAVED_ANALYSES_TITLE, expanded=False):
            try:
                available_analyses = persistence_manager.get_available_analyses()
                
                if not available_analyses:
                    st.info("No saved analyses found.")
                    return None
                
                return self._handle_saved_analyses_display(available_analyses)
                
            except Exception as e:
                st.error(f"Error loading saved analyses: {e}")
                st.info("You can still perform a new analysis by selecting a file.")
                return None
    
    def _handle_saved_analyses_display(self, available_analyses: List[Dict]) -> Optional[str]:
        """Handle the display of saved analyses"""
        analyses_df = pd.DataFrame(available_analyses)
        
        try:
            analyses_df['date'] = pd.to_datetime(analyses_df['date'])
            analyses_df = analyses_df.sort_values('date', ascending=False)
        except Exception as e:
            st.warning(f"Error processing dates: {e}")
        
        st.dataframe(analyses_df)
        
        if len(analyses_df) > 0:
            filenames = analyses_df['filename'].tolist()
            if filenames:
                selected_file = st.selectbox(
                    "Load saved analysis:",
                    options=filenames,
                    index=0
                )
                
                if st.button("Load Analysis"):
                    return selected_file
        
        return None


class UIManager:
    """
    Enterprise UI Manager for English Comment Analysis
    
    Manages all UI components with modular architecture and enterprise patterns
    """
    
    def __init__(self, config: Optional[UIConfig] = None):
        """
        Initialize the UI Manager with configuration
        
        Args:
            config: UI configuration object, uses default if None
        """
        self.config = config or UIConfig()
        self.header_renderer = HeaderRenderer(self.config)
        self.sidebar_manager = SidebarManager(self.config)
        self.metrics_calculator = MetricsCalculator()
        self.tab_manager = TabManager(self.config)
        self.debug_validator = DebugValidator(self.config)
        
        # Setup page configuration
        self.header_renderer.setup_page_config()
    
    def display_main_interface(self) -> None:
        """Display the main user interface"""
        self.header_renderer.display_main_header()
        self.sidebar_manager.setup_sidebar_copyright()
    
    def display_model_information(self, model_type: str) -> None:
        """
        Display model information section
        
        Args:
            model_type: Type of model ('sentiment', 'emotion', or 'topic')
        """
        self.header_renderer.display_model_info(model_type)
    
    def create_analysis_tabs(self, df: pd.DataFrame, available_modules: Dict[str, bool], 
                           additional_data: Optional[Dict] = None) -> List[Any]:
        """
        Create tabs for different analysis types
        
        Args:
            df: DataFrame with analysis results
            available_modules: Dictionary of available analysis modules
            additional_data: Additional data for analysis (e.g., models, topic info)
            
        Returns:
            List of tab objects
        """
        tab_configs = self.tab_manager.determine_available_tabs(df, available_modules)
        return self.tab_manager.create_analysis_tabs(tab_configs)
    
    def display_analysis_metrics(self, df: pd.DataFrame) -> None:
        """
        Display key metrics from analysis
        
        Args:
            df: DataFrame with analysis results
        """
        metrics = self.metrics_calculator.calculate_sentiment_metrics(df)
        if metrics:
            self.metrics_calculator.display_sentiment_metrics(metrics)
    
    def show_debug_section(self, persistence_manager: Any, results_dir: Path) -> None:
        """
        Show debug section with file system information and consistency tests
        
        Args:
            persistence_manager: Instance of CommentAnalysisPersistence
            results_dir: Path object for results directory
        """
        self.debug_validator.show_debug_section(persistence_manager, results_dir)
    
    def display_saved_analyses_section(self, persistence_manager: Any) -> Optional[str]:
        """
        Display section with saved analyses
        
        Args:
            persistence_manager: Instance of CommentAnalysisPersistence
            
        Returns:
            Selected filename or None
        """
        return self.debug_validator.display_saved_analyses_section(persistence_manager)
    
    def display_footer(self) -> None:
        """Display the footer copyright section"""
        self.sidebar_manager.display_footer_copyright()
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


# Backward Compatibility Layer
class CommentAnalysisUI:
    """
    Legacy class for backward compatibility
    
    Maintains the same API as the original implementation while
    internally using the new enterprise architecture
    """
    
    def __init__(self):
        """Initialize with legacy compatibility"""
        self.ui_manager = UIManager()
        self.setup_page_config()
    
    def setup_page_config(self):
        """Legacy method for page configuration"""
        # Already handled in UIManager initialization
        pass
    
    def display_header(self):
        """Legacy method for header display"""
        self.ui_manager.display_main_interface()
    
    def setup_sidebar_copyright(self):
        """Legacy method for sidebar setup"""
        # Already handled in display_main_interface
        pass
    
    def display_footer_copyright(self):
        """Legacy method for footer display"""
        self.ui_manager.display_footer()
    
    def display_model_info(self, model_type):
        """Legacy method for model info display"""
        self.ui_manager.display_model_information(model_type)
    
    def create_analysis_tabs(self, df, available_modules, additional_data=None):
        """Legacy method for tab creation"""
        return self.ui_manager.create_analysis_tabs(df, available_modules, additional_data)
    
    def display_analysis_metrics(self, df):
        """Legacy method for metrics display"""
        self.ui_manager.display_analysis_metrics(df)
    
    def show_debug_section(self, persistence_manager, results_dir):
        """Legacy method for debug section"""
        self.ui_manager.show_debug_section(persistence_manager, results_dir)
    
    def display_saved_analyses_section(self, persistence_manager):
        """Legacy method for saved analyses display"""
        return self.ui_manager.display_saved_analyses_section(persistence_manager)


# Factory function for easy instantiation
def create_ui_manager(theme: str = "default", debug_enabled: bool = True) -> UIManager:
    """
    Factory function to create a UI Manager with specific configuration
    
    Args:
        theme: Theme configuration ('default', 'minimal', 'colorful')
        debug_enabled: Whether to enable debug functionality
        
    Returns:
        Configured UIManager instance
    """
    config = UIConfig(debug_enabled=debug_enabled)
    
    # Apply theme-specific configurations
    if theme == "minimal":
        config.footer_enabled = False
        config.theme_color_primary = "#666666"
    elif theme == "colorful":
        config.theme_color_primary = "#FF6B98"
        config.theme_color_secondary = "#00D4FF"
        config.theme_color_success = "#00FF88"
    
    return UIManager(config)


# Quick start function for legacy compatibility
def get_comment_analysis_ui() -> CommentAnalysisUI:
    """
    Quick start function for legacy code compatibility
    
    Returns:
        CommentAnalysisUI instance
    """
    return CommentAnalysisUI()