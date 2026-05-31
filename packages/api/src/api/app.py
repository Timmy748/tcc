from fastapi import FastAPI

from api.routes import auth, user

app = FastAPI(
    title='TCC API',
)

app.include_router(user.router)
app.include_router(auth.router)
