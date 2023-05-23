# Designing the application & application flow

First of all let’s talk about the design of our application. There are certain things we should think about if we want to create a user-friendly application. Our application will read messages that are sent to user's own chat, using Whatsapp's [Message Yourself](https://faq.whatsapp.com/1785465805163404/?cms_platform=web) feature and schedule messages to send on behalf of the user. We have 4 important task to do

1. Logging user in
2. Reading & Parsing your own chat
3. Sending scheduled messages
4. Handling remote browser instances

Note: First 3 parts will be explained in a way that do not require a Docker Container i.e. running locally. At part 4 we will see relevant changes need to be done for a containerized environment. Main branch is for containerized environment. If you want full code for running local see [this](www.enesonus.com) branch.

## Logging User In

We will mainly use Selenium’s `visibility_of_element_located` function and WebDriverWait feature. We will also benefit from Chrome’s `--user-data-dir=PATH` option in order to persist our user data so that scanning Web Whatsapp’s QR will be enough for further logins.

```python
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import \*

from webdriver_manager.chrome import ChromeDriverManager

def user_sign_in():

# Checking user sign in status and signing in if not signed in

print("Signing in...")

driver_options = Options()

# Persisting user data for further logins

driver_options.add_argument("--user-data-dir=selenium")

# Performance optimization

driver_options.add_argument("--disable-extensions")
driver_options.add_argument("--disable-gpu")

# setting window size

driver_options.add_argument("--window-size=1366,768")

service = Service(ChromeDriverManager().install())

st = time.time()
try: # Open Chrome
driver = webdriver.Chrome(service=service, options=driver_options)
print('Driver initiated')

       driver.get('https://web.whatsapp.com')
       print('Accessed web.whatsapp.com successfully...')


       print("Waiting for page to load...")
       # Wait for loading page to complete
       wait_for_startup = EC.invisibility_of_element_located(
           (By.XPATH, '//*[@id="initial_startup"]'))
       WebDriverWait(driver, timeout=60).until(wait_for_startup)


       # Wait for QR code to be scanned if not signed in
       wait_for_qr = EC.visibility_of_element_located(
           (By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/div/span'))
       WebDriverWait(driver, timeout=90).until_not(wait_for_qr)


       # Wait for search bar to load i.e. user logged in
       wait_for_search = EC.visibility_of_element_located(
           (By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[1]/div'))
       WebDriverWait(driver, timeout=60).until(wait_for_search)


       print("User signed in successfully...")

       # Keep track of time
       et = time.time()
       print(f"\nsign_in() execution time: {et-st}\n")

       # Handle exceptions

except WebDriverException as driver_e:
print(
f"Webdriver could not be accessed at user_sign_in(): \n{driver_e}")
except Exception as e: # Get screenshot of screen at time of unknown error
driver.get_screenshot_as_file(f"screenshot_SIGNIN.png")
print("Unknown error at user_sign_in()...", e)
finally: # Our job is done close the browser
driver.close()
driver.quit()
```

## Reading & Parsing your own chat

In this part we are going to read and parse user's own chat’s messages and create JSON objects from messages. We will use environment variable for user's phone number because we will use this to send messages to people and also to reach user’s own chat so you should create a file named .env with `PHONE_NUMBER=YOUR_NUMBER_WITH_COUNTRY_CODE` field at the same path or write `export PHONE_NUMBER=YOUR_NUMBER_WITH_COUNTRY_CODE` in terminal (this method is not encouraged since at restart env var vanishes).

We will also check the chat every 5 minutes in case there is a new message scheduled to send. For scheduling please go to next part

Note: There will be some edge cases such as syncing messages etc. so I sincerely recommend reading comments on the code.

```python
# Some more packages to add
import json
import uuid

from dotenv import load_dotenv

# Getting environment variables and current path
load_dotenv()
phone = os.getenv("PHONE_NUMBER")

dir_path = os.path.dirname(os.path.realpath(**file**))

def whatsapp_messages():

    driver_options = Options()

    # We will run headless (i.e no GUI) to reduce CPU and memory usage
    driver_options.add_argument("--headless=new")

    # Some more performance optimization
    driver_options.add_argument("--disable-dev-shm-usage")
    driver_options.add_argument("--disable-extensions")
    driver_options.add_argument("--disable-gpu")

    # Using user data for login
    driver_options.add_argument("--user-data-dir=selenium")

    service = Service(ChromeDriverManager().install())

    # Even though we are running headless we need a window size to be set for the browser to adjust design
    driver_options.add_argument("--window-size=1366,768")

    st = time.time()
    print("Getting commands...")

    try:
        driver = webdriver.Chrome(options=driver_options, service=service)

        driver.get('https://web.whatsapp.com/send?phone='+phone)

        # Wait for search bar to load i.e. user logged in
        wait_for_search = EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="side"]/div[1]/div/div/div[2]/div'))
        WebDriverWait(driver, timeout=60).until(wait_for_search)
        time.sleep(1)
        print("Whatsapp window opened successfully...")

        try:
            # Wait for user's own chat to load and be visible
            wait_for_chat = EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/span[2]/div/span/div/div/div/div'))
            WebDriverWait(driver, timeout=60).until_not(wait_for_chat)
            print("Chat loaded successfully...")

            # We need to wait for messages to sync so that we dont lose data
            wait_for_sync = EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[2]/button'))
            WebDriverWait(driver, timeout=180).until_not(wait_for_sync)
            time.sleep(3)
            print("Synced successfully...")

        except TimeoutException:
            # If timeout occurs save current screen as png for debugging and try again
            print("\nwhatsapp_messages() Timed out see screenshot\n")
            driver.get_screenshot_as_file(
                f"screenshot_TIMEOUT.png")
            time.sleep(10)
            whatsapp_messages()
        except Exception as e:
            print("Unknown error at getting messages: ", e)

        time.sleep(3)

        # We got all messages synced now we can get all messages
        messages = driver.find_elements(
            By.XPATH, '//div[@class="_21Ahp"]/span[@class="_11JPr selectable-text copyable-text"]/span')

        # Empty the file in case there is outdated commands
        with open("commands.json", "w", encoding="utf-8") as file:
            json.dump([], file)

        # Add all messages to the file
        for message in messages:
            add_command(message.text)

        # Keep track of time
        et = time.time()

        print(
            f'\nwhatsapp_messages() execution time: {et-st} seconds\n')

    # Handle exceptions
    except WebDriverException as driver_e:
        print(
            f"Webdriver could not be accesed at whatsapp_messages(): \n{driver_e}")
    except Exception as e:
        driver.get_screenshot_as_file(f"screenshot_READMSG.png")
        print("Something went wrong at whatsapp_messages()...", e)
    finally:
        driver.close()
        driver.quit()

def add_command(string):
    # Check if the string has the required structure
    if "send_to:" not in string or "send_at:" not in string or "message:" not in string:
        print(f"Invalid string structure: {string}")
        return

    # Extract the values from the string
    phone_number = string.split("send_to:")[1].split(",")[0].strip()
    send_time = string.split("send_at:")[1].split(",")[0].strip()
    message = string.split("message:")[1].strip()

    # Attach an id to each JSON object so that we can avoid possible conflicts
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

```

## Sending scheduled messages

So everything is ready, we logged the user in, we have the commands, now we need to send messages on behalf of the user! We need to check every minute if there is a message to send. So at this task we will cover sending messages and scheduling tasks to run at a given interval.

This is the code to send message and scheduling of checks:

```python
def send_whatsapp_msg(phone_no, text, message_id):

    driver_options = Options()
    # Options for chrome
    driver_options.add_argument("-headless=new")
    driver_options.add_argument("--user-data-dir=selenium")
    driver_options.add_argument("--disable-extensions")
    driver_options.add_argument("--disable-gpu")
    driver_options.add_argument("--disable-dev-shm-usage")
    driver_options.add_argument("--window-size=1366,768")

    service = Service(ChromeDriverManager().install())

    st = time.time()

    try:
        driver = webdriver.Chrome(options=driver_options, service=service)

        print(f"from {phone} to {phone_no}")

        # Open the chat of the person we want to send messages to
        driver.get('https://web.whatsapp.com/send?phone='+phone_no+'&text='+text)

        # Wait for send button to appear
        wait_for_send_button = EC.visibility_of_element_located(
            (By.XPATH, '//span[@data-testid="send"]'))
        WebDriverWait(driver, timeout=60).until(wait_for_send_button)

        # Find the send button and click it
        send_button = driver.find_element(
            By.XPATH, '//span[@data-testid="send"]')
        send_button.click()

        # Remove the command from commands.json
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
                send_at = datetime.strptime(send_at, '%d/%m/%Y %H:%M')
            else:  # if send_at only includes time
                # convert send_at to datetime object for the next day

                send_at = datetime.strptime(send_at, '%H:%M')
                send_at = datetime(
                    started_at.year, started_at.month, started_at.day, send_at.hour, send_at.minute)

                # if the time has already passed today, add one day
                if send_at.hour == started_at.hour:
                    if send_at.minute < started_at.minute:
                        send_at = send_at + datetime.timedelta(days=1)
                if send_at.hour < started_at.hour:
                    send_at = send_at + datetime.timedelta(days=1)

            # check if it's time to send the message
            if datetime.now().strftime("%m/%d/%Y, %H:%M") == send_at.strftime("%m/%d/%Y, %H:%M"):
                sent_a_message = True
                send_whatsapp_msg(send_to, message, message_id)

        # If no messages sent at this minute state it
        if sent_a_message is False:
            print(
                f'There are no messages to send at this time: {datetime.now().strftime("%H:%M")}')

now = datetime.now()

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

```

## How to handle remote Browser instances?

Selenium uses Webdrivers for controlling browsers on your local machine but since we want to divide our application to two different containers we will be using Selenium Grid in order to create browser sessions and be able to scale our project easily. Thanks to docker-selenium and docker-seleniarm (use this one for M1 Macs) projects we will be able to run our application on multiple architectures.
Run this in your terminal to run a docker-selenium container that runs Selenium Grid:

For amd64 architecture:

```sh
docker run --rm -it --network wp-bot-eonus \
 --network-alias chromium \
 -e SE_VNC_NO_PASSWORD=1 \
 -p 4444:4444 -p 7900:7900 -p 5900:5900 \
 --shm-size 2g selenium/standalone-chrome:latest
```

For arm64 architecture (M1 Macs):

```sh
docker run --rm -it --network wp-bot-eonus \
 --network-alias chromium \
 -e SE_VNC_NO_PASSWORD=1 \
 -p 4444:4444 -p 7900:7900 -p 5900:5900 \
 --shm-size 2g seleniarm/standalone-chromium:latest
```

These commands will run our container that contains browsers. You can reach these containers using noVNC at <http://localhost:7900> and see the changes occurring while the code is running.

Please be careful about your architecture because if you are using arm64 architecture and try to run amd64 compatible software it will most probably crash and can not open Google Chrome as intended. You can check your architecture with the `uname -m`command.

After running containers we should connect to them with Remote Webdriver:

For amd64 (Intel or AMD) this uses Chrome:

```python
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

driver = webdriver.Remote(
'http://localhost:4444', options=driver_options)

```

For arm64 (M1 Macs) this uses Chromium:

```python

from selenium.webdriver.chromium.options import ChromiumOptions as Options
from selenium import webdriver

driver_options = Options()

driver = webdriver.Remote(
'http://localhost:4444', options=driver_options)
```

Now we constructed our app and it is ready to use. Go to [the next page](./2-running-the-bot.md) to see how we
can run it in Docker.
