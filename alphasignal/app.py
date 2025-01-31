from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from alphasignal.routers.wallet_router import router as wallet_router
from alphasignal.routers.order_router import router as order_router
from alphasignal.services.service import initialize_database
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
]

load_dotenv()
initialize_database()

app = FastAPI(docs_url="/api/docs")

# Include the test router
app.include_router(wallet_router)
app.include_router(order_router)

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
    uvicorn.run("alphasignal.app:app", host="127.0.0.1", port=8000, reload=True)
