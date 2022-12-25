import re
import selenium
from selenium.webdriver.common.by import By
import time

from common_functions import scroll_once_by_element_height_xpath_element, wait_for_xpath


class AlbumsParser:
    def __init__(self, driver, minimum_expected_albums):
        self.albums = {}

        self.__driver = driver
        self.__albums_main_div_xpath = '/html/body/div[1]/div/c-wiz/div[3]/c-wiz/div/div[2]'
        self.__albums_links_div_xpath = 'div/c-wiz/div/div/div[1]' # relative to albums_main_div_xpath
        self.__album_name_xpath = './div[2]/div[1]'  # relative of the '<a>' DOM of the link
        self.__album_items_desc_xpath = './div[2]/div[2]'  # relative of the '<a>' DOM of the link
        self.__minimum_expected_albums = minimum_expected_albums

    def get_albums_dict(self):
        return self.albums

    def parse(self):
        match=False
        lastCount = -1
        scroll_count=0
        valid_links = 0
        while(match==False):            
            # get the div with links
            links_div = wait_for_xpath(
                self.__driver, delay=10, xpath=f"{self.__albums_main_div_xpath}/{self.__albums_links_div_xpath}")
            visible_links = links_div.find_elements(By.XPATH, "//a")

            # parse links
            valid_links += self.parse_albums(visible_links)

            # scroll once
            lenOfPage = scroll_once_by_element_height_xpath_element(self.__driver, self.__albums_main_div_xpath)
            if lastCount == lenOfPage:
                match = True
            lastCount = lenOfPage

            time.sleep(0.2)
            scroll_count += 1

        print('Found albums:')
        for _album_name in self.albums:
            print(f'    album_name={_album_name},    album_items_desc={self.albums[_album_name][0]}')

        print(f'valid_links={valid_links}')
        print(f'unique_links={len(self.albums)}')

        assert len(self.albums) >= self.__minimum_expected_albums, f'Oh no! The parsed albums count {len(self.albums)} is less than {self.__minimum_expected_albums}!'

    def parse_albums(self, links):
        non_ascii_re = r'[^a-zA-Z0-9_\-\.\+ ]'  # r'[^a-zA-Z0-9 -.]'
        _valid_links = 0
        for _link in links:
            try:
                _album_link = _link.get_attribute('href')
                _album_name = _link.find_element(By.XPATH, self.__album_name_xpath).text
                _album_items_desc = _link.find_element(By.XPATH, self.__album_items_desc_xpath).text
                
            except selenium.common.exceptions.StaleElementReferenceException as e:
                pass
                    # print('Program raised an StaleElementReferenceException exception: '+ str(e) + '. This is expected. Ignoring all exceptions.')
            except Exception as e:
                pass
                    # print('Program raised an Exception exception: '+ str(e) + '. This is expected. Ignoring all exceptions.')
            else:  # successful to parse the link, store it
                _valid_links += 1
                
                _clean_album_name = re.sub(non_ascii_re, '', _album_name).strip()
                _clean_album_desc = re.sub(non_ascii_re, '', _album_items_desc).strip()
                if _clean_album_name not in self.albums:
                    self.albums[_clean_album_name] = (_clean_album_desc, _album_link)
        return _valid_links
