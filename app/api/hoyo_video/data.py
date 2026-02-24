import json
from pathlib import Path

from app.core.base_data import BaseData


class HoyoVideoData(BaseData):
    def load_file(self, file_path: Path) -> None:
        if file_path.name == "data.json":
            f = file_path.open("r", encoding="utf-8")
            setattr(self, "all_data", json.load(f))
            f.close()
        elif file_path.suffix == ".rss":
            if not hasattr(self, "rss"):
                setattr(self, "rss", {})
            rss_data = getattr(self, "rss")
            rss_data[file_path.stem] = file_path

    def on_file_deleted(self, file_path: Path) -> None:
        if file_path.name == "data.json":
            setattr(self, "all_data", {})
        elif file_path.suffix == ".rss":
            if hasattr(self, "rss"):
                rss_data = getattr(self, "rss")
                del rss_data[file_path.stem]


data = HoyoVideoData("hoyo_video")
