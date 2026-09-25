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
    # Review N2/M5: ehrlich "failed" (nicht "interrupted"), Meldung wurde angezeigt
    assert at.session_state[f"live_{lang}_error"]
    warnings = "\n".join(str(w.value) for w in at.warning)
    assert ("keine Kommentare" in warnings) or ("No comments" in warnings), warnings


# ---------------------------------------------------------------------------
# K1 (25.09.2026): Leser (H2), keine Zufalls-Emotionen (H1), M2–M6, N3, N5, N6, N8
# ---------------------------------------------------------------------------

from utils.comment_file_reader import CommentFileError, read_comments  # noqa: E402

COMMENTS_DIR = ROOT / "data" / "comments"


def _run_request(page, lang, data, name):
    at = AppTest.from_file(page, default_timeout=TIMEOUT)
    at.run()
    at.session_state[f"live_{lang}_request"] = {"data": data, "name": name, "lang": lang}
    at.session_state[f"live_{lang}_status"] = "pending"
    at.run()
    assert not at.exception, at.exception
    return at


def _warnings(at):
    return "\n".join(str(w.value) for w in at.warning)


def test_reader_header_csv_uses_text_column_not_second_column():
    data = ("\ufeffcomment_id,author,time,likes_count,text\n"
            "a1,@someone,1 year ago,3,\"This is the actual comment, with a comma\"\n"
            "a2,@other,2 years ago,0,\"Line one\nline two\"\n").encode("utf-8")
    df = read_comments(data, "x.csv")
    assert list(df.columns) == ["comment_text", "original_line"]
    assert list(df["comment_text"]) == ["This is the actual comment, with a comma", "Line one\nline two"]
    assert not df["comment_text"].str.startswith("@").any()


def test_reader_jsonl_with_csv_extension_has_no_prefix():
    data = b'{"cid": "1", "text": "Hallo \\"Welt\\"\\nzweite Zeile", "author": "@x"}\n{"cid": "2", "text": "  "}\n'
    df = read_comments(data, "comments.csv")
    assert list(df["comment_text"]) == ['Hallo "Welt"\nzweite Zeile']
    assert list(df["original_line"]) == [1]


def test_reader_json_list_semicolon_csv_and_bad_bytes():
    assert list(read_comments(b'[{"comment": "a"}, {"comment": "b"}]')["comment_text"]) == ["a", "b"]
    assert list(read_comments("id;Kommentar\n1;Grüße\n".encode("utf-8"))["comment_text"]) == ["Grüße"]
    df = read_comments("text\nK\xe4se\n".encode("latin-1"))   # kein UTF-8 -> ersetzt, kein Absturz
    assert len(df) == 1 and "\ufffd" in df["comment_text"][0]


@pytest.mark.parametrize("data,reason", [(b"", "empty"), (b"a,b\n1,2\n", "no_text_column"),
                                         (b"text\n\n", "empty")])
def test_reader_errors(data, reason):
    with pytest.raises(CommentFileError) as info:
        read_comments(data)
    assert info.value.reason == reason


def test_reader_all_repo_files():
    """Alle mitgelieferten Dateien: keine Praefixe, keine Escape-Reste, keine Autor-Namen als Text."""
    expected = {"Dweck": 1000, "Finland": 1000, "CNBC": 1000, "Lanz": 2082, "Malaysia": 1316}
    for path in COMMENTS_DIR.iterdir():
        df = read_comments(path.read_bytes(), path.name)
        key = next(k for k in expected if k in path.name)
        assert len(df) == expected[key], (path.name, len(df))
        texts = df["comment_text"]
        assert not texts.str.lstrip().str.startswith("text:").any()
        assert not texts.str.contains("\\n", regex=False).any()
        if path.read_bytes()[:1] != b"{":   # CSV mit Kopfzeile: Text != Autor
            header = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
            assert not texts.isin(set(header["author"])).any()


class RaisingModel:
    """Modell, das fuer jeden Text scheitert (MESS1-Szenario: nichts erkannt)."""

    def __call__(self, text, **kwargs):
        raise RuntimeError("kein Ergebnis")


