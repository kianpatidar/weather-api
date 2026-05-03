from flask import Flask, jsonify, request
import pandas as pd

# Import your existing pipeline functions
from task2 import (
    CITIES,
    fetch_weather, fetch_air_quality,
    normalise_weather, normalise_air_quality,
    merge
)

app = Flask(__name__)

#Task 1 — GET /cities
@app.route("/cities")
def list_cities():
    return jsonify ({"Cities" : list(CITIES.keys())})


#Task 2 — GET /snapshot
@app.route("/snapshot")
def full_snapshot():
    weather_data = []
    air_data = []

    #Loop over all cities
    for city, (lat,lon) in CITIES.items():
        weather_data.append(fetch_weather(city, lat, lon))
        air_data.append(fetch_air_quality(city, lat, lon))

    #Normalise both lists
    weather = [normalise_weather(w) for w in weather_data]
    air = [normalise_air_quality(c) for c in  air_data]

    # merge into a DataFrame
    df = merge(weather, air)

    #fix NaN for json
    df = df.where(pd.notnull(df), None)

    #Convert the DataFrame to a list of dicts
    result = df.to_dict(orient='records')

    return jsonify({"data": result})


#Task 3 — GET /snapshot/<city>
@app.route('/snapshot/<city>')
def city_snapshot(city):
    # normalise the input
    city_input = city.strip().lower()

    units = request.args.get('units', 'celsius')


    weather_data = []
    air_data = []
    #Loop over all cities
    for city1, (lat,lon) in CITIES.items():
        weather_data.append(fetch_weather(city1, lat, lon))
        air_data.append(fetch_air_quality(city1, lat, lon))

    #Normalise both lists
    weather = [normalise_weather(w) for w in weather_data]
    air = [normalise_air_quality(c) for c in  air_data]

    # merge into a DataFrame
    df = merge(weather, air)

    #lower the existing city
    df["city_existed"] = df["city"].str.lower()

    # check the condition for city
    if city_input not in  df["city_existed"].values:
         return jsonify({'error': 'City not found'}), 404 #error message with 404 code

    #pull the requested city
    df = df[df["city_existed"]==city_input]

    #convert to F
    if units != 'celsius':
        df["temperature_f"] = df["temperature_c"] * 9/5 + 32
        df.drop(columns = ['temperature_c'], inplace = True)


    #fix NaN for json
    df = df.where(pd.notnull(df), None)

    #Convert the DataFrame to a list of dicts
    result = df.to_dict(orient='records')

    return jsonify({"data": result})


#Task 4 — snapshot/<city>/aqi route
@app.route('/snapshot/<city>/aqi')
def city_aqi(city):
    city_input = city.strip().lower()

    weather_data = []
    air_data = []

    for city1, (lat, lon) in CITIES.items():
        weather_data.append(fetch_weather(city1, lat, lon))
        air_data.append(fetch_air_quality(city1, lat, lon))

    weather = [normalise_weather(w) for w in weather_data]
    air = [normalise_air_quality(c) for c in air_data]

    df = merge(weather, air)
    df["city_existed"] = df["city"].str.lower()

    if city_input not in df["city_existed"].values:
        return jsonify({"error": "City not found"}), 404

    df = df[df["city_existed"] == city_input]

    # 🧹 keep only AQI-related columns
    aqi_columns = [col for col in df.columns if "aqi" in col.lower() or "pm" in col.lower()]
    df = df[["city"] + aqi_columns]

    df = df.where(pd.notnull(df), None)

    result = df.to_dict(orient="records")
    return jsonify({"data": result})


@app.route("/")
def hello_world():
    return jsonify({"message": "Hello_world"})

if __name__ == '__main__':
    app.run(debug=True)
