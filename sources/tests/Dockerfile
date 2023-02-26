FROM python:3.9
COPY requirements.txt /tmp
WORKDIR /tmp 
RUN pip install -r requirements.txt

WORKDIR /usr/app/src

COPY authentication/ ./authentication
COPY  datas/ ./datas 
COPY models_and_API/ ./models_and_API
COPY ./card_transdata.csv ./var/lib/mysql-files
# CMD ["uvicorn", "main_docker:app", "--host', "0.0.0.0", "--port", "8000"]
