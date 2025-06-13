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
/* Professional UN/UNESCO Styling */
.copyright-footer {
    margin-top: 50px;
    padding: 25px 20px;
    border-top: 2px solid #FF6B98;
    text-align: center;
    color: #666666;
    font-size: 0.9rem;
    background-color: #f8f9fa;
    border-radius: 10px;
}
.author-name {
    color: #FF6B98;
    font-weight: 600;
}
.app-title {
    color: #FF6B98;
    font-weight: 500;
}

/* UN/UNESCO Professional Styling */
.un-blue {
    color: #009edb;
    font-weight: 600;
}
.unesco-orange {
    color: #ed6a37;
    font-weight: 600;
}
.sdg-hero {
    background: linear-gradient(135deg, #009edb, #ed6a37);
    color: white;
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
    text-align: center;
}
.methodology-highlight {
    background: #f8f9fa;
    border-left: 4px solid #009edb;
    padding: 20px;
    margin: 15px 0;
    border-radius: 5px;
}
.global-framework {
    background: linear-gradient(45deg, #e8f4fd, #fef2ee);
    padding: 25px;
    border-radius: 15px;
    border: 2px solid #009edb;
    margin: 20px 0;
}
.impact-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin: 20px 0;
}
.impact-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid #ed6a37;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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

# SDG 4 Hero Section - Global Focus
if st.session_state.language == "DE":
    st.markdown("""
    <div class="sdg-hero">
    <h2>🎯 UN SDG 4: Skalierbare Educational Equity Analytics</h2>
    <p><strong>Evidenzbasierte Policy Intelligence für internationale Entwicklungsorganisationen</strong></p>
    <p><em>Transferable Framework • Global Applicability • Cultural Adaptability</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Global Methodology Description
    st.markdown(f"""
    ### {t('app_subtitle')}
    
    **HerEducation** ist ein **übertragbares analytisches Framework**, das <span class="un-blue">UNESCO-Bildungsdaten</span> 
    mit <span class="unesco-orange">Social Media Discourse Analysis</span> kombiniert, um **datengestützte Politikempfehlungen** 
    für internationale Entwicklungsorganisationen zu generieren.
    
    ### {t('app_description')}
    
    Die Plattform wurde entwickelt, um **in jedem Land und kulturellen Kontext** anwendbar zu sein - von Südostasien bis Afrika, 
    von entwickelten bis zu sich entwickelnden Volkswirtschaften.
    """, unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div class="sdg-hero">
    <h2>🎯 UN SDG 4: Scalable Educational Equity Analytics</h2>
    <p><strong>Evidence-based Policy Intelligence for International Development Organizations</strong></p>
    <p><em>Transferable Framework • Global Applicability • Cultural Adaptability</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    ### {t('app_subtitle')}
    
    **HerEducation** is a **transferable analytical framework** that combines <span class="un-blue">UNESCO education data</span> 
    with <span class="unesco-orange">Social Media Discourse Analysis</span> to generate **data-driven policy recommendations** 
    for international development organizations.
    
    ### {t('app_description')}
    
    The platform was designed to be **applicable in any country and cultural context** - from Southeast Asia to Africa, 
    from developed to developing economies.
    """, unsafe_allow_html=True)

# ===== GLOBAL APPLICABILITY SECTION =====
if st.session_state.language == "DE":
    st.markdown("""
    <div class="global-framework">
    <h3>🌍 Globale Anwendbarkeit & Cross-Cultural Adaptability</h3>
    
    <div class="methodology-highlight">
    <h4>📊 Bewährte Methodik - Überall anwendbar:</h4>
    <strong>Schritt 1:</strong> UNESCO-Bildungsdaten-Integration (verfügbar für 196 Länder)<br>
    <strong>Schritt 2:</strong> Lokale Social Media Discourse Analysis (YouTube, Facebook, Twitter)<br>
    <strong>Schritt 3:</strong> Kulturspezifische NLP-Modellierung (jede Sprache adaptierbar)<br>
    <strong>Schritt 4:</strong> Cross-Country Benchmarking & Policy Recommendations<br>
    <strong>Schritt 5:</strong> Real-time Impact Monitoring & Evaluation
    </div>
    
    <div class="impact-grid">
    <div class="impact-card">
    <h4>🇲🇾 Südostasien (Pilot)</h4>
    <strong>Malaysia:</strong> 50+ Länder-Sentiment-Analyse<br>
    <strong>Adaptierbar für:</strong> Indonesien, Thailand, Philippinen<br>
    <strong>Sprachen:</strong> Malaiisch, Englisch, Chinesisch, Tamil
    </div>
    
    <div class="impact-card">
    <h4>🌍 Afrika (Expansion)</h4>
    <strong>Potenzielle Märkte:</strong> Nigeria, Kenia, Südafrika<br>
    <strong>Anpassungen:</strong> Lokale Sprachen, Bildungssysteme<br>
    <strong>Focus:</strong> Rural Education, Gender Barriers
    </div>
    
    <div class="impact-card">
    <h4>🇪🇺 Europa/Nordamerika</h4>
    <strong>Anwendung:</strong> Migrant/Refugee Education<br>
    <strong>Zielgruppe:</strong> Diaspora-Communities<br>
    <strong>Sprachen:</strong> Deutsch, Englisch, Französisch
    </div>
    
    <div class="impact-card">
    <h4>🇮🇳 Südasien</h4>
    <strong>Skalierung:</strong> Indien, Pakistan, Bangladesch<br>
    <strong>Komplexität:</strong> Multiple Sprachen, Kastensystem<br>
    <strong>Potenzial:</strong> 500+ Millionen Mädchen
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="global-framework">
    <h3>🌍 Global Applicability & Cross-Cultural Adaptability</h3>
    
    <div class="methodology-highlight">
    <h4>📊 Proven Methodology - Applicable Everywhere:</h4>
    <strong>Step 1:</strong> UNESCO Education Data Integration (available for 196 countries)<br>
    <strong>Step 2:</strong> Local Social Media Discourse Analysis (YouTube, Facebook, Twitter)<br>
    <strong>Step 3:</strong> Culture-specific NLP Modeling (adaptable to any language)<br>
    <strong>Step 4:</strong> Cross-Country Benchmarking & Policy Recommendations<br>
    <strong>Step 5:</strong> Real-time Impact Monitoring & Evaluation
    </div>
    
    <div class="impact-grid">
    <div class="impact-card">
    <h4>🇲🇾 Southeast Asia (Pilot)</h4>
    <strong>Malaysia:</strong> 50+ Countries Sentiment Analysis<br>
    <strong>Adaptable for:</strong> Indonesia, Thailand, Philippines<br>
    <strong>Languages:</strong> Malay, English, Chinese, Tamil
    </div>
    
    <div class="impact-card">
    <h4>🌍 Africa (Expansion)</h4>
    <strong>Potential Markets:</strong> Nigeria, Kenya, South Africa<br>
    <strong>Adaptations:</strong> Local languages, education systems<br>
    <strong>Focus:</strong> Rural Education, Gender Barriers
    </div>
    
    <div class="impact-card">
    <h4>🇪🇺 Europe/North America</h4>
    <strong>Application:</strong> Migrant/Refugee Education<br>
    <strong>Target Group:</strong> Diaspora Communities<br>
    <strong>Languages:</strong> German, English, French
    </div>
    
    <div class="impact-card">
    <h4>🇮🇳 South Asia</h4>
    <strong>Scaling:</strong> India, Pakistan, Bangladesh<br>
    <strong>Complexity:</strong> Multiple languages, caste system<br>
    <strong>Potential:</strong> 500+ Million girls
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ===== PROJEKTSTRUKTUR =====
with st.expander(f"📋 {t('project_structure')}" if st.session_state.language == "DE" else "📋 Comprehensive Technical Architecture"):
    if st.session_state.language == "DE":
        st.markdown("""
        ```
        HerEducation/ (Global Educational Equity Framework)
        ├── main.py                     # Haupteinstiegspunkt der Streamlit-App
        ├── requirements.txt            # Production-ready Python dependencies
        ├── README.md                   # Comprehensive Documentation (10+ KB)
        ├── LICENSE                     # Open Source License
        ├── pages/                      # Multi-Country Analysis Modules
        │   ├── __init__.py            # Page system initialization
        │   ├── 01_Projektidee.py       # Global Methodology & Concept
        │   ├── 02_HerAtlas_UNESCO_Dashboard.py  # UNESCO Data (196 countries)
        │   ├── 03_HerAtlas_Indicators_Development.py # Time series analysis
        │   ├── 04_YouTube_Analyzer.py  # Social Media Intelligence Tools
        │   ├── 05_Kommentaranalyse_deutsch.py # German NLP Analysis
        │   ├── 06_Comment_Analysis_english.py # English NLP Analysis
        │   └── 07_Globale_Diskurs_Analyse.py  # Cross-Country Comparisons
        ├── models/                     # Scalable ML Architecture
        │   ├── model_loader.py         # German language models
        │   └── model_loader_english.py # English language models
        ├── utils/                      # Comprehensive Utility Library (50+ modules)
        │   ├── __init__.py
        │   ├── language_switcher_config.py    # Multi-language system
        │   ├── language_switcher_ui.py        # Language UI components
        │   ├── shared_components.py           # Reusable UI components
        │   ├── data_loader.py                 # UNESCO data integration
        │   ├── youtube_downloader.py          # YouTube-specific tools
        │   ├── sentiment_analysis*.py         # Sentiment analysis (DE/EN)
        │   ├── emotion_analysis*.py           # Emotion detection (DE/EN)
        │   ├── topic_analysis*.py             # Topic modeling (DE/EN)
        │   ├── global_discourse_*.py          # Cross-country analysis tools
        │   ├── visualizations.py              # Chart & graph utilities
        │   └── ... (40+ additional specialized modules)
        ├── data/                       # Global Data Infrastructure
        │   ├── unesco_global/          # UNESCO datasets (196 countries)
        │   ├── social_media/           # Platform-specific data
        │   ├── cultural_contexts/      # Country adaptation configs
        │   └── analysis_results/       # Processed insights
        ├── saved_results/              # Country-specific Analysis Archives
        └── deployment/                 # UN/International deployment configs
        ```
        
        **🔧 Technische Highlights:**
        - **50+ spezialisierte Utils** für skalierbare Analyse
        - **Multi-Language NLP Pipeline** (Deutsch, Englisch, erweiterbar)
        - **UNESCO API Integration** für Real-time Daten
        - **Cultural Context Adapters** für verschiedene Länder
        - **Automated Reporting** für UN/World Bank Standards
        """)
    else:
        st.markdown("""
        ```
        HerEducation/ (Global Educational Equity Framework)
        ├── main.py                     # Main Streamlit application entry point
        ├── requirements.txt            # Production-ready Python dependencies
        ├── README.md                   # Comprehensive Documentation (10+ KB)
        ├── LICENSE                     # Open Source License
        ├── pages/                      # Multi-Country Analysis Modules
        │   ├── __init__.py            # Page system initialization
        │   ├── 01_Project_Concept.py   # Global Methodology & Framework
        │   ├── 02_UNESCO_Dashboard.py  # UNESCO Data (196 countries)
        │   ├── 03_Indicators_Development.py # Time series analysis
        │   ├── 04_Social_Media_Analyzer.py # Social Media Intelligence
        │   ├── 05_NLP_Analysis_German.py # German language analysis
        │   ├── 06_NLP_Analysis_English.py # English language analysis
        │   └── 07_Global_Discourse_Analysis.py # Cross-country comparisons
        ├── models/                     # Scalable ML Architecture
        │   ├── model_loader.py         # Language model management
        │   └── model_adapters/         # Cultural adaptation modules
        ├── utils/                      # Comprehensive Utility Library (50+ modules)
        │   ├── __init__.py
        │   ├── language_switcher_*.py          # Multi-language system
        │   ├── shared_components.py            # Reusable UI components
        │   ├── data_loader.py                  # UNESCO data integration
        │   ├── social_media_extractors.py      # Platform-specific tools
        │   ├── nlp_pipeline_*.py              # Language-specific NLP
        │   ├── cultural_adapters.py            # Cross-cultural analysis
        │   ├── policy_generators.py            # Automated recommendations
        │   ├── visualization_suite.py          # Interactive dashboards
        │   └── ... (40+ specialized modules for global deployment)
        ├── data/                       # Global Data Infrastructure
        │   ├── unesco_global/          # UNESCO datasets (196 countries)
        │   ├── social_media/           # Platform-specific data
        │   ├── cultural_contexts/      # Country adaptation configs
        │   └── analysis_results/       # Processed insights
        ├── saved_results/              # Country-specific Analysis Archives
        └── deployment/                 # UN/International deployment configs
        ```
        
        **🔧 Technical Highlights:**
        - **50+ specialized utils** for scalable analysis
        - **Multi-language NLP pipeline** (German, English, expandable)
        - **UNESCO API integration** for real-time data
        - **Cultural context adapters** for different countries
        - **Automated reporting** for UN/World Bank standards
        """)

# ===== HAUPTSEKTIONEN =====
if st.session_state.language == "DE":
    st.markdown("""
    ### 📊 Global Methodology & Transferable Framework
    Entdecken Sie das **wissenschaftliche Framework** und die **bewährten Methoden**, die in **jedem Land** 
    für Educational Equity Assessment eingesetzt werden können. **Proof-of-Concept:** Malaysia → **Skalierung:** Weltweit.

    ### 🌍 UNESCO HerAtlas (Global Coverage)
    Analysieren Sie den **rechtlichen Rahmen** und die **Bildungspolitik aller 196 UN-Mitgliedsländer** 
    basierend auf UNESCO HerAtlas-Daten:
    - **Gender-equitable Policy Analysis** mit Cross-Country Benchmarking
    - **International Agreements Tracking** für Girls' Education (CEDAW, CRC, etc.)
    - **Constitutional Rights Assessment** - Education as Human Right
    - **Compulsory Education Analysis** mit Gender Parity Indicators

    ### 📈 SDG 4 Indicators Development (Real-time Monitoring)
    **Kontinuierliches Tracking** der zeitlichen Entwicklung wichtiger **SDG 4-Indikatoren weltweit**:
    - **Multi-Country Rankings** und Regional Cluster Analysis
    - **Peer-Country Comparisons** für ähnliche Entwicklungsstadien  
    - **Progress Alerts** bei signifikanten Veränderungen
    - **Predictive Analytics** für Policy Success Probability

    ### 🎬 YouTube Intelligence (Fokus: Bildungsdiskurse)
    **Spezialisierte Tools** zur Analyse bildungsbezogener **YouTube-Diskurse**:
    - **YouTube Comment Analysis** (Kommentar-Download und Analyse)
    - **Cultural Sentiment Mapping** mit sprachspezifischen Modellen (Deutsch/Englisch)
    - **Video Transcription** (OpenAI Whisper) für Content-Analyse
    - **Batch Analysis** für mehrere Videos (manuell ausgewählt)

    ### 💬 Multilingual NLP Analysis (Culturally-Adaptive)
    **Umfassende Analyse** von Social Media-Diskursen in **jeder Sprache**:
    1. **Automated Language Detection** mit kultureller Kontextualisierung
    2. **Culturally-Calibrated Sentiment Analysis** (nicht nur positive/negative)
    3. **Topic Modeling** für länderspezifische Educational Themes
    4. **Cross-Cultural Emotion Analysis** adapted to expression patterns
    5. **Specialized Analysis** für Education & Gender Topics mit lokalen Nuancen

    ### 🌍 Global Discourse Analysis & Policy Intelligence
    **Vergleichende Analyse** von Bildungsdiskursen zwischen **allen analysierten Ländern**:
    - **Cross-Country Sentiment Benchmarking** mit kulturellen Insights
    - **International Topic Trend Analysis** und Emerging Issues Detection
    - **Evidence-based Insights** für Policy Development
    - **Interactive Global Dashboards** für Multi-Stakeholder Access
    - **Comprehensive Analysis Reports** nach UN/World Bank Standards
    """)
else:
    st.markdown("""
    ### 📊 Global Methodology & Transferable Framework
    Discover the **scientific framework** and **proven methods** that can be applied in **any country** 
    for Educational Equity Assessment. **Proof-of-Concept:** Malaysia → **Scaling:** Worldwide.

    ### 🌍 UNESCO HerAtlas (Global Coverage)
    Analyze the **legal framework** and **education policy of all 196 UN member countries** 
    based on UNESCO HerAtlas data:
    - **Gender-equitable Policy Analysis** with cross-country benchmarking
    - **International Agreements Tracking** for Girls' Education (CEDAW, CRC, etc.)
    - **Constitutional Rights Assessment** - Education as Human Right
    - **Compulsory Education Analysis** with Gender Parity Indicators

    ### 📈 SDG 4 Indicators Development (Real-time Monitoring)
    **Continuous tracking** of temporal development of important **SDG 4 indicators worldwide**:
    - **Multi-Country Rankings** and Regional Cluster Analysis
    - **Peer-Country Comparisons** for similar development stages
    - **Progress Alerts** for significant changes
    - **Predictive Analytics** for Policy Success Probability

    ### 🎬 YouTube Intelligence (Focus: Educational Discourse)
    **Specialized tools** for analyzing education-related **YouTube discourse**:
    - **YouTube Comment Analysis** (comment download and analysis)
    - **Cultural Sentiment Mapping** with language-specific models (German/English)
    - **Video Transcription** (OpenAI Whisper) for content analysis
    - **Batch Analysis** for multiple videos (manually selected)

    ### 💬 Multilingual NLP Analysis (Culturally-Adaptive)
    **Comprehensive analysis** of social media discourse in **any language**:
    1. **Automated Language Detection** with cultural contextualization
    2. **Culturally-Calibrated Sentiment Analysis** (beyond positive/negative)
    3. **Topic Modeling** for country-specific educational themes
    4. **Cross-Cultural Emotion Analysis** adapted to expression patterns
    5. **Specialized Analysis** for Education & Gender Topics with local nuances

    ### 🌍 Global Discourse Analysis & Policy Intelligence
    **Comparative analysis** of educational discourse between **all analyzed countries**:
    - **Cross-Country Sentiment Benchmarking** with cultural insights
    - **International Topic Trend Analysis** and Emerging Issues Detection
    - **Evidence-based Insights** for Policy Development
    - **Interactive Global Dashboards** for Multi-Stakeholder Access
    - **Comprehensive Analysis Reports** according to UN/World Bank Standards
    """)

# ===== INFO-BOX =====
if st.session_state.language == "DE":
    st.info(f"""
    📌 **{t('app_title')}** kombiniert **UNESCO-Bildungsdaten mit innovativer Social Media-Analyse**, 
    um **skalierbare, evidenzbasierte Lösungen** für **Educational Equity in jedem kulturellen Kontext** zu entwickeln.
    
    **🎯 UN SDG 4 Relevance:** Direct alignment mit SDG 4.1-4.7 indicators • **196 countries ready** • **Cultural adaptability proven**
    """)
else:
    st.info(f"""
    📌 **{t('app_title')}** combines **UNESCO education data with innovative social media analysis** 
    to develop **scalable, evidence-based solutions** for **Educational Equity in any cultural context**.
    
    **🎯 UN SDG 4 Relevance:** Direct alignment with SDG 4.1-4.7 indicators • **196 countries ready** • **Cultural adaptability proven**
    """)

# ===== TECHNISCHE FEATURES =====
if st.session_state.language == "DE":
    st.markdown("""
    ### 🔬 Skalierbare ML-Architektur für internationale Entwicklungszusammenarbeit
    
    **Multi-Language NLP Pipeline (Global Deployment Ready):**
    
    **1. Adaptive Sentiment Analysis**
    - **Models:** BERT, RoBERTa, DistilBERT (kulturspezifisch fine-tuned)
    - **Cultural Calibration:** Context-aware adaptation für verschiedene Kulturen
    - **Implementation:** Hugging Face Transformers mit Cultural Adapters
    - **Skalierung:** Template-basierte Erweiterung für neue Sprachen/Kulturen
    
    **2. Cross-Cultural Emotion Analysis**
    - **Models:** Emotion-RoBERTa mit kulturellen Anpassungsschichten
    - **Emotion Categories:** Universal emotions + kulturspezifische Kategorien
    - **Implementation:** Ensemble-Methods für kulturelle Nuancen
    - **Validation:** Native Speaker Validation in Zielsprachen
    
    **3. Global Topic Modeling**
    - **Framework:** BERTopic mit Multilingual-BERT-Embeddings
    - **Clustering:** HDBSCAN mit kulturellen Kontextvariablen
    - **Topic Mapping:** Automatisierte Cross-Language-Topic-Zuordnung
    - **Evaluation:** Coherence-Metrics + Expert Domain Validation
    
    **4. UNESCO Data Integration Pipeline**
    - **Coverage:** Alle 196 UN-Mitgliedsländer, Real-time Updates
    - **Indicators:** SDG 4.1-4.7 vollständig abgedeckt
    - **Analysis:** Automated Gap Analysis, Progress Tracking
    - **Reporting:** UN/World Bank-kompatible Formate
    
    ### 🎯 Praktische Anwendungen für International Development Organizations
    
    **UN Agencies (UNDP, UNESCO, UNICEF):**
    - Real-time SDG 4 Progress Monitoring in Programmländern
    - Cultural Barriers Assessment für Bildungsprogramme
    - Community Sentiment Analysis für lokale Akzeptanz
    - Evidence-based Program Design mit lokalen Insights
    
    **World Bank & Regional Development Banks:**
    - Policy Impact Assessment vor Programm-Implementation
    - Cultural Risk Analysis für Bildungsinvestitionen
    - Cross-Country Best Practice Identification
    - Automated Reporting für Donor Relations
    
    **Bilateral Development Cooperation:**
    - Cultural Intelligence für Entwicklungsprojekte
    - Local Stakeholder Sentiment Monitoring
    - Adaptive Program Management basierend auf Community Feedback
    - Success Probability Assessment für Policy Interventions
    
    **International NGOs:**
    - Community-based Program Design mit Cultural Insights
    - Local Partner Selection basierend auf Discourse Analysis
    - Impact Measurement durch Sentiment Change Tracking
    - Advocacy Strategy Development mit Evidence-based Arguments
    """)
else:
    st.markdown("""
    ### 🔬 Scalable ML Architecture for International Development Cooperation
    
    **Multi-Language NLP Pipeline (Global Deployment Ready):**
    
    **1. Adaptive Sentiment Analysis**
    - **Models:** BERT, RoBERTa, DistilBERT (culturally fine-tuned)
    - **Cultural Calibration:** Context-aware adaptation for different cultures
    - **Implementation:** Hugging Face Transformers with Cultural Adapters
    - **Scaling:** Template-based extension for new languages/cultures
    
    **2. Cross-Cultural Emotion Analysis**
    - **Models:** Emotion-RoBERTa with cultural adaptation layers
    - **Emotion Categories:** Universal emotions + culture-specific categories
    - **Implementation:** Ensemble methods for cultural nuances
    - **Validation:** Native speaker validation in target languages
    
    **3. Global Topic Modeling**
    - **Framework:** BERTopic with Multilingual-BERT embeddings
    - **Clustering:** HDBSCAN with cultural context variables
    - **Topic Mapping:** Automated cross-language topic assignment
    - **Evaluation:** Coherence metrics + expert domain validation
    
    **4. UNESCO Data Integration Pipeline**
    - **Coverage:** All 196 UN member countries, real-time updates
    - **Indicators:** SDG 4.1-4.7 fully covered
    - **Analysis:** Automated gap analysis, progress tracking
    - **Reporting:** UN/World Bank compatible formats
    
    ### 🎯 Practical Applications for International Development Organizations
    
    **UN Agencies (UNDP, UNESCO, UNICEF):**
    - Real-time SDG 4 progress monitoring in program countries
    - Cultural barriers assessment for education programs
    - Community sentiment analysis for local acceptance
    - Evidence-based program design with local insights
    
    **World Bank & Regional Development Banks:**
    - Policy impact assessment before program implementation
    - Cultural risk analysis for education investments
    - Cross-country best practice identification
    - Automated reporting for donor relations
    
    **Bilateral Development Cooperation:**
    - Cultural intelligence for development projects
    - Local stakeholder sentiment monitoring
    - Adaptive program management based on community feedback
    - Success probability assessment for policy interventions
    
    **International NGOs:**
    - Community-based program design with cultural insights
    - Local partner selection based on discourse analysis
    - Impact measurement through sentiment change tracking
    - Advocacy strategy development with evidence-based arguments
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
    with st.expander("⚠️ Technical Dependencies & Deployment Notes" if st.session_state.language == "EN" else "⚠️ Technische Abhängigkeiten & Deployment-Hinweise", expanded=False):
        if st.session_state.language == "DE":
            st.warning(f"Einige Module für vollständige Funktionalität: {', '.join(missing_modules)}")
            st.info("""
            **Production Deployment**: Verwenden Sie die `requirements.txt` für vollständige Installation:
            
            ```bash
            pip install -r requirements.txt
            python -m nltk.downloader all  # For NLP components
            ```
            
            **UN/International Deployment Recommendations:**
            - **Docker Containerization** für konsistente Environments
            - **Kubernetes Orchestration** für Multi-Country Deployment
            - **Cloud-native Architecture** (AWS/Azure/GCP) für globale Skalierung
            - **Security Compliance** nach UN IT Security Standards
            """)
        else:
            st.warning(f"Some modules for full functionality: {', '.join(missing_modules)}")
            st.info("""
            **Production Deployment**: Use the `requirements.txt` for complete installation:
            
            ```bash
            pip install -r requirements.txt
            python -m nltk.downloader all  # For NLP components
            ```
            
            **UN/International Deployment Recommendations:**
            - **Docker Containerization** for consistent environments
            - **Kubernetes Orchestration** for multi-country deployment
            - **Cloud-native Architecture** (AWS/Azure/GCP) for global scaling
            - **Security Compliance** according to UN IT Security Standards
            """)

# ===== FOOTER =====
display_main_footer()