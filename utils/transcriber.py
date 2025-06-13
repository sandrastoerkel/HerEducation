import os
import whisper
import pandas as pd
from pathlib import Path

def transcribe_audio(audio_path: str, output_dir: str) -> str:
    """
    Transkribiert eine Audiodatei mit Whisper (medium Modell) und speichert das Transkript als TXT und CSV.

    Args:
        audio_path (str): Pfad zur Audiodatei (.mp3).
        output_dir (str): Zielverzeichnis für die gespeicherten Transkripte.

    Returns:
        str: Pfad zur gespeicherten CSV-Transkriptdatei.
    """
    model = whisper.load_model("medium")

    audio_path = Path(audio_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = model.transcribe(str(audio_path.resolve()), language="de")

    base_name = audio_path.stem

    txt_path = output_dir / f"{base_name}.txt"
    csv_path = output_dir / f"{base_name}.csv"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    segments = pd.DataFrame(result['segments'])
    segments[['start', 'end', 'text']].to_csv(csv_path, index=False, encoding="utf-8")

    return str(csv_path)

def transcribe_all_audios(audio_dir: str = "audio",
                          output_dir: str = "transcripts"):
    """
    Transkribiert alle Audiodateien in einem Verzeichnis.

    Args:
        audio_dir (str): Verzeichnis mit MP3-Dateien.
        output_dir (str): Zielverzeichnis für Transkripte.
        
    Returns:
        list: Liste der Pfade zu den erstellten Transkript-Dateien
    """
    audio_dir = Path(audio_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mp3_files = list(audio_dir.glob("*.mp3"))
    created_files = []

    if not mp3_files:
        print(f"⚠️ Keine MP3-Dateien gefunden in {audio_dir}")
        return created_files

    for audio_file in mp3_files:
        # Prüfen, ob das Transkript bereits existiert
        base_name = audio_file.stem
        txt_path = output_dir / f"{base_name}.txt"
        csv_path = output_dir / f"{base_name}.csv"
        
        if txt_path.exists() and csv_path.exists() and txt_path.stat().st_size > 0:
            print(f"✅ Transkript bereits vorhanden: {txt_path.name}")
            created_files.append(str(csv_path))
            continue
        
        print(f"🔄 Verarbeite: {audio_file.name}")
        try:
            csv_path = transcribe_audio(audio_file, output_dir)
            print(f"✅ Transkript gespeichert: {csv_path}")
            created_files.append(csv_path)
        except Exception as e:
            print(f"❌ Fehler bei der Transkription von {audio_file.name}: {str(e)}")
    
    print("🎉 Alle Audiodateien verarbeitet.")
    return created_files

def analyze_transcript(transcript_path: str):
    """
    Analysiert ein Transkript und gibt grundlegende Statistiken zurück.
    
    Args:
        transcript_path (str): Pfad zur Transkript-Datei (TXT oder CSV)
        
    Returns:
        dict: Wörterbuch mit Analysen
    """
    try:
        path = Path(transcript_path)
        
        # TXT-Datei für Volltext
        if path.suffix.lower() == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            # Überprüfen, ob auch eine CSV-Datei existiert
            csv_path = path.with_suffix('.csv')
            has_segments = csv_path.exists()
            
        # CSV-Datei für segmentierte Daten
        elif path.suffix.lower() == '.csv':
            csv_path = path
            # Überprüfen, ob auch eine TXT-Datei existiert
            txt_path = path.with_suffix('.txt')
            
            if txt_path.exists():
                with open(txt_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
            else:
                # Wenn keine TXT-Datei existiert, Text aus CSV zusammenfügen
                segments_df = pd.read_csv(csv_path)
                transcript_text = ' '.join(segments_df['text'].astype(str))
            
            has_segments = True
        else:
            return {"error": "Unterstützt nur .txt oder .csv Dateien"}
        
        # Grundlegende Textanalyse
        import re
        words = re.findall(r'\b\w+\b', transcript_text.lower())
        sentences = re.split(r'[.!?]+', transcript_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        stats = {
            "total_words": len(words),
            "total_sentences": len(sentences),
            "avg_sentence_length": round(len(words) / len(sentences), 1) if sentences else 0,
            "transcript_length": len(transcript_text)
        }
        
        # Häufige Wörter analysieren
        from collections import Counter
        
        # Stopwords für Deutsch
        german_stopwords = set([
            "der", "die", "das", "dem", "den", "des", "ein", "eine", "einen", "einer", "eines",
            "in", "im", "und", "oder", "aber", "denn", "wenn", "als", "an", "am", "auf", "für",
            "mit", "zu", "zur", "zum", "von", "vom", "bei", "ist", "sind", "war", "waren", "wird",
            "werden", "hat", "haben", "hatte", "hatten", "ich", "du", "er", "sie", "es", "wir",
            "ihr", "sie", "mich", "dich", "sich", "uns", "euch", "mir", "dir", "ihm", "ihr",
            "ihnen", "mein", "dein", "sein", "ihre", "unser", "euer", "nicht", "auch", "schon",
            "noch", "nur", "so", "da", "hier", "dort", "dann", "doch", "mal", "ja", "nein",
            "dass", "was", "wer", "wie", "warum", "wo", "wann", "welche", "welcher", "man"
        ])
        
        # Wortfrequenzen ohne Stopwords
        word_freq = Counter([word for word in words if word not in german_stopwords and len(word) > 2])
        stats["top_words"] = dict(word_freq.most_common(20))
        
        # Zeitbasierte Analyse, wenn Segmente verfügbar sind
        if has_segments:
            try:
                segments_df = pd.read_csv(csv_path)
                
                if 'start' in segments_df.columns and 'end' in segments_df.columns:
                    total_duration = segments_df['end'].max()
                    stats["duration_seconds"] = total_duration
                    
                    # Formatierte Dauer
                    hours, remainder = divmod(total_duration, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    stats["duration_formatted"] = f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
                    
                    # Worte pro Minute
                    stats["words_per_minute"] = round(len(words) / (total_duration / 60), 1)
                    
                    # Segmentierte Analyse
                    if 'text' in segments_df.columns:
                        segments_df['word_count'] = segments_df['text'].apply(
                            lambda x: len(re.findall(r'\b\w+\b', str(x)))
                        )
                        segments_df['duration'] = segments_df['end'] - segments_df['start']
                        segments_df['words_per_minute'] = segments_df.apply(
                            lambda row: (row['word_count'] / row['duration'] * 60) if row['duration'] > 0 else 0, 
                            axis=1
                        )
                        
                        stats["avg_segment_duration"] = round(segments_df['duration'].mean(), 2)
                        stats["avg_words_per_segment"] = round(segments_df['word_count'].mean(), 1)
                        stats["avg_speaking_rate"] = round(segments_df['words_per_minute'].mean(), 1)
                        stats["max_speaking_rate"] = round(segments_df['words_per_minute'].max(), 1)
                        stats["min_speaking_rate"] = round(segments_df['words_per_minute'].min(), 1)
                        
                        # Zeitbasierte Verteilung für Visualisierungen
                        bins = 10  # Anzahl der Zeitabschnitte
                        bin_size = total_duration / bins if total_duration > 0 else 1
                        
                        speaking_rate_bins = []
                        for i in range(bins):
                            start_time = i * bin_size
                            end_time = (i + 1) * bin_size
                            
                            bin_segments = segments_df[
                                (segments_df['start'] >= start_time) & 
                                (segments_df['start'] < end_time)
                            ]
                            
                            if not bin_segments.empty:
                                avg_rate = bin_segments['words_per_minute'].mean()
                            else:
                                avg_rate = 0
                            
                            speaking_rate_bins.append({
                                "time_range": f"{int(start_time/60)}:{int(start_time%60):02d}-{int(end_time/60)}:{int(end_time%60):02d}",
                                "speaking_rate": round(avg_rate, 1)
                            })
                        
                        stats["speaking_rate_over_time"] = speaking_rate_bins
            except Exception as e:
                stats["segment_analysis_error"] = str(e)
                
        return stats
    except Exception as e:
        return {"error": f"Fehler bei der Analyse: {str(e)}"}

if __name__ == "__main__":
    # Beispielaufruf
    transcribed_files = transcribe_all_audios("data/audio", "data/transcripts")
    print(f"Transkribierte Dateien: {transcribed_files}")
    
    # Analyse eines Transkripts, falls vorhanden
    if transcribed_files:
        sample_analysis = analyze_transcript(transcribed_files[0])
        print("\nBeispielanalyse für", transcribed_files[0])
        for key, value in sample_analysis.items():
            if isinstance(value, dict) and len(value) > 5:
                print(f"{key}: {len(value)} Einträge")
            else:
                print(f"{key}: {value}")