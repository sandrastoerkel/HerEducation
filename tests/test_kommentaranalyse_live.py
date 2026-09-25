"""
Tests fuer die reparierte Kommentaranalyse (DE/EN) – mit ERSATZ-Modellen.

Laeuft ohne Hugging Face/transformers (Ersatz-Pipelines statt echter Modelle).
Echte Modelle: siehe Probelauf-Anleitung im Report (Claude Code auf dem Mac).

Start (im Repo-Ordner):  python -m pytest -q tests/test_kommentaranalyse_live.py
"""
import os
import sys
import zlib
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ["HEREDUCATION_LIVE_MAX_COMMENTS"] = "40"   # kleine Laeufe

from streamlit.testing.v1 import AppTest  # noqa: E402

from models import pipeline_adapters  # noqa: E402
from models.pipeline_adapters import AllScoresPipeline, CachedPipeline  # noqa: E402

DE_PAGE = "pages/05_Kommentaranalyse_deutsch.py"
EN_PAGE = "pages/06_Comment_Analysis_english.py"
TIMEOUT = 300


# ---------------------------------------------------------------------------
# Ersatz-Modelle
# ---------------------------------------------------------------------------

def _h(text: str) -> int:
    return zlib.crc32(text.encode("utf-8"))


class FakeSentiment:
    """Wie eine HF-Sentiment-Pipeline: str -> [{'label','score'}]."""

    def __init__(self, labels):
        self.labels = labels
        self.calls = 0

    def __call__(self, text, **kwargs):
        self.calls += 1
        h = _h(text)
        return [{"label": self.labels[h % 3], "score": 0.5 + (h % 50) / 100}]


class FakeEmotionV5:
    """Verhalten wie transformers 5.x: ohne top_k nur Top-Label, mit top_k=None flache Liste."""

    def __init__(self, labels):
        self.labels = labels
        self.calls = 0

    def _scores(self, text):
        h = _h(text)
        raw = [((h >> i) % 97) + 1 for i in range(len(self.labels))]
        total = float(sum(raw))
        return [{"label": lab, "score": r / total} for lab, r in zip(self.labels, raw)]

    def __call__(self, text, **kwargs):
        self.calls += 1
        if isinstance(text, list):
            return [self(t, **kwargs) for t in text]
        scores = self._scores(text)
        if "top_k" in kwargs and kwargs["top_k"] is None:
            return scores                                   # flache Liste
        return [max(scores, key=lambda d: d["score"])]      # nur Top-Label


DE_EMOTIONS = ["anger", "fear", "disgust", "sadness", "joy", "none of them"]
EN_EMOTIONS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]


@pytest.fixture
def fake_models(monkeypatch):
    import models.model_loader as de
    import models.model_loader_english as en
    fakes = {
        "de_sent": FakeSentiment(["positive", "neutral", "negative"]),
        "de_emo": FakeEmotionV5(DE_EMOTIONS),
        "en_sent": FakeSentiment(["negative", "neutral", "positive"]),
        "en_emo": FakeEmotionV5(EN_EMOTIONS),
    }
    monkeypatch.setattr(de, "load_sentiment_model", lambda: fakes["de_sent"])
    monkeypatch.setattr(de, "load_emotion_model", lambda: AllScoresPipeline(fakes["de_emo"]))
    monkeypatch.setattr(en, "load_sentiment_model", lambda: fakes["en_sent"])
    monkeypatch.setattr(en, "load_emotion_model", lambda: AllScoresPipeline(fakes["en_emo"]))
    return fakes


# ---------------------------------------------------------------------------
# Einheiten
# ---------------------------------------------------------------------------

def test_all_scores_adapter_shapes():
    fake = FakeEmotionV5(EN_EMOTIONS)
    wrapped = AllScoresPipeline(fake)
    out = wrapped("I am happy today")
    assert isinstance(out, list) and len(out) == 1 and len(out[0]) == len(EN_EMOTIONS)
    assert abs(sum(d["score"] for d in out[0]) - 1) < 1e-9
    # altes 4.x-Format (verschachtelt) bleibt unveraendert
    assert pipeline_adapters._normalize_all_scores([[{"label": "a", "score": 1.0}]]) == [[{"label": "a", "score": 1.0}]]
    assert pipeline_adapters._normalize_all_scores({"label": "a", "score": 1.0}) == [[{"label": "a", "score": 1.0}]]


def test_cached_pipeline_same_results_half_calls():
    from utils.sentiment_analysis import SentimentAnalysisConfig, perform_sentiment_analysis
    texts = [f"Kommentar Nummer {i} " * (1 + i % 40) for i in range(60)]
    raw = FakeSentiment(["positive", "neutral", "negative"])
    old = perform_sentiment_analysis(pd.DataFrame({"t": texts}), "t", raw, SentimentAnalysisConfig())
    calls_old = raw.calls
    raw2 = FakeSentiment(["positive", "neutral", "negative"])
    new = perform_sentiment_analysis(pd.DataFrame({"t": texts}), "t", CachedPipeline(raw2), SentimentAnalysisConfig())
    assert list(old["sentiment"]) == list(new["sentiment"])
    assert list(old["confidence"]) == list(new["confidence"])
    assert raw2.calls * 2 == calls_old          # Label + Konfidenz: jetzt nur ein Modellaufruf


