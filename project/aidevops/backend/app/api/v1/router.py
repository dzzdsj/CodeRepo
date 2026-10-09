from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}
