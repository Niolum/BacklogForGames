"""This file contain routes and also the app object.
App object is responsible to instantiate the FastAPI properly.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def main_route():
    """Start Route"""
    return {"message": "Start API"}
