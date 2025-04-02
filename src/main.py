from fastapi import FastAPI
import uvicorn
from scraper.rapid_api.rapid_api_main import router as rapid_api
from read_data.rapid_api import router as read_rapid_api

app = FastAPI()

# Include routers
app.include_router(rapid_api, prefix="/rapid", tags=["Activity"])
app.include_router(read_rapid_api, prefix="/read-rapid", tags=["Scraper"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)