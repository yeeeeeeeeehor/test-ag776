import time
import json
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import concurrent.futures

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

num_threads = int(input("Введите количество потоков: "))

urls = []
with open('url.txt', 'r') as url_file:
    urls = url_file.readlines()

wallets = []
with open('wallet.txt', 'r') as wallet_file:
    wallets = wallet_file.readlines()

# Путь к файлу веб-драйвера Chrome
driver_path = './chromedriver.exe'

def process_url(url):
    service = Service(driver_path)

    driver = webdriver.Chrome(service=service)

    driver.get(url.strip())

    time.sleep(2)

    while wallets:
        wallet = wallets.pop(0).strip()
        logging.info(f"Обработка кошелька: {wallet} для ссылки: {url.strip()}")

        address_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'currency-input--src'))
        )

        address_input.clear()
        address_input.send_keys(wallet)

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
                    logging.info(f"Найдена кнопка Withdraw для кошелька: {wallet}")
                    success = True
                elif response.status_code == 429:
                    logging.warning(f"Ошибка 429 - Превышен лимит запросов. Кошелек: {wallet}")
                    with open('POST.txt', 'a') as post_file:
                        post_file.write(f"Ссылка: {url.strip()}, Кошелек: {wallet}\n")
                    break
                else:
                    time.sleep(1)  # Пауза перед следующим нажатием кнопки

        except Exception as e:
            logging.error(f"Ошибка при нажатии кнопки для кошелька: {wallet}")
            logging.error(str(e))

        with open('log.txt', 'a') as log_file:
            log_file.write(f"Ссылка: {url.strip()}, Кошелек: {wallet}, Найдена кнопка Withdraw: {str(success)}\n")

    driver.quit()

num_urls = len(urls)
num_wallets = len(wallets)
logging.info(f"Количество ссылок: {num_urls}")
logging.info(f"Количество кошельков: {num_wallets}")

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(process_url, urls * (num_wallets // num_threads + 1))

print("Завершено made by Крипто Підпілля")
