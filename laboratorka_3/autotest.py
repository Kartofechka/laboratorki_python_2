import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest

BASE_URL = "https://127.0.0.1:443"

@pytest.fixture
def driver():
    drv = webdriver.Chrome()
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


def test_to_get_login_page(driver):
    driver.get(f"{BASE_URL}/login")
    assert "login" in driver.current_url or driver.title != "", "Страница /login должна быть доступна"


def input_login_form(driver, username, password):
    driver.get(f"{BASE_URL}/login")
    user_input = driver.find_element(By.NAME, "username")
    pass_input = driver.find_element(By.NAME, "password")
    user_input.clear()
    pass_input.clear()
    user_input.send_keys(username)
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.ENTER)
    time.sleep(0.5) 


def test_get_gome_without_session(driver):
    driver.get(f"{BASE_URL}/home/user1")
    time.sleep(0.3)
    assert "/login" in driver.current_url, "Без сессии должен быть редирект на /login"


def test_admin_login(driver):
    input_login_form(driver, "admin", "1234")
    time.sleep(0.5)
    assert "/home/admin" in driver.current_url, "Админ должен попасть на /home/admin"
    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    assert "session_id" in cookies, "После логина session_id должны быть в куки"


def test_logout_from_admin(driver):
    input_login_form(driver, "admin", "1234")
    time.sleep(0.5)
    driver.get(f"{BASE_URL}/logout")
    time.sleep(0.3)
    assert "/login" in driver.current_url or "Вы вышли из системы" in driver.page_source, "После логаута возвращаемся на /login"
    driver.get(f"{BASE_URL}/home/admin")
    time.sleep(0.3)
    assert "/login" in driver.current_url, "После логаута доступ закрыт"


def test_forbidden(driver):
    input_login_form(driver, "user1", "123")
    time.sleep(0.5)
    driver.get(f"{BASE_URL}/register")
    time.sleep(0.3)
    assert "ДОСТУП ЗАКРЫТ" in driver.page_source or "403" in driver.page_source, "Неадмин не должен попасть на /register"


def test_get_register_page(driver):
    input_login_form(driver, "admin", "1234")
    time.sleep(0.5)
    driver.get(f"{BASE_URL}/register")
    time.sleep(0.3)
    assert "registration" in driver.page_source.lower() or "Регистрация" in driver.page_source, "Админ должен видеть форму регистрации"


def test_register_new_humster_by_admin(driver):
    input_login_form(driver, "admin", "1234")
    time.sleep(0.5)
    driver.get(f"{BASE_URL}/register")
    time.sleep(0.3)

    name_input = driver.find_element(By.NAME, "reg_name")
    pass_input = driver.find_element(By.NAME, "reg_password")

    new_username = f"user_{int(time.time())}"
    new_password = "testpass123"

    name_input.clear()
    pass_input.clear()
    name_input.send_keys(new_username)
    pass_input.send_keys(new_password)
    pass_input.send_keys(Keys.ENTER)
    time.sleep(0.5)

    assert "Регистрация нового пользователя успешна" in driver.page_source or "main" in driver.page_source.lower(), "Ожидаем успешную регистрацию"

    driver.get(f"{BASE_URL}/logout")
    time.sleep(0.3)
    input_login_form(driver, new_username, new_password)
    time.sleep(0.5)
    assert "/home/" in driver.current_url, "Новый пользователь должен попасть на свою домашнюю страницу"
    assert "hamster" in driver.page_source.lower() or "Хомячок" in driver.page_source, "Ждем прогрузку страницы"
