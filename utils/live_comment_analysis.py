"""
Live-Analyse fuer die Kommentaranalyse-Seiten (DE/EN) – robuster Ablauf.

Warum (Diagnose 25.09.2026): Frueher lief die Analyse nur in dem einen Skript-Durchlauf
direkt nach dem Klick, `st.session_state.df` wurde schon VOR der Analyse gesetzt und
mitten im Ablauf standen Regler. Jede Bedienung oder Neuverbindung waehrend der Analyse
startete die Seite neu; sie zeigte dann halbfertige Daten mit der irrefuehrenden
Meldung "Sentiment-Analyse-Modul nicht verfuegbar".

Neuer Ablauf (Zustaende je Sprache in st.session_state):
  Formular "Analyse starten" -> status "pending" (Datei als Bytes gemerkt) -> Neustart
  -> status "running": Analyse ohne Bedienelemente, mit Fortschritt
  -> Ergebnis wird ERST NACH dem vollstaendigen Lauf in die Sitzung geschrieben -> "done"
  Wird der Lauf unterbrochen, steht status noch auf "running" -> ehrliche Meldung
  "Analyse wurde unterbrochen" statt halbfertiger Anzeige.

Einstellungen (Umgebungsvariable oder st.secrets):
  HEREDUCATION_LIVE_ANALYSIS / live_analysis        -> 0 schaltet die Live-Analyse ab (Standard: an)
  HEREDUCATION_LIVE_MAX_COMMENTS / live_max_comments -> Obergrenze Kommentare je Lauf
      (Standard: Cloud 100 – Entscheidung Sandra 26.09.2026 nach Cloud-Test (CPU-Drosselung
      schon nach 2 Laeufen a 300); lokal ohne Grenze; 0 = ohne Grenze)
  HEREDUCATION_LIVE_COOLDOWN_SECONDS / live_cooldown_seconds -> Pause nach jedem Live-Lauf fuer die
      ganze App (Standard: Cloud 300 s – Entscheidung Sandra 28.09.2026 nach Cloud-Nachtest B2
      (CPU-Drosselung nach ~5 Laeufen a 100 in ~10 Min.); lokal keine Pause; 0 = keine Pause)
"""
import gc
import os
import threading
import time
from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from utils.safe_log import log_exception

try:  # Streamlit 1.45: st.stop() wirft StopException (BaseException, nicht Exception)
    from streamlit.runtime.scriptrunner_utils.exceptions import StopException
except ImportError:  # pragma: no cover – andere Streamlit-Version
    StopException = None

CLOUD_DEFAULT_MAX_COMMENTS = 100   # Entscheidung Sandra 26.09.2026 (Cloud-Test B2: Drosselung nach 2 Laeufen a 300)
SAMPLE_SEED = 42                   # feste Stichprobe -> gleiche Datei = gleiche Auswahl
SENTIMENT_FAIL_LIMIT = 0.5         # mehr als die Haelfte ohne Modell-Ergebnis -> Lauf gilt als gescheitert (M6)
MAX_UPLOAD_MB = 10                 # passt zu server.maxUploadSize in .streamlit/config.toml
CLOUD_DEFAULT_COOLDOWN_SECONDS = 300  # B2: Pause nach jedem Live-Lauf (Entscheidung Sandra 28.09.2026: 5 Min.)
COOLDOWN_MIN_RUN_SECONDS = 10      # kuerzere Laeufe (z. B. Datei nicht lesbar) haben kaum gerechnet -> keine Pause


class LiveAnalysisError(Exception):
    """Fehler mit einer Meldung, die direkt den Besucher:innen gezeigt werden kann."""


# ---------------------------------------------------------------------------
# Einstellungen
# ---------------------------------------------------------------------------

def is_cloud() -> bool:
    """Streamlit Community Cloud legt die App unter /mount/src ab."""
    return Path("/mount/src").exists()


def _setting(env_name: str, secret_name: str) -> Optional[str]:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    try:
        if secret_name in st.secrets:
            return str(st.secrets[secret_name])
    except Exception:
        pass
    return None


def live_analysis_enabled() -> bool:
    value = _setting("HEREDUCATION_LIVE_ANALYSIS", "live_analysis")
    if value is None:
        return True
    return value.strip().lower() in ("1", "true", "yes", "on")


