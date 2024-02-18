import pandas as pd


def test_delete_empties(data_retrieval):
    data = [1, 2, {}, {'a': 1}, []]
    assert data_retrieval.filter_empties(data) == [{'a': 1}]


def test_delete_duplicate_positions(data_retrieval):
    busFrame = pd.DataFrame({
        'VehicleNumber': [1, 2, 1],
        'Time': ['2024-01-01 12:00:00', '2024-01-01 12:00:00', '2024-01-01 12:00:00'],
        'Lat': [52.2296756, 52.2296756, 52.2296756]
    })
    result = data_retrieval.delete_duplicate_positions(busFrame)
    assert len(result) == 1
