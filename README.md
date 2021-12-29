# healthstats-collector

Health stats collector downloads health data from garmin connect website, turn them into prometheus metrics,
and push the metrics to prometheus pushgateway, which exposes a `/metrics` endpoint, and can be scraped by
prometheus.

Special thank you goes to [tcgoetz/GarminDB](https://github.com/tcgoetz/GarminDB). The garmin connect scraper
in this repo was largely inspired by GarminDB.

Grafana dashboard built from those metrics:

![healthstats-dashboard](https://user-images.githubusercontent.com/965430/47626245-4d101400-dae7-11e8-9279-43ab4bcd0803.png)

![activities-as-annotations](https://user-images.githubusercontent.com/965430/47626249-539e8b80-dae7-11e8-99ea-a1c80fe10e5d.png)

## Getting started

Very cool! What do I need to generate a pretty dashboard like that??

Glad you asked, you will need:

- garmin connect account
- prometheus
- pushgateway
- grafana
- docker
- docker-compose

You will need to rename `.env.example` to `.env`, and fill in the actual values.

To run this tool, you have two options:

- single run: `make`
- cron job: `make cron`

PROFIT!

## List of metrics

| Metric name | Description |
| ----------- | ----------- |
| `weight_total` | Body weight in KG |
| `weight_body_fat` | Body fat in % |
| `weight_bone_mass` | Bone mass in KG |
| `weight_bmi` | BMI |
| `weight_body_water` | Body water in % |
| `weight_muscle_mass` | Muscle mass in KG |
| `resting_heart_rate` | Resting heart rate |
| `heart_rate_resting` | Resting heart rate |
| `heart_rate_min` | Minimum heart rate |
| `heart_rate_max` | Maximum heart rate |
| `steps` | Total steps |
| `steps_daily_goal` | Daily step goal |
| `distance_meters` | Total distance in meters |
| `active_seconds` | Seconds in movement |
| `sedentary_seconds` | Seconds in sedentary position |
| `calories` | Total calories |
| `calories_active` | Active calories |
| `calories_resting` | Resting calories |
| `intensity_minutes_moderate` | Minutes in moderate intensity activities |
| `intensity_minutes_vigorous` | Minutes in vigorous intensity activities |
| `floors_ascended` | Floors ascended |
| `floors_ascended_meters` | Floors ascended in meters |
| `floors_descended` | Floors descended |
| `floors_descended_meters` | Floors descended in meters |
| `sleep_time_sec` | Total sleep time in seconds |
| `sleep_deep_sec` | Deep sleep time in seconds |
| `sleep_light_sec` | Light sleep time in seconds |
| `sleep_awake_sec` | Sleep awake time in seconds |
