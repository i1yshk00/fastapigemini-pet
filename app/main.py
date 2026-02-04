from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.gemini import router as gemini_router
from app.api.admin import router as admin_router
from app.core.config import loguru_config_obj

# run logger before app
loguru_config_obj.setup_logging()

app = FastAPI()

app.include_router(auth_router)
app.include_router(gemini_router)
app.include_router(admin_router)


if __name__ == '__main__':
    pass
