from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import datasets as datasets_router
from app.api.routers import bookmarks as bookmarks_router

app = FastAPI(title="Data Explorer API", version="0.1.0")
app.include_router(datasets_router.router)
app.include_router(bookmarks_router.router)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
