import streamlit as st
from pathlib import Path

# === SPRACHSYSTEM IMPORTIEREN ===
from utils.language_switcher_config import init_language, get_text, t
from utils.language_switcher_ui import language_switcher, display_main_footer

# ===== SETUP IN KORREKTER REIHENFOLGE =====
try:
    # 1. SPRACHE INITIALISIEREN (vor allem anderen!)
    init_language()
    
    # 2. PAGE CONFIG (kann jetzt Übersetzungen verwenden)
    st.set_page_config(
        page_title=t("app_title"),
        page_icon="🌟",
        layout="wide"
    )
except Exception as e:
    st.error(f"Fehler beim Setzen der Seitenkonfiguration: {str(e)}")
    st.info("Versuchen Sie, die App neu zu laden oder kontaktieren Sie den Support.")

# 3. SPRACHSCHALTER HINZUFÜGEN (nach page config)
language_switcher()

# ===== SIDEBAR SETUP =====
st.sidebar.write("")

# Copyright fest am Boden der Navigation
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

# ===== CSS STYLING =====
st.markdown("""
<style>
/* Interactive Data Science Styling */
.hero-stats {
    background: linear-gradient(135deg, #2E86AB, #A23B72);
    color: white;
    padding: 30px;
    border-radius: 15px;
    margin: 20px 0;
    text-align: center;
}
.tech-card {
    background: #f8f9fa;
    border-left: 4px solid #2E86AB;
    padding: 20px;
    margin: 15px 0;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.achievement-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}
.achievement-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid #A23B72;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.model-specs {
    background: #e8f4fd;
    padding: 20px;
    border-radius: 10px;
    border: 2px solid #2E86AB;
    margin: 15px 0;
}
.pipeline-flow {
    background: linear-gradient(45deg, #f8f9fa, #e8f4fd);
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# Disable radio buttons außerhalb der Sidebar
try:
    hide_radio_buttons = """
    <style>
    div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] {
        display: none;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] {
        display: block !important;
    }
    </style>
    """
    st.markdown(hide_radio_buttons, unsafe_allow_html=True)
except Exception as e:
    pass

# ===== VERZEICHNISSE ERSTELLEN =====
saved_results_dir = Path(__file__).parent / "saved_results"
saved_results_dir.mkdir(exist_ok=True, parents=True)

# ===== HAUPTINHALT =====
st.title(f"🌟 {t('app_title')}")

# Hero Section - Honest Technical Achievement
if st.session_state.language == "DE":
    st.markdown("""
    <div class="hero-stats">
    <h2>🚀 Interactive Multi-Language NLP Pipeline</h2>
    <p><strong>YouTube → UNESCO Data: 7-Module Data Science System</strong></p>
    <div style="display: flex; justify-content: space-around; margin-top: 20px;">
        <div><h3>50+</h3><p>Countries Auto-Detected</p></div>
        <div><h3>196</h3><p>UNESCO Countries</p></div>
        <div><h3>7</h3><p>Interactive Apps</p></div>
        <div><h3>6</h3><p>ML Models Deployed</p></div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    ### {t('app_subtitle')}
    
    **HerEducation** ist ein **funktionsfähiges 7-Module-Data-Science-System**, das **YouTube-Kommentare** 
    in **UNESCO-kompatible Policy Intelligence** transformiert. **Interactive processing** von sozialen Medien 
    für **evidenzbasierte Bildungspolitik**.
    
    ### {t('app_description')}
    
    **Interactive ML-Pipeline** mit **automatischer Ländererkennung für 50+ Länder**, 
    **on-demand Whisper-Audio-Transkription** und **Cross-Country-Discourse-Analysis**.
    """, unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div class="hero-stats">
    <h2>🚀 Interactive Multi-Language NLP Pipeline</h2>
    <p><strong>YouTube → UNESCO Data: 7-Module Data Science System</strong></p>
    <div style="display: flex; justify-content: space-around; margin-top: 20px;">
        <div><h3>50+</h3><p>Countries Auto-Detected</p></div>
        <div><h3>196</h3><p>UNESCO Countries</p></div>
        <div><h3>7</h3><p>Interactive Apps</p></div>
        <div><h3>6</h3><p>ML Models Deployed</p></div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    ### {t('app_subtitle')}
    
    **HerEducation** is a **functional 7-module data science system** that transforms **YouTube comments** 
    into **UNESCO-compatible policy intelligence**. **Interactive processing** of social media 
    for **evidence-based education policy**.
    
    ### {t('app_description')}
    
    **Interactive ML pipeline** with **automatic country detection for 50+ countries**, 
    **on-demand Whisper audio transcription** and **cross-country discourse analysis**.
    """, unsafe_allow_html=True)

