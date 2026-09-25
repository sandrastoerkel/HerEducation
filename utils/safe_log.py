"""
Fehler ins Server-Log schreiben – ohne Eingabetexte (Review N7, 25.09.2026).

Streamlit Cloud zeigt stdout unter "Manage app -> Logs". Tracebacks von Tokenizer- oder
pandas-Fehlern koennen Kommentartext in der Fehlermeldung enthalten; darum werden nur
Fehlertyp, Schritt und die Code-Stellen (Datei:Zeile Funktion) geloggt, nie die Meldung.
Besucher:innen sehen keine Tracebacks.
"""
import traceback
from typing import Optional


def frames(error: BaseException, limit: int = 8) -> str:
    stack = traceback.extract_tb(error.__traceback__)[-limit:]
    return " <- ".join(f"{f.filename.rsplit('/', 1)[-1]}:{f.lineno} {f.name}" for f in reversed(stack))


def log_exception(area: str, error: BaseException, step: Optional[str] = None) -> None:
    where = f" step={step!r}" if step else ""
    print(f"[{area}] {type(error).__name__}{where} at {frames(error)}", flush=True)
