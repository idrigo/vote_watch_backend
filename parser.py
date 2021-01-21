from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import datetime
import os
import logging
import platform

path_script = os.path.dirname(os.path.abspath(__file__))
if platform.system() == 'Linux':
    drivername = "/usr/lib/chromium-browser/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
else:
    drivername = os.path.join(path_script, 'chromedriver')

def parce_element(n_element, browser):
    soup = BeautifulSoup(browser.page_source, features="lxml")
    comments = soup.findAll(text=lambda text: isinstance(text, Comment) and "/" not in text)
    voices = comments[n_element + 1].next_element
    name = comments[n_element + 1].find_parent().find_parent().findNext().findNext().findNext().findNext().find(
        'span').contents[0]
    return name, voices


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    fileHandler = logging.FileHandler(os.path.join(path_script, 'parser.log'))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    logger.info('STARTING')
    if os.path.exists(os.path.join(path_script, 'data.csv')):
        logger.info('Loading from file')
        df = pd.read_csv(os.path.join(path_script, 'data.csv'))
    else:
        df = pd.DataFrame()

    logger.info('Launching driver')
    browser = webdriver.Chrome(drivername, chrome_options=chrome_options)
    browser.get('http://vote.educom.ru/')
    buttons = browser.find_elements_by_xpath("//*[contains(text(), '↓')]")

    data = {}
    logger.info('Iterating')
    for i, button in enumerate(buttons):
        button.click()  # click on the i-th element in the list
        time.sleep(1)  # wait until list will be updated
        for attempt in range(10):
            try:
                name, voices = parce_element(i, browser)
            except AttributeError:
                logger.warning(f'{i} element failed, retrying')
                time.sleep(1)
            else:
                break
        data[name] = voices

    data['time'] = datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S")
    df = df.append(data, ignore_index=True)
    df.to_csv(os.path.join(path_script, 'data.csv'), index=False)
    browser.quit()

    logger.info('DONE')
