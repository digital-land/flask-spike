from application.data_access.digital_land_queries import (
    get_datasets_with_data_by_typology,
)
from application.db.models import DatasetOrm, EntityOrm


def test_get_datasets_with_data_by_typology_finds_if_typology_correct_and_entities_exist(
    db_session,
):
    # add a dataset with a typology geography and one entity
    dataset = DatasetOrm(
        dataset="test-dataset",
        typology="geography",
    )

    entity = EntityOrm(
        entity=1,
        dataset="test-dataset",
        typology="geography",
    )

    db_session.add(dataset)
    db_session.add(entity)

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert len(datasets) == 1


def test_get_datasets_with_data_by_typology_does_not_find_if_typology_incorrect(
    db_session,
):
    # add a dataset with a typology geography and one entity with a different dataset
    dataset = DatasetOrm(
        dataset="test-dataset",
        typology="geography",
    )

    entity = EntityOrm(
        entity=1,
        dataset="a-different-dataset",
        typology="geography",
    )

    db_session.add(dataset)
    db_session.add(entity)

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert len(datasets) == 0


def test_get_datasets_with_data_by_typology_does_not_find_if_no_entities_exist(
    db_session,
):
    # add a dataset with a typology geography and no entities
    dataset = DatasetOrm(
        dataset="test-dataset",
        typology="geography",
    )

    db_session.add(dataset)

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert len(datasets) == 0
