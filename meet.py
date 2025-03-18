import os
import sys
import json
import queue
import threading
import time
import logging
import base64
import requests  # type: ignore
import asyncio
import edge_tts  # pip install edge-tts
from flask import Flask, request, jsonify
import sounddevice as sd  # type: ignore
import vosk  # type: ignore
from colorama import init, Fore, Style  # type: ignore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import undetected_chromedriver as uc #type:ignore
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from gtts import gTTS  # type: ignore
import tempfile
from pydub import AudioSegment  # type: ignore
from pyngrok import ngrok # type: ignore
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
app = Flask(__name__)
init(autoreset=True)
MODEL_PATH = "./models/vosk-model-es-0.42"
if not os.path.exists(MODEL_PATH):
    raise Exception(
        f"Descarga el modelo de https://alphacephei.com/vosk/models y colócalo en {MODEL_PATH}"
    )
model = vosk.Model(MODEL_PATH)
q: queue.Queue = queue.Queue()  # type: ignore
working = False
isFinish = False
tts_active = False
op_scrum_active = False
current_stop_flag: threading.Event | None = None
start_phrases = [
    "empecemos la daily",
    "empezamos la daily",
    "comenzamos la daily",
    "comencemos la daily",
    "podemos comenzar la daily",
    "empezemos op",
    "damos inicio a la daily",
]
stop_phrases = ["chau op scrum", "terminamos la daily", "chau op", "hasta luego"]
accumulated_transcriptions = []  # type: ignore
last_complete_transcription_time = time.time()
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Error:", status)
    global tts_active
    if tts_active:
        return
    else:
        q.put(bytes(indata))
WEBHOOK_TRANSCRIPTION_URL = "https://sagasti.app.n8n.cloud/webhook/ed6f394b-3d61-4288-b8b7-15a34292c84e"  # Actualiza esta URL
def send_to_webhook(text, meet):
    """
    Envía la transcripción completa al webhook de n8n.
    """
    payload = {"transcription": text, "meet": meet}
    headers = {"Content-Type": "application/json"}
    global tts_active
    tts_active = True
    print(Fore.YELLOW + "\nEnviando a n8n" + Style.RESET_ALL, text)
    try:
        response = requests.post(
            WEBHOOK_TRANSCRIPTION_URL, json=payload, headers=headers
        )
        if response.ok:
            logging.info("Webhook de transcripción enviado exitosamente.")
        else:
            logging.error(
                f"Error en el webhook de transcripción: {response.status_code} - {response.text}"
            )
        print(Fore.YELLOW + "\nTermine de enviar:" + Style.RESET_ALL, text)
    except Exception as e:
        logging.error(f"Excepción al enviar webhook de transcripción: {e}")
meet_data = {"email": None, "password": None, "meet_url": None, "toSend": None}
meeting_driver: webdriver.Chrome | None = None
def join_meet(meet_url, email, password):
    logging.info("Iniciando proceso de unión a la reunión...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--disable-camera")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--start-maximized")
    user_data_dir = os.path.join(os.path.expanduser("~"), "selenium-chrome-profile")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=chrome_options)
    driver.get(meet_url)
    logging.info(meet_url)
    time.sleep(5)
    driver.save_screenshot("first_chrome_screenshot.png")
    try:
        camera_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@aria-label="Desactivar cámara"]')
            )
        )
        camera_button.click()
        logging.info("📷 Cámara apagada")
    except TimeoutException:
        driver.save_screenshot("error_screenshot.png")
        logging.warning("⚠️ No se encontró el botón de cámara.")
    time.sleep(2)
    wait = WebDriverWait(driver, 2)
    input_element = wait.until(EC.presence_of_element_located((By.ID, "c11")))
    time.sleep(2)
    input_element.send_keys("Op Scrum") 
    time.sleep(2)
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Solicitar unirse') or contains(., 'Ask to join')]")))
    time.sleep(2)
    button.click()
    time.sleep(5)  
    return driver

