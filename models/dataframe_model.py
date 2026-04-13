from pydantic import BaseModel

class DataSchema(BaseModel):
    column_name: str
    dtype: str