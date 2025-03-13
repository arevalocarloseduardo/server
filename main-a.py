import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def save_google_session():
    chrome_options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Navegar a Google y autenticarse
    driver.get("https://accounts.google.com")
    
    # Esperar a que te autentiques manualmente
    input("Inicia sesión en Google y presiona Enter cuando hayas terminado...")
    
    # Navegar a Google Meet para asegurar que tenemos todas las cookies necesarias
    driver.get("https://meet.google.com")
    time.sleep(3)  # Esperar para que se carguen todas las cookies
    
    # Guardar cookies
    pickle.dump(driver.get_cookies(), open("google_cookies.pkl", "wb"))
    
    print("Sesión guardada correctamente.")
    driver.quit()

def join_gmeet_with_session(meet_code="ach-hnno-sst"):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    
    # Si estás en un servidor sin interfaz gráfica, habilita el modo headless
    # chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Cargar cookies por dominio
    cookies = pickle.load(open("google_cookies.pkl", "rb"))
    
    # Agrupar cookies por dominio
    domains = {}
    for cookie in cookies:
        if 'domain' in cookie:
            domain = cookie['domain'] if cookie['domain'].startswith('.') else '.' + cookie['domain']
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(cookie)
    
    # Cargar cookies para cada dominio
    for domain, domain_cookies in domains.items():
        # Obtener el dominio base (sin el punto inicial)
        base_domain = domain[1:] if domain.startswith('.') else domain
        
        # Navegar al dominio antes de agregar las cookies
        driver.get(f"https://{base_domain}")
        time.sleep(1)
        
        # Agregar cookies para este dominio
        for cookie in domain_cookies:
            try:
                # Eliminar campos problemáticos
                if 'expiry' in cookie:
                    del cookie['expiry']
                if 'sameSite' in cookie and cookie['sameSite'] == 'None':
                    cookie['sameSite'] = 'Strict'
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Error al agregar cookie: {e}")
                print(f"Cookie problemática: {cookie}")
    
    # Navegar a Google para verificar que estamos logueados
    driver.get("https://www.google.com")
    time.sleep(2)
    
    # Ir a Google Meet con el código proporcionado
    # if meet_code:
    meet_url = f"https://meet.google.com/{meet_code}"
    # else:
        # meet_url = "https://meet.google.com"
    
    driver.get(meet_url)
    print(f"Accediendo a: {meet_url}")
    
    try:
        # Esperar a que aparezca algún elemento que confirme que estamos logueados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Meeting') or contains(@aria-label, 'Reunión')]"))
        )
        print("Sesión cargada correctamente y usuario autenticado.")
    except Exception as e:
        print(f"No se pudo verificar la autenticación: {e}")
    
    # Mantener la sesión abierta
    input("Presiona Enter para salir...")
    driver.quit()

# Si ejecutas este script directamente
if __name__ == "__main__":
    # Descomentar la función que quieras usar
    #save_google_session()
    join_gmeet_with_session()