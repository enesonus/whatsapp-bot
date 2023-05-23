FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y wget nano tzdata

WORKDIR /app
COPY . /app
ENV PYTHONUNBUFFERED=1
RUN pip3 install -r requirements.txt

ENV TZ=Europe/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 80

ENV IP_ADDR=chromium
CMD ["python3", "main.py"]