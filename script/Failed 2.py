import time
import concurrent.futures
import json
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

site_url = input("Введите ссылку на сайт: ")

num_threads = int(input("Введите количество потоков: "))

with open('wallet.txt', 'r') as file:
    wallets = file.readlines()

# Путь к файлу веб-драйвера Chrome
driver_path = './chromedriver.exe'

def process_wallet(wallet):
    service = Service(driver_path)

    driver = webdriver.Chrome(service=service)

    driver.get(site_url)

    time.sleep(2)

    address_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'currency-input--src'))
    )

    address_input.clear()
    address_input.send_keys(wallet.strip())

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn__text:nth-child(3)'))
    )

    try:
        time.sleep(2)  # Ожидание 2 секунд после вставки кошелька

        success = False
        while not success:
            submit_button.click()
            logging.info(f"Нажата кнопка Sumbit: {wallet.strip()}")

            # Проверка ответа от сайта
            response = requests.post("https://ethereumshanghai.com/airdrop/submit")
            if response.status_code == 200:
                withdraw_button = driver.find_element(By.XPATH, "//button[@id='withdraw-records']")
                logging.info(f"Найдена кнопка Withdraw для кошелька: {wallet.strip()}")
                success = True
            else:
                time.sleep(1)  # Пауза перед следующим нажатием кнопки

    except Exception as e:
        logging.error(f"Ошибка при нажатии кнопки для кошелька: {wallet.strip()}")
        logging.error(str(e))

    with open('log.txt', 'a') as log_file:
        log_file.write(f"Кошелек: {wallet.strip()}, Найдена кнопка Withdraw: {str(success)}\n")

    driver.quit()

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(process_wallet, wallets)

print("Завершено - made by Крипто Підпілля")
