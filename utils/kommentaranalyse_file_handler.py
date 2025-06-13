"""
File Handler für die Kommentaranalyse (05_kommentaranalyse_deutsch.py)
Verarbeitet Datei-Upload, Reinigung und Vorbereitung von Kommentardaten
"""
import streamlit as st
import pandas as pd
import re
from pathlib import Path
from io import BytesIO

class KommentaranalyseFileHandler:
    """
    Verarbeitet Dateien für die Kommentaranalyse
    """
    
    def __init__(self, data_dir):
        """
        Initialisiert den FileHandler
        
        Args:
            data_dir: Path-Objekt zum Datenverzeichnis
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_files_from_data_folder(self):
        """
        Gibt eine Liste aller CSV-Dateien aus dem Datenordner zurück
        
        Returns:
            List: Liste von CSV-Dateipfaden
        """
        if not self.data_dir.exists():
            self.data_dir.mkdir(exist_ok=True, parents=True)
        
        csv_files = list(self.data_dir.glob("*.csv"))
        return [str(file) for file in csv_files]
    
    def clean_csv_data(self, file_content):
        """
        Bereinigt CSV-Daten und extrahiert die Kommentarspalte
        
        Args:
            file_content: String-Inhalt der CSV-Datei
            
        Returns:
            DataFrame mit bereinigten Kommentaren
        """
        try:
            # Split file into lines
            lines = file_content.strip().split('\n')
            cleaned_data = []
            
            for line_index, line in enumerate(lines):
                # Extract comment manually - robust approach
                in_quotes = False
                fields = []
                current_field = ""
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        fields.append(current_field)
                        current_field = ""
                    else:
                        current_field += char
                
                # Add last field
                fields.append(current_field)
                
                # Extract comment column (second column, if available)
                comment = ""
                if len(fields) > 1:
                    comment = fields[1]
                
                cleaned_data.append({'comment_text': comment, 'original_line': line_index + 1})
            
            return pd.DataFrame(cleaned_data)
        
        except Exception as e:
            st.error(f"Fehler bei der Bereinigung der CSV-Datei: {e}")
            return pd.DataFrame(columns=['comment_text', 'original_line'])
    
    def clean_text(self, text):
        """
        Bereinigt Text für die Themenanalyse
        
        Args:
            text: Zu bereinigender Text
            
        Returns:
            str: Bereinigter Text
        """
        if pd.isna(text) or text is None or text == "":
            return ""
        
        text = str(text)
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s\äöüÄÖÜß]', '', text)  # Deutsche Zeichen beibehalten
        text = re.sub(r'\d+', '', text)
        # Convert to lowercase
        text = text.lower()
        
        # Try to remove stop words if NLTK is available
        try:
            import nltk
            from nltk.corpus import stopwords
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
            
            stop_words = set(stopwords.words('german'))
            text = ' '.join([word for word in text.split() if word not in stop_words and len(word) > 2])
        except:
            # If NLTK is not available, just filter short words
            text = ' '.join([word for word in text.split() if len(word) > 2])
                
        return text
    
    def load_and_clean_data(self, uploaded_file):
        """
        Lädt und bereinigt die hochgeladene Datei
        
        Args:
            uploaded_file: Streamlit UploadedFile-Objekt
            
        Returns:
            Tuple: (df, text_column)
        """
        # Determine file type
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type == 'csv':
            # Read and clean CSV file
            file_content = uploaded_file.getvalue().decode('utf-8')
            
            # Show file information
            st.info("CSV-Datei wird bereinigt und Kommentare werden extrahiert...")
            
            # Clean CSV and extract comments
            df = self.clean_csv_data(file_content)
            
            if df.empty:
                st.error("Keine gültigen Kommentare in der Datei gefunden.")
                st.stop()
            else:
                st.success(f"{len(df)} Kommentare erfolgreich extrahiert.")
                text_column = 'comment_text'
        
        elif file_type in ['json', 'jsonl']:
            # Read JSON file
            df = pd.read_json(uploaded_file, lines=True)
            
            # Check if required columns are present
            text_column = None
            possible_columns = ['text', 'comment', 'kommentar', 'content', 'Text', 'Comment', 'Kommentar', 'Content']
            
            for col in possible_columns:
                if col in df.columns:
                    text_column = col
                    break
            
            if text_column is None:
                st.error("Keine erkannte Textspalte in der JSON-Datei gefunden.")
                st.stop()
        
        return df, text_column
    
    def load_file_from_path(self, file_path):
        """
        Lädt eine Datei von einem Pfad
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            BytesIO: Datei als BytesIO-Objekt (simuliert Upload)
        """
        try:
            # Lese Datei
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # Konvertiere zu BytesIO für streamlit
            processed_file = BytesIO(file_content)
            processed_file.name = Path(file_path).name
            
            return processed_file
        except Exception as e:
            st.error(f"Fehler beim Lesen der Datei: {e}")
            return None
    
    def extract_video_id(self, filename):
        """
        Extrahiert die YouTube-Video-ID aus dem Dateinamen
        
        Args:
            filename: Name der Datei
            
        Returns:
            str: YouTube-Video-ID oder None
        """
        # Pattern to match YouTube ID format in filenames like "20240618_87TYPn6gbwA_title.csv"
        pattern = r'_([a-zA-Z0-9_-]{11})_'
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
        
        # Alternative pattern
        alt_pattern = r'_([a-zA-Z0-9_-]{11})'
        alt_match = re.search(alt_pattern, filename)
        if alt_match:
            return alt_match.group(1)
        
        return None
    
    def display_file_selection_ui(self):
        """
        Zeigt die Benutzeroberfläche für die Dateiauswahl an
        
        Returns:
            processed_file: Ausgewählte Datei oder None
        """
        # Flag for file processing
        processed_file = None
        
        # Container for file selection
        file_selection_container = st.container()
        
        with file_selection_container:
            # Option 1: Select file from data folder
            available_csv_files = self.get_files_from_data_folder()
            
            if available_csv_files:
                st.write("### 📁 Datei aus dem Datenordner auswählen")
                selected_csv_path = st.selectbox(
                    f"CSV-Datei aus dem Ordner '{self.data_dir}' auswählen:",
                    options=available_csv_files,
                    format_func=lambda x: Path(x).name
                )
                
                if st.button("🔍 Ausgewählte Datei analysieren"):
                    processed_file = self.load_file_from_path(selected_csv_path)
            else:
                st.warning(f"❌ Keine CSV-Dateien im Ordner '{self.data_dir}' gefunden.")
                st.info("📝 Bitte legen Sie CSV-Dateien in diesem Ordner ab oder nutzen Sie die Upload-Option unten.")
            
            # Option 2: Upload file
            st.write("### 📤 Datei hochladen")
            uploaded_file = st.file_uploader("CSV- oder JSON-Datei mit Kommentaren hochladen:", type=["csv", "json", "jsonl"])
            
            if uploaded_file is not None:
                processed_file = uploaded_file
        
        return processed_file
    
    def apply_text_cleaning(self, df, text_column):
        """
        Wendet Textreinigung auf alle Texte im DataFrame an
        
        Args:
            df: DataFrame mit Kommentaren
            text_column: Name der Textspalte
            
        Returns:
            DataFrame mit zusätzlicher 'clean_text'-Spalte
        """
        # Stelle sicher dass alle Texte Strings sind
        df[text_column] = df[text_column].fillna("").astype(str)
        
        # Wende clean_text auf jeden Text an
        df['clean_text'] = df[text_column].apply(self.clean_text)
        
        st.success(f"✅ Textreinigung auf {len(df)} Kommentare angewendet")
        return df
    
    def show_file_info(self, filename):
        """
        Zeigt Informationen über die geladene Datei an
        
        Args:
            filename: Dateiname
        """
        st.info(f"📄 Geladene Datei: {filename}")
        
        # Besondere Information zu YouTube-ID
        video_id = self.extract_video_id(filename)
        if video_id:
            st.info(f"🎬 YouTube Video-ID erkannt: {video_id}")
            
        # Filetyp
        file_extension = Path(filename).suffix.lower()
        if file_extension == '.csv':
            st.info("📊 Dateiformat: CSV (Komma-getrennte Werte)")
        elif file_extension in ['.json', '.jsonl']:
            st.info("📊 Dateiformat: JSON/JSONL")
        else:
            st.info(f"📊 Dateiformat: {file_extension}")
            
    def get_preview(self, df, max_rows=5, max_chars=100):
        """
        Erzeugt eine gekürzte Vorschau der Daten für die Anzeige
        
        Args:
            df: DataFrame
            max_rows: Maximale Anzahl Zeilen
            max_chars: Maximale Anzahl Zeichen pro Zelle
            
        Returns:
            DataFrame: Gekürzte Vorschau
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        preview = df.head(max_rows).copy()
        
        # Kürze lange Text-Spalten
        for col in preview.columns:
            if preview[col].dtype == 'object':
                preview[col] = preview[col].apply(
                    lambda x: f"{str(x)[:max_chars]}..." if isinstance(x, str) and len(str(x)) > max_chars else x
                )
        
        return preview