@pytest.mark.parametrize("page,lang,repo_file", [(DE_PAGE, "de", "Markus Lanz"), (EN_PAGE, "en", "Malaysia")])
def test_no_random_emotions_when_model_detects_nothing(fake_models, monkeypatch, page, lang, repo_file):
    import models.model_loader as de
    import models.model_loader_english as en
    module = de if lang == "de" else en
    monkeypatch.setattr(module, "load_emotion_model", lambda: AllScoresPipeline(RaisingModel()))
    path = next(p for p in COMMENTS_DIR.iterdir() if repo_file in p.name)
    at = _run_request(page, lang, path.read_bytes(), path.name)
    assert at.session_state[f"live_{lang}_status"] == "done"
    df = at.session_state["df"]
    emotion_cols = [c for c in df.columns if c in ("emotions", "dominant_emotion", "anger", "joy", "fear")]
    assert emotion_cols == [], emotion_cols      # keine (Zufalls-)Werte im Ergebnis/Export
    notes = "\n".join(at.session_state[f"live_{lang}_notes"])
    assert ("nicht erkannt" in notes) or ("could not be detected" in notes)


def test_prepare_emotion_analysis_all_none_is_deterministic_and_empty():
    from utils.emotion_analysis import prepare_emotion_analysis
    from utils.emotion_analysis_english import prepare_emotion_analysis as prepare_en
    for prepare in (prepare_emotion_analysis, prepare_en):
        runs = []
        for _ in range(2):
            df = pd.DataFrame({"clean_text": ["erster text hier", "zweiter text hier"]})
            out = prepare(df, AllScoresPipeline(RaisingModel()), show_config_ui=False)
            assert out["dominant_emotion"].isna().all()
            runs.append(out.drop(columns=["emotions"]))
        pd.testing.assert_frame_equal(runs[0], runs[1])   # nichts Zufaelliges
        numeric = runs[0].drop(columns=["clean_text", "dominant_emotion"]).apply(pd.to_numeric, errors="coerce")
        assert numeric.isna().all().all()                 # leere Werte statt 0/Zufall


def test_unrecognized_comment_gets_no_dominant_emotion():
    from utils.emotion_analysis import dominant_emotion_or_none
    df = pd.DataFrame({"emotions": [{"anger": 0.1, "joy": 0.9}, None]})
    scores = pd.DataFrame({"anger": [0.1, float("nan")], "joy": [0.9, float("nan")]})
    assert list(dominant_emotion_or_none(df, scores)) == ["joy", None]   # frueher: "anger"


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_file_without_text_column_fails_honestly(fake_models, page, lang):
    at = _run_request(page, lang, b"id,author\n1,@a\n", "ohne_text.csv")
    assert at.session_state[f"live_{lang}_status"] is None       # Meldung gezeigt, Status zurueckgesetzt
    assert ("Textspalte" in _warnings(at)) or ("text column" in _warnings(at))
    assert at.session_state["result_source"] == "example"


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_sentiment_total_failure_is_an_error(fake_models, monkeypatch, page, lang):
    import models.model_loader as de
    import models.model_loader_english as en
    module = de if lang == "de" else en
    monkeypatch.setattr(module, "load_sentiment_model", lambda: RaisingModel())
    path = next(p for p in COMMENTS_DIR.iterdir() if ("Lanz" if lang == "de" else "Malaysia") in p.name)
    at = _run_request(page, lang, path.read_bytes(), path.name)
    assert at.session_state["result_source"] == "example"         # kein "100 % neutral"-Ergebnis
    assert ("Sentiment-Modell" in _warnings(at)) or ("sentiment model" in _warnings(at))


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_emotion_model_load_error_is_not_cached(fake_models, monkeypatch, page, lang):
    """Review M2: Ladefehler -> Hinweis im Lauf, aber kein gecachtes None (Loader wirft)."""
    import models.model_loader as de
    import models.model_loader_english as en
    module = de if lang == "de" else en

    def broken():
        raise OSError("Download fehlgeschlagen")
    monkeypatch.setattr(module, "load_emotion_model", broken)
    path = next(p for p in COMMENTS_DIR.iterdir() if ("Lanz" if lang == "de" else "Malaysia") in p.name)
    at = _run_request(page, lang, path.read_bytes(), path.name)
    assert at.session_state[f"live_{lang}_status"] == "done"
    assert "dominant_emotion" not in at.session_state["df"].columns
    notes = "\n".join(at.session_state[f"live_{lang}_notes"])
    assert ("Emotions-Modell" in notes) or ("emotion model" in notes)


