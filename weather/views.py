import requests
from datetime import datetime

from django.shortcuts import render


def get_background_class(weather_main):
    """Return a background CSS class based on weather condition."""
    weather_main = weather_main.lower()

    if 'clear' in weather_main:
        return 'clear-bg'
    if 'cloud' in weather_main:
        return 'cloud-bg'
    if 'rain' in weather_main or 'drizzle' in weather_main:
        return 'rain-bg'
    if 'thunderstorm' in weather_main:
        return 'storm-bg'
    if 'snow' in weather_main:
        return 'snow-bg'
    if 'mist' in weather_main or 'fog' in weather_main or 'haze' in weather_main:
        return 'mist-bg'
    return 'default-bg'


def get_weather_emoji(weather_main):
    """Return an emoji icon based on weather condition."""
    weather_main = weather_main.lower()

    if 'clear' in weather_main:
        return '☀️'
    if 'cloud' in weather_main:
        return '☁️'
    if 'rain' in weather_main or 'drizzle' in weather_main:
        return '🌧️'
    if 'thunderstorm' in weather_main:
        return '⛈️'
    if 'snow' in weather_main:
        return '❄️'
    if 'mist' in weather_main or 'fog' in weather_main or 'haze' in weather_main:
        return '🌫️'
    return '🌤️'


def generate_ai_summary(weather):
    """Generate a simple AI-style weather summary."""
    temp = weather['temperature']
    description = weather['description'].lower()
    humidity = weather['humidity']
    wind = weather['wind']
    city = weather['city']

    temperature_advice = ''
    clothing_advice = ''
    activity_advice = ''
    wind_advice = ''
    humidity_advice = ''

    if temp >= 30:
        temperature_advice = 'It is very hot today.'
        clothing_advice = 'Wear light clothing and stay hydrated.'
    elif temp >= 22:
        temperature_advice = 'It is warm and comfortable.'
        clothing_advice = 'Light clothing should work well.'
    elif temp >= 15:
        temperature_advice = 'The temperature is mild.'
        clothing_advice = 'A light jersey or normal daywear should be fine.'
    elif temp >= 8:
        temperature_advice = 'It is fairly cool today.'
        clothing_advice = 'A jacket or warm layer is a good idea.'
    else:
        temperature_advice = 'It is quite cold today.'
        clothing_advice = 'Dress warmly and consider a heavier jacket.'

    if 'rain' in description or 'drizzle' in description:
        activity_advice = 'Take an umbrella because rain is likely.'
    elif 'thunderstorm' in description:
        activity_advice = 'Try to avoid unnecessary outdoor activity due to storm risk.'
    elif 'snow' in description:
        activity_advice = 'Take care outside because snowy conditions may affect movement.'
    elif 'clear' in description:
        activity_advice = 'Good conditions overall for outdoor activity.'
    elif 'cloud' in description:
        activity_advice = 'A decent day overall, though skies will stay cloudy.'
    else:
        activity_advice = 'Conditions look manageable overall.'

    if wind >= 10:
        wind_advice = 'Winds are quite strong.'
    elif wind >= 5:
        wind_advice = 'There is a noticeable breeze.'
    else:
        wind_advice = 'Winds are light.'

    if humidity >= 85:
        humidity_advice = 'Humidity is very high, so it may feel heavier than the actual temperature.'
    elif humidity >= 60:
        humidity_advice = 'Humidity is moderate.'
    else:
        humidity_advice = 'The air is fairly dry and comfortable.'

    return (
        f'{city} is currently experiencing {weather["description"]} with a '
        f'temperature of {temp}°C. {temperature_advice} {clothing_advice} '
        f'{wind_advice} {humidity_advice} {activity_advice}'
    )


def home(request):
    """Render home page with current weather, AI summary, and daily forecast."""

    current_weather = None
    forecast_list = []
    ai_summary = None
    error_message = None

    if request.method == 'POST':
        city = request.POST.get('city')

        if city:
            api_key = '037290af282c913bdefdedc3b673df98'

            current_url = (
                f'https://api.openweathermap.org/data/2.5/weather'
                f'?q={city}&appid={api_key}&units=metric'
            )

            forecast_url = (
                f'https://api.openweathermap.org/data/2.5/forecast'
                f'?q={city}&appid={api_key}&units=metric'
            )

            try:
                current_response = requests.get(current_url, timeout=10)
                forecast_response = requests.get(forecast_url, timeout=10)

                current_data = current_response.json()
                forecast_data = forecast_response.json()

                if current_data.get('cod') == 200:
                    weather_main = current_data['weather'][0]['main']
                    description = current_data['weather'][0]['description']

                    current_weather = {
                        'city': current_data['name'],
                        'temperature': round(current_data['main']['temp'], 1),
                        'description': description,
                        'humidity': current_data['main']['humidity'],
                        'wind': round(current_data['wind']['speed'], 2),
                        'feels_like': round(current_data['main']['feels_like'], 1),
                        'temp_min': round(current_data['main']['temp_min'], 1),
                        'temp_max': round(current_data['main']['temp_max'], 1),
                        'background_class': get_background_class(weather_main),
                        'emoji_icon': get_weather_emoji(weather_main),
                    }

                    ai_summary = generate_ai_summary(current_weather)

                    if forecast_data.get('cod') == '200':
                        daily_forecasts = {}

                        for item in forecast_data['list']:
                            date_obj = datetime.strptime(
                                item['dt_txt'],
                                '%Y-%m-%d %H:%M:%S'
                            )
                            day_key = date_obj.strftime('%Y-%m-%d')
                            hour = date_obj.hour
                            forecast_main = item['weather'][0]['main']

                            if day_key not in daily_forecasts and hour == 12:
                                daily_forecasts[day_key] = {
                                    'day_name': date_obj.strftime('%a'),
                                    'date_display': date_obj.strftime('%d %b'),
                                    'temperature': round(item['main']['temp'], 1),
                                    'description': item['weather'][0]['description'],
                                    'emoji_icon': get_weather_emoji(forecast_main),
                                }

                        if len(daily_forecasts) < 5:
                            for item in forecast_data['list']:
                                date_obj = datetime.strptime(
                                    item['dt_txt'],
                                    '%Y-%m-%d %H:%M:%S'
                                )
                                day_key = date_obj.strftime('%Y-%m-%d')
                                forecast_main = item['weather'][0]['main']

                                if day_key not in daily_forecasts:
                                    daily_forecasts[day_key] = {
                                        'day_name': date_obj.strftime('%a'),
                                        'date_display': date_obj.strftime('%d %b'),
                                        'temperature': round(item['main']['temp'], 1),
                                        'description': item['weather'][0]['description'],
                                        'emoji_icon': get_weather_emoji(forecast_main),
                                    }

                                if len(daily_forecasts) == 5:
                                    break

                        forecast_list = list(daily_forecasts.values())[:5]
                else:
                    error_message = 'City not found. Please enter a valid city name.'

            except requests.RequestException:
                error_message = (
                    'Unable to fetch weather data right now. Please try again.'
                )

    context = {
        'weather': current_weather,
        'forecast_list': forecast_list,
        'ai_summary': ai_summary,
        'error_message': error_message,
    }

    return render(request, 'weather/home.html', context)