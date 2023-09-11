from fastapi import APIRouter, Depends, HTTPException, status
from starlette.config import Config
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from .. import config, models, schemas
from ..database import get_db


router = APIRouter(tags=['Authentication'])

# OAuth settings
GOOGLE_CLIENT_ID = config.settings.google_client_id
GOOGLE_CLIENT_SECRET = config.settings.google_client_secret

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


@router.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        html = ('''
       <script>    
    function fetchItems() {
        var itemList = document.getElementById("item-list").getElementsByTagName("ul")[0];
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === 4) {
                if (req.status === 200) {
                    displayItems(itemList, req.response["items"]);
                } else {
                    showAlert('Error fetching items: ' + req.response.detail);
                }
            }
        };
        req.withCredentials = true;
        req.responseType = 'json';
        req.open("GET", "api/items", true);
        req.send();
    }
    function displayItems(itemList, items) {
            itemList.innerHTML = '';
            items.forEach(function(item) {
                var li = document.createElement("li");
                li.textContent = 'Item Name: ' + item.item + ', Amount: ' + item.amount;
                itemList.appendChild(li);
            });
        }
    function sendPhoneNumber() {
        var phoneNumber = document.getElementById("phone_number").value;
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === 4) {
                if (req.status === 200 && req.response["result"] === true) {
                    showAlert(req.response["success_message"])
                    clearInputFields();
                } else {
                    showAlert('Error: ' + req.response.detail);
                }
            }
        };
        req.withCredentials = true;
        req.responseType = 'json';
        req.open("POST", "/phone", true);
        req.setRequestHeader("Content-Type", "application/json");
        req.send(JSON.stringify({ phone_number: phoneNumber }));
    }

    function sendItemInfo() {
        var itemName = document.getElementById("item_name").value;
        var itemAmount = document.getElementById("item_amount").value;
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === 4) {
                if (req.status === 200) {
                    // Handle the response as needed
                    clearInputFields();
                    showAlert(req.response["success_message"])
                    fetchItems()
                } else {
                    showAlert('Error: ' + req.response.detail);
                }
            }
        };
        req.withCredentials = true;
        req.responseType = 'json';
        req.open("POST", "api/items", true);
        req.setRequestHeader("Content-Type", "application/json");
        req.send(JSON.stringify({ name: itemName, amount: itemAmount }));
    }

    function showAlert(message) {
        alert(message);
    }

    function clearInputFields() {
        document.getElementById("phone_number").value = "";
        document.getElementById("item_name").value = "";
        document.getElementById("item_amount").value = "";
    }
    </script>

    <form>
        <label for="phone_number">Phone Number:</label>
        <input type="text" id="phone_number" name="phone_number">
        <button type="button" onclick="sendPhoneNumber()">Submit Phone Number</button>
    </form>

    <form>
        <label for="item_name">Item Name:</label>
        <input type="text" id="item_name" name="item_name">
        <label for="item_amount">Amount:</label>
        <input type="number" id="item_amount" name="item_amount">
        <button type="button" onclick="sendItemInfo()">Submit Item Info</button>
    </form>
    <button type="button" onclick="fetchItems()"> View your orders</button>
    <div id="item-list">
        <h2>Items:</h2>
        <ul></ul>
    </div>
    <div>
    <a href="/logout">logout</a>
    </div>
    ''')
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">Press this link to log in with your google account</a>')


@router.get('/login')
async def login(request: Request):
    redirect_uri = f'{config.settings.frontend_url}/auth'
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        user_email = user["email"]
        user_name = user["name"]
        user_exists = db.query(models.Customer).filter(
            models.Customer.email == user_email).first()
        if user_exists:
            return RedirectResponse(url='/')

        new_user_data = schemas.UserCreate(
            email=user_email, name=user_name)
        # Create a new user using the UserCreate schema data
        new_user_dict = new_user_data.model_dump()  # Use model_dump instead of dict
        new_user = models.Customer(**new_user_dict)
        db.add(new_user)
        db.commit()  # Commit the changes to the database
        db.refresh(new_user)
        return RedirectResponse(url='/')

    return RedirectResponse(url='/')


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@router.post("/phone")
async def add_number(request: Request, db: Session = Depends(get_db)):
    request_body: dict = await request.json()
    phone_number = request_body.get('phone_number')
    # check if phone number is integer
    if phone_number is not None:
        try:
            phone_number = int(phone_number)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Phone number must be an integer")

    # check if phone number is accurate
    if len(str(phone_number)) != 9 or str(phone_number)[0] != "7":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f'Phone number must be 10 characters in length starting with 07')

    # search for customer with phone number and reject if user exists
    user_query = db.query(models.Customer).filter(
        models.Customer.phone_number == phone_number)
    user = user_query.first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'0{phone_number} already in use')
    # check if user is authenticated
    request_user = request.session.get('user')
    user_email = request_user["email"]
    user_updated = db.query(models.Customer).filter(
        models.Customer.email == user_email).first()
    if user_updated == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User does not exist")

    user_updated.phone_number = phone_number
    db.commit()
    return JSONResponse({
        "result": True,
        "success_message": "User successfully updated"
    })
