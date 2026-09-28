"""
Themen-Namen fuer die Beispielanalysen (K4, Entscheidung Sandra 28.09.2026).

Die Beispiel-CSVs in analyzed_data/results/ enthalten die Themen-Zuordnung (Spalte `topic`)
aus dem echten BERTopic-Lauf, aber die Themen-Modelle selbst wurden nie gespeichert. Ohne
Themen-Namen blieben die Spezial-Analysen (Bildung/Gender/eigene Suche) in den Beispielen aus.

Loesung: Die typischen Woerter je Thema werden einmalig nachberechnet – mit derselben Formel
wie BERTopic (klassenbasiertes TF-IDF ueber die Spalte `clean_text`, die schon ohne
Stoppwoerter gespeichert ist). Daraus entstehen die Namen mit DERSELBEN Namenslogik wie in
der Live-Analyse (utils/topic_labeling*.py). Die Themen-Zuordnung bleibt original, nur die
Namen sind nachberechnet.

Ergebnis: je Beispiel eine Datei <beispiel>.topic_labels.json neben der CSV.
Neu erzeugen (im Repo-Ordner):  python -m utils.example_topic_labels
"""
import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

OUTLIER_TOPIC = -1
N_WORDS = 10
LABEL_SUFFIX = ".topic_labels.json"
METHOD = ("c-TF-IDF wie BERTopic (tf je Thema L1-normiert x log(1 + A / f)) ueber clean_text; "
          "Namen mit utils/topic_labeling*.generate_smart_topic_labels")


def label_path(csv_path: Path) -> Path:
    return csv_path.with_name(csv_path.stem + LABEL_SUFFIX)


def class_tfidf_keywords(texts: List[str], topics: List[int], n_words: int = N_WORDS) -> Dict[int, List[Tuple[str, float]]]:
    """Typische Woerter je Thema, Formel wie bertopic.vectorizers.ClassTfidfTransformer (bm25/reduce aus)."""
    from sklearn.feature_extraction.text import CountVectorizer

    frame = pd.DataFrame({"text": [str(t) if isinstance(t, str) else "" for t in texts], "topic": topics})
    frame = frame[frame["topic"] != OUTLIER_TOPIC]
    if frame.empty:
        return {}
    grouped = frame.groupby("topic")["text"].apply(lambda s: " ".join(s))
    vectorizer = CountVectorizer()
    counts = vectorizer.fit_transform(grouped.values).toarray().astype(float)
    words = vectorizer.get_feature_names_out()
    tf = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1.0)
    avg_words = counts.sum(axis=1).mean()
    idf = np.log(1 + avg_words / np.maximum(counts.sum(axis=0), 1.0))
    ctfidf = tf * idf
    result = {}
    for row, topic in enumerate(grouped.index):
        order = np.argsort(ctfidf[row])[::-1][:n_words]
        result[int(topic)] = [(str(words[i]), float(round(ctfidf[row, i], 6))) for i in order if ctfidf[row, i] > 0]
    return result


class _KeywordTopicModel:
    """Minimaler Ersatz fuer ein BERTopic-Modell: nur get_topic_info()/get_topic(), damit die
    bestehende Namenslogik der Live-Analyse unveraendert benutzt werden kann."""

    def __init__(self, keywords: Dict[int, List[Tuple[str, float]]], sizes: Dict[int, int]):
        self.keywords = keywords
        self.sizes = sizes

    def get_topic_info(self) -> pd.DataFrame:
        rows = [{"Topic": t, "Count": c} for t, c in self.sizes.items()]
        return pd.DataFrame(rows)

    def get_topic(self, topic_id: int):
        return self.keywords.get(int(topic_id), [])


def build_labels(df: pd.DataFrame, lang: str) -> Dict:
    keywords = class_tfidf_keywords(df["clean_text"].tolist(), df["topic"].astype(int).tolist())
    sizes = {int(t): int(c) for t, c in df["topic"].value_counts().items()}
    model = _KeywordTopicModel(keywords, sizes)
    if lang == "de":
        from utils.topic_labeling import generate_smart_topic_labels
    else:
        from utils.topic_labeling_english import generate_smart_topic_labels
    labels = generate_smart_topic_labels(model)
    return {
        "method": METHOD,
        "created": date.today().isoformat(),
        "note": ("Themen-Zuordnung aus dem Original-Lauf; Namen nachtraeglich berechnet "
                 "(das Themen-Modell des Original-Laufs wurde nicht gespeichert)."),
        "labels": {str(k): v for k, v in sorted(labels.items())},
        "keywords": {str(k): [w for w, _ in v] for k, v in sorted(keywords.items())},
    }


def load_labels(csv_path: Path) -> Optional[Dict[int, str]]:
    """Themen-Namen eines Beispiels (oder None, wenn keine Datei da ist)."""
    path = label_path(Path(csv_path))
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {int(k): str(v) for k, v in data.get("labels", {}).items()} or None
    except (ValueError, OSError):
        return None


def main() -> None:
    from utils.example_analyses import EXAMPLES, EXAMPLES_DIR
    for example in EXAMPLES:
        csv_path = EXAMPLES_DIR / example["file"]
        df = pd.read_csv(csv_path, encoding="utf-8")
        data = build_labels(df, example["lang"])
        label_path(csv_path).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{csv_path.name}: {len(data['labels'])} Namen")


if __name__ == "__main__":
    main()