# ===== CORE TECHNICAL ACHIEVEMENTS =====
if st.session_state.language == "DE":
    st.markdown("""
    <div class="pipeline-flow">
    <h3>🔧 Interactive Data Science Pipeline - What It Actually Does</h3>
    
    <div class="tech-card">
    <h4>🎥 YouTube Intelligence System</h4>
    <strong>Manual Implementation:</strong> yt-dlp Integration → OpenAI Whisper Transcription → Comment Extraction<br>
    <strong>Input:</strong> YouTube URL or search terms (user-initiated)<br>
    <strong>Output:</strong> Transcribed audio + extracted comments → ready for NLP analysis<br>
    <strong>Formats:</strong> MP3, WAV, M4A support with 25MB limit (on-demand processing)
    </div>
    
    <div class="tech-card">
    <h4>🧠 Multi-Language NLP Processing</h4>
    <strong>German:</strong> oliverguhr/german-sentiment-bert + RoBERTa emotion detection<br>
    <strong>English:</strong> cardiffnlp/twitter-roberta + j-hartmann/emotion-english-distilroberta<br>
    <strong>Topics:</strong> BERTopic with distiluse-base-multilingual-cased-v1 embeddings<br>
    <strong>Processing:</strong> Batch processing ~1000 comments/session with confidence scoring
    </div>
    
    <div class="tech-card">
    <h4>🌍 Global Discourse Analysis</h4>
    <strong>Auto-Detection:</strong> 50+ countries from filename patterns<br>
    <strong>Visualization:</strong> PyDeck 3D world maps with sentiment overlays<br>
    <strong>Analytics:</strong> Cross-country topic similarity matrices + emotion heatmaps<br>
    <strong>Export:</strong> CSV/JSON for downstream analysis (session-based)
    </div>
    
    <div class="tech-card">
    <h4>📊 UNESCO Data Integration</h4>
    <strong>Coverage:</strong> All 196 UN member countries education indicators<br>
    <strong>Time Series:</strong> Static database 2019-2025 (manually updateable)<br>
    <strong>Analysis:</strong> Interactive Plotly dashboards + country rankings<br>
    <strong>Standards:</strong> SDG 4.1-4.7 compliant reporting
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="pipeline-flow">
    <h3>🔧 Interactive Data Science Pipeline - What It Actually Does</h3>
    
    <div class="tech-card">
    <h4>🎥 YouTube Intelligence System</h4>
    <strong>Manual Implementation:</strong> yt-dlp Integration → OpenAI Whisper Transcription → Comment Extraction<br>
    <strong>Input:</strong> YouTube URL or search terms (user-initiated)<br>
    <strong>Output:</strong> Transcribed audio + extracted comments → ready for NLP analysis<br>
    <strong>Formats:</strong> MP3, WAV, M4A support with 25MB limit (on-demand processing)
    </div>
    
    <div class="tech-card">
    <h4>🧠 Multi-Language NLP Processing</h4>
    <strong>German:</strong> oliverguhr/german-sentiment-bert + RoBERTa emotion detection<br>
    <strong>English:</strong> cardiffnlp/twitter-roberta + j-hartmann/emotion-english-distilroberta<br>
    <strong>Topics:</strong> BERTopic with distiluse-base-multilingual-cased-v1 embeddings<br>
    <strong>Processing:</strong> Batch processing ~1000 comments/session with confidence scoring
    </div>
    
    <div class="tech-card">
    <h4>🌍 Global Discourse Analysis</h4>
    <strong>Auto-Detection:</strong> 50+ countries from filename patterns<br>
    <strong>Visualization:</strong> PyDeck 3D world maps with sentiment overlays<br>
    <strong>Analytics:</strong> Cross-country topic similarity matrices + emotion heatmaps<br>
    <strong>Export:</strong> CSV/JSON for downstream analysis (session-based)
    </div>
    
    <div class="tech-card">
    <h4>📊 UNESCO Data Integration</h4>
    <strong>Coverage:</strong> All 196 UN member countries education indicators<br>
    <strong>Time Series:</strong> Static database 2019-2025 (manually updateable)<br>
    <strong>Analysis:</strong> Interactive Plotly dashboards + country rankings<br>
    <strong>Standards:</strong> SDG 4.1-4.7 compliant reporting
    </div>
    </div>
    """, unsafe_allow_html=True)

