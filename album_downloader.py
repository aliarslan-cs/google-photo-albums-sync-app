# https://stackoverflow.com/questions/61838269/how-can-i-get-selenium-to-get-a-keyboard-press-of-shift-enter-at-the-same-time
# https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html
# https://www.tutorialspoint.com/what-to-press-ctrl-plusc-on-a-page-in-selenium-with-python
# https://stackoverflow.com/questions/34338897/python-selenium-find-out-when-a-download-has-completed

import glob
import json
import os
import shutil
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from common_functions import bring_to_front, copy_file, create_dir, delete_dir, download_wait, extract_zip, minimize, wait_for_xpath
from driver_factory import DOWNLOAD_DIR, DriverFactory
from picture_downloader import PictureDownloader


class AlbumDownloader:
    def __init__(self, album_link, album_name, album_desc, minimum_expected_pictures, pictures_links):
        self.pictures = {}

        self._album_link = album_link
        self.__album_name = album_name
        self.__album_desc = album_desc
        self.__minimum_expected_pictures = minimum_expected_pictures
        self.__pictures_links = pictures_links
        
        self.__album_main_xpath = '/html/body/div[1]'
        # self.__menu_button_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/c-wiz[1]/div[2]/span/div/div[6]'
        # self.__menu_button_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/c-wiz[1]/div[2]/span/div/div[6]/div'
        # self.__download_button_xpath = '/html/body/div[7]/div/div/span[2]'
    
    def __navigate_to_album_page(self, driver):
        # Open google albums page on browser
        driver.get(self._album_link)

    def download_album(self):
        albums_main_dir = 'store/albums'
        album_dir = f'{albums_main_dir}/{self.__album_name}'

        album_txt_file = f'{album_dir}/album-info.json'
        album_pictures_file = f'{album_dir}/album-pictures.json'

        album_obj = [self.__album_name, self.__album_desc, self.__minimum_expected_pictures]

        # check if album already exists
        if os.path.isfile(album_txt_file) and os.path.isfile(album_pictures_file):
            with open(album_txt_file, mode='r', encoding='utf-8') as r_afile:
                old_album_obj = json.load(r_afile)
            with open(album_pictures_file, mode='r', encoding='utf-8') as r_pfile:
                old_pictures_obj = json.load(r_pfile)
            print(f'old: {old_album_obj}')
            print(f'new: {album_obj}')
            print(f'old len: {len(old_pictures_obj)}  -  new len: {len(self.__pictures_links)}')
            if old_album_obj == album_obj and len(old_pictures_obj) == len(self.__pictures_links):
                print('exisitng album is already up to date.')
                return
            elif len(old_pictures_obj) != len(self.__pictures_links):
                print("ALBUM EXISTS BUT NEEDS SYNC.")
                pictures_to_download = [_link for _link in self.__pictures_links if _link not in old_pictures_obj]
                driver = DriverFactory.createChromeGoogleSafeDriver(
                    headless=False, window_width=1200, window_height=800)
                for missing_picture_link in pictures_to_download:
                    print(f'Downloading {missing_picture_link}')
                    PictureDownloader(driver, missing_picture_link, album_dir).download_picture()
                with open(album_pictures_file, mode='w', encoding='utf-8') as w_album_pictures_file:
                    json.dump(self.__pictures_links, w_album_pictures_file, indent=4)
                DriverFactory.close_driver(driver_instance=driver)
                return
        driver = DriverFactory.createChromeGoogleSafeDriver(
                    headless=False, window_width=1200, window_height=800, url=self._album_link)
        # open the album page
        # self.__navigate_to_album_page(driver)
        wait_for_xpath(driver, delay=20, xpath=self.__album_main_xpath, ec_function=EC.element_to_be_clickable)

        # create temporary downloads dir
        delete_dir(DOWNLOAD_DIR)
        create_dir(DOWNLOAD_DIR)
        
        # bring browser to front, google photos does not allow to click on download button unless window is active
        bring_to_front(driver)
        
        # press shift + D
        ActionChains(driver).key_down(Keys.SHIFT).key_down('D').perform()
        time.sleep(0.1)
        ActionChains(driver).key_up('D').key_up(Keys.SHIFT).perform()

        # minimize window again
        # minimize(driver)

        # wait for downloads to finish (max: 3 hours)
        download_wait(DOWNLOAD_DIR, 3 * 60 * 60, 1)

        # zip_file = glob.glob(f'{DOWNLOAD_DIR}/*.zip')[0]
        downloaded_file = max(glob.glob(f'{DOWNLOAD_DIR}/*'), key=os.path.getctime)
        print(f'Downloaded file {downloaded_file}')

        # close the driver
        DriverFactory.close_driver(driver_instance=driver)

        # create the album dir if it does not exist
        # delete_dir(album_dir) - NOT SURE IF WE SHOULD DELETE EXISTING FILES?
        create_dir(album_dir)

        # add downloaded album to album directory
        if downloaded_file.lower().endswith('.zip'):
            extract_zip(downloaded_file, album_dir)
        else:
            copy_file(downloaded_file, album_dir)
        
        # update album info files
        with open(album_txt_file, mode='w', encoding='utf-8') as w_album_txt_file:
            json.dump(album_obj, w_album_txt_file, indent=4)
        with open(album_pictures_file, mode='w', encoding='utf-8') as w_album_pictures_file:
            json.dump(self.__pictures_links, w_album_pictures_file, indent=4)
        
        delete_dir(DOWNLOAD_DIR)
