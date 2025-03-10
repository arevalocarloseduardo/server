from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
options = Options()
options.add_argument("--headless")  # Modo sin interfaz gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
def join_meet(meet_url):
    driver.get(meet_url)
    time.sleep(5)
    try:
        join_button = driver.find_element(By.XPATH, "//span[text()='Unirse ahora']")
        join_button.click()
        time.sleep(5)
    except Exception as e:
        print("No se pudo encontrar el botón de 'Unirse ahora':", e)
def capture_screenshot(filename="meet_screenshot.png"):
    driver.save_screenshot(filename)
    img = Image.open(filename)
    img.show()  # Muestra la imagen capturada
meet_url = "https://meet.google.com/ach-hnno-sst"
join_meet(meet_url)
capture_screenshot()
driver.quit()