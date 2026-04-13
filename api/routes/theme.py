from fastapi import APIRouter, Body

router = APIRouter()

users_db = {}


@router.post("/set-theme")
def set_theme(username: str = Body(...), theme: str = Body(...)):
    if username in users_db:
        users_db[username]["theme"] = theme
        return {"msg": "Theme saved"}
    return {"msg": "User not found"}


@router.get("/get-theme")
def get_theme(username: str):
    return {"theme": users_db.get(username, {}).get("theme", "dark")}