def live_max_comments() -> Optional[int]:
    value = _setting("HEREDUCATION_LIVE_MAX_COMMENTS", "live_max_comments")
    if value is not None:
        try:
            number = int(str(value).strip())
            return number if number > 0 else None
        except ValueError:
            pass
    return CLOUD_DEFAULT_MAX_COMMENTS if is_cloud() else None


def live_cooldown_seconds() -> int:
    """Pause nach jedem Live-Lauf fuer die ganze App (B2)."""
    value = _setting("HEREDUCATION_LIVE_COOLDOWN_SECONDS", "live_cooldown_seconds")
    if value is not None:
        try:
            return max(0, int(str(value).strip()))
        except ValueError:
            pass
    return CLOUD_DEFAULT_COOLDOWN_SECONDS if is_cloud() else 0


def limit_comments(df: pd.DataFrame, max_comments: Optional[int]) -> Tuple[pd.DataFrame, int]:
    """Feste Zufallsstichprobe (Reihenfolge der Datei bleibt erhalten), wenn die Datei zu gross ist."""
    total = len(df)
    if not max_comments or total <= max_comments:
        return df, total
    sample = df.sample(n=max_comments, random_state=SAMPLE_SEED).sort_index().reset_index(drop=True)
    return sample, total


# ---------------------------------------------------------------------------
# Texte
# ---------------------------------------------------------------------------

