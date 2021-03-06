import RPi.GPIO as GPIO
import time
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import messaging
import firebase_admin

cred = credentials.Certificate(
    "/home/pi/dev/python/temp_server/check-my-temp-5e3d6-firebase-adminsdk-m5rzd-e70cd0a740.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)  # Read output from PIR motion sensor


def get_token():
    doc_ref = db.collection(u'tokens').document(u'token')
    doc = doc_ref.get()
    tokens = doc.to_dict()
    token_value = tokens['token']
    print(token_value)
    return token_value


def send_to_token():
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title="MY ROOM",
            body="Motion detected in your room"
        ),
        tokens=get_token(),
        android=messaging.AndroidConfig(
            priority="high"
        ),
    )
    try:
        response = messaging.send_multicast(message)
    except Exception as error:
        print(f'Something went wrong: {error}')
        return False
    else:
        print('Successfully sent message:', response)
        return True


while True:
    i = GPIO.input(8)
    if i == 1:  # When output from motion sensor is HIGH
        print("movement detected")
        f = send_to_token()
        while(f == False):
            f = send_to_token()
            time.sleep(2)
        time.sleep(120)
