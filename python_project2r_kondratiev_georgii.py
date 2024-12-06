#Библиотеки
from flask import Flask
import requests

#Общение с апишкой
api_key = 'wV5H0MQlbLQmiiZlDFz809FpAned4Rz7'
location_url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
forecast_url = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/"

def get_location_key(lat, lon):
    params = {
        'apikey': api_key,
        'q': f'{lat},{lon}'
    }
    response = requests.get(location_url, params=params)
    if response.status_code != 200:
        raise Exception(f'Error: {response.status_code}')
    location_data = response.json()
    return location_data['Key']

def get_weather(location_key):
    url = f'{forecast_url}{location_key}'
    params = {
        'apikey': api_key,
        'metric': True,
        'details': True
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f'Error: {response.status_code}')
    return response.json()


def check_bad_weather(t, h, w_s, p):
    feedback = []

    if (t > 27 or t < 3) and h >= 80:
        feedback.append(f'Неблагоприятная температура ({t} °C) и высокая влажность ({h}%)')
    elif t > 30 or t < 0:
        feedback.append(f'Неблагоприятная температура ({t} °C)')
    if w_s > 36:
        feedback.append(f'Высокая скорость ветра ({w_s} км/ч)')
    if p > 60:
        feedback.append(f'Высокая вероятность выпадения осадков ({p}%)')

    res = 'Погода благоприятная'
    if len(feedback) > 0:
        res = 'Погода неблагоприятная:'
        for i in feedback:
            res += f'\n{i}'
        return {'status': True, 'feedback': res}
    return {'status': False, 'feedback': res}
#проверка check_bad_weather
#print(check_bad_weather(-100, 100, 999, 100))
#print(check_bad_weather(5, 100, 10, 20))
#rint(check_bad_weather(500, 0, 0, 0))


#Проверка
lat, lon = 55.7558, 37.6173  #Москва
location_key = get_location_key(lat, lon)
data = get_weather(location_key)
tmp = data['DailyForecasts'][0]
temperature = data['DailyForecasts'][0]['Temperature']
temperature = (temperature['Minimum']['Value'] + temperature['Maximum']['Value'])/2
humidity = data['DailyForecasts'][0]['Day']['RelativeHumidity']['Average']
wind_speed = data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']
precipitation_probability = data['DailyForecasts'][0]['Day']['PrecipitationProbability']
print(check_bad_weather(temperature, humidity, wind_speed, precipitation_probability))

