import argparse
import transportanalysis.analysis as da
import transportanalysis.visualisation as dv
from transportanalysis import loading


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("buses_positions")
    parser.add_argument("-s", "--speed", action='store_true',
                        help="create map and histogram of speeding buses")
    parser.add_argument("-c", "--clusters", action='store_true',
                        help="create map with regions where buses are going above 50 kmh")
    parser.add_argument("-p", "--punctuality", action="store_true", help="create bar chart of punctuality of buses in "
                                                                         "given period")

    args = parser.parse_args()
    analysis = da.Analysis(loading.load_bus_positions(args.buses_positions),
                           loading.load_stop_location("../data/stops_locations_10-01-2024.json"),
                           loading.load_schedule("../data/schedules_08-02-2024.json"))
    if args.speed:
        analysis.analise_speed(args.buses_positions.replace("data_","speed_data_"),50)
        dv.DataVisual.speeding_map(loading.load_bus_speeds(args.buses_positions.replace("data_","speed_data_")))
    if args.clusters:
        analysis.analise_clusters(args.buses_positions.replace("data_", "clusters_data_"))
        dv.DataVisual.clusters(loading.load_json(args.buses_positions.replace("data_", "clusters_data_")))
    if args.speed or args.clusters:
        dv.DataVisual.save_map()
    if args.punctuality:
        analysis.check_punctuality(args.buses_positions.replace("data_","punctuality_"))
        dv.DataVisual.show_punctuality(analysis.check_punctuality(args.buses_positions.replace("data_","punctuality_")))


if __name__ == "__main__":
    main()
