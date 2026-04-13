from fastapi import FastAPI
from api.auth import router as auth_router
from api.routes.data import router as data_router
from api.routes.upload import router as upload_router
from api.routes.theme import router as theme_router

def create_app():
    app = FastAPI(title="SmartMerge AI")

    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(data_router, prefix="/api/v1/data", tags=["Data"])
    app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
    app.include_router(theme_router, prefix="/api/v1/theme", tags=["Theme"])

    return app
    
    
@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )