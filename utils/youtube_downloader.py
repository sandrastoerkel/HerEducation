"""
Modernisierter YouTube Downloader für 2025
Mit optimaler Cookie-Integration und verstärkten Anti-Detection-Maßnahmen

Autor: Sandra Störkel - HerEducation
Version: 2.2 - Modernisiert mit bewährten Patterns
"""

import os
import re
import time  
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union, Protocol
from dataclasses import dataclass, field
from enum import Enum

import yt_dlp
from yt_dlp import YoutubeDL

# ===== KONSTANTEN STATT MAGIC NUMBERS =====
class DownloadConstants:
    """Zentrale Konstanten für Download-Konfiguration"""
    
    # Qualitäts-Einstellungen
    DEFAULT_AUDIO_QUALITY = "192"
    DEFAULT_AUDIO_FORMAT = "mp3"
    MAX_FILENAME_LENGTH = 150
    
    # Anti-Detection Delays (verstärkt für 2025)
    MIN_DELAY_SECONDS = 3.0
    MAX_DELAY_SECONDS = 7.0
    MIN_MICRO_PAUSE = 0.2
    MAX_MICRO_PAUSE = 0.8
    MICRO_PAUSES_COUNT_MIN = 2
    MICRO_PAUSES_COUNT_MAX = 5
    
    # Retry-Einstellungen
    MAX_RETRIES = 5
    MAX_FRAGMENT_RETRIES = 5
    MAX_FILE_ACCESS_RETRIES = 5
    
    # Suchparameter (reduziert für weniger Erkennung)
    DEFAULT_MAX_RESULTS = 50
    RATE_LIMIT_PAUSE_MIN = 30
    RATE_LIMIT_PAUSE_MAX = 60
    
    # HTTP-Optimierungen
    HTTP_CHUNK_SIZE = 10485760  # 10MB chunks
    
    # Default-Verzeichnisse
    DEFAULT_OUTPUT_DIR = "data/audio"
    DEFAULT_COOKIE_FILE = "cookies.txt"

class UserAgents:
    """2025 User-Agents für Anti-Detection"""
    
    CHROME_2025 = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    ]
    
    FIREFOX_2025 = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
    ]
    
    SAFARI_2025 = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
    ]
    
    EDGE_2025 = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    ]
    
    @classmethod
    def get_all_agents(cls) -> List[str]:
        """Gibt alle verfügbaren User-Agents zurück"""
        return cls.CHROME_2025 + cls.FIREFOX_2025 + cls.SAFARI_2025 + cls.EDGE_2025

class DefaultKeywords:
    """Standard-Keywords für verschiedene Kategorien"""
    EDUCATION = ["Bildung", "Lehrer", "Schule", "Studium", "Lernen"]
    LANZ_EDUCATION = ["Bildung", "Lehrer", "Schule", "Studium", "Lernen"]

# ===== ERWEITERTE KONFIGURATION FÜR 2025 =====
@dataclass
class DownloadConfig:
    """Konfiguration für YouTube-Downloads - Erweitert für 2025"""
    
    # Verzeichnisse
    output_dir: str = DownloadConstants.DEFAULT_OUTPUT_DIR
    cookie_file: str = DownloadConstants.DEFAULT_COOKIE_FILE
    
    # Download-Parameter
    audio_quality: str = DownloadConstants.DEFAULT_AUDIO_QUALITY
    audio_format: str = DownloadConstants.DEFAULT_AUDIO_FORMAT
    max_filename_length: int = DownloadConstants.MAX_FILENAME_LENGTH
    
    # Anti-Detection für 2025
    min_delay: float = DownloadConstants.MIN_DELAY_SECONDS
    max_delay: float = DownloadConstants.MAX_DELAY_SECONDS
    max_retries: int = DownloadConstants.MAX_RETRIES
    
    # Suchparameter
    default_max_results: int = DownloadConstants.DEFAULT_MAX_RESULTS
    default_keywords: List[str] = field(default_factory=lambda: DefaultKeywords.EDUCATION.copy())
    
    def get_retry_sleep_functions(self) -> Dict[str, callable]:
        """Retry-Sleep-Funktionen für verschiedene Fehlertypen"""
        return {
            'http': lambda n: min(4 ** n, 60),
            'fragment': lambda n: min(4 ** n, 60),
            'file_access': lambda n: min(4 ** n, 60),
        }

