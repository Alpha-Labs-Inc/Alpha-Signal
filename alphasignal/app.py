from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from alphasignal.routers.wallet_router import router as wallet_router
from alphasignal.routers.coin_router import router as coin_router
from alphasignal.services.service import initialize_database

load_dotenv()
initialize_database()

app = FastAPI(docs_url="/api/docs")

# Include the test router
app.include_router(wallet_router)
app.include_router(coin_router)


if __name__ == "__main__":
    # Use Uvicorn to run the application
    initialize_database()
    uvicorn.run("alphasignal.app:app", host="127.0.0.1", port=8000, reload=True)
