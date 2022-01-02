FROM python:3.7.12-slim-buster

RUN apt-get update \
 && apt-get -y install cron git nodejs \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade cloudscraper prometheus_client pytz requests

ADD crontab /etc/cron.d/healthstats
RUN chmod 0644 /etc/cron.d/healthstats \
 && crontab /etc/cron.d/healthstats

COPY . /healthstats
RUN chmod +x /healthstats/entrypoint.sh

ENTRYPOINT ["/healthstats/entrypoint.sh"]
CMD env - `cat $HOME/.env` python /healthstats/collector.py
