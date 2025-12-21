from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str

@router.post("/page")
def scrape_page(request: ScrapeRequest):
    return {
        "url": request.url,
        "captcha_detected": True,
        "scraping_status": "success",
        "data_extracted": {
            "title": "Mock Page Title",
            "items": 12
        }
    }

