from fastapi import APIRouter, UploadFile, File
import pandas as pd

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    return {
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records")
    }