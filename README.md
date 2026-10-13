# ITCY 553 Lab: TDD and Security TDD (STDD) in Python

In this lab you practise the **Red → Green → Refactor** cycle, then use it to find and fix security flaws. You will turn **abuser stories** into tests and use a static scanner (SAST) and a dynamic scanner (DAST) along the way.

| Part | Topic | Time | Files |
|------|-------|------|-------|
| 1 | TDD: shopping cart | 45 min | `shopping_cart.py`, `test_shopping_cart.py` |
| 2 | STDD: product reviews (SAST + abuser stories) | 75 min | `reviews.py`, `test_reviews.py` |
| 3 | STDD: web form + DAST (OWASP ZAP) | 45 min | `app.py`, `test_app.py` |

**Learning outcomes.** By the end of the lab you can:

1. Write a failing test before you write any code, then write only enough code to make it pass.
2. Derive abuser stories from a user story, and test scenarios from the abuser stories.
3. Use SAST and DAST findings to drive new tests.
4. Fix security flaws without breaking functional behaviour.

After setting up, read the **[project walkthrough](#project-walkthrough)**. It explains what each file and test does and what to expect when you first run the tests.

---

## Setup

You need Python 3.9 or newer. You can set up the lab from the command line or in VS Code. Both give you the same `.venv` folder inside `starter/`, so you can switch between them at any time.

### Option A: Command line

```bash
cd starter
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
pytest -q                          # stops with an ImportError at first: that is expected
```

Run one file with `pytest -q test_shopping_cart.py`, and one test with `pytest -q -k new_cart`.

### Option B: VS Code (GUI)

1. Install [VS Code](https://code.visualstudio.com) and the **Python** extension by Microsoft (*Extensions* view, `Ctrl+Shift+X` / `Cmd+Shift+X`, search for "Python").
2. Choose *File → Open Folder…* and open the **`starter`** folder, not the repository root. If VS Code asks whether you trust the authors, click *Yes, I trust the authors*.
3. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`), run **Python: Create Environment**, choose **Venv**, then choose Python 3.9 or newer. VS Code creates `.venv` and selects it as the interpreter. It will not offer `requirements.txt`, because the file is one folder up; skip that step.
4. Open a new terminal with *Terminal → New Terminal*. VS Code activates the virtual environment for you, so the prompt starts with `(.venv)`. Install the packages:

   ```bash
   pip install -r ../requirements.txt
   ```

5. Click the **Testing** icon (the beaker) in the left Activity Bar. pytest is already configured in `starter/.vscode/settings.json`, so the tests are discovered automatically. If VS Code instead shows a *Configure Python Tests* button, choose **pytest** → **`.` (root directory)**.
6. The tests appear in a tree. Click the ▷ button at the top to run all tests, or the ▷ next to a file or a single test to run only that one. You can also click the ▷ in the editor gutter next to each `def test_...`.

Failing tests show a red ✗, passing tests a green ✓, which is exactly the Red → Green cycle you record in your TDD log. Click a failed test to see its failure message. To step through a test, set a breakpoint by clicking left of a line number, then right-click the test and choose *Debug Test*.

If the tests do not appear, or to run the Flask app from VS Code in Part 3, see [VSCODE.md](VSCODE.md).

### Setting up Bandit (SAST)

[Bandit](https://bandit.readthedocs.io) is a static analysis tool for Python. It is listed in `requirements.txt`, so the `pip install` above already installed it into your virtual environment. Check that it works:

```bash
bandit --version                   # should print "bandit 1.7.5" or newer
bandit reviews.py app.py           # scan the application code
```

The scan should report two B608 (SQL injection) issues in `reviews.py`. That is expected: you will fix them in Part 2.

If `bandit: command not found` appears:

- Make sure the virtual environment is active. Your prompt should start with `(.venv)`; if it does not, run `source .venv/bin/activate` again (Windows: `.venv\Scripts\activate`).
- Install it on its own with `pip install "bandit>=1.7.5"`.
- Run it through Python instead: `python -m bandit reviews.py app.py`.

Useful options:

| Command | What it does |
|---------|--------------|
| `bandit reviews.py app.py` | Scan specific files |
| `bandit -r . -x ./.venv -s B101` | Scan the whole folder, skipping the virtual environment and the B101 warning that every `assert` in the test files would trigger |
| `bandit -ll reviews.py` | Show only medium and high severity issues (`-lll` for high only) |
| `bandit -f html -o bandit-before.html reviews.py app.py` | Save the report as HTML, handy for the "before" and "after" outputs in your report |

### Setting up OWASP ZAP (DAST)

[ZAP](https://www.zaproxy.org) scans a **running** web application. You only need it in Part 3, but install it before the lab, because the download is large.

Download ZAP from <https://www.zaproxy.org/download/>. Each installer is about 250 MB. Follow the steps for your operating system.

**macOS**

1. Check your Mac's chip: Apple menu → *About This Mac*. Download the **macOS (Apple Silicon)** installer for an M-series chip, or the **macOS (Intel)** installer for an Intel chip. Both include the Java runtime, so you do not need to install Java.
2. Open the `.dmg` file and drag *ZAP* into *Applications*.
3. ZAP releases are not signed, so the first launch shows *"ZAP" cannot be opened because the developer cannot be verified*. Click *Done*, then go to *System Settings → Privacy & Security*, scroll down and click *Open Anyway* next to the message about ZAP.

If you use Homebrew, `brew install --cask zap` does steps 1 and 2 for you.

**Windows**

1. ZAP for Windows needs **Java 17 or newer**. Check with `java -version` in a terminal. If Java is missing or older than 17, install the *Temurin 17 (LTS)* or newer JDK from <https://adoptium.net>, then open a **new** terminal and check again.
2. Download the **Windows (64) Installer** and run it. If Windows SmartScreen says it protected your PC, click *More info → Run anyway*. ZAP releases are not signed, so this warning is expected.
3. Accept the default options and finish the installer. Start ZAP from the Start menu.

Alternatively, `winget install --id=ZAP.ZAP -e` installs ZAP, but you still need Java 17 or newer.

**Linux**

1. Install Java 17 or newer, for example `sudo apt install openjdk-17-jre` on Ubuntu or Debian, and check with `java -version`.
2. Install ZAP with `sudo snap install zaproxy --classic`, or download the **Linux Installer** (`.sh` file) and run `bash ZAP_*_unix.sh`.
3. Start ZAP from your applications menu, or run `zaproxy` if you installed the snap.

**First start (all systems)**

1. When ZAP asks whether to persist the session, choose *No, I do not want to persist this session*, then click *Start*.
2. If ZAP offers to update add-ons, accept. The download takes a minute.
3. You should see the *Quick Start* tab with an *Automated Scan* button. ZAP is ready.

If ZAP does not start on Windows or Linux, the usual cause is an old Java version. Run `java -version` and check that it reports 17 or newer.

> Scan only applications that you run yourself, such as the lab app on `localhost`. Scanning other people's sites without permission may be illegal.

Keep a **TDD log** as you go: one row per cycle. You will hand it in.

| # | Test written | Red? (failure message) | Code change to go green | Refactoring |
|---|--------------|------------------------|-------------------------|-------------|
| 1 | `test_new_cart_is_empty` | `ImportError: cannot import name 'Product'` | Added empty `ShoppingCart` and `Product` classes | none |

---

## Project walkthrough

Read this after Setup and before Part 1. It explains what each file in `starter/` does, how the tests are put together, and what you should see the first time you run them. It does not tell you how to fix anything: that is the lab.

### The files

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

### Part 1: `shopping_cart.py` and `test_shopping_cart.py`

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

### Part 2: `reviews.py` and `test_reviews.py`

#### The code

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

#### The tests

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

### Part 3: `app.py` and `test_app.py`

#### The code

`app.py` is a small [Flask](https://flask.palletsprojects.com) web app with one page, `/products/<product>/reviews`. `<product>` is a variable part of the URL, so `/products/widget/reviews` gives `product = "widget"`.

| Route | What it does |
|-------|--------------|
| `GET` | Fills the `PAGE` HTML template with the product name and `render_reviews(...)`, and returns it. |
| `POST` | Reads `author`, `rating` and `text` from the submitted form, calls `store.add_review`, then redirects back to the same page with status **303**. |

Two details matter later:

- The app is built by a function, `create_app(store=None)`. Tests pass in their own `ReviewStore`, so each test gets a clean database. The last line, `app = create_app()`, is the instance that `flask --app app run` starts.
- The form's `type="number" min="1" max="5"` is checked by the **browser** only. An attacker (or ZAP) can send any value they like straight to the server. Look at what `add_review` receives as `rating`.

#### The tests

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

### What you should see on the first run

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

### pytest cheat sheet

| Command | What it does |
|---------|--------------|
| `pytest -q` | Run everything, short output |
| `pytest -q test_reviews.py` | Run one file |
| `pytest -q -k author` | Run tests whose name contains `author` |
| `pytest -q -x` | Stop at the first failure |
| `pytest -q --lf` | Re-run only the tests that failed last time |
| `pytest -v` | List every test name with PASSED or FAILED |

---

## Part 1: TDD warm-up (shopping cart)

This is the shopping-basket example from the lecture, written in Python. `shopping_cart.py` is empty. The first test has been written for you.

**Rules**

- Never write production code without a failing test that needs it.
- Write **one** test at a time. Run it and **see it fail** before you write code.
- Write the **simplest** code that makes the test pass, even if it looks silly (for example, `return 25`). The next test will force you to generalise.
- Refactor only when all tests are green, and re-run the tests after every refactoring.

**Requirements.** Use these names so that the instructor's tests can run against your code.

| # | Requirement | API to use |
|---|-------------|------------|
| R1 | A new shopping cart is empty | `ShoppingCart()`, `cart.products` |
| R2 | Products can be added to the cart. Code outside the cart must not be able to change `cart.products` directly. | `Product(name, price)`, `cart.add_product(p)` |
| R3 | The cart calculates the total price (an empty cart totals 0; decimal prices work) | `cart.total` |
| R4 | A product can be removed. Removing a product that is not in the cart raises `ValueError`. | `cart.remove_product(p)` |
| R5 | A product price must not be negative (`ValueError`) | `Product("x", -1)` |

> **Think:** R5 looks like an ordinary business rule, but it is also a security requirement. What could an attacker do if negative prices were allowed? The same question applies to R2.

**Checkpoint 1:** all tests pass, and your TDD log has at least 8 rows.

---

## Part 2: Security TDD (product reviews)

A teammate built a product review feature using TDD. Their functional tests pass, but they never thought about attackers. You will follow the STDD loop from the lecture:

```
SAST scan → add a security test → run tests (RED) → fix code following
security guidelines → run tests (GREEN, functional tests still pass) → refactor → repeat
```

### Step 2.1: Static scan (SAST)

```bash
bandit reviews.py app.py
```

Write down each finding: its ID, line number, severity and confidence. Look up what the ID means at <https://bandit.readthedocs.io>.

> SAST tells you **where** the code looks risky. It does not prove that the code can be exploited. Your next job is to prove it with a test.

### Step 2.2: From user story to abuser stories

**User story:** *As a customer, I want to add a review of a product so that information about products can be shared between customers.*

| ID | Abuser story | Test scenarios |
|----|--------------|----------------|
| A1 | An attacker uses the Review Product function to spread malicious JavaScript (XSS). | (a) For all inputs in the table, assert that the output is properly escaped. (b) For all inputs in the table, assert that the submission is rejected on the server. |
| A2 | An attacker abuses the Review Product function to gain unlimited access to the database (SQL injection). | For all inputs in the table, assert that they are stored as plain text and the database is still intact. Lookups cannot be bypassed. |
| A3 | *Write this one yourself.* | *Write these yourself.* |

The `XSS_PAYLOADS` and `SQLI_PAYLOADS` tables are already in `test_reviews.py`. Use `@pytest.mark.parametrize` so that one test runs once for every row in a table.

### Step 2.3: Red

The first security test, `test_sql_in_review_text_is_stored_as_plain_text`, is written for you. Run it:

```bash
pytest -q test_reviews.py
```

It fails for every payload. Note that even the **legitimate** review `It's great!` fails, so a security bug is often a functional bug too. Write the remaining tests marked `TODO` and watch each one fail **before** you fix anything. Record each test in your TDD log.

### Step 2.4: Green

Change `reviews.py` according to secure-coding guidelines:

- **SQL injection:** use parameterised queries (`?` placeholders). Do not use string formatting, and do not use `executescript` with user input.
- **XSS on output:** escape every value you put into HTML with `html.escape`. Escaping on output protects you even if bad data is already in the database.
- **XSS on input:** reject reviews that contain HTML tags by raising `ValidationError`. A harmless `<`, as in `2 < 3`, must still be accepted.
- **Input validation (A3):** decide on sensible limits, document them, and test the boundary values.

Your fixes **must not change functional behaviour**: the teammate's three original tests must still pass.

### Step 2.5: Re-scan and refactor

```bash
pytest -q && bandit reviews.py app.py
```

Both commands should now be clean. If Bandit still reports something you believe is a false positive, explain why in your report. Do **not** silence it with `# nosec` unless you can justify it.

**Checkpoint 2:** every test passes, Bandit reports no issues, and you have at least 3 abuser stories with tests.

---

## Part 3: The web form and DAST

`app.py` puts the review store behind a Flask web page. Some flaws only appear when the application is running, so this part uses DAST.

### Step 3.1: Server-side rejection through the form

Complete the `TODO` tests in `test_app.py`. A POST that contains a script, or a rating such as `abc` or `5); DROP TABLE reviews; --`, must receive a **400** response and must not be stored. Make each test fail first, then fix `app.py`.

Hint: what does the starter return for `rating=abc`? Why is a 500 error with a stack trace a security problem?

### Step 3.2: Dynamic scan with OWASP ZAP

Start the application. Use port 8000, because macOS uses port 5000 for AirPlay.

```bash
flask --app app run --port 8000
```

In VS Code you can instead start the app from the *Run and Debug* view; see [VSCODE.md](VSCODE.md#running-the-flask-app-part-3).

Open `http://localhost:8000/products/widget/reviews` in a browser to check that the app is running. Keep it running while you scan.

1. In ZAP's *Quick Start* tab, click *Automated Scan*.
2. Set *URL to attack* to `http://localhost:8000/products/widget/reviews`. Leave *Use traditional spider* ticked and *Use ajax spider* unticked.
3. Click *Attack*. Wait until the progress bars at the bottom finish.
4. Open the *Alerts* tab to see the findings, grouped by risk: High, Medium, Low and Informational. Click an alert to see the affected URL, the evidence and the suggested fix. Look up an alert's ID at <https://www.zaproxy.org/docs/alerts/> for more detail.
5. Save the report with *Report → Generate Report*, choosing the *Traditional HTML Report* template. Name it `zap-before.html`, and later `zap-after.html`.

*Automated Scan* first crawls the site, then runs an **active** scan: it sends attack payloads to your app. This finds more problems than just reading the responses, but it also posts junk reviews into the in-memory database. Restart Flask before you scan again.

If ZAP cannot reach the target, check that Flask is still running and that the URL uses port 8000.

Also try visiting `/products/<img src=x onerror=alert(1)>/reviews` in a browser on the **starter** version. Which line of `app.py` is responsible?

### Step 3.3: Turn findings into tests

For each High, Medium or Low alert that ZAP reports, such as a missing `Content-Security-Policy`, a missing `X-Content-Type-Options` or a missing anti-clickjacking header:

1. Write a test in `test_app.py` that checks the response for the fix. Run it and see it fail (Red).
2. Fix `app.py`. A single `@app.after_request` hook is the cleanest place to set headers (Green).
3. Re-run ZAP and confirm that the finding is gone.

Some findings you may decide to **accept** instead of fixing. Examples are "Server Leaks Version Information" from the development server, and "Absence of Anti-CSRF Tokens". If you accept one, explain why in your report and say how production would deal with it.

**Checkpoint 3:** all tests pass, and a ZAP report from before and after your fixes.

---

## Deliverables

Submit a zip containing:

1. Your final `starter/` folder (code and tests).
2. Your **TDD log** (Parts 1 to 3).
3. A short report (2 to 3 pages) containing:
   - the Bandit output before and after your fixes;
   - your abuser stories table, including A3;
   - the ZAP summary before and after, and which findings you fixed or accepted, with reasons;
   - answers to the reflection questions below.

## Reflection questions

1. In Part 2 the teammate's functional tests all passed. What does that tell you about the claim that TDD yields "near-zero defects"?
2. Bandit found the SQL injection, but did it find the XSS? Why or why not? What kinds of flaw does SAST miss that tests or DAST catch, and the other way round?
3. You both escaped output **and** rejected HTML on input. Why use both? Which one is the essential defence, and why?
4. Give one example of a security fix that would have **changed functional behaviour** if you had not had tests. How did the tests protect you?
5. Where in a CI pipeline would you run `pytest`, `bandit` and ZAP? Which should block a merge?

## Grading rubric (100 points)

| Criterion | Points |
|-----------|--------|
| Part 1: correct cart; tests cover R1 to R5; log shows real Red → Green steps | 20 |
| Part 2: security tests for A1 and A2 that are parameterised and fail on the starter code | 20 |
| Part 2: own abuser story A3 with boundary tests | 10 |
| Part 2: fixes follow guidelines; Bandit clean; functional tests still pass | 15 |
| Part 3: form rejection tests and fixes; ZAP findings converted into tests | 20 |
| Report and reflection answers | 15 |
