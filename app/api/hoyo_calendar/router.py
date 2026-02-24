from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.responses import FileResponse

from app.utils.logger import get_logger
from . import services, schemas

router = APIRouter(tags=["游戏日历订阅"])
logger = get_logger("API_CAL")


@router.get(
    "/games",
    response_model=schemas.GameListResponse,
    summary="获取游戏日历订阅 - 支持的游戏列表",
    description="""
返回当前日历订阅功能支持的游戏名称列表。

**返回数据示例：**
```json
{
    "total": 2,
    "items": [
        {
            "name": "原神"
        },
        {
            "name": "崩坏：星穹铁道"
        }
    ]
}
```
""",
    operation_id="cal_list_games",
    responses={
        200: {"description": "成功获取游戏列表"},
        500: {"description": "服务器内部错误"},
    },
)
async def list_games() -> schemas.GameListResponse:
    try:
        game_list = await services.list_games()
        return schemas.GameListResponse(
            total=len(game_list),
            items=game_list,
        )
    except Exception as e:
        logger.error(f"获取游戏名列表异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/{game}/event-types",
    response_model=schemas.EventTypeListResponse,
    summary="获取游戏支持的事件类型",
    description="""
返回指定游戏支持的事件类型列表。

**支持的游戏：**
- 原神
- 崩坏：星穹铁道
- 绝区零

**返回的事件类型示例：**
- 活动
- 生日

**注意事项：**
- 游戏名称为中文
- 如果游戏不存在，返回 404
""",
    operation_id="cal_list_event_types",
    responses={
        200: {"description": "成功获取事件类型列表"},
        404: {"description": "游戏不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def list_event_types(
    game: str = Path(..., description="游戏名称"),
) -> schemas.EventTypeListResponse:
    try:
        type_list = await services.list_event_types(game)
        return schemas.EventTypeListResponse(
            total=len(type_list),
            items=type_list,
        )
    except KeyError:
        logger.error(f"游戏 {game} 不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"游戏 {game} 不存在"
        )
    except Exception as e:
        logger.error(f"获取游戏支持的事件类型异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/{game}/events/{data_type}",
    response_model=schemas.EventListResponse,
    summary="获取游戏事件数据",
    description="""
获取指定游戏和类型的事件数据，支持分页。

**支持的游戏和事件类型组合：**
- 原神 / 活动
- 原神 / 生日
- 崩坏：星穹铁道 / 活动
- 崩坏：星穹铁道 / 生日

**分页工作原理**：
- `offset`：要跳过的数据数量（从0开始）
- `limit`：要获取的数据数量（默认20，最大100）
- 返回的数据范围：`[offset, offset + limit)`

**注意事项**：
- 如果游戏或事件类型不存在，返回404
- 如果offset超出数据范围，返回空列表
- 建议始终使用分页参数，避免返回大量数据

**返回数据格式**：
```json
{
    "total": 100,
    "items": [...],
    "offset": 0,
    "limit": 20
}
""",
    operation_id="cal_get_event_data",
    responses={
        200: {"description": "成功获取事件数据"},
        404: {"description": "游戏或事件类型不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_event_data(
    game: str = Path(..., description="游戏名称"),
    data_type: str = Path(..., description="事件类型"),
    offset: int = Query(0, ge=0, description="偏移量，从第几条开始"),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="每页数量（默认20，最大100）",
    ),
) -> schemas.EventListResponse:
    try:
        data_list = await services.get_event_data(game, data_type)

        # 分页处理
        total = len(data_list)
        if limit > 0:
            items = data_list[offset : offset + limit]
        else:
            items = data_list[offset:]

        return schemas.EventListResponse(
            total=total, items=items, offset=offset, limit=limit
        )
    except KeyError:
        logger.error(f"游戏 {game} 或事件类型 {data_type} 不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏 {game} 或事件类型 {data_type} 不存在",
        )
    except Exception as e:
        logger.error(f"获取游戏事件数据异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/{game}/birthday",
    summary="获取角色生日",
    description="""
返回指定游戏中指定角色的生日信息。

**支持的游戏：**
- 原神
- 崩坏：星穹铁道
- 绝区零

**注意事项：**
- 角色名称为中文
- 如果游戏或角色不存在，返回 404
""",
    operation_id="cal_get_birthday",
    responses={
        200: {"description": "成功获取角色生日"},
        404: {"description": "游戏或角色不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_birthday(
    game: str = Path(..., description="游戏名称"),
    char: str = Query(..., description="角色名称"),
):
    try:
        birthday = await services.get_birthday(game, char)
        return birthday
    except KeyError:
        logger.error(f"游戏 {game} 或角色 {char} 不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏 {game} 或角色 {char} 不存在",
        )
    except Exception as e:
        logger.error(f"获取游戏{game}角色{char}生日异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/ics",
    summary="导出日历文件",
    description="""
导出指定游戏和事件类型的日历文件（.ics 格式）。

**支持的游戏和事件类型：**
- 原神 / 活动
- 原神 / 生日
- 崩坏：星穹铁道 / 活动
- 崩坏：星穹铁道 / 生日

**返回文件：**
- 格式：.ics 日历文件
- 文件名：{游戏}{事件类型}日历.ics

**注意事项：**
- 如果游戏或事件类型不存在，返回404
- 如果文件生成失败，返回500
""",
    operation_id="cal_export_ics",
    responses={
        200: {"description": "成功获取日历文件", "content": {"text/calendar": {}}},
        404: {"description": "游戏或事件类型不存在，或ICS文件不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_ics(
    game: str = Query(..., description="游戏名称"),
    data_type: str = Query(..., description="事件类型"),
):
    try:
        ics_path = await services.get_ics_path(game, data_type)
        return FileResponse(path=ics_path, filename=f"{game}{data_type}日历.ics")
    except KeyError:
        logger.error(f"游戏 {game} 或事件类型 {data_type} 不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏 {game} 或事件类型 {data_type} 不存在",
        )
    except FileNotFoundError:
        logger.error(f"ICS文件 {ics_path} 不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICS文件 {game}/{data_type} 不存在",
        )
    except Exception as e:
        logger.error(f"获取游戏{data_type}数据异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