TEXTS = {
    "de": {
        "section_title": "🔬 Eigene Analyse starten",
        "section_caption": "Die Live-Analyse rechnet mit drei KI-Modellen (Sentiment, Emotionen, Themen).",
        "limit_note": ("In der kostenlosen Online-Version werden höchstens {n} Kommentare je Lauf analysiert; "
                       "bei größeren Dateien eine feste Stichprobe. Je nach Auslastung dauert ein Lauf einige Minuten."),
        "source_label": "Datenquelle",
        "source_repo": "Mitgelieferte Datei",
        "source_upload": "Eigene Datei hochladen",
        "repo_select": "Mitgelieferte Datei (bei Quelle „Mitgelieferte Datei“):",
        "upload_label": f"Eigene CSV- oder JSON-Datei (bei Quelle „Eigene Datei hochladen“, max. {MAX_UPLOAD_MB} MB):",
        "start": "▶️ Analyse starten",
        "need_upload": "Bitte zuerst eine Datei hochladen – oder als Quelle „Mitgelieferte Datei“ wählen.",
        "too_big": f"Die Datei ist größer als {MAX_UPLOAD_MB} MB.",
        "no_repo_files": "Keine mitgelieferten Dateien gefunden.",
        "running_title": "⏳ Analyse läuft",
        "running_info": "Bitte die Seite während der Analyse nicht bedienen oder neu laden – sonst wird der Lauf abgebrochen.",
        "step": "**Schritt {i}/{n}:** {label}",
        "sample_note": "Die Datei enthält {total} Kommentare – analysiert wurde eine feste Stichprobe von {n}.",
        "duration": "Dauer der Analyse: {sec} s",
        "done": "✅ Eigene Analyse fertig: {name} · {n} Kommentare",
        "interrupted": ("⚠️ Die Analyse wurde unterbrochen (Seite bedient, neu geladen oder Verbindung getrennt) – "
                        "zuletzt bei: {stage}. Bitte unten erneut starten."),
        "failed": "⚠️ Die Analyse konnte nicht abgeschlossen werden: {msg}",
        "unexpected": "Unerwarteter Fehler ({err}). Bitte mit einer kleineren Datei erneut versuchen.",
        "download": "⬇️ Ergebnis als CSV herunterladen",
        "stage_unknown": "unbekannter Schritt",
        "busy": ("⏳ Gerade läuft eine andere Analyse auf diesem Server. Ein Lauf dauert einige Minuten, "
                 "bei hoher Serverauslastung auch deutlich länger. Die Auswahl bleibt gemerkt – "
                 "bitte später auf „Erneut versuchen“ klicken."),
        "retry": "🔄 Erneut versuchen",
        "cooldown": ("⏸️ Die kostenlose Online-Version legt nach jeder Analyse eine Pause von {pause} Minuten ein, "
                     "damit der Server nicht gedrosselt wird. Die nächste Analyse ist in etwa {min} "
                     "{min_word} möglich. Die Auswahl bleibt gemerkt – bitte dann auf „Erneut versuchen“ klicken."),
        "cooldown_hint": ("⏸️ Pause nach der letzten Analyse: Die nächste Analyse ist in etwa {min} {min_word} "
                          "möglich (die kostenlose Online-Version pausiert nach jedem Lauf {pause} Minuten)."),
        "minute": ("Minute", "Minuten"),
        "cooldown_over": "✅ Die Pause ist vorbei – bitte auf „Erneut versuchen“ klicken.",
        "stopped": "Die Analyse wurde vorzeitig beendet.",
        "no_comments": "Nach dem Filtern sind keine Kommentare übrig.",
        "sentiment_failed": "Das Sentiment-Modell hat für die meisten Kommentare kein Ergebnis geliefert.",
        "sentiment_partial": ("Für {k} von {n} Kommentaren lieferte das Sentiment-Modell kein Ergebnis "
                              "(als „neutral“ mit Konfidenz 0 gezählt)."),
    },
    "en": {
        "section_title": "🔬 Run your own analysis",
        "section_caption": "The live analysis uses three AI models (sentiment, emotions, topics).",
        "limit_note": ("The free online version analyses at most {n} comments per run; larger files use a fixed sample. "
                       "Depending on server load a run takes a few minutes."),
        "source_label": "Data source",
        "source_repo": "Included file",
        "source_upload": "Upload your own file",
        "repo_select": "Included file (for source “Included file”):",
        "upload_label": f"Your CSV or JSON file (for source “Upload your own file”, max. {MAX_UPLOAD_MB} MB):",
        "start": "▶️ Start analysis",
        "need_upload": "Please upload a file first – or choose “Included file” as the source.",
        "too_big": f"The file is larger than {MAX_UPLOAD_MB} MB.",
        "no_repo_files": "No included files found.",
        "running_title": "⏳ Analysis running",
        "running_info": "Please do not interact with or reload the page during the analysis – that would cancel the run.",
        "step": "**Step {i}/{n}:** {label}",
        "sample_note": "The file contains {total} comments – a fixed sample of {n} was analysed.",
        "duration": "Analysis time: {sec} s",
        "done": "✅ Your analysis is ready: {name} · {n} comments",
        "interrupted": ("⚠️ The analysis was interrupted (page used, reloaded or connection lost) – "
                        "last step: {stage}. Please start it again below."),
        "failed": "⚠️ The analysis could not be completed: {msg}",
        "unexpected": "Unexpected error ({err}). Please try again with a smaller file.",
        "download": "⬇️ Download result as CSV",
        "stage_unknown": "unknown step",
        "busy": ("⏳ Another analysis is currently running on this server. A run takes a few minutes, "
                 "much longer when the server is busy. Your selection is kept – "
                 "please click “Try again” later."),
        "retry": "🔄 Try again",
        "cooldown": ("⏸️ The free online version pauses for {pause} minutes after each analysis so that the server "
                     "is not throttled. The next analysis is possible in about {min} {min_word}. "
                     "Your selection is kept – please click “Try again” then."),
        "cooldown_hint": ("⏸️ Pause after the last analysis: the next analysis is possible in about {min} {min_word} "
                          "(the free online version pauses for {pause} minutes after each run)."),
        "minute": ("minute", "minutes"),
        "cooldown_over": "✅ The pause is over – please click “Try again”.",
        "stopped": "The analysis was stopped early.",
        "no_comments": "No comments remain after filtering.",
        "sentiment_failed": "The sentiment model returned no result for most comments.",
        "sentiment_partial": ("The sentiment model returned no result for {k} of {n} comments "
                              "(counted as “neutral” with confidence 0)."),
    },
}


def fmt_int(n: int, lang: str) -> str:
    """Nur die Zahl formatieren (Review N8): DE 1.234, EN 1,234."""
    text = f"{int(n):,}"
    return text.replace(",", ".") if lang == "de" else text


def _keys(lang: str) -> Dict[str, str]:
    return {name: f"live_{lang}_{name}"
            for name in ("status", "request", "error", "notes", "stage", "ignore_submit")}


def sample_note(lang: str, total: int, n: int) -> str:
    return TEXTS[lang]["sample_note"].format(total=fmt_int(total, lang), n=fmt_int(n, lang))


# ---------------------------------------------------------------------------
# Speicher und Parallelbetrieb (Review M3/N3)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _run_lock() -> threading.Lock:
    """Ein Lock fuer den ganzen App-Prozess: hoechstens eine Live-Analyse gleichzeitig."""
    return threading.Lock()


