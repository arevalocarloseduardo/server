import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Directorio para el perfil de Chrome
PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")
# PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile_unique")
def create_chrome_session():
    """Crea una sesión de Chrome con un perfil persistente y permite el login manual"""
    
    # Asegurarse de que el directorio del perfil existe
    os.makedirs(PROFILE_PATH, exist_ok=True)
    
    # Configurar opciones de Chrome con el perfil persistente
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    
    # Iniciar el navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Navegar a la página de inicio de sesión de Google
    driver.get("https://accounts.google.com")
    
    print("Por favor, inicia sesión en tu cuenta de Google.")
    input("Presiona Enter cuando hayas completado el inicio de sesión...")
    
    # Verificar que estamos logueados navegando a Google Meet
    driver.get("https://meet.google.com")
    time.sleep(3)
    
    print("Sesión guardada en el perfil. Puedes cerrar esta ventana.")
    driver.quit()

def join_gmeet_with_profile(meet_code=""):
    """Usa el perfil guardado para unirse a una reunión de Google Meet"""
    
    # Verificar que el directorio del perfil existe
    if not os.path.exists(PROFILE_PATH):
        print("¡Error! No se encontró el perfil de Chrome. Ejecuta primero create_chrome_session().")
        return
    
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Para permitir acceso a micrófono/cámara
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    
    # Para servidores sin interfaz gráfica (descomenta si es necesario)
    # chrome_options.add_argument("--headless=new")  # nuevo modo headless compatible con Chrome reciente
    
    # Iniciar el navegador con el perfil guardado
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Navegar a Google para verificar que estamos logueados
    driver.get("https://www.google.com")
    time.sleep(2)
    
    # Navegar a Google Meet
    if meet_code:
        meet_url = f"https://meet.google.com/{meet_code}"
    else:
        meet_url = "https://meet.google.com"
    
    driver.get(meet_url)
    print(f"Navegando a: {meet_url}")
    
    # Esperar y comprobar que estamos autenticados
    try:
        # Esperar a que aparezca algún elemento que confirme que estamos en Meet y logueados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Join') or contains(@aria-label, 'Create') or contains(@aria-label, 'Unirse') or contains(@aria-label, 'Crear')]"))
        )
        print("¡Éxito! Sesión cargada correctamente y usuario autenticado.")
        
        # Si hay un código de reunión, intentar unirse
        if meet_code:
            try:
                # Buscar el botón para unirse y hacer clic
                join_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Join') or contains(text(), 'Unirse')]/parent::button"))
                )
                join_button.click()
                print("Uniéndose a la reunión...")
            except Exception as e:
                print(f"No se pudo unir automáticamente a la reunión: {e}")
    
    except Exception as e:
        print(f"No se pudo verificar la autenticación: {e}")
        print("Es posible que la sesión haya expirado o que no se haya iniciado sesión correctamente.")
    
    # Mantener la sesión abierta hasta que el usuario decida cerrarla
    input("Presiona Enter para salir...")
    driver.quit()

# Uso del script
if __name__ == "__main__":
    # Descomentar la función que quieras usar
    #create_chrome_session()  # Ejecuta esto primero para crear el perfil y hacer login
    join_gmeet_with_profile("ach-hnno-sst")  # Reemplaza con tu código de reunión o déjalo vacío