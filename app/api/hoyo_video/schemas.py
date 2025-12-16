# Pydantic 模型 (Request/Response)
from datetime import datetime
from pydantic import BaseModel, Field


class UpdateTimeResponse(BaseModel):
    update_time: str = Field(
        ...,
        description="最近一次数据的更新时间，格式通常为 YYYY-MM-DD HH:MM:SS",
        examples=["2023-10-27 12:30:00"],
        pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
    )


class GameInfo(BaseModel):
    """
    游戏基本信息
    """

    name: str = Field(
        ...,
        description="游戏唯一标识/名称",
        examples=["原神", "崩坏：星穹铁道"],
    )
    weight: int = Field(
        ...,
        description="排序权重，值越大越靠前。用于前端展示顺序控制。",
        examples=[1, 2, 3],
    )
    news_detail_url: str = Field(
        ...,
        description="新闻详情跳转链接模板。注意：包含 '%id' 作为占位符，客户端需替换为实际文章ID。",
        examples=["https://ys.mihoyo.com/main/news/detail/%id"],
    )


class GameListResponse(BaseModel):
    total: int = Field(..., description="游戏总数")
    items: list[GameInfo] = Field(..., description="游戏列表数据")


class VideoTypeInfo(BaseModel):
    """
    视频分类标签信息
    """

    type_name: str = Field(
        ...,
        description="类型名称",
        examples=["全部视频", "角色演示", "拾枝杂谈", "其他"],
    )
    cover: str = Field(
        ...,
        description="封面图片链接",
        examples=[
            "https://fastcdn.mihoyo.com/content-v2/hk4e/161423/28fbaa73981862b02d29e0fec56797ac_9204611254022937976.png"
        ],
    )


class TypeListResponse(BaseModel):
    total: int
    items: list[VideoTypeInfo]


class VideoInfo(BaseModel):
    """
    单个视频详细信息
    """

    id: int = Field(..., description="视频唯一ID", examples=[123456])
    title: str = Field(..., description="视频标题")
    time: datetime = Field(..., description="发布时间")
    type: list[str] = Field(..., description="所属分类标签列表")
    src: str = Field(..., description="视频播放地址或跳转链接")
    cover: str = Field(..., description="视频封面图链接")
    intro: str = Field(..., description="视频简介/摘要")
    game: str = Field(..., description="所属游戏标识")


class VideoListResponse(BaseModel):
    total: int = Field(..., description="当前页/总视频数")
    items: list[VideoInfo]