class DownloadStrategy(Enum):
    """Download-Strategien für verschiedene Szenarien - Erweitert für 2025"""
    STANDARD = "standard"
    ANDROID = "android"
    ANDROID_CREATOR = "android_creator"
    WEB_ONLY = "web_only"
    MOBILE = "mobile"
    IOS = "ios"
    EMBEDDED = "embedded"

class DownloadResult(Enum):
    """Download-Ergebnis Status"""
    SUCCESS = "success"
    ALREADY_EXISTS = "already_exists"
    FAILED = "failed"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"

# ===== DATACLASSES FÜR STRUKTURIERTE DATEN =====
@dataclass
class VideoInfo:
    """Strukturierte Video-Informationen"""
    id: str
    title: str
    duration: int = 0
    uploader: str = "Unknown"
    
    @property
    def duration_formatted(self) -> str:
        """Formatierte Dauer"""
        return f"{self.duration}s" if self.duration else "Unknown"

@dataclass
class DownloadAttempt:
    """Einzelner Download-Versuch"""
    strategy: DownloadStrategy
    success: bool
    message: str
    video_info: Optional[VideoInfo] = None
    filepath: Optional[str] = None

@dataclass
class CookieStatus:
    """Cookie-Datei Status"""
    exists: bool
    file_size: int = 0
    modification_time: Optional[datetime] = None
    has_login_info: bool = False
    
    @property
    def status_emoji(self) -> str:
        """Status als Emoji"""
        if not self.exists:
            return "❌"
        return "✅" if self.has_login_info else "⚠️"

# ===== SPECIALIZED COMPONENTS =====
class FileNameSanitizer:
    """Sichere Dateinamen-Behandlung"""
    
    @staticmethod
    def sanitize_filename(name: str, max_length: int = DownloadConstants.MAX_FILENAME_LENGTH) -> str:
        """Bereinigt einen Dateinamen von ungültigen Zeichen"""
        sanitized = re.sub(r'[^\w\-_. äöüÄÖÜß]', '_', name)
        sanitized = re.sub(r'[_\s]+', '_', sanitized)
        sanitized = sanitized.strip('_. ')[:max_length]
        return sanitized if sanitized else "unknown_title"
    
    @staticmethod
    def extract_broadcast_date_and_clean_title(title: str) -> Tuple[str, str]:
        """Extrahiert Sendedatum aus Titel und bereinigt ihn"""
        date_pattern = r"vom (\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]+)\s*(\d{4})"
        match = re.search(date_pattern, title)
        
        if match:
            day = int(match.group(1))
            month_str = match.group(2).lower()
            year = int(match.group(3))
            
            months = {
                'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
                'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
                'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12
            }
            
            month = months.get(month_str, 0)
            
            if month and 1 <= day <= 31:
                try:
                    dt = datetime(year, month, day)
                    date_str = dt.strftime("%Y-%m-%d")
                    cleaned_title = re.sub(date_pattern, "", title)
                    cleaned_title = re.sub(r'[:\-_\s]+', ' ', cleaned_title).strip()
                    return date_str, cleaned_title
                except ValueError:
                    pass
        
        return "unknown_date", title
    
    @staticmethod
    def get_file_modification_date(filepath: Union[str, Path]) -> str:
        """Gibt Änderungsdatum einer Datei zurück"""
        try:
            path = Path(filepath)
            if path.exists():
                mtime = path.stat().st_mtime
                dt = datetime.fromtimestamp(mtime)
                return dt.strftime("%Y-%m-%d")
        except Exception as e:
            logging.warning(f"Konnte Änderungsdatum nicht ermitteln: {e}")
        
        return "unknown_date"

