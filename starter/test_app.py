import pytest

from app import create_app
from reviews import ReviewStore

URL = "/products/widget/reviews"


@pytest.fixture
def store():
    return ReviewStore()


@pytest.fixture
def client(store):
    return create_app(store).test_client()


def post_review(client, author="alice", rating="5", text="Works well"):
    return client.post(URL, data={"author": author, "rating": rating, "text": text})


# Functional behaviour (these already pass)

def test_posting_a_review_redirects_back_to_the_page(client):
    response = post_review(client)
    assert response.status_code == 303


def test_posted_review_is_shown(client):
    post_review(client, text="Works well")
    assert b"Works well" in client.get(URL).data


# TODO (abuser stories through the web form): a POST containing a script, or
#      a rating such as "abc" or "5); DROP TABLE reviews; --", must get a
#      400 response and must not be stored.

# TODO (Part 3, DAST): turn each OWASP ZAP finding into a test BEFORE you
#      fix it. For example, the Content-Security-Policy header must be set.
