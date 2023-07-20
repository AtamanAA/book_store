import json
import pathlib

import pytest
from django.core.management import call_command
from django.test import Client

root = pathlib.Path(__file__).parent


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


@pytest.mark.django_db
def test_books_get():
    client = Client()
    response = client.get("/api/books/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/books_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_valid_filter_get():
    client = Client()
    response = client.get("/api/books/?genre=g1")
    response_body = response.json()
    expected_response = json.load(
        open(root / "fixtures/books_filter_by_genre_get_response.json")
    )
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
    expected_response = json.load(open(root / "fixtures/books_id_get_response.json"))
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
def test_books_post_valid():
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
        "count": 0,
        "price": 1000,
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_json():
    client = Client()
    body = {
        "name": "b6",
        "authors": ["1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
    }
    response = client.post(
        "/api/books/",
        data=body,
    )
    response_body = response.json()
    expected_response = {"Error": "Invalid json"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_type():
    client = Client()
    body = {
        "name": "b4",
        "authors": ["1"],
        "genre": 2,
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Invalid type or empty fields"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_long_name():
    client = Client()
    long_name = 130 * "b"
    body = {
        "name": long_name,
        "authors": ["1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Name field is too long"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_long_genre():
    client = Client()
    long_genre = 130 * "b"
    body = {
        "name": "b4",
        "authors": ["1"],
        "genre": long_genre,
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Genre field is too long"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_author_type():
    client = Client()
    body = {
        "name": "b4",
        "authors": "bbb",
        "genre": "g4",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Invalid authors field"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_data():
    client = Client()
    body = {
        "name": "b4",
        "authors": "1",
        "genre": "g4",
        "publication_date": "2023",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Invalid publication_date field"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_invalid_author_not_found():
    client = Client()
    body = {
        "name": "b4",
        "authors": "4",
        "genre": "g4",
        "publication_date": "2023-05-20",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "/api/books/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Author with id=4 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_all_field():
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
        "count": 10,
        "price": 10000,
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_some_field():
    client = Client()
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
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
        "publication_date": "1990-01-01",
        "count": 10,
        "price": 10000,
    }
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_invalid_type():
    client = Client()
    body = {
        "name": "update_name",
        "authors": 1,
        "genre": 2,
    }
    json_body = json.dumps(body, indent=4)
    response = client.put(
        "/api/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Invalid type or empty fields"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_long_name():
    client = Client()
    long_name = 130 * "b"
    body = {
        "name": long_name,
        "authors": 1,
        "genre": 2,
    }
    json_body = json.dumps(body, indent=4)
    response = client.put(
        "/api/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Name field is too long"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_long_genre():
    client = Client()
    long_genre = 130 * "b"
    body = {
        "name": "update_name",
        "authors": 1,
        "genre": long_genre,
    }
    json_body = json.dumps(body, indent=4)
    response = client.put(
        "/api/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Genre field is too long"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_invalid_data():
    client = Client()
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
        "publication_date": "2011",
    }
    json_body = json.dumps(body, indent=4)
    response = client.put(
        "/api/books/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Invalid publication_date field"}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_put_invalid_id():
    client = Client()
    body = {
        "name": "update_name",
        "authors": [3],
        "genre": "new_genre",
        "publication_date": "2011-01-01",
    }
    json_body = json.dumps(body, indent=4)
    response = client.put(
        "/api/books/10/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": f"Book with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_delete():
    client = Client()
    response = client.delete("/api/books/1/")
    response_body = response.json()
    expected_response = {"Success": "Book with id=1 success delete"}
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_delete_invalid_id():
    client = Client()
    response = client.delete("/api/books/10/")
    response_body = response.json()
    expected_response = {"Error": f"Book with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_get():
    client = Client()
    response = client.get("/api/authors/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/authors_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_valid_filter_get():
    client = Client()
    response = client.get("/api/authors/?first_name=a_fn2")
    response_body = response.json()
    expected_response = json.load(
        open(root / "fixtures/authors_filter_get_response.json")
    )
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
    expected_response = json.load(open(root / "fixtures/authors_id_get_response.json"))
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
