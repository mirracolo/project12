from flask import Flask, request, render_template
import requests
from api import API_KEY

app = Flask(__name__)

BASE_URL = "http://dataservice.accuweather.com"

# Функция для оценки погодных условий
def evaluate_weather_conditions(min_temp, max_temp, wind_speed, precipitation_chance):
    if min_temp < 0 or max_temp > 35:
        return "Температура неблагоприятная!"
    if wind_speed > 50:
        return "Сильный ветер!"
    if precipitation_chance > 70:
        return "Ожидается дождь!"
    return "Погода хорошая."

# Функция для получения ключа местоположения по координатам
def fetch_location_key(latitude, longitude):
    url = f"{BASE_URL}/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={latitude}%2C{longitude}"
    try:
        response = requests.get(url)
        location_data = response.json()
        return location_data['Key']
    except Exception as e:
        return render_template('index.html', error="Не удалось получить ключ местоположения")

# Функция для получения погодных данных по ключу местоположения
def fetch_weather_info(location_key):
    url = f"{BASE_URL}/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&language=en-us&details=true&metric=true"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        return render_template('index.html', error="Не удалось получить данные о погоде")

# Главная страница приложения
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для получения прогноза погоды
@app.route('/weather', methods=['POST'])
def get_weather_forecast():
    start_lat = request.form['lat_st']
    start_lon = request.form['lon_st']
    end_lat = request.form['lat_end']
    end_lon = request.form['lon_end']

    # Проверка заполненности всех полей
    if not all([start_lat, start_lon, end_lat, end_lon]):
        return "Ошибка: Укажите все координаты!", 400

    # Получаем ключи местоположений для начальной и конечной точек
    start_location_key = fetch_location_key(start_lat, start_lon)
    if not start_location_key:
        return "Ошибка: Не удалось найти начальную точку!", 400

    end_location_key = fetch_location_key(end_lat, end_lon)
    if not end_location_key:
        return "Ошибка: Не удалось найти конечную точку!", 400

    # Получаем данные о погоде для обеих точек
    start_weather_data = fetch_weather_info(start_location_key)
    end_weather_data = fetch_weather_info(end_location_key)

    if not start_weather_data or not end_weather_data:
        return "Ошибка: Не удалось получить данные о погоде!", 400

    # Извлекаем необходимые данные о погоде для начальной точки
    start_forecast = start_weather_data['DailyForecasts'][0]
    max_temp_start = start_forecast['Temperature']['Maximum']['Value']
    min_temp_start = start_forecast['Temperature']['Minimum']['Value']
    wind_speed_start = start_forecast['Day']['Wind']['Speed']['Value']
    rain_chance_start = start_forecast['Day']['PrecipitationProbability']

    # Извлекаем необходимые данные о погоде для конечной точки
    end_forecast = end_weather_data['DailyForecasts'][0]
    max_temp_end = end_forecast['Temperature']['Maximum']['Value']
    min_temp_end = end_forecast['Temperature']['Minimum']['Value']
    wind_speed_end = end_forecast['Day']['Wind']['Speed']['Value']
    rain_chance_end = end_forecast['Day']['PrecipitationProbability']

    # Оцениваем погодные условия для обеих точек
    weather_report_start = evaluate_weather_conditions(min_temp_start, max_temp_start, wind_speed_start, rain_chance_start)
    weather_report_end = evaluate_weather_conditions(min_temp_end, max_temp_end, wind_speed_end, rain_chance_end)

    # Возвращаем результаты пользователю
    return f'''
        <h2>Прогноз для начальной точки:</h2>
        <p>{weather_report_start}</p>
        <h2>Прогноз для конечной точки:</h2>
        <p>{weather_report_end}</p>
        <a href="/">Назад</a>
    '''

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)