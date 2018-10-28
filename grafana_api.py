import datetime
import math
import os
import pytz
import requests
import traceback


class GrafanaAPI():
    def __init__(self, logger):
        self.logger = logger
        self.timezone = os.environ.get('TIMEZONE', 'UTC')
        self.api = os.environ.get('GRAFANA_API')
        self.api_key = os.environ.get('GRAFANA_API_KEY')

    def activities_as_annotations(self, activities):
        tz = pytz.timezone(self.timezone)
        utc = datetime.datetime.now()
        now = tz.fromutc(utc)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_from_midnight = (now - midnight).seconds

        # start from 1 hour ago and end at the current time
        from_time = now - datetime.timedelta(hours=1)
        to_time = now

        # when it's the first hour of the day, start from 2 hours ago
        # so we can also grab the activities from the last hour of yesterday
        if seconds_from_midnight <= 3600:
            from_time = now - datetime.timedelta(hours=2)

        for activity in activities:
            ts = math.floor(activity['beginTimestamp'] / 1000)
            utc = datetime.datetime.utcfromtimestamp(ts)
            duration = math.ceil(activity['duration'])
            delta = datetime.timedelta(seconds=duration)
            time = tz.fromutc(utc)
            time_end = time + delta
            if from_time < time <= to_time \
                or from_time < time_end <= to_time:
                self.annotation({
                    'time': int(time.timestamp() * 1000),
                    'timeEnd': int(time_end.timestamp() * 1000),
                    'isRegion': True,
                    'tags': ['healthstats'],
                    'text': '{} with time {}, average HR {}, and calories {}'.format(
                        activity['activityName'],
                        str(delta),
                        activity['averageHR'],
                        activity['calories']
                    )
                })

    def annotation(self, data):
        '''
        {
            "dashboardId":468,
            "panelId":1,
            "time":1507037197339,
            "isRegion":true,
            "timeEnd":1507180805056,
            "tags":["tag1","tag2"],
            "text":"Annotation Description"
        }
        '''
        try:
            response = requests.post(self.api + '/annotations', json=data, headers={
                'Authorization': 'Bearer {}'.format(self.api_key),
                'Context-Type': 'application/json'
            })
            self.logger.info(response.text)
        except Exception as e:
            self.logger.error(traceback.format_exc())
