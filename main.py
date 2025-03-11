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

def join_meet_as_guest(driver, meet_url, guest_name="Invitado", disable_camera=True, disable_mic=True):
    """Entra a la reunión de Google Meet como invitado"""
    try:
        logger.info(f"Intentando unirse a la reunión como invitado: {meet_url}")
        driver.get(meet_url)
        wait = WebDriverWait(driver, 35)
        
        # Esperar a que la página cargue completamente
        time.sleep(20)
        logger.info(f"URL actual: {driver.current_url}")
        capture_screenshot(driver, "1_pagina_meet_cargada")
        
        # Ingresar nombre de invitado
        logger.info(f"Ingresando nombre de invitado: {guest_name}")
        try:
            # Intentar diferentes selectores para el campo de nombre
            name_selectors = [
                "input[type='text']",
                "input#mat-input-0",
                "input[aria-label*='name']",
                "input[aria-label*='nombre']",
                "input[placeholder*='name']",
                "input[placeholder*='nombre']"
            ]
            
            name_entered = False
            for selector in name_selectors:
                try:
                    name_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    name_input.clear()
                    name_input.send_keys(guest_name)
                    logger.info(f"Nombre ingresado con selector: {selector}")
                    name_entered = True
                    break
                except Exception as e:
                    logger.info(f"Selector para nombre {selector} falló: {e}")
                    continue
            
            if not name_entered:
                # Intentar buscar todos los inputs como último recurso
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for input_field in inputs:
                    if input_field.is_displayed():
                        try:
                            input_field.clear()
                            input_field.send_keys(guest_name)
                            logger.info("Nombre ingresado en campo de entrada encontrado")
                            name_entered = True
                            break
                        except:
                            continue
            
            if not name_entered:
                logger.warning("No se pudo ingresar el nombre de invitado")
                
            capture_screenshot(driver, "2_nombre_ingresado")
        except Exception as e:
            logger.error(f"Error al ingresar nombre: {e}")
        
        # Desactivar cámara y micrófono si es necesario
        logger.info("Configurando cámara y micrófono...")
        try:
            # Tomar una captura antes de cualquier acción para debugging
            capture_screenshot(driver, "3_antes_de_configurar_dispositivos")
            
            # El micrófono y cámara deberían estar desactivados por defecto
            # Pero verificamos y los desactivamos si es necesario
            if disable_camera:
                try:
                    # Buscar botones de cámara para comprobar su estado (rojo = desactivado)
                    camera_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='cámara'], button[aria-label*='camera']")
                    for btn in camera_buttons:
                        try:
                            # Si el botón no está en rojo (desactivado), hacer clic
                            if "off" not in btn.get_attribute("aria-label").lower() and btn.is_displayed():
                                btn.click()
                                logger.info("Cámara desactivada manualmente")
                                time.sleep(1)
                        except:
                            continue
                except Exception as e:
                    logger.info(f"Error al verificar cámara: {e}")
            
            if disable_mic:
                try:
                    # Buscar botones de micrófono para comprobar su estado
                    mic_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='micrófono'], button[aria-label*='microphone']")
                    for btn in mic_buttons:
                        try:
                            # Si el botón no está en rojo (desactivado), hacer clic
                            if "off" not in btn.get_attribute("aria-label").lower() and btn.is_displayed():
                                btn.click()
                                logger.info("Micrófono desactivado manualmente")
                                time.sleep(1)
                        except:
                            continue
                except Exception as e:
                    logger.info(f"Error al verificar micrófono: {e}")
        
        except Exception as e:
            logger.warning(f"No se pudieron configurar los dispositivos: {e}")
        
        capture_screenshot(driver, "4_antes_de_pedir_unirse")
        
        # Buscar y hacer clic en el botón "Ask to join" o "Pedir unirse"
        try:
            
            join_button_selectors = [
                "button:contains('Ask to join')",
                "button:contains('Pedir unirse')",
                "button[aria-label*='Ask']",
                "button[aria-label*='unirse']",
                "button.join-button",
                ".join-button",
                "button.ask-to-join",
                ".ask-to-join"
            ]
            
            joined = False
            
            # Primero intentamos con selectores CSS
            for selector in join_button_selectors:
                try:
                    join_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if join_btn.is_displayed():
                        join_btn.click()
                        logger.info(f"Botón 'Pedir unirse' encontrado y clicado con selector: {selector}")
                        joined = True
                        break
                except:
                    continue
            
            # Si no funciona, intentamos buscar por texto en los botones
            if not joined:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        if button.is_displayed() and any(text in button.text.lower() for text in ["Ask", "pedir"]):
                            logger.info(f"Encontrado botón con texto: {button.text}")
                            button.click()
                            joined = True
                            break
                    except:
                        continue
            
            if not joined:
                # Como último recurso, buscar cualquier botón visible
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        if button.is_displayed():
                            logger.info(f"Intentando con botón visible: {button.get_attribute('outerHTML')}")
                            button.click()
                            time.sleep(2)
                            # Verificar si la URL cambió como señal de éxito
                            if driver.current_url != meet_url:
                                joined = True
                                break
                    except:
                        continue
            if not joined:
               
                    buttonss = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Solicitar unirse') or contains(., 'Ask to join')]")))
                    buttonss.click()
                    time.sleep(2)
                    logger.info(f"Intentando con botón visible: esta")
                    if driver.current_url != meet_url:
                        joined = True
                         
                            
            
            if not joined:
                logger.error("No se pudo encontrar el botón 'Pedir unirse'")
                # Guardar HTML para depuración
                with open("meet_page.html", "w") as f:
                    f.write(driver.page_source)
                logger.info("HTML de la página guardado en meet_page.html para depuración")
        except Exception as e:
            logger.error(f"Error al intentar unirse: {e}")
        
        # Esperar a que se una a la reunión o a que se acepte la solicitud
        logger.info("Esperando a que se acepte la solicitud de unirse...")
        time.sleep(10)
        capture_screenshot(driver, "5_esperando_aceptacion")
        
        # Verificar cada 10 segundos si se unió correctamente durante 2 minutos
        for _ in range(12):  # 12 x 10 segundos = 2 minutos
            try:
                # Tomar captura para verificar estado
                capture_screenshot(driver, f"verificacion_{_}")
                
                # Si encontramos elementos que indican que estamos dentro de la reunión
                participants = driver.find_elements(By.CSS_SELECTOR, ".participant-name, .ZjFb7c")
                if participants:
                    logger.info("Detectados participantes - Unido exitosamente a la reunión")
                    return True
                
                # O si la URL cambió de manera que indica que estamos dentro
                if "?authuser=" in driver.current_url and "lookup" not in driver.current_url:
                    logger.info("URL indica que estamos dentro de la reunión")
                    return True
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error al verificar estado de reunión: {e}")
                time.sleep(10)
        
        logger.warning("No se pudo confirmar la entrada a la reunión después de esperar 2 minutos")
        return False
    except Exception as e:
        logger.error(f"Error general al unirse a la reunión como invitado: {e}")
        capture_screenshot(driver, "error_join_meet")
        return False

def main():
    # Configuración
    meet_url = "https://meet.google.com/buv-dknh-dsx"
    guest_name = "Invitado Bot"  # Nombre que aparecerá en la reunión
    
    driver = None
    try:
        # Verificar que Chrome esté instalado
        chrome_check = os.system("which google-chrome > /dev/null")
        if chrome_check != 0:
            logger.error("Google Chrome no está instalado. Instálalo con: sudo apt install google-chrome-stable")
            return
            
        # Inicializar el driver
        driver = setup_driver()
        
        # Unirse directamente como invitado
        if join_meet_as_guest(driver, meet_url, guest_name, disable_camera=True, disable_mic=True):
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
            logger.error("No se pudo unir a la reunión como invitado")
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {e}")
    finally:
        # Cerrar el navegador al finalizar
        if driver:
            logger.info("Cerrando el navegador")
            driver.quit()

if __name__ == "__main__":
    main()