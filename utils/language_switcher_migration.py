# utils/language_switcher_migration.py
"""
Migration und Helper-Tools für das Sprachschalter-System
Unterstützt bei der schrittweisen Migration bestehender Seiten
"""

import re
from typing import Dict, List, Tuple
from utils.language_switcher_config import TRANSLATIONS

class LanguageMigrationHelper:
    """
    Helper-Klasse für die Migration bestehender Seiten zum Sprachsystem
    """
    
    def __init__(self):
        self.common_translations = self._build_common_translations()
    
    def _build_common_translations(self) -> Dict[str, str]:
        """
        Erstellt ein Mapping von deutschen Texten zu Übersetzungsschlüsseln
        basierend auf dem TRANSLATIONS Dictionary
        """
        mapping = {}
        
        # Durchsuche alle deutschen Übersetzungen
        for key, german_text in TRANSLATIONS["DE"].items():
            mapping[german_text] = key
        
        return mapping
    
    def suggest_translation_key(self, german_text: str) -> str:
        """
        Schlägt einen Übersetzungsschlüssel für einen deutschen Text vor
        
        Args:
            german_text: Der deutsche Text
            
        Returns:
            Vorgeschlagener Übersetzungsschlüssel
        """
        # Direkter Match
        if german_text in self.common_translations:
            return self.common_translations[german_text]
        
        # Generiere Schlüssel basierend auf Text
        # Entferne Sonderzeichen und konvertiere zu lowercase
        clean_text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s]', '', german_text)
        clean_text = clean_text.lower().strip()
        
        # Ersetze Umlaute
        replacements = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
            'ß': 'ss'
        }
        for german, english in replacements.items():
            clean_text = clean_text.replace(german, english)
        
        # Ersetze Leerzeichen mit Unterstrichen
        suggested_key = clean_text.replace(' ', '_')
        
        return suggested_key
    
    def find_hardcoded_strings(self, file_content: str) -> List[Tuple[str, int, str]]:
        """
        Findet hardcoded deutsche Strings in Python-Code
        
        Args:
            file_content: Der Dateiinhalt als String
            
        Returns:
            Liste von (text, line_number, suggested_key) Tupeln
        """
        findings = []
        lines = file_content.split('\n')
        
        # Regex für deutsche Strings in Anführungszeichen
        german_pattern = r'["\']([^"\']*[äöüÄÖÜßa-zA-Z][^"\']*)["\']'
        
        for line_num, line in enumerate(lines, 1):
            # Überspringe Kommentare und Imports
            stripped_line = line.strip()
            if (stripped_line.startswith('#') or 
                stripped_line.startswith('import') or 
                stripped_line.startswith('from')):
                continue
            
            matches = re.finditer(german_pattern, line)
            for match in matches:
                text = match.group(1)
                
                # Filter für wahrscheinlich deutsche UI-Texte
                if (len(text) > 3 and 
                    any(german_char in text for german_char in 'äöüÄÖÜß') or
                    any(german_word in text.lower() for german_word in 
                        ['analyse', 'übersicht', 'auswählen', 'herunterladen', 
                         'speichern', 'laden', 'suchen', 'filter'])):
                    
                    suggested_key = self.suggest_translation_key(text)
                    findings.append((text, line_num, suggested_key))
        
        return findings
    
    def generate_migration_report(self, file_path: str) -> str:
        """
        Generiert einen Migration-Report für eine Datei
        
        Args:
            file_path: Pfad zur Python-Datei
            
        Returns:
            Migration-Report als String
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return f"❌ Datei nicht gefunden: {file_path}"
        
        findings = self.find_hardcoded_strings(content)
        
        if not findings:
            return f"✅ {file_path}: Keine hardcoded deutschen Strings gefunden"
        
        report = f"""
📋 **Migration Report für {file_path}**

Gefundene hardcoded deutsche Strings: {len(findings)}

| Zeile | Deutscher Text | Vorgeschlagener Key |
|-------|----------------|---------------------|
"""
        
        for text, line_num, suggested_key in findings:
            report += f"| {line_num} | `{text}` | `{suggested_key}` |\n"
        
        report += f"""
🔄 **Empfohlene Schritte:**
1. Füge Imports hinzu:
   ```python
   from utils.language_switcher_config import init_language, get_text, t
   from utils.language_switcher_ui import language_switcher, setup_standard_page_with_language
   ```

2. Füge in main() ganz oben hinzu:
   ```python
   init_language()
   language_switcher()
   ```

3. Ersetze hardcoded Strings:
   ```python
   # Beispiel:
   # VORHER:
   st.title("Sentiment-Analyse")
   
   # NACHHER:
   st.title(t("sentiment_analysis"))
   ```

