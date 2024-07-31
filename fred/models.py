# models.py
from pydantic import BaseModel
from typing import Optional, List, Any, Union, Literal
from datetime import datetime, date
from enum import Enum

class Series(BaseModel):
    fred_id: str
    title: str
    observation_start: str
    observation_end: str
    frequency: str
    frequency_short: str
    units: str
    units_short: str
    seasonal_adjustment: str
    seasonal_adjustment_short: str
    last_updated: str
    popularity: int
    notes: Optional[str]

class DateValuePair(BaseModel):
    date: date
    value: float

class SeriesData(BaseModel):
    units: str
    ObservationsData: List[DateValuePair]

class SeriesForSearch(BaseModel):
    fred_id:str
    title:str
    units:str
    popularity: int
    relevance_lower_better: Optional[float]

    class Config:
        frozen = True

class SeriesForRanking(BaseModel):
    fred_id:str
    title:str
    units:str

class Keywords(BaseModel):
    word: List[str]

class ClassifiedSeries(BaseModel):
    relevant: List[SeriesForSearch]
    notRelevant: List[SeriesForSearch]

class Search(BaseModel):
    query: str

class SearchList(BaseModel):
    queries: List[Search]
