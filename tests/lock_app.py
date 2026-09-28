"""Mini-App fuer den Browser-Regressionstest B1 (test_live_lock_browser.py).

Nutzt die ECHTE utils/live_comment_analysis.py mit einem Ersatz-Lauf (Fortschrittsbalken,
~6 s), damit Stop/Neuladen/Tab-Schliessen waehrend eines Laufs geprueft werden kann.
Start:  LOCK_APP_FILE=<irgendeine Datei> streamlit run tests/lock_app.py
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import live_comment_analysis as L  # noqa: E402

STEPS = int(os.environ.get("LOCK_APP_STEPS", "24"))


def runner(file_obj, request, progress):
    progress.step(0)
    bar = st.progress(0)
    for i in range(STEPS):
        time.sleep(0.25)                       # simuliert Modellrechnung
        bar.progress((i + 1) / STEPS)
    progress.step(1)
    return {"df": pd.DataFrame({"comment_text": ["a"]}), "text_column": "comment_text", "notes": []}


st.sidebar.write(f"LOCK_LOCKED={L._run_lock().locked()}")
L.run_pending_analysis("de", runner, ["Rechnen", "Fertig"])
L.render_status("de")
st.write("STATUS=" + str(st.session_state.get(L._keys("de")["status"])))
L.render_live_section("de", [os.environ["LOCK_APP_FILE"]])