# ===== 7-MODULE SYSTEM =====
if st.session_state.language == "DE":
    st.markdown("""
    <div class="achievement-grid">
    <div class="achievement-card">
    <h4>📖 01_Projektidee.py</h4>
    <strong>Function:</strong> Interactive storytelling about methodology<br>
    <strong>Features:</strong> 8 themed tabs, bilingual support, language switcher<br>
    <strong>Tech:</strong> Streamlit multipage with custom CSS + i18n
    </div>
    
    <div class="achievement-card">
    <h4>🗺️ 02_UNESCO_Dashboard.py</h4>
    <strong>Function:</strong> Interactive world maps for 196 countries<br>
    <strong>Features:</strong> Static education indicators, country comparison, language switcher<br>
    <strong>Tech:</strong> PyDeck visualization + Plotly charts + i18n
    </div>
    
    <div class="achievement-card">
    <h4>📈 03_Indicators_Development.py</h4>
    <strong>Function:</strong> Educational progress tracking 2019-2025<br>
    <strong>Features:</strong> Country rankings, regional analysis, language switcher<br>
    <strong>Tech:</strong> Time series analysis + statistical modeling + i18n
    </div>
    
    <div class="achievement-card">
    <h4>🎬 04_YouTube_Analyzer.py</h4>
    <strong>Function:</strong> Manual video search + audio transcription<br>
    <strong>Features:</strong> On-demand yt-dlp download + Whisper processing<br>
    <strong>Tech:</strong> OpenAI Whisper + comment extraction API
    </div>
    
    <div class="achievement-card">
    <h4>💬 05_Kommentaranalyse_deutsch.py</h4>
    <strong>Function:</strong> German NLP analysis pipeline<br>
    <strong>Features:</strong> Interactive sentiment + emotion + topics + special analysis<br>
    <strong>Tech:</strong> BERT + RoBERTa + BERTopic + WordClouds
    </div>
    
    <div class="achievement-card">
    <h4>💬 06_Comment_Analysis_english.py</h4>
    <strong>Function:</strong> English NLP analysis pipeline<br>
    <strong>Features:</strong> Interactive sentiment + emotion + topic modeling<br>
    <strong>Tech:</strong> DistilRoBERTa + ensemble methods + validation
    </div>
    
    <div class="achievement-card">
    <h4>🌍 07_Globale_Diskurs_Analysis.py</h4>
    <strong>Function:</strong> Cross-country comparison system<br>
    <strong>Features:</strong> 50+ country auto-detection + similarity matrices<br>
    <strong>Tech:</strong> Geographic NLP + statistical correlation analysis
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="achievement-grid">
    <div class="achievement-card">
    <h4>📖 01_Project_Concept.py</h4>
    <strong>Function:</strong> Interactive storytelling about methodology<br>
    <strong>Features:</strong> 8 themed tabs, bilingual support, language switcher<br>
    <strong>Tech:</strong> Streamlit multipage with custom CSS + i18n
    </div>
    
    <div class="achievement-card">
    <h4>🗺️ 02_UNESCO_Dashboard.py</h4>
    <strong>Function:</strong> Interactive world maps for 196 countries<br>
    <strong>Features:</strong> Static education indicators, country comparison, language switcher<br>
    <strong>Tech:</strong> PyDeck visualization + Plotly charts + i18n
    </div>
    
    <div class="achievement-card">
    <h4>📈 03_Indicators_Development.py</h4>
    <strong>Function:</strong> Educational progress tracking 2019-2025<br>
    <strong>Features:</strong> Country rankings, regional analysis, language switcher<br>
    <strong>Tech:</strong> Time series analysis + statistical modeling + i18n
    </div>
    
    <div class="achievement-card">
    <h4>🎬 04_YouTube_Analyzer.py</h4>
    <strong>Function:</strong> Manual video search + audio transcription<br>
    <strong>Features:</strong> On-demand yt-dlp download + Whisper processing<br>
    <strong>Tech:</strong> OpenAI Whisper + comment extraction API
    </div>
    
    <div class="achievement-card">
    <h4>💬 05_German_NLP_Analysis.py</h4>
    <strong>Function:</strong> German NLP analysis pipeline<br>
    <strong>Features:</strong> Interactive sentiment + emotion + topics + special analysis<br>
    <strong>Tech:</strong> BERT + RoBERTa + BERTopic + WordClouds
    </div>
    
    <div class="achievement-card">
    <h4>💬 06_English_NLP_Analysis.py</h4>
    <strong>Function:</strong> English NLP analysis pipeline<br>
    <strong>Features:</strong> Interactive sentiment + emotion + topic modeling<br>
    <strong>Tech:</strong> DistilRoBERTa + ensemble methods + validation
    </div>
    
    <div class="achievement-card">
    <h4>🌍 07_Global_Discourse_Analysis.py</h4>
    <strong>Function:</strong> Cross-country comparison system<br>
    <strong>Features:</strong> 50+ country auto-detection + similarity matrices<br>
    <strong>Tech:</strong> Geographic NLP + statistical correlation analysis
    </div>
    </div>
    """, unsafe_allow_html=True)

