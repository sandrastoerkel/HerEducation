"""Central switch for developer/debug controls.

Debug widgets (cache buttons, detection debug, consistency tests) are hidden
for normal visitors. Enable them locally with either
  HEREDUCATION_DEBUG=1 streamlit run main.py
or in .streamlit/secrets.toml:
  debug = true
Default (production): off.
"""
import os

import streamlit as st


def is_debug() -> bool:
    if os.environ.get("HEREDUCATION_DEBUG", "").strip().lower() in ("1", "true", "yes", "on"):
        return True
    try:
        return bool(st.secrets.get("debug", False))
    except Exception:
        # No secrets.toml present -> not in debug mode
        return False
