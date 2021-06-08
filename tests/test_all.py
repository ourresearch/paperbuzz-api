from datetime import datetime
import pytest
from views import app, db
from event import CedEvent, CedSource

# to run these tests, create local database named paperbuzz_test
# then run with $ pytest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost:5432/paperbuzz_test"
    return app.test_client()


@pytest.fixture
def init_database():
    # create the database tables
    with app.app_context():
        db.create_all()

        # insert sample data
        source = CedSource(
            id="datacite", display_name="DataCite", icon_url="datacite.png"
        )
        event1 = CedEvent(
            id="peeZ2knsGxRzvuw4NVW6",
            doi="10.1039/c5ce01901j",
            api_raw=dict(
                {
                    "id": "80c78ffb-8d32-4de7-8023-1187dffdaef2",
                    "terms": "https://doi.org/10.13003/CED-terms-of-use",
                    "obj_id": "https://doi.org/10.1039/c5ce01901j",
                    "license": "https://creativecommons.org/publicdomain/zero/1.0/",
                    "subj_id": "https://doi.org/10.5517/cc13t0gd",
                    "source_id": "datacite",
                    "timestamp": "2017-06-28T04:23:34Z",
                    "occurred_at": "2014-12-01T14:09:33Z",
                    "source_token": "28276d12-b320-41ba-9272-bb0adc3466ff",
                    "message_action": "create",
                    "relation_type_id": "is_supplement_to",
                }
            ),
            occurred_at=datetime.strptime("2014-12-01", "%Y-%m-%d"),
            normalized_subj_id="https://doi.org/10.5517/cc13t0gd",
            uniqueness_key="08d64da78ed5223c2329d00350727581",
        )
        event2 = CedEvent(
            id="XnXvJVPNq2FkWD4VD6uv",
            doi="10.1039/c5ce01901j",
            api_raw=dict(
                {
                    "id": "4d6a48be-6d51-4d4b-be91-4d5929fa0ba0",
                    "terms": "https://doi.org/10.13003/CED-terms-of-use",
                    "obj_id": "https://doi.org/10.1039/c5ce01901j",
                    "license": "https://creativecommons.org/publicdomain/zero/1.0/",
                    "subj_id": "https://doi.org/10.5517/cc13t0hf",
                    "source_id": "datacite",
                    "timestamp": "2017-06-28T04:23:34Z",
                    "occurred_at": "2014-12-01T14:09:34Z",
                    "source_token": "28276d12-b320-41ba-9272-bb0adc3466ff",
                    "message_action": "create",
                    "relation_type_id": "is_supplement_to",
                }
            ),
            occurred_at=datetime.strptime("2014-12-01", "%Y-%m-%d"),
            normalized_subj_id="https://doi.org/10.5517/cc13t0hf",
            uniqueness_key="2ed6a1381d65683ec3c1ddf575d7709a",
        )
        db.session.add(source)
        db.session.add(event1)
        db.session.add(event2)

        # Commit the changes
        db.session.commit()

        yield db

        # remove tables
        db.session.remove()
        db.drop_all()


def test_api_index(client):
    response = client.get("/")
    json_data = response.get_json()
    assert response.status_code == 200
    assert "wrapper for crossrev event data api." in json_data["description"]


def test_api_doi_events(client, init_database):
    response = client.get("/v0/doi/10.1039/c5ce01901j")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["doi"] == "10.1039/c5ce01901j"
    assert json_data["altmetrics_sources"][0]["events_count"] == 2


def test_api_doi_metadata(client, init_database):
    response = client.get("/v0/doi/10.1039/c5ce01901j")
    json_data = response.get_json()
    assert json_data["metadata"]["DOI"] == "10.1039/c5ce01901j"
    assert "1466-8033" in json_data["metadata"]["ISSN"]


def test_api_doi_source(client, init_database):
    response = client.get("/v0/doi/10.1039/c5ce01901j")
    json_data = response.get_json()
    assert json_data["altmetrics_sources"][0]["source"]["id"] == "datacite"
    assert json_data["altmetrics_sources"][0]["source"]["display_name"] == "DataCite"
    assert "datacite.png" in json_data["altmetrics_sources"][0]["source"]["icon_url"]
