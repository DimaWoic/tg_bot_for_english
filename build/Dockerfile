FROM python:3.10.12-bullseye

RUN mkdir /home/bot && mkdir /home/bot/sqlite && mkdir /home/bot/methods
WORKDIR /home/bot
COPY build/requirements.txt .
COPY methods/tables.py methods
COPY main.py .
RUN pip install -r requirements.txt
ENV TOKEN=''

CMD python main.py
