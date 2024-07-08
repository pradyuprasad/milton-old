from .classes import ProcessedMetaData, Frequency, DataType, Level, DatabaseRow
from typing import Dict, List, Optional
from datetime import date
from .utils import fix_dates, findType, getLevel, make_indexNo_to_element, find_parent_csv


def make_metadata(elements_to_csv:Dict[str, str], metadata:ProcessedMetaData, agg_internal_name:str) -> List[DatabaseRow]:
    AggregationId: str = metadata.Data.records.id
    AggregationOfficialName: str = metadata.Data.records.title
    frequency:Frequency = metadata.Data.records.frequency
    startDate: date = fix_dates(metadata.Data.records.startPeriod, frequency)
    endDate: date = fix_dates(metadata.Data.records.endPeriod, frequency)
    default_footnote: str = metadata.Data.records.footnote
    dataType: DataType = findType(agg_internal_name)
    indexNo_to_elements: Dict[str, str] = make_indexNo_to_element(metadata=metadata)
    seasonally_adjusted: int = int("adjusted" in agg_internal_name or "Adjusted" in agg_internal_name)

    



    def metadata_for_element(element: ProcessedMetaData.MetaDataDetails.MetaDataRecords.ElementMetaData) -> DatabaseRow:
        final_footnote: str = default_footnote
        if element.footnote != "":
            final_footnote += "  " + element.footnote
        
        
        unitOfMeasure: str = element.uoM
        ElementName: str = element.rowText
        filePath: str = elements_to_csv[ElementName]
        level: Level = getLevel(element.seriesNo)
        parent: Optional[str] = find_parent_csv(element=element, indexNo_to_elements=indexNo_to_elements, elements_to_csv=elements_to_csv)

        return DatabaseRow(AggregationId=AggregationId, AggregationOfficialName=AggregationOfficialName, frequency=frequency, footnote=final_footnote, unitOfMeasure=unitOfMeasure, startDate=startDate, endDate=endDate, ElementName=element.rowText, filePath=filePath, dataType=dataType, level=level, parent=parent, seasonally_adjusted=seasonally_adjusted)
    
    return list(map(metadata_for_element, metadata.Data.records.row))