FROM python:3.10

LABEL project="moeflow-backend"

COPY . /app
WORKDIR /app
EXPOSE 5000

RUN pip install -r requirements.txt
