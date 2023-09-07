from fastapi import APIRouter, Request, Depends, HTTPException, status
from starlette.responses import JSONResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from .. import models, oauth2
from ..schemas import UserCreate

router = APIRouter(
    prefix="/api/auth",
    tags=['auth']
)

# OAuth settings
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
               'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


# Frontend URL
FRONTEND_URL = f'{settings.frontend_url}/token'


@router.get('/login')
async def login(request: Request):
    redirect_uri = FRONTEND_URL
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/token')
async def auth(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        user_email = user["email"]
        user_name = user["name"]
        user_exists = db.query(models.Customer).filter(
            models.Customer.email == user_email).first()
        if user_exists:
            return JSONResponse({
                'result': True,
                'access_token': oauth2.create_access_token(data={"user_id": user_exists.id}),
            }, status_code=200)
        new_user_data = UserCreate(
            email=user_email, name=user_name)
        # Create a new user using the UserCreate schema data
        new_user = models.Customer(**new_user_data.dict())
        db.add(new_user)
        db.commit()  # Commit the changes to the database
        db.refresh(new_user)
        return JSONResponse({
            'result': True,
            'access_token': oauth2.create_access_token(data={"user_id": new_user.id}),
        }, status_code=201)


@router.post('/phone', status_code=status.HTTP_200_OK)
async def add_number(request: Request, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.Customer).filter(
        models.Customer.id == current_user.id)
    user = user_query.first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No post with id {id} exists')
    request_body: dict = await request.json()
    phone_number = request_body.get('phone_number')
    if phone_number is not None:
        try:
            phone_number = int(phone_number)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="phone_number must be an integer")

    if len(str(phone_number)) != 9 or str(phone_number)[:1] != "7":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f'Phone number must be 10 characters in length starting with 07')

    user.phone_number = phone_number
    db.commit()
    return user_query.first()
