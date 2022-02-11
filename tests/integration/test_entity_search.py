import pytest

from application.data_access.entity_queries import get_entity_search
from application.search.enum import EntriesOption, GeometryRelation


@pytest.fixture(scope="module")
def raw_params():
    return {
        "theme": None,
        "typology": None,
        "dataset": None,
        "organisation": None,
        "organisation_entity": None,
        "entity": None,
        "curie": None,
        "prefix": None,
        "reference": None,
        "related_entity": None,
        "entries": EntriesOption.all,
        "start_date": None,
        "start_date_year": None,
        "start_date_month": None,
        "start_date_day": None,
        "start_date_match": None,
        "end_date": None,
        "end_date_year": None,
        "end_date_month": None,
        "end_date_day": None,
        "end_date_match": None,
        "entry_date": None,
        "entry_date_year": "",
        "entry_date_month": "",
        "entry_date_day": "",
        "entry_date_match": None,
        "longitude": None,
        "latitude": None,
        "geometry": None,
        "geometry_entity": None,
        "geometry_reference": None,
        "geometry_relation": None,
        "limit": 10,
        "offset": None,
        "suffix": None,
    }


@pytest.fixture()
def params(raw_params):
    return raw_params.copy()


def test_search_entity_by_dataset_name_not_in_system(test_data, params):

    params["dataset"] = ["not-exists"]
    result = get_entity_search(params)
    assert 0 == result["count"]
    assert [] == result["entities"]


def test_search_entity_by_single_dataset_name(test_data, params):

    params["dataset"] = ["greenspace"]
    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "greenspace" == entity.dataset
    assert "geography" == entity.typology


def test_search_entity_by_list_of_dataset_names(test_data, params):

    params["dataset"] = ["greenspace", "brownfield-site"]
    result = get_entity_search(params)
    assert 2 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["greenspace", "brownfield-site"]
        assert "geography" == e.typology


def test_search_entity_by_date_since(test_data, params):

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "since"

    result = get_entity_search(params)
    assert 4 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]
        assert "geography" == e.typology

    params["entry_date_year"] = 2020
    result = get_entity_search(params)
    assert 3 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["forest", "brownfield-site", "historical-monument"]
        assert e.dataset != "greenspace"

    params["entry_date_year"] = 2021
    result = get_entity_search(params)
    assert 2 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["brownfield-site", "historical-monument"]
        assert e.dataset not in ["greenspace", "forest"]

    params["entry_date_year"] = 2022
    result = get_entity_search(params)
    assert 1 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["historical-monument"]
        assert e.dataset not in ["greenspace", "forest", "brownfield-site"]

    params["entry_date_year"] = 2023
    result = get_entity_search(params)
    assert 0 == result["count"]


def test_search_entity_by_date_before(test_data, params):

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "before"

    result = get_entity_search(params)
    assert 0 == result["count"]

    params["entry_date_year"] = 2020
    result = get_entity_search(params)
    assert 1 == result["count"]

    params["entry_date_year"] = 2021
    result = get_entity_search(params)
    assert 2 == result["count"]

    params["entry_date_year"] = 2022
    result = get_entity_search(params)
    assert 3 == result["count"]

    params["entry_date_year"] = 2023
    result = get_entity_search(params)
    assert 4 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_entity_by_date_equal(test_data, params):

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1

    result = get_entity_search(params)
    assert 0 == result["count"]

    params["entry_date_day"] = 7

    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "greenspace" == entity.dataset


def test_search_entity_by_point(test_data, params):

    params["longitude"] = -1.64794921875
    params["latitude"] = 50.51342652633956

    result = get_entity_search(params)
    assert 0 == result["count"]

    params["longitude"] = -1.82398796081543
    params["latitude"] = 51.18064775509972

    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "historical-monument" == entity.dataset


def test_search_entity_by_single_polygon_intersects(test_data, params):

    from tests.test_data.wkt_data import intersects_with_brownfield_entity as brownfield
    from tests.test_data.wkt_data import intersects_with_greenspace_entity as greenspace

    params["geometry"] = [brownfield]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "brownfield-site" == entity.dataset

    params["geometry"] = [greenspace]
    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "greenspace" == entity.dataset


def test_search_entity_by_list_of_polygons_that_intersect(test_data, params):

    from tests.test_data.wkt_data import intersects_with_brownfield_entity as brownfield
    from tests.test_data.wkt_data import intersects_with_greenspace_entity as greenspace

    params["geometry"] = [brownfield, greenspace]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(params)
    assert 2 == result["count"]


def test_search_entity_by_polygon_with_no_intersection(test_data, params):

    from tests.test_data.wkt_data import no_intersection

    params["geometry"] = [no_intersection]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(params)
    assert 0 == result["count"]


def test_search_all_entities(test_data, params):

    # default is EntriesOption.all - already in params
    result = get_entity_search(params)
    assert 4 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_current_entries(test_data, params):

    # entries without an end date
    params["entries"] = EntriesOption.current

    result = get_entity_search(params)
    assert 3 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_historical_entries(test_data, params):

    # entries with an end date
    params["entries"] = EntriesOption.historical

    result = get_entity_search(params)
    assert 1 == result["count"]
    e = result["entities"][0]
    assert "greenspace" == e.dataset