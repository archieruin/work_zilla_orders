import pickle

import urllib3
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from config import TOKEN, cache_file, CHROME_DRIVER_PATH, mail, password
from selenium import webdriver
import telebot

import sys
import time

runnable = True

bot = telebot.TeleBot(TOKEN)

key_words = ['телеграм', 'телеграм бот', 'бот телеграм', 'бот для телеграм', 'telegram bot', 'telegram', 'bot']
except_words = ['доработ', 'ботка', 'обработ']
test_tags = ['дизайн']


def create_file() -> bool:
    file = open(cache_file, 'w', encoding='utf-8')
    file.close()
    return True


def save_task(order_id, description):
    with open(cache_file, 'a', encoding='utf-8') as file:
        tasks = file.write(str(order_id) + ':' + description + '\n')


def task_exists(order_id):
    try:
        with open(cache_file, 'r') as file:
            tasks = file.read(order_id)
            if str(order_id) in tasks:
                return True
        return False
    except FileNotFoundError:
        create_file()
        return False


def search_tasks_by_words(words: list, except_words: list) -> list:
    orders_list_wrapper = driver.find_element_by_class_name('orders_list')
    orders_list = orders_list_wrapper.find_elements_by_class_name('order')
    for order in orders_list:
        order_id: int = int(order.get_attribute("orderid"))
        description: str = order.\
            find_element_by_class_name('job_descrition')\
            .find_element_by_tag_name('h5')\
            .text
        description_lower: str = description.lower()
        for word in words:
            for except_word in except_words:
                if word.lower() in description_lower and except_word.lower() not in description_lower:
                    if not task_exists(order_id):
                        save_task(order_id, description)
                        print('Save task %s %s' % (order_id, description,))
                        bot.send_message(182552976, 'New order in work-zilla.com\n{}'.format(description))
                    else:
                        print('Task exists %s %s' % (order_id, description,))


if __name__ == '__main__':
    url = 'https://client.work-zilla.com/freelancer'

    if runnable:

        options = webdriver.ChromeOptions()
        if '-h' in sys.argv:
            options.add_argument('--headless')
            driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
            print('   ---   Start session with headless mode   ---   ')
            print('Does not work!')
            exit(0)
        else:
            driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
            print('   ---   Start session without headless mode   ---   ')

        while runnable:
            try:
                if driver.current_url != url:
                    url = 'https://www.google.com/accounts/Login'
                    driver.get(url)

                    emailElem = driver.find_element_by_id('identifierId')
                    emailElem.send_keys(mail)

                    nextButton = driver.find_element_by_id('identifierNext')
                    nextButton.click()
                    time.sleep(2)
                    ActionChains(driver).send_keys(password).perform()
                    element = driver.find_element_by_id('passwordNext')
                    driver.execute_script("arguments[0].click();", element)
                    #time.sleep(5)
                    driver.get('https://client.work-zilla.com/freelancer')
                    driver.find_element_by_class_name('google-icon').click()
                    time.sleep(10)

                print('Start check tasks')
                res = search_tasks_by_words(key_words, except_words)
                print('Sleep 5 minutes')
                time.sleep(60*5)
            except KeyboardInterrupt:
                driver.quit()
