from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from app.db.session import SessionLocal
from app.models.file_status import FileStatus, FileStatusEnum
import os

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, source_id: str, workspace_id: str):
        self.source_id = source_id
        self.workspace_id = workspace_id

    def on_created(self, event):
        if event.is_directory:
            return
        _, ext = os.path.splitext(event.src_path)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return
        filename = os.path.basename(event.src_path)
        print(f"Detected: {filename}")
        db = SessionLocal()
        try:
            file_status = FileStatus(
                workspace_id=self.workspace_id,
                source_id=self.source_id,
                filename=filename,
                filepath=event.src_path,
                status=FileStatusEnum.pending,
            )
            db.add(file_status)
            db.commit()
        finally:
            db.close()


class WatcherManager:
    def __init__(self):
        self.observer = Observer()

    def watch(self, source_id: str, workspace_id: str, path: str):
        if not os.path.exists(path):
            print(f"Skipping watcher for missing path: {path}")
            return
        handler = FolderEventHandler(source_id=source_id, workspace_id=workspace_id)
        self.observer.schedule(handler, path=path, recursive=False)
        print(f"Watching: {path}")

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


watcher_manager = WatcherManager()

