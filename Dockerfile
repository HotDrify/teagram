FROM python:3.10
ADD . /
RUN apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
RUN pip install -r requirements.txt
EXPOSE 4040
RUN mkdir /data
CMD python3.10 -m teagram