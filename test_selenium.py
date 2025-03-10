from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image

# Configurar Chrome en modo headless
options = Options()
options.add_argument("--headless")  # Modo sin interfaz gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializar el WebDriver
driver = webdriver.Chrome(options=options)

# Función para iniciar sesión en Google
def login_to_google(email, password):
    driver.get("https://accounts.google.com/ServiceLogin")
    driver.find_element(By.ID, "identifierId").send_keys(email)
    driver.find_element(By.ID, "identifierNext").click()
    time.sleep(2)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.ID, "passwordNext").click()
    time.sleep(5)

# Función para unirse a la reunión de Google Meet
def join_meet(meet_url):
    driver.get(meet_url)
    time.sleep(5)
    # Hacer clic en el botón para unirse a la reunión (sólo si es necesario)
    try:
        join_button = driver.find_element(By.XPATH, "//span[text()='Unirse ahora']")
        join_button.click()
        time.sleep(5)
    except Exception as e:
        print("No se pudo encontrar el botón de 'Unirse ahora':", e)

# Función para tomar captura de pantalla
def capture_screenshot(filename="meet_screenshot.png"):
    driver.save_screenshot(filename)
    # Si deseas recortar la imagen o procesarla, puedes usar Pillow:
    img = Image.open(filename)
    img.show()  # Muestra la imagen capturada

# Credenciales de Google (cambia esto por tus propias credenciales)
email = "tu_email@gmail.com"
password = "tu_contraseña"

# URL de la reunión de Google Meet (cambia esto por tu URL de reunión)
meet_url = "https://meet.google.com/xyz-abc-123"

# Proceso completo
login_to_google(email, password)
join_meet(meet_url)
capture_screenshot()

# Cerrar el navegador
driver.quit()