import folium
import matplotlib.pyplot as plt
import transportanalysis.analysis as da
from transportanalysis import loading


class DataVisual:
    loc_center = [52.22909188772849, 21.014005878402372]
    map1 = folium.Map(location=loc_center, tiles="Openstreetmap", zoom_start=11, control_scale=True)
    speeding_flag = False
    clusters_flag = False

    @classmethod
    def save_map(cls):
        cls.map1.save(f"mapa{'_speeding' if cls.speeding_flag else ''}{'_clusters' if cls.clusters_flag else ''}.html")
        cls.speeding_flag = False
        cls.clusters_flag = False

    @classmethod
    def speeding_map(cls, speed_frame):
        for index, loc in speed_frame.iterrows():
            color = "red"
            name = f"Linia: {loc['Lines']}\n" \
                   f"Brygada: {loc['Brigade']}"
            pop = f"Prędkość: {loc['Velocity']}"
            folium.RegularPolygonMarker([loc['Lat'], loc['Lon']], tooltip=name, popup=pop, fill_color=color,
                                        number_of_sides=3, radius=6, rotation=30).add_to(cls.map1)
        folium.LayerControl().add_to(cls.map1)
        cls.speeding_flag = True

    @classmethod
    def clusters(cls, clusters):
        info = clusters
        for cluster_info in info:
            text = f"Lokalizacja: {cluster_info[0]}\n" \
                   f"Średnia prędkość: {cluster_info[1]}\n" \
                   f"Liczba przypadków: {cluster_info[2]}"
            folium.Circle(cluster_info[0], 1000, popup=text, color="cornflowerblue", stroke=False, fill=True,
                          fill_opacity=0.6, opacity=1).add_to(cls.map1)
        cls.clusters_flag = True

    @classmethod
    def show_speed_histogram(cls, speed_frame):
        speed_frame.hist(column="Velocity", bins=[0., 10., 20., 30., 40., 50., 60., 70., 80., 90.])
        plt.show()

    @classmethod
    def show_punctuality(cls, punctuality_histogram):
        plt.bar(["Na czas", "Spóźnione"], [punctuality_histogram["On time"], punctuality_histogram["Late"]])


if __name__ == '__main__':
    analysis = da.Analysis(loading.load_bus_positions("../data/data_2024-02-17.json"),
                           loading.load_stop_location("../data/stops_locations_10-01-2024.json"),
                           loading.load_schedule("../data/schedules_08-02-2024.json"))
    analysis.analise_speed("../data/speed_data_2024-02-17.json")
    DataVisual.show_speed_histogram(analysis.analise_speed("../data/speed_data_2024-02-17.json")[0])
    DataVisual.clusters(analysis.analise_clusters("../data/clusters_data_2024-02-17.json"))
    DataVisual.speeding_map(analysis.analise_speed("../data/speed_data_2024-02-17.json",50)[0])
    DataVisual.save_map()
