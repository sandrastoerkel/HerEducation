"""
Adapter fuer Hugging-Face-Pipelines (Kommentaranalyse DE/EN).

- AllScoresPipeline: liefert fuer einen Text immer alle Emotions-Scores im
  bisherigen Format [[{"label": ..., "score": ...}, ...]].
  Hintergrund (MESS1, 25.09.2026): Mit transformers 5.x wirkt
  `return_all_scores=True` beim Erstellen der Pipeline nicht mehr; es kam nur
  noch das Top-Label zurueck (DE fast immer "anger", EN gar kein Ergebnis).
  Loesung: `top_k=None` beim Aufruf + einheitliche Form, unabhaengig von der Version.
- CachedPipeline: merkt sich Ergebnisse je Text fuer die Dauer EINES Analyselaufs.
  Die Sentiment-Analyse ruft das Modell fuer Label und Konfidenz getrennt auf;
  mit dem Cache rechnet das Modell jeden Textabschnitt nur noch einmal.
"""
from typing import Any, Dict


def _normalize_all_scores(result: Any) -> Any:
    """Bringt die Pipeline-Antwort fuer EINEN Text auf die Form [[{label, score}, ...]]."""
    if isinstance(result, dict):
        return [[result]]
    if isinstance(result, list):
        if not result:
            return [[]]
        first = result[0]
        if isinstance(first, dict):
            return [result]
        if isinstance(first, list):
            return result
    return result


class AllScoresPipeline:
    """Emotions-Pipeline, die immer alle Scores zurueckgibt (altes Format)."""

    def __init__(self, pipe: Any):
        self.pipe = pipe
        # fuer Code, der auf Pipeline-Attribute zugreift (z. B. model.config)
        self.model = getattr(pipe, "model", None)
        self.tokenizer = getattr(pipe, "tokenizer", None)

    def __call__(self, text: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("top_k", None)
        kwargs.setdefault("truncation", True)
        if isinstance(text, str):
            return _normalize_all_scores(self.pipe(text, **kwargs))
        results = self.pipe(text, **kwargs)
        return [_normalize_all_scores(r)[0] for r in results]


class CachedPipeline:
    """Merkt sich Ergebnisse je Text (nur fuer einen Analyselauf erzeugen, nicht global cachen)."""

    def __init__(self, pipe: Any, max_items: int = 50000):
        self.pipe = pipe
        self.model = getattr(pipe, "model", None)
        self.tokenizer = getattr(pipe, "tokenizer", None)
        self.max_items = max_items
        self._cache: Dict[Any, Any] = {}
        self.hits = 0
        self.misses = 0

    def __call__(self, text: Any, **kwargs: Any) -> Any:
        if not isinstance(text, str):
            return self.pipe(text, **kwargs)
        key = (text, tuple(sorted(kwargs.items())))
        if key in self._cache:
            self.hits += 1
            return self._cache[key]
        self.misses += 1
        result = self.pipe(text, **kwargs)
        if len(self._cache) < self.max_items:
            self._cache[key] = result
        return result
