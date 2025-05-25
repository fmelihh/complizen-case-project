from fastapi import FastAPI

from .routers import *


app = FastAPI()
app.include_router(graph_router, tags=["Graph"])
