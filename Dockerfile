FROM python:3.11
ADD . /
RUN apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
RUN ls
RUN pip install -r teagram/requirements.txt
CMD python -m teagram 