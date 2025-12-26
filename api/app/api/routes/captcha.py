from fastapi import APIRouter, Query
from api.app.services.ocr_service import solve_captcha_from_url

router = APIRouter(prefix="/captcha", tags=["captcha"])

@router.post("/solve-from-url")
def solve_from_url(url: str = Query(...)):
    return solve_captcha_from_url(url)
