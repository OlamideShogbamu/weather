from flask import Flask, request, jsonify
import os
import json
import urllib.request
from datetime import datetime

app = Flask(__name__)

API = os.getenv('KEY')
CountryCode = "NG"

# Convert the date string to a more readable format
def format_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    return date_obj.strftime('%dth of %B, %Y')

def getLocation(coordinate):
  searchaddress = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API}&q="+coordinate+"&details=True"
  with urllib.request.urlopen(searchaddress) as searchaddress:
    data = json.loads(searchaddress.read().decode())
  location_key = data['Key']
  return location_key


def getForecast(location_key):
    daily_forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}?apikey={API}&details=True"
    with urllib.request.urlopen(daily_forecast_url) as response:
        data = json.loads(response.read().decode())
    return data

@app.route('/weather/<coordinate>', methods=['GET'])
def weather(coordinate):
    coordinate = coordinate
    if not coordinate:
        return jsonify({"error": "coordinate is required"}), 400
    
    try:
        location_key = getLocation(coordinate)
        data = getForecast(location_key)

        daily_forecast = data['DailyForecasts'][0]

        min_temp_f = daily_forecast['Temperature']['Minimum']['Value']
        max_temp_f = daily_forecast['Temperature']['Maximum']['Value']
        # Convert Fahrenheit to Celsius
        min_temp_c = (min_temp_f - 32) * 5/9
        max_temp_c = (max_temp_f - 32) * 5/9
        avg_temp_c = round((min_temp_c + max_temp_c) / 2, 1)


        weather_info = {
            'Date': format_date(daily_forecast['Date']),
            'Temperature': {
                'Average': str(avg_temp_c),   # Converted to string
                'Unit': 'Celsius'  # Updated unit
            },
            'PrecipitationType': daily_forecast['Day']['PrecipitationType'] if 'PrecipitationType' in daily_forecast['Day'] else 'Rain',
            'Humidity': daily_forecast['Day']['RelativeHumidity']['Average'] if 'RelativeHumidity' in daily_forecast['Day'] and 'Average' in daily_forecast['Day']['RelativeHumidity'] else 0, 
            'Wind': {
                'Speed': daily_forecast['Day']['Wind']['Speed']['Value'],
                'Direction': daily_forecast['Day']['Wind']['Direction']['English']
            },
            'Rainfall': daily_forecast['Day']['Rain']['Value'],  # Assuming the key exists
            'ThunderstormProbability': daily_forecast['Day']['ThunderstormProbability']
        }
        

        # Convert to JSON format
        return jsonify(weather_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)