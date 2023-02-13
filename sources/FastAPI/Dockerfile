FROM python:3.9
COPY requirements.txt /tmp
WORKDIR /tmp 
RUN pip install -r requirements.txt

WORKDIR /usr/app/src
EXPOSE 8000
COPY models ./models
COPY main_docker.py Fraud_docker.py ./

CMD ["uvicorn", "main_docker:app", "--host', "0.0.0.0", "--port", "8000"]
