"""
Beispielanalysen fuer die Kommentaranalyse-Seiten (DE/EN).

Besucher:innen sehen sofort ein fertiges, vorab berechnetes Ergebnis aus
analyzed_data/results/. Darunter steht die Live-Analyse ("Eigene Analyse starten",
utils/live_comment_analysis.py).
"""
import ast
import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.live_comment_analysis import (  # noqa: F401 – live_analysis_enabled: Rueckwaertskompatibilitaet
    fmt_int, is_live_result, live_analysis_enabled, render_live_result_info)

APP_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = APP_ROOT / "analyzed_data" / "results"

# source_name: urspruenglicher Dateiname (enthaelt die YouTube-ID fuer die Video-Infos)
EXAMPLES = [
    {
        "lang": "de",
        "file": "20250612_100240_de_sentiment_emotion_topic_german_Wie_Künstliche_Intelligenz_die.csv",
        "label": "Markus Lanz: „Wie Künstliche Intelligenz die Bildung verändert“ (ZDF, 18.06.2024)",
        "source_name": "2024-06-18_87TYPn6gbwA_Wie Künstliche Intelligenz die Bildung verändert _ Markus Lanz.csv",
    },
    {
        "lang": "en",
        "file": "20250612_100702_en_sentiment_emotion_topic_Why_Malaysia_Education_System.csv",
        "label": "Why Malaysia Education System Is A Failure? (2024)",
        "source_name": "2024-11-23_KdIw52uLW8g_Why Malaysia Education System Is A Failure_.csv",
    },
    {
        "lang": "en",
        "file": "20250612_101129_en_sentiment_emotion_topic_Why_The_Education_System_Is_Fa.csv",
        "label": "Why The Education System Is Failing America | CNBC Marathon (2022)",
        "source_name": "2022-08-21_XlnspY2wOVw_Why The Education System Is Failing America _ CNBC Marathon.csv",
    },
    {
        "lang": "en",
        "file": "20260925_en_sentiment_emotion_topic_5_Reasons_Why_Finland_Is_A_Global_Education_Leader.csv",
        "label": "5 Reasons Why Finland Is A Global Education Leader (2016)",
        "source_name": "2016-08-15_UfmFIEh2QjU_5 Reasons Why Finland Is A Global Education Leader.csv",
    },
]

DATA_DIR = APP_ROOT / "data" / "comments"

# Sprache der mitgelieferten Kommentardateien (Review N5): Die DE-Seite bietet nur deutsche,
# die EN-Seite nur englische Dateien an. Neue Dateien hier eintragen; nicht eingetragene
# Dateien erscheinen auf beiden Seiten.
DATA_FILE_LANG = {
    "2024-06-18_87TYPn6gbwA_Wie Künstliche Intelligenz die Bildung verändert _ Markus Lanz.csv": "de",
    "2024-11-23_KdIw52uLW8g_Why Malaysia Education System Is A Failure_.csv": "en",
    "2022-08-21_XlnspY2wOVw_Why The Education System Is Failing America _ CNBC Marathon.csv": "en",
    "2016-08-15_UfmFIEh2QjU_5 Reasons Why Finland Is A Global Education Leader.csv": "en",
    "2014-12-17__X0mgOOSpLU_The power of believing that you can improve _ Carol Dweck _ TED.csv": "en",
}


def repo_files_for_language(lang: str):
    """Mitgelieferte Dateien fuer eine Sprache (Pfade als Strings, sortiert)."""
    if not DATA_DIR.exists():
        return []
    files = sorted(p for p in DATA_DIR.iterdir() if p.is_file() and p.suffix.lower() in (".csv", ".json", ".jsonl"))
    langs = {unicodedata.normalize("NFC", k): v for k, v in DATA_FILE_LANG.items()}
    return [str(p) for p in files if langs.get(unicodedata.normalize("NFC", p.name), lang) == lang]


def known_source_names(lang: str):
    """Dateinamen der Beispiele (fuer die Video-ID, Review N6)."""
    return [e["source_name"] for e in EXAMPLES if e["lang"] == lang]


