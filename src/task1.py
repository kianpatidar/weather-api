#Project 1: The Weather Pipeline
import requests
import json
import pandas as pd
import sys




#-------------------------------
#Task 1 — fetch_weather()
#-------------------------------

def fetch_weather(latitude, longitude):
    try:
        req= requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true")
        req.raise_for_status()
   
        data = req.json()
        weather_data = data.get("current_weather", {})
        return weather_data
    except requests.exceptions.RequestException as e:
        print("some error in fetching data", e)
        






#results = [fetch_weather(43.70455, -79.404625)] 


#-------------------------------
#Task 2 — transform()
#-------------------------------

#weather_data = [results]

#print(weather_data)

def transform(weather_data):
    df = pd.DataFrame([i for i in weather_data if i ])
    
    
    df["feel_cold"] = df["temperature"] <10
    df["feels_hot"] = df["temperature"] >25


    return df


#-------------------------------
#Task 3 — output()
#-------------------------------

def output(df):

    # Save to csv file
    df.to_csv(r"/Users/kiranpatidar/Desktop/Practice/LangGraph/Fast_Practice/docs/weather_output.csv", index = False)

    #coldest city
    coldest = df.loc[df["temperature"].idxmin()]
    print("coldest city: ", coldest)

    #average temperature
    avg_temp = df["temperature"].mean()
    print("Average_temperatur: ", avg_temp)

    #wind speed
    print("Wind Spped")
    print(df["windspeed"])


#-------------------------------
#Task 4 — take input from csv file
#-------------------------------
def read_coordinates(file_path):
    try:
        df=pd.read_csv(file_path)
        return df
    except Exception as e:
        print("Error reading CSV:", e)



if __name__ == "__main__":

#--------------------------------------------------------------
    #aruguments = sys.argv
    #latitude = aruguments[1]
    #longitude= aruguments[2]
    #weather_data=[fetch_weather(latitude, longitude)]
#---------------------------------------------------------------
    # cordinates = [
    # (43.7, -79.4),
    # (51.5, -0.1),
    # (35.7, 139.7),
    # ]
    # weather_data = [fetch_weather(latitude, longitude) for latitude, longitude in cordinates]

    # df = transform(weather_data)
    # print(df)

    # output(df)
#---------------------------------------------------------------

    file_path="/Users/kiranpatidar/Desktop/Practice/LangGraph/Fast_Practice/docs/data.csv"
    data_file = read_coordinates(file_path)

    weather_data = [fetch_weather(row["latitude"], row["longitude"]) for index, row in data_file.iterrows() ] 
    df = transform(weather_data)
    print(df)

    output(df)






