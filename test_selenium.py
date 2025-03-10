from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Configura el perfil de usuario para mantener la sesión de Google
options.add_argument("user-data-dir=/tmp/selenium_profile")  # Cambia esto a una ruta persistente si es necesario

driver = webdriver.Chrome(options=options)

def login_google(email, password):
    driver.get("https://accounts.google.com/signin")
    capture_screenshot()
    wait = WebDriverWait(driver, 20)  # Espera hasta 20 segundos
    email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
    email_input.send_keys(email)
    capture_screenshot()
    driver.find_element(By.ID, "identifierNext").click()
    capture_screenshot()
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
    password_input.send_keys(password)
    capture_screenshot()
    driver.find_element(By.ID, "passwordNext").click()
    time.sleep(5) # Espera a que se complete el inicio de sesión

def join_meet(meet_url):
    driver.get(meet_url)
    wait = WebDriverWait(driver, 20)
    capture_screenshot()
    try:
        # Busca el botón "Unirse ahora" utilizando una estrategia más robusta
        join_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[jsname='CQylAd']")))
        join_button.click()
        time.sleep(5)
    except Exception as e:
        print("No se pudo encontrar el botón de 'Unirse ahora':", e)

def capture_screenshot(filename="meet_screenshot.png"):
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # Formato: AñoMesDía_HoraMinutoSegundo
    filename = f"{filename}_{timestamp}.png"
    driver.save_screenshot(filename)
    img = Image.open(filename)
    img.show()

# Reemplaza con tus credenciales
email = "juanperez8761arg@gmail.com"
password = "Algoritmo12."

login_google(email, password)
meet_url = "https://meet.google.com/cri-vaob-nyw"
capture_screenshot()
join_meet(meet_url)
capture_screenshot()
driver.quit()