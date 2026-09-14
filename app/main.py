from fastapi import FastAPI
from app.core.db import engine, Base
from app.api.v1.posts.router import router as post_router

def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(post_router)

    @app.get("/")
    def home():
        return {"message": "Hello api funcionando correctamente"}

    return app

app = create_app()

