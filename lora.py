#!/usr/bin/env python3
"""
    Test harness for dragino module - sends hello world out over LoRaWAN 5 times
"""
import logging
import json
from datetime import datetime
from time import sleep
import RPi.GPIO as GPIO
from dragino import Dragino
import sqlite3
from sys import argv

def main(): 
    send_to_gateway()
   

def data_to_json(data):
    return {
        "date": data[0],
        "temp": data[1],
        "baro": data[2],
        "humi": data[3],
        "pres": data[4],
        "rain": data[5],
        "rate": data[6],
        "wind": data[7],
        "speed": data[8],
        "dir": data[9]
     }

def get_data_from_db():
    connection = sqlite3.connect("/var/lib/weewx/weewx.sdb")
    db = connection.cursor()

    sql = """
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
        LIMIT 1; 
    """

    db.execute(sql)
    data = db.fetchall()
    
    return data


def send_to_gateway():
    GPIO.setwarnings(False)

    # add logfile
    logLevel=logging.DEBUG
    logging.basicConfig(filename="test.log", format='%(asctime)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s', level=logLevel)


    D = Dragino("dragino.ini", logging_level=logLevel)
    D.join()
    while not D.registered():
        print("Waiting for JOIN ACCEPT")
        sleep(5 * 60)
    # for i in range(0, 2):
    while True:
        raw = get_data_from_db()
        dct = data_to_json(raw[0])
        data = json.dumps(dct, indent=2)
        print(json.dumps(dct, indent=2))
        D.send(data)
        start = datetime.utcnow()
        while D.transmitting:
            pass
        end = datetime.utcnow()
        print(f"Sent payload message (Time: {end})")
        sleep(10)
        
if __name__ == "__main__":
    main()
