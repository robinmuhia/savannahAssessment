from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from . import models, config
from .database import engine
from .routers import frontend, auth, item


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# to be used in middleware
origins = ['*']
SECRET_KEY = config.settings.session_secret_key

# middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# routes
app.include_router(frontend.router)
app.include_router(auth.router)
app.include_router(item.router)


print('Successful connection')
