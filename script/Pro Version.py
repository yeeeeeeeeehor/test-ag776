import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Путь к файлу веб-драйвера Chrome
driver_path = './chromedriver.exe'

def process_site():
    service = Service(driver_path)
    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://ethereumshanghai.com/")

    time.sleep(2)

    wallets = []
    with open('main.txt', 'r') as wallet_file:
        wallets = wallet_file.readlines()

    while len(wallets) > 0:
        wallet = wallets.pop(0).strip()

        address_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'currency-input--src'))
        )
        address_input.clear()
        address_input.send_keys(wallet)

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn__text:nth-child(3)'))
        )
        submit_button.click()
        logging.info(f"Нажата кнопка Submit")

        try:
            withdraw_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@id='withdraw-records']"))
            )
            logging.info("Найдена кнопка Withdraw")

            # Получение данных
            link_element = driver.find_element(By.XPATH, "//a[@class='copy coin-name font-w--600 color--white ml-1 has-tooltip']")
            link = link_element.get_attribute('href')

            eths_element = driver.find_element(By.XPATH, "//span[@class='coin-name font-w--600 color--white ml-1']")
            eths_value = eths_element.text

            count_element = driver.find_elements(By.XPATH, "//span[@class='coin-name font-w--600 color--white ml-1']")[1]
            count_value = count_element.text

            total_eths_element = driver.find_elements(By.XPATH, "//span[@class='coin-name font-w--600 color--white ml-1']")[2]
            total_eths_value = total_eths_element.text

            with open('info.txt', 'a') as info_file:
                info_file.write(f"Кошелек: {wallet}, Ссылка: {link}, ETHS: {eths_value}, Count: {count_value}, Total ETHS: {total_eths_value}\n")

        except Exception as e:
            logging.error("Ошибка при поиске кнопки Withdraw")
            logging.error(str(e))

        withdraw_button = driver.find_element(By.XPATH, "//button[@id='withdraw']")
        withdraw_button.click()
        logging.info("Нажата кнопка Withdraw")

        time.sleep(3)

        modal_close_button = driver.find_element(By.XPATH, "//div[@id='airdrop-modal']/div/div/div/button/span")
        modal_close_button.click()
        logging.info("Нажата кнопка для закрытия модального окна")

        time.sleep(1)  # Добавляем задержку перед закрытием веб-драйвера, чтобы страница успела обработать событие закрытия модального окна

        driver.quit()

process_site()
print("Завершено made by Крипто Підпілля")
