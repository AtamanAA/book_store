import json
import pathlib

import pytest
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

root = pathlib.Path(__file__).parent


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


@pytest.fixture
def api_client():
    user = User.objects.create_user(username="test", password="test")
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
def test_books_get(api_client):
    response = api_client.get("/api/v2/books/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/books_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_valid_filter_get(api_client):
    response = api_client.get("/api/v2/books/?genre=g1")
    response_body = response.json()
    expected_response = json.load(
        open(root / "fixtures/books_filter_by_genre_get_response.json")
    )
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_invalid_filter_get(api_client):
    response = api_client.get("/api/v2/books/?genre_=g1")
    response_body = response.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_invalid_authors_filter_get(api_client):
    response = api_client.get("/api/v2/books/?authors=ggg")
    response_body = response.json()
    expected_response = {"Error": "Invalid authors query parameter"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_get(api_client):
    response = api_client.get("/api/v2/books/1/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/books_id_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_invalid_get(api_client):
    response = api_client.get("/api/v2/books/10/")
    response_body = response.json()
    expected_response = {"Error": "Book with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_valid_new(api_client):
    body = {
        "name": "b6",
        "authors": ["1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 4,
        "name": "b6",
        "authors": ["a_fn1 l1 p1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_empty_json(api_client):
    body = {}
    response = api_client.post(
        "/api/v2/books/",
        data=body,
    )
    response_body = response.json()
    expected_response = {
        "authors": ["This list may not be empty."],
        "name": ["This field is required."],
        "genre": ["This field is required."],
        "publication_date": ["This field is required."],
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_long_name(api_client):
    long_name = 130 * "b"
    body = {
        "name": long_name,
        "authors": ["1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"name": ["Ensure this field has no more than 128 characters."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_long_genre(api_client):
    long_genre = 130 * "b"
    body = {
        "name": "b4",
        "authors": ["1"],
        "genre": long_genre,
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"genre": ["Ensure this field has no more than 40 characters."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_author_type(api_client):
    body = {
        "name": "b4",
        "authors": "bbb",
        "genre": "g4",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"authors": ['Expected a list of items but got type "str".']}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_data(api_client):
    body = {
        "name": "b4",
        "authors": ["1"],
        "genre": "g4",
        "publication_date": "2023",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "publication_date": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_author_not_found(api_client):
    body = {
        "name": "b4",
        "authors": ["4"],
        "genre": "g4",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"authors": ['Invalid pk "4" - object does not exist.']}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_all_field(api_client):
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
        "publication_date": "2011-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 1,
        "name": "update_name",
        "authors": ["a_fn2 l3 p3"],
        "genre": "new_genre",
        "publication_date": "2011-05-20",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_some_field(api_client):
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 1,
        "name": "update_name",
        "authors": ["a_fn2 l3 p3"],
        "genre": "new_genre",
        "publication_date": "1990-01-01",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_long_name(api_client):
    long_name = 130 * "b"
    body = {
        "name": long_name,
        "authors": [1],
        "genre": 2,
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"name": ["Ensure this field has no more than 128 characters."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_long_genre(api_client):
    long_genre = 130 * "b"
    body = {
        "name": "update_name",
        "authors": [1],
        "genre": long_genre,
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"genre": ["Ensure this field has no more than 40 characters."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_invalid_data(api_client):
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
        "publication_date": "2011",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "publication_date": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_invalid_id(api_client):
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
        "publication_date": "2011-01-01",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/books/10/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": f"Book with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_delete(api_client):
    response = api_client.delete("/api/v2/books/1/")
    response_body = response.json()
    expected_response = {"Success": "Book with id=1 success delete"}
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_delete_invalid_id(api_client):
    response = api_client.delete("/api/v2/books/10/")
    response_body = response.json()
    expected_response = {"Error": f"Book with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_get(api_client):
    response = api_client.get("/api/v2/authors/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/authors_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_valid_filter_get(api_client):
    response = api_client.get("/api/v2/authors/?first_name=a_fn2")
    response_body = response.json()
    expected_response = json.load(
        open(root / "fixtures/authors_filter_get_response.json")
    )
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_invalid_filter_get(api_client):
    response = api_client.get("/api/v2/authors/?first_name_=a_fn2")
    response_body = response.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_post_valid(api_client):
    body = {
        "first_name": "a4",
        "last_name": "l4",
        "patronymic": "p4",
        "birthday": "1970-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/authors/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 4,
        "first_name": "a4",
        "last_name": "l4",
        "patronymic": "p4",
        "birthday": "1970-05-20",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_post_empty_json(api_client):
    body = {}
    response = api_client.post(
        "/api/v2/authors/",
        data=body,
    )
    response_body = response.json()
    expected_response = {
        "first_name": ["This field is required."],
        "last_name": ["This field is required."],
        "birthday": ["This field is required."],
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_post_long_first_name(api_client):
    long_first_name = 130 * "b"
    body = {
        "first_name": long_first_name,
        "last_name": "l4",
        "birthday": "1970-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/authors/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "first_name": ["Ensure this field has no more than 20 characters."]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_post_long_last_name(api_client):
    long_last_name = 130 * "b"
    body = {
        "first_name": "a4",
        "last_name": long_last_name,
        "birthday": "1970-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/authors/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "last_name": ["Ensure this field has no more than 20 characters."]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_post_invalid_data(api_client):
    body = {
        "first_name": "a4",
        "last_name": "l4",
        "birthday": "1970",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/authors/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "birthday": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_valid_get(api_client):
    response = api_client.get("/api/v2/authors/1/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/authors_id_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_invalid_get(api_client):
    response = api_client.get("/api/v2/authors/10/")
    response_body = response.json()
    expected_response = {"Error": "Author with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_put_all_field(api_client):
    body = {
        "first_name": "update_a4",
        "last_name": "update_l4",
        "patronymic": "update_p4",
        "birthday": "1980-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/authors/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 1,
        "first_name": "update_a4",
        "last_name": "update_l4",
        "patronymic": "update_p4",
        "birthday": "1980-05-20",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_put_some_field(api_client):
    body = {"first_name": "new_update"}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/authors/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 1,
        "first_name": "new_update",
        "last_name": "l1",
        "patronymic": "p1",
        "birthday": "1970-05-20",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_put_long_first_name(api_client):
    long_first_name = 130 * "b"
    body = {"first_name": long_first_name}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/authors/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "first_name": ["Ensure this field has no more than 20 characters."]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_put_long_last_name(api_client):
    long_last_name = 130 * "b"
    body = {"last_name": long_last_name}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/authors/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "last_name": ["Ensure this field has no more than 20 characters."]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_put_invalid_data(api_client):
    body = {
        "birthday": "1980",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/authors/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "birthday": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_put_invalid_id(api_client):
    body = {
        "first_name": "update_a4",
        "last_name": "update_l4",
        "patronymic": "update_p4",
        "birthday": "1980-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/authors/10/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": f"Author with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_delete(api_client):
    response = api_client.delete("/api/v2/authors/1/")
    response_body = response.json()
    expected_response = {"Success": "Author with id=1 success delete"}
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_delete_invalid_id(api_client):
    response = api_client.delete("/api/v2/authors/10/")
    response_body = response.json()
    expected_response = {"Error": f"Author with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response
