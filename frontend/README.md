# People Directory

Single-page React app for looking up a person's name and country by ID using
the FastAPI service. Use **Create new entry** to add a name and country; the API
assigns the next ID and saves the entry to `data.csv`.

## Run locally

Start the API from the project root:

```powershell
python main.py
```

In another terminal, start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (usually `http://localhost:5173`).
The frontend calls `http://127.0.0.1:8000` by default. To use a different API
base URL, define `VITE_API_BASE_URL` in a `.env.local` file in this directory.

## Checks

```powershell
npm run build
npm run lint
npm run test:e2e
```

`npm run test:e2e` runs the browser tests in Chromium. Install the browser once
with `npx playwright install chromium` if Playwright prompts you to do so.

The UI-01 test can also be run with pytest from the project root:

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m pytest tests/test_frontend.py -q
```

The pytest test starts and stops Vite automatically. It uses port `5174`.
