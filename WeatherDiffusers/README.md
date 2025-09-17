## WeatherDiffusers

Generate weather alert images based on imminent precipitation using Windy (primary) and OpenWeather (fallback). Creates a simple image via Pillow by default.

### Prerequisites
- Python 3.10+
- A Windy Point Forecast API key (optional OpenWeather key for fallback)

### Setup (Windows PowerShell)
```powershell
cd "C:\Users\YUVA\Desktop\WeatherDiffusers"
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment
notepad .env  # set WINDY_API_KEY, DEFAULT_CITY, UNITS (optional OPENWEATHER_API_KEY)
```

### Run
```powershell
# Example
python -m src.main --city "Chennai"

# Adjust detection window/step (Windy series)
python -m src.main --city "Chennai" --window-min 240 --step-min 60

# Force an image even if nothing is detected
python -m src.main --city "Chennai" --force-image
```

Images are saved under `outputs/`.

### Notes
- Uses geocoding, current weather, and 3-hour forecast endpoints (not One Call) to avoid 401 limitations.
- Detects precipitation now (current) or in the next 3–6 hours (forecast).
- The default image generator uses Pillow to create an alert image.
