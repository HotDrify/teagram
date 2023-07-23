FROM python:3.8
ADD . /
RUN pip install -r requirements.txt
RUN apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
EXPOSE 4040
RUN mkdir /data
CMD python -m teagram 