def monitor_meeting(driver, stop_flag):
    while not stop_flag.is_set():
        try:
            driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'removed from the meeting') or contains(text(), 'Te quitaron de la reunión')]",
            )
            global op_scrum_active
            op_scrum_active = False
            logging.info("🛑 Usuario expulsado, deteniendo proceso...")
            stop_flag.set()
            break
        except NoSuchElementException:
            pass
        time.sleep(2)
    logging.info("🔴 Monitoreo de eventos finalizado.")

def monitor_meeting_participant(driver, stop_flag_participant):
    while not stop_flag_participant.is_set():
        participants = driver.find_elements(By.XPATH, "//div[@role='listitem']")
        speaking_participants = []
        for participant in participants:
            try:
                name_element = participant.find_element(By.CSS_SELECTOR, "span.zWGUib")
                name = name_element.text.strip()
            except Exception as e:
                name = "Desconocido"
            try:
                voice_indicator = participant.find_element(By.XPATH, ".//div[@jscontroller='ES310d']")
                classes = voice_indicator.get_attribute("class")
            except Exception as e:
                classes = ""
            if  not "gjg47c" in classes:
                speaking_participants.append(name)
        if speaking_participants:
            for sp in speaking_participants:
                print(f"Hablando: {sp}")
        time.sleep(0.2)
    logging.info("🔴 Monitoreo de participantes finalizado.")

def silence_timer():
    global last_complete_transcription_time, accumulated_transcriptions,tts_active,working
    while not working:
        time.sleep(0.2)
        elapsed = time.time() - last_complete_transcription_time
        if elapsed >= 1.0 and accumulated_transcriptions:
            if op_scrum_active:
                joined_text = " ".join(accumulated_transcriptions)
                if tts_active:
                    print(
                        Fore.BLUE
                        + f"\nTranscripción acumulada tras {elapsed:.2f} segundos de silencio:\n{joined_text}\n"
                        + Style.RESET_ALL,
                        "",
                    )
                else:
                    print(
                        Fore.BLUE
                        + f"\nTranscripción acumulada tras {elapsed:.2f} segundos de silencio:\n{joined_text}\n"
                        + Style.RESET_ALL,
                        "",
                    )
                    working = True
                    tts_active = True
                    send_to_webhook(joined_text, meet_data["meet_url"])

            accumulated_transcriptions = []
            last_complete_transcription_time = time.time()

def transcribe_audio(stop_flag):
    samplerate = 16000
    global last_complete_transcription_time, accumulated_transcriptions, op_scrum_active, tts_active
    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        rec = vosk.KaldiRecognizer(model, samplerate)
        print("Transcripción iniciada... Presiona Ctrl+C para detener el programa.")
        while not stop_flag.is_set():
            try:
                data = q.get(timeout=0.1)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                result = rec.Result()
                try:
                    text = json.loads(result).get("text", "")
                except Exception:
                    text = ""
                if text:
                    start_detected = any(phrase in text for phrase in start_phrases)
                    stop_detected = any(phrase in text for phrase in stop_phrases)
                    print(
                        Fore.GREEN + "\nTranscripción completa:" + Style.RESET_ALL, text
                    )
                    if start_detected:
                        global tts_active
                        tts_active = True
                        op_scrum_active = True
                        send_to_webhook("Estamos listos", meet_data["meet_url"])
                    accumulated_transcriptions.append(text)
                    last_complete_transcription_time = time.time()

            else:
                partial_result = rec.PartialResult()
                try:
                    partial_text = json.loads(partial_result).get("partial", "")
                except Exception:
                    partial_text = ""
                if partial_text:
                    last_complete_transcription_time = time.time()
                    print("\rTranscripción parcial:", partial_text, end="", flush=True)


