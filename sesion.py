from selenium import webdriver
import pickle
import time

# Configura el navegador
driver = webdriver.Chrome()
driver.get("https://accounts.google.com")

# Inicia sesión MANUALMENTE en Google
input("Inicia sesión manualmente y presiona Enter aquí cuando termines...")

# Guarda las cookies en un archivo
with open("google_cookies.pkl", "wb") as file:
    pickle.dump(driver.get_cookies(), file)

driver.quit()