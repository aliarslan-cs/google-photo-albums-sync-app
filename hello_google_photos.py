#!/usr/bin/python3

import click
import sys
import traceback

import google_photos_utility as google_photos_utility


DEFAULT_ALBUMS_FILENAME = google_photos_utility.DEFAULT_ALBUMS_FILENAME

# the default encoding 'windows-1252' gives error with old Powershell, forcing utf-8
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')


@click.group()
def cli():
    pass


@cli.command(name='login-test')
def login_test():
    """
    Test if already logged in to Google Photos.
    """
    google_photos_utility.login_test()


@cli.command(name='login')
def login():
    """
    Login to Google Photos.
    """
    google_photos_utility.login()


@cli.command(name='download_albums_info')
@click.option('--save_to', 'filename', is_flag=False, show_default=True, default=DEFAULT_ALBUMS_FILENAME, help="Directory to store albums information. For example: --save_to=./store/albums.txt.")
def download_albums_info(filename: str = DEFAULT_ALBUMS_FILENAME):
    """
    Downloads & Saves the albums information in the file specified.
    """
    google_photos_utility.download_albums_info(filename)


@cli.command(name='download_photos_links')
@click.argument('ALBUM_NAME')
@click.option('--albums_file', 'albums_file', is_flag=False, show_default=True, default=DEFAULT_ALBUMS_FILENAME, help="Json file to load albums data.")
def download_photos_links(album_name: str, albums_file: str = DEFAULT_ALBUMS_FILENAME):
    """
    Saves the links for all pictures in the album specified.
    """
    google_photos_utility.download_photos_links(album_name, albums_file)


@cli.command(name='download_photos_links_for_all_albums')
@click.option('--albums_file', 'albums_file', is_flag=False, show_default=True, default=DEFAULT_ALBUMS_FILENAME, help="Json file to load albums data.")
def download_photos_links_for_all_albums(albums_file: str = DEFAULT_ALBUMS_FILENAME):
    """
    Saves the links for all pictures in all albums.
    """
    google_photos_utility.download_photos_links_for_all_albums(albums_file)


@cli.command(name='download_album')
@click.argument('ALBUM_NAME')
@click.option('--albums_file', 'albums_file', is_flag=False, show_default=True, default=DEFAULT_ALBUMS_FILENAME, help="Json file to load albums data.")
def download_album(album_name: str, albums_file: str = DEFAULT_ALBUMS_FILENAME):
    """
    Downloads the album as zip and extracts to album dir.
    """
    google_photos_utility.download_album(album_name, albums_file)


@cli.command(name='download_all_albums')
@click.option('--albums_file', 'albums_file', is_flag=False, show_default=True, default=DEFAULT_ALBUMS_FILENAME, help="Json file to load albums data.")
def download_all_albums(albums_file: str = DEFAULT_ALBUMS_FILENAME):
    """
    Downloads all the albums as zip and extracts to album dir.
    """
    google_photos_utility.download_all_albums(albums_file)


@cli.command(name='synchronize')
def synchronize():
    """
    Retrieves the albums information from Google Photos, then synchronizes all the albums.
    """
    google_photos_utility.download_albums_info()
    google_photos_utility.download_all_albums()


def main() -> int:
    return_code = 0
    try:
        cli()

    except KeyboardInterrupt:
        print("User interrupted program.")
        return_code = 42

    except Exception as e:
        print('Program raised an exception: ' +
              str(e) + '. See traceback below.')
        print(traceback.format_exc())
        # Logs the error appropriately.
        return_code = 42

    else:  # execute if no exception
        print("Program did not raise any exception. Ending gracefully.")
        return_code = 0

    finally:  # always executed, with or without an exception
        # 8. End the session
        google_photos_utility.quit_driver()
        print('Ending Program.')
        return return_code


if __name__ == '__main__':
    sys.exit(main())
