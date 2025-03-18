from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
import os
from pyngrok import ngrok

app = Flask(__name__)
driver = None

# def start_ngrok():
#     ngrok_tunnel = ngrok.connect(5000)
#     print(' * Ngrok URL:', ngrok_tunnel.public_url)

def take_screenshot():
    timestamp = str(int(time.time()))
    filename = f"screenshot_{timestamp}.png"
    driver.save_screenshot(filename)
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    os.remove(filename)
    return encoded_string

def get_interactive_elements():
    elements = []
    
    # Buscar todos los elementos interactivos
    selectors = [
        ('button', 'button'),
        ('input', 'input'),
        ('a', 'link'),
        ('[role="button"]', 'button'),
        ('[role="link"]', 'link'),
        ('[onclick]', 'clickable')
    ]
    
    for selector, element_type in selectors:
        found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in found_elements:
            if element.is_displayed() and element.is_enabled():
                elements.append({
                    'type': element_type,
                    'id': element.get_attribute('id'),
                    'name': element.get_attribute('name'),
                    'class': element.get_attribute('class'),
                    'text': element.text.strip(),
                    'tag': element.tag_name
                })
    
    return elements

@app.route('/navigate', methods=['POST'])
def navigate():
    global driver
    if driver:
        driver.quit()
        
    data = request.json
    url = data['url']
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    time.sleep(2)  # Esperar carga inicial
    
    return jsonify({
        'screenshot': take_screenshot(),
        'elements': get_interactive_elements()
    })

@app.route('/perform-action', methods=['POST'])
def perform_action():
    data = request.json
    action_type = data['action']
    target = data['target']
    
    try:
        element = None
        
        if target.get('id'):
            element = driver.find_element(By.ID, target['id'])
        elif target.get('text'):
            element = driver.find_element(By.LINK_TEXT, target['text'])
        elif target.get('selector'):
            element = driver.find_element(By.CSS_SELECTOR, target['selector'])
        
        if element:
            element.click()
            time.sleep(1)  # Esperar acción
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({
        'screenshot': take_screenshot(),
        'elements': get_interactive_elements()
    })

@app.route('/scroll', methods=['POST'])
def scroll():
    data = request.json
    scroll_type = data.get('type', 'down')
    
    try:
        if scroll_type == 'down':
            driver.execute_script("window.scrollBy(0, window.innerHeight)")
        elif scroll_type == 'up':
            driver.execute_script("window.scrollBy(0, -window.innerHeight)")
        elif scroll_type == 'bottom':
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            
        time.sleep(0.5)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({
        'screenshot': take_screenshot(),
        'elements': get_interactive_elements()
    })

if __name__ == '__main__':
    # start_ngrok()
    app.run(port=5000)