class Cooldown:
    """Pause nach jedem Live-Lauf fuer den ganzen App-Prozess (B2, Cloud-Nachtest 28.09.2026).

    Reines Python, kein st.*-Zugriff: mark() darf im finally-Block einer abgebrochenen Sitzung
    laufen, ohne StopException auszuloesen (siehe B1)."""

    def __init__(self):
        self.ready_at = 0.0

    def mark(self, started: Optional[float], seconds: int, now: Optional[float] = None) -> None:
        now = time.time() if now is None else now
        if started is not None and seconds > 0 and now - started >= COOLDOWN_MIN_RUN_SECONDS:
            self.ready_at = max(self.ready_at, now + seconds)

    def remaining(self, now: Optional[float] = None) -> float:
        now = time.time() if now is None else now
        return max(0.0, self.ready_at - now)


@st.cache_resource(show_spinner=False)
def _cooldown() -> Cooldown:
    return Cooldown()


def _minutes_text(lang: str, seconds: float) -> Dict[str, object]:
    minutes = max(1, int(-(-seconds // 60)))        # aufrunden, mindestens 1
    words = TEXTS[lang]["minute"]
    pause = max(1, round(live_cooldown_seconds() / 60))
    return {"min": minutes, "min_word": words[0] if minutes == 1 else words[1], "pause": pause}


def free_other_language_models(lang: str) -> None:
    """Vor dem Laden der Modelle einer Sprache die der anderen Sprache freigeben."""
    try:
        if lang == "de":
            from models import model_loader_english as other
        else:
            from models import model_loader as other
        other.clear_models()
    except Exception as error:  # noqa: BLE001
        log_exception(f"live-analysis {lang}", error, "free_other_language_models")
    gc.collect()


def check_sentiment_result(df: pd.DataFrame, lang: str, notes: List[str]) -> None:
    """Sentiment-Totalausfall erkennen (Review M6): Die Analyzer machen aus jeder Modell-Ausnahme
    still "neutral" mit Konfidenz 0.0 – das darf nicht als fertiges Ergebnis durchgehen."""
    t = TEXTS[lang]
    if len(df) == 0:
        raise LiveAnalysisError(t["no_comments"])
    if "confidence" not in df.columns:
        raise LiveAnalysisError(t["sentiment_failed"])
    failed = int((pd.to_numeric(df["confidence"], errors="coerce").fillna(0) <= 0).sum())
    if failed > len(df) * SENTIMENT_FAIL_LIMIT:
        raise LiveAnalysisError(t["sentiment_failed"])
    if failed:
        notes.append(t["sentiment_partial"].format(k=fmt_int(failed, lang), n=fmt_int(len(df), lang)))


# ---------------------------------------------------------------------------
# Fortschritt
# ---------------------------------------------------------------------------

class Progress:
    """Zeigt die Schritte an und merkt sich den aktuellen Schritt fuer die Unterbrechungs-Meldung."""

    def __init__(self, lang: str, steps: List[str]):
        self.lang = lang
        self.steps = steps
        self.key = _keys(lang)["stage"]

    def step(self, index: int) -> None:
        label = self.steps[index]
        st.session_state[self.key] = label
        st.markdown(TEXTS[self.lang]["step"].format(i=index + 1, n=len(self.steps), label=label))


# ---------------------------------------------------------------------------
# Ablauf
# ---------------------------------------------------------------------------

Runner = Callable[[BytesIO, Dict, "Progress"], Dict]


def run_pending_analysis(lang: str, runner: Runner, steps: List[str]) -> None:
    """Am Anfang von main() aufrufen. Fuehrt eine angeforderte Analyse aus und startet die Seite danach neu.

    runner(file_obj, request, progress) muss ein dict mit df, text_column, additional_data, notes liefern
    und darf KEINE Bedienelemente anzeigen.
    """
    k = _keys(lang)
    t = TEXTS[lang]
    status = st.session_state.get(k["status"])

    if status == "running":
        # Der letzte Lauf wurde nicht zu Ende gefuehrt (Neustart der Seite waehrend der Analyse)
        st.session_state[k["status"]] = "interrupted"
        return
    if status != "pending":
        return

    if not st.session_state.get(k["request"]):
        st.session_state.pop(k["request"], None)
        st.session_state[k["status"]] = None
        return

    # B2: Pause nach dem letzten Lauf? Vor acquire() pruefen – so bleibt kein st.*-Zugriff
    # zwischen acquire() und try (B1). Die Anfrage bleibt erhalten wie bei "busy".
    cooldown = _cooldown()
    cooldown_seconds = live_cooldown_seconds()
    if cooldown.remaining() > 0:
        st.session_state[k["status"]] = "cooldown"
        return

    lock = _run_lock()
    if not lock.acquire(blocking=False):
        # Eine andere Sitzung rechnet gerade – nicht parallel starten (RAM/CPU der Cloud).
        # Die Anfrage bleibt erhalten; "Erneut versuchen" startet sie ohne neue Auswahl
        # (Nachreview NEU7, 26.09.2026: frueher war sie hier schon verworfen).
        st.session_state[k["status"]] = "busy"
        return
    finished = False
    started = None
    try:
        # Ab hier ist jeder st.*-Zugriff im try: Auch ein Abbruch genau jetzt gibt den Lock frei.
        # Erst mit dem Lock die Anfrage (Datei-Bytes) aus der Sitzung nehmen
        request = st.session_state.pop(k["request"])
        st.session_state[k["status"]] = "running"
        st.session_state[k["stage"]] = None
        st.subheader(t["running_title"])
        st.info(t["running_info"])
        started = time.time()
        file_obj = BytesIO(request["data"])
        file_obj.name = request["name"]
        progress = Progress(lang, steps)
        try:
            result = runner(file_obj, request, progress)
        except BaseException as error:
            # Schutz fuer st.stop() aus Alt-Funktionen (Review M5a). Achtung: Nach st.stop()
            # verwirft Streamlit weitere Aenderungen dieses Durchlaufs (in AppTest belegt) –
            # darum ist st.stop() im Live-Pfad entfernt; dies ist nur die letzte Absicherung.
            if StopException is not None and isinstance(error, StopException):
                raise LiveAnalysisError(t["stopped"]) from None
            raise

        df = result["df"]
        # Erst jetzt, nach dem vollstaendigen Lauf, in die Sitzung schreiben
        st.session_state.df = df
        st.session_state.text_column = result["text_column"]
        st.session_state.additional_data = result.get("additional_data") or {}
        st.session_state.current_file = request["name"]
        st.session_state.result_source = "live"
        st.session_state.example_lang = lang
        notes = list(result.get("notes") or [])
        notes.append(t["duration"].format(sec=round(time.time() - started)))
        st.session_state[k["notes"]] = notes
        st.session_state[k["status"]] = "done"
        finished = True
    except LiveAnalysisError as error:
        st.session_state[k["status"]] = "failed"
        st.session_state[k["error"]] = str(error)
        finished = True
    except Exception as error:  # noqa: BLE001 – Besucher:innen bekommen eine verstaendliche Meldung
        # nur Fehlertyp + Schritt + Code-Stellen ins Server-Log, keine Kommentartexte (Review N7)
        log_exception(f"live-analysis {lang}", error, st.session_state.get(k["stage"]))
        st.session_state[k["status"]] = "failed"
        st.session_state[k["error"]] = t["unexpected"].format(err=type(error).__name__)
        finished = True
    finally:
        # B1 (Cloud-Test 26.09.2026, kritisch): Lock ZUERST freigeben. Nach Stop, Neuladen oder
        # Tab-Schliessen wirft jeder weitere st.*-Zugriff dieser Sitzung (auch st.session_state)
        # erneut StopException – schon im except-Block oben. Stand release() hinter einem
        # st.session_state-Zugriff, wurde es nie erreicht: "busy" fuer alle bis zum Reboot.
        # Die Pause (B2) wird noch unter der Sperre gesetzt – reines Python, kein st.*-Zugriff.
        cooldown.mark(started, cooldown_seconds)
        lock.release()
        try:
            if not finished and st.session_state.get(k["status"]) == "running":
                st.session_state[k["status"]] = "interrupted"
        finally:
            gc.collect()
    st.rerun()


def render_status(lang: str) -> None:
    """Meldung zum letzten Lauf (fertig / fehlgeschlagen / unterbrochen)."""
    k = _keys(lang)
    t = TEXTS[lang]
    status = st.session_state.get(k["status"])
    if status == "interrupted":
        stage = st.session_state.get(k["stage"]) or t["stage_unknown"]
        st.warning(t["interrupted"].format(stage=stage))
        st.session_state[k["status"]] = None
        # Review N3: Wurde der Lauf durch einen Klick auf das (noch sichtbare) Startformular
        # unterbrochen, startet dieser Klick NICHT sofort einen neuen Lauf.
        st.session_state[k["ignore_submit"]] = True
    elif status == "failed":
        st.warning(t["failed"].format(msg=st.session_state.get(k["error"], "")))
        st.session_state[k["status"]] = None


def render_busy(lang: str) -> None:
    """Meldung "andere Analyse laeuft" bzw. "Pause" (B2) + "Erneut versuchen" – direkt ueber dem Startformular
    (Cloud-Test N-b, Entscheidung Sandra 28.09.2026: oben auf der Seite wurde sie uebersehen)."""
    k = _keys(lang)
    t = TEXTS[lang]
    status = st.session_state.get(k["status"])
    remaining = _cooldown().remaining()
    if status not in ("busy", "cooldown"):
        if remaining > 0:
            st.info(t["cooldown_hint"].format(**_minutes_text(lang, remaining)))
        return
    if status == "busy":
        st.warning(t["busy"])
    elif remaining > 0:
        st.warning(t["cooldown"].format(**_minutes_text(lang, remaining)))
    else:
        st.info(t["cooldown_over"])     # Pause inzwischen vorbei
    if st.session_state.get(k["request"]):
        # Status bleibt "busy"/"cooldown", bis erneut versucht oder neu gestartet wird (NEU7)
        if st.button(t["retry"], key=f"live_retry_{lang}"):
            st.session_state[k["status"]] = "pending"
            st.rerun()
    else:
        st.session_state[k["status"]] = None


def is_live_result(lang: str) -> bool:
    return (st.session_state.get("result_source") == "live"
            and st.session_state.get("example_lang") == lang
            and st.session_state.get("df") is not None)


def render_live_result_info(lang: str) -> None:
    """Info-Zeile + Hinweise zur eigenen Analyse (Stichprobe, Dauer)."""
    t = TEXTS[lang]
    df = st.session_state.get("df")
    n = len(df) if df is not None else 0
    st.success(t["done"].format(name=st.session_state.get("current_file"), n=fmt_int(n, lang)))
    for note in st.session_state.get(_keys(lang)["notes"]) or []:
        st.caption(note)


def render_result_download(lang: str) -> None:
    """Ergebnis der eigenen Analyse als CSV (die Cloud speichert nichts dauerhaft)."""
    df = st.session_state.get("df")
    if df is None or not is_live_result(lang):
        return
    name = Path(str(st.session_state.get("current_file") or "analyse")).stem
    st.download_button(
        TEXTS[lang]["download"],
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{name}_analyse_{lang}.csv",
        mime="text/csv",
        key=f"live_download_{lang}",
    )


def render_live_section(lang: str, repo_files: List) -> None:
    """Formular 'Eigene Analyse starten' (unter den Beispielen)."""
    k = _keys(lang)
    ignore_submit = st.session_state.pop(k["ignore_submit"], False)
    if not live_analysis_enabled():
        return
    t = TEXTS[lang]
    st.divider()
    st.subheader(t["section_title"])
    caption = t["section_caption"]
    max_comments = live_max_comments()
    if max_comments:
        caption += " " + t["limit_note"].format(n=max_comments)
    st.caption(caption)
    render_busy(lang)

    repo_files = [str(p) for p in (repo_files or [])]
    sources = [t["source_repo"], t["source_upload"]] if repo_files else [t["source_upload"]]
    with st.form(f"live_form_{lang}"):
        source = st.radio(t["source_label"], sources, horizontal=True, key=f"live_source_{lang}")
        repo_choice = None
        if repo_files:
            repo_choice = st.selectbox(t["repo_select"], repo_files, format_func=lambda p: Path(p).name,
                                       key=f"live_repo_{lang}")
        upload = st.file_uploader(t["upload_label"], type=["csv", "json", "jsonl"], key=f"live_upload_{lang}")
        submitted = st.form_submit_button(t["start"], type="primary")

    if not submitted or ignore_submit:
        return
    if source == t["source_upload"]:
        if upload is None:
            st.warning(t["need_upload"])
            return
        data = upload.getvalue()
        name = upload.name
    else:
        if repo_choice is None:
            st.warning(t["no_repo_files"])
            return
        data = Path(repo_choice).read_bytes()
        name = Path(repo_choice).name
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        st.warning(t["too_big"])
        return
    st.session_state[k["request"]] = {"data": data, "name": name, "lang": lang}
    st.session_state[k["status"]] = "pending"
    st.rerun()
