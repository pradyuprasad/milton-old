from pydantic import BaseModel
from typing import Optional, Any, List, Dict, Type 
from datetime import date
from enum import Enum

class Aggregation(BaseModel):
    '''
    Structure of the aggregation from aggregations_list.json
    '''
    OfficialName: str
    SeriesId: str
    InternalName: str

class UnTransformed(BaseModel):
    Data: Dict[str, Any]
    DataCount: int
    StatusCode: int
    Message: str


class TotalDownload(BaseModel):
    '''
    Structure of the data we download from SingStat
    '''
    class DataDetail(BaseModel):  # Subclass to describe the structure of Data
        class DataDetailRow(BaseModel):
            class KVPair(BaseModel):
                key: str
                value: str
            seriesNo: str
            rowText: str
            uoM: str
            footnote: str
            columns: List[KVPair]
        id: str
        title: str
        footnote: str
        frequency: str
        datasource: str
        generatedBy: str
        dataLastUpdated: str
        dateGenerated: str
        offset: str
        limit: str
        sortBy: Optional[Any]  
        timeFilter: Optional[Any]  
        between: Optional[Any]  
        search: Optional[Any]  
        row: List[DataDetailRow]  # Assuming rows can contain any type of data



    Data: DataDetail  # Use the DataDetail class for the nested structure
    DataCount: int
    StatusCode: int
    Message: str

KVPairList = List[TotalDownload.DataDetail.DataDetailRow.KVPair]
KVPair = TotalDownload.DataDetail.DataDetailRow.KVPair

class DateValuePair(BaseModel):
    date: date
    value: float

DateValuePairList = List[DateValuePair]

class Frequency(str, Enum):
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'

    @classmethod
    def _missing_(cls: Type['Frequency'], value: Any) -> 'Frequency':
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"Invalid frequency value: {value}")


class DataType(str, Enum):
    Real_GDP = 'REAL_GDP'
    Nominal_GDP = 'Nominal_GDP'
    Unemployment = 'Unemployment'
    Consumer_Price_Index = 'Consumer_Price_Index'

class RawMetaData(BaseModel):
    Data: Dict[str, Any]
    DataCount: int
    StatusCode: int
    Message: str

class Level(str, Enum):
    TotalEconomy = 'TotalEconomy'
    SuperSector = 'SuperSector'
    Sector = 'Sector'
    SubSector = 'SubSector'


class ProcessedMetaData(BaseModel):
    class MetaDataDetails(BaseModel):
        class MetaDataRecords(BaseModel):
            class ElementMetaData(BaseModel):
                seriesNo: str
                rowText: str
                uoM: str
                footnote: str
                
            id: str
            title: str
            frequency: Frequency
            dataSource: str
            footnote: str
            dataLastUpdated: str
            startPeriod: str
            endPeriod: str
            total: int
            row: List[ElementMetaData]

        generatedBy: str
        dateGenerated: str
        records: MetaDataRecords 
        
    Data: MetaDataDetails
    DataCount: int
    StatusCode: int
    Message: str
    

class DatabaseRow(BaseModel):
    AggregationId: str
    AggregationOfficialName: str
    frequency: Frequency
    footnote: str
    unitOfMeasure: str
    startDate: date
    endDate: date
    ElementName: str
    filePath: str # file paths don't have ../data
    dataType: DataType
    level: Level
    parent: Optional[str] # must be a csv file path
    seasonally_adjusted: int


    class Config:
        use_enum_values = True