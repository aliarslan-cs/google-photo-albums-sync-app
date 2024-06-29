import os
import re
import time
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from logger import setup_logger

DESTINATION_PATH = os.path.join('e:', os.sep, 'GooglePhotosSyncUsingAPI')
COMPARE_FILESIZE_OF_EXISTING_FILES = False
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

logger = setup_logger(log_file='logs/download-with-api.log', log_level='DEBUG', file_log_level='WARNING')

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_albums(creds):
    headers = {
        'Authorization': 'Bearer ' + creds.token
    }
    albums = []
    next_page_token = None

    while True:
        params = {'pageSize': 50}  # Adjust the page size if needed
        if next_page_token:
            params['pageToken'] = next_page_token

        response = requests.get('https://photoslibrary.googleapis.com/v1/albums', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        albums.extend(data.get('albums', []))

        # next_page_token = data.get('nextPageToken')
        next_page_token = None
        if not next_page_token:
            break

    return albums

def get_media_items(creds, album_id):
    headers = {
        'Authorization': 'Bearer ' + creds.token
    }
    media_items = []
    next_page_token = None

    last_counter = 500

    while True:
        body = {'albumId': album_id, 'pageSize': 100}  # Adjust the page size if needed
        if next_page_token:
            body['pageToken'] = next_page_token

        response = requests.post('https://photoslibrary.googleapis.com/v1/mediaItems:search', headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        media_items.extend(data.get('mediaItems', []))

        next_page_token = data.get('nextPageToken')

        if len(media_items) >= last_counter:
            logger.debug(f"      - Retrieved metadata for {len(media_items)} items.")
            last_counter += 500

        if not next_page_token:
            break

    return media_items

def get_file_size(download_url):
    response = requests.head(download_url, allow_redirects=True)
    response.raise_for_status()
    return int(response.headers.get('Content-Length'))

def sanitize_filename(filename):
    # Define a pattern for invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    
    # Replace invalid characters with an underscore
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Trim any trailing spaces or periods
    sanitized = sanitized.rstrip('. ')
    
    # Check for reserved names and adjust if necessary
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    
    if sanitized.upper() in reserved_names:
        sanitized = f"_{sanitized}_"
    
    return sanitized

def download_media_item(media_item, directory):
    filename = media_item['filename']
    sanitized_filename = sanitize_filename(filename)  # Sanitize the filename
    file_path = os.path.join(directory, sanitized_filename)
    
    base_url = media_item['baseUrl']
    
    # Determine the correct suffix based on the media type
    if 'video' in media_item['mediaMetadata']:
        download_url = f"{base_url}=dv"  # The '=dv' suffix requests the original quality download for videos
    else:
        download_url = f"{base_url}=d"  # The '=d' suffix requests the original quality download for photos

    # Check if file already exists and verify its size
    if os.path.exists(file_path):
        if not COMPARE_FILESIZE_OF_EXISTING_FILES:
            logger.info(f"      - File {filename} already exists, skipping download.")
            return
        
        existing_file_size = os.path.getsize(file_path)
        expected_file_size = get_file_size(download_url)
        
        if existing_file_size == expected_file_size:
            logger.info(f"      - File {filename} already exists and matches size, skipping download.")
            return
        else:
            logger.info(f"  X   - File size mismatch for {filename}. Expected: {expected_file_size}, Found: {existing_file_size}. Redownloading...")


    # Download the media item using requests
    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def download_photos():
    creds = authenticate()
    albums = get_albums(creds)
    total_albums = len(albums)

    for index, album in enumerate(albums, start=1):
        album_title = album['title']
        album_id = album['id']
        logger.info(f"Downloading Album {index}/{total_albums}: {album_title}")


        album_directory = os.path.join(DESTINATION_PATH, sanitize_filename(album_title))
        os.makedirs(album_directory, exist_ok=True)

        media_items = get_media_items(creds, album_id)
        total_media_items = len(media_items)
        for media_index, media_item in enumerate(media_items, start=1):
            logger.info(f"  - Downloading {media_index}/{total_media_items}: {media_item['filename']}")
            retries = 3
            while retries > 0:
                try:
                    download_media_item(media_item, album_directory)
                except Exception as e:
                    retries -= 1
                    time_to_wait = 5  # seconds
                    if retries > 0:
                        logger.error(f'Failed to download Album: "{album_title}", Item: {media_item['filename']}, will retry {retries} more time(s) after {time_to_wait} seconds.')
                    else:
                        logger.critical(f'Failed to download Album: "{album_title}", Item: {media_item['filename']}, exception: {str(e)}.')
                    time.sleep(time_to_wait)  # wait before retrying
                else:
                    break
                

if __name__ == '__main__':
    download_photos()
