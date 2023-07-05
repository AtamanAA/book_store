import os

import requests

# BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v2/")
BASE_URL = os.getenv(
    "API_URL", "https://ataman-book-store-71ea28220527.herokuapp.com/api/v2/"
)


REQUIRED_BOOK_FIELDS = ["id", "name", "authors", "genre", "publication_date"]

# TEST_ID = {"test_author_id": None,
#            "test_book_id": None
#            }


def test_books_get():
    r = requests.get(BASE_URL + "books/")
    assert r.status_code == 200


def test_authors_get():
    r = requests.get(BASE_URL + "authors/")
    assert r.status_code == 200


def test_authors_post_valid():
    body = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "patronymic": "test-patronymic",
        "birthday": "1970-05-20",
    }
    r = requests.post(BASE_URL + "authors/", json=body)
    assert r.status_code == 200


def test_authors_post_empty_json():
    body = {}
    r = requests.post(BASE_URL + "authors/", json=body)
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
    r = requests.post(BASE_URL + "authors/", json=body)
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
    r = requests.post(BASE_URL + "authors/", json=body)
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
    r = requests.post(BASE_URL + "authors/", json=body)
    response_body = r.json()
    expected_response = {
        "birthday": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_valid():
    author_response = requests.get(BASE_URL + "authors/?first_name=test_first_name")
    test_author_id = author_response.json()[0]["id"]
    body = {
        "name": "test_book",
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(BASE_URL + "books/", json=body)
    assert r.status_code == 200


def test_books_post_empty_json():
    body = {}
    r = requests.post(BASE_URL + "books/", json=body)
    response_body = r.json()
    expected_response = {
        "name": ["This field is required."],
        "genre": ["This field is required."],
        "publication_date": ["This field is required."],
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_long_name():
    author_response = requests.get(BASE_URL + "authors/")
    test_author_id = author_response.json()[0]["id"]
    long_name = 130 * "b"
    body = {
        "name": long_name,
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(BASE_URL + "books/", json=body)
    response_body = r.json()
    expected_response = {"name": ["Ensure this field has no more than 128 characters."]}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_long_genre():
    author_response = requests.get(BASE_URL + "authors/")
    test_author_id = author_response.json()[0]["id"]
    long_genre = 130 * "b"
    body = {
        "name": "test_name",
        "authors": [test_author_id],
        "genre": long_genre,
        "publication_date": "2023-05-20",
    }
    r = requests.post(BASE_URL + "books/", json=body)
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
    r = requests.post(BASE_URL + "books/", json=body)
    response_body = r.json()
    expected_response = {"authors": ['Expected a list of items but got type "str".']}
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_invalid_data():
    author_response = requests.get(BASE_URL + "authors/")
    test_author_id = author_response.json()[0]["id"]
    body = {
        "name": "test_name",
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023",
    }
    r = requests.post(BASE_URL + "books/", json=body)
    response_body = r.json()
    expected_response = {
        "publication_date": [
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
        ]
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_post_invalid_author_not_found():
    author_response = requests.get(BASE_URL + "authors/")
    test_author_id = (
        author_response.json()[0]["id"] + 100
    )  # Find max ID in JSON!!!!!!!!!!!!!!!!!!!
    body = {
        "name": "test_name",
        "authors": [test_author_id],
        "genre": "test_genre",
        "publication_date": "2023-05-20",
    }
    r = requests.post(BASE_URL + "books/", json=body)
    response_body = r.json()
    expected_response = {
        "authors": [f'Invalid pk "{test_author_id}" - object does not exist.']
    }
    assert r.status_code == 400
    assert response_body == expected_response


def test_books_put_valid():
    book_response = requests.get(BASE_URL + "books/?name=test_book")
    test_book_id = book_response.json()[0]["id"]
    body = {
        "name": "update_test_book",
        "genre": "update_test_genre",
    }
    r = requests.put(BASE_URL + f"books/{test_book_id}/", json=body)
    assert r.status_code == 200


def test_books_id_put_invalid_id():
    book_response = requests.get(BASE_URL + "books/")
    test_book_id = (
        book_response.json()[0]["id"] + 100
    )  # Find max ID in JSON!!!!!!!!!!!!!!!!!!!
    body = {
        "name": "update_test_book",
        "genre": "update_test_genre",
    }
    r = requests.put(BASE_URL + f"books/{test_book_id}/", json=body)
    response_body = r.json()
    expected_response = {"Error": f"Book with id={test_book_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_books_delete():
    book_response = requests.get(BASE_URL + "books/?name=update_test_book")
    test_book_id = book_response.json()[0]["id"]
    r = requests.delete(BASE_URL + f"books/{test_book_id}/")
    assert r.status_code == 200
    r = requests.delete(BASE_URL + f"books/{test_book_id}/")
    assert r.status_code == 404


def test_authors_put_valid():
    author_response = requests.get(BASE_URL + "authors/?first_name=test_first_name")
    test_author_id = author_response.json()[0]["id"]
    body = {
        "first_name": "update_first_name",
        "last_name": "update_last_name",
    }
    r = requests.put(BASE_URL + f"authors/{test_author_id}/", json=body)
    assert r.status_code == 200


def test_authors_id_put_invalid_id():
    author_response = requests.get(BASE_URL + "authors/")
    test_author_id = author_response.json()[0]["id"] + 100  # Find max in JSON
    body = {
        "first_name": "update_first_name",
        "last_name": "update_last_name",
    }
    r = requests.put(BASE_URL + f"authors/{test_author_id}/", json=body)
    response_body = r.json()
    expected_response = {"Error": f"Author with id={test_author_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_authors_delete():
    author_response = requests.get(BASE_URL + "authors/?first_name=update_first_name")
    print(author_response.json())
    test_author_id = author_response.json()[0]["id"]
    r = requests.delete(BASE_URL + f"authors/{test_author_id}/")
    assert r.status_code == 200
    r = requests.delete(BASE_URL + f"authors/{test_author_id}/")
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
    book_response = requests.get(BASE_URL + "books/")
    invalid_test_book_id = (
        len(book_response.json()) + 100
    )  # Find max ID in JSON!!!!!!!!!!!!!!!!!!!
    r = requests.get(BASE_URL + f"books/{invalid_test_book_id}")
    response_body = r.json()
    expected_response = {"Error": f"Book with id={invalid_test_book_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response


def test_authors_invalid_filter_get():
    r = requests.get(BASE_URL + "authors/?first_name_=g1")
    response_body = r.json()
    expected_response = {"Error": "Invalid query parameter name"}
    assert r.status_code == 400
    assert response_body == expected_response


def test_authors_id_invalid_get():
    authors_response = requests.get(BASE_URL + "authors/")
    invalid_test_author_id = (
        len(authors_response.json()) + 100
    )  # Find max ID in JSON!!!!!!!!!!!!!!!!!!!
    r = requests.get(BASE_URL + f"authors/{invalid_test_author_id}")
    response_body = r.json()
    expected_response = {"Error": f"Author with id={invalid_test_author_id} not found"}
    assert r.status_code == 404
    assert response_body == expected_response
