from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

def join_google_meet(meet_link):
    """Une a una reunión de Google Meet usando un perfil de Chrome preautenticado."""
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Evita diálogos de permisos

    # Especificar un directorio de usuario para conservar la sesión de Google
    # La primera vez, se abrirá y tendrás que iniciar sesión manualmente.
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    chrome_options.add_argument(f"--user-data-dir={profile_path}")

    # Inicializar el navegador
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    try:
        # Acceder al enlace de Google Meet
        print("Accediendo a Google Meet...")
        driver.get(meet_link)
        wait = WebDriverWait(driver, 30)

        # Esperar a que se muestre el botón de "Unirse" o "Participar"
        join_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Unirse') or contains(text(), 'Participar')]/parent::button")
            )
        )

        # Intentar desactivar micrófono y cámara antes de unirse
        try:
            mic_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button' and contains(@aria-label, 'micrófono')]")
                )
            )
            if "activado" in mic_button.get_attribute("aria-label").lower():
                mic_button.click()
                print("Micrófono desactivado")
        except Exception as e:
            print(f"No se pudo configurar el micrófono: {e}")

        try:
            camera_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button' and contains(@aria-label, 'cámara')]")
                )
            )
            if "activada" in camera_button.get_attribute("aria-label").lower():
                camera_button.click()
                print("Cámara desactivada")
        except Exception as e:
            print(f"No se pudo configurar la cámara: {e}")

        # Unirse a la reunión
        join_button.click()
        print("Unido a la reunión")

        print("Estás en la reunión. Presiona Ctrl+C en la consola para salir.")
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("Cerrando sesión...")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        # Si quieres que el navegador se cierre automáticamente, descomenta la siguiente línea:
        # driver.quit()
        pass

if __name__ == "__main__":
    # Cambia esto por el enlace de tu reunión de Google Meet
    meet_link = "https://meet.google.com/ach-hnno-sst"
    join_google_meet(meet_link)