class CookieManager:
    """Cookie-Datei Management"""
    
    def __init__(self, cookie_file: str):
        self.cookie_file = cookie_file
        self.logger = logging.getLogger(__name__)
    
    def get_cookie_status(self) -> CookieStatus:
        """Prüft Cookie-Datei Status"""
        if not os.path.exists(self.cookie_file):
            return CookieStatus(exists=False)
        
        try:
            file_size = os.path.getsize(self.cookie_file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(self.cookie_file))
            
            # LOGIN_INFO Cookie prüfen
            has_login_info = False
            try:
                with open(self.cookie_file, 'r') as f:
                    content = f.read()
                    has_login_info = 'LOGIN_INFO' in content
            except Exception:
                pass
            
            return CookieStatus(
                exists=True,
                file_size=file_size,
                modification_time=mod_time,
                has_login_info=has_login_info
            )
        except Exception as e:
            self.logger.warning(f"Fehler beim Prüfen der Cookie-Datei: {e}")
            return CookieStatus(exists=False)
    
    def log_cookie_status(self) -> None:
        """Loggt Cookie-Status"""
        status = self.get_cookie_status()
        
        if status.exists:
            self.logger.info(f"✅ Cookie-Datei gefunden: {self.cookie_file}")
            self.logger.info(f"   Größe: {status.file_size} Bytes, Geändert: {status.modification_time.strftime('%Y-%m-%d %H:%M') if status.modification_time else 'Unknown'}")
            
            if status.has_login_info:
                self.logger.info("✅ LOGIN_INFO Cookie gefunden - Authentication sollte funktionieren")
            else:
                self.logger.warning("⚠️ LOGIN_INFO Cookie fehlt - möglicherweise nicht eingeloggt")
        else:
            self.logger.error(f"❌ Cookie-Datei nicht gefunden: {self.cookie_file}")
            self.logger.error("   Downloads werden wahrscheinlich mit 403 Forbidden fehlschlagen!")
            self.logger.error("   Erstelle cookies.txt mit Browser-Extension oder --cookies-from-browser")

class AntiDetectionManager:
    """Anti-Detection Strategien"""
    
    def __init__(self, config: DownloadConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def execute_delay(self) -> None:
        """VERSTÄRKTE Anti-Detection Verzögerung für 2025"""
        # Längere Basis-Verzögerung
        base_delay = random.uniform(self.config.min_delay, self.config.max_delay)
        
        # Zusätzliche zufällige Mikro-Pausen für menschlicheres Verhalten
        micro_pauses = random.randint(
            DownloadConstants.MICRO_PAUSES_COUNT_MIN, 
            DownloadConstants.MICRO_PAUSES_COUNT_MAX
        )
        for _ in range(micro_pauses):
            time.sleep(random.uniform(
                DownloadConstants.MIN_MICRO_PAUSE,
                DownloadConstants.MAX_MICRO_PAUSE
            ))
        
        self.logger.info(f"🛡️ Anti-Detection Pause: {base_delay:.1f}s")
        time.sleep(base_delay)
    
    def get_random_user_agent(self) -> str:
        """Gibt zufälligen User-Agent zurück"""
        return random.choice(UserAgents.get_all_agents())
    
    def execute_strategy_pause(self) -> None:
        """Pause zwischen Download-Strategien"""
        pause_time = random.uniform(2, 5)
        self.logger.info(f"⏳ Pausiere {pause_time:.1f}s vor nächster Strategie...")
        time.sleep(pause_time)
    
    def execute_rate_limit_pause(self) -> None:
        """Längere Pause bei Rate-Limit"""
        pause_time = random.uniform(
            DownloadConstants.RATE_LIMIT_PAUSE_MIN,
            DownloadConstants.RATE_LIMIT_PAUSE_MAX
        )
        self.logger.warning(f"⏱️ Rate-Limit erreicht - pausiere extra lang: {pause_time:.1f}s...")
        time.sleep(pause_time)

class YtDlpOptionsBuilder:
    """Builder für yt-dlp Optionen"""
    
    def __init__(self, config: DownloadConfig, cookie_manager: CookieManager, anti_detection: AntiDetectionManager):
        self.config = config
        self.cookie_manager = cookie_manager
        self.anti_detection = anti_detection
        self.logger = logging.getLogger(__name__)
    
    def build_base_options(self) -> Dict:
        """Erstellt Basis-Optionen für yt-dlp"""
        cookie_status = self.cookie_manager.get_cookie_status()
        
        base_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.config.output_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.config.audio_format,
                'preferredquality': self.config.audio_quality,
            }],
            
            # VERSTÄRKTE Anti-Detection Maßnahmen für 2025
            'user-agent': self.anti_detection.get_random_user_agent(),
            'sleep_interval': self.config.min_delay,
            'max_sleep_interval': self.config.max_delay,
            'retries': self.config.max_retries,
            'fragment_retries': self.config.max_retries,
            'file_access_retries': self.config.max_retries,
            
            # Robustheit
            'ignoreerrors': False,
            'no_warnings': False,
            'extract_flat': False,
            
            # HTTP-Optimierungen für 2025
            'http_chunk_size': DownloadConstants.HTTP_CHUNK_SIZE,
            'retry_sleep_functions': self.config.get_retry_sleep_functions()
        }
        
        # Cookie-Datei hinzufügen wenn verfügbar
        if cookie_status.exists:
            base_opts['cookiefile'] = self.config.cookie_file
            self.logger.info(f"🍪 Verwende Cookie-Datei: {self.config.cookie_file}")
        else:
            self.logger.error(f"❌ Cookie-Datei nicht gefunden: {self.config.cookie_file}")
        
        return base_opts
    
    def build_strategy_options(self, strategy: DownloadStrategy) -> Dict:
        """Erstellt Strategie-spezifische Optionen"""
        base_opts = self.build_base_options()
        
        strategy_configs = {
            DownloadStrategy.ANDROID: {
                'player_client': ['android', 'android_creator'],
                'skip': ['dash']
            },
            DownloadStrategy.ANDROID_CREATOR: {
                'player_client': ['android_creator', 'android'],
                'skip': ['dash', 'hls']
            },
            DownloadStrategy.WEB_ONLY: {
                'player_client': ['web'],
                'skip': ['dash', 'hls']
            },
            DownloadStrategy.MOBILE: {
                'player_client': ['mweb', 'ios'],
                'skip': ['dash']
            },
            DownloadStrategy.IOS: {
                'player_client': ['ios', 'mweb'],
                'skip': ['dash']
            },
            DownloadStrategy.EMBEDDED: {
                'player_client': ['embed'],
                'skip': ['dash', 'hls']
            }
        }
        
        if strategy in strategy_configs:
            base_opts['extractor_args'] = {
                'youtube': strategy_configs[strategy]
            }
        
        return base_opts
    
    def build_search_options(self) -> Dict:
        """Erstellt Optionen für Suche"""
        cookie_status = self.cookie_manager.get_cookie_status()
        
        search_opts = {
            'quiet': True,
            'extract_flat': True,
            'user-agent': self.anti_detection.get_random_user_agent(),
        }
        
        if cookie_status.exists:
            search_opts['cookiefile'] = self.config.cookie_file
            self.logger.info("🍪 Verwende Cookies für Suche")
        
        return search_opts

