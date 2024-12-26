from twilio.rest import Client
import cv2
import os
import datetime
import requests

TWILIO_CONFIG = {
    "account_sid": "YOUR_ACCOUNT_SID",
    "auth_token": "YOUR_AUTH_TOKEN",
    "from_phone": "YOUR_TWILIO_PHONE",
    "to_phone": "YOUR_PHONE_NUMBER",
}

TELEGRAM_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
}

def send_alert(image, message):
    # Enviar notificación por Twilio
    send_twilio_alert(image, message)

    # Enviar notificación por Telegram
    send_telegram_alert(image, message)

def send_twilio_alert(image, message):
    client = Client(TWILIO_CONFIG["account_sid"], TWILIO_CONFIG["auth_token"])
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = f"temp_{timestamp}.jpg"
    cv2.imwrite(image_path, image)

    client.messages.create(
        body=f"{message} - Hora: {timestamp}",
        from_=TWILIO_CONFIG["from_phone"],
        to=TWILIO_CONFIG["to_phone"],
        media_url=f"file://{os.path.abspath(image_path)}"
    )

    os.remove(image_path)

def send_telegram_alert(image, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = f"temp_{timestamp}.jpg"
    cv2.imwrite(image_path, image)

    with open(image_path, "rb") as img:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendPhoto",
            data={"chat_id": TELEGRAM_CONFIG["chat_id"], "caption": message},
            files={"photo": img}
        )

    os.remove(image_path)
