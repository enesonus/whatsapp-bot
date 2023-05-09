import datetime
import random
import string
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


BASE_URL = "https://web.whatsapp.com/"
CHAT_URL = "https://web.whatsapp.com/send?phone={phone}&text&type=phone_number&app_absent=1"

chrome_options = Options()
chrome_options.add_argument("start-maximized")
user_data_dir = ''.join(random.choices(string.ascii_letters, k=8))
chrome_options.add_argument("--user-data-dir=selenium")
# chrome_options.add_argument("--incognito")

service = Service(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)


driver.get(BASE_URL)
driver.maximize_window()

load_dotenv()

message = 'First line,' + Keys.SHIFT + Keys.ENTER + Keys.SHIFT + 'second line' + Keys.SHIFT + Keys.ENTER + \
    Keys.SHIFT + 'message from bot at time: ' + \
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
phone = os.getenv("PHONE_NUMBER_ME")
print(phone)

driver.get(CHAT_URL.format(phone=phone))
time.sleep(3)


inp_xpath = (
    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'
)

input_box = WebDriverWait(driver, 60).until(
    expected_conditions.presence_of_element_located((By.XPATH, inp_xpath))
)

input_box.send_keys(message)
input_box.send_keys(Keys.ENTER)

time.sleep(3)

messages = driver.find_elements(By.CLASS_NAME, "_21Ahp")
for message in messages:
    print(message.text + '\n')
time.sleep(1)  # wait 1 second before checking again


time.sleep(100)
driver.quit()
