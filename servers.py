import pickle
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
def join_gmeet_with_session():
    # Configurar Chrome en modo headless para servidor sin GUI
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Para audio/video en Google Meet
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Ir a Google primero para cargar las cookies
    driver.get("https://www.google.com")
    
    # Cargar cookies guardadas
    cookies = pickle.load(open("google_cookies.pkl", "rb"))
    for cookie in cookies:
        # Algunos campos pueden causar problemas al restaurar
        if 'expiry' in cookie:
            del cookie['expiry']
        driver.add_cookie(cookie)
    
    # Ir a Google Meet
    meet_url = "https://meet.google.com/ach-hnno-sst"
    driver.get(meet_url)
    
    print("Unido a la reunión: ach-hnno-sst")
    
    # Aquí puedes agregar lógica para unirte a la reunión, desactivar micrófono/cámara, etc.
    
    # Para mantener la sesión activa
    input("Presiona Enter para salir de la reunión...")
    driver.quit()
join_gmeet_with_session()