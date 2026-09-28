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
- Einspaltige CSV (Kopfzeile nur "text" o. Ae.): jede Zeile ist GANZ ein Kommentar, auch mit
  Kommas ohne Anfuehrungszeichen (Cloud-Test N-c, Entscheidung Sandra 28.09.2026 – frueher
  fehlte der Text nach dem ersten Komma ohne Hinweis).
- Mehrspaltige CSV: Zeilen mit mehr oder weniger Feldern als die Kopfzeile werden gezaehlt
  (df.attrs["irregular_rows"]); reader_notes() macht daraus einen Hinweis fuer die Seite.
- Leere Kommentare werden entfernt. Kein Treffer -> CommentFileError mit Grund.
- YouTube-Namen in Antworten ("@name ...") werden durch "@…" ersetzt (Entscheidung Sandra
  25.09.2026: keine Nutzernamen in der oeffentlichen Datenvorschau). Gilt fuer jedes @-Wort
  am Textanfang, nach einem Leerzeichen oder nach einem unsichtbaren Zeichen (Zero-Width-Space);
  E-Mail-Adressen bleiben unberuehrt.
"""
import csv
import io
import json
import re
import warnings
from typing import List, Optional, Tuple

import pandas as pd

# Reihenfolge = Prioritaet (Vergleich ohne Gross-/Kleinschreibung)
TEXT_COLUMNS = ["text", "comment_text", "comment", "kommentar", "content", "body", "message", "textoriginal"]
OUTPUT_COLUMN = "comment_text"
# Vor dem "@" steht Textanfang, ein Leerzeichen ODER ein unsichtbares Zeichen
# (Zero-Width-Space U+200B, ZWNJ U+200C, ZWJ U+200D, Word-Joiner U+2060, BOM U+FEFF).
# YouTube setzt bei Antworten teilweise U+200B vor "@name" (Nachreview NEU2, 26.09.2026).
# Die unsichtbaren Zeichen bleiben im Text (ZWJ gehoert z. B. zu Emoji-Folgen).
MENTION_PATTERN = re.compile(r"(?<![^\s\u200b-\u200d\u2060\ufeff])@[\w\-]+(?:\.[\w\-]+)*")
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


DELIMITERS = (",", ";", "\t")


def _csv_rows(text: str, delimiter: str) -> List[List[str]]:
    return list(csv.reader(io.StringIO(text), delimiter=delimiter))


def _single_column_texts(text: str) -> Optional[List[Optional[str]]]:
    """Einspaltige Datei mit Textspalten-Kopfzeile -> jede Zeile ganz (N-c).

    Das csv-Modul beachtet Anfuehrungszeichen (auch mehrzeilige Kommentare); Felder, die an
    einem Komma ohne Anfuehrungszeichen getrennt wurden, werden mit genau diesem Komma
    wieder zusammengesetzt – der Kommentar bleibt unveraendert.
    """
    try:
        rows = _csv_rows(text, ",")
    except csv.Error:
        return None
    if not rows:
        return None
    header = rows[0]
    # Kopfzeile genau ein Feld mit bekanntem Namen ("text;author" ist hier EIN Feld ohne Treffer)
    if len(header) != 1 or _pick_text_key(header) is None:
        return None
    return [",".join(row) if row else None for row in rows[1:]]


def _count_irregular_rows(text: str, delimiter: str, n_columns: int) -> int:
    """Zeilen, deren Feldzahl nicht zur Kopfzeile passt (werden von pandas gekuerzt/uebersprungen)."""
    try:
        rows = _csv_rows(text, delimiter)
    except csv.Error:
        return 0
    return sum(1 for row in rows[1:] if row and any(f.strip() for f in row) and len(row) != n_columns)


def _read_csv(text: str) -> Tuple[List[Optional[str]], int]:
    """CSV mit Kopfzeile; probiert Komma, Semikolon (Excel DE) und Tab.
    Ergebnis: (Texte, Anzahl unregelmaessiger Zeilen)."""
    single = _single_column_texts(text)
    if single is not None:
        return single, 0
    columns_seen = []
    last_error = None
    for delimiter in DELIMITERS:
        try:
            with warnings.catch_warnings():
                # ParserWarning bei zu vielen Feldern: wird jetzt gezaehlt und den Nutzer:innen
                # gemeldet (N-c), im Server-Log nur Rauschen
                warnings.simplefilter("ignore", pd.errors.ParserWarning)
                df = pd.read_csv(io.StringIO(text), sep=delimiter, dtype=str, keep_default_na=False,
                                 engine="python", on_bad_lines="skip", index_col=False)
            # index_col=False (Nachreview NEU1): Sonst macht pandas bei einer Zeile mit
            # ueberzaehligen Feldern die vorderen Spalten zum Index und verschiebt alle Texte.
        except Exception as error:  # noqa: BLE001 – naechstes Trennzeichen probieren
            last_error = error
            continue
        key = _pick_text_key(df.columns)
        if key is not None:
            return df[key].tolist(), _count_irregular_rows(text, delimiter, len(df.columns))
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
    irregular = 0
    if fmt == "jsonl":
        texts = _read_jsonl(text)
    elif fmt == "json":
        texts = _read_json_list(text)
    else:
        texts, irregular = _read_csv(text)

    rows = []
    for number, value in enumerate(texts, start=1):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        comment = mask_mentions(str(value).replace("\r\n", "\n").replace("\r", "\n")).strip()
        if comment:
            rows.append({OUTPUT_COLUMN: comment, "original_line": number})
    if not rows:
        raise CommentFileError("empty")
    df = pd.DataFrame(rows, columns=[OUTPUT_COLUMN, "original_line"])
    df.attrs["irregular_rows"] = irregular
    return df


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


NOTES = {
    "de": ("⚠️ {k} Zeilen der Datei haben mehr oder weniger Felder als die Kopfzeile (z. B. Kommas "
           "ohne Anführungszeichen) und wurden gekürzt oder übersprungen. Tipp: den Kommentartext "
           "in Anführungszeichen setzen."),
    "en": ("⚠️ {k} rows of the file have more or fewer fields than the header row (e.g. commas "
           "without quotation marks) and were shortened or skipped. Tip: put the comment text "
           "in quotation marks."),
}


def reader_notes(df: pd.DataFrame, lang: str) -> List[str]:
    """Hinweise zum Einlesen fuer die Seite (N-c). Direkt nach read_comments() aufrufen –
    spaetere Filter/Stichproben uebernehmen df.attrs nicht zuverlaessig."""
    k = int(df.attrs.get("irregular_rows", 0) or 0)
    if not k:
        return []
    number = f"{k:,}".replace(",", ".") if lang == "de" else f"{k:,}"
    return [NOTES.get(lang, NOTES["en"]).format(k=number)]


def error_message(error: CommentFileError, lang: str) -> str:
    messages = MESSAGES.get(lang, MESSAGES["en"])  # Nachreview NEU6: kein KeyError bei fremder Sprache
    return messages.get(error.reason, messages["unreadable"])
