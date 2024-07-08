from pydantic import BaseModel, FieldValidationInfo, field_validator
from datetime import date, datetime

class DateValue(BaseModel):
    date: date

    @field_validator('date', mode='before')
    def validate_date(cls, value: str, info: FieldValidationInfo):
        if isinstance(value, str):
            # Attempt to parse the string to a date
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format")
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        else:
            raise ValueError("Invalid date format")

# Example usage
try:
    dv = DateValue(date="2024-06-29")
    print(dv)
except ValueError as e:
    print(e)

