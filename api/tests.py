import json
import pytest
from django.test import Client
from django.core.management import call_command


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


@pytest.mark.django_db
def test_authors_get():
    client = Client()
    response = client.get("/api/authors/")
    response_body = response.json()
    expected_response = [
        {
            "id": 1,
            "first_name": "a_fn1",
            "last_name": "l1",
            "patronymic": "p1",
            "birthday": "1970-05-20",
        },
        {
            "id": 2,
            "first_name": "a_fn2",
            "last_name": "l2",
            "patronymic": "p2",
            "birthday": "1970-05-20",
        },
        {
            "id": 3,
            "first_name": "a_fn2",
            "last_name": "l3",
            "patronymic": "p3",
            "birthday": "1970-05-20",
        },
    ]
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_valid_filter_get():
    client = Client()
    response = client.get("/api/authors/?first_name=a_fn2")
    response_body = response.json()
    expected_response = [
        {
            "id": 2,
            "first_name": "a_fn2",
            "last_name": "l2",
            "patronymic": "p2",
            "birthday": "1970-05-20",
        },
        {
            "id": 3,
            "first_name": "a_fn2",
            "last_name": "l3",
            "patronymic": "p3",
            "birthday": "1970-05-20",
        },
    ]
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_invalid_filter_get():
    client = Client()
    response = client.get("/api/authors/?first_name_=a_fn2")
    response_body = response.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_valid_get():
    client = Client()
    response = client.get("/api/authors/1/")
    response_body = response.json()
    expected_response = {
        "id": 1,
        "first_name": "a_fn1",
        "last_name": "l1",
        "patronymic": "p1",
        "birthday": "1970-05-20",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_invalid_get():
    client = Client()
    response = client.get("/api/authors/10/")
    response_body = response.json()
    expected_response = {"Error": "Author with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_get():
    client = Client()
    response = client.get("/api/books/")
    response_body = response.json()
    expected_response = [
        {
            "id": 1,
            "name": "b1",
            "authors": ["a_fn1 l1 p1"],
            "genre": "g1",
            "publication_date": "1990-01-01",
        },
        {
            "id": 2,
            "name": "b2",
            "authors": ["a_fn1 l1 p1", "a_fn2 l2 p2"],
            "genre": "g2",
            "publication_date": "1990-01-01",
        },
        {
            "id": 3,
            "name": "b3",
            "authors": ["a_fn2 l3 p3"],
            "genre": "g1",
            "publication_date": "1990-01-01",
        },
    ]
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_valid_filter_get():
    client = Client()
    response = client.get("/api/books/?genre=g1")
    response_body = response.json()
    expected_response = [
        {
            "id": 1,
            "name": "b1",
            "authors": ["a_fn1 l1 p1"],
            "genre": "g1",
            "publication_date": "1990-01-01",
        },
        {
            "id": 3,
            "name": "b3",
            "authors": ["a_fn2 l3 p3"],
            "genre": "g1",
            "publication_date": "1990-01-01",
        },
    ]
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_invalid_filter_get():
    client = Client()
    response = client.get("/api/books/?genre_=g1")
    response_body = response.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert response.status_code == 400
    assert response_body == expected_response


def test_books_invalid_authors_filter_get():
    client = Client()
    response = client.get("/api/books/?authors=ggg")
    response_body = response.json()
    expected_response = {"Error": "Invalid authors query parameter"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_get():
    client = Client()
    response = client.get("/api/books/1/")
    response_body = response.json()
    expected_response = {
        "id": 1,
        "name": "b1",
        "authors": ["a_fn1 l1 p1"],
        "genre": "g1",
        "publication_date": "1990-01-01",
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_invalid_get():
    client = Client()
    response = client.get("/api/books/10/")
    response_body = response.json()
    expected_response = {"Error": "Book with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post():
    client = Client()
    body = {
        "name": "b6",
        "authors": ["1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
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
def test_books_id_put():
    client = Client()
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
        "publication_date": "2011-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.put(
        "/api/books/1/", data=json_body, content_type="application/json"
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
