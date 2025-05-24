import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from alphasignal.routers.wallet_router import router as wallet_router
from alphasignal.routers.orders_router import router as order_router
from alphasignal.routers.config_router import router as config_router
from alphasignal.routers.profile_router import router as profile_router
from alphasignal.routers.webhook_router import router as webhook_router

from alphasignal.services.service import initialize_database
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = ["http://localhost", "http://localhost:8000", "http://localhost:6969"]

load_dotenv()

app = FastAPI(docs_url="/api/docs")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(
        f"Unexpected error at {request.method} {request.url}: {exc}",
        exc_info=True,  # Logs full traceback
    )

    print(f"Unexpected error at {request.method} {request.url}: {exc}")

    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# Include the test router
app.include_router(wallet_router, tags=["Wallet Management"])
app.include_router(order_router, tags=["Orders"])
app.include_router(config_router, tags=["Configurations"])
app.include_router(profile_router, tags=["Profiles"])
app.include_router(webhook_router, tags=["Webhooks"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Use Uvicorn to run the application
    initialize_database()
    uvicorn.run("alphasignal.app:app", host="0.0.0.0", port=8000, reload=True)
