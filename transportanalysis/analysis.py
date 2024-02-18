import logging

import numpy as np
import pandas as pd

from transportanalysis import loading

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


def velocity(distance, time1, time2):
    """Funkcja pomocnicza licząca prędkość między dwoma położeniami autobusu"""
    datetime_time1 = pd.to_datetime(time1, format='%Y-%m-%d %H:%M:%S')
    datetime_time2 = pd.to_datetime(time2, format='%Y-%m-%d %H:%M:%S')
    time_difference = (datetime_time2 - datetime_time1) / pd.Timedelta(hours=1)
    return distance / time_difference


def get_time_range(time):
    earlier_time = time - pd.Timedelta(minutes=2)
    later_time = time + pd.Timedelta(minutes=2)
    return [earlier_time.time(), later_time.time()]


class Analysis:
    def __init__(self, temp_bus_positions_pd, temp_stop_locations_pd, temp_schedule_pd):
        # TODO wczytanie różnych danych

        self.bus_data = temp_bus_positions_pd.sort_values(by=["VehicleNumber", "Time"])
        self.stop_locations = temp_stop_locations_pd
        self.uniqueVehicles = self.bus_data.VehicleNumber.unique()
        self.schedule = temp_schedule_pd

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
        index = pd.DatetimeIndex(bus_positions['Time'])
        filtered_bus_positions = bus_positions.iloc[index.indexer_between_time(time_range[0], time_range[1])]
        for index, bus_row in filtered_bus_positions.iterrows():
            stop_distance = haversine(bus_row["Lat"], bus_row["Lon"],
                                      float(stop_position["szer_geo"].iloc[0]),
                                      float(stop_position["dlug_geo"].iloc[0]))
            if stop_distance < 0.5:
                return 0
        return 1

    def check_punctuality(self):
        logging.info("Starting punctuality check")
        schedule_frame = self.schedule
        logging.info("Loaded schedules")

        index = pd.DatetimeIndex(schedule_frame['czas'])
        filtered_schedule = schedule_frame.iloc[index.indexer_between_time(self.bus_data["Time"].min().split(" ")[1],
                                                                           self.bus_data["Time"].max().split(" ")[1])]

        logging.info("Analysing all buses and stations")

        filtered_schedule["punctuality"] = filtered_schedule.apply(self.is_near, axis=1)
        on_time_statistics = {-1: (filtered_schedule["punctuality"] == -1).count(),
                              0: (filtered_schedule["punctuality"] == 0).count(),
                              1: (filtered_schedule["punctuality"] == 1).count()}

        logging.info("Finished analysis")
        return on_time_statistics


if __name__ == '__main__':
    #  ETL
    # extract (wcczytujesz z api
    # transform (modyfikujesz)
    # load (zapisujesz do bazki albo pliku)
    bus_filename = "../data/data_2024-02-17.json"
    bus_positions_pd = loading.load_bus_positions(bus_filename)
    stop_loc_filename = "../data/stops_locations_10-01-2024.json"
    stop_locations_pd = loading.load_stop_location(stop_loc_filename)
    schedule_filename = "../data/schedules_08-02-2024.json"
    schedule_pd = loading.load_schedule(schedule_filename)

    analysis_pd = Analysis(bus_positions_pd, stop_locations_pd, schedule_pd)

    logging.info(analysis_pd.check_punctuality())