@app.route("/join-meet", methods=["POST"])
def handle_join_meet():
    data = request.json
    meet_data["email"] = data.get("email")
    meet_data["password"] = data.get("password")
    meet_data["meet_url"] = data.get("meet_url")
    meet_data["toSend"] = data.get("toSend")
    if not all(meet_data.values()):
        logging.error("⚠️ Faltan datos: email, password, meet_url o toSend")
        return (
            jsonify({"error": "Faltan datos: email, password, meet_url o toSend"}),
            400,
        )
    threading.Thread(target=start_meeting_process).start()
    logging.info("🟢 Reunión iniciada")
    return jsonify({"message": "Reunión iniciada"}), 200

async def generate_tts_audio(text, filename):
    communicate = edge_tts.Communicate(text, "es-AR-ElenaNeural", rate="+23%")
    await communicate.save(filename)

@app.route("/inject-audio", methods=["POST"])
def handle_inject_audio():
    data = request.get_json()
    text_to_speak = data.get("text")
    if not text_to_speak:
        return jsonify({"error": "No se proporcionó 'text'"}), 400
    global meeting_driver, tts_active,working
    if meeting_driver is None:
        return jsonify({"error": "No hay una reunión activa para inyectar audio."}), 400
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            temp_filename = fp.name
        asyncio.run(generate_tts_audio(text_to_speak, temp_filename))
        audio_segment = AudioSegment.from_mp3(temp_filename)
        duration = audio_segment.duration_seconds
        tts_active = True
        with open(temp_filename, "rb") as f:
            audio_data = f.read()
        b64_audio = base64.b64encode(audio_data).decode("utf-8")
        js_script = f"""
        var audio = new Audio("data:audio/mpeg;base64,{b64_audio}");
        audio.play();
        """
        meeting_driver.execute_script(js_script)
        os.remove(temp_filename)
        logging.info("Audio inyectado exitosamente en la reunión.")
        def disable_tts():
            global tts_active,working
            working = False
            time.sleep(duration + 1.2)  # margen extra
            tts_active = False
            logging.info("Reproducción finalizada, tts_active desactivado.")
            if isFinish: 
                tts_active = not tts_active
                meeting_driver.quit()
                logging.info("meet finalizada.")
        threading.Thread(target=disable_tts, daemon=True).start()
        return jsonify({"message": "Audio inyectado exitosamente"}), 200
    except Exception as e:
        logging.error(f"Error inyectando audio: {e}")
        return jsonify({"error": str(e)}), 500
@app.route("/end-meet", methods=["POST"])
def end_meet():
    global isFinish
    isFinish = True
    return jsonify({"message": "Reunión finalizada exitosamente"}), 200
@app.route("/toggle-tts", methods=["POST"])
def toggle_tts():
    global tts_active
    tts_active = not tts_active
    logging.info("Se tocó el boton de Muted.")
    return jsonify({"message": "ok"}), 200

def start_meeting_process():
    global meeting_driver, current_stop_flag, isFinish
    stop_flag = threading.Event()
    current_stop_flag = stop_flag
    driver = join_meet(meet_data["meet_url"], meet_data["email"], meet_data["password"])
    if driver is None:
        logging.error("No se pudo iniciar el navegador correctamente.")
        return
    meeting_driver = driver
    stop_flag = threading.Event()
    stop_flag_participant = threading.Event()
    silence_thread = threading.Thread(target=silence_timer, daemon=True)
    silence_thread.start()
    transcription_thread = threading.Thread(target=transcribe_audio, args=(stop_flag,))
    transcription_thread.start()
    monitor_thread = threading.Thread(target=monitor_meeting, args=(driver, stop_flag))
    monitor_thread.start()
    while monitor_thread.is_alive():
        time.sleep(1)
    stop_flag.set()
    stop_flag_participant.set()
    transcription_thread.join()
    driver.quit()
    isFinish = False
    current_stop_flag = None  # Restablecer bandera
    meeting_driver = None
    logging.info("El proceso de la reunión ha finalizado.")
    
if __name__ == "__main__":
    public_url = ngrok.connect(5004)
    print(" * ngrok tunnel URL:", public_url)
    app.run(host="0.0.0.0", port=5004)
