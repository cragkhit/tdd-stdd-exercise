"""Part 2: product reviews.

Written by a teammate with TDD. All of their functional tests pass...
but nobody wrote any abuser stories.
"""

import sqlite3
from dataclasses import dataclass


class ValidationError(ValueError):
    pass


@dataclass
class Review:
    author: str
    rating: int
    text: str


class ReviewStore:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS reviews ("
            "id INTEGER PRIMARY KEY, product TEXT NOT NULL, author TEXT NOT NULL, "
            "rating INTEGER NOT NULL, text TEXT NOT NULL)"
        )

    def add_review(self, product, author, rating, text):
        self.conn.executescript(
            f"INSERT INTO reviews (product, author, rating, text) "
            f"VALUES ('{product}', '{author}', {rating}, '{text}')"
        )

    def reviews_for(self, product):
        rows = self.conn.execute(
            f"SELECT author, rating, text FROM reviews WHERE product = '{product}' ORDER BY id"
        ).fetchall()
        return [Review(*row) for row in rows]

    def table_exists(self):
        row = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'reviews'"
        ).fetchone()
        return row is not None


def render_reviews(reviews):
    items = "".join(f"<li><b>{r.author}</b> ({r.rating}/5): {r.text}</li>" for r in reviews)
    return f'<ul class="reviews">{items}</ul>'
