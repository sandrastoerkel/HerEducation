"""
Persistence Manager für 05_kommentaranalyse_deutsch.py
Behandelt Speichern und Laden von Analyseergebnissen mit relativen Pfaden
"""
import streamlit as st
import pandas as pd
import json
import pickle
import re
from datetime import datetime
from pathlib import Path
import traceback

class KommentaranalysePersistence:
    """
    Manager für das Speichern und Laden von Kommentaranalyse-Ergebnissen
    """
    
    def __init__(self, results_dir):
        """
        Initialisiert den Persistence Manager
        
        Args:
            results_dir: Pfad zum Ergebnisverzeichnis
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def create_safe_filename(self, filename):
        """
        Erstellt einen sicheren Dateinamen - IDENTICAL in all functions
        """
        # Extract only filename without path and extension
        base_filename = Path(filename).stem
        
        # Remove all problematic characters (EXACT same rule everywhere)
        safe_filename = re.sub(r'[^\w\-\.]', '_', base_filename)
        
        return safe_filename
    
    def save_analysis_results(self, filename, df, additional_data=None):
        """
        Speichert Analyseergebnisse mit full consistency checking
        
        Args:
            filename: Originalname der Datei
            df: DataFrame mit Analyseergebnissen
            additional_data: Zusätzliche Daten (z.B. Modelle, Topic-Labels)
            
        Returns:
            bool: True wenn erfolgreich gespeichert
        """
        try:
            safe_filename = self.create_safe_filename(filename)
            
            st.info(f"💾 Speichere Analyse...")
            st.info(f"   Original-Name: {filename}")
            st.info(f"   Sicherer Name: {safe_filename}")
            st.info(f"   Verzeichnis: {self.results_dir}")
            
            # Define all file paths
            df_pkl_path = self.results_dir / f"{safe_filename}_results.pkl"
            df_csv_path = self.results_dir / f"{safe_filename}_results.csv"
            additional_path = self.results_dir / f"{safe_filename}_additional.pkl"
            meta_path = self.results_dir / f"{safe_filename}_meta.json"
            
            # 1. Save DataFrame (try pickle, fallback to CSV)
            success_df_save = False
            try:
                df.to_pickle(df_pkl_path)
                st.success(f"✅ DataFrame als Pickle gespeichert")
                success_df_save = True
                saved_df_path = df_pkl_path
            except Exception as e:
                st.warning(f"⚠️ Pickle fehlgeschlagen ({e}), versuche CSV...")
                try:
                    df.to_csv(df_csv_path, index=False, encoding='utf-8')
                    st.success(f"✅ DataFrame als CSV gespeichert")
                    success_df_save = True
                    saved_df_path = df_csv_path
                except Exception as csv_e:
                    st.error(f"❌ CSV-Speicherung auch fehlgeschlagen: {csv_e}")
                    return False
            
            # 2. Save additional data
            has_additional = False
            if additional_data:
                try:
                    with open(additional_path, 'wb') as f:
                        pickle.dump(additional_data, f)
                    st.success(f"✅ Zusatzdaten gespeichert")
                    has_additional = True
                except Exception as e:
                    st.warning(f"⚠️ Zusatzdaten nicht gespeichert: {e}")
            
            # 3. Save metadata (IMPORTANT: includes all info for retrieval)
            metadata = {
                'original_filename': filename,  # Original filename
                'safe_filename': safe_filename,  # Processed safe name
                'analysis_date': datetime.now().isoformat(),
                'num_comments': len(df),
                'columns': list(df.columns),
                'has_additional_data': has_additional,
                'saved_files': {
                    'dataframe': str(saved_df_path),
                    'additional': str(additional_path) if has_additional else None,
                    'metadata': str(meta_path)
                }
            }
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Metadaten gespeichert: {meta_path}")
            
            # Verify saved files
            existing_files = []
            for path in [saved_df_path, meta_path]:
                if path.exists():
                    existing_files.append(f"   ✓ {path.name} ({path.stat().st_size} bytes)")
            
            if additional_path.exists():
                existing_files.append(f"   ✓ {additional_path.name} ({additional_path.stat().st_size} bytes)")
            
            st.success(f"🎉 Speichern erfolgreich! Dateien:")
            for file_info in existing_files:
                st.text(file_info)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern: {e}")
            st.error(traceback.format_exc())
            return False
    
    def load_analysis_results(self, filename):
        """
        Lädt gespeicherte Analyseergebnisse - uses EXACTLY same logic as save
        
        Args:
            filename: Originalname der Datei
            
        Returns:
            Tuple: (df, additional_data, metadata)
        """
        try:
            safe_filename = self.create_safe_filename(filename)
            
            st.info(f"📂 Lade Analyse...")
            st.info(f"   Original-Name: {filename}")
            st.info(f"   Sicherer Name: {safe_filename}")
            st.info(f"   Verzeichnis: {self.results_dir}")
            
            # Define all file paths (EXACT same logic as when saving)
            df_pkl_path = self.results_dir / f"{safe_filename}_results.pkl"
            df_csv_path = self.results_dir / f"{safe_filename}_results.csv"
            additional_path = self.results_dir / f"{safe_filename}_additional.pkl"
            meta_path = self.results_dir / f"{safe_filename}_meta.json"
            
            # Check if metadata exists
            if not meta_path.exists():
                st.error(f"❌ Metadaten nicht gefunden: {meta_path}")
                return None, None, None
            
            # Load metadata first
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            st.success(f"✅ Metadaten geladen")
            
            # Load DataFrame (try pickle first, then CSV)
            df = None
            if df_pkl_path.exists():
                try:
                    df = pd.read_pickle(df_pkl_path)
                    st.success(f"✅ DataFrame aus Pickle geladen")
                except Exception as e:
                    st.warning(f"⚠️ Pickle-Laden fehlgeschlagen: {e}")
            
            if df is None and df_csv_path.exists():
                try:
                    df = pd.read_csv(df_csv_path, encoding='utf-8')
                    st.success(f"✅ DataFrame aus CSV geladen")
                except Exception as e:
                    st.error(f"❌ CSV-Laden fehlgeschlagen: {e}")
                    return None, None, metadata
            
            if df is None:
                st.error(f"❌ Keine DataFrame-Datei gefunden")
                return None, None, metadata
            
            # Load additional data if available
            additional_data = None
            if additional_path.exists():
                try:
                    with open(additional_path, 'rb') as f:
                        additional_data = pickle.load(f)
                    st.success(f"✅ Zusatzdaten geladen")
                except Exception as e:
                    st.warning(f"⚠️ Zusatzdaten nicht geladen: {e}")
            
            st.success(f"🎉 Laden erfolgreich!")
            return df, additional_data, metadata
            
        except Exception as e:
            st.error(f"❌ Fehler beim Laden: {e}")
            st.error(traceback.format_exc())
            return None, None, None
    
    def get_available_analyses(self):
        """
        Returns a list of available saved analyses - clean version without debug output
        
        Returns:
            List: Liste von Dictionaries mit Analysen
        """
        try:
            analyses = []
            meta_files = list(self.results_dir.glob("*_meta.json"))
            
            for meta_file in meta_files:
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Use original_filename from metadata
                    original_filename = metadata.get('original_filename', 'Unbekannt')
                    safe_filename = metadata.get('safe_filename', 'Unbekannt')
                    
                    analyses.append({
                        'filename': original_filename,
                        'safe_filename': safe_filename,
                        'date': metadata.get('analysis_date', datetime.now().isoformat()),
                        'num_comments': metadata.get('num_comments', 0),
                        'meta_file': str(meta_file)
                    })
                    
                except Exception as e:
                    continue
            
            return analyses
            
        except Exception as e:
            return []
    
    def test_save_load_consistency(self):
        """
        Testet die Konsistenz zwischen Speichern und Laden
        """
        st.subheader("🧪 Test Save/Load Konsistenz")
        
        if st.button("Konsistenz-Test durchführen"):
            # Erstelle Testdaten
            test_filename = "test_datei_123!@#.csv"  # Problematic characters
            test_df = pd.DataFrame({
                'comment_text': ['Test 1', 'Test 2', 'Test 3'],
                'sentiment': ['positive', 'negative', 'neutral'],
                'topic': [0, 1, 2]
            })
            test_additional = {'model_info': 'test_model', 'topics': [0, 1, 2]}
            
            st.info(f"Test-Dateiname: {test_filename}")
            
            # 1. Save
            st.info("1. Speichere Test-Daten...")
            save_success = self.save_analysis_results(test_filename, test_df, test_additional)
            
            if save_success:
                # 2. Check available analyses
                st.info("2. Suche gespeicherte Analysen...")
                available = self.get_available_analyses()
                
                found_test = False
                for analysis in available:
                    if analysis['filename'] == test_filename:
                        found_test = True
                        st.success(f"✅ Test-Analyse in Liste gefunden: {analysis['filename']}")
                        break
                
                if not found_test:
                    st.error("❌ Test-Analyse NICHT in Liste gefunden!")
                    st.json(available)
                
                # 3. Load
                st.info("3. Lade Test-Daten...")
                loaded_df, loaded_additional, loaded_metadata = self.load_analysis_results(test_filename)
                
                if loaded_df is not None:
                    st.success("✅ Laden erfolgreich!")
                    st.info("Vergleiche Daten:")
                    
                    # Compare DataFrame
                    if test_df.equals(loaded_df):
                        st.success("✅ DataFrame identisch")
                    else:
                        st.error("❌ DataFrame unterschiedlich")
                        st.write("Original:", test_df)
                        st.write("Geladen:", loaded_df)
                    
                    # Compare Additional Data
                    if test_additional == loaded_additional:
                        st.success("✅ Zusatzdaten identisch")
                    else:
                        st.error("❌ Zusatzdaten unterschiedlich")
                        st.write("Original:", test_additional)
                        st.write("Geladen:", loaded_additional)
                else:
                    st.error("❌ Laden fehlgeschlagen!")
            else:
                st.error("❌ Speichern fehlgeschlagen!")