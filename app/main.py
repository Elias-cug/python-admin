from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.database import engine

from app.core.exceptions import register_exception
from scalar_fastapi import get_scalar_api_reference


logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Fail fast if DB is misconfigured/unreachable; print a success line when connected.
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        logger.info("Database connection OK")
    except Exception:
        logger.exception("Database connection failed")
        raise

    yield


app = FastAPI(title="python-admin", version="0.1.0", lifespan=lifespan)

register_exception(app)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")




def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Convenience runner for quick local startup."""
    import uvicorn

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run(reload=True)
