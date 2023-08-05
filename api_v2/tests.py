import json
import pathlib

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
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


@pytest.fixture
def api_client_is_staff():
    user = User.objects.create_user(username="test", password="test", is_staff="True")
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
    expected_response = json.load(open(root / "fixtures/books_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_invalid_authors_filter_get(api_client):
    response = api_client.get("/api/v2/books/?authors=ggg")
    response_body = response.json()
    expected_response = {"authors": ["“ggg” is not a valid value."]}
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
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_post_valid_new(api_client):
    body = {
        "name": "b6",
        "authors": ["1"],
        "genre": "g2",
        "publication_date": "2023-05-20",
        "count": 10,
        "price": 10000,
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
        "count": 10,
        "price": 10000,
    }
    assert response.status_code == 201
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
        "count": 10,
        "price": 10000,
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
        "count": 10,
        "price": 10000,
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
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_books_id_delete(api_client):
    response = api_client.delete("/api/v2/books/1/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_books_id_delete_invalid_id(api_client):
    response = api_client.delete("/api/v2/books/10/")
    response_body = response.json()
    expected_response = {"detail": "Not found."}
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
    response = api_client.get("/api/v2/authors/?name=a_fn2")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/authors_get_response.json"))
    assert response.status_code == 200
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
    assert response.status_code == 201
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
    expected_response = {"detail": "Not found."}
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
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_authors_id_delete(api_client):
    response = api_client.delete("/api/v2/authors/1/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_authors_id_delete_invalid_id(api_client):
    response = api_client.delete("/api/v2/authors/10/")
    response_body = response.json()
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_get(api_client):
    response = api_client.get("/api/v2/users/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/users_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_post_valid(api_client):
    body = {"username": "test_user_4", "password": "random4!"}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/users/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "id": 4,
        "username": "test_user_4",
    }
    assert response.status_code == 201
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_post_empty_json(api_client):
    body = {}
    response = api_client.post(
        "/api/v2/users/",
        data=body,
    )
    response_body = response.json()
    expected_response = {
        "username": ["This field is required."],
        "password": ["This field is required."],
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_post_short_password(api_client):
    body = {"username": "test_user_4", "password": "ran"}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/users/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "password": [
            "['This password is too short. It must contain at least 8 characters.']"
        ]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_post_same_username(api_client):
    body = {"username": "test_user_2", "password": "random4!"}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/users/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"username": ["A user with that username already exists."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_valid_get(api_client):
    response = api_client.get("/api/v2/users/1/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/users_id_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_invalid_get(api_client):
    response = api_client.get("/api/v2/users/10/")
    response_body = response.json()
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_put_valid(api_client):
    body = {"username": "update_test", "password": "new_password_3!"}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/users/3/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"id": 3, "username": "update_test"}
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_put_shot_password(api_client):
    body = {"username": "update_test", "password": "nr"}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/users/3/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "password": [
            "['This password is too short. It must contain at least 8 characters.']"
        ]
    }
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_put_another_user(api_client):
    body = {"username": "update_test", "password": "new_password"}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/users/1/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"detail": "You do not have permission to perform this action."}
    assert response.status_code == 403
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_put_not_found(api_client):
    body = {"username": "update_test", "password": "new_password"}
    json_body = json.dumps(body, indent=4)
    response = api_client.put(
        "/api/v2/users/10/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_not_found_id_delete(api_client):
    response = api_client.delete("/api/v2/users/10/")
    response_body = response.json()
    expected_response = {"detail": "Not found."}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_users_id_delete(api_client_is_staff):
    response = api_client_is_staff.delete("/api/v2/users/3/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_orders_get(api_client):
    response = api_client.get("/api/v2/orders/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/orders_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_orders_post_valid_one_book(api_client):
    body = {"books": [{"book_id": 1, "quantity": 2}]}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/orders/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    assert response.status_code == 200
    assert "order_id" and "pageUrl" in response_body


@pytest.mark.django_db
def test_orders_post_valid_two_book(api_client):
    body = {"books": [{"book_id": 1, "quantity": 2}, {"book_id": 2, "quantity": 3}]}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/orders/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    assert response.status_code == 200
    assert "order_id" and "pageUrl" in response_body


@pytest.mark.django_db
def test_orders_post_invalid_book_not_found(api_client):
    body = {"books": [{"book_id": 10, "quantity": 2}]}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/orders/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Book with id 10 not found"}
    assert response.status_code == 404
    assert expected_response == response_body


@pytest.mark.django_db
def test_orders_post_invalid_book_quantity_zero(api_client):
    body = {"books": [{"book_id": 1, "quantity": 0}]}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/orders/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"Error": "Quantity must be more that 0"}
    assert response.status_code == 400
    assert expected_response == response_body


@pytest.mark.django_db
def test_orders_post_invalid_many_count_book(api_client):
    body = {"books": [{"book_id": 3, "quantity": 2}]}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/orders/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {
        "Error": "There are not enough books with id 3 in stock to create an order"
    }
    assert response.status_code == 406
    assert expected_response == response_body


@pytest.mark.django_db
def test_orders_post_invalid_quantity(api_client):
    body = {"books": [{"book_id": 3, "quantity": "one"}]}
    json_body = json.dumps(body, indent=4)
    response = api_client.post(
        "/api/v2/orders/", data=json_body, content_type="application/json"
    )
    response_body = response.json()
    expected_response = {"books": [{"quantity": ["A valid integer is required."]}]}
    assert response.status_code == 400
    assert expected_response == response_body


@pytest.mark.django_db
def test_orders_post_empty_json(api_client):
    body = {}
    response = api_client.post(
        "/api/v2/orders/",
        data=body,
    )
    response_body = response.json()
    expected_response = {"books": ["This field is required."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_orders_post_empty_book_list(api_client):
    body = {"books": []}
    response = api_client.post(
        "/api/v2/orders/",
        data=body,
    )
    response_body = response.json()
    expected_response = {"books": ["This field is required."]}
    assert response.status_code == 400
    assert response_body == expected_response


@pytest.mark.django_db
def test_orders_id_get(api_client):
    response = api_client.get("/api/v2/orders/1/")
    response_body = response.json()
    expected_response = json.load(open(root / "fixtures/orders_id_get_response.json"))
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_orders_id_invalid_get(api_client):
    response = api_client.get("/api/v2/orders/10/")
    response_body = response.json()
    expected_response = {"Error": "Order with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response


@pytest.mark.django_db
def test_orders_id_delete(api_client_is_staff):
    response = api_client_is_staff.delete("/api/v2/orders/1/")
    response_body = response.json()
    expected_response = {"Success": "Order with id=1 success delete"}
    assert response.status_code == 200
    assert response_body == expected_response


@pytest.mark.django_db
def test_orders_id_delete_invalid_id(api_client_is_staff):
    response = api_client_is_staff.delete("/api/v2/orders/10/")
    response_body = response.json()
    expected_response = {"Error": f"Order with id=10 not found"}
    assert response.status_code == 404
    assert response_body == expected_response
