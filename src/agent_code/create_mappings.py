from ..download.database_operations import DatabaseConnection
from typing import Optional, Any, List

DB:Optional[Any] = DatabaseConnection().get_connection()
if not DB:
    raise Exception("No DB found")

def convert_SQL_answer_to_list(input: List[tuple[str]]) -> List[str]:
    return list(map(lambda x: x[0], input))

GDP_levels =(DB.execute('SELECT * FROM datasets where dataType = \'REAL_GDP\' AND level =\'SuperSector\';').fetchall())
for item in GDP_levels:
    print(item)