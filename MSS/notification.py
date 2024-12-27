import os
import datetime
import logging
from gtts import gTTS
import subprocess
import cv2

# Configuración del sistema de logs
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_folder, "notifications.log"),
    level=logging.DEBUG,  # Cambiado a DEBUG para más detalles
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuración de Linphone
LINPHONE_CONFIG = {
    "sip_address": "sip:name@sip.linphone.org",
    "password": "password",
    "call_to": "sip:number@sip.linphone.org",
    "audio_file": "voice_message.wav",
}

def send_alert(image, message):
    try:
        logging.info("Generando alerta.")
        print("Generando alerta.")
        generate_voice_message(message)
        initiate_sip_call()
        logging.info("Alerta enviada correctamente.")
        print("Alerta enviada correctamente.")
    except Exception as e:
        logging.error(f"Error al enviar alerta: {str(e)}")
        print(f"Error al enviar alerta: {str(e)}")

def generate_voice_message(message):
    tts = gTTS(text=message, lang='es')
    tts.save(LINPHONE_CONFIG["audio_file"])
    logging.info("Mensaje de voz generado y guardado.")
    print("Mensaje de voz generado y guardado.")

def initiate_sip_call():
    try:
        command = [
            "linphonecsh",
            "init",
        ]
        subprocess.run(command, check=True)

        login_command = [
            "linphonecsh",
            "generic", f"register --username {LINPHONE_CONFIG['sip_address']} --password {LINPHONE_CONFIG['password']}"
        ]
        subprocess.run(login_command, check=True)

        call_command = [
            "linphonecsh",
            "generic", f"call {LINPHONE_CONFIG['call_to']}"
        ]
        subprocess.run(call_command, check=True)

        play_audio_command = [
            "linphonecsh",
            "generic", f"play {LINPHONE_CONFIG['audio_file']}"
        ]
        subprocess.run(play_audio_command, check=True)

        hangup_command = [
            "linphonecsh",
            "generic", "terminate"
        ]
        subprocess.run(hangup_command, check=True)

        logging.info("Llamada realizada exitosamente.")
        print("Llamada realizada exitosamente.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error en la llamada SIP: {str(e)}")
        print(f"Error en la llamada SIP: {str(e)}")