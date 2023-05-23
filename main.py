from flask import Flask, request, send_file, redirect, render_template
import datetime
import time
import os
import json
import uuid
import schedule
import threading

from dotenv import load_dotenv

from selenium import webdriver

from selenium.webdriver.chromium.options import ChromiumOptions as Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException


# Checking user sign in status and signing in if not signed in


def user_sign_in():

    print("Signing in...")

    driver_options = Options()
    # driver_options.add_argument("-headless=new")
    driver_options.add_argument("--user-data-dir=/home/seluser/selenium")
    driver_options.add_argument("--disable-extensions")
    driver_options.add_argument("--disable-gpu")
    driver_options.add_argument("--disable-dev-shm-usage")
    # driver_options.add_argument("-browserVersion=113.0")
    # driver_options.add_argument("-platformName=linux")
    driver_options.add_argument("--window-size=1366,768")

    # service = Service(ChromeDriverManager(
    #     chrome_type=ChromeType.CHROMIUM).install())

    st = time.time()
    # driver = webdriver.Chrome(service=service, options=driver_options)
    print(f"browser_ip: {browser_ip}")

    try:
        driver = webdriver.Remote(
            f'http://{browser_ip}:4444', options=driver_options)

        print('Driver initiated... web.whatsapp.com is being loaded...')
        driver.get('https://web.whatsapp.com')

        print('accessed web.whatsapp.com successfully...')

        print("Waiting for page to load...")
        wait_for_startup = EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div'))
        WebDriverWait(driver, timeout=60).until(wait_for_startup)

        print("Getting QR Info")

        wait_for_loading_qr = EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[3]/div[1]/div/div/div[2]/div/span'))
        WebDriverWait(driver, timeout=30).until_not(wait_for_loading_qr)
        time.sleep(3)
        qr_exists = False
        try:
            qr_exists = driver.find_element(
                By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/div/span').is_displayed()
        except NoSuchElementException:
            qr_exists = False
            print("QR doesn't exist i.e. already logged in")

        if qr_exists:
            driver.get_screenshot_as_file(f'screenshot_QR_{phone}.png')
            print('Screenshot of QR is saved')
            wait_for_qr = EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/div/span'))
            WebDriverWait(driver, timeout=60).until_not(wait_for_qr)
        else:
            if os.path.exists(f'screenshot_QR_{phone}.png'):
                os.remove(f'screenshot_QR_{phone}.png')
            else:
                print(
                    f'screenshot_QR_{phone}.png does not exist, could not delete')

        wait_for_search = EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[1]/div'))
        WebDriverWait(driver, timeout=60).until(wait_for_search)

        print("User signed in successfully...")
        et = time.time()

        print(f"\nsign_in() execution time: {et-st}\n")
    except WebDriverException as driver_e:
        print(
            f"WebDriverException at user_sign_in(): \n{driver_e}")
    except Exception as e:
        driver.get_screenshot_as_file(f"screenshot_SIGNIN_{time.time()}.png")
        print("Unknown error at user_sign_in()...", e)
    finally:
        driver.close()
        driver.quit()
    return


def whatsapp_messages():

    driver_options = Options()

    # driver_options.add_argument("--headless=new")
    # driver_options.add_argument("--no-sandbox")

    driver_options.add_argument("--disable-dev-shm-usage")

    driver_options.add_argument("--disable-extensions")
    driver_options.add_argument("--disable-gpu")
    # driver_options.add_argument('--profile-directory=Default')
    driver_options.add_argument("--user-data-dir=/home/seluser/selenium")

    # service = Service(ChromeDriverManager(
    #     chrome_type=ChromeType.CHROMIUM).install(), start_error_message='error')

    driver_options.add_argument("-browserVersion=113.0")
    driver_options.add_argument("-platformName=linux")
    driver_options.add_argument("--window-size=1366,768")

    # driver = webdriver.Chrome(options=driver_options, service=service)
    st = time.time()
    print("Getting commands...")

    try:
        driver = webdriver.Remote(
            f'http://{browser_ip}:4444', options=driver_options)

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
            driver.get_screenshot_as_file(
                f"screenshot_TIMEOUT_{time.time()}.png")
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
    except WebDriverException as driver_e:
        print(
            f"Webdriver could not be accesed at whatsapp_messages(): \n{driver_e}")
    except Exception as e:
        driver.get_screenshot_as_file(f"screenshot_READMSG_{time.time()}.png")
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

    # service = Service(ChromeDriverManager(
    #     chrome_type=ChromeType.CHROMIUM).install())

    st = time.time()
    # driver = webdriver.Chrome(options=driver_options, service=service)

    try:
        driver = webdriver.Remote(
            f'http://{browser_ip}:4444', options=driver_options)

        print(f"from {phone} to {phone_no}")

        driver.get('https://web.whatsapp.com/send?phone=' +
                   phone_no+'&text='+text)
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

    except WebDriverException as driver_e:
        print(
            f"Webdriver could not be accesed at send_whatsapp_msg(): \n{driver_e}")
    except Exception as e:
        driver.get_screenshot_as_file(f"screenshot_MSG_{time.time()}.png")
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
        sent_a_message = False

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
                sent_a_message = True
                send_whatsapp_msg(send_to, message, message_id)

        # If no messages sent at this minute state it
        if sent_a_message is False:
            print(
                f'There are no messages to send at this time: {datetime.datetime.now().strftime("%H:%M")}')


load_dotenv()
phone = os.getenv("PHONE_NUMBER_ME")
browser_ip = os.getenv("IP_ADDR")
dir_path = os.path.dirname(os.path.realpath(__file__))

filename = 'commands.json'

with open(filename, 'w', encoding='utf-8') as file:
    file.write('[]')
    print("Created commands.json file")


app = Flask(__name__)


@app.route('/phone_num', methods=["GET"])
def phone_num():
    return phone, 200


@app.route('/photo', methods=["GET"])
def get_photo():
    args = request.args
    num = args.get('num')
    filename_qr = 'screenshot_QR_' + num + '.png'
    return send_file(filename_qr, mimetype='image/gif'), 200


@app.route('/', methods=["GET", "POST"])
def home():
    try:
        file_path = f'screenshot_QR_{phone}.png'
        thread_sign_in = threading.Thread(target=user_sign_in)
        thread_sign_in.daemon = True
        # Start sign-in thread if file does not exist
        thread_sign_in.start()

        # Wait until the file is created
        while thread_sign_in.is_alive() and not os.path.exists(file_path):
            print('sleep')
            time.sleep(1)

        print('return')
        return render_template('get_photo.html')
    finally:
        print('finally')
        thread_start = threading.Thread(target=start, args=[thread_sign_in])
        thread_start.start()


def start(old_thread: threading.Thread):

    print('Waiting for sign in thread to complete')
    old_thread.join()

    whatsapp_messages()
    # generate_commands(phone, now, duration=3)

    now = datetime.datetime.now()

    job(started_at=now)
    # Every 5 minutes read commands from the user's chat
    schedule.every(interval=5).minutes.do(whatsapp_messages)
    # Every minute check if there are messages to send
    schedule.every().minute.do(job, started_at=now)

    while True:
        # If time came run the job
        schedule.run_pending()
        # sleep for 1 second
        time.sleep(1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7575, debug=True)
# easy link for whatsapp web
# https://web.whatsapp.com/send?phone=YOURPHONENUMBER&text=send_to:(num%20with%20country%20code)%0A,%0Asend_at:HH:MM%0A,%0Amessage:%20
