from pydantic import BaseModel, BeforeValidator, model_validator
from datetime import datetime
from typing import List, Any, Optional, Annotated


class Entries(BaseModel):
    entries: List[Any]
    name: str
    status: str


class MediaListCollection(BaseModel):
    lists: List[Entries]


class Data(BaseModel):
    MediaListCollection: MediaListCollection
    User: Any


class Raw(BaseModel):
    data: Data


class Tag(BaseModel):
    category: Optional[str]
    description: Optional[str]
    name: Optional[str]
    rank: Optional[int]


class Title(BaseModel):
    english: Optional[str]
    native: Optional[str]
    romaji: Optional[str]


class Flattened(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def flatten(cls, data: Optional[Any]) -> Optional[Any]:
        if data:
            cls.convert_date("startedAt", data)
            cls.convert_date("completedAt", data)
            cls.convert_date("startDate", data)
            cls.convert_date("endDate", data)
            cls.flatten_image("coverImage", data)
            cls.flatten_image("avatar", data)
        return data

    @classmethod
    def convert_date(cls, field: str, data: Optional[Any]):
        if (
            field in data
            and data[field]["year"]
            and data[field]["month"]
            and data[field]["day"]
        ):
            data[field] = datetime(
                data[field]["year"], data[field]["month"], data[field]["day"]
            ).strftime("%Y-%m-%d")
        else:
            data[field] = None

    @classmethod
    def flatten_image(cls, field: str, data: Optional[Any]):
        if field in data:
            if "extraLarge" in data[field]:
                data[field] = data[field]["extraLarge"]
            elif "large" in data[field]:
                data[field] = data[field]["large"]


class FactAnime(Flattened):
    id: int
    userId: int
    mediaId: int
    averageScore: Optional[int]
    meanScore: Optional[int]
    popularity: Optional[int]
    trending: Optional[int]
    favourites: Optional[int]
    progress: Optional[int]
    episodes: Optional[int]
    score: Optional[int]
    watchStatus: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    stats: Optional[Any]
    rankings: Optional[Any]


class DimensionMedia(Flattened):
    id: int
    genres: List[str]
    description: Optional[str]
    coverImage: Optional[str]
    type: Optional[str]
    tags: List[Tag]
    episodes: Optional[int]
    format: Optional[str]
    season: Optional[str]
    seasonYear: Optional[int]
    startDate: Optional[str]
    endDate: Optional[str]
    synonyms: List[str]
    title: Title
    source: Optional[str]
    bannerImage: Optional[str]
    siteUrl: Optional[str]
    status: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def use_media_id(cls, data: Optional[Any]) -> Optional[Any]:
        if data and "mediaId" in data:
            data["id"] = data["mediaId"]
        return data


class DimensionUser(Flattened):
    id: int
    name: str
    avatar: Optional[str]
    bannerImage: str
    siteUrl: str
    statistics: Any


class Anime(Flattened):
    id: int
    userId: int
    genres: List[str]
    description: Optional[str]
    coverImage: Optional[str]
    type: Optional[str]
    tags: List[Tag]
    episodes: Optional[int]
    format: Optional[str]
    season: Optional[str]
    seasonYear: Optional[int]
    startDate: Optional[str]
    endDate: Optional[str]
    synonyms: List[str]
    title: Title
    source: Optional[str]
    bannerImage: Optional[str]
    averageScore: Optional[int]
    meanScore: Optional[int]
    popularity: Optional[int]
    trending: Optional[int]
    favourites: Optional[int]
    siteUrl: Optional[str]
    progress: Optional[int]
    score: Optional[int]
    startedAt: Optional[str]
    completedAt: Optional[str]
    status: Optional[str]
    watchStatus: Optional[str]


class User(Flattened):
    id: int
    name: str
    avatar: Optional[str]
    bannerImage: str
    siteUrl: str
