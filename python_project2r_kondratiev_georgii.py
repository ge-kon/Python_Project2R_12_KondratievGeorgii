from flask import Flask, render_template, request
import requests

app = Flask(__name__)

#для общения с api
api_key = 'CrU7fid7K598iH1ns9qJo3IBrLII53Wl'
forecast_url = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/'
location_city_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
location_xy_url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'

#получаем key по координатам
def get_location_key(lat, lon):
    params = {
        'apikey': api_key,
        'q': f'{lat},{lon}'
    }
    response = requests.get(location_xy_url, params=params)
    if response.status_code != 200:
        print(response.status_code)
        raise Exception(f'{response.status_code}')
    location_data = response.json()
    return location_data['Key']

#получаем key по названию
def get_city_key(city):
    params = {
        'apikey': api_key,
        'q': city
    }
    response = requests.get(location_city_url, params=params)
    if response.status_code != 200:
        print(response.status_code)
        raise Exception(f'{response.status_code}')
    location_data = response.json()
    if not location_data:
        print('Город не найден.')
        raise Exception('Город не найден.')
    return location_data[0]['Key']

#получаем всё о погоде
def get_weather(location_key):
    url = f'{forecast_url}{location_key}'
    params = {
        'apikey': api_key,
        'metric': True,
        'details': True
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(response.status_code)
        raise Exception(f'{response.status_code}')
    return response.json()

#проверяем погоду на благоприятность
def check_bad_weather(t, h, w_s, p):
    feedback = []
    if (t > 27 or t < 3) and h >= 80:
        feedback.append(f'неблагоприятная температура ({t} °C) и высокая влажность ({h}%)')
    elif t > 30 or t < 0:
        feedback.append(f'неблагоприятная температура ({t} °C)')
    if w_s > 36:
        feedback.append(f'высокая скорость ветра ({w_s} км/ч)')
    if p > 60:
        feedback.append(f'высокая вероятность выпадения осадков ({p}%)')

    res = 'Погода благоприятная'
    if len(feedback) > 0:
        res = 'Погода неблагоприятная: ' + ', '.join(feedback)
        return {'status': True, 'feedback': res}
    return {'status': False, 'feedback': res}
#проверка check_bad_weather
#print(check_bad_weather(-100, 100, 999, 100))
#print(check_bad_weather(5, 100, 10, 20))
#rint(check_bad_weather(500, 0, 0, 0))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_point = request.form.get('start_point')
        end_point = request.form.get('end_point')
        try:
            if ',' in start_point:
                lat, lon = map(float, start_point.split(','))
                key = get_location_key(lat, lon)
            else:
                key = get_city_key(start_point)

            data = get_weather(key)
            temperature = data['DailyForecasts'][0]['Temperature']
            temperature = (temperature['Minimum']['Value'] + temperature['Maximum']['Value']) / 2
            humidity = data['DailyForecasts'][0]['Day']['RelativeHumidity']['Average']
            wind_speed = data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']
            precipitation_probability = data['DailyForecasts'][0]['Day']['PrecipitationProbability']
            start = check_bad_weather(temperature, humidity, wind_speed, precipitation_probability)

            if ',' in end_point:
                lat, lon = map(float, end_point.split(','))
                key = get_location_key(lat, lon)
            else:
                key = get_city_key(end_point)

            data = get_weather(key)
            temperature = data['DailyForecasts'][0]['Temperature']
            temperature = (temperature['Minimum']['Value'] + temperature['Maximum']['Value']) / 2
            humidity = data['DailyForecasts'][0]['Day']['RelativeHumidity']['Average']
            wind_speed = data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']
            precipitation_probability = data['DailyForecasts'][0]['Day']['PrecipitationProbability']
            end = check_bad_weather(temperature, humidity, wind_speed, precipitation_probability)

            #print(start, '\n', end) #просмотр погоды
            return render_template('result.html', start=start['feedback'], end=end['feedback'])

        except Exception as e:
            return render_template('error.html', error=f'{e}')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)