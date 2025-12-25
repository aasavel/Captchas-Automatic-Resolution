from fastapi import FastAPI
from api.app.api.routes import captcha, scrape, training

app = FastAPI()

app.include_router(captcha.router, prefix="/captcha", tags=["CAPTCHA"])
