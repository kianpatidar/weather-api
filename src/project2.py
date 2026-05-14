from flask import Flask, jsonify, request
import pandas as pd
from database import db
from models import Snapshot
from datetime import datetime, timezone

# Import your existing pipeline functions
from task2 import (
    CITIES,
    fetch_weather, fetch_air_quality,
    normalise_weather, normalise_air_quality,
    merge
)

app = Flask(__name__)


# Point SQLAlchemy at a SQLite file in the project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect the db object to this app
db.init_app(app)

# Create the tables if they don't exist yet
with app.app_context():
    db.create_all()


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


    # --- NEW: save each row to the database ---
    fetched_at = datetime.now(timezone.utc)
 
    for row in df.to_dict(orient='records'):
        snapshot = Snapshot(
            fetched_at        = fetched_at,
            city              = row['city'],
            temperature_c     = row.get('temperature_c'),
            wind_speed_kmh    = row.get('wind_speed_kmh'),
            weather_code      = row.get('weather_code'),
            pm10              = row.get('pm10'),
            pm2_5             = row.get('pm2_5'),
            air_quality_index = row.get('air_quality_index'),
        )
        db.session.add(snapshot)
 
    db.session.commit()


    # --- existing return ---
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

#----------New endpoints--------
#Task 5a — GET /history
#--------------------------------

@app.route('/history')
def history():
    # Get the most recent row for each city
    # Strategy: query all rows, ordered newest first, deduplicate by city
    rows = (
        Snapshot.query
        .order_by(Snapshot.fetched_at.desc())
        .all()
    )
 
    # Keep only the first occurrence of each city (i.e. most recent)
    seen   = set()
    latest = []
    for row in rows:
        if row.city not in seen:
            seen.add(row.city)
            latest.append(row.to_dict())
 
    return jsonify({'data': latest, 'count': len(latest)})


def validate_city(city):

    city = city.strip().lower()

    valid_cities = [c.lower() for c in CITIES.keys()]

    if city not in valid_cities:
        return jsonify({
            "error": f"City '{city}' not supported"
        }), 404

    return None

def error_response(message, status_code):

    response = jsonify({
        "error": message
    })

    response.status_code = status_code

    return response

#----------New endpoints--------
#Task 5b — GET /history/<city>
#--------------------------------
@app.route('/history/<city>')
def city_history(city):
    err = validate_city(city)
    if err:
        return err
 
    rows = (
        Snapshot.query
        .filter(Snapshot.city.ilike(city))   # case-insensitive match
        .order_by(Snapshot.fetched_at.desc())
        .all()
    )
 
    if not rows:
        return error_response(
            f'No history found for {city.title()}. Try fetching /snapshot first.',
            404
        )
 
    return jsonify({
        'city':  city.title(),
        'count': len(rows),
        'data':  [r.to_dict() for r in rows]
    })

#----------New endpoints--------
#Task 5c — GET /history/<city>/summary
#--------------------------------
@app.route('/history/<city>/summary')
def city_summary(city):
    err = validate_city(city)
    if err:
        return err
 
    rows = (
        Snapshot.query
        .filter(Snapshot.city.ilike(city))
        .order_by(Snapshot.fetched_at.asc())
        .all()
    )
 
    if not rows:
        return error_response(
            f'No history found for {city.title()}.',
            404
        )
 
    # Extract non-None values for each metric
    temps = [r.temperature_c for r in rows if r.temperature_c is not None]
    aqis  = [r.air_quality_index for r in rows if r.air_quality_index is not None]
 
    summary = {
        'city':             city.title(),
        'total_readings':   len(rows),
        'first_fetched':    rows[0].fetched_at.isoformat(),
        'last_fetched':     rows[-1].fetched_at.isoformat(),
        'temperature_c': {
            'avg': round(sum(temps) / len(temps), 2) if temps else None,
            'min': min(temps) if temps else None,
            'max': max(temps) if temps else None,
        },
        'air_quality_index': {
            'avg': round(sum(aqis) / len(aqis), 2) if aqis else None,
            'min': min(aqis) if aqis else None,
            'max': max(aqis) if aqis else None,
        },
    }
 
    return jsonify(summary)



if __name__ == '__main__':
    app.run(debug=True)
        
 

