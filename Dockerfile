# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster
# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update; apt-get clean

# Add a user for running applications.
RUN useradd apps
RUN mkdir -p /home/apps && chown apps:apps /home/apps

# # Set the Chrome repo.
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install wget.
RUN apt-get install -y wget
RUN apt-get install -y nano


# RUN apt install python3 -y
# RUN apt install python3-pip -y

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

ENV TZ=Europe/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt install tzdata -y


# Make port 80 available to the world outside this container
EXPOSE 80

COPY . .

# Run app.py when the container launches
CMD ["python3", "whatsapp_bot.py"]
