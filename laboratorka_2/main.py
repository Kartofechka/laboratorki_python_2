from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import pandas as pd
import logging

URL = "https://belavia.by/booking/#/results/1306839043"

logging.basicConfig(level=logging.INFO, filename="avialogger.log",filemode="w", encoding='utf-8', format="%(asctime)s %(levelname)s %(message)s")


def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    logging.info("Драйвер установлен")
    return webdriver.Chrome(options=options)


def select_next_available_date(driver):
    DAY_WRAPPER_SELECTOR = ".dayWrapper-3RXmG.dayWrapper-3ITLw"
    
    try:
        time.sleep(1.5)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, DAY_WRAPPER_SELECTOR))
        )
        
        day_elements = driver.find_elements(By.CSS_SELECTOR, DAY_WRAPPER_SELECTOR)
        
        if len(day_elements) < 5:
            return False
        
        fifth_day = day_elements[4]
        
        try:
            date_text = fifth_day.find_element(By.CSS_SELECTOR, ".date-24_Tz").text
            day_inner_element = fifth_day.find_element(By.CSS_SELECTOR, ".day-3UEdI")
            is_unavailable = 'day_notAvailable-1kG9q' in day_inner_element.get_attribute('class')
        except Exception as e:
            logging.error(f"Возникла ошибка: {e}")
            return False
        
        if is_unavailable:
            return False
        
        driver.execute_script("arguments[0].click();", day_inner_element)
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".flight-1d4hF.flight-1-H3h"))
            )
            logging.info("Успешный переход на следующую дату")
            return True
        except Exception as e:
            logging.error(f"Возникла ошибка: {e}")
            return False
        
    except Exception as e:
        logging.error(f"Возникла ошибка: {e}")
        return False


def get_all_flights_for_date(driver):
    flights_data = []
    
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".flight-1d4hF.flight-1-H3h"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='price__']"))
        )
    except Exception as e:
        logging.error(f"Возникла ошибка: {e}")
    
    planes = driver.find_elements(By.CSS_SELECTOR, ".flight-1d4hF.flight-1-H3h")

    for plane in planes:
        try:
            date = plane.find_element(By.CSS_SELECTOR, ".flightInfo__date-1faz2.flightInfo__date-fp5kN").text
            city_from = plane.find_element(By.CSS_SELECTOR, ".airport-1slwI.airport-1R4Jq:not(.airport_arrival-2Y5kV)").text
            city_to = plane.find_element(By.CSS_SELECTOR, ".airport-1slwI.airport-1R4Jq.airport_arrival-2Y5kV").text
            time_leave = plane.find_element(By.CSS_SELECTOR, ".point-xHwcA:not(.point_arrival-24M7C) .time-39idp").text
            time_arrive = plane.find_element(By.CSS_SELECTOR, ".point-xHwcA.point_arrival-24M7C .time-39idp").text
        except Exception as e:
            logging.error(f"Возникла ошибка: {e}")
            continue 
        
        try:
            price_element = plane.find_element(By.CSS_SELECTOR, ".money-DHk3Z.money-1RYHH.price__money-2aUrq.price__money-bRhYz span")
            price = price_element.text
        except Exception:
            try:
                price = plane.find_element(By.CSS_SELECTOR, "div[class*='money-']").text
            except Exception:
                price = "None"

        
        flights_data.append([date, price + " Br", city_from, city_to, time_leave, time_arrive])
        logging.info("Успешная запись информации по рейсу")
        time.sleep(0.3)
    
    return flights_data


def get_products(driver, url):
    driver.get(url)
    time.sleep(2)
    header = ["Дата", "Стоимость", "Аэропорт отправления", "Аэропорт прибытия", "Время отправления", "Время прибытия", "Ссылка"]

    with open("products.csv", mode="w", encoding='utf-8', newline='') as w_file:
        file_writer = csv.writer(w_file, delimiter="|")
        file_writer.writerow(header)
        logging.info("Создана таблица для данных")

        date_counter = 0
        max_dates = 30

        while date_counter < max_dates:
            time.sleep(2.5)
            logging.info("Вызов функции: get_all_flights_for_date(driver)")
            planes = get_all_flights_for_date(driver)
            
            if not planes:
                break
                
            for plane in planes:
                file_writer.writerow(plane)
            
            logging.info("Вызов функции: select_next_available_date(driver)")
            if not select_next_available_date(driver):
                logging.info("Достигнут заданный лимит по датам")
                break
                
            date_counter += 1
    
    logging.info(f"Завершение парсинга для {date_counter} дат")


def sort_table():
    df = pd.read_csv('products.csv', delimiter='|', encoding='utf-8')
    df = df.sort_values(['Стоимость', 'Дата'])
    df.to_csv('products.csv', sep='|', index=False, encoding='utf-8')


if __name__ == "__main__":
    driver = setup_driver()

    try:
        logging.info("Вызов функции: get_products(driver, URL")
        get_products(driver, URL)
        sort_table()
    finally:
        input("Нажмите Enter для выхода...")
        driver.quit()