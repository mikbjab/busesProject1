import copy
import datetime
import os
import requests
import json
import time
import pandas as pd
import logging
from os.path import join
from dotenv import load_dotenv
from pathlib import Path

import loading

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

dotenv_path = join(Path(__file__).parent.parent, '.env')
load_dotenv(dotenv_path)


class DataRetrieval:
    apikey = os.environ.get("API_KEY")
    project_path = Path(__file__).parent.parent

    @classmethod
    def collect_bus_location(cls, minutes):
        """Metoda zapisująca pozycje autobusów z czasu (minutes), pozycje są wczytywane co minutę"""
        result = []
        for i in range(minutes):
            response = requests.get(
                f"https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=f2e5503e927d-4ad3-9500"
                f"-4ab9e55deb59&apikey={cls.apikey}&type=1")
            if response.status_code == 200:
                current_data = response.json()["result"]
                result.append(current_data)
            else:
                logging.info(response)
            time.sleep(60)

        data_path = cls.project_path.joinpath("data")
        if not data_path.exists():
            data_path.mkdir()
        with open(data_path.joinpath(f"data{datetime.datetime.now().strftime('_%Y-%m-%d.json')}"), "w") as file:
            json.dump(result, file)

    @classmethod
    def collect_busstops_location(cls):
        """Metoda do zapisania lokalizacji wszystkich przystanków (słupków)"""
        print(cls.apikey)
        response_stops_location = requests.get(
            f"https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&apikey"
            f"={cls.apikey}")
        if response_stops_location.status_code == 200:
            stops_location = response_stops_location.json()["result"]
            temp = []
            temp_dict = dict()
            for item in stops_location:
                list_of_attributes = item["values"]
                for attr in list_of_attributes:
                    temp_dict[attr["key"]] = attr["value"]
                temp.append(copy.deepcopy(temp_dict))
                temp_dict = dict()

            data_path = cls.project_path.joinpath("data")
            if not data_path.exists():
                data_path.mkdir()
            with open(data_path.joinpath(f"stops_locations{datetime.datetime.now().strftime('_%Y-%m-%d.json')}"), "w") as file:
                json.dump(temp, file)
        else:
            logging.info(response_stops_location)



    @classmethod
    def collect_lines_single(cls, zespol, slupek):
        """Metoda wczytująca z API linie przechodzące przez konkretny przystanek"""
        response_lines = requests.get(
            f"https://api.um.warszawa.pl/api/action/dbtimetable_get?id=88cd555f-6f31-43ca-9de4-66c479ad5942"
            f"&busstopId={zespol}&busstopNr={slupek}&apikey={cls.apikey}")
        if response_lines.status_code == 200:
            stop_lines = response_lines.json()["result"]
        else:
            logging.info(response_lines)

        assert response_lines.status_code == 200
        result = []
        for line in stop_lines:
            result.append(line["values"][0]["value"])
        return result

    @classmethod
    def collect_lines_all(cls):
        """Metoda zapisująca linie autobusowe dla każdego przystanku"""
        with open("../data/stops_locations_10-01-2024.json", "r") as file:
            data = json.load(file)
        dataFrame = pd.DataFrame.from_records(data)
        stops_lines = dataFrame[["zespol", "slupek"]]
        stops_lines["Linie"] = stops_lines.apply(lambda row: cls.collect_lines_single(row["zespol"], row["slupek"]),
                                                 axis=1)

        data_path = cls.project_path.joinpath("data")
        if not data_path.exists():
            data_path.mkdir()
        stops_lines.to_json(data_path.joinpath(f"stops_lines{datetime.datetime.now().strftime('_%d-%m-%Y.json')}"),
                            orient="columns")

    @classmethod
    def collect_schedule_single(cls, zespol, slupek, line):
        """Metoda wczytująca rozkład dla konkretnego przystanku dla konkretnej linii"""
        logging.info(f"Collecting schedule for given slupek: {slupek} and line: {line}")
        response_lines = requests.get(
            f"https://api.um.warszawa.pl/api/action/dbtimetable_get/?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&busstopId={zespol}"
            f"&busstopNr={slupek}&line={line}&apikey={cls.apikey}")
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
            scheduleFrame["linia"] = line
            return scheduleFrame
        else:
            logging.info(response_lines)

    @classmethod
    def collect_schedule_all(cls):
        stopsFrame = loading.load_stop_lines("../data/stops_lines_06-02-2024.json")
        list_of_schedules = []
        logging.info("Read list of schedules")

        for index, record in stopsFrame.iterrows():
            for line in record["Linie"]:
                list_of_schedules.append(cls.collect_schedule_single(record["zespol"], record["slupek"], line))
        all_schedules = pd.concat(list_of_schedules, ignore_index=True)

        data_path = cls.project_path.joinpath("data")
        if not data_path.exists():
            data_path.mkdir()
        all_schedules.to_json(data_path.joinpath(f"schedules{datetime.datetime.now().strftime('_%Y-%m-%d.json')}"),
                              orient="records")


if __name__ == '__main__':
    # read input e.g. file name with data
    logging.info(DataRetrieval.collect_schedule_all())
