#Project 2: The City Snapshot
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime


CITIES = {
    "Toronto": (43.7, -79.4),
    "London": (51.5, -0.1),
    "Tokyo": (35.7, 139.7),
    "Paris": (48.85, 2.35)
}

# def get_data_by_coords(url, lat, lon):
#     try:
#         req=requests.


#-------------------------------
#Task 1a — fetch_weather()
#-------------------------------

def fetch_weather(city, lat, lon):
    try:
        req1=requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
        req1.raise_for_status()

        data1 = req1.json()

        weather_data = data1.get("current_weather", {})

        weather_data["city"]=city

        return weather_data
    
    except requests.exceptions.RequestException as e:
        print("some error in fetching data", e)

#-------------------------------
#Task 1b — fetch_air_quality()
#-------------------------------

def fetch_air_quality(city, lat, lon):
    try:
        req2=requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm10,pm2_5,european_aqi")
        req2.raise_for_status()

        data2 = req2.json()

        current_data= data2.get("current", {})

        current_data["city"] = city
        return current_data
    except requests.exceptions.RequestException as e:
        print("some error in fetching data", e)


#-------------------------------
#Task 2a — normalise_weather()
#-------------------------------

def normalise_weather(weather_data):
    if weather_data is None:
        return None
    else:
        weather ={
        "city" : weather_data.get("city"),
        "temperature_c" : weather_data.get("temperature"),
         "wind_speed_kmh" : weather_data.get("windspeed"),
         "weather_code": weather_data.get("weathercode")
        }
    return weather

#-------------------------------
#Task 2b — normalise_air_quality()
#-------------------------------

def normalise_air_quality(current_data):
    if current_data is None:
        return None
    else:
        air = {
        "city" : current_data.get("city"),
        "pm10" : current_data.get("pm10"),
         "pm2_5" : current_data.get("pm2_5"),
         "air_quality_index": current_data.get("european_aqi")
        }
    return air

#-------------------------------
#Task 3 — merge()
#-------------------------------

def merge(weather, air):
    weather_df = pd.DataFrame([i for i in weather if i is not None])
    air_df = pd.DataFrame([i for i in air if i is not None])

    merge_df = pd.merge(weather_df, air_df, on = 'city', how = 'left')


    merge_df['aqi_label'] = np.where(merge_df['air_quality_index'] <=20, 'Good',
                            np.where(merge_df['air_quality_index'] <=40, 'Fair', "Poor"))


    merge_df['time_stamp'] = datetime.utcnow()

    return merge_df

    
#-------------------------------
#Task 4 — output()
#-------------------------------

def output(merge_df):

    # Save to csv file
    merge_df.to_csv(r"/Users/kiranpatidar/Desktop/Practice/LangGraph/Fast_Practice/docs/task2.csv", index = False)

    #The city with the worst air quality (highest european_aqi)
    worst_air_quality = merge_df.loc[merge_df['air_quality_index'].idxmax()]
    print("The city with worst air quality: ", worst_air_quality['city'])

    #The city with the highest wind speed
    wind_speed = merge_df.loc[merge_df['wind_speed_kmh'].idxmax()]
    print("The city with worst air quality: ", wind_speed['city'])

    #How many cities had complete data vs partial data (NaN in air quality columns)
    partial_data = merge_df[merge_df[['pm10', 'pm2_5', 'air_quality_index']].isna().any(axis=1)]
    complete_data = merge_df[merge_df[['pm10', 'pm2_5', 'air_quality_index']].notna().all(axis=1)]

    print(f"Partial Data cities length: {len(partial_data)}")
    print(f"Complete Data cities length: {len(complete_data)}")
                                     

if __name__ == "__main__":

    # cordinates = [
    # ('Toronto', 43.7, -79.4),
    # ('London', 51.5, -0.1),
    # ('Tokyo', 35.7, 139.7),
    # ('Paris', 48.85, 2.35),
    # ]

    cordinates = [(city,lat,lon) for city, (lat,lon) in CITIES.items()]

    weather_data = [fetch_weather(city, lat, lon) for city, lat, lon in cordinates]
    current_data = [fetch_air_quality(city, lat, lon) for city, lat, lon in cordinates]

  
    weather = [normalise_weather(w) for w in weather_data]
    print("DF1: ",weather)

    air = [normalise_air_quality(c) for c in current_data]
    print("DF2: ",air)

    merge_df = merge(weather, air)

    print("Merge_DF", "\n")
    print(merge_df)

    output(merge_df)



