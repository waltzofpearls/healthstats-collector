single_run_image = healthstats
cron_image = healthstats-cron
cron_container = healthstats-cron

all: run

mon:
	docker-compose up -d prometheus pushgateway grafana

run:
	docker build -t $(single_run_image) .
	docker run --rm \
		--name healthstats \
		--network="healthstats-collector_monitor-net" \
		--env-file .env \
		$(single_run_image)

cron:
	docker-compose up -d

off:
	docker-compose down

clean:
	docker-compose down
	docker volume rm healthstats-collector_grafana_data
	docker volume rm healthstats-collector_prometheus_data

dev:
	docker build -t $(single_run_image) .
	docker run -it --rm \
		--name healthstats \
		--env-file .env \
		-v $(PWD):/healthstats \
		-w /healthstats \
		$(single_run_image) /bin/bash
