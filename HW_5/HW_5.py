import os  # работа с файловой системой
from dotenv import load_dotenv  # загрузка информации из ".env"-файла
from time import sleep
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common import exceptions
from selenium.webdriver.support.wait import WebDriverWait

from lxml import html
from pymongo import errors

from convert_date_time import convert_to_datetime
import draft_settings


def config():

    # загрузка информации из ".env"-файла
    load_dotenv()

    # получение логина и пароля из файла .env
    mail_login = os.getenv("mail_login")
    mail_password = os.getenv("mail_password")
    url = 'https://mail.ru/'

    return mail_login, mail_password, url


def insert_data_to_mongodb(input_dict: dict):    
    try:
        draft_settings.letters.insert_one(input_dict)
    except errors.DuplicateKeyError:
        draft_settings.duplicates.insert_one({'dup_id': input_dict['_id']})


def main():
    user_login, user_password, target_url = config()

    s = Service('./geckodriver')
    # s = Service('./chromedriver')
    driver = webdriver.Firefox(service=s)
    # driver = webdriver.Chrome(service=s)
    driver.implicitly_wait(30)

    wait = WebDriverWait(driver, 30)

    # Open a browser with Selenium
    # for starting and stopping a session:
    # https://mail.ru/
    driver.get(target_url)

    # set window position 0, 0
    driver.set_window_position(0, 0)

    # window size 1280 720
    driver.set_window_size(1280, 720)

    # print(driver.current_url)

    button_in = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Войти")]')))
    button_in.click()
    # print('нажали кнопку "Войти"')

    sleep(1)
    frame = driver.find_element(By.CLASS_NAME, 'ag-popup__frame__layout__iframe')
    driver.switch_to.frame(frame)
    # print('переключились во фрейм')

    input_user = (By.NAME, 'username')
    input_user = wait.until(EC.presence_of_element_located(input_user))
    input_user.send_keys(user_login)
    # print('ввели логин')
    input_user.send_keys(Keys.ENTER)
    # password
    input_user = (By.NAME, 'password')
    input_user = wait.until(EC.visibility_of_element_located(input_user))
    input_user.send_keys(user_password)
    # print('ввели пароль')
    input_user.send_keys(Keys.ENTER)

    driver.switch_to.default_content()

    letters_xpath = '//div[@class="layout__main-frame"]' \
                    '//a[contains(@class, "letter-list-item")]' \
                    '[contains(@class, "letter-bottom")]'

    letters = (By.XPATH, letters_xpath)
    letters = wait.until(EC.visibility_of_element_located(letters))
    # print('переходим в первое письмо:')
    driver.get(letters.get_attribute('href'))
    # print('- выполнено')

    count = 0
    while True:
        count += 1
        print(count)
        # if count == 3:
        #     break
        if count % 5 == 0:
            driver.refresh()
            sleep(3)
        # --------------------------------------------------------------- try
        try:
            print(driver.current_url)
            driver.get(driver.current_url.split('?')[0])
            next_arrow = (By.XPATH, '//span[@title="Следующее"][@data-title-shortcut]')
            next_arrow = wait.until(EC.element_to_be_clickable(next_arrow))
            print("get_attribute('data-title-shortcut')")
            print(driver.find_element(By.XPATH, '//span[@title="Следующее"]').get_attribute('data-title-shortcut'))
            next_arrow.click()
            # print('элемент найден')
            sleep(2)
            link_letter = driver.current_url.split('?')[0]
            driver.get(link_letter)
            # print(driver.current_url)
            if not draft_settings.letters.find_one({'_id': link_letter}):
                print('letters.find_one')
                layout__content = (By.XPATH, '//div[@class="layout__content"]')
                layout_content = wait.until(EC.presence_of_element_located(layout__content))
                layout_content_for_dom = driver.find_element(By.XPATH, '//div[@class="layout__content"]')
                dom = html.fromstring(driver.page_source)
                title_dom = dom.xpath('//h2[@class="thread-subject"]/text()')
                # print('title_dom:')
                # print(title_dom[0])
                letter_author_dom = dom.xpath('//div[@class="letter__author"]//span[@class="letter-contact"]/text()')
                # print('letter_author_dom:')
                # print(letter_author_dom[0])
                letter_date_dom = dom.xpath('//div[@class="letter__date"]/text()')
                # print('letter_date_dom:')
                # print(letter_date_dom[0])
                date_time = convert_to_datetime(letter_date_dom[0])
                # print(date_time)
                letter_content = layout_content.find_element(By.XPATH, '//div[@class="letter__body"]')
                # print('letter_content:')
                letter_content = letter_content.text
                letter_dict = {'_id': link_letter,
                               'title': title_dom[0],
                               'letter_author': letter_author_dom[0],
                               'letter_date': date_time,
                               'letter_content': letter_content}
                insert_data_to_mongodb(letter_dict)
                sleep(0.5)
                driver.refresh()
                print('driver.refresh')
        except exceptions.NoSuchElementException:
            print('элемент не найден')
            break

    sleep(3)

    y_input = input('type "z" to close: ')
    if y_input == 'z':
        driver.quit()
        exit(0)
    else:
        sleep(60)
        driver.quit()


if __name__ == '__main__':
    main()
