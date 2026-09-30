import datetime
import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from tools import print_data
from weather import Flag, get_forecast


FORECAST_PAGE = b"""<html><body>
<script>var unused = 0;</script>
<script>var day = [{"time": 1609459200, "temperature": 5, "summary": "Cloudy", "windGust": 8, "windSpeed": 6, "humidity": 0.7, "dewPoint": 1, "pressure": 1008}];</script>
<script>
var currently = {"time": 1609459200, "temperature": 70.2, "summary": "Clear", "windGust": 1, "windSpeed": 2, "humidity": 0.5, "dewPoint": 50, "pressure": 1012};
var hours = [{"time": 1609459200, "temperature": 10, "summary": "Clear", "windGust": 3, "windSpeed": 4, "humidity": 0.4, "dewPoint": 3, "pressure": 1000}];
</script>
</body></html>"""


class TestForecastParsing(unittest.TestCase):
    def _response(self):
        response = Mock()
        response.content = FORECAST_PAGE
        return response

    def test_flag_values(self):
        self.assertEqual(Flag.HOURLY.value, 'hourly')
        self.assertEqual(Flag.CURRENTLY.value, 'currently')
        self.assertEqual(Flag.DAY_DETAILS.value, 'day_details')

    def test_hourly_parses_embedded_script(self):
        with patch('weather.requests.get', return_value=self._response()) as get:
            forecast = get_forecast(40.64, 22.94, Flag.HOURLY)

        get.assert_called_once_with('https://darksky.net/forecast/40.64,22.94/ca12/en')
        self.assertEqual(forecast[0]['temperature'], 10)
        self.assertEqual(forecast[0]['summary'], 'Clear')

    def test_currently_parses_embedded_script(self):
        with patch('weather.requests.get', return_value=self._response()):
            forecast = get_forecast(40.64, 22.94, Flag.CURRENTLY)

        self.assertEqual(forecast['summary'], 'Clear')
        self.assertEqual(forecast['temperature'], 70.2)

    def test_day_details_parses_embedded_script(self):
        with patch('weather.requests.get', return_value=self._response()) as get:
            forecast = get_forecast(40.64, 22.94, Flag.DAY_DETAILS, '2021-02-08')

        get.assert_called_once_with(
            'https://darksky.net/details/40.64,22.94/2021-02-08/ca12/en'
        )
        self.assertEqual(forecast[0]['temperature'], 5)
        self.assertEqual(forecast[0]['summary'], 'Cloudy')


class TestPrintData(unittest.TestCase):
    def setUp(self):
        self._previous = os.environ.get('LOCATION')
        os.environ['LOCATION'] = 'Thessaloniki, Greece'

    def tearDown(self):
        if self._previous is None:
            os.environ.pop('LOCATION', None)
        else:
            os.environ['LOCATION'] = self._previous

    def test_list_forecast_uses_reported_temperature(self):
        sample = [{
            'time': 1609459200,
            'temperature': 10,
            'windGust': 3,
            'windSpeed': 4,
            'humidity': 0.4,
            'dewPoint': 3,
            'summary': 'Clear',
            'pressure': 1000,
        }]
        stamp = datetime.datetime.fromtimestamp(sample[0]['time']).strftime('%d/%m/%Y %H:%M')
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_data(sample)
        text = buffer.getvalue()
        self.assertIn(f'Thessaloniki at {stamp}', text)
        self.assertIn('Temperature: 10', text)
        self.assertIn('Humidity: 40.0 %', text)

    def test_dict_forecast_converts_fahrenheit_to_celsius(self):
        sample = {
            'time': 1609459200,
            'temperature': 70.2,
            'windGust': 1,
            'windSpeed': 2,
            'humidity': 0.5,
            'dewPoint': 50,
            'summary': 'Clear',
            'pressure': 1012,
        }
        stamp = datetime.date.fromtimestamp(sample['time']).strftime('%d/%m/%Y')
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_data(sample)
        text = buffer.getvalue()
        self.assertIn(f'Thessaloniki at {stamp}', text)
        self.assertIn('Temperature: 21', text)
        self.assertIn('Dew point: 10', text)


if __name__ == '__main__':
    unittest.main()
