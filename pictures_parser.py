import json
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from common_functions import scroll_once_by_element_height_xpath_element, wait_for_xpath


class PicturesParser:
    def __init__(self, driver, album_name, album_desc, album_link):
        self.pictures = {}

        self.__driver = driver
        self.__album_name = album_name
        self.__album_desc = album_desc
        self.__album_link = album_link
        try: self.__minimum_expected_pictures = int(self.__album_desc.split(' ')[0])
        except: self.__minimum_expected_pictures = 0
        
        self.__pictures_main_div_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/c-wiz[2]'
        self.__pictures_links_div_xpath = 'div/div[3]/span/div/div/div[1]' # relative to albums_main_div_xpath
        self.picture_link_xpath = "a"
        self._picture_uploader_xpath = "div[3]/div"

    def get_pictures_dict(self):
        return self.pictures

    def get__expected_pictures_count(self):
        return self.__minimum_expected_pictures

    def download_photos_links(self):
        print(f'album to retrieve:\n album_name={self.__album_name}\n album_desc={self.__album_desc}\n album_link={self.__album_link}')
        print(f'minimum_expected_pictures={self.__minimum_expected_pictures}')
        self.__parse_links()

    def __parse_links(self):
        match=False
        last_scroll_top_position = -1
        scroll_count=0
        valid_links = 0
        while True:            
            # get the div with links
            links_div = wait_for_xpath(
                self.__driver, delay=10, xpath=f"{self.__pictures_main_div_xpath}/{self.__pictures_links_div_xpath}")
            visible_links_div = links_div.find_elements(By.XPATH, "div")

            # print(f'len(visible_links_div)={len(visible_links_div)}')
            # visible_links[3].get_attribute('outerHTML')
            # one_picture_link = visible_links_div[1].find_element(By.XPATH, "a").get_attribute('href')
            # one_picture_uploader=visible_links_div[1].find_element(By.XPATH, "div[3]/div").text
            # import pdb; pdb.set_trace()

            # parse links
            valid_links += self.__parse_links_div(visible_links_div)
            print(f'    scroll_count={scroll_count}    last_scroll_top_position={last_scroll_top_position}    unique_links={len(self.pictures)}/{self.__minimum_expected_pictures}')
            if len(self.pictures) >= self.__minimum_expected_pictures or match==True:
                break

            # scroll once
            scroll_top_position = scroll_once_by_element_height_xpath_element(self.__driver, self.__pictures_main_div_xpath)
            if last_scroll_top_position == scroll_top_position:
                match = True
            last_scroll_top_position = scroll_top_position


            time.sleep(0.20)
            scroll_count += 1

        # print('Found pictures:')
        # for _picture_link, _picture_uploader in self.pictures.items():
        #     print(f'    _picture_uploader={_picture_uploader},    _picture_link={_picture_link}')

        # print(f'valid_links={valid_links}')
        # print(f'unique_links={len(self.pictures)}')
        # import pdb; pdb.set_trace()

        if len(self.pictures) < self.__minimum_expected_pictures:
            print(f'WARNING: The parsed pictures count {len(self.pictures)} is less than {self.__minimum_expected_pictures}! sometimes, google photos shows wrong number of total pictures in the album description, which is why we allow a threshold of 3%. Retrying may also improve the results.')
        assert len(self.pictures) >= (self.__minimum_expected_pictures * 0.970), f'Oh no! The parsed pictures count {len(self.pictures)} is less than {self.__minimum_expected_pictures}!'

    def __parse_links_div(self, links_div):
        _valid_links = 0
        for _link_div in links_div:
            try:
                _picture_link = _link_div.find_element(By.XPATH, self.picture_link_xpath).get_attribute('href')
                try: _picture_uploader = _link_div.find_element(By.XPATH, self._picture_uploader_xpath).text
                except: _picture_uploader = 'self'
            except StaleElementReferenceException as e:
                pass
                    # print('Program raised an StaleElementReferenceException exception: '+ str(e) + '. This is expected. Ignoring all exceptions.')
            except Exception as e:
                pass
                    # print('Program raised an Exception exception: '+ str(e) + '. This is expected. Ignoring all exceptions.')
            else:  # successful to parse the link, store it
                _valid_links += 1
                if _picture_link not in self.pictures:
                    self.pictures[_picture_link] = _picture_uploader
        return _valid_links