4. Neue Übersetzungen zu language_switcher_config.py hinzufügen falls nötig
"""
        
        return report

def quick_migrate_text(text: str) -> str:
    """
    Schnelle Text-Migration für häufige Fälle
    
    Args:
        text: Der zu migrierende Text
        
    Returns:
        Migrierter Text mit t() Aufrufen
    """
    helper = LanguageMigrationHelper()
    
    # Häufige direkte Ersetzungen
    quick_replacements = {
        '"Sentiment-Analyse"': 't("sentiment_analysis")',
        "'Sentiment-Analyse'": 't("sentiment_analysis")',
        '"Themen-Analyse"': 't("topic_analysis")',
        "'Themen-Analyse'": 't("topic_analysis")',
        '"Emotions-Analyse"': 't("emotion_analysis")',
        "'Emotions-Analyse'": 't("emotion_analysis")',
        '"Datenvorschau"': 't("data_preview")',
        "'Datenvorschau'": 't("data_preview")',
        '"Jahr auswählen"': 't("year_select")',
        "'Jahr auswählen'": 't("year_select")',
        '"Land auswählen"': 't("country_select")',
        "'Land auswählen'": 't("country_select")',
        '"Herunterladen"': 't("download")',
        "'Herunterladen'": 't("download")',
        '"Speichern"': 't("save")',
        "'Speichern'": 't("save")',
        '"Laden"': 't("load")',
        "'Laden'": 't("load")',
        '"Suchen"': 't("search")',
        "'Suchen'": 't("search")',
        '"Analysieren"': 't("analyze")',
        "'Analysieren'": 't("analyze")'
    }
    
    result = text
    for old, new in quick_replacements.items():
        result = result.replace(old, new)
    
    return result

def add_missing_translations(new_keys: List[str]) -> str:
    """
    Generiert Code zum Hinzufügen neuer Übersetzungen
    
    Args:
        new_keys: Liste neuer Übersetzungsschlüssel
        
    Returns:
        Python-Code zum Hinzufügen zu TRANSLATIONS
    """
    if not new_keys:
        return "# Keine neuen Übersetzungen nötig"
    
    code = "# Füge diese Übersetzungen zu TRANSLATIONS hinzu:\n\n"
    code += "TRANSLATIONS = {\n"
    code += '    "DE": {\n'
    code += "        # ... bestehende Übersetzungen\n"
    
    for key in new_keys:
        code += f'        "{key}": "TODO: Deutsche Übersetzung",\n'
    
    code += "    },\n"
    code += '    "EN": {\n'
    code += "        # ... bestehende Übersetzungen\n"
    
    for key in new_keys:
        code += f'        "{key}": "TODO: English Translation",\n'
    
    code += "    }\n"
    code += "}\n"
    
    return code

def create_page_migration_template(page_name: str, icon: str, title_key: str = None) -> str:
    """
    Erstellt eine Vorlage für die Migration einer Page
    
    Args:
        page_name: Name der Seite
        icon: Emoji-Icon
        title_key: Übersetzungsschlüssel für Titel
        
    Returns:
        Python-Code-Template
    """
    if not title_key:
        title_key = page_name.lower().replace(' ', '_')
    
    template = f'''# {page_name}.py - MIGRIERTE VERSION

"""
{page_name}
Modernisierte Version mit Sprachunterstützung
"""

import streamlit as st

# === SPRACHSYSTEM IMPORTIEREN ===
from utils.language_switcher_config import init_language, get_text, t
from utils.language_switcher_ui import language_switcher, setup_standard_page_with_language

# === SETUP MIT SPRACHUNTERSTÜTZUNG ===
# Sprache initialisieren
init_language()

# Sprachschalter hinzufügen
language_switcher()

# Page Config
st.set_page_config(
    page_title=f"{page_name} | HerEducation",
    page_icon="{icon}",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Hauptfunktion der Page - Mit Sprachunterstützung"""
    
    # Titel mit Übersetzung
    st.title(f"{icon} {{t('{title_key}')}}")
    
    # Weitere Inhalte mit Übersetzungen...
    # st.header(t("section_header"))
    # st.button(t("action_button"))
    
    # TODO: Bestehenden Content hier mit t() migrieren

if __name__ == "__main__":
    main()
else:
    main()
'''
    
    return template

# Utility-Funktionen für interaktive Migration
def interactive_migration_suggestions():
    """
    Zeigt interaktive Migrations-Vorschläge in Streamlit
    (Kann in einer Debug-Seite verwendet werden)
    """
    import streamlit as st
    
    st.subheader("🔄 Language Switcher Migration Helper")
    
    helper = LanguageMigrationHelper()
    
    # Text-Input für schnelle Migration
    st.write("**Schnelle Text-Migration:**")
    input_text = st.text_area("Python-Code eingeben:", height=200)
    
    if st.button("🔄 Migrieren"):
        if input_text:
            migrated = quick_migrate_text(input_text)
            st.write("**Migrierter Code:**")
            st.code(migrated, language="python")
    
    # Übersetzungsvorschläge
    st.write("**Neuen Übersetzungsschlüssel vorschlagen:**")
    german_text = st.text_input("Deutscher Text:")
    
    if german_text:
        suggested_key = helper.suggest_translation_key(german_text)
        st.write(f"**Vorgeschlagener Key:** `{suggested_key}`")
        st.code(f't("{suggested_key}")', language="python")