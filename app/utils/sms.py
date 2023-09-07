import africastalking
from ..config import settings

username = settings.africatalking_sms_username
api_key = settings.africatalking_sms_api_key

africastalking.initialize(
    username=username,
    api_key=api_key
)

sms = africastalking.SMS


def sending(phone_number, message):
    recipients = [f'+254{phone_number}']
    sender = "Robin Muhia"
    try:
        response = sms.send(message, recipients, sender)
        print(response)
    except Exception as e:
        print(f'Error sending messsage: {e}')
