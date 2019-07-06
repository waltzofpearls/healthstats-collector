import json
import logging
import os
import sys
import tempfile
import time

from pathlib import Path

from garmin_connect import GarminConnect
from grafana_api import GrafanaAPI
from prometheus_metrics import PrometheusMetrics


def main():
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format='%(asctime)s [%(name)s:%(levelname)s] %(message)s')
    logger = logging.getLogger()

    connect = GarminConnect(logger)
    metrics = PrometheusMetrics(logger)
    grafana = GrafanaAPI(logger)

    logger.info('Logging in to garmin connect ...')
    if connect.login() == False:
        logger.error('Failed to log into garmin connect')
        sys.exit(1)

    logger.info('Downloading summary data ...')
    data = connect.get_summary()
    logger.info('Generating resting heart rate, steps, floor and calorie metrics ...')
    metrics.summary(data)

    time.sleep(1)

    logger.info('Downloading weight data ...')
    data = connect.get_weight()
    logger.info('Generating weight metrics ...')
    metrics.weight(data)

    time.sleep(1)

    logger.info('Downloading sleep data ...')
    data = connect.get_sleep()
    logger.info('Generating sleep metrics ...')
    metrics.sleep(data)

    logger.info('Publishing metrics to Pushgateway ...')
    metrics.publish()

    time.sleep(1)

    logger.info('Downloading activities data ...')
    data = connect.get_activities()
    logger.info('Creating grafana annotations ...')
    grafana.activities_as_annotations(data)


if __name__ == '__main__':
    main()
