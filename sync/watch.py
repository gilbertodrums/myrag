"""
watch.py — Observa el vault/ y sincroniza con Open WebUI automáticamente.

Uso:
    cd sync
    uv run python watch.py

Deja este proceso corriendo en una terminal. Cada vez que añadas,
edites o borres un archivo .md en vault/, el sync se ejecutará
automáticamente después de 2 segundos de inactividad.
"""
import sys
import time
import logging
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Añadir el directorio sync al path
sys.path.insert(0, str(Path(__file__).parent))
import sync as syncer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

VAULT_DIR = Path(__file__).parent.parent / "vault"
DEBOUNCE_SECONDS = 2  # Esperar 2s de inactividad antes de sincronizar


class VaultHandler(FileSystemEventHandler):
    def __init__(self):
        self._pending = False
        self._last_event = 0

    def on_any_event(self, event):
        # Solo interesa archivos .md, no directorios ni archivos temporales
        if event.is_directory:
            return
        src = getattr(event, "src_path", "")
        if not src.endswith(".md"):
            return
        if "~" in src or ".tmp" in src:
            return

        logging.info(f"Cambio detectado: {Path(src).name} — esperando {DEBOUNCE_SECONDS}s...")
        self._last_event = time.time()
        self._pending = True

    def should_sync(self):
        if not self._pending:
            return False
        if time.time() - self._last_event >= DEBOUNCE_SECONDS:
            self._pending = False
            return True
        return False


def main():
    if not VAULT_DIR.exists():
        logging.error(f"No se encontró el directorio vault/ en {VAULT_DIR}")
        return

    handler = VaultHandler()
    observer = Observer()
    observer.schedule(handler, str(VAULT_DIR), recursive=True)
    observer.start()

    logging.info(f"Observando cambios en {VAULT_DIR}")
    logging.info("Pulsa Ctrl+C para detener.")

    try:
        while True:
            time.sleep(0.5)
            if handler.should_sync():
                logging.info("Iniciando sincronización...")
                syncer.main()
    except KeyboardInterrupt:
        logging.info("Deteniendo watcher...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
