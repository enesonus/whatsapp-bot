import datetime
import time
import os
import json
import uuid
import schedule


from dotenv import load_dotenv

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType


from selenium import webdriver

from selenium.webdriver.chromium.options import ChromiumOptions as Options

from selenium.webdriver.common.by import By
from selenium.webdriver.chromium.service import ChromiumService as Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

load_dotenv()
phone = os.getenv("PHONE_NUMBER_ME")


def user_sign_in():

    # //*[@id="app"]/div/div/div[5]

    try:
        driver_options = Options()

        # driver_options.add_argument("-headless=new")
        driver_options.add_argument("--user-data-dir=/home/seluser/selenium")
        driver_options.add_argument("--disable-extensions")
        driver_options.add_argument("--disable-gpu")
        driver_options.add_argument("--disable-dev-shm-usage")
        driver_options.add_argument("-browserVersion=113.0")
        driver_options.add_argument("-platformName=linux")
        driver_options.add_argument("--window-size=1366,768")

        service = Service(ChromeDriverManager(
            chrome_type=ChromeType.CHROMIUM).install())
        st = time.time()
        # driver = webdriver.Chrome(service=service, options=driver_options)
        driver = webdriver.Remote(
            'http://localhost:4444', options=driver_options)

        driver.get('https://web.whatsapp.com')

        wait_for_qr = EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[1]/div'))
        WebDriverWait(driver, timeout=60).until(wait_for_qr)
        # time.sleep(15)
        print("User signed in successfully...")
        et = time.time()

        print(f"\nsign_in() execution time: {et-st}\n")

    except Exception as e:
        driver.get_screenshot_as_file("screenshot_SIGNIN.png")
        print("Something went wrong at user_sign_in()...", e)
    finally:
        driver.close()
        driver.quit()


def whatsapp_messages():

    driver_options = Options()

    driver_options.add_argument("--headless=new")
    driver_options.add_argument("--no-sandbox")

    driver_options.add_argument("--disable-dev-shm-usage")

    driver_options.add_argument("--disable-extensions")
    driver_options.add_argument("--disable-gpu")
    # driver_options.add_argument('--profile-directory=Default')
    driver_options.add_argument("--user-data-dir=/home/seluser/selenium")

    # service = Service(ChromeDriverManager(
    #     chrome_type=ChromeType.CHROMIUM).install(), start_error_message='error')

    driver_options.add_argument("-browserVersion=113.0")
    driver_options.add_argument("-platformName=linux")
    driver_options.add_argument("--window-size=3840,2160")

    # driver = webdriver.Chrome(options=driver_options, service=service)
    st = time.time()
    print("Getting commands...")
    driver = webdriver.Remote(
        'http://localhost:4444', options=driver_options)

    try:

        driver.get('https://web.whatsapp.com/send?phone='+phone)

        wait_for_search = EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="side"]/div[1]/div/div/div[2]/div'))
        WebDriverWait(driver, timeout=60).until(wait_for_search)
        time.sleep(1)
        print("Whatsapp window opened successfully...")

        try:
            wait_for_chat = EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/span[2]/div/span/div/div/div/div'))
            WebDriverWait(driver, timeout=60).until_not(wait_for_chat)
            print("Chat loaded successfully...")

            wait_for_sync = EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[2]/button'))
            WebDriverWait(driver, timeout=150).until_not(wait_for_sync)
            time.sleep(10)
            print("Synced successfully...")

        except TimeoutException:
            print("\nwhatsapp_messages() Timed out see screenshot\n")
            driver.get_screenshot_as_file("screenshot_TIMEOUT.png")
            whatsapp_messages()
        except Exception as e:
            print("Unknown error at getting messages: ", e)

        time.sleep(3)

        messages = driver.find_elements(
            By.XPATH, '//div[@class="_21Ahp"]/span[@class="_11JPr selectable-text copyable-text"]/span')

        with open("commands.json", "w", encoding="utf-8") as file:
            json.dump([], file)

        for message in messages:
            add_command(message.text)

        et = time.time()

        print(
            f'\nwhatsapp_messages() execution time: {et-st} seconds\n')

    except Exception as e:
        driver.get_screenshot_as_file("screenshot_READMSG.png")
        print("Something went wrong at whatsapp_messages()...", e)
    finally:
        driver.close()
        driver.quit()


