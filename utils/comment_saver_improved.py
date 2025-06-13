import subprocess
import json
from pathlib import Path
import pandas as pd
import re
import os
from io import BytesIO

def save_all_comments(audio_dir="audio", comments_dir="comments"):
    """
    REPARIERTE VERSION - Behandelt JSON-Output korrekt!
    
    Sucht alle MP3-Dateien im audio_dir, extrahiert die Video-IDs und speichert
    die YouTube-Kommentare als CSV in comments_dir.
    
    Die CSV-Dateien enthalten folgende Spalten:
    - comment_id: Eindeutige ID des Kommentars
    - author: Name des Autors
    - time: Zeitstempel des Kommentars
    - votes: Anzahl der Likes
    - text: Der eigentliche Kommentartext
    - parent_id: ID des übergeordneten Kommentars (für Antworten)
    - video_id: ID des YouTube-Videos

    Args:
        audio_dir (str): Pfad zum Verzeichnis mit Audiodateien.
        comments_dir (str): Pfad zum Verzeichnis, in dem die Kommentare gespeichert werden.
    
    Returns:
        list: Liste der Pfade zu den erstellten Kommentar-Dateien
    """
    audio_path = Path(audio_dir)
    comments_path = Path(comments_dir)
    
    # Verzeichnis erstellen, falls es nicht existiert
    comments_path.mkdir(parents=True, exist_ok=True)
    
    mp3_files = list(audio_path.glob("*.mp3"))
    created_files = []
    
    if not mp3_files:
        print(f"⚠️ Keine MP3-Dateien gefunden in {audio_path}")
        return created_files
    
    print(f"📁 Gefunden: {len(mp3_files)} MP3-Dateien")
    
    for i, mp3_file in enumerate(mp3_files, 1):
        base_name = mp3_file.stem
        parts = base_name.split("_")
        
        print(f"🔄 Verarbeite ({i}/{len(mp3_files)}): {mp3_file.name}")
        
        if len(parts) < 2:
            print(f"⚠️ Warnung: Datei {mp3_file.name} hat nicht das erwartete Namensschema.")
            continue
        
        video_id = parts[1]
        output_file = comments_path / f"{base_name}.csv"
        
        # Prüfen, ob die Datei bereits existiert und Größe > 0 ist
        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"✅ Kommentare bereits vorhanden: {output_file.name}")
            created_files.append(str(output_file))
            continue
        
        print(f"💬 Lade Kommentare für Video ID {video_id} -> {output_file.name}")
        
        # REPARIERT: Temporäre JSON-Datei (nicht CSV!)
        temp_output = comments_path / f"temp_{video_id}.json"
        
        # REPARIERT: Korrekte Befehlszeile
        cmd = [
            "youtube-comment-downloader",
            "--youtubeid", video_id,
            "--output", str(temp_output),
            "--limit", "1000"  # Limit für Performance
        ]
        
        try:
            print(f"🔧 Führe aus: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            print(f"📊 Return Code: {result.returncode}")
            if result.stdout:
                print(f"📝 Output: {result.stdout[:100]}...")
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr[:100]}...")
            
            if temp_output.exists() and temp_output.stat().st_size > 0:
                print(f"📁 JSON-Datei erstellt: {temp_output.stat().st_size} Bytes")
                
                # REPARIERT: JSON zu CSV konvertieren
                try:
                    comments_data = []
                    
                    # Lese Line-Delimited JSON
                    with open(temp_output, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line:
                                try:
                                    comment = json.loads(line)
                                    
                                    # Konvertiere zu einheitlichem Format
                                    comment_data = {
                                        'comment_id': comment.get('cid', ''),
                                        'author': comment.get('author', ''),
                                        'time': comment.get('time_parsed', comment.get('time', '')),
                                        'likes_count': comment.get('votes', 0),
                                        'text': comment.get('text', ''),
                                        'parent_id': comment.get('parent', ''),
                                        'video_id': video_id
                                    }
                                    comments_data.append(comment_data)
                                    
                                except json.JSONDecodeError as e:
                                    print(f"⚠️ JSON-Fehler in Zeile {line_num}: {e}")
                                    continue
                    
                    if comments_data:
                        # Erstelle DataFrame
                        df = pd.DataFrame(comments_data)
                        
                        print(f"📊 Verarbeitet: {len(df)} Kommentare")
                        
                        # Datenbereinigung
                        # Likes zu numerisch konvertieren
                        df['likes_count'] = pd.to_numeric(df['likes_count'], errors='coerce').fillna(0).astype(int)
                        
                        # Leere Texte entfernen
                        df = df[df['text'].str.strip() != ''].copy()
                        
                        # Parent-ID verarbeiten
                        df['parent_id'] = df['parent_id'].fillna('').astype(str)
                        
                        # Nach Likes sortieren für bessere Analysemöglichkeiten
                        df = df.sort_values('likes_count', ascending=False)
                        
                        # Speichern als CSV (UTF-8 mit BOM für Excel-Kompatibilität)
                        df.to_csv(output_file, index=False, encoding='utf-8-sig')
                        
                        print(f"✅ Kommentare gespeichert und aufbereitet: {output_file.name} ({len(df)} Einträge)")
                        created_files.append(str(output_file))
                        
                        # Zeige Beispiel-Statistiken
                        if len(df) > 0:
                            max_likes = df['likes_count'].max()
                            avg_likes = df['likes_count'].mean()
                            print(f"📊 Statistik: Max Likes: {max_likes}, Avg Likes: {avg_likes:.1f}")
                    else:
                        print(f"⚠️ Keine gültigen Kommentare in JSON gefunden")
                    
                    # Temporäre JSON-Datei löschen
                    temp_output.unlink()
                    
                except Exception as e:
                    print(f"❌ Fehler beim Verarbeiten der JSON-Kommentare: {str(e)}")
                    print(f"💡 JSON-Datei behalten für Debug: {temp_output}")
                    # Bei Fehler JSON-Datei für Debug behalten
                    
            else:
                print(f"❌ Keine Kommentare gefunden für {video_id}")
                if result.stdout:
                    print("Ausgabe:", result.stdout)
                if result.stderr:
                    print("Fehlerausgabe:", result.stderr)
        
        except subprocess.TimeoutExpired:
            print(f"⚠️ Zeitüberschreitung beim Herunterladen der Kommentare für {video_id}")
            # Prüfen, ob teilweise Daten heruntergeladen wurden
            if temp_output.exists() and temp_output.stat().st_size > 0:
                print(f"⚠️ Teilweise JSON-Datei vorhanden: {temp_output}")
        
        except Exception as e:
            print(f"❌ Fehler beim Herunterladen der Kommentare für {video_id}: {str(e)}")
    
    print("🎉 Alle Dateien verarbeitet.")
    print(f"📊 Insgesamt erfolgreich: {len(created_files)} von {len(mp3_files)} Videos")
    return created_files


def analyze_comments(csv_file_path):
    """
    Analysiert eine CSV-Datei mit Kommentaren und gibt grundlegende Statistiken zurück.
    
    Args:
        csv_file_path (str): Pfad zur CSV-Datei
        
    Returns:
        dict: Wörterbuch mit Analysen
    """
    try:
        df = pd.read_csv(csv_file_path)
        
        # Prüfen, ob die erwarteten Spalten vorhanden sind
        if 'text' not in df.columns:
            return {"error": "Keine Textspalte in der CSV-Datei gefunden"}
        
        # Einfache Statistiken berechnen
        stats = {
            "total_comments": len(df),
            "avg_comment_length": int(df['text'].str.len().mean()) if 'text' in df.columns else 0,
            "unique_authors": df['author'].nunique() if 'author' in df.columns else 0,
            "top_commenters": df['author'].value_counts().head(5).to_dict() if 'author' in df.columns else {},
        }
        
        # Likes-Statistiken berechnen, wenn verfügbar
        if 'likes_count' in df.columns:
            likes_series = pd.to_numeric(df['likes_count'], errors='coerce').fillna(0)
            stats["total_likes"] = int(likes_series.sum())
            stats["avg_likes"] = round(likes_series.mean(), 2)
            stats["max_likes"] = int(likes_series.max())
            stats["median_likes"] = int(likes_series.median())
            
            # Kommentar mit den meisten Likes
            if stats["max_likes"] > 0:
                most_liked_idx = likes_series.idxmax()
                most_liked = df.loc[most_liked_idx]
                stats["most_liked_comment"] = {
                    "text": str(most_liked['text'])[:200] + "..." if len(str(most_liked['text'])) > 200 else str(most_liked['text']),
                    "author": str(most_liked.get('author', 'Unbekannt')),
                    "likes": int(likes_series.loc[most_liked_idx])
                }
        
        # Antwort-Statistiken, wenn parent_id vorhanden ist
        if 'parent_id' in df.columns:
            replies = df[df['parent_id'].str.strip() != '']
            stats["replies_count"] = len(replies)
            stats["replies_percentage"] = round((len(replies) / len(df) * 100), 2) if len(df) > 0 else 0
        
        # Zeitliche Verteilung, wenn Zeitstempel vorhanden
        if 'time' in df.columns:
            try:
                df['datetime'] = pd.to_datetime(df['time'], errors='coerce')
                valid_dates = df['datetime'].dropna()
                if len(valid_dates) > 0:
                    stats["oldest_comment"] = valid_dates.min().strftime('%Y-%m-%d')
                    stats["newest_comment"] = valid_dates.max().strftime('%Y-%m-%d')
                    stats["comments_by_date"] = df.groupby(df['datetime'].dt.date).size().to_dict()
            except:
                # Wenn das Parsen des Zeitstempels fehlschlägt, überspringen
                pass
        
        return stats
        
    except Exception as e:
        return {"error": f"Fehler bei der Analyse: {str(e)}"}


# Test-Funktion
def test_single_video_download(video_id="dQw4w9WgXcQ"):
    """
    Testet den Download für ein einzelnes Video
    """
    print(f"🧪 Teste Kommentar-Download für Video-ID: {video_id}")
    
    temp_file = Path(f"test_{video_id}.json")
    
    cmd = [
        "youtube-comment-downloader",
        "--youtubeid", video_id,
        "--output", str(temp_file),
        "--limit", "5"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(f"📊 Return Code: {result.returncode}")
        
        if temp_file.exists():
            print(f"✅ JSON-Datei erstellt: {temp_file.stat().st_size} Bytes")
            
            # Zeige ersten Kommentar
            with open(temp_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if first_line:
                    comment = json.loads(first_line)
                    print(f"📝 Erster Kommentar: {comment.get('text', '')[:100]}...")
            
            # Aufräumen
            temp_file.unlink()
            return True
        else:
            print("❌ Keine Datei erstellt")
            return False
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    # Test-Modus
    print("🧪 Test-Modus")
    test_single_video_download()