from pathlib import Path
from typing import Callable
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from app.utils.logger import get_logger

logger = get_logger("WATCHER")


class DirectoryChangeHandler(FileSystemEventHandler):
    def __init__(
        self,
        load_file: Callable[[Path], None],
        on_file_deleted: Callable[[Path], None],
    ):
        self.load_file = load_file
        self.on_file_deleted = on_file_deleted

    def on_created(self, event: FileSystemEvent) -> None:
        logger.info(f"创建文件: {event.src_path}")
        self.load_file(Path(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        logger.info(f"修改文件: {event.src_path}")
        self.load_file(Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        logger.info(f"删除文件: {event.src_path}")
        self.on_file_deleted(Path(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        logger.info(f"移动文件: {event.src_path} -> {event.dest_path}")
        self.on_file_deleted(Path(event.src_path))
        self.load_file(Path(event.dest_path))


class DirWatcher:
    def __init__(
        self,
        watch_dir: Path,
        load_file: Callable[[Path], None],
        delete_file: Callable[[Path], None],
        recursive: bool = True,
    ) -> None:
        """
        Args:
            watch_dir: 要监控的目录
            callback: 回调函数，接收变化的文件路径集合
            recursive: 是否递归监控子目录
        """
        self.watch_dir = Path(watch_dir).resolve()
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.recursive = recursive

        self.observer = Observer()
        self.handler = DirectoryChangeHandler(load_file, delete_file)

    def start(self) -> None:
        """开始监控"""
        self.observer.schedule(
            self.handler, path=self.watch_dir, recursive=self.recursive
        )
        self.observer.start()
        logger.info(f"开始监控目录: {self.watch_dir.relative_to(Path.cwd())}")

    def stop(self) -> None:
        """停止监控"""
        if self.observer and self.observer.is_alive():
            self.handler.flush()
            self.observer.stop()
            self.observer.join()
            logger.info(f"停止监控目录: {self.watch_dir}")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
