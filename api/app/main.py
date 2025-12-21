from fastapi import FastAPI
from app.api.routes import captcha, scrape, training

app = FastAPI(
    title="CAPTCHA Automatic Resolution API (Mock)",
    description="Maquette fonctionnelle – Projet M2 MoSEF",
    version="1.0.0"
)

app.include_router(captcha.router, prefix="/captcha", tags=["CAPTCHA"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])
app.include_router(training.router, prefix="/training", tags=["Training"])

@app.get("/health")
def health():
    return {"status": "ok"}

