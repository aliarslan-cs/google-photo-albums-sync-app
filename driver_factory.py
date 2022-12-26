from pathlib import Path
import undetected_chromedriver.v2 as uc


SESSION_DIR = 'session'
DOWNLOAD_DIR = 'store\downloads'

class DriverFactory:
    @staticmethod
    def createChromeGoogleSafeDriver(headless = True, window_width=1200, window_height=800, url=None):
        options = uc.ChromeOptions()
        # the 'user-data-dir' option helps maintain the session
        session_path = Path(SESSION_DIR)
        print(f'session path: {str(session_path.absolute())}')
        if not session_path.exists():
            session_path.mkdir(parents=True, exist_ok=True)
        options.add_argument(f'--user-data-dir={str(session_path.absolute())}')
        # run in headless mode
        if headless:
            options.add_argument("--headless")

        prefs = {
            "download.default_directory" : str(Path(DOWNLOAD_DIR).absolute()),
            "profile.default_content_setting_values.popups": 1
        }
        options.add_experimental_option("prefs",prefs)
        
        # set url
        if url is not None:
            options.add_argument(url)

        # start session
        driver = uc.Chrome(options=options, use_subprocess=True)
        # set window size
        driver.set_window_position(0, 0)
        
        # some pages have a very large number of pictures, so setting the height high (1400, 5000) helps to capture more links with minimal scrolling
        driver.set_window_size(window_width, window_height)
        print(f'session started with width: {window_width}, height: {window_height}')

        # return driver object
        return driver

    @staticmethod
    def close_driver(driver_instance):
        print("Attempting to quit driver.")
        if driver_instance.service.is_connectable():
            driver_instance.quit()
            print("Driver quit successfully.")
        else:
            print("Driver not connectable to perform quit action.")
