FROM python:3.10
ADD . /
RUN pip install -r requirements.txt
RUN apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
RUN git config --global --add safe.directory /mnt/d/GITHUB/teagram-tl
EXPOSE 4040
RUN mkdir /data
CMD python -m teagram 
