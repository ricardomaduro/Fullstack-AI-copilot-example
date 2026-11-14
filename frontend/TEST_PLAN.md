# Frontend test plan

## Setup

1. Start the FastAPI app from the project root:

   ```powershell
   python main.py
   ```

2. Start the React app in another terminal:

   ```powershell
   cd frontend
   npm run dev
   ```

3. Open the Vite URL, usually `http://localhost:5173`.
4. Use an existing ID from `data.csv` for successful lookup cases. Use an ID
   absent from that file (for example `999`) for the not-found case.

## Scenarios

| ID | Priority | Scenario | Steps | Expected result |
|---|---|---|---|---|
| UI-01 | P1 | Initial page | Open the frontend. | Page title is “Find a person”; the Person ID input and Search button are visible; no result or error is shown. **Automated:** `tests/test_frontend.py` and `e2e/initial-page.spec.ts`. |
| UI-02 | P1 | Find an existing person | Enter an existing ID from `data.csv` and submit. | The API lookup succeeds. Name and country appear in separate labeled fields with the values from that CSV row. **Automated:** `tests/test_frontend.py`. |
| UI-03 | P1 | Replace a previous result | Look up one existing ID, then submit a different existing ID. | Both fields update to the second person's values; no stale values remain. **Automated:** `tests/test_frontend.py`. |
| UI-04 | P1 | Unknown ID | Submit an ID absent from `data.csv`. | A “No person found” alert appears, and any prior result is cleared. **Automated:** `tests/test_frontend.py`. |
| UI-05 | P1 | Empty input | Leave the input empty and submit. | Required-field browser validation prevents submission; no API request is sent. **Automated:** `tests/test_frontend.py`. |
| UI-06 | P2 | Invalid numeric input | Try `0`, a negative number, or a fractional number. | The input's minimum/step validation prevents submission; no lookup request is sent. **Automated:** `tests/test_frontend.py` (three values). |
| UI-07 | P2 | Loading state | Delay the API response (for example, intercept the request in Playwright and wait 500 ms). Submit an existing ID. | “Looking up person…” is announced, the button changes to “Searching…” and is disabled, then the result appears after the response. **Automated:** `tests/test_frontend.py`. |
| UI-08 | P1 | API unavailable | Stop the API or abort the request in Playwright, then submit an existing ID. | A connection error alert tells the user the API could not be reached. **Automated:** `tests/test_frontend.py`. |
| UI-09 | P2 | API server error | Make the API return a 5xx response, then submit an ID. | An error alert reports the server error; no stale result is displayed. **Automated:** `tests/test_frontend.py`. |
| UI-10 | P2 | Keyboard and accessibility | Navigate with Tab, enter an ID, submit with Enter, and inspect accessible names/live announcements. | Input and button are keyboard accessible and labeled; loading, result, and error updates are announced. **Automated:** `tests/test_frontend.py`. |
| UI-11 | P2 | Responsive layout | Check at desktop width and a mobile viewport such as 375 × 812. | Content remains visible without horizontal scrolling; the input and Search button stack on narrow screens. **Automated:** `tests/test_frontend.py`. |
| UI-12 | P1 | Local API CORS | Load from `http://localhost:5173` and look up a person. | The browser request succeeds; API responses include the allowed frontend origin. **Automated:** `tests/test_frontend.py` against a live local FastAPI server. |

## Playwright smoke checks performed

- Opened the app and confirmed the initial form renders.
- Submitted ID `2`; the page displayed name `Maria` and country `Portugal` in
  separate fields, matching the current second record in `data.csv`.
- Submitted ID `999`; the page displayed the not-found alert.
- Viewed the page at 375 × 812; the form and content remained present.
- Automated UI-01 with Playwright Chromium: passed; the page rendered the
  initial form without an API request, result, or error.
- The same UI-01 checks are available under pytest as
  `tests/test_frontend.py`.

Run the frontend checks with:

```powershell
npm run build
npm run lint
npm run test:e2e
```
