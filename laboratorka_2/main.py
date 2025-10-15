from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

URL = "https://belavia.by/booking/#/"

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def input_route_data(driver, CITY_TO, DATE):
    # Ввод города отправления
    city_from = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'input_departure')]"))
    )
    city_from.clear()
    city_from.send_keys("Минск")
    time.sleep(1)
    city_from.send_keys(Keys.ARROW_DOWN)
    city_from.send_keys(Keys.ENTER)
    time.sleep(1)

    # Ввод города назначения
    city_to = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'input_arrival')]"))
    )
    city_to.clear()
    city_to.send_keys(CITY_TO)
    time.sleep(1)
    city_to.send_keys(Keys.ARROW_DOWN)
    city_to.send_keys(Keys.ENTER)
    time.sleep(1)

    # Сброс фокуса, чтобы закрыть выпадающий список
    driver.execute_script("arguments[0].blur();", city_to)
    time.sleep(1)

    # Выбор даты вылета
    departure_date_field = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dates__to')]"))
    )
    departure_date_field.click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "monthWrapper-1bC4p"))
    )
    available_days = driver.find_elements(By.XPATH, "//div[contains(@class, 'day-12oh8') and not(contains(@class, 'day_notAvailable'))]")
    for day in available_days:
        if day.text.strip() == DATE:
            day.click()
            break
    time.sleep(1)

    # Выбор "В одну сторону"
    one_way_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'В одну сторону')]"))
    )
    driver.execute_script("arguments[0].click();", one_way_button)
    time.sleep(1)

    # Кнопка "Поиск"
    search_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Поиск')]"))
    )
    driver.execute_script("arguments[0].click();", search_button)

def get_products(driver, url, CITY_TO, DATE):
    driver.get(url)
    input_route_data(driver, CITY_TO, DATE)

if __name__ == "__main__":
    driver = setup_driver()
    CITY_TO = input("Введите город назначения: ")
    DATE = input("Введите дату вылета (например, '15'): ")
    get_products(driver, URL, CITY_TO, DATE)
    input("Нажмите Enter для выхода...")
    driver.quit()
