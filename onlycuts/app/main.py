from fastapi import FastAPI

from onlycuts.app.api.admin import router as admin_router
from onlycuts.app.api.health import router as health_router
from onlycuts.app.api.telegram_callbacks import router as telegram_router

app = FastAPI(title="onlycuts")
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(telegram_router)
