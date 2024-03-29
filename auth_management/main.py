import json
import os

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from auth_management.config.config import initiate_database, initiate_redis_pool
from auth_management.controllers.router import api_router
from auth_management.utils.logger import get_logger

# API Doc
if os.getenv("ENVIRONMENT") == "local":
    auth_app = FastAPI(
        title="AuthApp",
        description="Authentication Application",
        version="1.0.0",
        openapi_url="/api/v1/auth/openapi.json",
        docs_url="/api/v1/auth/docs",
        # root_path="/api/v1"
    )
else:
    auth_app = FastAPI(
        title="AuthApp",
        description="Authentication Application",
        version="1.0.0",
        openapi_url="/api/v1/auth/openapi.json",
        docs_url="/api/v1/auth/docs",
        debug=True
        # root_path="/api/v1"
    )
auth_app.add_middleware(GZipMiddleware)
auth_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

auth_app.include_router(api_router, prefix='/api/v1/auth')


@auth_app.on_event("startup")
async def start_database() -> None:
    logger = get_logger()
    with open('openapi/auth_management/openapi.json', 'w') as f:
        json.dump(get_openapi(
            title=auth_app.title,
            version=auth_app.version,
            openapi_version=auth_app.openapi_version,
            description=auth_app.description,
            routes=auth_app.routes,
        ), f)
    logger.info("Initiating database........")
    await initiate_database()
    logger.info("Initiating database completed........")
    logger.info("OpenAPI specification created.........")
    logger.info("Connecting to redis.........")
    auth_app.state.redis_connection = await initiate_redis_pool()
    logger.info("Redis Connected.........")

#
# PORT = 8000
# BIND = '127.0.0.1'
# WORKERS = 10
# RELOAD = True
# app = FastAPI(
#     title="SkillMatrix",
#     description="Skill Matrix Application",
#     version="1.0.0")
# # app.mount("/auth", auth_management)
# if __name__ == "__main__":
#     # install_packages()
#     # uvicorn.run("hello:app", host=BIND, port=int(PORT), reload=RELOAD, debug=RELOAD, workers=int(WORKERS))
#     uvicorn.run("auth_management.main:auth_management", host=BIND, port=int(PORT), reload=RELOAD, workers=int(WORKERS))