class ErrorAnalyzer:
    """Analysiert Download-Fehler für bessere Diagnose"""
    
    @staticmethod
    def analyze_error(error_msg: str, strategy: DownloadStrategy) -> Tuple[DownloadResult, str]:
        """Analysiert Fehlermeldung und gibt strukturiertes Ergebnis zurück"""
        error_lower = error_msg.lower()
        
        if "http error 403" in error_lower or "forbidden" in error_lower:
            return DownloadResult.BLOCKED, f"🚫 YouTube blockiert Zugriff - Cookie-Problem? ({strategy.value})"
        elif "http error 429" in error_lower:
            return DownloadResult.RATE_LIMITED, f"⏱️ Rate-Limit erreicht - längere Pause nötig ({strategy.value})"
        elif "sign in to confirm" in error_lower or "not a bot" in error_lower:
            return DownloadResult.BLOCKED, f"🤖 Bot-Erkennung - bessere Cookies nötig ({strategy.value})"
        elif "nsig extraction failed" in error_lower:
            return DownloadResult.FAILED, f"🔧 YouTube Signatur-Problem - yt-dlp aktualisieren ({strategy.value})"
        elif "precondition check failed" in error_lower:
            return DownloadResult.BLOCKED, f"🛡️ YouTube Anti-Bot erkannt - VPN versuchen ({strategy.value})"
        elif "video unavailable" in error_lower:
            return DownloadResult.FAILED, f"📵 Video nicht verfügbar ({strategy.value})"
        else:
            return DownloadResult.FAILED, f"❓ Unbekannter Fehler ({strategy.value}): {error_msg}"

