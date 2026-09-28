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
    """Quelltext-Waechter: im finally-Block steht lock.release() vor jedem st.*-Zugriff."""
    import inspect
    source = inspect.getsource(L.run_pending_analysis)
    finally_block = source.split("    finally:", 1)[1]
    code_lines = [line.strip() for line in finally_block.splitlines()
                  if line.strip() and not line.strip().startswith("#")]
    assert code_lines[0] == "lock.release()", code_lines[:3]
