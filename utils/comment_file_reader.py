"""
Gemeinsamer Datei-Leser fuer die Kommentaranalyse (DE + EN) – ohne Streamlit-Aufrufe.

Warum (Review H2, 25.09.2026): Die alten Leser nahmen bei CSV-Dateien immer die ZWEITE
Spalte als Kommentar. Bei den YouTube-Exporten mit Kopfzeile
(comment_id,author,time,likes_count,text,...) war das der Autor-Name; bei den
JSON-Lines-Dateien mit Endung .csv (Lanz, Malaysia) entstand ein Praefix " text: " plus
Escape-Reste (\\n, \\"). Beides ging in die Modelle und in die Beispielanalysen ein.

Regeln:
- Bytes werden als UTF-8 gelesen, ungueltige Zeichen ersetzt (errors="replace"), BOM entfernt.
- Beginnt der Inhalt mit "{" -> JSON Lines (eine JSON-Zeile je Kommentar), mit "[" -> JSON-Liste.
  Das Format wird am Inhalt erkannt, nicht an der Dateiendung.
- Sonst CSV mit Kopfzeile; die Textspalte wird am Namen erkannt (TEXT_COLUMNS).
- Ergebnis: DataFrame mit genau den Spalten comment_text und original_line
  (Nummer des Datensatzes in der Datei, ab 1). Autor, Zeit, IDs usw. werden bewusst
  NICHT uebernommen (Datenvorschau zeigt keine Nutzernamen).
- Leere Kommentare werden entfernt. Kein Treffer -> CommentFileError mit Grund.
- YouTube-Namen in Antworten ("@name ...") werden durch "@…" ersetzt (Entscheidung Sandra
  25.09.2026: keine Nutzernamen in der oeffentlichen Datenvorschau). Gilt fuer jedes @-Wort
  am Textanfang oder nach einem Leerzeichen; E-Mail-Adressen bleiben unberuehrt.
"""
import io
import json
import re
from typing import List, Optional

import pandas as pd

# Reihenfolge = Prioritaet (Vergleich ohne Gross-/Kleinschreibung)
TEXT_COLUMNS = ["text", "comment_text", "comment", "kommentar", "content", "body", "message", "textoriginal"]
OUTPUT_COLUMN = "comment_text"
MENTION_PATTERN = re.compile(r"(?<!\S)@[\w\-]+(?:\.[\w\-]+)*")
MENTION_MASK = "@…"


def mask_mentions(text: str) -> str:
    """"@name danke!" -> "@… danke!" (Nutzernamen nicht anzeigen)."""
    return MENTION_PATTERN.sub(MENTION_MASK, text)


class CommentFileError(ValueError):
    """Datei kann nicht als Kommentarliste gelesen werden. reason: empty | no_text_column | unreadable"""

    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


def decode_bytes(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    return text.lstrip("﻿")


def detect_format(text: str) -> str:
    start = text.lstrip()[:1]
    if start == "{":
        return "jsonl"
    if start == "[":
        return "json"
    return "csv"


def _pick_text_key(keys) -> Optional[str]:
    lookup = {str(k).strip().lstrip("﻿").lower(): k for k in keys}
    for name in TEXT_COLUMNS:
        if name in lookup:
            return lookup[name]
    return None


def _records_to_texts(records: List[dict]) -> List[Optional[str]]:
    keys = set()
    for rec in records:
        if isinstance(rec, dict):
            keys.update(rec.keys())
    key = _pick_text_key(keys)
    if key is None:
        raise CommentFileError("no_text_column", ", ".join(sorted(map(str, keys)))[:200])
    return [rec.get(key) if isinstance(rec, dict) else None for rec in records]


def _read_jsonl(text: str) -> List[Optional[str]]:
    records = []
    bad = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
            records.append(None)
    if not any(isinstance(r, dict) for r in records):
        raise CommentFileError("unreadable", f"{bad} ungueltige JSON-Zeilen")
    return _records_to_texts(records)


def _read_json_list(text: str) -> List[Optional[str]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise CommentFileError("unreadable", f"JSON: {error.msg}")
    if not isinstance(data, list):
        raise CommentFileError("unreadable", "JSON ist keine Liste")
    return _records_to_texts(data)


def _read_csv(text: str) -> List[Optional[str]]:
    """CSV mit Kopfzeile; probiert Komma, Semikolon (Excel DE) und Tab."""
    columns_seen = []
    last_error = None
    for delimiter in (",", ";", "\t"):
        try:
            df = pd.read_csv(io.StringIO(text), sep=delimiter, dtype=str, keep_default_na=False,
                             engine="python", on_bad_lines="skip")
        except Exception as error:  # noqa: BLE001 – naechstes Trennzeichen probieren
            last_error = error
            continue
        key = _pick_text_key(df.columns)
        if key is not None:
            return df[key].tolist()
        columns_seen = list(map(str, df.columns))
    if not columns_seen and last_error is not None:
        raise CommentFileError("unreadable", type(last_error).__name__)
    raise CommentFileError("no_text_column", ", ".join(columns_seen)[:200])


def read_comments(data: bytes, name: str = "") -> pd.DataFrame:
    """Liest eine Kommentardatei (JSON Lines, JSON-Liste oder CSV mit Kopfzeile)."""
    text = decode_bytes(data or b"")
    if not text.strip():
        raise CommentFileError("empty")
    fmt = detect_format(text)
    if fmt == "jsonl":
        texts = _read_jsonl(text)
    elif fmt == "json":
        texts = _read_json_list(text)
    else:
        texts = _read_csv(text)

    rows = []
    for number, value in enumerate(texts, start=1):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        comment = mask_mentions(str(value).replace("\r\n", "\n").replace("\r", "\n")).strip()
        if comment:
            rows.append({OUTPUT_COLUMN: comment, "original_line": number})
    if not rows:
        raise CommentFileError("empty")
    return pd.DataFrame(rows, columns=[OUTPUT_COLUMN, "original_line"])


# Meldungen fuer Besucher:innen (Seiten DE/EN)
MESSAGES = {
    "de": {
        "empty": "In der Datei wurden keine Kommentare gefunden.",
        "no_text_column": ("In der Datei wurde keine Textspalte gefunden. Erwartet wird eine Spalte "
                           "„text“ oder „comment_text“ (CSV mit Kopfzeile oder JSON Lines)."),
        "unreadable": "Die Datei konnte nicht gelesen werden (erwartet: CSV mit Kopfzeile oder JSON Lines).",
    },
    "en": {
        "empty": "No comments were found in the file.",
        "no_text_column": ("No text column was found in the file. Expected a column "
                           "“text” or “comment_text” (CSV with header row or JSON Lines)."),
        "unreadable": "The file could not be read (expected: CSV with header row or JSON Lines).",
    },
}


def error_message(error: CommentFileError, lang: str) -> str:
    return MESSAGES.get(lang, MESSAGES["en"]).get(error.reason, MESSAGES[lang]["unreadable"])
