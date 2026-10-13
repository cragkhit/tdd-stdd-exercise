# VS Code tips for the lab

These notes add to [Setup, Option B](README.md#option-b-vs-code-gui) in the main README. Read them if the tests do not show up, or when you reach Part 3.

## If the tests do not appear

- Check the interpreter shown in the bottom-right status bar. It should say `('.venv': venv)`. If not, click it (or run **Python: Select Interpreter**) and choose the one in `./.venv`.
- Open the *Output* panel and select *Python* from the drop-down to see the test discovery error. An `ImportError` for `Product` in `test_shopping_cart.py` is expected at first, because `shopping_cart.py` is empty.
- Click the *Refresh Tests* button at the top of the Testing view after you change the configuration.

## Running the Flask app (Part 3)

`starter/.vscode/launch.json` contains a **Flask app (port 8000)** configuration. Open the *Run and Debug* view (`Ctrl+Shift+D` / `Cmd+Shift+D`), select it and press ▷ (or `F5`). This runs the same command as `flask --app app run --port 8000`, and you can set breakpoints in `app.py`. Press the red ■ to stop it, or the green ⟳ in the debug toolbar to restart it before each ZAP scan.

## Bandit and ZAP

Bandit and ZAP have no VS Code integration in this lab. Run `bandit` in the VS Code terminal (*Terminal → New Terminal*) as shown in the README, and use the ZAP desktop app.
