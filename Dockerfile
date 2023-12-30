FROM python:3.10

LABEL project="moeflow-backend"

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
EXPOSE 5000
RUN pip install --no-deps -r /app/requirements.txt

COPY . /app
