"""
Browser-Regressionstest B1: Nach Stop / Neuladen / Tab-Schliessen waehrend eines Laufs ist die
Lauf-Sperre sofort wieder frei, und eine neue Sitzung kann rechnen (kein "busy").

Echtes `streamlit run` + Playwright (Chromium). Wird uebersprungen, wenn Playwright oder ein
Browser fehlt (z. B. Streamlit Cloud, Cowork-VM). Lokal einmalig:
    pip install playwright && playwright install chromium
Start (im Repo-Ordner):  python -m pytest -q tests/test_live_lock_browser.py
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "tests" / "lock_app.py"
START = "Analyse starten"


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _server(tmp_path_factory, **extra_env):
    dummy = tmp_path_factory.mktemp("lock") / "dummy.csv"
    dummy.write_text("text\nhallo\n", encoding="utf-8")
    port = _free_port()
    env = dict(os.environ, LOCK_APP_FILE=str(dummy), HEREDUCATION_LIVE_ANALYSIS="1", **extra_env)
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(APP), "--server.port", str(port),
         "--server.headless", "true", "--browser.gatherUsageStats", "false"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}/"
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except OSError:
            time.sleep(0.5)
    else:
        proc.kill()
        pytest.skip("streamlit startet nicht")
    yield url
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    yield from _server(tmp_path_factory, HEREDUCATION_LIVE_COOLDOWN_SECONDS="0")


@pytest.fixture(scope="module")
def cooldown_server(tmp_path_factory):
    """B2: Pause 60 s, Ersatz-Lauf ~12 s (ueber der Mindestlaufzeit von 10 s)."""
    yield from _server(tmp_path_factory, HEREDUCATION_LIVE_COOLDOWN_SECONDS="60", LOCK_APP_STEPS="48")


@pytest.fixture(scope="module")
def browser():
    with playwright_sync.sync_playwright() as pw:
        try:
            b = pw.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
        except Exception as error:  # noqa: BLE001
            pytest.skip(f"kein Chromium: {type(error).__name__}")
        yield b
        b.close()


def _open(browser, url):
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector(f"text={START}", timeout=30000)
    return page


def _lock_state(page):
    page.wait_for_selector("text=LOCK_LOCKED=", timeout=20000)
    return "LOCK_LOCKED=True" in page.inner_text("body")


@pytest.mark.parametrize("mode", ["stop", "reload", "close"])
def test_lock_free_after_interrupt_and_new_run_works(server, browser, mode):
    p1 = _open(browser, server)
    p1.get_by_role("button", name=START).click()
    p1.wait_for_selector("text=Analyse läuft", timeout=20000)
    time.sleep(2)                                       # mitten im Lauf
    if mode == "stop":
        p1.get_by_role("button", name="Stop").click()
    elif mode == "reload":
        p1.reload()
    else:
        p1.close()
    time.sleep(2)

    p2 = _open(browser, server)
    assert not _lock_state(p2), f"Sperre haengt nach '{mode}' (B1)"
    # Eine neue Sitzung kann sofort rechnen – kein "Gerade läuft eine andere Analyse"
    p2.get_by_role("button", name=START).click()
    p2.wait_for_selector("text=STATUS=done", timeout=60000)
    assert "andere Analyse" not in p2.inner_text("body")
    p2.close()
    if mode != "close":
        p1.close()


def test_cooldown_after_finished_run_blocks_next_start(cooldown_server, browser):
    """B2 (K4, 28.09.2026): Nach einem fertigen Lauf zeigt eine NEUE Sitzung die Pause statt zu rechnen;
    die Sperre ist frei (kein 'busy'), die Auswahl bleibt fuer 'Erneut versuchen'."""
    p1 = _open(browser, cooldown_server)
    p1.get_by_role("button", name=START).click()
    p1.wait_for_selector("text=STATUS=done", timeout=60000)
    p1.close()

    p2 = _open(browser, cooldown_server)
    assert not _lock_state(p2)
    assert "Pause nach der letzten Analyse" in p2.inner_text("body")     # Hinweis schon vor dem Klick
    p2.get_by_role("button", name=START).click()
    p2.wait_for_selector("text=STATUS=cooldown", timeout=20000)
    body = p2.inner_text("body")
    assert "legt nach jeder Analyse eine Pause von 1 Minute ein" in body
    assert "andere Analyse" not in body
    assert p2.get_by_role("button", name="Erneut versuchen").count() == 1
    p2.close()
