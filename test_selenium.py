from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
import time
import os
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("meet_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Crear directorio para capturas de pantalla si no existe
screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)

def setup_driver():
    try:
        options = uc.ChromeOptions()
        
        # Configuraciones esenciales para servidor headless
        options.add_argument("--headless=new")  # Nueva forma recomendada para headless
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Importante para servidores sin GPU
        options.add_argument("--window-size=1920,1080")  # Asegura tamaño de ventana adecuado
        
        # Configuraciones adicionales para evitar detección
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--use-fake-ui-for-media-stream")  # Permite acceso a cámara/micrófono
        options.add_argument("--use-fake-device-for-media-stream")  # Dispositivos falsos para servidor sin hardware
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Guardar la sesión para futuros usos (ajusta la ruta según tu sistema)
        user_data_dir = os.path.join(os.path.expanduser("~"), "chrome-data")
        options.add_argument(f"user-data-dir={user_data_dir}")
        
        # Inicializar el driver
        driver = uc.Chrome(options=options)
        logger.info("Driver headless inicializado correctamente")
        return driver
    except Exception as e:
        logger.error(f"Error al inicializar el driver en modo headless: {e}")
        raise

def capture_screenshot(driver, name="meet"):
    """Captura una pantalla y la guarda con marca de tiempo"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(screenshots_dir, f"{name}_{timestamp}.png")
        driver.save_screenshot(filename)
        logger.info(f"Captura guardada: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error al capturar pantalla: {e}")
        return None

def login_google(driver, email, password):
    """Inicia sesión en Google"""
    try:
        logger.info("Iniciando proceso de login en Google")
        driver.get("https://accounts.google.com/signin")
        
        wait = WebDriverWait(driver, 30)
        
        # Esperar e ingresar email
        logger.info("Esperando campo de email...")
        email_input = wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        email_input.clear()
        email_input.send_keys(email)
        capture_screenshot(driver, "1_email_ingresado")
        
        # Hacer clic en Siguiente
        next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        next_button.click()
        logger.info("Email ingresado, pasando a contraseña")
        
        # Esperar e ingresar contraseña
        logger.info("Esperando campo de contraseña...")
        password_input = wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
        time.sleep(2)  # Pequeña pausa para asegurar interactividad
        password_input.clear()
        password_input.send_keys(password)
        capture_screenshot(driver, "2_password_ingresado")
        
        # Hacer clic en Iniciar sesión
        password_next = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
        password_next.click()
        
        # Esperar a que se complete el inicio de sesión
        time.sleep(10)
        try: 
            logger.info("Intentando encontrar botón por texto")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed() and any(text in button.text.lower() for text in ["Get a verification",]):
                    logger.info(f"Encontrado botón con texto: {button.text}")
                    button.click()
                        
        except:
            pass
        logger.info("Login completado exitosamente")
        capture_screenshot(driver, "3_login_completado")
        
        # Verificar si hay página de bienvenida o verificación
        try:
            if "myaccount.google.com" in driver.current_url or "accounts.google.com/signin/newfeatures" in driver.current_url:
                logger.info("Detectada página post-login, continuando...")
                driver.get("https://meet.google.com/")  # Navegar directamente a Meet
                time.sleep(5)
        except:
            pass
            
        return True
    except Exception as e:
        logger.error(f"Error en login_google: {e}")
        capture_screenshot(driver, "error_login")
        return False

def join_meet(driver, meet_url, disable_camera=True, disable_mic=True):
    """Entra a la reunión de Google Meet con opciones para cámara y micrófono"""
    try:
        logger.info(f"Intentando unirse a la reunión: {meet_url}")
        driver.get(meet_url)
        wait = WebDriverWait(driver, 30)
        
        # Esperar a que la página cargue completamente
        time.sleep(10)  # Más tiempo para asegurar carga completa
        logger.info(f"URL actual: {driver.current_url}")
        capture_screenshot(driver, "4_pagina_meet_cargada")
        
        # Verificar si ya estamos dentro de la reunión
        if "?authuser=" in driver.current_url and not "/lookup/" in driver.current_url:
            logger.info("Ya dentro de la página de reunión")
        capture_screenshot(driver, "esperandocontroles")
        # En un entorno headless, puede ser mejor esperar elementos específicos
        logger.info("Esperando que aparezcan controles de audio/vídeo y botón de unirse...")
        time.sleep(5)
        capture_screenshot(driver, "controlesnada")
        # Intentar diferentes selectores para deshabilitar cámara/micrófono
        try:
            if disable_camera:
                camera_selectors = [
                    "[data-is-muted='false'][aria-label*='cámara']",
                    "[data-is-muted='false'][aria-label*='camera']",
                    "button[jsname='BOHaEe']",
                    "button[jscontroller='FTBAv']"
                ]
                for selector in camera_selectors:
                    try:
                        camera_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        camera_button.click()
                        logger.info(f"Cámara desactivada con selector: {selector}")
                        break
                    except:
                        continue
            
            if disable_mic:
                mic_selectors = [
                    "[data-is-muted='false'][aria-label*='micrófono']",
                    "[data-is-muted='false'][aria-label*='microphone']",
                    "button[jsname='DOYHte']",
                    "button[jscontroller='T6gjed']"
                ]
                for selector in mic_selectors:
                    try:
                        mic_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        mic_button.click()
                        logger.info(f"Micrófono desactivado con selector: {selector}")
                        break
                    except:
                        continue
        except Exception as e:
            logger.warning(f"No se pudieron configurar los dispositivos: {e}")
        
        capture_screenshot(driver, "5_antes_de_unirse")
        
        # HTML visible para debugging
        logger.debug(f"HTML de la página: {driver.page_source[:500]}...")
        
        # Intentar diferentes selectores para el botón de unirse
        join_selectors = [
            # "button[jscontroller='soHxf']", # Otro posible selector
            "[aria-label*='Solicitar unirse']", # Buscar por texto del aria-label
            "[aria-label*='Join now']",      # Buscar en inglés también
            "button[data-mdc-dialog-action='join']" # Otro posible selector
        ]
        capture_screenshot(driver, "6_antes_de_unirse")
        joined = False
        for selector in join_selectors:
            try:
                logger.info(f"Intentando con selector: {selector}")
                join_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                join_button.click()
                logger.info("Botón 'Unirse ahora' encontrado y clicado")
                joined = True
                break
            except Exception as e:
                logger.debug(f"Selector {selector} falló: {e}")
                continue
        
        if not joined:
            # Intentar buscar por el texto del botón como último recurso
            try:
                logger.info("Intentando encontrar botón por texto")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if button.is_displayed() and any(text in button.text.lower() for text in ["unirse", "ask"]):
                        logger.info(f"Encontrado botón con texto: {button.text}")
                        button.click()
                        joined = True
                        break
            except Exception as e:
                logger.debug(f"Búsqueda por texto falló: {e}")
        
        if not joined:
            logger.error("No se pudo encontrar el botón de 'Unirse ahora' con ningún método")
            raise Exception("No se pudo encontrar el botón para unirse")
        
        # Esperar a que se una a la reunión
        time.sleep(10)
        capture_screenshot(driver, "6_reunion_unido")
        logger.info("¡Unido a la reunión exitosamente!")
        
        return True
    except Exception as e:
        logger.error(f"Error al unirse a la reunión: {e}")
        capture_screenshot(driver, "error_join_meet")
        return False

def main():
    # Configuración
    email = "robertogomez5769@gmail.com"
    password = "Algoritmo12."  # Considera usar variables de entorno para credenciales
    meet_url = "https://meet.google.com/cri-vaob-nyw"
    
    driver = None
    try:
        # Verificar que Chrome esté instalado
        chrome_check = os.system("which google-chrome > /dev/null")
        if chrome_check != 0:
            logger.error("Google Chrome no está instalado. Instálalo con: sudo apt install google-chrome-stable")
            return
            
        # Inicializar el driver
        driver = setup_driver()
        
        # Iniciar sesión en Google
        if login_google(driver, email, password):
            # Unirse a la reunión
            join_meet(driver, meet_url, disable_camera=True, disable_mic=True)
            
            # Mantener el bot en la reunión por un tiempo determinado
            stay_time = 60 * 60  # 1 hora en segundos
            logger.info(f"Permaneciendo en la reunión por {stay_time // 60} minutos")
            
            # Loop para mantenerse activo y verificar periódicamente
            start_time = time.time()
            while time.time() - start_time < stay_time:
                # Cada 5 minutos, verificar si seguimos en la reunión
                if (time.time() - start_time) % 300 < 10:  # Verificar aproximadamente cada 5 minutos
                    capture_screenshot(driver, f"verificacion_{int((time.time() - start_time) // 60)}min")
                    logger.info(f"Todavía en la reunión - {int((time.time() - start_time) // 60)} minutos transcurridos")
                time.sleep(10)
        else:
            capture_screenshot(driver, f"verificacion_{int((time.time() - start_time) // 60)}min")
            logger.error("No se pudo iniciar sesión en Google")
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {e}")
    finally:
        # Cerrar el navegador al finalizar
        if driver:
            logger.info("Cerrando el navegador")
            driver.quit()

if __name__ == "__main__":
    main()