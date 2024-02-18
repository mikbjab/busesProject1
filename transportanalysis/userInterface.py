import argparse
import transportanalysis.models.data_analysis as da
import transportanalysis.models.data_visualisation as dv


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("buses_positions")
    parser.add_argument("-s", "--speed", action='store_true',
                        help="create map and histogram of speeding buses")
    parser.add_argument("-c", "--clusters", action='store_true',
                        help="create map with regions where buses are going above 50 kmh")
    parser.add_argument("-p", "--punctuality", action="store_true", help="create bar chart of punctuality of buses in "
                                                                         "given period")

    args = parser.parse_args()
    analysis = da.Analysis(filename=args.buses_positions)
    if args.speed:
        dv.DataVisual.speeding_map(analysis.analise_speed()[0])
        dv.DataVisual.speeding_map(analysis.analise_speed(50)[0])
    if args.clusters:
        dv.DataVisual.clusters(analysis.analise_clusters())
    if args.speed or args.clusters:
        dv.DataVisual.save_map()
    if args.punctuality:
        dv.DataVisual.show_punctuality(analysis.check_punctuality("../resources/schedules_08-02-2024.json"))

