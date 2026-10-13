"""Part 3: a small web front end for product reviews.

Run with:  flask --app app run
"""

from flask import Flask, redirect, request

from reviews import ReviewStore, render_reviews

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Reviews</title></head>
<body>
<h1>Reviews for {product}</h1>
{reviews}
<form method="post">
  <input name="author" placeholder="Your name">
  <input name="rating" type="number" min="1" max="5">
  <textarea name="text"></textarea>
  <button type="submit">Post review</button>
</form>
</body></html>"""


def create_app(store=None):
    app = Flask(__name__)
    store = store or ReviewStore()

    @app.get("/products/<product>/reviews")
    def show_reviews(product):
        return PAGE.format(product=product, reviews=render_reviews(store.reviews_for(product)))

    @app.post("/products/<product>/reviews")
    def add_review(product):
        store.add_review(
            product,
            request.form.get("author", ""),
            request.form.get("rating", ""),
            request.form.get("text", ""),
        )
        return redirect(request.path, code=303)

    return app


app = create_app()
