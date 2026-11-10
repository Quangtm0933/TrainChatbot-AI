
import pytest

from utils.entity_extractor import (
    normalize_text,
    extract_stations,
    extract_travel_date,
    extract_passengers,
    extract_entities,
)


def test_normalize_text():
    assert normalize_text("Đường Sắt Việt Nam") == (
        "duong sat viet nam"
    )


def test_extract_stations():
    result = extract_stations(
        "Tôi muốn đi từ Hà Nội đến Huế"
    )

    assert result == {
        "departure_station": "Hà Nội",
        "arrival_station": "Huế",
    }


def test_extract_stations_without_known_station():
    result = extract_stations(
        "Tôi muốn đi từ Hà Nội đến Paris"
    )

    assert result["departure_station"] == "Hà Nội"
    assert result["arrival_station"] is None


def test_extract_date_slash_format():
    assert extract_travel_date(
        "Tôi muốn đi ngày 20/12/2026"
    ) == "2026-12-20"


def test_extract_date_iso_format():
    assert extract_travel_date(
        "Tôi muốn đi ngày 2026-12-20"
    ) == "2026-12-20"


def test_invalid_date():
    assert extract_travel_date(
        "Tôi muốn đi ngày 32/12/2026"
    ) is None


def test_missing_date():
    assert extract_travel_date(
        "Tôi muốn đi Huế"
    ) is None


def test_extract_passengers():
    assert extract_passengers(
        "Tôi muốn mua vé cho 2 người"
    ) == 2


def test_extract_passengers_with_hanh_khach():
    assert extract_passengers(
        "Có 3 hành khách"
    ) == 3


def test_invalid_passenger_count():
    assert extract_passengers(
        "Tôi muốn mua vé cho 25 người"
    ) is None


def test_extract_all_entities():
    result = extract_entities(
        "Tôi muốn đi từ Hà Nội đến Huế ngày 20/12/2026 "
        "cho 2 người"
    )

    assert result == {
        "departure_station": "Hà Nội",
        "arrival_station": "Huế",
        "travel_date": "2026-12-20",
        "passengers": 2,
    }


def test_invalid_input():
    with pytest.raises(TypeError):
        extract_entities(None)
