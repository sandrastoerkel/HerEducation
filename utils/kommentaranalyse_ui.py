"""
UI-Komponenten für die Kommentaranalyse (05_kommentaranalyse_deutsch.py)
Enthält wiederverwendbare UI-Elemente, Layouts und visuelle Komponenten
"""
import streamlit as st
import pandas as pd
from pathlib import Path

class KommentaranalyseUI:
    """
    Stellt UI-Komponenten für die Kommentaranalyse bereit
    """
    
    def __init__(self):
        """
        Initialisiert die UI-Komponenten
        """
        # Eventuelle gemeinsame Einstellungen hier initialisieren
        pass
    
    def setup_page_config(self):
        """
        Konfiguriert die Streamlit-Seite
        """
        st.set_page_config(
            page_title="Kommentaranalyse (Deutsch)",
            page_icon="🗣️",
            layout="wide"
        )
    
    def display_header(self):
        """
        Zeigt den Seitenkopf mit Titel und Beschreibung an
        """
        st.title("📝 Kommentaranalyse (Deutsch)")
        
        st.markdown("""
        Diese Seite ermöglicht die Analyse von deutschen Kommentaren hinsichtlich:
        - 💭 **Sentiment** (positiv/negativ/neutral)
        - 😊 **Emotionen** (Freude, Trauer, Angst, etc.)
        - 🏷️ **Themen** und Schlüsselkonzepte
        
        Laden Sie eine CSV-Datei mit Kommentaren hoch, um die Analyse zu starten.
        """)
    
    def setup_sidebar_copyright(self):
        """
        Zeigt das Copyright in der Sidebar an
        """
        # Aktiviere Sidebar
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

        /* Platz für das Copyright in der Navigation schaffen */
        section[data-testid="stSidebar"] > div:first-child {
            padding-bottom: 80px;
        }
        </style>

        <div class="sidebar-copyright-fixed-bottom">
            <div class="author">© Sandra Störkel</div>
            <div class="project">HerEducation 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_footer_copyright(self):
        """
        Zeigt das Copyright im Footer an
        """
        st.markdown("""
        <style>
        /* Professional Copyright Footer */
        .copyright-footer {
            margin-top: 50px;
            padding: 20px 0;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666666;
            font-size: 0.9rem;
            background-color: #f8f9fa;
        }
        .author-name {
            color: #FF6B98;
            font-weight: 500;
        }
        </style>

        <div class="copyright-footer">
            <p>© 2025 <span class="author-name">Sandra Störkel</span> | HerEducation Platform</p>
            <p>Entwickelt für Bildungsgleichberechtigung weltweit</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_model_info(self, model_type):
        """
        Zeigt Informationen über die verwendeten Modelle an
        
        Args:
            model_type: Typ des Modells ("sentiment", "emotion", "topic")
        """
        if model_type == "sentiment":
            st.markdown("""
            <div style="background-color: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 4px solid #0ea5e9; margin-bottom: 20px;">
                <h4 style="color: #0369a1; margin-top: 0;">🤖 Sentiment Analysis Model</h4>
                <ul style="margin-bottom: 0; color: #475569;">
                    <li><strong>Modell:</strong> oliverguhr/german-sentiment-bert</li>
                    <li><strong>Typ:</strong> Feinabgestimmtes BERT-Modell für deutsche Stimmungsanalyse</li>
                    <li><strong>Zweck:</strong> Kategorisiert Kommentare als positiv, neutral oder negativ</li>
                    <li><strong>Implementierung:</strong> Verwendet die Pipeline von Hugging Face zur Stimmungsanalyse</li>
                    <li><strong>Confidence:</strong> Gibt die Sicherheit des Modells in seine Vorhersage an (0-1, wobei 1 höchste Sicherheit bedeutet)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        elif model_type == "emotion":
            st.markdown("""
            <div style="background-color: #fdf4ff; padding: 15px; border-radius: 10px; border-left: 4px solid #d946ef; margin-bottom: 20px;">
                <h4 style="color: #a21caf; margin-top: 0;">😊 Emotionsanalyse-Modell</h4>
                <ul style="margin-bottom: 0; color: #475569;">
                    <li><strong>Modell:</strong> visegradmedia-emotion/Emotion_RoBERTa_german6_v7</li>
                    <li><strong>Typ:</strong> RoBERTa-Modell für deutsche Emotionserkennung</li>
                    <li><strong>Zweck:</strong> Erkennung von sechs emotionalen Zuständen in Kommentaren:
                        <ul style="margin-top: 5px;">
                            <li>Wut (Anger)</li>
                            <li>Furcht (Fear)</li>
                            <li>Abscheu (Disgust)</li>
                            <li>Ekel (Revulsion)</li>
                            <li>Traurigkeit (Sadness)</li>
                            <li>Freude (Joy)</li>
                            <li>Neutral ("keiner von ihnen")</li>
                        </ul>
                    </li>
                    <li><strong>Implementierung:</strong> Verwendung einer Textklassifizierungspipeline mit Emotionskennzeichnungen</li>
                    <li><strong>Confidence:</strong> Zeigt die Wahrscheinlichkeit der erkannten Emotion an (0-1, höhere Werte = sicherere Vorhersage)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        elif model_type == "topic":
            st.markdown("""
            <div style="background-color: #f0fdf4; padding: 15px; border-radius: 10px; border-left: 4px solid #22c55e; margin-bottom: 20px;">
                <h4 style="color: #16a34a; margin-top: 0;">🏷️ Themenanalyse-Modell</h4>
                <ul style="margin-bottom: 0; color: #475569;">
                    <li><strong>Modell:</strong> BERTopic mit distiluse-base-multilingual-cased-v1</li>
                    <li><strong>Typ:</strong> Themen-Clustering-Modell mit multilingualem Embedding</li>
                    <li><strong>Zweck:</strong> Identifizierung von Themen und Konzepten in den Kommentaren</li>
                    <li><strong>Implementierung:</strong> Verwendet:
                        <ul style="margin-top: 5px;">
                            <li>Sentence Transformers für Embeddings</li>
                            <li>HDBSCAN für Clustering</li>
                            <li>Benutzerdefinierte Themenbeschriftung (Smart Labels)</li>
                        </ul>
                    </li>
                    <li><strong>Confidence:</strong> Basiert auf der Distanz der Dokumente zum Themen-Zentrum (niedrigere Distanz = höhere Zugehörigkeit zum Thema)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def create_analysis_tabs(self, df, available_modules, additional_data=None):
        """
        Erstellt die Analyse-Tabs basierend auf den verfügbaren Daten und Modulen
        
        Args:
            df: DataFrame mit den Analyseergebnissen
            available_modules: Dictionary mit verfügbaren Modulen
            additional_data: Zusätzliche Daten (optional)
            
        Returns:
            Tuple: (tabs_to_create, main_tabs)
        """
        tabs_to_create = ["📊 Sentiment-Analyse"]
        
        # Check which analysis results are present in the data
        if 'topic' in df.columns:
            tabs_to_create.append("🏷️ Themen-Analyse")
        
        if 'dominant_emotion' in df.columns:
            tabs_to_create.append("😊 Emotions-Analyse")
            
            # More tabs depending on available data
            if available_modules.get('EMOTION_COMPARISON_AVAILABLE', False):
                tabs_to_create.append("⚖️ Emotionsmodell-Vergleich")
        
        if 'topic' in df.columns and available_modules.get('SPECIAL_ANALYSIS_AVAILABLE', False):
            tabs_to_create.append("🔍 Spezial-Analysen")
        
        # Create tabs
        if len(tabs_to_create) > 1:
            main_tabs = st.tabs(tabs_to_create)
        else:
            main_tabs = [st.container()]
        
        return tabs_to_create, main_tabs
    
    def display_analysis_metrics(self, df):
        """
        Zeigt Metriken zur aktuellen Analyse an
        
        Args:
            df: DataFrame mit den Analyseergebnissen
        """
        if df is not None:
            # Erstelle Mehrspaltenlayout für Metriken
            col1, col2, col3, col4 = st.columns(4)
            
            # Gesamtzahl der Kommentare
            col1.metric("Gesamte Kommentare", len(df))
            
            # Sentiment-Metriken
            if 'sentiment' in df.columns:
                positive_count = len(df[df['sentiment'] == 'positive'])
                negative_count = len(df[df['sentiment'] == 'negative'])
                neutral_count = len(df[df['sentiment'] == 'neutral'])
                
                col2.metric("Positive Kommentare", positive_count, f"{positive_count/len(df):.1%}")
                col3.metric("Neutrale Kommentare", neutral_count, f"{neutral_count/len(df):.1%}")
                col4.metric("Negative Kommentare", negative_count, f"{negative_count/len(df):.1%}")
            
            # Topic-Metriken
            if 'topic' in df.columns:
                # Zweite Reihe für Topic-Metriken
                st.write("")
                topic_cols = st.columns(4)
                
                # Anzahl der Themen (ohne -1)
                unique_topics = len(set(df['topic'].unique()) - {-1})
                topic_cols[0].metric("Identifizierte Themen", unique_topics)
                
                # Größte Themengruppe
                if unique_topics > 0:
                    topic_counts = df[df['topic'] != -1]['topic'].value_counts()
                    largest_topic = topic_counts.index[0] if not topic_counts.empty else "N/A"
                    largest_topic_count = topic_counts.iloc[0] if not topic_counts.empty else 0
                    topic_cols[1].metric("Größte Themengruppe", f"Topic {largest_topic}", f"{largest_topic_count} Kommentare")
                
                # Outlier-Kommentare (-1)
                outlier_count = len(df[df['topic'] == -1])
                outlier_pct = outlier_count / len(df) if len(df) > 0 else 0
                topic_cols[2].metric("Outlier-Kommentare", outlier_count, f"{outlier_pct:.1%}")
            
            # Emotions-Metriken
            if 'dominant_emotion' in df.columns:
                # Dritte Reihe für Emotions-Metriken
                st.write("")
                emotion_cols = st.columns(4)
                
                # Hauptemotion
                top_emotion = df['dominant_emotion'].value_counts().index[0] if not df['dominant_emotion'].empty else "N/A"
                top_emotion_count = df['dominant_emotion'].value_counts().iloc[0] if not df['dominant_emotion'].empty else 0
                emotion_cols[0].metric("Hauptemotion", top_emotion, f"{top_emotion_count} Kommentare")
                
                # Verhältnis positiv/negativ (Joy vs. Rest)
                joy_count = len(df[df['dominant_emotion'] == 'joy'])
                joy_pct = joy_count / len(df) if len(df) > 0 else 0
                emotion_cols[1].metric("Freude (Joy)", joy_count, f"{joy_pct:.1%}")
                
                # Wut-Kommentare
                anger_count = len(df[df['dominant_emotion'] == 'anger'])
                anger_pct = anger_count / len(df) if len(df) > 0 else 0
                emotion_cols[2].metric("Wut (Anger)", anger_count, f"{anger_pct:.1%}")
    
    def show_debug_section(self, persistence_manager, results_dir):
        """
        Zeigt den Debug-Bereich an
        
        Args:
            persistence_manager: Persistence Manager Instanz
            results_dir: Ergebnisverzeichnis
        """
        with st.expander("🔧 Debug & Konsistenz-Test"):
            persistence_manager.test_save_load_consistency()
            
            # Zeige aktuelles Verzeichnis
            st.info(f"Aktueller Speicher-Pfad: {results_dir}")
            
            # Zeige alle Dateien im Verzeichnis
            if st.button("Zeige alle Dateien im Speicher-Verzeichnis"):
                try:
                    all_files = list(results_dir.glob("*"))
                    st.write(f"Gefundene Dateien ({len(all_files)}):")
                    for file in sorted(all_files):
                        size = file.stat().st_size if file.is_file() else "DIR"
                        st.text(f"  {file.name} ({size} bytes)")
                except Exception as e:
                    st.error(f"Fehler beim Listen der Dateien: {e}")
    
    def display_saved_analyses_section(self, persistence_manager):
        """
        Zeigt den Bereich für gespeicherte Analysen an
        
        Args:
            persistence_manager: Instance des PersistenceManager
            
        Returns:
            Tuple: (df, additional_data, metadata) if analysis loaded, else (None, None, None)
        """
        with st.expander("📁 Gespeicherte Analysen", expanded=False):
            try:
                available_analyses = persistence_manager.get_available_analyses()
                
                if not available_analyses:
                    st.info("Keine gespeicherten Analysen gefunden.")
                    return None, None, None
                else:
                    # Zeige Tabelle mit gespeicherten Analysen
                    analyses_df = pd.DataFrame(available_analyses)
                    try:
                        analyses_df['date'] = pd.to_datetime(analyses_df['date'])
                        analyses_df = analyses_df.sort_values('date', ascending=False)
                    except Exception as e:
                        st.warning(f"Fehler beim Verarbeiten der Datumsangaben: {e}")
                    
                    st.dataframe(analyses_df)
                    
                    # Stelle sicher, dass die Options-Liste nie leer ist
                    if len(analyses_df) > 0:
                        filenames = analyses_df['filename'].tolist()
                        if filenames:  # Zusätzliche Sicherheitsprüfung
                            # Sichere Auswahl
                            selected_file = st.selectbox(
                                "Gespeicherte Analyse laden:",
                                options=filenames,
                                index=0  # Der erste Eintrag ist standardmäßig ausgewählt
                            )
                            
                            if st.button("Analyse laden"):
                                with st.spinner(f"Lade Analyse für '{selected_file}'..."):
                                    df, additional_data, metadata = persistence_manager.load_analysis_results(selected_file)
                                    
                                    if df is not None:
                                        st.success(f"Analyse für '{selected_file}' erfolgreich geladen!")
                                        return df, additional_data, metadata
                                    else:
                                        st.error(f"Konnte keine Daten für '{selected_file}' laden.")
                                        return None, None, None
            except Exception as e:
                st.error(f"Fehler beim Laden der gespeicherten Analysen: {e}")
                st.info("Sie können trotzdem eine neue Analyse durchführen, indem Sie eine Datei hochladen.")
                return None, None, None
        
        return None, None, None