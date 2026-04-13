from fastapi import APIRouter, Body
from services.ai_merge_service import match_columns

router = APIRouter()

@router.post("/match")
def match(data: dict = Body(...)):
    cols1 = data.get("cols1", [])
    cols2 = data.get("cols2", [])

    return match_columns(cols1, cols2)