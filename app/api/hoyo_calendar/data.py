import json
from pathlib import Path

from app.core.base_data import BaseData


class HoyoCalendarData(BaseData):
    def load_file(self, file_path: Path) -> None:
        relative_path = file_path.relative_to(self.watch_dir)
        file_type, game, _ = relative_path.parts
        data_type = file_path.stem

        if not hasattr(self, file_type):
            setattr(self, file_type, {})
        file_type_data = getattr(self, file_type)

        if game not in file_type_data:
            file_type_data[game] = {}

        match file_type:
            case "json":
                f = file_path.open("r", encoding="utf-8")
                data = json.load(f)
                file_type_data[game][data_type] = data
                f.close()
            case "ics":
                file_type_data[game][data_type] = file_path

    def on_file_deleted(self, file_path: Path) -> None:
        relative_path = file_path.relative_to(self.watch_dir)
        file_type, game, _ = relative_path.parts
        data_type = file_path.stem

        if not hasattr(self, file_type):
            return
        file_type_data = getattr(self, file_type)

        if game not in file_type_data:
            return

        del file_type_data[game][data_type]


data = HoyoCalendarData("hoyo_calendar")