def test_limit_comments_fixed_sample():
    from utils.live_comment_analysis import limit_comments
    df = pd.DataFrame({"x": range(1000)})
    a, total = limit_comments(df, 100)
    b, _ = limit_comments(df, 100)
    assert total == 1000 and len(a) == 100 and list(a["x"]) == list(b["x"])
    assert list(a["x"]) == sorted(a["x"])        # Reihenfolge der Datei bleibt
    c, _ = limit_comments(df, None)
    assert len(c) == 1000


def test_topic_merge_keeps_alignment():
    from utils.topic_analysis_english import MIN_TEXT_LENGTH, merge_topics_to_dataframe
    long = "x" * (MIN_TEXT_LENGTH + 5)
    df = pd.DataFrame({"clean_text": [long, "", long, long]})
    topic_df = df[df["clean_text"].str.len() > MIN_TEXT_LENGTH].reset_index(drop=True)
    topic_df["topic"] = [7, 8, 9]
    out = merge_topics_to_dataframe(df, topic_df)
    assert list(out["topic"]) == [7, -1, 8, 9]  # frueher: [7, 8, 9, -1]


def test_no_heavy_imports_on_page_view():
    at = AppTest.from_file(DE_PAGE, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, at.exception
    assert "transformers" not in sys.modules
    assert "bertopic" not in sys.modules


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------

def _page_text(at):
    parts = []
    for kind in ("markdown", "info", "warning", "success", "caption", "error", "subheader"):
        parts += [str(e.value) for e in getattr(at, kind)]
    return "\n".join(parts)


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_example_shown_on_first_view(page, lang):
    at = AppTest.from_file(page, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["result_source"] == "example"
    assert len(at.session_state["df"]) > 0
    assert "sentiment" in at.session_state["df"].columns
    text = _page_text(at)
    assert ("Eigene Analyse starten" if lang == "de" else "Run your own analysis") in text
    assert "Modul nicht verfügbar" not in text


@pytest.mark.parametrize("page,lang,repo_file", [
    (DE_PAGE, "de", "Markus Lanz"),
    (EN_PAGE, "en", "Malaysia"),
])
def test_live_run_with_fake_models(fake_models, page, lang, repo_file):
    at = AppTest.from_file(page, default_timeout=TIMEOUT)
    at.run()
    select = at.selectbox(key=f"live_repo_{lang}")
    name = next(o for o in select.options if repo_file in str(o))
    select.set_value(str(ROOT / "data" / "comments" / name))
    submit = next(b for b in at.button if "▶" in str(b.label))
    submit.click()
    at.run()
    assert not at.exception, at.exception
    status = at.session_state[f"live_{lang}_status"]
    assert status == "done", (status, at.session_state[f"live_{lang}_error"] if f"live_{lang}_error" in at.session_state else None)
    df = at.session_state["df"]
    assert repo_file in at.session_state["current_file"]
    assert at.session_state["result_source"] == "live"
    assert len(df) == 40                               # Obergrenze (Umgebungsvariable)
    assert {"sentiment", "confidence", "dominant_emotion"} <= set(df.columns)
    # Emotionen kommen aus dem Modell (nicht alles gleich / kein Zufalls-Ersatz)
    assert df["dominant_emotion"].nunique() > 1
    assert df["emotions"].notna().sum() > 0
    text = _page_text(at)
    assert "Stichprobe" in text or "sample" in text
    assert "Modul nicht verfügbar" not in text


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_interrupted_run_is_reported(page, lang):
    at = AppTest.from_file(page, default_timeout=TIMEOUT)
    at.run()
    at.session_state[f"live_{lang}_status"] = "running"
    at.session_state[f"live_{lang}_stage"] = "Testschritt"
    at.run()
    assert not at.exception, at.exception
    warnings = "\n".join(str(w.value) for w in at.warning)
    assert "Testschritt" in warnings
    assert ("unterbrochen" in warnings) or ("interrupted" in warnings)
    assert at.session_state["result_source"] == "example"   # keine halbfertigen Daten


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_empty_file_fails_honestly(fake_models, page, lang):
    at = AppTest.from_file(page, default_timeout=TIMEOUT)
    at.run()
    at.session_state[f"live_{lang}_request"] = {"data": b"", "name": "leer.csv", "lang": lang}
    at.session_state[f"live_{lang}_status"] = "pending"
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["result_source"] == "example"
    status = at.session_state[f"live_{lang}_status"]
    assert status in (None, "failed", "interrupted")
    warnings = "\n".join(str(w.value) for w in at.warning)
    assert warnings  # es gibt eine Meldung
