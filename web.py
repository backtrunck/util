from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

def wait_visible(drive, qt_seconds, locator, target):
    '''Verifica se o elemento vai ficar visivel, caso passe uma quantidade de segundos(qt_seconds) retorna False'''
    try:
        WebDriverWait(drive, qt_seconds).until(
            EC.visibility_of_element_located((locator, target)))
        return False #ok, achou o elemento
    except TimeoutException:
        return True

def wait_clickable(driver, qt_seconds, locator, target):
    '''Verifica se o elemento vai ficar visivel, caso passe uma quantidade de segundos(qt_seconds) retorna False'''
    WebDriverWait(driver, qt_seconds).until(EC.element_to_be_clickable((locator, target)))
