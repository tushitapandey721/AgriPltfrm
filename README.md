Agricultural AI Platform
========================

An end-to-end, hackathon-ready agricultural decision support system with:

- Real-time sensor ingestion (ESP8266/Arduino → Flask)
- Weather + satellite proxy data fusion
- Rule-based AI insights (crop health, risk zone, insurance risk)
- Calamity detection and recovery guidelines
- Insurance management (types, premium calculator, claims)
- Notifications (visual + audio), multi-language UI
- Privacy features (export/delete), feasibility analysis


Quick Start
-----------

Prerequisites:

- Python 3.10+
- PowerShell (Windows) or shell
- Optional: Virtual environment (recommended)

1) Backend (Flask)

```powershell
cd agricultural-ai-backend

# Create venv (if you don't have one)
python -m venv venv
./venv/Scripts/Activate.ps1

pip install -r requirements.txt

# Set your OpenWeather key (or edit in code)
$env:OPENWEATHER_API_KEY = "YOUR_KEY"

# Run
./venv/Scripts/python.exe src/server.py
```

Verify:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -UseBasicParsing | Select-Object -Expand Content
```

2) Frontend (static)

- Open `frontend/index.html` directly in your browser (double-click the file).
- The dashboard will fetch from `http://127.0.0.1:5000`.
- <img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5979d4cc-22b4-4716-85e7-3af39ebd5ac5" />



Key Features
------------

- Real-time monitoring: `/api/sensor` accepts sensor JSON; `/api/data` aggregates weather + NDVI proxy + latest sensor.
- AI predictions: Simple rules compute `health_status`, `risk_zone`, `insurance_risk`.
- Calamities: Detection based on thresholds; `/api/calamities` and alerts.
- Recovery guidelines: Rich guidance via `/api/recovery/guidelines` and `/api/recovery/guidelines/<type>`.
- Insurance: `/api/insurance/types`, premium calculator, policy and claim endpoints.
- Notifications: In-browser toasts + bell badge + audio.
- Multi-language: Client-side translation for key UI text.
- Privacy: `/api/privacy/settings`, export, delete.
- Feasibility analysis: `/api/feasibility/analysis`.


Project Structure
-----------------

```
SIH/
├─ agricultural-ai-backend/
│  ├─ src/
│  │  ├─ server.py              # Main Flask server
│  │  ├─ simple_server.py       # Minimal server for debugging
│  │  └─ test_server.py         # Tiny test server (optional)
│  ├─ requirements.txt          # Python deps
│  └─ ...
└─ frontend/
   └─ index.html                # Static dashboard (Tailwind, Chart.js, JS)
```


API Highlights
--------------

- `GET /api/health` – server status
- `GET /api/data` – fused data + predictions + calamities
- `POST /api/sensor` – ingest sensor reading `{ temperature, humidity, soil_moisture }`
- `GET /api/recovery/guidelines` – all calamity guidelines
- `GET /api/recovery/guidelines/<type>` – specific calamity
- `GET /api/insurance/types` – insurance types and coverages
- `POST /api/insurance/calculate-premium` – premium estimation
- `POST /api/insurance/policy` – create policy (in-memory)
- `POST /api/insurance/claim` – submit claim (in-memory)
- `GET /api/calamities` – recent detections
- `GET/POST /api/privacy/settings` – privacy config
- `GET /api/privacy/data-export` – data export snapshot
- `DELETE /api/privacy/data-delete` – purge in-memory data


IoT Ingestion (ESP8266/Arduino)
--------------------------------

- Post JSON to the backend from your ESP8266/ESP-01/NodeMCU:

```json
POST http://<PC-IP>:5000/api/sensor
{"temperature": 29.5, "humidity": 62, "soil_moisture": 415}
```

Replace `<PC-IP>` with the machine IP printed by Flask at startup.


Environment & Configuration
---------------------------

- `OPENWEATHER_API_KEY` – required for weather fetch.
- All data stores are in-memory for the hackathon. For persistence, consider SQLite/PostgreSQL/MongoDB.


Troubleshooting
---------------

- Failed to fetch on frontend
  - Ensure backend is running at `http://127.0.0.1:5000`.
  - Use health check: `Invoke-WebRequest http://127.0.0.1:5000/api/health`.
  - Disable corporate VPN/Proxy that may block localhost.

- 404 on endpoints
  - Confirm you’re running `src/server.py`, not the minimal `simple_server.py` (unless testing).

- CORS errors
  - `server.py` adds permissive CORS headers. Hard-refresh the browser.


License
-------

For hackathon/demo use. Add a proper OSS license before public release.


 

