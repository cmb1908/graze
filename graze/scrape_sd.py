import argparse
import cv2
import os
import logging
from io import BytesIO
import numpy

from pyvirtualdisplay import Display
from selenium import webdriver
from PIL import Image
import pytesseract

logging.getLogger().setLevel(logging.INFO)

class Scrape:
    def __init__(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        logging.info('Initialized virtual display..')

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')

        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })
        logging.info('Prepared chrome options..')

        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        logging.info('Initialized chrome browser..')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.browser.quit()
        self.display.stop()

    def scrape(self, url):
        self.browser.get(url)
        logging.info('Accessed %s ..', url)

        logging.info('Page title: %s', self.browser.title)

        fp = open('test.html','w', encoding='utf-8')
        fp.write(self.browser.page_source)
        fp.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to scrape")
    args = parser.parse_args()
    
    with Scrape() as so:
        so.scrape(args.url)
