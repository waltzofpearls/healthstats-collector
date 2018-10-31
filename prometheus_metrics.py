import datetime
import os
import pytz

from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway


class PrometheusMetrics:
    def __init__(self, logger):
        self.logger = logger
        self.registry = CollectorRegistry()
        self.pushgateway = os.environ.get("PUSHGATEWAY", "localhost:9091")
        self.job_name = os.environ.get("JOB_NAME", "healthstats")
        self.timezone = os.environ.get("TIMEZONE", "UTC")

    def summary(self, data):
        self._weight(data)
        self._heart_rate(data)
        self._intensity_minutes(data)
        self._steps(data)
        self._floors(data)
        self._calories(data)

    def _weight(self, data):
        if (
            data.get("weight") is None
            or data.get("weight") == 0
            or data.get("bodyFat") is None
            or data.get("boneMass") is None
            or data.get("bmi") is None
            or data.get("bodyWater") is None
            or data.get("muscleMass") is None
        ):
            return

        # create metrics
        weight_total = self.gauge("weight_total", "Body weight in KG")
        weight_body_fat = self.gauge("weight_body_fat", "Body fat in %")
        weight_bone_mass = self.gauge("weight_bone_mass", "Bone mass in KG")
        weight_bmi = self.gauge("weight_bmi", "BMI")
        weight_body_water = self.gauge("weight_body_water", "Body water in %")
        weight_muscle_mass = self.gauge("weight_muscle_mass", "Muscle mass in KG")

        # set metrics values
        weight_total.set(data["weight"] / 1000.0)
        weight_body_fat.set(data["bodyFat"])
        weight_bone_mass.set(data["boneMass"] / 1000.0)
        weight_bmi.set(data["bmi"])
        weight_body_water.set(data["bodyWater"])
        weight_muscle_mass.set(data["muscleMass"] / 1000.0)

    def _heart_rate(self, data):
        if (
            data.get("restingHeartRate") is None
            or data.get("minHeartRate") is None
            or data.get("maxHeartRate") is None
        ):
            return

        # create metrics
        resting_heart_rate = self.gauge("resting_heart_rate", "Resting heart rate")
        heart_rate_resting = self.gauge("heart_rate_resting", "Resting heart rate")
        heart_rate_min = self.gauge("heart_rate_min", "Minimum heart rate")
        heart_rate_max = self.gauge("heart_rate_max", "Maximum heart rate")

        # set metrics values
        resting_heart_rate.set(data["restingHeartRate"])
        heart_rate_resting.set(data["restingHeartRate"])
        heart_rate_min.set(data["minHeartRate"])
        heart_rate_max.set(data["maxHeartRate"])

    def _steps(self, data):
        if (
            data.get("totalSteps") is None
            or data.get("dailyStepGoal") is None
            or data.get("totalDistanceMeters") is None
            or data.get("activeSeconds") is None
            or data.get("sedentarySeconds") is None
        ):
            return

        # create metrics
        steps = self.gauge("steps", "Total steps")
        steps_daily_goal = self.gauge("steps_daily_goal", "Daily step goal")
        distance_meters = self.gauge("distance_meters", "Total distance in meters")
        active_seconds = self.gauge("active_seconds", "Seconds in movement")
        sedentary_seconds = self.gauge(
            "sedentary_seconds", "Seconds in sedentary position"
        )

        # set metrics values
        steps.set(data["totalSteps"])
        steps_daily_goal.set(data["dailyStepGoal"])
        distance_meters.set(data["totalDistanceMeters"])
        active_seconds.set(data["activeSeconds"])
        sedentary_seconds.set(data["sedentarySeconds"])

    def _calories(self, data):
        if (
            data.get("totalKilocalories") is None
            or data.get("activeKilocalories") is None
            or data.get("bmrKilocalories") is None
        ):
            return

        # create metrics
        calories = self.gauge("calories", "Total calories")
        calories_active = self.gauge("calories_active", "Active calories")
        calories_resting = self.gauge("calories_resting", "Resting calories")

        # set metrics values
        calories.set(data["totalKilocalories"])
        calories_active.set(data["activeKilocalories"])
        calories_resting.set(data["bmrKilocalories"])

    def _intensity_minutes(self, data):
        if (
            data.get("moderateIntensityMinutes") is None
            or data.get("vigorousIntensityMinutes") is None
        ):
            return

        # create metrics
        intensity_minutes_moderate = self.gauge(
            "intensity_minutes_moderate", "Minutes in moderate intensity activities"
        )
        intensity_minutes_vigorous = self.gauge(
            "intensity_minutes_vigorous", "Minutes in vigorous intensity activities"
        )

        # set metrics values
        intensity_minutes_moderate.set(data["moderateIntensityMinutes"])
        intensity_minutes_vigorous.set(data["vigorousIntensityMinutes"])

    def _floors(self, data):
        if (
            data.get("floorsAscended") is None
            or data.get("floorsAscendedInMeters") is None
            or data.get("floorsDescended") is None
            or data.get("floorsDescendedInMeters") is None
        ):
            return

        # create metrics
        floors_ascended = self.gauge("floors_ascended", "Floors ascended")
        floors_ascended_meters = self.gauge(
            "floors_ascended_meters", "Floors ascended in meters"
        )
        floors_descended = self.gauge("floors_descended", "Floors descended")
        floors_descended_meters = self.gauge(
            "floors_descended_meters", "Floors descended in meters"
        )

        # set metrics values
        floors_ascended.set(data["floorsAscended"])
        floors_ascended_meters.set(data["floorsAscendedInMeters"])
        floors_descended.set(data["floorsDescended"])
        floors_descended_meters.set(data["floorsDescendedInMeters"])

    def sleep(self, data):
        utc = datetime.datetime.now()
        now = pytz.timezone(self.timezone).fromutc(utc)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        duration = (now - midnight).seconds

        if duration < 43200:
            # only sync when the day past 12 hours
            # 43200 = 3600 * 12
            return

        if (
            data.get("sleepTimeSeconds") is None
            or data.get("deepSleepSeconds") is None
            or data.get("lightSleepSeconds") is None
            or data.get("awakeSleepSeconds") is None
        ):
            return

        # create metrics
        sleep_time_sec = self.gauge("sleep_time_sec", "Total sleep time in seconds")
        sleep_deep_sec = self.gauge("sleep_deep_sec", "Deep sleep time in seconds")
        sleep_light_sec = self.gauge("sleep_light_sec", "Light sleep time in seconds")
        sleep_awake_sec = self.gauge("sleep_awake_sec", "Sleep awake time in seconds")

        # set metrics values
        sleep_time_sec.set(data["sleepTimeSeconds"])
        sleep_deep_sec.set(data["deepSleepSeconds"])
        sleep_light_sec.set(data["lightSleepSeconds"])
        sleep_awake_sec.set(data["awakeSleepSeconds"])

    def gauge(self, name, documentation):
        return Gauge(name, documentation, registry=self.registry)

    def publish(self):
        pushadd_to_gateway(self.pushgateway, job=self.job_name, registry=self.registry)
