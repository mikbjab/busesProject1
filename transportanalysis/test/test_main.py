import pytest
from unittest.mock import patch, MagicMock

# Importy funkcji z testowanego kodu
from scripts import main


# Fixtures

@pytest.fixture
def mock_args():
    return MagicMock(buses_positions="sample_positions.json", speed=False, clusters=False, punctuality=False)


@pytest.fixture
def mock_Analysis():
    return MagicMock()


@pytest.fixture
def mock_load_bus_positions():
    with patch("transportanalysis.loading.load_bus_positions") as mock_load:
        yield mock_load


@pytest.fixture
def mock_load_stop_location():
    with patch("transportanalysis.loading.load_stop_location") as mock_load:
        yield mock_load


@pytest.fixture
def mock_load_schedule():
    with patch("transportanalysis.loading.load_schedule") as mock_load:
        yield mock_load


@pytest.fixture
def mock_Analysis_instance():
    with patch("transportanalysis.analysis.Analysis") as mock_Analysis_class:
        yield mock_Analysis_class.return_value


@pytest.fixture
def mock_DataVisual():
    with patch("transportanalysis.visualisation.DataVisual") as mock_dv:
        yield mock_dv


# Tests

def test_main(mock_args, mock_load_bus_positions, mock_load_stop_location, mock_load_schedule, mock_Analysis,
              mock_Analysis_instance, mock_DataVisual):
    main.main(mock_args)
    mock_load_bus_positions.assert_called_once_with("sample_positions.json")
    mock_load_stop_location.assert_called_once_with("data/stops_locations_10-01-2024.json")
    mock_load_schedule.assert_called_once_with("data/schedules_08-02-2024.json")
    mock_Analysis.assert_called_once_with(mock_load_bus_positions.return_value, mock_load_stop_location.return_value,
                                          mock_load_schedule.return_value)

    assert mock_Analysis_instance.analise_speed.called == (mock_args.speed or mock_args.clusters)
    assert mock_Analysis_instance.analise_clusters.called == mock_args.clusters
    assert mock_Analysis_instance.check_punctuality.called == mock_args.punctuality

    if mock_args.speed or mock_args.clusters:
        mock_DataVisual.speeding_map.assert_called_once_with(mock_Analysis_instance.analise_speed.return_value[0])
        mock_DataVisual.save_map.assert_called_once()

    if mock_args.clusters:
        mock_DataVisual.clusters.assert_called_once_with(mock_Analysis_instance.analise_clusters.return_value)

    if mock_args.punctuality:
        mock_DataVisual.show_punctuality.assert_called_once_with(mock_Analysis_instance.check_punctuality.return_value)
