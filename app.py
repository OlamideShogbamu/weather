from flask import Flask, request, jsonify
import os
import json
import urllib.request

app = Flask(__name__)

API = os.getenv('KEY')
CountryCode = "NG"

def getLocation(CountryCode, city):
    searchaddress = f"http://dataservice.accuweather.com/locations/v1/cities/{CountryCode}/search?apikey={API}&q={city}&details=True"
    with urllib.request.urlopen(searchaddress) as response:
        data = json.loads(response.read().decode())
    location_key = data[0]['Key']
    return location_key

def getForecast(location_key):
    daily_forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API}&details=true"
    with urllib.request.urlopen(daily_forecast_url) as response:
        data = json.loads(response.read().decode())
    return data

@app.route('/weather/<city>', methods=['GET'])
def weather(city):
    city = city
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    try:
        key = getLocation(CountryCode, city)
        data = getForecast(key)

        daily_forecast = data['DailyForecasts'][0]
        weather_info = {
            'Date': daily_forecast['Date'],
            'Time': daily_forecast['Sun']['Rise'],
            'Temperature': {
                'Minimum': daily_forecast['Temperature']['Minimum']['Value'],
                'Maximum': daily_forecast['Temperature']['Maximum']['Value'],
                'Unit': daily_forecast['Temperature']['Maximum']['Unit']
            },
            'Rainfall': daily_forecast['Day']['Rain']['Value'],
            'ThunderstormProbability': daily_forecast['Day']['ThunderstormProbability']
        }

        # Convert to JSON format
        return jsonify(weather_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)