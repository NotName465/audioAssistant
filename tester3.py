from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def count_tabs_selenium(browser_path):
    """Подсчет вкладок через Selenium"""

    options = Options()
    options.binary_location = browser_path

    try:
        driver = webdriver.Chrome(options=options)
        tab_count = len(driver.window_handles)
        driver.quit()
        return tab_count
    except Exception as e:
        print(f"Ошибка: {e}")
        return 0


# Использование
tabs = count_tabs_selenium(r"C:\Program Files\Opera GX\opera.exe")
print(f"Открыто вкладок: {tabs}")