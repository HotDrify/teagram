# ©️ TriggerEarth, 2023
# This file is a part of teagram Userbot
# ✳️ https://github.com/HotDrify/teagram
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🍵 https://www.gnu.org/licenses/agpl-3.0.html
FROM python:3.8
ADD . /
RUN pip install -r requirements.txt
RUN apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
EXPOSE 4040
RUN mkdir /data
CMD python -m teagram 
