# People Directory

Single-page React app for looking up a person's name and country by ID using
the FastAPI service.

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
```
