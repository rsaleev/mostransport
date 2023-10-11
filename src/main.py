from fastapi import FastAPI
from .routes.find import router as find_router
from .routes.problems import router as problems_router

app = FastAPI()


app.include_router(problems_router)
app.include_router(find_router)

