from fastapi import FastAPI

from api.routes import user

app = FastAPI(
    title='TCC API',
)

app.include_router(user.router)
