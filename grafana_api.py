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
        duration = (now - midnight).seconds

        # start from 1 hour ago and end at the current time
        start = now - datetime.timedelta(hours=1)
        end = now

        # when it's the first hour of the day, start from 2 hours ago
        # so we can also grab the activities from the last hour of yesterday
        if duration <= 3600:
            start = now - datetime.timedelta(hours=2)

        for activity in activities:
            ts = math.floor(activity['beginTimestamp'] / 1000)
            utc = datetime.datetime.utcfromtimestamp(ts)
            time = tz.fromutc(utc)
            if time < start or time > end:
                continue
            self.annotation({
                'time': int(time.timestamp() * 1000),
                'timeEnd': math.ceil((time.timestamp() + activity['duration']) * 1000),
                'isRegion': True,
                'tags': ['healthstats'],
                'text': '{} with time {}, average HR {}, and calories {}'.format(
                    activity['activityName'],
                    str(datetime.timedelta(seconds=math.ceil(activity['duration']))),
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