# ===== HAUPTKLASSE - MODERNISIERT =====
class RobustYouTubeDownloader:
    """
    Modernisierter YouTube Downloader mit optimaler Cookie-Integration
    """
    
    def __init__(self, config: DownloadConfig = None):
        self.config = config or DownloadConfig()
        self.sanitizer = FileNameSanitizer()
        self.cookie_manager = CookieManager(self.config.cookie_file)
        self.anti_detection = AntiDetectionManager(self.config)
        self.options_builder = YtDlpOptionsBuilder(self.config, self.cookie_manager, self.anti_detection)
        self._setup_logging()
        self.cookie_manager.log_cookie_status()
    
    def _setup_logging(self) -> None:
        """Konfiguriert Logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _extract_video_info(self, ydl: YoutubeDL, url: str) -> Optional[VideoInfo]:
        """Extrahiert Video-Informationen"""
        try:
            video_info = ydl.extract_info(url, download=False)
            if not video_info:
                return None
            
            return VideoInfo(
                id=video_info.get('id', 'unknown'),
                title=video_info.get('title', 'Unknown Title'),
                duration=video_info.get('duration', 0),
                uploader=video_info.get('uploader', 'Unknown')
            )
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren der Video-Info: {e}")
            return None
    
    def _try_download_with_strategy(self, url: str, strategy: DownloadStrategy) -> DownloadAttempt:
        """Versucht Download mit spezifischer Strategie"""
        try:
            opts = self.options_builder.build_strategy_options(strategy)
            
            with YoutubeDL(opts) as ydl:
                # Video-Info extrahieren
                self.logger.info(f"🔍 Extrahiere Video-Info mit Strategie: {strategy.value}")
                video_info = self._extract_video_info(ydl, url)
                
                if not video_info:
                    return DownloadAttempt(
                        strategy=strategy,
                        success=False,
                        message="Keine Video-Informationen erhalten"
                    )
                
                self.logger.info(f"📺 Video: {video_info.title} von {video_info.uploader} ({video_info.duration_formatted})")
                
                # VERSTÄRKTE Anti-Detection Delay
                self.anti_detection.execute_delay()
                
                # Download durchführen
                ydl.download([url])
                
                return DownloadAttempt(
                    strategy=strategy,
                    success=True,
                    message=f"Download erfolgreich: {video_info.title}",
                    video_info=video_info
                )
                
        except Exception as e:
            result, message = ErrorAnalyzer.analyze_error(str(e), strategy)
            return DownloadAttempt(
                strategy=strategy,
                success=False,
                message=message
            )
    
    def _process_downloaded_file(self, video_info: VideoInfo) -> Optional[str]:
        """Verarbeitet heruntergeladene Datei (umbenennen, etc.)"""
        try:
            # Temporäre Datei finden
            temp_path = Path(self.config.output_dir) / f"{video_info.id}.mp3"
            
            if not temp_path.exists():
                self.logger.error(f"Temporäre Datei nicht gefunden: {temp_path}")
                return None
            
            # Datum und bereinigten Titel extrahieren
            date_str, clean_title = self.sanitizer.extract_broadcast_date_and_clean_title(video_info.title)
            
            if date_str == "unknown_date":
                date_str = self.sanitizer.get_file_modification_date(temp_path)
            
            # Sicheren Dateinamen erstellen
            safe_title = self.sanitizer.sanitize_filename(clean_title, self.config.max_filename_length)
            
            # Finalen Dateinamen erstellen
            final_filename = f"{date_str}_{video_info.id}_{safe_title}.mp3"
            final_path = Path(self.config.output_dir) / final_filename
            
            # Umbenennen (nur wenn Ziel nicht existiert)
            if not final_path.exists():
                temp_path.rename(final_path)
                self.logger.info(f"📁 Datei umbenannt: {final_filename}")
            else:
                # Temp-Datei löschen wenn Ziel bereits existiert
                temp_path.unlink()
                self.logger.info(f"✅ Datei bereits vorhanden: {final_filename}")
            
            return str(final_path)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der Datei: {e}")
            return None
    
    def _get_download_strategies(self) -> List[DownloadStrategy]:
        """Gibt Download-Strategien in der Reihenfolge zurück"""
        return [
            DownloadStrategy.STANDARD,
            DownloadStrategy.ANDROID,
            DownloadStrategy.ANDROID_CREATOR,
            DownloadStrategy.IOS,
            DownloadStrategy.WEB_ONLY,
            DownloadStrategy.MOBILE,
            DownloadStrategy.EMBEDDED
        ]
    
    def download_single_video(self, url: str) -> Tuple[DownloadResult, str, Optional[str]]:
        """Lädt einzelnes Video mit erweiterten Fallback-Strategien herunter"""
        # Verzeichnis erstellen
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"🚀 Starte Download: {url}")
        
        strategies = self._get_download_strategies()
        last_error = "Keine Strategie verfügbar"
        
        for i, strategy in enumerate(strategies, 1):
            self.logger.info(f"🎯 Versuche Strategie {i}/{len(strategies)}: {strategy.value}")
            
            attempt = self._try_download_with_strategy(url, strategy)
            
            if attempt.success and attempt.video_info:
                # Datei verarbeiten und umbenennen
                filepath = self._process_downloaded_file(attempt.video_info)
                if filepath:
                    return DownloadResult.SUCCESS, attempt.message, filepath
            
            last_error = attempt.message
            self.logger.warning(f"⚠️ Strategie {strategy.value} fehlgeschlagen: {attempt.message}")
            
            # Pause zwischen Strategien
            if i < len(strategies):
                self.anti_detection.execute_strategy_pause()
        
        # Ergebnis basierend auf letztem Fehler
        if "403" in last_error or "Forbidden" in last_error:
            return DownloadResult.BLOCKED, f"🚫 Alle Strategien blockiert. Cookie-Problem? Letzter Fehler: {last_error}", None
        elif "429" in last_error:
            return DownloadResult.RATE_LIMITED, f"⏱️ Rate-Limit erreicht. Später versuchen. Letzter Fehler: {last_error}", None
        else:
            return DownloadResult.FAILED, f"❌ Alle Strategien fehlgeschlagen. Letzter Fehler: {last_error}", None
            
    def _filter_videos_by_keywords(self, entries: List[Dict], positive_keywords: List[str]) -> List[Dict]:
        """Filtert Videos nach positiven Keywords"""
        if not positive_keywords:
            return entries
        
        filtered = []
        for entry in entries:
            title = entry.get('title', '').lower()
            if any(keyword.lower() in title for keyword in positive_keywords):
                filtered.append(entry)
            else:
                self.logger.info(f"⏭️ Übersprungen: {entry.get('title', 'Unknown')}")
        
        return filtered
    
    def _check_existing_download(self, video_id: str) -> List[Path]:
        """Prüft ob Video bereits heruntergeladen wurde"""
        if not video_id:
            return []
        
        return list(Path(self.config.output_dir).glob(f"*{video_id}*.mp3"))
    
    def _handle_search_and_download_loop(self, entries: List[Dict], positive_keywords: List[str]) -> List[str]:
        """Hauptschleife für Suche und Download"""
        downloaded_files = []
        filtered_entries = self._filter_videos_by_keywords(entries, positive_keywords)
        
        for i, entry in enumerate(filtered_entries, 1):
            try:
                video_id = entry.get('id')
                entry_title = entry.get('title', 'Unknown')
                
                if not video_id:
                    continue
                
                # Prüfen ob bereits existiert
                existing_files = self._check_existing_download(video_id)
                if existing_files:
                    self.logger.info(f"✅ Bereits vorhanden ({i}/{len(filtered_entries)}): {entry_title}")
                    downloaded_files.extend([str(f) for f in existing_files])
                    continue
                
                # Download versuchen
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                self.logger.info(f"📥 Download ({i}/{len(filtered_entries)}): {entry_title}")
                
                result, message, filepath = self.download_single_video(video_url)
                
                if result == DownloadResult.SUCCESS and filepath:
                    downloaded_files.append(filepath)
                    self.logger.info(f"✅ Erfolgreich ({i}/{len(filtered_entries)}): {os.path.basename(filepath)}")
                elif result == DownloadResult.RATE_LIMITED:
                    self.anti_detection.execute_rate_limit_pause()
                else:
                    self.logger.warning(f"❌ Fehlgeschlagen ({i}/{len(filtered_entries)}): {message}")
                
                # VERSTÄRKTE Pause zwischen Downloads
                if i < len(filtered_entries):
                    enhanced_pause = random.uniform(
                        self.config.min_delay * 1.5, 
                        self.config.max_delay * 1.5
                    )
                    self.logger.info(f"🛡️ Anti-Detection Pause: {enhanced_pause:.1f}s")
                    time.sleep(enhanced_pause)
                
            except Exception as e:
                self.logger.error(f"Fehler bei Video {i}: {e}")
                continue
        
        return downloaded_files
    
    def search_and_download_videos(self, 
                                  query: str,
                                  max_results: int = None,
                                  positive_keywords: List[str] = None) -> List[str]:
        """Sucht und lädt Videos basierend auf Kriterien herunter"""
        if max_results is None:
            max_results = self.config.default_max_results
        
        if positive_keywords is None:
            positive_keywords = self.config.default_keywords
        
        self.logger.info(f"🔍 Starte Suche: '{query}' (max: {max_results})")
        
        # Suche durchführen
        search_query = f"ytsearch{max_results}:{query}"
        search_opts = self.options_builder.build_search_options()
        
        try:
            with YoutubeDL(search_opts) as ydl:
                search_result = ydl.extract_info(search_query, download=False)
                entries = search_result.get('entries', [])
            
            self.logger.info(f"📋 Gefunden: {len(entries)} Videos")
            
        except Exception as e:
            self.logger.error(f"Suche fehlgeschlagen: {e}")
            return []
        
        # Download-Loop
        downloaded_files = self._handle_search_and_download_loop(entries, positive_keywords)
        
        self.logger.info(f"🎉 Download abgeschlossen: {len(downloaded_files)} Dateien")
        return sorted(downloaded_files)

# ===== UTILITY CLASSES =====
class YouTubeDownloadUtility:
    """Utility-Klasse für häufige Download-Szenarien"""
    
    @staticmethod
    def create_education_config(output_dir: str = DownloadConstants.DEFAULT_OUTPUT_DIR) -> DownloadConfig:
        """Erstellt Konfiguration für Bildungsvideos"""
        return DownloadConfig(
            output_dir=output_dir,
            default_keywords=DefaultKeywords.EDUCATION,
            default_max_results=DownloadConstants.DEFAULT_MAX_RESULTS
        )
    
    @staticmethod
    def create_lanz_config(output_dir: str = DownloadConstants.DEFAULT_OUTPUT_DIR) -> DownloadConfig:
        """Erstellt Konfiguration für Lanz-Bildungsvideos"""
        return DownloadConfig(
            output_dir=output_dir,
            default_keywords=DefaultKeywords.LANZ_EDUCATION,
            default_max_results=DownloadConstants.DEFAULT_MAX_RESULTS
        )

# ===== CONVENIENCE FUNCTIONS (Backward-compatible) =====
def search_and_download_videos(query: str, 
                              output_dir: str = DownloadConstants.DEFAULT_OUTPUT_DIR, 
                              positive_keywords: List[str] = None,
                              max_results: int = DownloadConstants.DEFAULT_MAX_RESULTS) -> List[str]:
    """Backward-compatible Funktion für bestehenden Code"""
    config = DownloadConfig(
        output_dir=output_dir, 
        default_max_results=max_results,
        default_keywords=positive_keywords or DefaultKeywords.EDUCATION
    )
    
    downloader = RobustYouTubeDownloader(config)
    return downloader.search_and_download_videos(query, max_results, positive_keywords)

def search_and_download_lanz_bildung(output_dir: str = DownloadConstants.DEFAULT_OUTPUT_DIR, 
                                   positive_keywords: List[str] = None) -> List[str]:
    """Spezialisierte Funktion für Markus Lanz Bildungsvideos"""
    if positive_keywords is None:
        positive_keywords = DefaultKeywords.LANZ_EDUCATION
    
    return search_and_download_videos(
        query="Markus Lanz Bildung",
        output_dir=output_dir,
        positive_keywords=positive_keywords,
        max_results=DownloadConstants.DEFAULT_MAX_RESULTS
    )

def download_video_by_url(url: str, output_dir: str = DownloadConstants.DEFAULT_OUTPUT_DIR) -> Optional[str]:
    """Lädt einzelnes Video per URL herunter"""
    config = DownloadConfig(output_dir=output_dir)
    downloader = RobustYouTubeDownloader(config)
    
    result, message, filepath = downloader.download_single_video(url)
    
    if result == DownloadResult.SUCCESS:
        return filepath
    else:
        logging.error(f"Download fehlgeschlagen: {message}")
        return None

# ===== DIAGNOSE UND TEST FUNKTIONEN =====
class YouTubeDiagnostics:
    """Diagnose-Funktionen für YouTube-Setup"""
    
    @staticmethod
    def diagnose_youtube_setup() -> bool:
        """Diagnostiziert YouTube-Download Setup für 2025"""
        print("🔧 YouTube Download Diagnose 2025")
        print("=" * 40)
        
        # 1. yt-dlp Version prüfen
        try:
            import yt_dlp
            print(f"✅ yt-dlp Version: {yt_dlp.version.__version__}")
        except ImportError:
            print("❌ yt-dlp nicht installiert!")
            return False
        
        # 2. Cookie-Datei prüfen
        config = DownloadConfig()
        cookie_manager = CookieManager(config.cookie_file)
        status = cookie_manager.get_cookie_status()
        
        if status.exists:
            print(f"✅ Cookie-Datei: {config.cookie_file} ({status.file_size} Bytes, {status.modification_time.strftime('%Y-%m-%d %H:%M') if status.modification_time else 'Unknown'})")
            
            if status.has_login_info:
                print("✅ LOGIN_INFO Cookie gefunden")
            else:
                print("⚠️ LOGIN_INFO Cookie fehlt - möglicherweise nicht eingeloggt")
        else:
            print(f"❌ Cookie-Datei nicht gefunden: {config.cookie_file}")
        
        # 3. Verzeichnisse prüfen
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        print(f"✅ Ausgabe-Verzeichnis: {config.output_dir}")
        
        print("\n🎯 Empfehlungen für 2025:")
        print("- Verwende aktuelle cookies.txt mit LOGIN_INFO")
        print("- Längere Pausen zwischen Downloads (3-7s)")
        print("- Weniger Videos auf einmal (max 50)")
        print("- Bei 403-Fehlern: neue Cookies exportieren")
        
        return True
    
    @staticmethod
    def test_single_download(test_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ") -> bool:
        """Testet einen einzelnen Download"""
        print(f"🧪 Teste Download: {test_url}")
        
        result = download_video_by_url(test_url)
        
        if result:
            print(f"✅ Test erfolgreich: {os.path.basename(result)}")
            return True
        else:
            print("❌ Test fehlgeschlagen")
            return False

# ===== BACKWARD-COMPATIBLE FUNCTIONS =====
def diagnose_youtube_setup() -> bool:
    """Backward-compatible Diagnose-Funktion"""
    return YouTubeDiagnostics.diagnose_youtube_setup()

def test_single_download(test_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ") -> bool:
    """Backward-compatible Test-Funktion"""
    return YouTubeDiagnostics.test_single_download(test_url)

# ===== HAUPTFUNKTION FÜR TESTING =====
def main():
    """Hauptfunktion für Testing und direkte Ausführung"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Modernisierter YouTube Video Downloader 2025')
    parser.add_argument('--diagnose', action='store_true', help='Führe System-Diagnose durch')
    parser.add_argument('--test', action='store_true', help='Teste Download-Funktionalität')
    parser.add_argument('--query', '-q', type=str, help='Suchanfrage')
    parser.add_argument('--url', '-u', type=str, help='Video URL')
    parser.add_argument('--output', '-o', type=str, default=DownloadConstants.DEFAULT_OUTPUT_DIR, help='Ausgabe-Verzeichnis')
    parser.add_argument('--max-results', '-m', type=int, default=10, help='Max. Suchergebnisse')
    
    args = parser.parse_args()
    
    if args.diagnose:
        diagnose_youtube_setup()
    elif args.test:
        test_single_download()
    elif args.query:
        print(f"Starte Suche: {args.query}")
        files = search_and_download_videos(
            query=args.query,
            output_dir=args.output,
            max_results=args.max_results
        )
        print(f"Heruntergeladen: {len(files)} Dateien")
        for file in files:
            print(f"  - {os.path.basename(file)}")
    elif args.url:
        print(f"Lade Video: {args.url}")
        filepath = download_video_by_url(args.url, args.output)
        if filepath:
            print(f"Erfolgreich heruntergeladen: {os.path.basename(filepath)}")
        else:
            print("Download fehlgeschlagen")
    else:
        print("Verwende --diagnose, --test, --query oder --url")
        print("Beispiel: python youtube_downloader.py --diagnose")

if __name__ == "__main__":
    main()