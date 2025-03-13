import pickle
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Paso 1: Crear una sesión y guardar las cookies (ejecutar esto en una máquina con GUI)
def save_google_session():
    # Configurar Chrome
    chrome_options = Options()
    # Opcional: descomenta si quieres ver el navegador
    # chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Navegar a Google y autenticarse
    driver.get("https://accounts.google.com")
    
    # Esperar a que te autentiques manualmente
    input("Inicia sesión en Google y presiona Enter cuando hayas terminado...")
    
    # Guardar cookies
    pickle.dump(driver.get_cookies(), open("google_cookies.pkl", "wb"))
    
    print("Sesión guardada correctamente.")
    driver.quit()
save_google_session()