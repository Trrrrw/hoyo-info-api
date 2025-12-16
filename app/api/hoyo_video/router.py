# 路由逻辑
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import Response
from loguru import logger

from . import services, schemas


router = APIRouter(tags=["影像档案架"])


@router.get(
    "/update_time",
    response_model=schemas.UpdateTimeResponse,
    summary="获取最新一条视频的发布时间",
    operation_id="get_update_time",
)
async def get_update_time():
    try:
        time_str = await services.get_update_time()
        return {"update_time": time_str}
    except Exception as e:
        logger.error(f"获取更新时间失败: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/games",
    response_model=schemas.GameListResponse,
    summary="获取游戏信息列表",
    description="查询游戏中文名称和新闻详情页模板；使用时需将模板中的 '%id' 占位符替换为后续获取的视频ID，以合成完整的官方公告链接。",
    operation_id="list_games",
)
async def list_games():
    try:
        game_list = await services.list_games()
        return {"total": len(game_list), "items": game_list}
    except Exception as e:
        logger.error(f"获取游戏列表异常: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/{game}/types",
    response_model=schemas.TypeListResponse,
    summary="获取视频类型列表",
    description="查询特定游戏的所有视频栏目分类；注意返回列表除常规分类外，还包含 '全部视频' 与 '其他' 选项。",
    operation_id="list_video_types",
)
async def list_video_types(game: str = Path(..., description="游戏名称")):
    try:
        type_list = await services.list_video_types(game)
        return {"total": len(type_list), "items": type_list}
    except Exception as e:
        logger.error(f"获取类型列表异常: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/{game}/videos",
    response_model=schemas.VideoListResponse,
    summary="获取视频列表",
    description="查询特定游戏分类下的视频数据；支持分页参数(page/page_size)，**AI禁止**将 all 参数设为 True 以避免全量拉取。",
    operation_id="list_videos",
)
async def list_videos(
    game: str = Path(..., description="游戏名称", examples=["原神", "崩坏：星穹铁道"]),
    type: str = Query(
        ..., description="视频类型", examples=["全部视频", "角色PV", "其他"]
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    all_data: bool = Query(False, alias="all", description="是否获取全部"),
):
    try:
        total, videos = await services.list_videos(
            game, type, page, page_size, all_data
        )
        return {
            "total": total,
            "items": videos,
        }
    except Exception as e:
        logger.error(f"获取视频列表异常: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/{game}/videos/{video_id}",
    response_model=schemas.VideoInfo,
    summary="获取视频详细信息",
    operation_id="get_video_detail",
)
async def get_video_detail(
    game: str = Path(..., description="游戏名称"),
    video_id: int = Path(..., description="视频ID"),
):
    try:
        video_detail = await services.get_video_detail(game, video_id)
        if not video_detail:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
        return video_detail
    except Exception as e:
        logger.error(f"获取视频详情失败: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/search",
    response_model=schemas.VideoListResponse,
    summary="搜索视频",
    description="根据关键词（支持空格分隔）搜索视频；game 参数可选，传入游戏中文名可精确筛选，不传或传入 '全部游戏' 则默认搜索所有游戏。",
    operation_id="search_videos",
)
async def search_videos(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    game: str = Query("全部游戏", description="指定游戏范围"),
):
    try:
        results = await services.search_videos(q, game)
        return {
            "total": len(results),
            "items": results,
        }
    except Exception as e:
        logger.error(f"搜索视频失败: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/{game}/rss",
    responses={
        200: {
            "content": {"application/xml": {}},
            "description": "RSS XML content",
        }
    },
    summary="RSS 订阅文件获取",
    operation_id="get_rss",
)
async def get_rss(game: str):
    try:
        rss_content = await services.get_rss(game)
        if not rss_content:
            raise HTTPException(status_code=404, detail=f"RSS for {game} not found")
        return Response(content=rss_content, media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 RSS 失败: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
