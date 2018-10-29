# healthstats-collector

Health stats collector downloads health data from garmin connect website, turn them into prometheus metrics,
and push the metrics to prometheus pushgateway, which exposes a `/metrics` endpoint, and can be scraped by
prometheus.

Grafana dashboard built from those metrics:

![healthstats-dashboard](https://user-images.githubusercontent.com/965430/47626245-4d101400-dae7-11e8-9279-43ab4bcd0803.png)

![activities-as-annotations](https://user-images.githubusercontent.com/965430/47626249-539e8b80-dae7-11e8-99ea-a1c80fe10e5d.png)

## Getting started

Very cool! What do I need to generate a pretty dashboard like that??

Glad you asked, you will need:

- garmin connect account
- promethues
- pushgateway
- grafana
- docker
- docker-compose

You will need to rename `.env.example` to `.env`, and fill in the actual values.

To run this tool, you have two options:

- single run: `make`
- cron job: `make cron`

PROFIT!
