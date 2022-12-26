import glob
import os
from pathlib import Path
import shutil
import zipfile
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time


def wait_for(driver, delay, specifier=By.ID, identifier='', ec_function=EC.presence_of_element_located):
    assert identifier != ''
    try:
        myElem = WebDriverWait(driver, delay).until(
            ec_function((specifier, identifier)))
        # print(f"Identifier '{identifier}' is ready!")
        return myElem
    except TimeoutException:
        print(f"Identifier '{identifier}' took too much time!")
        raise TimeoutException(
            f"Identifier '{identifier}' took too much time!")


def wait_for_xpath(driver, delay, xpath, ec_function=EC.presence_of_element_located):
    assert xpath != ''
    return wait_for(driver=driver, delay=delay, specifier=By.XPATH, identifier=xpath, ec_function=ec_function)

def scroll_to_bottom_xpath_element(driver, xpath):
    set_elem_var_str = f"var elem_obj = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    update_scroll_js = f"{set_elem_var_str}; elem_obj.scrollTop = elem_obj.scrollHeight; var lenOfPage=elem_obj.scrollHeight; return lenOfPage;"

    match=False
    lastCount = -1
    while(match==False):
            lenOfPage = driver.execute_script(update_scroll_js)
            if lastCount == lenOfPage:
                match = True
            lastCount = lenOfPage
            time.sleep(3)

def scroll_once_xpath_element(driver, xpath):
    set_elem_var_str = f"var elem_obj = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    update_scroll_js = f"{set_elem_var_str}; elem_obj.scrollTop = elem_obj.scrollHeight; var lenOfPage=elem_obj.scrollHeight; return lenOfPage;"

    # lastCount = driver.execute_script(f"{set_elem_var_str}; return elem_obj.scrollTop;")
    lenOfPage = driver.execute_script(update_scroll_js)

    # print(f'    lastCount={lastCount}\nlenOfPage={lenOfPage}')
    print(f'    lenOfPage={lenOfPage}')

    # return lastCount != lenOfPage
    return lenOfPage

def scroll_once_by_element_height_xpath_element(driver, xpath):
    set_elem_var_str = f"var elem_obj = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    set_elem_height_var_str = f"var elem_height = elem_obj.getBoundingClientRect().height"
    update_scroll_top_js_str = f"elem_obj.scrollTop = elem_obj.scrollTop + elem_height"
    update_scroll_js = f"{set_elem_var_str}; {set_elem_height_var_str}; {update_scroll_top_js_str}; return elem_obj.scrollTop;"

    # lastCount = driver.execute_script(f"{set_elem_var_str}; return elem_obj.scrollTop;")
    scroll_top_position = driver.execute_script(update_scroll_js)

    # print(f'    lastCount={lastCount}\nlenOfPage={lenOfPage}')
    # print(f'    scroll_top_position={scroll_top_position}')

    # return lastCount != lenOfPage
    return scroll_top_position


def trigger_right_click_by_xpath_using_js(driver, xpath):
    element_js = f"var element = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
    ev1_js = 'var ev1 = new MouseEvent("mousedown", {bubbles: true, cancelable: false, view: window, button: 2, buttons: 2, clientX: element.getBoundingClientRect().x,clientY: element.getBoundingClientRect().y});'
    ev1_dispatch_js = 'element.dispatchEvent(ev1);'
    ev2_js = 'var ev2 = new MouseEvent("mouseup", {bubbles: true, cancelable: false, view: window, button: 2, buttons: 0, clientX: element.getBoundingClientRect().x, clientY: element.getBoundingClientRect().y});'
    ev2_dispatch_js = 'element.dispatchEvent(ev2);'
    ev3_js = 'var ev3 = new MouseEvent("contextmenu", {bubbles: true, cancelable: false, view: window, button: 2, buttons: 0, clientX: element.getBoundingClientRect().x, clientY: element.getBoundingClientRect().y});'
    ev3_dispatch_js = 'element.dispatchEvent(ev3);'

    full_js_str = f'{element_js} {ev1_js} {ev1_dispatch_js} {ev2_js} {ev2_dispatch_js} {ev3_js} {ev3_dispatch_js}'
    return driver.execute_script(full_js_str)


def trigger_left_click_by_xpath_using_js(driver, xpath):
    js_str = f"var element = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
    js_str += "var element_bb = element.getBoundingClientRect();"
    js_str += 'element.dispatchEvent(new Event("focus", {isTrusted: true, type: "focus", target: Window, currentTarget: Window, eventPhase: 2}));'
    js_str += 'element.dispatchEvent(new MouseEvent("mousedown", {isTrusted: true, bubbles: true, defaultPrevented: true, cancelable: true, view: window, button: 0, buttons: 1, composed: true, clientX: element_bb.x + element_bb.width/2, clientY: element_bb.y + element_bb.height/2}));'
    js_str += 'element.dispatchEvent(new MouseEvent("mouseup", {isTrusted: true, bubbles: true, defaultPrevented: false, cancelable: true, view: window, button: 0, buttons: 0, composed: true, clientX: element_bb.x + element_bb.width/2, clientY: element_bb.y + element_bb.height/2 + 1}));'
    js_str += 'element.dispatchEvent(new PointerEvent("click", {isTrusted: true, bubbles: true, defaultPrevented: false, cancelable: true, pointerId: 1, pointerType: "mouse", view: window, button: 0, buttons: 0, composed: true, clientX: element_bb.x + element_bb.width/2, clientY: element_bb.y + element_bb.height/2 + 1}));'
    # js_str += 'element.dispatchEvent(new MouseEvent("click", {bubbles: true, cancelable: false, view: window, button: 1, buttons: 0, clientX: element_bb.x,clientY: element_bb.y}));'
    # js_str += 'element.dispatchEvent(new MouseEvent("mouseleave", {bubbles: true, cancelable: false, view: window, button: 1, buttons: 0, clientX: element_bb.x,clientY: element_bb.y}));'

    return driver.execute_script(js_str)

def download_wait(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for at least the expected number of files.

    """
    seconds = 0
    seconds_wait = 3
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(seconds_wait)
        dl_wait = False
        # files = os.listdir(f'{directory}/*.zip')
        files = glob.glob(f'{directory}/*')
        if nfiles and len(files) < nfiles:
            print(f'waiting until at least {nfiles} file(s) is/are downloaded, current count: {len(files)} file(s).')
            dl_wait = True

        for fname in files:
            if fname.lower().endswith('.crdownload') or fname.lower().endswith('.tmp'):
                print(f'waiting until .crdownload and/or .tmp file is gone')
                dl_wait = True

        seconds += seconds_wait
    return seconds

def create_dir(dir_path):
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)

def delete_dir(dir_path):
    path = Path(dir_path)
    shutil.rmtree(path, ignore_errors=True)

def copy_file(soure_path, destination_path):
    shutil.copy(soure_path, destination_path)

def bring_to_front(driver):
    # position = driver.get_window_position()
    # driver.minimize_window()
    # time.sleep(1)
    # driver.set_window_position(position['x'], position['y'])
    driver.set_window_position(0, 0)

def minimize(driver):
    driver.minimize_window()

def extract_zip(zip_file, directory_to_extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # zip_ref.extractall(directory_to_extract_to)
        for zip_info in zip_ref.infolist():
            if zip_info.filename[-1] == '/':
                continue
            zip_info.filename = os.path.basename(zip_info.filename)
            zip_ref.extract(zip_info, directory_to_extract_to)

