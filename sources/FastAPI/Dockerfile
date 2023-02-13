FROM python:3.9
COPY requirements.txt /tmp
WORKDIR /tmp 
RUN pip install -r requirements.txt

WORKDIR /usr/app/src

COPY models ./models
COPY main.py Fraud.py ./

