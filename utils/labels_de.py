"""
Deutsche Anzeige-Namen fuer die Diagramme der deutschen Kommentaranalyse (K4, 28.09.2026).

Die Modelle liefern englische Labels (negative/neutral/positive, anger/fear/... /none of them).
Die Daten und CSV-Exporte behalten diese Labels; nur die Diagramme zeigen deutsche Namen.
"""
from typing import Dict

LABELS_DE: Dict[str, str] = {
    "positive": "positiv",
    "neutral": "neutral",
    "negative": "negativ",
    "anger": "Wut",
    "fear": "Angst",
    "disgust": "Ekel",
    "sadness": "Trauer",
    "joy": "Freude",
    "none of them": "keins davon",
}


def label_de(value):
    """Ein Label uebersetzen (unbekannte Werte bleiben unveraendert)."""
    return LABELS_DE.get(value, value) if isinstance(value, str) else value


def translate_labels_de(fig):
    """Plotly-Figur: Kategorien auf den Achsen, Legenden-Namen und Tooltips auf Deutsch."""
    try:
        for trace in fig.data:
            name = getattr(trace, "name", None)
            if isinstance(name, str) and name in LABELS_DE:
                trace.name = LABELS_DE[name]
                if getattr(trace, "legendgroup", None) == name:
                    trace.legendgroup = LABELS_DE[name]
            for axis in ("x", "y"):
                values = getattr(trace, axis, None)
                if values is not None and len(values) and all(isinstance(v, str) for v in values):
                    setattr(trace, axis, [label_de(v) for v in values])
            template = getattr(trace, "hovertemplate", None)
            if isinstance(template, str):
                for english, german in LABELS_DE.items():
                    template = template.replace(f"={english}<", f"={german}<")
                trace.hovertemplate = template
    except Exception:  # noqa: BLE001 – Anzeige-Kosmetik darf nie ein Diagramm verhindern
        pass
    return fig


def count_with_share_de(count, share: float) -> str:
    """Kennzahl ohne gruenen Pfeil (K4): '1.197 (57,5 %)' statt st.metric-delta, das wie ein Zuwachs wirkt.
    share als Anteil 0..1."""
    number = f"{int(count):,}".replace(",", ".")
    percent = f"{share * 100:.1f}".replace(".", ",")
    return f"{number} ({percent} %)"
