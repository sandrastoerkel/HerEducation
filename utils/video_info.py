"""
YouTube-Video zur Kommentaranalyse (DE/EN) – Review M4/N6, 25.09.2026.

- Video-Infos (Titel, Aufrufe ...) holt yt-dlp von youtube.com. Frueher bei JEDEM
  Seitenaufruf/Klick, ungecacht. Jetzt: hoechstens einmal pro Tag und Video (st.cache_data),
  in der Streamlit-Cloud gar nicht (dort oft blockiert, kostet CPU) – dort nur das
  eingebettete Video.
- Video-ID nur fuer mitgelieferte Dateien und Beispiele (N6), nicht fuer Upload-Namen.
"""
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Optional

import streamlit as st

from utils.live_comment_analysis import is_cloud
from utils.safe_log import log_exception

INFO_KEYS = ("title", "view_count", "upload_date", "duration", "uploader", "description",
             "thumbnail", "channel_id", "category", "tags")

TEXTS = {
    "de": {"title": "YouTube-Video", "cloud_note": "Video-Details (Titel, Aufrufe, Beschreibung) stehen direkt auf YouTube."},
    "en": {"title": "YouTube video", "cloud_note": "Video details (title, views, description) are available on YouTube."},
}


class _QuietLogger:
    """yt-dlp soll nichts ins Log schreiben (Fehlertyp loggt log_exception)."""

    def debug(self, msg):
        pass

    info = warning = error = debug


@st.cache_data(ttl=86400, show_spinner=False, max_entries=50)
def extract_info_cached(video_id: str) -> Optional[dict]:
    """yt-dlp extract_info, gecacht; None bei Fehler (nur Fehlertyp ins Log)."""
    try:
        from yt_dlp import YoutubeDL
    except ImportError:
        return None
    try:
        opts = {"quiet": True, "no_warnings": True, "extract_flat": False, "socket_timeout": 10,
                "logger": _QuietLogger()}
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return {k: info.get(k) for k in INFO_KEYS if info.get(k) is not None}
    except Exception as error:  # noqa: BLE001
        log_exception("video-info", error)
        return None


def _video_id_from_name(name: str) -> Optional[str]:
    match = re.search(r"_([a-zA-Z0-9_-]{11})_", name) or re.search(r"_([a-zA-Z0-9_-]{11})", name)
    return match.group(1) if match else None


def video_id_for_display(filename: Optional[str], known_names: Iterable[str]) -> Optional[str]:
    """Video-ID nur, wenn der Dateiname zu einer mitgelieferten Datei/einem Beispiel gehoert (N6)."""
    if not filename:
        return None
    def norm(value) -> str:
        return unicodedata.normalize("NFC", Path(str(value)).name)
    name = norm(filename)
    if name not in {norm(n) for n in known_names}:
        return None
    return _video_id_from_name(name)


def render_video(video_id: str, lang: str, youtube_manager) -> None:
    """Cloud: nur eingebettetes Video. Lokal: bisherige Anzeige mit (gecachten) Video-Infos."""
    if not video_id:
        return
    if not is_cloud():
        youtube_manager.display_youtube_info(video_id)
        return
    t = TEXTS[lang]
    with st.expander(t["title"], expanded=True):
        st.markdown(
            f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" '
            'frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; '
            'picture-in-picture" allowfullscreen></iframe>',
            unsafe_allow_html=True,
        )
        st.caption(t["cloud_note"])
