import pytest
from unittest.mock import patch
import numpy as np
import pandas as pd


@pytest.fixture
def analysis():
    return analysis.Analysis("test_data.json")  # Provide test data file


def test_haversine():
    # Test for haversine function
    assert np.isclose(analysis.haversine(52.2296756, 21.0122287, 52.406374, 16.9251681), 278.45817507541943)


def test_velocity():
    # Test for velocity function
    distance = 100  # in km
    time1 = "2024-01-01 12:00:00"
    time2 = "2024-01-01 13:00:00"
    assert analysis.velocity(distance, time1, time2) == 100  # Speed should be 100 km/h


def test_get_time_range():
    # Test for get_time_range function
    assert analysis.get_time_range("120000") == [115800, 120200]
    assert analysis.get_time_range("002000") == [1800, 2200]


def test_analise_speed(analysis):
    # Test for analise_speed function
    min_speed = 70  # km/h
    result_df, speeding_buses = analysis.analise_speed(min_speed)
    assert all(result_df['Velocity'] >= min_speed)
    assert isinstance(speeding_buses, dict)


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