def test_loader_source_does_not_swallow_errors():
    for name in ("models/model_loader.py", "models/model_loader_english.py"):
        source = (ROOT / name).read_text(encoding="utf-8")
        emotion = source.split("def load_emotion_model")[1].split("\n@st.cache_resource")[0]
        assert "return None" not in emotion and "except" not in emotion
        assert source.count("ttl=MODEL_TTL_SECONDS") == 3
        assert "def clear_models" in source


@pytest.mark.parametrize("page,lang", [(DE_PAGE, "de"), (EN_PAGE, "en")])
def test_second_run_waits_while_another_runs(fake_models, page, lang):
    """Review M3: prozessweiter Lauf-Lock -> ehrliche Meldung statt Parallelbetrieb."""
    from utils.live_comment_analysis import _run_lock
    lock = _run_lock()
    assert lock.acquire(blocking=False)
    try:
        path = next(p for p in COMMENTS_DIR.iterdir() if ("Lanz" if lang == "de" else "Malaysia") in p.name)
        at = _run_request(page, lang, path.read_bytes(), path.name)
        assert at.session_state["result_source"] == "example"
        assert ("andere Analyse" in _warnings(at)) or ("Another analysis" in _warnings(at))
    finally:
        lock.release()


def test_live_path_has_no_st_stop():
    """Review M5a: Nach st.stop() gehen alle Statusaenderungen des Durchlaufs verloren
    (Seite bliebe auf "Analyse laeuft"). Der Live-Pfad darf st.stop() nicht erreichen."""
    import inspect
    from utils import comment_file_reader, live_comment_analysis
    from utils.sentiment_analysis import perform_sentiment_analysis, SentimentAnalysisConfig
    def calls_stop(obj):
        return any("st.stop(" in line.split("#")[0] for line in inspect.getsource(obj).splitlines())
    for obj in (comment_file_reader, live_comment_analysis, perform_sentiment_analysis):
        assert not calls_stop(obj), obj
    out = perform_sentiment_analysis(pd.DataFrame({"t": [""]}), "t", FakeSentiment(["positive", "neutral", "negative"]),
                                     SentimentAnalysisConfig(min_comment_length=5))
    assert len(out) == 0


def test_click_after_interruption_does_not_restart_immediately():
    """Review N3: Klick auf das alte Startformular waehrend eines Laufs startet nicht sofort neu."""
    at = AppTest.from_file(DE_PAGE, default_timeout=TIMEOUT)
    at.run()
    at.session_state["live_de_status"] = "running"          # Lauf wurde durch den Klick unterbrochen
    at.session_state["live_de_stage"] = "Testschritt"
    next(b for b in at.button if "▶" in str(b.label)).click()
    at.run()
    assert not at.exception, at.exception
    assert "unterbrochen" in _warnings(at)
    assert at.session_state["live_de_status"] is None        # kein neuer Lauf angefordert
    assert "live_de_request" not in at.session_state


def test_files_per_language_and_video_ids():
    from utils.example_analyses import known_source_names, repo_files_for_language
    from utils.video_info import video_id_for_display
    de = [Path(p).name for p in repo_files_for_language("de")]
    en = [Path(p).name for p in repo_files_for_language("en")]
    assert len(de) == 1 and "Lanz" in de[0]
    assert len(en) == 4 and not any("Lanz" in n for n in en)
    known = known_source_names("de") + repo_files_for_language("de")
    assert video_id_for_display(de[0], known) == "87TYPn6gbwA"
    assert video_id_for_display("meine_datei_abcdefghijk.csv", known) is None   # Upload: keine Video-ID


def test_number_format_only_touches_numbers():
    from utils.live_comment_analysis import fmt_int, sample_note
    assert fmt_int(2082, "de") == "2.082" and fmt_int(2082, "en") == "2,082"
    assert sample_note("de", 2082, 300) == ("Die Datei enthält 2.082 Kommentare – analysiert wurde "
                                            "eine feste Stichprobe von 300.")
