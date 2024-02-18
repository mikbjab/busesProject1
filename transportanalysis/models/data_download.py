import copy
import datetime
import os
import requests
import json
import time
import pandas as pd


class DataRetrieval:
    apikey = "c2cc3730-aabd-482e-a16f-e911fd7439d2"

    @classmethod
    def delete_empties(cls, data):
        """Metoda usuwa puste wpisy ze słownika"""
        result = []
        for item in data:
            if type(item) is dict:
                result.append(item)
        return result

    @classmethod
    def delete_duplicate_positions(cls, busFrame):
        """Metoda usuwa powtórzone lokalizacje autobusów
        oraz jeśli jest tylko jeden punkt związany z danym autobusem"""
        result = busFrame.drop_duplicates(["VehicleNumber", "Time", "Lat"])
        busGroupBy = result.groupby(result["VehicleNumber"]).filter(lambda x: len(x) > 1)["VehicleNumber"].tolist()
        result = result[result["VehicleNumber"].isin(busGroupBy)]
        return result

    @classmethod
    def load_bus_positions(cls, filename):
        """Wczytywanie pozycji autobusów z pliku"""
        with open(filename) as file:
            data = json.load(file)
            data = cls.delete_empties(data)
            data = cls.delete_different_dates(data, filename[-15:-5])
            dataFrame = pd.DataFrame.from_records(data)
            dataFrame = cls.delete_duplicate_positions(dataFrame)
        return dataFrame

    @classmethod
    def collect_bus_location(cls, minutes):
        """Metoda zapisująca pozycje autobusów z czasu (minutes), pozycje są wczytywane co minutę"""
        result = []
        for i in range(minutes):
            response = requests.get(
                "https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=f2e5503e927d-4ad3-9500"
                "-4ab9e55deb59&apikey=" + cls.apikey + "&type=1")
            if response.status_code == 200:
                current_data = response.json()["result"]
                result.append(current_data)
            else:
                print(response)
            time.sleep(60)
        data = cls.delete_empties(result)

        # dane są zapisywane w folderze resources, który jest umieszczony w folderze z kodem źródłowym
        if not os.path.exists("../resources"):
            os.mkdir("../resources")
        with open("../resources/data" + datetime.datetime.now().strftime('_%d-%m-%Y.json'), "w") as file:
            json.dump(data, file)

        dataFrame = pd.DataFrame.from_records(data)
        return dataFrame

    @classmethod
    def collect_busstops_location(cls):
        """Metoda do zapisania lokalizacji wszystkich przystanków (słupków)"""
        response_stops_location = requests.get(
            "https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&apikey"
            "=" + cls.apikey)
        if response_stops_location.status_code == 200:
            stops_location = response_stops_location.json()["result"]
        else:
            print(response_stops_location)

        temp = []
        temp_dict = dict()
        for item in stops_location:
            list_of_attributes = item["values"]
            for attr in list_of_attributes:
                temp_dict[attr["key"]] = attr["value"]
            temp.append(copy.deepcopy(temp_dict))
            temp_dict = dict()

        if not os.path.exists("../resources"):
            os.mkdir("../resources")
        with open("resources/stops_locations" + datetime.datetime.now().strftime('_%d-%m-%Y.json'), "w") as file:
            json.dump(temp, file)
        dataFrame = pd.DataFrame.from_records(temp)
        return dataFrame

    @classmethod
    def load_stop_location(cls, filename):
        """Wczytywanie rozkładów jazdy z pliku"""
        with open(filename) as file:
            data = json.load(file)
            data = cls.delete_empties(data)
            dataFrame = pd.DataFrame.from_records(data)
        return dataFrame

    @classmethod
    def collect_lines_single(cls, zespol, slupek):
        """Metoda wczytująca z API linie przechodzące przez konkretny przystanek"""
        response_lines = requests.get(
            f"https://api.um.warszawa.pl/api/action/dbtimetable_get?id=88cd555f-6f31-43ca-9de4-66c479ad5942"
            f"&busstopId={zespol}&busstopNr={slupek}&apikey={cls.apikey}")
        if response_lines.status_code == 200:
            stop_lines = response_lines.json()["result"]
        else:
            print(response_lines)

        assert response_lines.status_code == 200
        result = []
        for line in stop_lines:
            result.append(line["values"][0]["value"])
        return result

    @classmethod
    def collect_lines_all(cls):
        """Metoda zapisująca linie autobusowe dla każdego przystanku"""
        with open("../resources/stops_locations_10-01-2024.json", "r") as file:
            data = json.load(file)
        dataFrame = pd.DataFrame.from_records(data)
        stops_lines = dataFrame[["zespol", "slupek"]]
        stops_lines["Linie"] = stops_lines.apply(lambda row: cls.collect_lines_single(row["zespol"], row["slupek"]),
                                                 axis=1)

        if not os.path.exists("../resources"):
            os.mkdir("../resources")
        stops_lines.to_json("resources/stops_lines" + datetime.datetime.now().strftime('_%d-%m-%Y.json'),
                            orient="columns")
        return stops_lines

    @classmethod
    def collect_schedule_single(cls, zespol, slupek, linie):
        """Metoda wczytująca rozkład dla konkretnego przystanku dla konkretnej linii"""
        response_lines = requests.get(
            f"https://api.um.warszawa.pl/api/action/dbtimetable_get/?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&busstopId={zespol}"
            f"&busstopNr={slupek}&line={linie}&apikey=c2cc3730-aabd-482e-a16f-e911fd7439d2")
        if response_lines.status_code == 200:
            stop_lines = response_lines.json()["result"]
            temp = []
            temp_dict = dict()
            for item in stop_lines:
                list_of_attributes = item["values"]
                for attr in list_of_attributes:
                    temp_dict[attr["key"]] = attr["value"]
                temp.append(copy.deepcopy(temp_dict))
                temp_dict = dict()
            scheduleFrame = pd.DataFrame.from_records(temp)
            scheduleFrame["zespol"] = zespol
            scheduleFrame["slupek"] = slupek
            scheduleFrame["linia"] = linie
            return scheduleFrame
        else:
            print(response_lines)

    @classmethod
    def collect_schedule_all(cls):
        with open("../resources/stops_lines_06-02-2024.json") as file:
            data = json.load(file)
            stopsFrame = pd.DataFrame.from_records(data)
            list_of_schedules = []
        counter = 0
        for index, record in stopsFrame.iterrows():
            counter += 1
            if counter % 100 == 0:
                print(counter)
            for line in record["Linie"]:
                list_of_schedules.append(cls.collect_schedule_single(record["zespol"], record["slupek"], line))
        all_schedules = pd.concat(list_of_schedules, ignore_index=True)
        if not os.path.exists("../resources"):
            os.mkdir("../resources")
        all_schedules.to_json("../resources/schedules" + datetime.datetime.now().strftime('_%d-%m-%Y.json'),
                              orient="records")
        return all_schedules

    @classmethod
    def load_schedule(cls, filename):
        """Wczytywanie rozkładów jazdy z pliku"""
        with open(filename) as file:
            data = json.load(file)
            data = cls.delete_empties(data)
            dataFrame = pd.DataFrame.from_records(data)
        return dataFrame

    @classmethod
    def delete_different_dates(cls, data, file_date):
        result=[]
        for position in data:
            if file_date in position["Time"]:
                result.append(position)
        return result


if __name__ == '__main__':
    print(DataRetrieval.collect_schedule_all())