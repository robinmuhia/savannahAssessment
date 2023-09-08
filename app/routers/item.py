from fastapi import APIRouter, Request, Depends, HTTPException, status
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, oauth2
from ..schemas import OrderCreate, OrdersOut
from ..utils import sms

router = APIRouter(
    prefix="/api/items",
    tags=['items']
)

# create item


@router.post('/')
async def login(request: Request, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    request_body: dict = await request.json()
    item = request_body.get('name')
    amount = request_body.get('amount')
    # check for null values

    if len(str(amount)) == 0 or len(item) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Make sure the item and amount field are filled in")

    # check amount is int and greater than 0
    try:
        amount = int(amount)
        if amount < 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Amount must be greater than 0")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Amount must be an integer")

    user = db.query(models.Customer).filter(
        models.Customer.id == current_user.id).first()
    # check is user exists
    if user == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User does not exist")

    # check if user has a phone_number to be able to send sms
    if user.phone_number == None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Add phone number before placing order")

    new_order_data = OrderCreate(item=item, amount=amount, owner_id=user.id)
    new_order = models.Order(**new_order_data.dict())
    db.add(new_order)
    db.commit()  # Commit the changes to the database
    db.refresh(new_order)
    return JSONResponse({
        'result': True,
        'success_message': "Order successfully added"
    }, status_code=200)


@router.get('/', status_code=status.HTTP_200_OK, response_model=OrdersOut)
async def add_number(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # check if user is authenticated
    user = db.query(models.Customer).filter(
        models.Customer.id == current_user.id).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User does not exist")
    items = db.query(models.Order).filter(
        models.Order.owner_id == current_user.id).all()
    return {
        "result": True,
        "items": items,
        "success_message": "User successfully updated"
    }
