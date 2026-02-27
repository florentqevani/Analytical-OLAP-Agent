# Frontend Notes

React/Vite client for interacting with the analytics API.

## Runtime Requirement

`VITE_API_URL` is required.

- The API module reads `import.meta.env.VITE_API_URL`.
- If missing, it throws on every request and logs a warning.

Example:
```bash
# PowerShell
$env:VITE_API_URL="http://localhost:8001"
npm run dev
```

## Local Development

```bash
npm install
npm run dev
```

Default Vite dev URL is typically `http://localhost:5173`.

## API Calls Used

- `GET /agents`
- `GET /history?user_id=<id>&limit=<n>`
- `POST /analyze`

Implemented in `src/services/api.js` with centralized error handling.

## Contract Expectations

The UI expects `POST /analyze` responses to include:
- `result.message`
- `result.report.executiveSummary`
- `result.report.keyFindings[]`
- `result.report.risks[]`
- `result.report.recommendations[]`
- `result.report.chartHint`
- `result.report.chartData.series[]` with numeric values

If this contract changes, update:
- `buildConversation` in `src/App.jsx`
- `buildChartModel` in `src/App.jsx`

## Build for Static Hosting

```bash
npm run build
```

Artifacts are emitted to `frontend/dist` and used by the Render static service.
