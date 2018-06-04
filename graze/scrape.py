import argparse
import cv2
import os
import logging
from io import BytesIO
import numpy
import time

from pyvirtualdisplay import Display
from PIL import Image
import pytesseract

from contextlib import contextmanager

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

logging.getLogger().setLevel(logging.INFO)

def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 10:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(condition_function.__name__))


class Captcha(object):
    def __init__(self, img, code, button, retry=5, log=False):
        '''Init object to handle capture
        
        @param img      XPath for the catpcha image.
        @param code     XPath for text field the catpcha code.
        @param button   XPath for the button to press.
        @param retry    Number of retry to attempt.
        @param log      If set - log images found.'''

        self.img = img
        self.code = code
        self.button = button
        self.retry = retry
        self.log = log

    def captcha(self, browser, img_id=0):
        '''Looks for captcha image.  If found, guesses string.

        @param browser  WebDriver instance.
        @param img_id   ID for logged image filename.'''

        try:
            e = browser.find_element_by_xpath(self.img)
        except exceptions.NoSuchElementException:
            return None

        png = browser.get_screenshot_as_png() # saves screenshot of entire page

        im = Image.open(BytesIO(png)) # uses PIL library to open image in memory
        im = im.convert('L')

        left = e.location['x']
        top = e.location['y']
        right = e.location['x'] + e.size['width']
        bottom = e.location['y'] + e.size['height']

        im = im.crop((left, top, right, bottom)) # defines crop points

        if self.log:
            im.save("img%d.png" % img_id)

        image = numpy.array(im, dtype=numpy.uint8)
        image = cv2.GaussianBlur(image, (3,3), 0)

        captcha = pytesseract.image_to_string(image)
        logging.info("Found captcha '%s'" % captcha)

        return captcha

    def bypass(self, browser):
        '''Attempts to bypass captcha if it is encountered.

        @param browser  WebDriver instance.
        '''

        retry = self.retry
        while 1:
            if retry < 1:
                logging.info("Captcha Failed")
                return
            captcha = self.captcha(browser, retry)
            if captcha is None:
                break
            ef = browser.find_element_by_xpath(self.code)
            ef.send_keys(captcha)
            eb = browser.find_element_by_xpath(self.button)

            eb.click()
            time.sleep(2)
            retry -= 1


class Scrape(object):
    def __init__(self, log=False):
        self.log = log
        self.display = Display(visible=0, size=(800, 2400))
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

    def click_through(self, button):
        button.click()

        def link_has_gone_stale():
            try:
                # poll the link with an arbitrary call
                button.find_elements_by_id('doesnt-matter')
                return False
            except exceptions.StaleElementReferenceException:
                return True

        wait_for(link_has_gone_stale)

    def scrape(self, url):
        self.browser.get(url)
        logging.info('Accessed %s ..', url)

        logging.info('Page title: %s', self.browser.title)

    def download_nsw(self, year=1989, retry=5):
        '''
        @param retry Number of retry attempts on captcha
        '''

        self.scrape('https://www.apps08.osr.nsw.gov.au/erevenue/ucm/ucm_list.php')
        cobj = Captcha(
            "//img[@id='captcha']",
            "//input[@id='gd_securityCode']",
            "//button[@id='captcha']",
            retry,
            self.log
        )
        cobj.bypass(self.browser)

        er = self.browser.find_element_by_xpath("//select[@name='g_range']")
        select = Select(er)
        select.select_by_value('6')

        for y in range(year, 2019):
            for q in range(1, 8, 6):
                if q == 7 and y == 2018:
                    break
                ed = self.browser.find_element_by_xpath("//input[@id='g_date']")
                ed.send_keys(Keys.CONTROL + 'a')
                ed.send_keys('01/0%d/%d' % (q, y))
                esb = self.browser.find_element_by_xpath("//button[@id='g_submit']")
                esb.click()
                time.sleep(1)
                eeb = self.browser.find_element_by_xpath("//button[@id='OpenResultDialog']")
                eeb.click()
                time.sleep(1)
                eeb = self.browser.find_element_by_xpath("//button[@name='export_download']")
                eeb.click()
                time.sleep(20)
                os.rename("ucmlist.slk", "ucmlist-%d-0%d-01.slk" % (y, q))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", type=boolean, default=False, help="Log downloaded images")
    parser.add_argument("-r", "--retries", type=int, default=5, help="Captcha retries")
    parser.add_argument("url", help="URL to scrape")
    args = parser.parse_args()
    
    with Scrape(args.log) as so:
        so.scrape(args.url, args.retries)
