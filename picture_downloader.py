# https://stackoverflow.com/questions/61838269/how-can-i-get-selenium-to-get-a-keyboard-press-of-shift-enter-at-the-same-time
# https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html
# https://www.tutorialspoint.com/what-to-press-ctrl-plusc-on-a-page-in-selenium-with-python
# https://stackoverflow.com/questions/34338897/python-selenium-find-out-when-a-download-has-completed

import glob
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from common_functions import bring_to_front, copy_file, create_dir, delete_dir, download_wait, minimize, wait_for_xpath
from driver_factory import DOWNLOAD_DIR


class PictureDownloader:
    def __init__(self, driver, picture_link, album_dir):
        self.__driver = driver
        self._picture_link = picture_link
        self.__album_dir = album_dir
        # self.__photo_main_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[2]/div/div/div/div[2]/div[2]/div'
        self.__photo_main_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/c-wiz[2]/div[2]/span'
    
    def __navigate_to_photo_page(self):
        # Open google albums page on browser
        self.__driver.get(self._picture_link)

    def download_picture(self):
        self.__navigate_to_photo_page()
        wait_for_xpath(self.__driver, delay=5, xpath=self.__photo_main_xpath)
        
        # create temporary downloads dir
        create_dir(DOWNLOAD_DIR)

        # bring browser to front, google photos does not allow to click on download button unless window is active
        bring_to_front(self.__driver)
        
        # press shift + D
        ActionChains(self.__driver).key_down(Keys.SHIFT).key_down('D').perform()
        time.sleep(0.1)
        ActionChains(self.__driver).key_up('D').key_up(Keys.SHIFT).perform()

        # minimize window again
        minimize(self.__driver)
        
         # wait for downloads to finish (max: 3 hours)
        download_wait(DOWNLOAD_DIR, 3 * 60 * 60, 1)
        dl_file = glob.glob(f'{DOWNLOAD_DIR}/*')[0]
        print(f'Downloaded file {dl_file}')

        # move file
        copy_file(dl_file, self.__album_dir)
        delete_dir(DOWNLOAD_DIR)
