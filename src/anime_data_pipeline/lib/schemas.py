from pydantic import BaseModel, BeforeValidator
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


class Image(BaseModel):
    large: Optional[str]
    extraLarge: Optional[str]

    def to_string(value: Optional[Any]) -> Optional[str]:
        if value:
            if "extraLarge" in value:
                return value["extraLarge"]
            if "large" in value:
                return value["large"]
        return None


class Date(BaseModel):
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]

    def to_string(value: Optional[Any]) -> Optional[datetime]:
        if not value or not value["year"] or not value["month"] or not value["day"]:
            return None
        return datetime(value["year"], value["month"], value["day"]).strftime(
            "%Y-%m-%d"
        )


class FactAnime(BaseModel):
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
    startedAt: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    completedAt: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    stats: Optional[Any]
    rankings: Optional[Any]


class DimensionMedia(BaseModel):
    id: int
    genres: List[str]
    description: Optional[str]
    coverImage: Annotated[Optional[str], BeforeValidator(Image.to_string)]
    type: Optional[str]
    tags: List[Tag]
    episodes: Optional[int]
    format: Optional[str]
    season: Optional[str]
    seasonYear: Optional[int]
    startDate: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    endDate: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    synonyms: List[str]
    title: Title
    source: Optional[str]
    bannerImage: Optional[str]
    siteUrl: Optional[str]
    status: Optional[str]


class DimensionUser(BaseModel):
    id: int
    name: str
    avatar: Annotated[Optional[str], BeforeValidator(Image.to_string)]
    bannerImage: str
    siteUrl: str
    statistics: Any


class Anime(BaseModel):
    id: int
    userId: int
    genres: List[str]
    description: Optional[str]
    coverImage: Annotated[Optional[str], BeforeValidator(Image.to_string)]
    type: Optional[str]
    tags: List[Tag]
    episodes: Optional[int]
    format: Optional[str]
    season: Optional[str]
    seasonYear: Optional[int]
    startDate: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    endDate: Annotated[Optional[str], BeforeValidator(Date.to_string)]
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
    startedAt: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    completedAt: Annotated[Optional[str], BeforeValidator(Date.to_string)]
    status: Optional[str]
    watchStatus: Optional[str]


class User(BaseModel):
    id: int
    name: str
    avatar: Annotated[Optional[str], BeforeValidator(Image.to_string)]
    bannerImage: str
    siteUrl: str
