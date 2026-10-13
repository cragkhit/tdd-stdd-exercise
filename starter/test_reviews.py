import html

import pytest

from reviews import Review, ReviewStore, ValidationError, render_reviews


@pytest.fixture
def store():
    return ReviewStore()


# ---------------------------------------------------------------------------
# User story: As a customer, I want to add a review of a product so that
# information about products can be shared between customers.
# (Your teammate's functional tests: these already pass.)
# ---------------------------------------------------------------------------

def test_can_add_and_read_a_review(store):
    store.add_review("widget", "alice", 5, "Works well")
    assert store.reviews_for("widget") == [Review("alice", 5, "Works well")]


def test_reviews_are_listed_per_product(store):
    store.add_review("widget", "alice", 5, "Works well")
    store.add_review("gadget", "bob", 2, "Broke after a week")
    assert [r.author for r in store.reviews_for("widget")] == ["alice"]


def test_render_shows_author_rating_and_text():
    page = render_reviews([Review("alice", 4, "Nice")])
    assert "alice" in page and "4/5" in page and "Nice" in page


# ---------------------------------------------------------------------------
# Abuser story A2: An attacker abuses the Review Product function to gain
# unlimited access to the database (SQL injection).
# ---------------------------------------------------------------------------

SQLI_PAYLOADS = [
    "It's great!",  # a legitimate review must not break the query either
    "x'); DROP TABLE reviews; --",
    "'); DELETE FROM reviews; --",
    "' OR '1'='1",
]


# Worked example: "For all inputs in the table, assert that they are stored
# as plain text and the database is intact."
@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_sql_in_review_text_is_stored_as_plain_text(store, payload):
    store.add_review("widget", "mallory", 3, payload)
    assert store.table_exists()
    assert store.reviews_for("widget")[-1].text == payload


# TODO: the same attack through the author field.

# TODO: reviews_for("' OR '1'='1") must not return other products' reviews.

# TODO: a rating of "5); DROP TABLE reviews; --" must raise ValidationError
#       and leave the table in place.


# ---------------------------------------------------------------------------
# Abuser story A1: An attacker uses the Review Product function to spread
# malicious JavaScript (XSS).
# ---------------------------------------------------------------------------

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<ScRiPt>alert(1)</ScRiPt>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    '"><script>alert(document.cookie)</script>',
    '<a href="javascript:alert(1)">click me</a>',
]

# TODO scenario 1: for all inputs in the table, assert that the output of
#      render_reviews() is properly escaped (text AND author).
#      Hint: html.escape(payload) should appear, payload itself should not.

# TODO scenario 2: for all inputs in the table, assert that add_review()
#      rejects the submission with ValidationError (server side).

# TODO: make sure a harmless review such as "Speed: 2 < 3 and 5 > 4" is
#       still accepted. Security fixes must not break functional behaviour.


# ---------------------------------------------------------------------------
# Abuser story A3: write this one yourself. Ideas: ratings outside 1-5,
# ratings that are not integers, empty or very large reviews.
# ---------------------------------------------------------------------------
