from fastapi import APIRouter, Depends
from api.auth import get_current_user
from services.data_service import get_data, aggregate_data

router = APIRouter()


@router.get("/")
async def fetch_data(limit: int = 100, offset: int = 0, user=Depends(get_current_user)):
    return get_data(limit, offset)


@router.get("/aggregate")
async def aggregate(x: str, y: str, agg: str, user=Depends(get_current_user)):
    return aggregate_data(x, y, agg)
    
    
@router.post("/process")
def process(user=Depends(get_current_user)):
    start_background_job()
    return {"msg": "Processing started"}