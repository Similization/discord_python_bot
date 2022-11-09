#FROM python:3.10.8-slim-buster
#
#ENV DEBIAN_FRONTEND=noninteractive
#
#WORKDIR /app
#
#COPY requirements.txt requirements.txt
#
#RUN apt update && apt upgrade -y && \
#    apt install build-essential -y && \
#    apt-get install default-mysql-client -y &&  \
#    apt-get install default-libmysqlclient-dev -y && \
#    apt install --yes libxml2-dev libxslt-dev && \
#    apt clean && \
#    apt autoclean && \
#    apt autoremove --yes && \
#    rm -rf /var/lib/{apt,dpkg,cache,log}/
#
#RUN pip3 install --upgrade pip && \
#    pip3 install -r requirements.txt
#
#COPY . .
#
#ENTRYPOINT [ "python3", "bot_example.py" ]

FROM ubuntu:latest

WORKDIR /discord-bot

RUN apt update &&  apt upgrade &&  \
    apt install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt update && \
    apt install python3.10 -y && \
    apt install python3.10-dev -y &&  \
    apt install python3-pip -y && \
    apt install python3.10-venv -y &&  \
    apt-get install mysql-server -y &&  \
    apt-get install libmysqlclient-dev -y && \
    apt install libopus-dev libopus0 -y &&  \
    apt install ffmpeg -y

RUN mkdir discord_bot && cd discord_bot &&  \
    python3 -m venv discord-env &&  \
    . ./discord-env/bin/activate

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot_example.py" ]
