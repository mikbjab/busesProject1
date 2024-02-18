import logging
import time

import numpy as np
import pandas as pd

from transportanalysis.models.data_download import DataRetrieval

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """Funkcja pomocnicza mierząca odległość (km) między dwoma punktami opisanymi współrzędnymi geograficznymi"""
    if to_radians:
        lat1 = np.radians(lat1)
        lat2 = np.radians(lat2)
        lon1 = np.radians(lon1)
        lon2 = np.radians(lon2)

    a = np.sin((lat2 - lat1) / 2.0) ** 2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2.0) ** 2

    return earth_radius * 2 * np.arcsin(np.sqrt(a))


def haversine_rows(rows: np.ndarray):
    return haversine()

def velocity(distance, time1, time2):
    """Funkcja pomocnicza licząca prędkość między dwoma położeniami autobusu"""
    datetime_time1 = pd.to_datetime(time1, format='%Y-%m-%d %H:%M:%S')
    datetime_time2 = pd.to_datetime(time2, format='%Y-%m-%d %H:%M:%S')
    time_difference = (datetime_time2 - datetime_time1) / pd.Timedelta(hours=1)
    return distance / time_difference


def get_time_range(time):
    time = str(time)
    if len(time) == 6:
        if int(time[:-5]) > 24:
            time = str(int(time[:-5]) - 24) + time[-4:]
    formatted_time = time
    pd_time = pd.to_datetime(formatted_time, format="%H%M%S")
    earlier_time = pd_time - pd.Timedelta(minutes=2)
    later_time = pd_time + pd.Timedelta(minutes=2)
    return [int(earlier_time.strftime('%H%M%S')), int(later_time.strftime('%H%M%S'))]


class Analysis:
    def __init__(self, filename=""):
        # TODO wczytanie różnych danych
        data = DataRetrieval.load_bus_positions(filename)

        self.bus_data = data.sort_values(by=["VehicleNumber", "Time"])
        self.stop_locations = DataRetrieval.load_stop_location("../resources/stops_locations_10-01-2024.json")
        self.uniqueVehicles = self.bus_data.VehicleNumber.unique()

    def analise_speed(self, min_speed=0):
        speeding_buses = dict.fromkeys(self.uniqueVehicles)
        result = []
        for vehicle in self.uniqueVehicles:
            vehicle_frame = self.bus_data[self.bus_data.VehicleNumber == vehicle]
            vehicle_frame.loc[:, 'Distance'] = haversine(vehicle_frame.Lat.shift(), vehicle_frame.Lon.shift(),
                                                         vehicle_frame.loc[1:, 'Lat'], vehicle_frame.loc[1:, 'Lon'])
            vehicle_frame.loc[:, "Velocity"] = velocity(vehicle_frame.loc[:, "Distance"], vehicle_frame.Time.shift(),
                                                        vehicle_frame.loc[1:, 'Time'])
            result.append(vehicle_frame)
            speeding_buses[vehicle] = len(vehicle_frame.query("100>Velocity>50"))
        velocity_frame = pd.concat(result, ignore_index=True)
        return velocity_frame.query(f"100>Velocity>{min_speed}"), speeding_buses

    def analise_clusters(self, distance=1):
        speed_frame = self.analise_speed()[0]
        speed_frame = speed_frame.query("100>Velocity>50")
        list_of_clusters = []
        for index, loc in speed_frame.iterrows():
            temp_list = [[loc["Lat"], loc["Lon"], loc["Velocity"], loc["VehicleNumber"]]]
            updated_flag = False
            for index2, loc2 in speed_frame.iterrows():
                if loc["VehicleNumber"] == loc2["VehicleNumber"] and loc["Lat"] == loc2["Lat"]:
                    continue

                if haversine(loc["Lat"], loc["Lon"], loc2["Lat"], loc2["Lon"]) < distance:
                    temp_list.append([loc2["Lat"], loc2["Lon"], loc2["Velocity"], loc2["VehicleNumber"]])

            for item in list_of_clusters:
                if temp_list[0] in item:
                    item.extend(temp_list)
                    updated_flag = True
            if not updated_flag:
                list_of_clusters.append(temp_list)
        clusters = list(filter(lambda x: len(x) > 2, list_of_clusters))
        clusters_info = []
        for cluster in clusters:
            tempFrame = pd.DataFrame(cluster, columns=["Lat", "Lon", "Velocity", "VehicleNumber"])
            location = [tempFrame["Lat"].mean(), tempFrame["Lon"].mean()]
            speed = tempFrame["Velocity"].mean()
            occurrences = tempFrame.count()[0]
            clusters_info.append([location, speed, occurrences])
        return [clusters, clusters_info]

    def is_near(self, schedule_row):
        """ Sprawdzenie, czy wokół danego przystanku (schedule_row) był autobus tej linii i tej brygady,
            'w okolicy' definiujemy jako odległość 400 m w każdą stronę (z uwagi na pozycje aktualizowane co minutę)
        """
        logging.info("Analysing row")
        bus_positions = self.bus_data[(self.bus_data["Brigade"] == schedule_row.brygada)
                                      & (self.bus_data["Lines"] == schedule_row.linia)]
        if bus_positions.empty:
            return -1

        stop_position = self.stop_locations[(self.stop_locations["zespol"] == schedule_row.zespol)
                                            & (self.stop_locations["slupek"] == schedule_row.slupek)]

        time_range = get_time_range(schedule_row["czas"])
        for index, bus_row in bus_positions.iterrows():
            bus_time = int(bus_row["Time"].split(" ")[1].replace(":", ""))
            if time_range[0] < bus_time < time_range[1]:
                stop_distance = haversine(bus_row["Lat"], bus_row["Lon"],
                                          stop_position["szer_geo"].iloc[0],
                                          stop_position["dlug_geo"].iloc[0])
                if stop_distance < 0.5:
                    return 0
        return 1

    def check_punctuality(self, schedule_filename):
        logging.info("Starting punctuality check")
        begin_time = self.bus_data["Time"].min().split(" ")[1].replace(":", "_")
        if begin_time[0] == "0":
            begin_time = begin_time[1:]
        end_time = self.bus_data["Time"].max().split(" ")[1].replace(":", "_")
        # TODO filtrowanie w datafrme, nie w liscie
        schedule_frame = DataRetrieval.load_schedule(schedule_filename)
        logging.info("Loaded schedules")
        schedule_frame["czas"] = schedule_frame["czas"].str.replace(":", "_").astype(int)
        schedule_frame = schedule_frame.query(f"{end_time}>czas>{begin_time}")

        on_time_statistics = {"Not found": 0, "On time": 0, "Late": 0}
        logging.info("Analysing all buses and stations")

        schedule_frame["punctuality"] = schedule_frame.apply(self.is_near, axis=1)
        # for index, row in schedule_frame.iterrows():
        #     logging.info("Analysing row")
        #     temp = self.is_near(row)
        #     if temp == 0:
        #         on_time_statistics["On time"] += 1
        #     elif temp == 1:
        #         on_time_statistics["Late"] += 1
        #     else:
        #         on_time_statistics["Not found"] += 1

        logging.info("Finished analysis")
        return on_time_statistics



def load_bus_positions(filename) -> pd.DataFrame:
    pass

if __name__ == '__main__':

    #  ETL
    # extract (wcczytujesz z api
    # transform (modyfikujesz)
    # load (zapisujesz do bazki albo pliku)
    filename = "../resources/data_2024-02-17.json"
    bus_positions_pd = load_bus_positions(filename)


    analysis_pd = Analysis(filename)

    logging.info(analysis.check_punctuality("../resources/schedules_08-02-2024.json"))
