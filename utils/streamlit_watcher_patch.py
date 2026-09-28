"""
NEU-a (Cloud-Nachtest 28.09.2026): Watcher-Tracebacks trotz `fileWatcherType = "none"`.

Ursache (Quelltext Streamlit 1.45.0, im Repo gepinnt):
- runtime/app_session.py ruft nach jedem erfolgreichen Skriptlauf (und bei Neustart per Rerun)
  `LocalSourcesWatcher.update_watched_modules()` auf – fuer jede Sitzung, unabhaengig vom
  Watcher-Typ.
- watcher/local_sources_watcher.py prueft dort NICHT, ob ueberhaupt beobachtet wird: Sobald
  sich sys.modules seit dem letzten Aufruf dieser Sitzung geaendert hat (bei einer NEUEN Sitzung
  immer, z. B. nach Neuladen), ruft es get_module_paths() fuer ALLE geladenen Module auf. Erst
  danach verwirft _register_watcher() alles, weil der Typ "none" ist (NoOpPathWatcher).
- get_module_paths() liest __file__/__spec__/__path__; bei den trägen transformers-Modulen loest
  das Importe aus, die an fehlendem torchvision scheitern -> je Modul ein Traceback im Log
  ("Examining the path of transformers.models... raised") plus CPU-Last.

Loesung: Ist der Watcher-Typ "none", ist der Modul-Scan wirkungslos und wird uebersprungen.
Bei jedem anderen Watcher-Typ (z. B. lokal "auto") bleibt Streamlit unveraendert.
"""
import logging

_LOGGER = logging.getLogger(__name__)
_PATCHED_FLAG = "_hereducation_noop_when_watcher_none"


def apply() -> bool:
    """Einmal pro Prozess anwenden (main.py). Gibt True zurueck, wenn der Scan jetzt uebersprungen wird."""
    try:
        from streamlit import config
        from streamlit.watcher.local_sources_watcher import LocalSourcesWatcher
    except Exception:  # noqa: BLE001 – andere Streamlit-Version: nichts tun
        return False
    if config.get_option("server.fileWatcherType") != "none":
        return False
    original = LocalSourcesWatcher.update_watched_modules
    if getattr(original, _PATCHED_FLAG, False):
        return True

    def update_watched_modules(self):
        # Mit Watcher-Typ "none" registriert Streamlit ohnehin keinen Beobachter (NoOpPathWatcher);
        # der teure Scan ueber alle Module waere reine Last.
        from streamlit import config as _config
        if _config.get_option("server.fileWatcherType") == "none":
            return None
        return original(self)

    setattr(update_watched_modules, _PATCHED_FLAG, True)
    LocalSourcesWatcher.update_watched_modules = update_watched_modules
    _LOGGER.info("NEU-a: module scan of LocalSourcesWatcher disabled (fileWatcherType=none)")
    return True
