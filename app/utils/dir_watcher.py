import threading
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
        debounce_seconds: float = 0.5,
    ):
        self.load_file = load_file
        self.on_file_deleted = on_file_deleted
        self.debounce_seconds = debounce_seconds
        # 存储每个文件路径对应的定时器: {path_str: Timer}
        self._timers: dict[str, threading.Timer] = {}
        # 锁，用于保护 _timers 字典的线程安全访问
        self._timer_lock = threading.Lock()

    def _debounce_trigger(self, file_path: Path, callback: Callable[[Path], None]):
        """内部防抖触发器：取消旧定时器，启动新定时器"""
        path_str = str(
            file_path.resolve()
        )  # 使用绝对路径字符串作为 Key，避免相对路径问题

        with self._timer_lock:
            # 1. 如果该文件已有待执行的定时器，先取消它
            if path_str in self._timers:
                logger.debug(f"重置防抖计时器: {file_path}")
                self._timers[path_str].cancel()
                del self._timers[path_str]

            # 2. 创建并启动新定时器
            def _safe_execute():
                """定时器到期后的执行包装器，负责清理状态和异常捕获"""
                try:
                    callback(file_path)
                except Exception as e:
                    # 关键：捕获回调中的异常，防止后台线程崩溃导致监听停止
                    logger.error(f"执行回调时发生错误 {file_path}: {e}", exc_info=True)
                finally:
                    # 3. 执行完毕后，从字典中移除定时器引用
                    with self._timer_lock:
                        self._timers.pop(path_str, None)

            timer = threading.Timer(self.debounce_seconds, _safe_execute)
            timer.daemon = True  # 设为守护线程，防止主程序退出时阻塞
            self._timers[path_str] = timer
            timer.start()
            logger.debug(f"计划执行任务: {file_path} (延迟 {self.debounce_seconds}s)")

    def on_created(self, event: FileSystemEvent) -> None:
        logger.info(f"创建文件: {event.src_path}")
        self._debounce_trigger(Path(event.src_path), self.load_file)

    def on_modified(self, event: FileSystemEvent) -> None:
        logger.info(f"修改文件: {event.src_path}")
        self._debounce_trigger(Path(event.src_path), self.load_file)

    def on_deleted(self, event: FileSystemEvent) -> None:
        logger.info(f"删除文件: {event.src_path}")
        self.on_file_deleted(Path(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        logger.info(f"移动文件: {event.src_path} -> {event.dest_path}")
        self.on_file_deleted(Path(event.src_path))
        self._debounce_trigger(Path(event.src_path), self.load_file)


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
