from pydantic import BaseModel, BeforeValidator
from datetime import datetime
from typing import List, Any, Optional, Annotated


class EntriesModel(BaseModel):
    entries: List[Any]
    name: str
    status: str


class MediaListCollectionModel(BaseModel):
    lists: List[EntriesModel]


class DataModel(BaseModel):
    MediaListCollection: MediaListCollectionModel
    User: Any


class RawModel(BaseModel):
    data: DataModel


class TagModel(BaseModel):
    category: Optional[str]
    description: Optional[str]
    name: Optional[str]
    rank: Optional[int]


class TitleModel(BaseModel):
    english: Optional[str]
    native: Optional[str]
    romaji: Optional[str]


class CoverImageModel(BaseModel):
    extraLarge: str

    def to_string(value: Optional[Any]) -> Optional[str]:
        if not value or not value["extraLarge"]:
            return None
        return value["extraLarge"]


class DateModel(BaseModel):
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]

    def to_string(value: Optional[Any]) -> Optional[datetime]:
        if not value or not value["year"] or not value["month"] or not value["day"]:
            return None
        return datetime(value["year"], value["month"], value["day"]).strftime(
            "%Y-%m-%d"
        )


class AnimeModel(BaseModel):
    id: int
    genres: List[str]
    description: Optional[str]
    coverImage: Annotated[Optional[str], BeforeValidator(CoverImageModel.to_string)]
    type: Optional[str]
    tags: List[TagModel]
    episodes: Optional[int]
    format: Optional[str]
    season: Optional[str]
    seasonYear: Optional[int]
    startDate: Annotated[Optional[str], BeforeValidator(DateModel.to_string)]
    endDate: Annotated[Optional[str], BeforeValidator(DateModel.to_string)]
    synonyms: List[str]
    title: TitleModel
    source: Optional[str]
    bannerImage: Optional[str]
    averageScore: Optional[int]
    meanScore: Optional[int]
    popularity: Optional[int]
    trending: Optional[int]
    favourites: Optional[int]
    siteUrl: Optional[str]
    rankings: Optional[Any]
    stats: Optional[Any]
    progress: Optional[int]
    score: Optional[int]
    startedAt: Annotated[Optional[str], BeforeValidator(DateModel.to_string)]
    completedAt: Annotated[Optional[str], BeforeValidator(DateModel.to_string)]
    status: Optional[str]
    watchStatus: Optional[str]


class UserModel(BaseModel):
    id: int
    name: str
    avatar: str
    bannerImage: str
    siteUrl: str
    statistics: Any
