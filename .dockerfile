# syntax=docker/dockerfile:1
FROM joyzoursky/python-chromedriver:latest
WORKDIR /app
COPY requirements.txt requirements.txt
COPY ./src/rewards_lambda.py rewards_lambda.py
COPY ./src/telegram-send.conf telegram-send.conf
COPY ./src/accounts.json accounts.json
RUN pip3 install -r requirements.txt
CMD [ "python", "rewards_lambda.py"]