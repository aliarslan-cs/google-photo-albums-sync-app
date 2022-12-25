#!/usr/bin/python3

import undetected_chromedriver.v2 as uc

from album_downloader import AlbumDownloader
from albums_parser import AlbumsParser
from common_functions import create_dir
from driver_factory import DriverFactory
from google_login_navigator import GoogleLoginNavigator
from pictures_parser import PicturesParser

import os
from dotenv import dotenv_values
import json


DEFAULT_ALBUMS_FILENAME = 'store/albums.json'

driver = object


def login():
    """
    Login to Google Photos.
    """
    global driver

    # load credentials
    google_credentials = dotenv_values(".env")
    
    # check if already logged in
    driver = DriverFactory.createChromeGoogleSafeDriver(headless=True, window_width=800, window_height=1200)
    if GoogleLoginNavigator(driver=driver, email=google_credentials['EMAIL'], password=google_credentials['PASSWORD']).is_signed_in():
        print(f"Already signed in!")
        quit_driver()
        return

    # login to google if requried
    driver = DriverFactory.createChromeGoogleSafeDriver(headless=False, window_width=800, window_height=1200)
    GoogleLoginNavigator(driver=driver, email=google_credentials['EMAIL'], password=google_credentials['PASSWORD']).login()
    quit_driver()


def quit_driver():
    """
    Close the selenium session
    """
    if driver is not None and type(driver) is uc.Chrome:
        DriverFactory.close_driver(driver_instance=driver)
    else:
        print("Driver not initialized to perform quit action.")


def download_albums_info(filename: str = DEFAULT_ALBUMS_FILENAME):
    """
    Downloads & Saves the albums information in the file specified.
    """
    global driver
    driver = DriverFactory.createChromeGoogleSafeDriver(
        headless=True, window_width=1400, window_height=5000)

    # Open google albums page on browser
    driver.get('https://photos.google.com/albums')

    # parse album links
    albums_parser = AlbumsParser(driver=driver, minimum_expected_albums=0)
    albums_parser.parse()
    albums = albums_parser.get_albums_dict()
    
    
    sorted_albums = get_sorted_albums_dict(albums_dict=albums)

    with open(filename, mode='w', encoding='utf-8') as albums_file:
        json.dump(sorted_albums, albums_file, indent=4)

    quit_driver()


def download_photos_links(album_name: str, albums_filename: str = DEFAULT_ALBUMS_FILENAME):
    """
    Saves the links for all pictures in the album specified.
    """
    with open(albums_filename, mode='r', encoding='utf-8') as albums_file:
        albums = json.load(albums_file)

    assert album_name in albums, f'{album_name} NOT FOUND in albums'

    global driver
    # some pages have a very large number of pictures, so setting the height high to capture more links with minimal scrolling
    driver = DriverFactory.createChromeGoogleSafeDriver(
        headless=True, window_width=1400, window_height=5000, url=albums[album_name][1])

    pictures_parser = PicturesParser(driver=driver, album_name=album_name,
                                     album_desc=albums[album_name][0], album_link=albums[album_name][1])
    if pictures_parser.get__expected_pictures_count() > 0:
        pictures_parser.download_photos_links()
    else:
        print(f'IGNORE ALBUM {album_name} AS ALBUM HAS NO PICTURES.')
        return

    pictures = pictures_parser.get_pictures_dict()
    create_dir('store/pictures-metadata')
    with open(f'store/pictures-metadata/{album_name}.json', mode='w', encoding='utf-8') as pictures_file:
        json.dump(pictures, pictures_file, indent=4)

    quit_driver()
    return pictures


def download_photos_links_for_all_albums(albums_filename: str = DEFAULT_ALBUMS_FILENAME):
    """
    Saves the links for all pictures in all albums.
    """
    with open(albums_filename, mode='r', encoding='utf-8') as albums_file:
        albums = json.load(albums_file)

    for album_name in albums:
        print(f'album_name={album_name}')
        download_photos_links(album_name=album_name,
                              albums_filename=albums_filename)


def download_album(album_name: str, albums_filename: str = DEFAULT_ALBUMS_FILENAME):
    """
    Downloads the album as zip and extracts to album dir.
    """
    with open(albums_filename, mode='r', encoding='utf-8') as albums_file:
        albums = json.load(albums_file)

    assert album_name in albums, f'{album_name} NOT FOUND in albums'

    album_desc = albums[album_name][0]
    album_link = albums[album_name][1]

    print(f'Downloading album: {album_name}')
    print(f'    ALBUM_DESC={album_desc}\n    ALBUM_LINK={album_link}')

    minimum_expected_pictures = int(album_desc.split(' ')[0])
    print(f'    minimum_expected_pictures={minimum_expected_pictures}')

    metadata_file = f'store/pictures-metadata/{album_name}.json'
    
    pictures_links = []
    # read the pictures links if the file exists
    if os.path.isfile(metadata_file):
        print(f'Reading Metadata file "{metadata_file}".')
        with open(metadata_file, mode='r', encoding='utf-8') as pictures_file:
            pictures_links = json.load(pictures_file)
    # re-download the pictures links if the file does not exist or the count does not match
    if (not os.path.isfile(metadata_file)) or len(pictures_links) != minimum_expected_pictures:
        print(f'Metadata file "{metadata_file}" DOES NOT EXIST or Length does not match expected count. Creating it now.')
        pictures_links = download_photos_links(album_name, albums_filename)

    AlbumDownloader(album_link=album_link, album_name=album_name, album_desc=album_desc,
                    minimum_expected_pictures=minimum_expected_pictures, pictures_links=pictures_links).download_album()


def download_all_albums(albums_filename: str = DEFAULT_ALBUMS_FILENAME):
    """
    Downloads all the albums as zip and extracts to album dir.
    """
    with open(albums_filename, mode='r', encoding='utf-8') as albums_file:
        albums = json.load(albums_file)
    
    
    sorted_albums_dict = get_sorted_albums_dict(albums_dict=albums)
    for album_name in sorted_albums_dict:
        print('-'*50)
        print(f'Album {list(sorted_albums_dict).index(album_name) + 1} of {len(sorted_albums_dict)}')
        download_album(album_name, albums_filename)

def get_sorted_albums_dict(albums_dict):
    def get_minimum_expected_pictures(item):
        try: minimum_expected_pictures = int(item[1][0].split(' ')[0])
        except: minimum_expected_pictures = 0
        return minimum_expected_pictures

    sorted_albums = {}
    for _key, _value in sorted(albums_dict.items(), key=get_minimum_expected_pictures):
        album_name = _key
        album_desc = _value[0]

        if album_name == '':
            print(f'Ignoring album "{album_name}" with no name.')
            continue
        if 'No items' in album_desc:
            print(f'Ignoring album "{album_name}" with no items.')
            continue
        sorted_albums[album_name] = albums_dict[album_name]
    return sorted_albums
