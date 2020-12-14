#!/bin/python3

from requests import get as getRequest

URLS = {
    "weather": "http://api.openweathermap.org/data/2.5/weather?",
    "forecast": "http://api.openweathermap.org/data/2.5/forecast?",
}
TEMP_0 = -273.15


class OpenWeather:
    def __init__(self, config):
        self._key = config["key"]
        self.location = config["location"]

    def _get_json(self, url):
        weather_request = URLS[url] + "appid=" + self._key + "&q=" + self.location
        try:
            weather_response = getRequest(weather_request)
            return weather_response.json()
        except:
            return {}

    def get_weather(self):
        weather = self._get_json("weather")
        try:
            temperature = "{:.0f}".format(weather["main"]["temp"] + TEMP_0, 0)
            icon = weather["weather"][0]["icon"]
            return temperature, icon
        except:
            return "", None

    def get_forecast(self):
        forecast = self._get_json("forecast")
        print(forecast)


if __name__ == "__main__":
    import json
    with open("config.json") as f:
        config = json.loads(f.read())
    open_weather = OpenWeather(config["open_weather"])
    print(open_weather.get_weather())
