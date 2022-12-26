# google-photos-albums-sync-app

Google photos has stopped allowing to keep a local synchronized version of photos via Google Drive sync app. This is a python based selenium solution to synchronize albums on google photos.

## Install Selenium library & dependencies

    pip install -r requirements.txt
    python3 install-chrome-browser-driver.py

## Executing the program cli

Use the help command to see the cli usage docs:

    python3 hello_google_photos.py --help

## Known Errors

### SSL Certs

You get an error when the browser asks you to accept the certificate from a website. You can set to ignore these errors by default in order avoid these errors.
> `[7420:17060:1127/075138.342:ERROR:ssl_client_socket_impl.cc(982)] handshake failed; returned -1, SSL error code 1, net_error -3`

For Chrome, you need to add --ignore-certificate-errors and --ignore-ssl-errors ChromeOptions() argument:

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(chrome_options=options)

For the Firefox, you need to set accept_untrusted_certs FirefoxProfile() option to True:

    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    driver = webdriver.Firefox(firefox_profile=profile)

For the Internet Explorer, you need to set acceptSslCerts desired capability:

    capabilities = webdriver.DesiredCapabilities().INTERNETEXPLORER
    capabilities['acceptSslCerts'] = True
    driver = webdriver.Ie(capabilities=capabilities)
