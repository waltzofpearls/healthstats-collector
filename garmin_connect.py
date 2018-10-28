import cfscrape
import datetime
import json
import os
import pytz
import re
import requests
import traceback


class GarminConnect():
    base_url = "https://connect.garmin.com"

    sso_url = 'https://sso.garmin.com/sso'
    sso_login_url = sso_url + '/signin'
    login_url = base_url + "/en-US/signin"
    css_url = 'https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css'

    modern_url = base_url + '/modern'
    modern_proxy_url = modern_url + '/proxy'

    user_profile_url = modern_proxy_url + '/userprofile-service/userprofile'
    personal_info_url = user_profile_url + '/personal-information'
    wellness_url = modern_proxy_url + '/wellness-service/wellness'
    sleep_daily_url = wellness_url + '/dailySleepData'
    summary_url = modern_proxy_url + '/usersummary-service/usersummary/daily'
    activities_url = modern_proxy_url + '/activitylist-service/activities/search/activities'

    def __init__(self, logger):
        self.logger = logger
        self.session = cfscrape.create_scraper(
            sess=requests.session(),
            delay=15
        )
        self.username = os.environ.get('GARMIN_USERNAME')
        self.password = os.environ.get('GARMIN_PASSWORD')
        self.timezone = os.environ.get('TIMEZONE', 'UTC')
        self.localtime = self.to_localtime(datetime.datetime.now())
        self.formatted_date = self.localtime.strftime("%Y-%m-%d")

    def to_localtime(self, datetime_in_utc):
        return pytz.timezone(self.timezone).fromutc(datetime_in_utc)

    def get(self, url, params={}):
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response

    def post(self, url, params, data):
        response = self.session.post(url, params=params, data=data)
        response.raise_for_status()
        return response

    def get_json(self, page_html, key):
        found = re.search(key + r" = JSON.parse\(\"(.*)\"\);", page_html, re.M)
        if found:
            json_text = found.group(1).replace('\\"', '"')
            return json.loads(json_text)

    def login(self):
        params = {
            'service': self.modern_url,
            'webhost': self.base_url,
            'source': self.login_url,
            'redirectAfterAccountLoginUrl': self.modern_url,
            'redirectAfterAccountCreationUrl': self.modern_url,
            'gauthHost': self.sso_url,
            'locale': 'en_US',
            'id': 'gauth-widget',
            'cssUrl': self.css_url,
            'clientId': 'GarminConnect',
            'rememberMeShown': 'true',
            'rememberMeChecked': 'false',
            'createAccountShown': 'true',
            'openCreateAccount': 'false',
            'usernameShown': 'false',
            'displayNameShown': 'false',
            'consumeServiceTicket': 'false',
            'initialFocus': 'true',
            'embedWidget': 'false',
            'generateExtraServiceTicket': 'false'
        }
        self.get(self.sso_login_url, params)
        data = {
            'username': self.username,
            'password': self.password,
            'embed': 'true',
            'lt': 'e1s1',
            '_eventId': 'submit',
            'displayNameRequired': 'false'
        }
        response = self.post(self.sso_login_url, params, data)
        found = re.search(r"\?ticket=([\w-]*)", response.text, re.M)
        if not found:
            return False
        params = {'ticket' : found.group(1)}
        response = self.get(self.modern_url, params)
        self.user_prefs = self.get_json(response.text, 'VIEWER_USERPREFERENCES')
        self.display_name = self.user_prefs['displayName']
        self.english_units = (self.user_prefs['measurementSystem'] == 'statute_us')
        self.social_profile = self.get_json(response.text, 'VIEWER_SOCIAL_PROFILE')
        self.full_name = self.social_profile['fullName']
        return True

    def get_summary(self):
        '''
        [{
        	"userProfileId": 48251499,
        	"displayName": null,
        	"totalKilocalories": 2525.0,
        	"activeKilocalories": 71.0,
        	"bmrKilocalories": 2454.0,
        	"wellnessKilocalories": 2525.0,
        	"burnedKilocalories": null,
        	"consumedKilocalories": null,
        	"remainingKilocalories": 2525.0,
        	"totalSteps": 4136,
        	"netCalorieGoal": null,
        	"totalDistanceMeters": 3350,
        	"wellnessDistanceMeters": 3350,
        	"wellnessActiveKilocalories": 71.0,
        	"netRemainingKilocalories": 71.0,
        	"userDailySummaryId": 48251499,
        	"calendarDate": "2018-10-22",
        	"rule": {
        		"typeId": 4,
        		"typeKey": "groups"
        	},
        	"uuid": "a48067837f9c433484f3d3908ce8823f",
        	"dailyStepGoal": 5832,
        	"wellnessStartTimeGmt": "2018-10-22T07:00:00.0",
        	"wellnessStartTimeLocal": "2018-10-22T00:00:00.0",
        	"wellnessEndTimeGmt": "2018-10-23T07:00:00.0",
        	"wellnessEndTimeLocal": "2018-10-23T00:00:00.0",
        	"durationInMilliseconds": 86400000,
        	"wellnessDescription": null,
        	"highlyActiveSeconds": 155,
        	"activeSeconds": 2342,
        	"sedentarySeconds": 51683,
        	"sleepingSeconds": 32220,
        	"includesWellnessData": true,
        	"includesActivityData": false,
        	"includesCalorieConsumedData": false,
        	"privacyProtected": false,
        	"moderateIntensityMinutes": 0,
        	"vigorousIntensityMinutes": 0,
        	"floorsAscendedInMeters": 40.377,
        	"floorsDescendedInMeters": 22.309,
        	"floorsAscended": 13.24705,
        	"floorsDescended": 7.31923,
        	"intensityMinutesGoal": 150,
        	"userFloorsAscendedGoal": 10,
        	"minHeartRate": 42,
        	"maxHeartRate": 107,
        	"restingHeartRate": 58,
        	"lastSevenDaysAvgRestingHeartRate": 62,
        	"source": "GARMIN",
        	"averageStressLevel": null,
        	"maxStressLevel": null,
        	"stressDuration": null,
        	"restStressDuration": null,
        	"activityStressDuration": null,
        	"uncategorizedStressDuration": null,
        	"totalStressDuration": null,
        	"lowStressDuration": null,
        	"mediumStressDuration": null,
        	"highStressDuration": null,
        	"stressPercentage": null,
        	"restStressPercentage": null,
        	"activityStressPercentage": null,
        	"uncategorizedStressPercentage": null,
        	"lowStressPercentage": null,
        	"mediumStressPercentage": null,
        	"highStressPercentage": null,
        	"stressQualifier": null,
        	"measurableAwakeDuration": null,
        	"measurableAsleepDuration": null,
        	"lastSyncTimestampGMT": null,
        	"weight": 106490.0,
        	"bmi": 33.6,
        	"bodyFat": 33.81,
        	"bodyWater": 48.31,
        	"boneMass": 5989,
        	"muscleMass": 39830,
        	"physiqueRating": null,
        	"visceralFat": null,
        	"metabolicAge": null,
        	"caloricIntake": null,
        	"biometricsTimeLocal": "2018-10-22T12:31:16.0",
        	"biometricsTimeGmt": "2018-10-22T19:31:16.0",
        	"minAvgHeartRate": 43,
        	"maxAvgHeartRate": 103
        }]
        '''
        try:
            response = self.get(self.summary_url + '/' + self.display_name, {
                'calendarDate': self.formatted_date,
            })
            return response.json()
        except Exception as e:
            self.logger.error(traceback.format_exc())
        return {}


    def get_sleep(self):
        '''
        {'dailySleepDTO': {
	    	'sleepQualityTypePK': None,
	    	'remSleepSeconds': 0,
	    	'napTimeSeconds': 0,
	    	'autoSleepEndTimestampGMT': 1539874440000,
	    	'userProfilePK': 48251499,
	    	'sleepResultTypePK': None,
	    	'awakeSleepSeconds': 1500,
	    	'sleepEndTimestampGMT': 1539874440000,
	    	'sleepEndTimestampLocal': 1539849240000,
	    	'sleepStartTimestampGMT': 1539828300000,
	    	'autoSleepStartTimestampGMT': 1539828300000,
	    	'sleepStartTimestampLocal': 1539803100000,
	    	'unmeasurableSleepSeconds': 0,
	    	'calendarDate': '2018-10-18',
	    	'sleepTimeSeconds': 44640,
	    	'deepSleepSeconds': 22920,
	    	'sleepWindowConfirmationType': 'auto_confirmed_final',
	    	'lightSleepSeconds': 21720,
	    	'deviceRemCapable': False,
	    	'id': 1539828300000,
	    	'sleepWindowConfirmed': True
	    }}
        '''
        try:
            response = self.get(self.sleep_daily_url + '/' + self.display_name, {
                'date': self.formatted_date
            })
            data = response.json()
            if 'dailySleepDTO' in data:
                return data['dailySleepDTO']
            self.logger.info('no daily sleep data from garmin connect')
        except Exception as e:
            self.logger.error(traceback.format_exc())
        return {}

    def get_activities(self):
        try:
            response = self.get(self.activities_url, {
                'start': 0,
                'limit': 10
            })
            return response.json()
        except Exception as e:
            self.logger.error(traceback.format_exc())
        return []
