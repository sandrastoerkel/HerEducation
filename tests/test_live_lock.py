"""
Regressionstests B1 (Cloud-Test 26.09.2026, kritisch): Lauf-Sperre nach Stop/Neuladen/Tab-Schliessen.

Nach st.stop()/Stop-Knopf/Neuladen/Tab-Schliessen wirft Streamlit in der abgebrochenen Sitzung bei
JEDEM weiteren st.*-Zugriff (auch st.session_state) erneut StopException. Frueher stand
lock.release() hinter solchen Zugriffen -> Sperre blieb fuer alle Besucher:innen bis zum Reboot.

Diese Tests simulieren das ohne Browser (schnell, laufen immer). Der Browser-Test mit echtem
`streamlit run` steht in test_live_lock_browser.py (nur mit Playwright).

Start (im Repo-Ordner):  python -m pytest -q tests/test_live_lock.py
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from utils import live_comment_analysis as L  # noqa: E402

StopException = L.StopException
pytestmark = pytest.mark.skipif(StopException is None, reason="Streamlit ohne StopException")


class DyingSessionState(dict):
    """Wie st.session_state einer abgebrochenen Sitzung: nach kill() wirft jeder Zugriff StopException."""

    dead = False

    def kill(self):
        self.dead = True

    def _check(self):
        if self.dead:
            raise StopException()

    def __getitem__(self, key):
        self._check()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self._check()
        super().__setitem__(key, value)

    def get(self, key, default=None):
        self._check()
        return super().get(key, default)

    def pop(self, key, *default):
        self._check()
        return super().pop(key, *default)

    def __setattr__(self, name, value):
        if name == "dead":
            object.__setattr__(self, name, value)
            return
        self[name] = value


@pytest.fixture
def state(monkeypatch):
    s = DyingSessionState()
    monkeypatch.setattr(st, "session_state", s)
    lock = L._run_lock()
    if lock.locked():            # Reste frueherer Tests nie mitschleppen
        lock.release()
    yield s
    if lock.locked():
        lock.release()


def _pending(state, lang="de"):
    k = L._keys(lang)
    state[k["request"]] = {"data": b"text\nhallo\n", "name": "x.csv", "lang": lang}
    state[k["status"]] = "pending"


def _runner_stopped_in_step(file_obj, request, progress):
    """Stop waehrend eines Schritts: Streamlit bricht ab, danach ist die Sitzung 'tot'."""
    progress.step(0)
    st.session_state.kill()
    raise StopException()


def _runner_dies_on_session_access(file_obj, request, progress):
    """Sitzung stirbt, der naechste Zugriff auf st.session_state (hier: progress.step) wirft."""
    st.session_state.kill()
    progress.step(1)
    return {}


def _runner_other_error_then_dead(file_obj, request, progress):
    """Normaler Fehler, aber die Sitzung ist schon weg (except-Block wirft StopException)."""
    st.session_state.kill()
    raise RuntimeError("Modell weg")


@pytest.mark.parametrize("runner", [_runner_stopped_in_step, _runner_dies_on_session_access,
                                    _runner_other_error_then_dead])
def test_lock_is_released_when_session_dies_during_run(state, runner):
    _pending(state)
    with pytest.raises(StopException):
        L.run_pending_analysis("de", runner, ["A", "B", "C"])
    assert not L._run_lock().locked(), "Sperre haengt nach Abbruch (B1)"


def test_lock_is_released_when_session_dies_right_after_acquire(state, monkeypatch):
    """Abbruch genau zwischen acquire() und Lauf-Start (pop der Anfrage)."""

    class DieOnPop(DyingSessionState):
        def pop(self, key, *default):
            self.kill()
            return super().pop(key, *default)

    dying = DieOnPop()
    monkeypatch.setattr(st, "session_state", dying)
    _pending(dying)
    with pytest.raises(StopException):
        L.run_pending_analysis("de", lambda *a: {}, ["A"])
    assert not L._run_lock().locked()


def test_next_run_can_start_after_interrupted_run(state, monkeypatch):
    """Nach dem Abbruch kann eine andere Sitzung sofort rechnen (kein 'busy')."""
    _pending(state)
    with pytest.raises(StopException):
        L.run_pending_analysis("de", _runner_stopped_in_step, ["A"])
    # neue Sitzung
    fresh = DyingSessionState()
    monkeypatch.setattr(st, "session_state", fresh)
    _pending(fresh)
    import pandas as pd

    def ok_runner(file_obj, request, progress):
        progress.step(0)
        return {"df": pd.DataFrame({"comment_text": ["a"]}), "text_column": "comment_text", "notes": []}

    class Rerun(Exception):
        pass

    def fake_rerun():
        raise Rerun()

    monkeypatch.setattr(st, "rerun", fake_rerun)
    with pytest.raises(Rerun):
        L.run_pending_analysis("de", ok_runner, ["A"])
    assert fresh[L._keys("de")["status"]] == "done"
    assert not L._run_lock().locked()


def test_release_comes_before_any_session_access_in_finally():
    """Quelltext-Waechter: im finally-Block steht lock.release() vor jedem st.*-Zugriff.
    Davor ist nur das Setzen der Pause (B2) erlaubt – reines Python, kein st.*."""
    import inspect
    source = inspect.getsource(L.run_pending_analysis)
    finally_block = source.split("    finally:", 1)[1]
    code_lines = [line.strip() for line in finally_block.splitlines()
                  if line.strip() and not line.strip().startswith("#")]
    release = code_lines.index("lock.release()")
    assert code_lines[:release] == ["cooldown.mark(started, cooldown_seconds)"], code_lines[:3]
    import ast
    import textwrap
    tree = ast.parse(textwrap.dedent(inspect.getsource(L.Cooldown)))
    uses_st = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "st"]
    assert not uses_st, "Cooldown darf kein st.* benutzen (B1)"


# ---------------------------------------------------------------------------
# B2 (Cloud-Nachtest 28.09.2026): Pause nach jedem Live-Lauf, app-weit
# ---------------------------------------------------------------------------

class Rerun(Exception):
    pass


@pytest.fixture
def cooldown(monkeypatch):
    c = L._cooldown()
    c.ready_at = 0.0
    monkeypatch.setenv("HEREDUCATION_LIVE_COOLDOWN_SECONDS", "300")
    monkeypatch.setattr(L, "COOLDOWN_MIN_RUN_SECONDS", 0)
    monkeypatch.setattr(st, "rerun", lambda: (_ for _ in ()).throw(Rerun()))
    yield c
    c.ready_at = 0.0


def _ok_runner(file_obj, request, progress):
    import pandas as pd
    progress.step(0)
    return {"df": pd.DataFrame({"comment_text": ["a"]}), "text_column": "comment_text", "notes": []}


def test_cooldown_blocks_next_run_and_keeps_request(state, cooldown, monkeypatch):
    _pending(state)
    with pytest.raises(Rerun):
        L.run_pending_analysis("de", _ok_runner, ["A"])
    assert 290 < cooldown.remaining() <= 300
    # andere Sitzung direkt danach
    fresh = DyingSessionState()
    monkeypatch.setattr(st, "session_state", fresh)
    _pending(fresh)
    L.run_pending_analysis("de", _ok_runner, ["A"])        # kein Rerun: nicht gestartet
    k = L._keys("de")
    assert fresh[k["status"]] == "cooldown"
    assert fresh[k["request"]]["name"] == "x.csv", "Auswahl muss erhalten bleiben"
    assert not L._run_lock().locked()
    # Pause vorbei -> "Erneut versuchen" (status pending) startet den Lauf
    cooldown.ready_at = 0.0
    fresh[k["status"]] = "pending"
    with pytest.raises(Rerun):
        L.run_pending_analysis("de", _ok_runner, ["A"])
    assert fresh[k["status"]] == "done"


def test_cooldown_is_set_even_when_session_dies(state, cooldown):
    """Auch ein abgebrochener Lauf hat gerechnet -> Pause gilt (und die Sperre ist frei, B1)."""
    _pending(state)
    with pytest.raises(StopException):
        L.run_pending_analysis("de", _runner_stopped_in_step, ["A"])
    assert cooldown.remaining() > 0
    assert not L._run_lock().locked()


def test_short_run_sets_no_cooldown(state, cooldown, monkeypatch):
    """Lauf, der sofort scheitert (z. B. Datei ohne Text), hat kaum gerechnet -> keine Pause."""
    monkeypatch.setattr(L, "COOLDOWN_MIN_RUN_SECONDS", 10)

    def failing(file_obj, request, progress):
        raise L.LiveAnalysisError("keine Textspalte")

    _pending(state)
    with pytest.raises(Rerun):
        L.run_pending_analysis("de", failing, ["A"])
    assert state[L._keys("de")["status"]] == "failed"
    assert cooldown.remaining() == 0


def test_cooldown_defaults(monkeypatch):
    """Cloud 5 Min. (Entscheidung Sandra 28.09.2026), lokal keine Pause, per Umgebung einstellbar."""
    monkeypatch.delenv("HEREDUCATION_LIVE_COOLDOWN_SECONDS", raising=False)
    monkeypatch.setattr(L, "is_cloud", lambda: True)
    assert L.live_cooldown_seconds() == 300
    monkeypatch.setattr(L, "is_cloud", lambda: False)
    assert L.live_cooldown_seconds() == 0
    monkeypatch.setenv("HEREDUCATION_LIVE_COOLDOWN_SECONDS", "120")
    assert L.live_cooldown_seconds() == 120
    monkeypatch.setenv("HEREDUCATION_LIVE_COOLDOWN_SECONDS", "0")
    assert L.live_cooldown_seconds() == 0


def test_cooldown_mark_and_minutes_text():
    c = L.Cooldown()
    c.mark(started=None, seconds=300, now=1000)            # Lauf nie gestartet
    assert c.remaining(now=1000) == 0
    c.mark(started=900, seconds=300, now=1000)
    assert c.remaining(now=1000) == 300
    assert c.remaining(now=1400) == 0
