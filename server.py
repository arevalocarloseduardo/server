from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle

# Configuración para modo headless
chrome_options = Options()
# chrome_options.add_argument("--headless=new")  # Usa el nuevo modo headless de Chrome
# chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Inicia el navegador en el servidor
driver = webdriver.Chrome(options=chrome_options)

# Navega a Google Meet (para establecer el dominio correcto)
driver.get("https://meet.google.com")

# Carga las cookies
try:
    with open("google_cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)
except Exception as e:
    print("Error al cargar cookies:", e)

# Actualiza la página para aplicar las cookies
driver.refresh()

# Verifica si estás autenticado
# Ejemplo: Buscar un elemento que solo exista cuando estás logueado
try:
    driver.find_element("xpath", "//div[@aria-label='Crear una reunión nueva']")
    print("¡Sesión cargada correctamente!")
except:
    print("Error: No se pudo cargar la sesión.")

# Continúa con tu lógica de negocio aquí...

driver.quit()