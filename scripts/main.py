import argparse
from pathlib import Path

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

    file_path = Path(__file__).parent
    data_dir_path = file_path.joinpath("data")
    analysis = da.Analysis(loading.load_bus_positions(args.buses_positions),
                           loading.load_stop_location(loading.find_latest_file(data_dir_path, "stops_locations")),
                           loading.load_schedule(loading.find_latest_file(data_dir_path, "schedules")))

    if args.speed:
        speed_filename=args.buses_positions.replace("data_", "speed_data_")
        analysis.analise_speed(speed_filename, 50)
        dv.DataVisual.speeding_map(loading.load_bus_speeds(speed_filename))
    if args.clusters:
        cluster_filename = args.buses_positions.replace("data_", "clusters_data_")
        analysis.analise_clusters(cluster_filename)
        dv.DataVisual.clusters(loading.load_json(cluster_filename))
    if args.speed or args.clusters:
        dv.DataVisual.save_map()
    if args.punctuality:
        punctuality_filename=args.buses_positions.replace("data_", "punctuality_")
        analysis.check_punctuality(punctuality_filename)
        dv.DataVisual.show_punctuality(analysis.check_punctuality(punctuality_filename))


if __name__ == "__main__":
    main()
