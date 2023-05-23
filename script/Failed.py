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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

proxy_type = input("Введите тип прокси (http, https, socks4, socks5): ")

proxies = []
with open('proxy.txt', 'r') as proxy_file:
    for line in proxy_file:
        proxy_data = line.strip().split(':')
        proxy = {
            'proxyType': ProxyType.MANUAL,
            'httpProxy': f'{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}',
            'sslProxy': f'{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}'
        }
        proxies.append(proxy)

site_url = input("Введите ссылку на сайт: ")
num_threads = int(input("Введите количество потоков: "))

with open('wallet.txt', 'r') as file:
    wallets = file.readlines()

withdraw_count = 0

def process_wallet(wallet):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    # Установка прокси
    proxy = Proxy(proxies=proxies)
    proxy.add_to_capabilities(options.to_capabilities())
    
    driver = webdriver.Chrome(service=Service(executable_path='./chromedriver.exe'), options=options)

    try:
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

        submit_button.click()
        logging.info(f"Нажата кнопка для кошелька: {wallet.strip()}")
        time.sleep(2)  # Дополнительная пауза после первого нажатия кнопки
        submit_button.click()

        withdraw_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='withdraw']"))
        )
        logging.info(f"Найдена кнопка для снятия для кошелька: {wallet.strip()}")

        submit_button.click()
        logging.info(f"Дополнительное нажатие кнопки для кошелька: {wallet.strip()}")
        time.sleep(2)  # Дополнительная пауза после второго нажатия кнопки

        withdraw_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='withdraw']"))
        )
        logging.info(f"Найдена кнопка для снятия после дополнительного нажатия для кошелька: {wallet.strip()}")

        withdraw_count += 1

        link_element = driver.find_element(By.XPATH, "//a[contains(@class, 'copy coin-name')]")
        link = link_element.get_attribute("href")

        with open('ref.json', 'a') as ref_file:
            data = {
                "wallet": wallet.strip(),
                "link": link
            }
            ref_file.write(json.dumps(data) + "\n")

    except Exception as e:
        logging.error(f"Ошибка при нажатии кнопки для кошелька: {wallet.strip()}")
        logging.error(str(e))

    driver.quit()

    if withdraw_count >= 300:
        return

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(process_wallet, wallets)

print(f"Количество успешных появлений кнопки: {withdraw_count}")
