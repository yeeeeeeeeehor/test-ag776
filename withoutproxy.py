import time
import concurrent.futures
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

site_url = input("Введите ссылку на сайт: ")

num_threads = int(input("Введите количество потоков: "))

with open('wallet.txt', 'r') as file:
    wallets = file.readlines()

# Путь к файлу веб-драйвера Chrome
driver_path = './chromedriver.exe'

withdraw_count = 0

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
        EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'btn__text') and text()='Submit']"))
    )

    submit_button.click()

    try:
        withdraw_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "withdraw"))
        )
        withdraw_count += 1

        link_element = driver.find_element(By.XPATH, "//a[contains(@class, 'copy coin-name')]")
        link = link_element.get_attribute("href")

        with open('ref.json', 'a') as ref_file:
            data = {
                "wallet": wallet.strip(),
                "link": link
            }
            ref_file.write(json.dumps(data) + "\n")

    except:
        pass

    driver.quit()

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(process_wallet, wallets)

print(f"Количество успешных появлений кнопки: {withdraw_count}")
