# Deploying our bot using kubernetes

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

## **Kubernetes**

Now that we have instruments that we need now we will proceed with the kubernetes. In this part we will:

1. Create a cluster setup to use with Ingress NGINX
2. Create a Flask web server to serve relevant HTML pages, multithreading and sign up functionality
3. Build and Deploy Docker image to cluster
4. Use ingress to open ports of cluster to outer world to reach our bot via [URL]()

Prerequisites:

- install [docker](https://docs.docker.com/get-docker/)
- install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

First of all lets get our manifest files and HTML. These files will have our configuration for container and ingress.

```bash
mkdir cluster && cd cluster && mkdir manifests && cd manifests;

curl -LJO https://raw.githubusercontent.com/enesonus/whatsapp-bot/main/cluster/manifests/selenium.yaml;

curl -LJO https://raw.githubusercontent.com/enesonus/whatsapp-bot/main/cluster/manifests/whatsappbot.yaml;

cd ../.. && mkdir templates && cd templates;

curl -LJO https://raw.githubusercontent.com/enesonus/whatsapp-bot/main/templates/get_photo.html
```

Now you have the yaml files for your cluster. This files have information about containers, services and ingress. In order to run on your cloud provider or server you need to properly create [DNS A records](https://help.one.com/hc/en-us/articles/360000799298-How-do-I-create-an-A-record-) for the URL. After handling DNS records you need to change `bot.yourURL.com` and `vnc.yourURL.com` to your own host URL.

whatsappbot.yaml:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wp-bot-ingress
spec:
  rules:
    - host: bot.yourURL.com # Change this row
      http:
        paths:
          - pathType: Prefix
            path: /
            backend:
              service:
                name: whatsapp-bot
                port:
                  number: 7575
```

selenium.yaml:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: selenium-grid-ingress
spec:
  rules:
    - host: vnc.yourURL.com # Change this row
      http:
        paths:
          - pathType: Prefix
            path: /
            backend:
              service:
                name: selenium-grid
                port:
                  number: 7900
```

We will create a kind cluster with extraPortMappings and node-labels so that we can use Ingress on our URL properly.

```bash
cat <<EOF | kind create cluster --wa --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

Setting up Ingress NGINX

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

Get our pods running

```bash
kubectl apply -f cluster/manifests
```

Now run one by one:

```shell
kubectl get pods
```

```shell
kubectl get svc
```

```shell
kubectl get ingress
```

You will see the pods, services and ingress running. If there are some error you can use command:

```shell
kubectl describe pod <pod name>
```

or

```shell
kubectl logs -f <pod name>
```

If there are no error, you can reach your container's screen from your vnc.yourURL.com and sign up (i.e. scan Web Whatsapp QR) from bot.yourURL.com

If you are here without problem CONGRATS!! You can go to bot.yourURL.com , scan the qr and start using the bot.

---

**NOTE**

First setup (i.e. bot accesing web.whatsapp.com reading messages sent to yourself etc.) may take 2-3 minutes since syncing messages from whatsapp takes 2~ minutes generally. To speed up process please have your whatsapp open on your phone for 1-2 minutes.

---
