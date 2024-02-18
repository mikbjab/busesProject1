import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import transportanalysis.loading as tl


# Fixtures

@pytest.fixture
def sample_data():
    return [
        {"VehicleNumber": "ABC123", "Time": "2024-02-18 08:00:00", "Lat": 52.22977, "Lon": 21.01178},
        {"VehicleNumber": "DEF456", "Time": "2024-02-18 08:10:00", "Lat": 52.22977, "Lon": 21.01178},
        {"VehicleNumber": "ABC123", "Time": "2024-02-18 08:20:00", "Lat": 52.22977, "Lon": 21.01178},
        {"VehicleNumber": "GHI123", "Time": "2024-02-17 08:20:00", "Lat": 52.22977, "Lon": 21.01178}
    ]


@pytest.fixture
def sample_dataframe(sample_data):
    return pd.DataFrame(sample_data)


# Tests

def test_filter_empties_deleting():
    data = [
        {"foo": "bar"},
        {"baz": "qux"},
        {},
        {"spam": "eggs"}
    ]
    assert tl.filter_empties(data) == [{"foo": "bar"}, {"baz": "qux"}, {"spam": "eggs"}]


def test_filter_empties_no_change():
    data = [
        {"foo": "bar"},
        {"baz": "qux"},
        {"spam": "eggs"}
    ]
    assert tl.filter_empties(data) == [{"foo": "bar"}, {"baz": "qux"}, {"spam": "eggs"}]


def test_delete_duplicate_positions_with_change(sample_dataframe):
    # Sample DataFrame with duplicate entries
    df = sample_dataframe.append(sample_dataframe.iloc[0]).reset_index(drop=True)
    result = tl.delete_duplicate_positions(df)
    assert len(result) == len(sample_dataframe)


def test_delete_duplicate_positions_with_no_change(sample_dataframe):
    # Sample DataFrame with duplicate entries
    df = sample_dataframe
    result = tl.delete_duplicate_positions(df)
    assert len(result) == len(sample_dataframe)


def test_filter_different_dates(sample_data):
    result = tl.filter_different_dates(sample_data, "2024-02-18")
    assert all("2024-02-18" in item["Time"] for item in result)


def test_load_date_from_file():
    assert tl.load_date_from_file("file_2024-02-18.json") == "2024-02-18"


def test_change_time_format_with_change():
    assert tl.change_time_format("25:30:45") == "01:30:45"


def test_change_time_format_with_no_change():
    assert tl.change_time_format("20:30:45") == "20:30:45"


def test_change_hours():
    # Mocking DataFrame
    mock_df = MagicMock()
    mock_df["czas"] = pd.Series(["25:30:45", "26:15:20", "23:45:00"])
    tl.change_hours(mock_df)
    assert (mock_df["czas"] == pd.to_datetime(["01:30:45", "02:15:20", "23:45:00"], format="%H:%M:%S")).all()

# Add more tests for other functions as needed...

# Tests for functions reading from files might require additional fixtures or mocking depending on file availability and content.
