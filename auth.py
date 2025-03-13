from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from googleapiclient.discovery import build
import pickle
import os
import time
import json

# Ámbitos necesarios para acceder a los servicios de Google
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Directorio para guardar capturas de pantalla
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(driver, step):
    """Captura una pantalla y la guarda con el nombre del paso."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{step}_{timestamp}.png")
    driver.save_screenshot(screenshot_path)
    print(f"Captura guardada: {screenshot_path}")

def get_credentials():
    """Obtiene credenciales válidas utilizando OAuth2."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds

def join_google_meet_with_auth_session(meet_link):
    """Une a una reunión de Google Meet usando una sesión autenticada."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    user_data_dir = os.path.join(os.path.expanduser("~"), "selenium-chrome-profile")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    take_screenshot(driver, "antes_google_login")
    try:
        driver.get("https://accounts.google.com")
        time.sleep(3)
        take_screenshot(driver, "google_login")
        
        wait = WebDriverWait(driver, 120)
        if "myaccount.google.com" not in driver.current_url:
            print("Inicia sesión en la ventana del navegador...")
            wait.until(lambda d: "myaccount.google.com" in d.current_url or "google.com/webhp" in d.current_url)
            print("Inicio de sesión detectado!")
        take_screenshot(driver, "after_login")
        
        driver.get(meet_link)
        print("Accediendo a Google Meet...")
        wait = WebDriverWait(driver, 30)
        time.sleep(5)
        take_screenshot(driver, "meet_page_loaded")
        
        try:
            mic_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@aria-label, 'micrófono')]"))
            )
            mic_button.click()
            print("Micrófono desactivado")
        except:
            print("No se pudo desactivar el micrófono")
        take_screenshot(driver, "mic_off")
        
        try:
            camera_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@aria-label, 'cámara')]"))
            )
            camera_button.click()
            print("Cámara desactivada")
        except:
            print("No se pudo desactivar la cámara")
        take_screenshot(driver, "camera_off")
        
        try:
            join_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Unirse')]/parent::button"))
            )
            join_button.click()
            print("Unido a la reunión")
        except:
            print("No se pudo unir a la reunión")
        take_screenshot(driver, "joined_meeting")
        
        while True:
            time.sleep(10)
            take_screenshot(driver, "meeting_active")
            
    except KeyboardInterrupt:
        print("Cerrando sesión...")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        driver.quit()
        
if __name__ == "__main__":
    meet_link = "https://meet.google.com/ach-hnno-sst"
    credentials = get_credentials()
    join_google_meet_with_auth_session(meet_link)
