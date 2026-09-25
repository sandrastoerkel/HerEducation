"""HerEducation – entry point / navigation router.

Streamlit Cloud runs this file. It only builds the sidebar navigation
(page titles follow the language switcher) and runs the selected page.
The former start page lives in home.py. URL paths are fixed so existing
links keep working.
"""
import streamlit as st

from utils.language_switcher_config import init_language

init_language()

# (file, url_path, title DE, title EN) – url_path must stay stable
PAGES = [
    ("home.py", None, "Startseite", "Home"),
    ("pages/01_Projektidee.py", "Projektidee", "Projektidee", "Project Idea"),
    ("pages/02_HerAtlas_UNESCO_Dashboard.py", "HerAtlas_UNESCO_Dashboard",
     "HerAtlas UNESCO Dashboard", "HerAtlas UNESCO Dashboard"),
    ("pages/03_HerAtlas_Indicators_Development.py", "HerAtlas_Indicators_Development",
     "Indikatoren & Entwicklung", "Indicators & Development"),
    ("pages/04_YouTube_Analyzer.py", "YouTube_Analyzer", "YouTube-Analyse", "YouTube Analyzer"),
    ("pages/05_Kommentaranalyse_deutsch.py", "Kommentaranalyse_deutsch",
     "Kommentaranalyse (Deutsch)", "Comment Analysis (German)"),
    ("pages/06_Comment_Analysis_english.py", "Comment_Analysis_english",
     "Kommentaranalyse (Englisch)", "Comment Analysis (English)"),
    ("pages/07_Globale_Diskurs_Analysis.py", "Globale_Diskurs_Analysis",
     "Globale Diskursanalyse", "Global Discourse Analysis"),
]

lang_index = 3 if st.session_state.get("language") == "EN" else 2

pages = []
for entry in PAGES:
    path, url_path, title = entry[0], entry[1], entry[lang_index]
    if url_path is None:
        pages.append(st.Page(path, title=title, default=True))
    else:
        pages.append(st.Page(path, title=title, url_path=url_path))

st.navigation(pages).run()
