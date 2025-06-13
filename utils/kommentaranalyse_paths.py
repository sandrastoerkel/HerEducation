"""
Pfad-Konfiguration speziell für 05_kommentaranalyse_deutsch.py
Automatische Erkennung des App-Verzeichnisses mit relativen Pfaden
"""
from pathlib import Path

def get_app_root():
    """
    Findet das App-Root-Verzeichnis automatisch
    Geht von utils/kommentaranalyse_paths.py aus 1 Ebene nach oben zum Hauptverzeichnis
    """
    # Von utils/kommentaranalyse_paths.py aus eine Ebene hoch
    current_file = Path(__file__)
    app_root = current_file.parent.parent.absolute()
    return app_root

# App-Verzeichnisse
APP_ROOT = get_app_root()
DATA_DIR = APP_ROOT / "data" / "comments"
RESULTS_DIR = APP_ROOT / "saved_results"

# Erstelle Verzeichnisse falls sie nicht existieren
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warnung: Konnte Verzeichnisse nicht erstellen: {e}")

# Debugging-Informationen (können später entfernt werden)
if __name__ == "__main__":
    print(f"🔍 Kommentaranalyse Pfad-Debug:")
    print(f"   App Root: {APP_ROOT}")
    print(f"   Data Dir: {DATA_DIR} (exists: {DATA_DIR.exists()})")
    print(f"   Results Dir: {RESULTS_DIR} (exists: {RESULTS_DIR.exists()})")