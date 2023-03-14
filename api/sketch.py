from fastapi import FastAPI
import sqlite3
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

app = FastAPI(
    title="BlazinglyFast - API",
    version="1.0.0"
)

favicon_path = 'favicon.png'

cache = []

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get("/latest")
@app.post("/latest/query")
async def weewx_datapoints(limit: int = 1):
    return datas_to_json(get_data_from_db(limit))

@app.get("/plot")
async def plotting():
    return []

def get_data_from_db(limit = 1):
    connection = sqlite3.connect("/var/lib/weewx/weewx.sdb")
    db = connection.cursor()

    sql = f"""
        SELECT
            DATETIME(dateTime, 'unixepoch') as 'Time',
            ROUND(appTemp,2) as 'Temp',
            ROUND(barometer, 2),
            ROUND(inHumidity, 2),
            ROUND(pressure, 2),
            CASE WHEN rain is NULL THEN 0 ELSE ROUND(rain, 2) END,
            ROUND(rainRate, 2),
            ROUND(windchill, 2),
            ROUND(windSpeed, 2),
            CASE WHEN windDir is NULL THEN 0 ELSE ROUND(windDir, 1) END
        FROM archive
        ORDER BY dateTime DESC
        LIMIT {limit}; 
    """
    db.execute(sql)
    data = db.fetchall()
    
    return data

def datas_to_json(data):
    return {
        "data" : [data_to_json(i) for i in data ]
    }

def data_to_json(data):
    return {
        "date": data[0],
        "temp": round((data[1] - 32.0) * (5/9), 1),
        "baro": data[2],
        "humi": data[3],
        "pres": data[4],
        "rain": data[5],
        "rate": data[6],
        "wind": data[7],
        "speed": data[8],
        "dir": data[9]
     }