import os

import requests


BASE_URL = os.getenv(
    "API_URL", "https://ataman-book-store-71ea28220527.herokuapp.com/api/v2/"
)

test_id = {}
test_token = {}


def test_books_get():
    r = requests.get(BASE_URL + "books/")
    assert r.status_code == 200


def test_authors_get():
    r = requests.get(BASE_URL + "authors/")
    assert r.status_code == 200


def test_users_post_valid():
    body = {"username": "test_user", "password": "random1!"}
    r = requests.post(BASE_URL + "users/", json=body)
    response_body = r.json()
    test_id["test_user_id"] = response_body["id"]
    assert r.status_code == 201


def test_users_get_token_valid():
    body = {
        "username": "test_user",
        "password": "random1!",
    }
    r = requests.post(BASE_URL + "token/", json=body)
    response_body = r.json()
    test_token["refresh"] = response_body["refresh"]
    test_token["access"] = response_body["access"]
    test_token["token_header"] = {"Authorization": "Bearer " + test_token["access"]}
    assert r.status_code == 200


def test_users_get():
    r = requests.get(BASE_URL + "users/")
    assert r.status_code == 200


def test_users_post_invalid():
    body = {}
    r = requests.post(BASE_URL + "users/", json=body)
    response_body = r.json()
    expected_response = {
        "username": ["This field is required."],
        "password": ["This field is required."],
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_users_post_same_username():
    body = {"username": "test_user", "password": "random4!"}
    r = requests.post(BASE_URL + "users/", json=body)
    response_body = r.json()
    expected_response = {"username": ["A user with that username already exists."]}
    assert r.status_code == 400
    assert response_body == expected_response


def test_users_id_put_valid():
    user_id = test_id["test_user_id"]
    body = {"username": "test_user_update", "password": "random4!"}
    r = requests.put(
        BASE_URL + f"users/{user_id}/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {"id": user_id, "username": "test_user_update"}
    assert r.status_code == 200
    assert response_body == expected_response


def test_users_id_put_shot_password():
    user_id = test_id["test_user_id"]
    body = {"username": "test_user_update", "password": "ran"}
    r = requests.put(
        BASE_URL + f"users/{user_id}/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "password": [
            "['This password is too short. It must contain at least 8 characters.']"
        ]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_users_id_put_not_found():
    user_id = test_id["test_user_id"] + 10
    body = {"username": "test_user_update", "password": "random4!"}
    r = requests.put(
        BASE_URL + f"users/{user_id}/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {"detail": "Not found."}
    assert r.status_code == 404
    assert response_body == expected_response


def test_users_id_put_without_header():
    user_id = test_id["test_user_id"]
    body = {"username": "test_user_update", "password": "random4!"}
    r = requests.put(BASE_URL + f"users/{user_id}/", json=body)
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_users_id_put_invalid_token():
    user_id = test_id["test_user_id"]
    invalid_access_token = test_token["refresh"]
    invalid_header = {"Authorization": "Bearer " + invalid_access_token}
    body = {"username": "test_user_update", "password": "random4!"}
    r = requests.put(
        BASE_URL + f"users/{user_id}/",
        json=body,
        headers=invalid_header,
    )
    response_body = r.json()
    expected_response = {
        "detail": "Given token not valid for any token type",
        "code": "token_not_valid",
        "messages": [
            {
                "token_class": "AccessToken",
                "token_type": "access",
                "message": "Token has wrong type",
            }
        ],
    }
    assert r.status_code == 401
    assert response_body == expected_response


def test_authors_post_valid():
    body = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "patronymic": "test-patronymic",
        "birthday": "1970-05-20",
    }
    r = requests.post(
        BASE_URL + "authors/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    test_id["test_author_id"] = response_body["id"]
    assert r.status_code == 200


def test_authors_post_empty_json():
    body = {}
    r = requests.post(
        BASE_URL + "authors/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "first_name": ["This field is required."],
        "last_name": ["This field is required."],
        "birthday": ["This field is required."],
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_authors_post_long_first_name():
    long_first_name = 130 * "b"
    body = {
        "first_name": long_first_name,
        "last_name": "test_last_name",
        "patronymic": "test-patronymic",
        "birthday": "1970-05-20",
    }
    r = requests.post(
        BASE_URL + "authors/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "first_name": ["Ensure this field has no more than 20 characters."]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_authors_post_long_last_name():
    long_last_name = 130 * "b"
    body = {
        "first_name": "test_first_name",
        "last_name": long_last_name,
        "patronymic": "test-patronymic",
        "birthday": "1970-05-20",
    }
    r = requests.post(
        BASE_URL + "authors/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "last_name": ["Ensure this field has no more than 20 characters."]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_authors_post_invalid_data():
    body = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "patronymic": "test-patronymic",
        "birthday": "1970",
    }
    r = requests.post(
        BASE_URL + "authors/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "birthday": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_authors_post_without_token():
    body = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "patronymic": "test-patronymic",
        "birthday": "1970-05-20",
    }
    r = requests.post(BASE_URL + "authors/", json=body)
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_authors_put_without_token():
    author_id = test_id["test_author_id"]
    body = {
        "first_name": "update_first_name",
    }
    r = requests.put(BASE_URL + f"authors/{author_id}/", json=body)
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_books_post_valid():
    test_author_id = test_id["test_author_id"]
    body = {
        "name": "test_book",
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    test_id["test_book_id"] = response_body["id"]
    assert r.status_code == 200


def test_books_post_empty_json():
    body = {}
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "name": ["This field is required."],
        "genre": ["This field is required."],
        "publication_date": ["This field is required."],
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_long_name():
    test_author_id = test_id["test_author_id"]
    long_name = 130 * "b"
    body = {
        "name": long_name,
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {"name": ["Ensure this field has no more than 128 characters."]}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_long_genre():
    test_author_id = test_id["test_author_id"]
    long_genre = 130 * "b"
    body = {
        "name": "test_name",
        "authors": [test_author_id],
        "genre": long_genre,
        "publication_date": "2023-05-20",
    }
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {"genre": ["Ensure this field has no more than 40 characters."]}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_invalid_author_type():
    body = {
        "name": "test_name",
        "authors": "bbb",
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {"authors": ['Expected a list of items but got type "str".']}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_invalid_data():
    test_author_id = test_id["test_author_id"]
    body = {
        "name": "test_name",
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023",
    }
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "publication_date": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_invalid_author_not_found():
    author_id = test_id["test_author_id"] + 10
    body = {
        "name": "test_name",
        "authors": [author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(
        BASE_URL + "books/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {
        "authors": [f'Invalid pk "{author_id}" - object does not exist.']
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_without_header():
    test_author_id = test_id["test_author_id"]
    body = {
        "name": "test_book",
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(BASE_URL + "books/", json=body)
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_books_put_valid():
    book_id = test_id["test_book_id"]
    body = {
        "name": "update_test_book",
        "genre": "update_test_genre",
    }
    r = requests.put(
        BASE_URL + f"books/{book_id}/", json=body, headers=test_token["token_header"]
    )
    assert r.status_code == 200


def test_books_id_put_invalid_id():
    book_id = test_id["test_book_id"] + 10
    body = {
        "name": "update_test_book",
        "genre": "update_test_genre",
    }
    r = requests.put(
        BASE_URL + f"books/{book_id}/", json=body, headers=test_token["token_header"]
    )
    response_body = r.json()
    expected_response = {"Error": f"Book with id={book_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_books_id_put_without_header():
    book_id = test_id["test_book_id"] + 10
    body = {
        "name": "update_test_book",
        "genre": "update_test_genre",
    }
    r = requests.put(BASE_URL + f"books/{book_id}/", json=body)
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_books_delete_without_header():
    books_id = test_id["test_book_id"]
    r = requests.delete(BASE_URL + f"books/{books_id}/")
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_books_delete():
    book_id = test_id["test_book_id"]
    r = requests.delete(
        BASE_URL + f"books/{book_id}/", headers=test_token["token_header"]
    )
    assert r.status_code == 200
    r = requests.delete(
        BASE_URL + f"books/{book_id}/", headers=test_token["token_header"]
    )
    assert r.status_code == 404


def test_authors_put_valid():
    author_id = test_id["test_author_id"]
    body = {
        "first_name": "update_first_name",
        "last_name": "update_last_name",
    }
    r = requests.put(
        BASE_URL + f"authors/{author_id}/",
        json=body,
        headers=test_token["token_header"],
    )
    assert r.status_code == 200


def test_authors_id_put_invalid_id():
    author_id = test_id["test_author_id"] + 10
    body = {
        "first_name": "update_first_name",
        "last_name": "update_last_name",
    }
    r = requests.put(
        BASE_URL + f"authors/{author_id}/",
        json=body,
        headers=test_token["token_header"],
    )
    response_body = r.json()
    expected_response = {"Error": f"Author with id={author_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_authors_delete_without_header():
    author_id = test_id["test_author_id"]
    r = requests.delete(BASE_URL + f"authors/{author_id}/")
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_authors_delete():
    author_id = test_id["test_author_id"]
    r = requests.delete(
        BASE_URL + f"authors/{author_id}/", headers=test_token["token_header"]
    )
    assert r.status_code == 200
    r = requests.delete(
        BASE_URL + f"authors/{author_id}/", headers=test_token["token_header"]
    )
    assert r.status_code == 404


def test_books_invalid_filter_get():
    r = requests.get(BASE_URL + "books/?genre_=g1")
    response_body = r.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_invalid_authors_filter_get():
    r = requests.get(BASE_URL + "books/?authors=ggg")
    response_body = r.json()
    expected_response = {"Error": "Invalid authors query parameter"}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_id_invalid_get():
    book_id = test_id["test_book_id"] + 10
    r = requests.get(BASE_URL + f"books/{book_id}")
    response_body = r.json()
    expected_response = {"Error": f"Book with id={book_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_authors_invalid_filter_get():
    r = requests.get(BASE_URL + "authors/?first_name_=g1")
    response_body = r.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert r.status_code == 400
    assert response_body == expected_response


def test_authors_id_invalid_get():
    author_id = test_id["test_author_id"] + 10
    r = requests.get(BASE_URL + f"authors/{author_id}")
    response_body = r.json()
    expected_response = {"Error": f"Author with id={author_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_users_delete_invalid():
    body_admin_token = {
        "username": "admin",
        "password": "random1!",
    }
    r = requests.post(BASE_URL + "token/", json=body_admin_token)
    response_body = r.json()
    admin_token = {"Authorization": "Bearer " + response_body["access"]}
    user_id = test_id["test_user_id"] + 1
    r = requests.delete(BASE_URL + f"users/{user_id}/", headers=admin_token)
    response_body = r.json()
    expected_response = {"detail": "Not found."}
    assert r.status_code == 404
    assert response_body == expected_response


def test_users_delete_without_token():
    user_id = test_id["test_user_id"]
    r = requests.delete(BASE_URL + f"users/{user_id}/")
    response_body = r.json()
    expected_response = {"detail": "Authentication credentials were not provided."}
    assert r.status_code == 401
    assert response_body == expected_response


def test_users_delete_valid():
    body_admin_token = {
        "username": "admin",
        "password": "random1!",
    }
    r = requests.post(BASE_URL + "token/", json=body_admin_token)
    response_body = r.json()
    admin_token = {"Authorization": "Bearer " + response_body["access"]}
    user_id = test_id["test_user_id"]
    r = requests.delete(BASE_URL + f"users/{user_id}/", headers=admin_token)
    assert r.status_code == 204
