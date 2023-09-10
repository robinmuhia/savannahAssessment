from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from . import config
from .routers import order, auth


app = FastAPI()

# to be used in middleware
origins = ['*']
SECRET_KEY = config.settings.session_secret_key

# middleware

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# routes
app.include_router(order.router)
app.include_router(auth.router)
