FROM python:3.11
ADD . /
RUN apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
RUN pip install -r requirements.txt
CMD python -m teagram 