# ===== TECHNICAL ARCHITECTURE =====
with st.expander(f"🔧 Interactive Architecture & Dependencies" if st.session_state.language == "EN" else "🔧 Interaktive Architektur & Dependencies"):
    if st.session_state.language == "DE":
        st.markdown("""
        <div class="model-specs">
        <h4>🧠 Deployed ML Models (Interactive Processing)</h4>
        
        <strong>German Language Processing:</strong><br>
        • <strong>Sentiment:</strong> oliverguhr/german-sentiment-bert (110M parameters)<br>
        • <strong>Emotion:</strong> visegradmedia-emotion/Emotion_RoBERTa_german6_v7 (125M parameters)<br>
        • <strong>Preprocessing:</strong> German stopwords + custom tokenization<br><br>
        
        <strong>English Language Processing:</strong><br>
        • <strong>Sentiment:</strong> cardiffnlp/twitter-roberta-base-sentiment-latest<br>
        • <strong>Emotion:</strong> j-hartmann/emotion-english-distilroberta-base<br>
        • <strong>Topic Modeling:</strong> BERTopic + all-MiniLM-L6-v2 embeddings<br><br>
        
        <strong>Audio & Video Processing:</strong><br>
        • <strong>Download:</strong> yt-dlp (manual YouTube processing, multiple formats)<br>
        • <strong>Transcription:</strong> OpenAI Whisper (on-demand: tiny, base, small, medium, large)<br>
        • <strong>Comment Extraction:</strong> Custom API integration<br><br>
        
        <strong>Visualization & Mapping:</strong><br>
        • <strong>3D Maps:</strong> PyDeck with geographical sentiment overlays<br>
        • <strong>Charts:</strong> Plotly interactive dashboards<br>
        • <strong>Word Clouds:</strong> Custom styling with confidence filtering
        </div>
        
        ```python
        # Core Technology Stack (requirements.txt)
        streamlit>=1.28.0
        transformers>=4.30.0
        torch>=2.0.0
        bertopic>=0.15.0
        sentence-transformers>=2.2.0
        plotly>=5.15.0
        pydeck>=0.8.0
        yt-dlp>=2023.7.6
        openai-whisper>=20230314
        pandas>=2.0.0
        numpy>=1.24.0
        scikit-learn>=1.3.0
        hdbscan>=0.8.29
        umap-learn>=0.5.3
        wordcloud>=1.9.2
        langdetect>=1.0.9
        
        # File Structure (50+ specialized modules)
        HerEducation/
        ├── main.py                     # Multi-page app entry point
        ├── pages/                      # 7 interactive apps
        │   ├── 01_Projektidee.py
        │   ├── 02_HerAtlas_UNESCO_Dashboard.py
        │   ├── 03_HerAtlas_Indicators_Development.py
        │   ├── 04_YouTube_Analyzer.py
        │   ├── 05_Kommentaranalyse_deutsch.py
        │   ├── 06_Comment_Analysis_english.py
        │   └── 07_Globale_Diskurs_Analyse.py
        ├── models/                     # ML model management
        │   ├── model_loader_german.py
        │   └── model_loader_english.py
        ├── utils/                      # 50+ utility modules
        │   ├── sentiment_analysis_german.py
        │   ├── emotion_analysis_german.py
        │   ├── topic_analysis_german.py
        │   ├── sentiment_analysis_english.py
        │   ├── emotion_analysis_english.py
        │   ├── topic_analysis_english.py
        │   ├── global_discourse_country_detector.py
        │   ├── youtube_downloader.py
        │   ├── data_loader.py
        │   └── ... (40+ more specialized modules)
        ├── data/                       # UNESCO static datasets
        └── saved_results/              # Session-based analysis persistence
        ```
        """)
    else:
        st.markdown("""
        <div class="model-specs">
        <h4>🧠 Deployed ML Models (Interactive Processing)</h4>
        
        <strong>German Language Processing:</strong><br>
        • <strong>Sentiment:</strong> oliverguhr/german-sentiment-bert (110M parameters)<br>
        • <strong>Emotion:</strong> visegradmedia-emotion/Emotion_RoBERTa_german6_v7 (125M parameters)<br>
        • <strong>Preprocessing:</strong> German stopwords + custom tokenization<br><br>
        
        <strong>English Language Processing:</strong><br>
        • <strong>Sentiment:</strong> cardiffnlp/twitter-roberta-base-sentiment-latest<br>
        • <strong>Emotion:</strong> j-hartmann/emotion-english-distilroberta-base<br>
        • <strong>Topic Modeling:</strong> BERTopic + all-MiniLM-L6-v2 embeddings<br><br>
        
        <strong>Audio & Video Processing:</strong><br>
        • <strong>Download:</strong> yt-dlp (manual YouTube processing, multiple formats)<br>
        • <strong>Transcription:</strong> OpenAI Whisper (on-demand: tiny, base, small, medium, large)<br>
        • <strong>Comment Extraction:</strong> Custom API integration<br><br>
        
        <strong>Visualization & Mapping:</strong><br>
        • <strong>3D Maps:</strong> PyDeck with geographical sentiment overlays<br>
        • <strong>Charts:</strong> Plotly interactive dashboards<br>
        • <strong>Word Clouds:</strong> Custom styling with confidence filtering
        </div>
        
        ```python
        # Core Technology Stack (requirements.txt)
        streamlit>=1.28.0
        transformers>=4.30.0
        torch>=2.0.0
        bertopic>=0.15.0
        sentence-transformers>=2.2.0
        plotly>=5.15.0
        pydeck>=0.8.0
        yt-dlp>=2023.7.6
        openai-whisper>=20230314
        pandas>=2.0.0
        numpy>=1.24.0
        scikit-learn>=1.3.0
        hdbscan>=0.8.29
        umap-learn>=0.5.3
        wordcloud>=1.9.2
        langdetect>=1.0.9
        
        # File Structure (50+ specialized modules)
        HerEducation/
        ├── main.py                     # Multi-page app entry point
        ├── pages/                      # 7 interactive apps
        │   ├── 01_Project_Concept.py
        │   ├── 02_UNESCO_Dashboard.py
        │   ├── 03_Indicators_Development.py
        │   ├── 04_YouTube_Analyzer.py
        │   ├── 05_German_NLP_Analysis.py
        │   ├── 06_English_NLP_Analysis.py
        │   └── 07_Global_Discourse_Analysis.py
        ├── models/                     # ML model management
        │   ├── model_loader_german.py
        │   └── model_loader_english.py
        ├── utils/                      # 50+ utility modules
        │   ├── sentiment_analysis_german.py
        │   ├── emotion_analysis_german.py
        │   ├── topic_analysis_german.py
        │   ├── sentiment_analysis_english.py
        │   ├── emotion_analysis_english.py
        │   ├── topic_analysis_english.py
        │   ├── global_discourse_country_detector.py
        │   ├── youtube_downloader.py
        │   ├── data_loader.py
        │   └── ... (40+ more specialized modules)
        ├── data/                       # UNESCO static datasets
        └── saved_results/              # Session-based analysis persistence
        ```
        """)

