from fastapi import APIRouter
from api.app.services.ocr_service import solve_captcha_from_url, get_model_info

router = APIRouter(prefix="/captcha", tags=["captcha"])

@router.get("/model-info")
def model_info():
    return get_model_info()

@router.post("/solve-from-url")
async def solve_from_url(url: str):
    return solve_captcha_from_url(url)
