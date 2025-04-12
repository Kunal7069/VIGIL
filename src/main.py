from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from scraper.rapid_api.rapid_api_main import router as rapid_api
from read_data.rapid_api import router as read_rapid_api
from scraper.apify.apify_main import router as apify_api
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Server Instance is ready to use"}

# Include routers
app.include_router(rapid_api, prefix="/rapid", tags=["Activity"])
app.include_router(read_rapid_api, prefix="/read-rapid", tags=["Scraper"])

# Not in use
app.include_router(apify_api, prefix="/apify", tags=["Scraper"])

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