# ===== VALUE PROPOSITION =====
if st.session_state.language == "DE":
    st.markdown("""
    ### 🎯 Data Science Portfolio Highlights
    
    **Für Senior Data Science Positionen:**
    
    **🚀 End-to-End ML Pipeline:** Raw YouTube data → 6 ML models → Interactive dashboards → Policy recommendations
    
    **🌍 Geographic Data Science:** 50+ country auto-detection + 3D sentiment mapping + cross-cultural analytics
    
    **🔧 Interactive Architecture:** Modular design + error handling + session-based caching + batch processing
    
    **🧠 Advanced NLP:** Multi-language transformers + topic modeling + emotion analysis + confidence scoring
    
    **📊 Business Intelligence:** UNESCO data integration + statistical modeling + automated insights + export systems
    """)
else:
    st.markdown("""
    ### 🎯 Data Science Portfolio Highlights
    
    **For Senior Data Science Positions:**
    
    **🚀 End-to-End ML Pipeline:** Raw YouTube data → 6 ML models → Interactive dashboards → Policy recommendations
    
    **🌍 Geographic Data Science:** 50+ country auto-detection + 3D sentiment mapping + cross-cultural analytics
    
    **🔧 Interactive Architecture:** Modular design + error handling + session-based caching + batch processing
    
    **🧠 Advanced NLP:** Multi-language transformers + topic modeling + emotion analysis + confidence scoring
    
    **📊 Business Intelligence:** UNESCO data integration + statistical modeling + automated insights + export systems
    """)

