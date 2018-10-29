single_run_image = healthstats
cron_image = healthstats-cron
cron_container = healthstats-cron

all: run

run:
	docker build -t $(single_run_image) .
	docker run --rm --env-file .env $(single_run_image)

cron:
	docker-compose up -d
