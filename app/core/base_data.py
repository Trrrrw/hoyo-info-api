from abc import ABC, abstractmethod
from pathlib import Path

from app.utils.dir_watcher import DirWatcher
from app.utils.logger import get_logger
from app.core.config import app_config


class BaseData(ABC):
    logger = get_logger("DATA")

    def __init__(self, data_subdir: str) -> None:
        self.watch_dir = (app_config.data_dir / data_subdir).resolve()
        self.data = None

        self.load_all()

        self.dir_watcher = DirWatcher(
            self.watch_dir,
            self.load_file,
            self.on_file_deleted,
        )
        self.dir_watcher.start()

    def load_all(self) -> None:
        for file_path in self.watch_dir.rglob("*"):
            if file_path.is_file():
                self.load_file(file_path)

    @abstractmethod
    def load_file(self, file_path: Path) -> None:
        pass

    @abstractmethod
    def on_file_deleted(self, file_path: Path) -> None:
        pass