# ===== INFO-BOX =====
if st.session_state.language == "DE":
    st.info(f"""
    🎯 **Einstein-Prinzip:** YouTube + UNESCO = Policy Intelligence
    
    **Kernformel:** Social Media Discourse → Interactive ML Analysis → Evidence-Based Policy
    
    **Messbare Ergebnisse:** 50+ Länder • 196 UNESCO-Datensätze • 7 interaktive Apps • 6 ML-Modelle
    """)
else:
    st.info(f"""
    🎯 **Einstein Principle:** YouTube + UNESCO = Policy Intelligence
    
    **Core Formula:** Social Media Discourse → Interactive ML Analysis → Evidence-Based Policy
    
    **Measurable Results:** 50+ Countries • 196 UNESCO Datasets • 7 Interactive Apps • 6 ML Models
    """)

# ===== QUICK START =====
if st.session_state.language == "DE":
    st.markdown("""
    ### 🚀 Schnellstart für Recruiter
    
    **1. System verstehen:** Navigieren Sie durch die 7 Seiten um die Funktionalität zu sehen
    **2. YouTube-Analyse testen:** Seite 4 → Video-URL eingeben → Audio manuell transkribieren
    **3. NLP-Pipeline erleben:** Seite 5/6 → Kommentare interaktiv analysieren → Sentiment/Emotion/Topics
    **4. Global Analysis:** Seite 7 → Ländervergleiche → 3D-Weltkarte → Session-Export
    **5. UNESCO-Daten:** Seite 2/3 → 196 Länder → Statische Bildungsindikatoren
    """)
else:
    st.markdown("""
    ### 🚀 Quick Start for Recruiters
    
    **1. Understand System:** Navigate through 7 pages to see functionality
    **2. Test YouTube Analysis:** Page 4 → Enter video URL → Manually transcribe audio
    **3. Experience NLP Pipeline:** Page 5/6 → Interactively analyze comments → Sentiment/Emotion/Topics
    **4. Global Analysis:** Page 7 → Country comparisons → 3D world map → Session export
    **5. UNESCO Data:** Page 2/3 → 196 countries → Static education indicators
    """)

# ===== MODUL-PROBLEME PRÜFEN =====
try:
    import nltk
    nltk_available = True
except ImportError:
    nltk_available = False

try:
    import pickle
    import json
    persistence_available = True
except ImportError:
    persistence_available = False

missing_modules = []
if not nltk_available:
    missing_modules.append("nltk")
if not persistence_available:
    missing_modules.append("pickle und/oder json")

if missing_modules:
    with st.expander("⚠️ Installation Notes (Click for Setup)" if st.session_state.language == "EN" else "⚠️ Installations-Hinweise (Klicken für Setup)", expanded=False):
        if st.session_state.language == "DE":
            st.warning(f"Für vollständige Funktionalität installieren: {', '.join(missing_modules)}")
            st.code("""
# Full Installation
pip install -r requirements.txt
python -m nltk.downloader all

# Launch Interactive Application
streamlit run main.py
            """)
        else:
            st.warning(f"For full functionality install: {', '.join(missing_modules)}")
            st.code("""
# Full Installation
pip install -r requirements.txt
python -m nltk.downloader all

# Launch Interactive Application
streamlit run main.py
            """)

# ===== FOOTER =====
display_main_footer()