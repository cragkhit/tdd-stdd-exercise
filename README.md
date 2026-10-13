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

---

## Setup

You need Python 3.9 or newer.

```bash
cd starter
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
pytest -q                          # pytest runs all tests in the folder
```

Run one file with `pytest -q test_shopping_cart.py`, and one test with `pytest -q -k new_cart`.

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

[ZAP](https://www.zaproxy.org) scans a **running** web application. You only need it in Part 3, but install it before the lab, because the download is large. Choose **one** option.

**Option A: Docker (recommended).** This runs the baseline scan from the command line.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows or macOS) or Docker Engine (Linux), and start it.
2. Download the ZAP image (over 1 GB) and check that it runs:

   ```bash
   docker pull ghcr.io/zaproxy/zaproxy:stable
   docker run --rm ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -h    # prints the scan options
   ```

If `docker` reports that it cannot connect to the Docker daemon, Docker Desktop is not running. Start it and try again.

**Option B: the ZAP desktop app.** Use this option if you cannot install Docker.

1. Download the installer for your operating system from <https://www.zaproxy.org/download/> and install it. The Windows and macOS installers include the Java runtime that ZAP needs.
2. Start ZAP. When it asks whether to persist the session, choose *No, I do not want to persist this session*.
3. You should see the *Quick Start* tab with an *Automated Scan* button.

> Scan only applications that you run yourself, such as the lab app on `localhost`. Scanning other people's sites without permission may be illegal.

Keep a **TDD log** as you go: one row per cycle. You will hand it in.

| # | Test written | Red? (failure message) | Code change to go green | Refactoring |
|---|--------------|------------------------|-------------------------|-------------|
| 1 | `test_new_cart_is_empty` | `ImportError: cannot import name 'Product'` | Added empty `ShoppingCart` and `Product` classes | none |

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
flask --app app run --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/products/widget/reviews` in a browser to check that the app is running. Then run the scan in a **second** terminal while the app keeps running in the first one.

**Option A: Docker baseline scan.** Run this from the `starter` folder. It saves an HTML report in your current folder:

```bash
docker run --rm -t -v "$(pwd)":/zap/wrk/:rw ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
    -t http://host.docker.internal:8000/products/widget/reviews \
    -r zap-before.html
# Linux: add  --add-host=host.docker.internal:host-gateway  after "docker run"
# Windows PowerShell: use  -v "${PWD}:/zap/wrk/:rw"  and put the command on one line
```

- `-t` is the target URL. Inside the container, `localhost` means the container itself, so use `host.docker.internal` to reach your machine.
- `-r zap-before.html` saves the report. After your fixes, run the same command with `-r zap-after.html`.
- The `-v` option shares your current folder with the container as `/zap/wrk`. ZAP writes the report there.

The baseline scan crawls the site for about a minute and checks the responses **passively**. It does not attack the app. The terminal output ends with a summary like this (your alerts and numbers will differ):

```
WARN-NEW: Content Security Policy (CSP) Header Not Set [10038] x 2
...
FAIL-NEW: 0  FAIL-INPROG: 0  WARN-NEW: 6  WARN-INPROG: 0  INFO: 0  IGNORE: 0  PASS: 60
```

Each WARN or FAIL line gives the alert name, its ID in square brackets and the number of URLs affected. Look up an ID at <https://www.zaproxy.org/docs/alerts/> to see what it means and how to fix it. The command exits with code 1 if there is any FAIL, 2 if there are only WARNs and 0 if everything passes. This is how a CI pipeline would use it.

If the scan reports that it cannot reach the target, check that Flask is still running with `--host 0.0.0.0` and that the URL uses port 8000.

**Option B: ZAP desktop app.**

1. In the *Quick Start* tab, click *Automated Scan*.
2. Set *URL to attack* to `http://localhost:8000/products/widget/reviews`. Leave *Use traditional spider* ticked and *Use ajax spider* unticked.
3. Click *Attack*. Wait until the progress bars at the bottom finish.
4. Open the *Alerts* tab to see the findings. Click an alert to see the affected URL, the evidence and the suggested fix.
5. Save the report with *Report → Generate Report*, choosing the *Traditional HTML Report* template. Name it `zap-before.html`, and later `zap-after.html`.

Unlike the Docker baseline, *Automated Scan* also runs an **active** scan: it sends attack payloads to your app. This finds more problems, but it also posts junk reviews into the in-memory database. Restart Flask before you scan again.

Also try visiting `/products/<img src=x onerror=alert(1)>/reviews` in a browser on the **starter** version. Which line of `app.py` is responsible?

### Step 3.3: Turn findings into tests

For each WARN or FAIL that ZAP reports, such as a missing `Content-Security-Policy`, a missing `X-Content-Type-Options` or a missing anti-clickjacking header:

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