def send_whatsapp_msg(phone_no, text, message_id):

    driver_options = Options()

    driver_options.add_argument("-headless=new")
    driver_options.add_argument("--user-data-dir=/home/seluser/selenium")
    driver_options.add_argument("--disable-extensions")
    driver_options.add_argument("--disable-gpu")
    driver_options.add_argument("--disable-dev-shm-usage")
    driver_options.add_argument("-browserVersion=113.0")
    driver_options.add_argument("-platformName=linux")
    # driver_options.add_argument("--window-size=1366,768")

    service = Service(ChromeDriverManager(
        chrome_type=ChromeType.CHROMIUM).install())

    st = time.time()
    # driver = webdriver.Chrome(options=driver_options, service=service)
    driver = webdriver.Remote(
        'http://localhost:4444', options=driver_options)

    print(f"from {phone} to {phone_no}")

    driver.get('https://web.whatsapp.com/send?phone='+phone_no+'&text='+text)

    try:
        wait_for_send_button = EC.visibility_of_element_located(
            (By.XPATH, '//span[@data-testid="send"]'))
        WebDriverWait(driver, timeout=60).until(wait_for_send_button)

        # Find the send button and click it
        send_button = driver.find_element(
            By.XPATH, '//span[@data-testid="send"]')
        send_button.click()

        remove_command(message_id)
        print(f"Message sent to {phone_no}")
        et = time.time()
        time.sleep(3)
        print(f"\nsend_whatsapp_msg() execution time: {et-st}\n")
    except Exception as e:
        driver.get_screenshot_as_file("screenshot_MSG.png")
        print("Something went wrong at send_whatsapp_msg()...", e)
    finally:
        driver.close()
        driver.quit()


def remove_command(message_id):
    try:
        # Read the existing commands from commands.json
        with open("commands.json", "r", encoding="utf-8") as file:
            existing_commands = json.load(file)

        # Check if the given JSON object exists in the commands list
        for command in existing_commands:
            if command["message_id"] == message_id:
                # Remove the JSON object from the commands list
                existing_commands.remove(command)
                break

        # Write the updated commands back to commands.json
        with open("commands.json", "w", encoding="utf-8") as file:
            json.dump(existing_commands, file)

        print("JSON object removed successfully")
    except Exception as e:
        print("Something went wrong at remove_command()...", e)


def add_command(string):
    # Check if the string has the required structure
    if "send_to:" not in string or "send_at:" not in string or "message:" not in string:
        print(f"Invalid string structure: {string}")
        return

    # Extract the values from the string
    phone_number = string.split("send_to:")[1].split(",")[0].strip()
    send_time = string.split("send_at:")[1].split(",")[0].strip()
    message = string.split("message:")[1].strip()
    message_id = uuid.uuid4().hex

    # Create a dictionary object for the new command
    new_command = {
        "send_to": phone_number,
        "send_at": send_time,
        "message": message,
        "message_id": message_id
    }

    # Read the existing commands from commands.json
    with open("commands.json", "r", encoding="utf-8") as file:
        existing_commands = json.load(file)

    # Append the new command to the existing array
    existing_commands.append(new_command)

    # Write the updated commands back to commands.json
    with open("commands.json", "w", encoding="utf-8") as file:
        json.dump(existing_commands, file)

    print(f"String processed successfully: {new_command}")


def generate_commands(num, start_time, duration=7):
    commands = []

    for i in range(duration):
        send_at = (start_time + datetime.timedelta(minutes=i)
                   ).strftime('%H:%M')
        message = f"This is message number {i+1}"

        command = {
            "send_to": num,
            "send_at": send_at,
            "message": message,
            "message_id": uuid.uuid4().hex
        }
        commands.append(command)

    with open('commands.json', 'w', encoding='utf-8') as f:
        json.dump(commands, f, indent=4)


def job(started_at: datetime):
    with open('commands.json', 'r', encoding='utf-8') as command_file:
        data = json.load(command_file)
        # print(data)
        for command in data:
            send_to = command.get('send_to')
            send_at = command.get('send_at')
            message = command.get('message')
            message_id = command.get('message_id')

            # if send_at includes a date
            if len(send_at) > 5:
                # convert send_at to datetime object
                send_at = datetime.datetime.strptime(send_at, '%d/%m/%Y %H:%M')
            else:  # if send_at only includes time
                # convert send_at to datetime object for the next day

                send_at = datetime.datetime.strptime(send_at, '%H:%M')
                send_at = datetime.datetime(
                    started_at.year, started_at.month, started_at.day, send_at.hour, send_at.minute)

                # if the time has already passed today, add one day

                if send_at.hour == started_at.hour:
                    if send_at.minute < started_at.minute:
                        send_at = send_at + datetime.timedelta(days=1)
                if send_at.hour < started_at.hour:
                    send_at = send_at + datetime.timedelta(days=1)

            # check if it's time to send the message

            if datetime.datetime.now().strftime("%m/%d/%Y, %H:%M") == send_at.strftime("%m/%d/%Y, %H:%M"):
                print("datetime.now= {}, send_at= {}" .format(datetime.datetime.now().strftime(
                    "%m/%d/%Y, %H:%M"), send_at.strftime("%m/%d/%Y, %H:%M")))
                send_whatsapp_msg(send_to, message, message_id)


now = datetime.datetime.now()

user_sign_in()
whatsapp_messages()
generate_commands(phone, now, duration=3)

job(started_at=now)
schedule.every(interval=5).minutes.do(whatsapp_messages)
schedule.every().minute.do(job, started_at=now)


while True:
    schedule.run_pending()
    time.sleep(1)

# easy link for whatsapp web
# https://web.whatsapp.com/send?phone=YOURPHONENUMBER&text=send_to:(num%20with%20country%20code)%0A,%0Asend_at:HH:MM%0A,%0Amessage:%20
