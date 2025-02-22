import time
import os
import logging
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ModRegister(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            novo_mod = os.path.basename(event.src_path)
            mensagem = f'Mod adicionado: {novo_mod}'
            print(mensagem)
            logging.info(mensagem)
    
    def on_deleted(self, event):
        if not event.is_directory:
            mod_removido = os.path.basename(event.src_path)
            mensagem = f'Mod removido: {mod_removido}'
            print(mensagem)
            logging.info(mensagem)

       
mods_path = r"G:\mods" # Altere para o caminho da pasta de mods

# print(f"Mods path: {mods_path}")

observer = Observer()
event_handler = ModRegister()
observer.schedule(event_handler, mods_path, recursive=True)
observer.start()

print("Monitoring mods folder...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()