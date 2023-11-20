FROM python:3.10.8-alpine

ENV FLASK_APP igame.py
ENV FLASK_CONFIG docker

RUN adduser -D igame
USER igame

WORKDIR /home/igame

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY iGame app
COPY migrations migrations
COPY igame.py config.py boot.sh ./

EXPOSE 8000
ENTRYPOINT ["./boot.sh"]
