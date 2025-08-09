from fastapi import FastAPI

from .lifespan import lifespan


app = FastAPI(
    version='1.0.0',
    root_path='/api/v1',
    lifespan=lifespan,
)
