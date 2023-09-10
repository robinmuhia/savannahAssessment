from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from ..config import settings


router = APIRouter(tags=['Authentication'])

frontend = settings.frontend_url


@router.get('/api')
async def root():
    return HTMLResponse('<body><a href="api/auth/login">Log In with your Google Account</a></body>')


@router.get('/token')
async def homepage(request: Request):
    return HTMLResponse('''
       <script>    
        function send(){
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === 4) {
                console.log(req.response);
                if (req.status === 200 && req.response["result"] === true) {
                    window.localStorage.setItem('jwt', req.response["access_token"]);
                    showAlert(req.response["success_message"])
                } else {
                    showAlert('Error: This is an Oauth authlib cache issue. Use another browser or clear cache');
                }
            }
        }
        req.withCredentials = true;
        req.responseType = 'json';
        req.open("get", "api/auth/token?" + window.location.search.substr(1), true);
        req.send("");
        }
        send();
    function fetchItems() {
        var itemList = document.getElementById("item-list").getElementsByTagName("ul")[0];
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === 4) {
                console.log(req.response);
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
        req.setRequestHeader("Authorization", "Bearer " + window.localStorage.getItem("jwt"));
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
                console.log(req.response);
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
        req.open("POST", "api/auth/phone", true);
        req.setRequestHeader("Content-Type", "application/json");
        req.setRequestHeader("Authorization", "Bearer " + window.localStorage.getItem("jwt"));
        req.send(JSON.stringify({ phone_number: phoneNumber }));
    }

    function sendItemInfo() {
        var itemName = document.getElementById("item_name").value;
        var itemAmount = document.getElementById("item_amount").value;
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === 4) {
                console.log(req.response);
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
        req.setRequestHeader("Authorization", "Bearer " + window.localStorage.getItem("jwt"));
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
    ''')
