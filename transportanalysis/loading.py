import json
import os
import time

import pandas as pd


def filter_nondict(data):
    """Metoda usuwa puste wpisy niebędące słownikami"""
    result = []
    for item in data:
        if type(item) is dict:
            result.append(item)
    return result


def delete_duplicate_positions(busFrame):
    """Metoda usuwa powtórzone lokalizacje autobusów
        oraz jeśli jest tylko jeden punkt związany z danym autobusem"""
    result = busFrame.drop_duplicates(["VehicleNumber", "Time", "Lat"])
    busGroupBy = result.groupby(result["VehicleNumber"]).filter(lambda x: len(x) > 1)["VehicleNumber"].tolist()
    result = result[result["VehicleNumber"].isin(busGroupBy)]
    return result


def filter_different_dates(data, file_date):
    result = []
    for position in data:
        if file_date in position["Time"]:
            result.append(position)
    return result


def load_stop_location(filename):
    """Wczytywanie rozkładów jazdy z pliku"""
    with open(filename) as file:
        data = json.load(file)
        data = filter_nondict(data)
        dataFrame = pd.DataFrame.from_records(data)
        return dataFrame


def load_schedule(filename):
    """Wczytywanie rozkładów jazdy z pliku"""
    with open(filename) as file:
        data = json.load(file)
        data = filter_nondict(data)
        dataFrame = pd.DataFrame.from_records(data)
        change_hours(dataFrame)
        return dataFrame


def load_bus_positions(filename):
    """Wczytywanie pozycji autobusów z pliku"""
    with open(filename) as file:
        data = json.load(file)
        data = filter_nondict(data)
        data = filter_different_dates(data, load_date_from_file(filename))
        dataFrame = pd.DataFrame.from_records(data)
        dataFrame = delete_duplicate_positions(dataFrame)
        return dataFrame


def load_bus_speeds(filename):
    """Wczytywanie pozycji autobusów z pliku z uwzględnieniem prędkości autobusów"""
    with open(filename) as file:
        data = json.load(file)
        dataFrame = pd.DataFrame.from_records(data)
        return dataFrame


def load_json(filename):
    with open(filename) as file:
        data = json.load(file)
        return data


def load_stop_lines(filename):
    with open(filename) as file:
        data = json.load(file)
        stopsFrame = pd.DataFrame.from_records(data)
        return stopsFrame


def load_date_from_file(filename):
    t = time.strptime(time.ctime(os.path.getmtime(filename)))
    return str(time.strftime("%Y-%m-%d",t))


def change_time_format(temp_time):
    time_list = temp_time.split(":")
    if int(time_list[0]) >= 24:
        time_list[0] = str(int(time_list[0]) - 24)
    return ":".join(time_list)


def change_hours(schedule):
    schedule["czas"] = schedule["czas"].apply(change_time_format)
    schedule["czas"] = pd.to_datetime(schedule["czas"], format="%H:%M:%S")


def find_latest_file(filepath, name):
    files = os.listdir(filepath)
    paths = []
    for basename in files:
        if name in basename:
            paths.append(os.path.join(filepath, basename))
    return max(paths, key=os.path.getctime)
