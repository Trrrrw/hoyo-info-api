from pathlib import Path

from .data import data
from . import schemas


async def list_games() -> list[schemas.GameInfo]:
    json_data = getattr(data, "json", {})
    return [schemas.GameInfo(name=game_name) for game_name in json_data.keys()]


async def list_event_types(game: str) -> list[schemas.EventTypeInfo]:
    json_data = getattr(data, "json", {})
    if game not in json_data:
        raise KeyError(f"Game {game} not found")
    game_data = json_data.get(game, {})
    return [schemas.EventTypeInfo(name=type_name) for type_name in game_data.keys()]


async def get_event_data(game: str, data_type: str) -> list[dict]:
    json_data = getattr(data, "json", {})
    if game not in json_data:
        raise KeyError(f"Game {game} not found")
    game_data = json_data.get(game, {})
    if data_type not in game_data:
        raise KeyError(f"Event type {data_type} not found for game {game}")
    return game_data.get(data_type, [])


async def get_birthday(game: str, char: str) -> dict:
    json_data = getattr(data, "json", {})
    if game not in json_data:
        raise KeyError(f"Game {game} not found")
    game_data = json_data.get(game, {})
    if "生日" not in game_data:
        raise KeyError(f"Event type 生日 not found for game {game}")
    birthday_data = game_data.get("生日", [])
    for item in birthday_data:
        if item.get("name", "") == char:
            return item
    raise KeyError(f"Character {char} not found in birthday data for game {game}")


async def get_ics_path(game: str, data_type: str) -> str:
    ics_data = getattr(data, "ics", {})
    if game not in ics_data:
        raise KeyError(f"Game {game} not found")
    game_data = ics_data.get(game, {})
    if data_type not in game_data:
        raise KeyError(f"Event type {data_type} not found for game {game}")
    ics_path = game_data.get(data_type, None)
    if not Path(ics_path).exists():
        raise FileNotFoundError(f"ICS file {ics_path} not found")
