import json

import pandas as pd


def filter_empties(data):
    """Metoda usuwa puste wpisy ze słownika"""
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
        data = filter_empties(data)
        dataFrame = pd.DataFrame.from_records(data)
    return dataFrame


def load_schedule(filename):
    """Wczytywanie rozkładów jazdy z pliku"""
    with open(filename) as file:
        data = json.load(file)
        data = filter_empties(data)
        dataFrame = pd.DataFrame.from_records(data)
    return dataFrame


def load_bus_positions(filename):
    """Wczytywanie pozycji autobusów z pliku"""
    with open(filename) as file:
        data = json.load(file)
        data = filter_empties(data)
        data = filter_different_dates(data, load_date_from_file(filename))
        dataFrame = pd.DataFrame.from_records(data)
        dataFrame = delete_duplicate_positions(dataFrame)
    return dataFrame


def load_stop_lines(filename):
    with open(filename) as file:
        data = json.load(file)
        stopsFrame = pd.DataFrame.from_records(data)
        return stopsFrame


def load_date_from_file(filename):
    return filename[-15:-5]
