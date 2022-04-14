FROM python:3.9-alpine

RUN mkdir -p /discordbot
WORKDIR /discordbot/

COPY . .

RUN apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev git
RUN pip install -U git+https://github.com/Rapptz/discord.py 
RUN pip install -r /discordbot/requirements.txt

CMD ["python3", "src/main.py"]
