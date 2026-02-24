# 具体的业务逻辑
import os
import aiofiles
from pathlib import Path
from datetime import datetime
from loguru import logger
from pydantic import ValidationError

from . import schemas
from .data import data


async def get_update_time() -> str:
    return data.all_data.get("update_time", "1970-01-01 08:00:00.000000")


async def list_games() -> list[schemas.GameInfo]:
    game_list = []
    raw_data = data.all_data.get("data", {})
    for game_name, game_data in raw_data.items():
        game_list.append(
            schemas.GameInfo(
                name=game_name,
                weight=game_data.get("weight", 0),
                news_detail_url=game_data.get("news_detail_url", ""),
            )
        )
    game_list.sort(key=lambda x: x.weight, reverse=False)
    return game_list


async def list_video_types(game: str) -> list[schemas.TypeListResponse]:
    game_data = data.all_data.get("data", {}).get(game, {})
    video_list = game_data.get("videos", [])
    if not game_data or not video_list:
        return []
    type_list = game_data.get("video_types", [])
    if "其他" not in type_list:
        type_list.append("其他")

    results = []

    def sort_videos_by_time(v_list):
        return sorted(
            v_list,
            key=lambda v: datetime.strptime(
                v.get("time", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
            reverse=True,
        )

    for type_name in type_list:
        one_type_videos = [v for v in video_list if type_name in v.get("type", [])]
        sorted_videos = sort_videos_by_time(one_type_videos)

        if sorted_videos:
            results.append(
                {"type_name": type_name, "cover": sorted_videos[0].get("cover", "")}
            )
    if video_list:
        results.insert(
            0,
            {
                "type_name": "全部视频",
                "cover": video_list[-1].get("cover", ""),  # 原逻辑是取最后一个？
            },
        )

    return results


async def list_videos(
    game: str,
    type: str,
    page: int,
    page_size: int,
    all_data: bool,
) -> tuple[int, list[schemas.VideoInfo]]:
    game_data = data.all_data.get("data", {}).get(game, {})
    video_list = game_data.get("videos", [])
    if not game_data or not video_list:
        return 0, []

    if type == "全部视频":
        filtered_videos = video_list
    else:
        filtered_videos = [v for v in video_list if type in v.get("type", [])]

    sorted_videos = sorted(
        filtered_videos,
        key=lambda v: datetime.strptime(
            v.get("time", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
        ),
        reverse=True,
    )
    total = len(sorted_videos)

    if all_data:
        paged_videos = sorted_videos
    else:
        start = (page - 1) * page_size
        end = start + page_size
        paged_videos = sorted_videos[start:end]

    result_videos = []
    for video in paged_videos:
        video_info = schemas.VideoInfo(**video)
        result_videos.append(video_info)

    return total, result_videos


async def get_video_detail(game: str, video_id: int) -> schemas.VideoInfo | None:
    game_data = data.all_data.get("data", {}).get(game, {})
    video_list = game_data.get("videos", [])
    for video in video_list:
        if video.get("id") == video_id:
            return schemas.VideoInfo(**video)
    return None


async def search_videos(q: str, game: str) -> list[schemas.VideoInfo]:
    results: list[tuple[int, schemas.VideoInfo]] = []

    query_list = q.lower().strip().split()
    raw_data = data.all_data.get("data", {})

    target_games = [game] if game != "全部游戏" else raw_data.keys()
    for game_name in target_games:
        game_data = raw_data.get(game_name)
        if not game_data:
            continue
        weight = game_data.get("weight", 0)

        for video in game_data.get("videos", []):
            title = video.get("title", "").lower()
            # 关键词全匹配
            if all(k in title for k in query_list if k):
                try:
                    video_obj = schemas.VideoInfo(**video)
                    results.append((weight, video_obj))
                except ValidationError as e:
                    logger.warning(
                        f"视频数据格式错误: {video.get('title', 'Unknown')} - {e}"
                    )
                    continue

    results.sort(key=lambda x: (-x[0], x[1].time), reverse=True)
    return [item[1] for item in results]


RSS_FOLDER = Path("data/hoyo_video/rss")
RSS_LAST_MTIME = {}
RSS_CACHE = {}


async def get_rss(game: str) -> bytes | None:
    global RSS_CACHE, RSS_LAST_MTIME
    rss_file = RSS_FOLDER / (game + ".xml")
    try:
        mtime = os.path.getmtime(rss_file)
    except OSError:
        logger.warning(f"RSS 文件不存在或无法访问: {rss_file}")
        return None
    if game in RSS_LAST_MTIME and RSS_LAST_MTIME[game] == mtime and game in RSS_CACHE:
        logger.debug(f"RSS 文件未更改，使用缓存: {rss_file}")
        return RSS_CACHE[game]
    logger.info(f"加载 RSS 文件: {rss_file}")
    try:
        async with aiofiles.open(rss_file, "rb") as f:
            content = await f.read()
            RSS_CACHE[game] = content
            RSS_LAST_MTIME[game] = mtime
            return content
    except Exception as e:
        logger.error(f"加载 RSS 失败: {e}")
        if game in RSS_CACHE:
            return RSS_CACHE[game]
        raise e


async def get_rss_path(game: str) -> str:
    return data.rss.get(game, "")
