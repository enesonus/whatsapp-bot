# Deploying Our Bot on Kubernetes

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
cat <<EOF | kind create cluster --wait=5m --config=-
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
