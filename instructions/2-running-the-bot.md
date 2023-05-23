# Running Our Bot in Docker

So now we are done with the bot part. It works, but it only works on your machine :)) We will be using containers and kubernetes to be able to deploy our bot to a server or a cloud provider like AWS, Google Cloud. We also will be dividing our bot to 2 parts since we will be now accesing our bot from a URL and we need to serve to more than 1 person. We will have a Remote Browser container and a Server container that serves HTML pages for bot access and containing Selenium.

---

## **Containerizing**

We will be using [Selenium Grid](https://www.selenium.dev/documentation/grid/) in order to create remote browser sessions to be used by our Selenium script. Thanks to docker-selenium and docker-seleniarm (use this one for M1 Macs) projects we will be able to run our application on multiple architectures.
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

You can reach containers' screen i.e. browser instances using noVNC at <http://0.0.0.0:7900>.

After running containers we should connect to them with Remote Webdriver:

For amd64 (Intel or AMD) this uses Chrome:

```python
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

driver = webdriver.Remote(
'http://0.0.0.0:4444', options=driver_options)

```

For arm64 (M1 Macs) this uses Chromium:

```python

from selenium.webdriver.chromium.options import ChromiumOptions as Options
from selenium import webdriver

driver_options = Options()

driver = webdriver.Remote(
'http://0.0.0.0:4444', options=driver_options)
```

We will build our Server container with the [Dockerfile]() we have.

---

**NOTE**

Please be careful about your architecture because if you are using arm64 architecture and try to run amd64 compatible software it will most probably Chrome will crash . You can check your architecture with the `uname -m` command.

---


Go to [the next page](./3-deploying-the-bot.md) to see how we can deploy this image on Kubernetes.