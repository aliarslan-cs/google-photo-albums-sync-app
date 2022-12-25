from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from common_functions import wait_for, wait_for_xpath


class GoogleLoginNavigator:
    def __init__(self, driver, email, password):
        self.__driver = driver
        self.__email = email
        self.__password = password

    def is_signed_in(self):
        # check if already logged in
        self.__navigate_to_login_page()
        return self.__check_is_signed_in()
    
    def __check_is_signed_in(self):
        try:
            wait_for_xpath(self.__driver, delay=5, xpath="(//a[@aria-label='Albums'])")
            return True
        except Exception:
            return False

    def __navigate_to_login_page(self):
        # Open google photos page on browser
        self.__driver.get('https://photos.google.com/login')

    def login(self):
        self.__navigate_to_login_page()

        # check if already logged in
        if self.__check_is_signed_in():
            return

        # wait for the login page to load
        wait_for(self.__driver, delay=1, specifier=By.ID,
                 identifier='identifierId', ec_function=EC.presence_of_element_located)

        # enter email
        email_input = wait_for(self.__driver, delay=10, specifier=By.XPATH,
                               identifier="(//input[@type='email'])", ec_function=EC.presence_of_element_located)
        email_input.send_keys(self.__email)
        self.__driver.find_element(By.XPATH, '//*[@id="identifierNext"]').click()

        # enter password
        password_input = wait_for(self.__driver, delay=10, specifier=By.XPATH,
                                  identifier="(//input[@type='password'])", ec_function=EC.element_to_be_clickable)
        password_input.send_keys(self.__password)
        self.__driver.find_element(By.XPATH, '//*[@id="passwordNext"]').click()

        input("Press Enter when you've completed the 2FA login and Google Photos are loaded...")
