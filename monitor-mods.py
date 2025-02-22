import time
import os
import logging
import configparser
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from threading import Timer, Lock

logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

MOD_EXTENSIONS = {'.esp', '.esm', '.bsa', '.ba2', '.pak', '.jar'}
CONFIG_FILE = 'config.ini'

class ModRegister(FileSystemEventHandler):
    def __init__(self, debounce_interval=2):
        super().__init__()
        self.debounce_interval = debounce_interval
        self.pending_events = {} # dictionary
        self.timer = None # timer to avoid multiple events in short time
        self.lock = Lock()  # avoid race condition

    def is_valid_mod(self, file_path):
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        if filename.startswith('~') or filename.endswith('.tmp'):
            return False
        return ext in MOD_EXTENSIONS

    def schedule_update(self): # when a event is created call process_pending_events() to process events in dictionary after debounce_interval
        with self.lock:
            if self.timer:
                self.timer.cancel()
            self.timer = Timer(self.debounce_interval, self.process_pending_events)
            self.timer.start()

    def process_pending_events(self): # process events in dictionary to note in log the last status and clear it
        with self.lock:
            for mod, event_type in self.pending_events.items():
                if event_type == 'added':
                    mensagem = f'Mod adicionado: {mod}'
                else:
                    mensagem = f'Mod removido: {mod}'
                print(mensagem)
                logging.info(mensagem)
            self.pending_events.clear()
            self.timer = None

    def on_created(self, event): # event
        if not event.is_directory and self.is_valid_mod(event.src_path):
            mod = os.path.basename(event.src_path)
            with self.lock:
                self.pending_events[mod] = 'added'
            self.schedule_update()

    def on_deleted(self, event): # event
        if not event.is_directory and self.is_valid_mod(event.src_path):
            mod = os.path.basename(event.src_path)
            with self.lock:
                self.pending_events[mod] = 'removed'
            self.schedule_update()

def get_mods_path():
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'DEFAULT' in config and 'mods_path' in config['DEFAULT']:
            return config['DEFAULT']['mods_path']
    
    while True:
        path = input("Por favor, digite o caminho da pasta de mods: ").strip()
        if os.path.isdir(path):
            # Salva no arquivo de configuração
            config['DEFAULT'] = {'mods_path': path}
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
            return path
        print(f"Erro: O caminho '{path}' não existe ou não é uma pasta válida!")

mods_path = get_mods_path()

observer = Observer()
event_handler = ModRegister(debounce_interval=2)
observer.schedule(event_handler, mods_path, recursive=True)
observer.start()

print("Monitoring mods folder...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
