# Project walkthrough

Read this after [Setup](README.md#setup) and before Part 1. It explains what each file in `starter/` does, how the tests are put together, and what you should see the first time you run them. It does not tell you how to fix anything: that is the lab.

## The files

```
starter/
├── shopping_cart.py        Part 1: empty, you build it with TDD
├── test_shopping_cart.py   Part 1: one test written for you
├── reviews.py              Part 2: review storage + HTML rendering (has flaws)
├── test_reviews.py         Part 2: functional tests + security test tables
├── app.py                  Part 3: Flask web page on top of reviews.py
├── test_app.py             Part 3: tests that drive the web app
└── .vscode/                VS Code settings (see VSCODE.md)
```

Each part has one code file and one test file with the same name plus `test_`. pytest finds every file named `test_*.py` and runs every function in it named `test_*`.

The three parts build on each other: `app.py` imports `reviews.py`, so the fixes you make in Part 2 also protect the web page in Part 3.

```
browser ──HTTP──▶ app.py ──calls──▶ reviews.py ──SQL──▶ SQLite (in memory)
                    ▲                   ▲
               test_app.py         test_reviews.py
```

---

## Part 1: `shopping_cart.py` and `test_shopping_cart.py`

`shopping_cart.py` contains only a docstring. There is no code yet, on purpose.

`test_shopping_cart.py` starts like this:

```python
from shopping_cart import Product, ShoppingCart

# Requirement 1: a new shopping cart is empty
def test_new_cart_is_empty():
    cart = ShoppingCart()
    assert len(cart.products) == 0
```

- The `import` line names the two classes you will create. Because neither exists, this file cannot even be loaded. That is your first **Red**: an `ImportError`, not a failed assertion.
- A test is a plain function. It sets something up (`cart = ShoppingCart()`), then states what must be true with `assert`. If the assertion is false, the test fails and pytest shows you both sides of the comparison.
- The rest of the file is comments, one per requirement (R2 to R5), marking where your tests go.

**Things to notice**

- The requirements table in the README fixes the names (`add_product`, `total`, `remove_product`, ...). Use them exactly, because the instructor's tests import them.
- To test that something raises an error, use `pytest.raises`:

  ```python
  with pytest.raises(ValueError):
      something_that_should_fail()
  ```

- When you compare decimal prices, `0.1 + 0.2 == 0.3` is `False` in Python. `pytest.approx` helps: `assert cart.total == pytest.approx(0.3)`.

---

## Part 2: `reviews.py` and `test_reviews.py`

### The code

`reviews.py` stores product reviews in an SQLite database and turns them into HTML. It has four pieces:

| Name | What it is |
|------|------------|
| `ValidationError` | An exception for rejected input. It is defined but **never raised** yet. You will raise it. |
| `Review` | A `@dataclass` with `author`, `rating` and `text`. Two `Review`s with the same values compare equal, which keeps the tests short. |
| `ReviewStore` | Wraps the database. `ReviewStore()` uses `":memory:"`, a fresh database that lives only as long as the object, so every test starts empty. |
| `render_reviews(reviews)` | Builds a `<ul>` of `<li>` items, one per review. |

`ReviewStore` methods:

| Method | What it does |
|--------|--------------|
| `__init__` | Opens the database and creates the `reviews` table. |
| `add_review(product, author, rating, text)` | Inserts one row. |
| `reviews_for(product)` | Returns a list of `Review` objects for one product, oldest first. |
| `table_exists()` | Returns `True` if the `reviews` table is still there. It exists only so tests can check whether an attack destroyed the table. |

Read `add_review`, `reviews_for` and `render_reviews` carefully and ask yourself: **how does the user's input end up inside the SQL query or the HTML?** That question is the heart of Part 2.

### The tests

The file is divided into blocks by comment banners.

**1. A fixture.**

```python
@pytest.fixture
def store():
    return ReviewStore()
```

A fixture is set-up code that pytest runs for you. Any test that has a parameter called `store` receives a new, empty `ReviewStore`. Tests never share data, so the order they run in does not matter.

**2. The teammate's functional tests.** Three tests check the user story: you can add a review and read it back, reviews are kept per product, and the HTML shows author, rating and text. These pass on the starter code, and they must **still pass** after your security fixes.

**3. Abuser story A2 (SQL injection).** A table of inputs and one test that uses it:

```python
SQLI_PAYLOADS = [
    "It's great!",
    "x'); DROP TABLE reviews; --",
    ...
]

@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_sql_in_review_text_is_stored_as_plain_text(store, payload):
    store.add_review("widget", "mallory", 3, payload)
    assert store.table_exists()
    assert store.reviews_for("widget")[-1].text == payload
```

`@pytest.mark.parametrize` runs the test once for every item in the list, passing it in as `payload`. One function becomes four tests, and pytest reports each one separately with the payload in brackets:

```
FAILED test_reviews.py::test_sql_in_review_text_is_stored_as_plain_text[It's great!]
```

The two assertions say "the attack did not damage the database" and "the input came back exactly as typed, as plain text". This is the worked example; copy its shape for the `TODO`s below it.

**4. Abuser story A1 (XSS).** Only the `XSS_PAYLOADS` table and `TODO` comments. You write the tests. The file already imports `html`, so you can use `html.escape(payload)` in your assertions.

**5. Abuser story A3.** Empty. You choose the abuse case and write the tests.

---

## Part 3: `app.py` and `test_app.py`

### The code

`app.py` is a small [Flask](https://flask.palletsprojects.com) web app with one page, `/products/<product>/reviews`. `<product>` is a variable part of the URL, so `/products/widget/reviews` gives `product = "widget"`.

| Route | What it does |
|-------|--------------|
| `GET` | Fills the `PAGE` HTML template with the product name and `render_reviews(...)`, and returns it. |
| `POST` | Reads `author`, `rating` and `text` from the submitted form, calls `store.add_review`, then redirects back to the same page with status **303**. |

Two details matter later:

- The app is built by a function, `create_app(store=None)`. Tests pass in their own `ReviewStore`, so each test gets a clean database. The last line, `app = create_app()`, is the instance that `flask --app app run` starts.
- The form's `type="number" min="1" max="5"` is checked by the **browser** only. An attacker (or ZAP) can send any value they like straight to the server. Look at what `add_review` receives as `rating`.

### The tests

```python
@pytest.fixture
def client(store):
    return create_app(store).test_client()

def post_review(client, author="alice", rating="5", text="Works well"):
    return client.post(URL, data={"author": author, "rating": rating, "text": text})
```

- Fixtures can use other fixtures: `client` asks for `store`, builds an app around it and returns Flask's **test client**. The test client sends fake HTTP requests directly to the app, with no server or browser needed.
- `post_review` is a helper with sensible defaults. Override only what a test is about, for example `post_review(client, rating="abc")`.
- A response has `.status_code` (such as `303` or `400`), `.data` (the body as **bytes**, which is why the tests write `b"Works well"`) and `.headers` (for the ZAP findings, for example `response.headers.get("X-Content-Type-Options")`).

Two functional tests pass on the starter code. The `TODO`s ask for form-rejection tests and one test per ZAP finding.

---

## What you should see on the first run

From inside `starter/`:

```bash
pytest -q
```

pytest stops straight away with `ImportError: cannot import name 'Product'` and `Interrupted: 1 error during collection`. That is Part 1's first Red. While one test file cannot be imported, pytest runs **no** tests at all, so to look at the other parts before you finish this first step, name their files:

```bash
pytest -q test_reviews.py test_app.py
```

```
FAILED test_reviews.py::test_sql_in_review_text_is_stored_as_plain_text[It's great!]
FAILED test_reviews.py::test_sql_in_review_text_is_stored_as_plain_text[x'); DROP TABLE reviews; --]
FAILED test_reviews.py::test_sql_in_review_text_is_stored_as_plain_text['); DELETE FROM reviews; --]
FAILED test_reviews.py::test_sql_in_review_text_is_stored_as_plain_text[' OR '1'='1]
4 failed, 5 passed
```

The 5 passing tests are the functional ones (3 in `test_reviews.py`, 2 in `test_app.py`). The 4 failures are the worked SQL injection example, one per payload. All of this is expected. Read one of the failure messages now, and work out why even `It's great!` fails, before you start Part 1.

## pytest cheat sheet

| Command | What it does |
|---------|--------------|
| `pytest -q` | Run everything, short output |
| `pytest -q test_reviews.py` | Run one file |
| `pytest -q -k author` | Run tests whose name contains `author` |
| `pytest -q -x` | Stop at the first failure |
| `pytest -q --lf` | Re-run only the tests that failed last time |
| `pytest -v` | List every test name with PASSED or FAILED |
