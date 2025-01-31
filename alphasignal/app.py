from fastapi import FastAPI
import uvicorn
from alphasignal.routers.test_router import router as test_router
from alphasignal.routers.wallet_router import router as wallet_router
from alphasignal.routers.coin_router import router as coin_router

app = FastAPI(docs_url="/api/docs")

# Include the test router
# app.include_router(test_router)
app.include_router(wallet_router)
app.include_router(coin_router)


if __name__ == "__main__":
    # Use Uvicorn to run the application
    uvicorn.run("alphasignal.app:app", host="127.0.0.1", port=8000, reload=True)