TEXTS = {
    "de": {
        "title": "📂 Beispielanalysen",
        "caption": ("Vorab berechnete Analysen echter YouTube-Kommentare (Sentiment, Emotionen, Themen). "
                    "Weiter unten können Sie eine eigene Live-Analyse starten."),
        "select": "Beispiel auswählen:",
        "button": "Beispiel anzeigen",
        "comments": "Kommentare",
        "current": "📄 Beispielanalyse",
        "back": "📂 Zurück zu den Beispielen",
    },
    "en": {
        "title": "📂 Example analyses",
        "caption": ("Pre-computed analyses of real YouTube comments (sentiment, emotions, topics). "
                    "Further down you can run your own live analysis."),
        "select": "Choose an example:",
        "button": "Show example",
        "comments": "comments",
        "current": "📄 Example analysis",
        "back": "📂 Back to the examples",
    },
}


def _examples(lang: str):
    return [e for e in EXAMPLES if e["lang"] == lang and (EXAMPLES_DIR / e["file"]).exists()]


def _parse_dict(value):
    """CSV speichert die Spalte 'emotions' als Text ("{'anger': 0.1, ...}") -> wieder dict."""
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip().startswith("{"):
        return None
    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, dict) else None
    except (ValueError, SyntaxError):
        return None


@st.cache_data(show_spinner=False)
def _load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    if "emotions" in df.columns:
        # die Emotions-Anzeige (v. a. EN) erwartet dicts, sonst Absturz beim Oeffnen des Beispiels
        df["emotions"] = df["emotions"].apply(_parse_dict)
    return df


def _text_column(df: pd.DataFrame):
    for col in ["comment_text", "text", "comment", "kommentar", "content"]:
        if col in df.columns:
            return col
    return None


def load_example(example: dict) -> None:
    df = _load(str(EXAMPLES_DIR / example["file"]))
    st.session_state.df = df
    st.session_state.text_column = _text_column(df)
    st.session_state.current_file = example["source_name"]
    st.session_state.additional_data = {}
    st.session_state.example_label = example["label"]
    st.session_state.result_source = "example"


def render_example_picker(lang: str) -> None:
    """Auswahl der Beispielanalysen; laedt beim ersten Aufruf automatisch das erste Beispiel."""
    t = TEXTS[lang]
    examples = _examples(lang)
    if not examples:
        return
    if st.session_state.get("df") is None or st.session_state.get("example_lang") != lang:
        load_example(examples[0])
        st.session_state.example_lang = lang

    st.subheader(t["title"])
    st.caption(t["caption"])

    # Eigene Analyse wird gerade angezeigt -> Info + Rueckweg zu den Beispielen
    if is_live_result(lang):
        render_live_result_info(lang)
        if st.button(t["back"], key=f"example_back_{lang}"):
            label = st.session_state.get("example_label")
            match = [e for e in examples if e["label"] == label]
            load_example(match[0] if match else examples[0])
            st.rerun()
        return
    if st.session_state.get("result_source") == "saved":
        st.info(f"📁 {st.session_state.get('current_file')}")
        if st.button(t["back"], key=f"example_back_saved_{lang}"):
            label = st.session_state.get("example_label")
            match = [e for e in examples if e["label"] == label]
            load_example(match[0] if match else examples[0])
            st.rerun()
        return

    labels = [e["label"] for e in examples]
    current = st.session_state.get("example_label")
    index = labels.index(current) if current in labels else 0
    col1, col2 = st.columns([4, 1])
    with col1:
        choice = st.selectbox(t["select"], labels, index=index, key=f"example_select_{lang}")
    with col2:
        st.write("")
        st.write("")
        clicked = st.button(t["button"], key=f"example_button_{lang}")
    if clicked and choice != current:
        load_example(examples[labels.index(choice)])
        st.rerun()
    df = st.session_state.get("df")
    if df is not None:
        st.info(f"{t['current']}: {st.session_state.get('example_label')} · {fmt_int(len(df), lang)} {t['comments']}")
