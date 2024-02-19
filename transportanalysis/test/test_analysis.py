import datetime

import pytest
from unittest.mock import patch
import numpy as np
import pandas as pd
import transportanalysis.analysis as ta


@pytest.fixture
def analysis():
    data_buses=pd.read_csv("test_bus_positions.csv")
    stop_locations=pd.read_csv("test_stop_locations.csv")
    data_schedule=pd.read_csv("test_schedule.csv")
    return ta.Analysis(data_buses,stop_locations,data_schedule)


def test_haversine_good():
    # Test for haversine function
    assert np.isclose(ta.haversine(52.2296756, 21.0122287, 52.406374, 16.9251681), 278.45817507541943)


def test_haversine_wrong_format():
    # Test for haversine function
    pytest.raises(TypeError, ta.haversine,"A", 21.0122287, 52.406374, 16.9251681)


def test_velocity():
    # Test for velocity function
    distance = 100  # in km
    time1 = "2024-01-01 12:00:00"
    time2 = "2024-01-01 13:00:00"
    assert ta.velocity(distance, time1, time2) == 100  # Speed should be 100 km/h


def test_get_time_range():
    # Test for get_time_range function
    assert ta.get_time_range(pd.to_datetime("1900-01-01 04:56:00", format='%Y-%m-%d %H:%M:%S')) == [datetime.time(4,54), datetime.time(4,58)]
    assert ta.get_time_range(pd.to_datetime("1900-01-01 12:00:00", format='%Y-%m-%d %H:%M:%S')) == [datetime.time(11,58), datetime.time(12,2)]


def test_analise_speed(analysis,mock_file):
    # Test for analise_speed function
    min_speed = 70  # km/h
    analysis.analise_speed(mock_file,min_speed)



def test_analise_clusters(analysis):
    # Test for analise_clusters function
    distance = 1  # km
    clusters, clusters_info = analysis.analise_clusters(distance)
    assert isinstance(clusters, list)
    assert isinstance(clusters_info, list)


@patch('sys.stdout')
def test_is_near(mock_stdout, analysis):
    # Test for is_near function
    wrong_row = {"zespol": "A", "slupek": "01", "brygada": "1", "linia": "1", "czas": "2024-01-01 12:00:00"}
    assert analysis.is_near(pd.Series(wrong_row)) == -1


def test_check_punctuality(analysis):
    # Test for check_punctuality function
    on_time_statistics = analysis.check_punctuality("schedule.csv")
    assert isinstance(on_time_statistics, dict)
