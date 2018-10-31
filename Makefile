single_run_image = healthstats
cron_image = healthstats-cron
cron_container = healthstats-cron

all: run

mon:
	docker-compose up -d prometheus pushgateway grafana

run:
	docker build -t $(single_run_image) .
	docker run --rm --network="healthstats-collector_monitor-net" --env-file .env $(single_run_image)

cron:
	docker-compose up -d

clean:
	docker-compose down
