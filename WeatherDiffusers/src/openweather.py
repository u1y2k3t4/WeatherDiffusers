from __future__ import annotations

import requests
from typing import Any, Dict, List, Optional, Tuple

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"  


class OpenWeatherClient:
	def __init__(self, api_key: str, units: str = "metric") -> None:
		self.api_key = api_key
		self.units = units

	def geocode_city(self, city: str, limit: int = 1) -> Optional[Tuple[float, float, str]]:
		params = {"q": city, "limit": limit, "appid": self.api_key}
		r = requests.get(GEOCODE_URL, params=params, timeout=20)
		r.raise_for_status()
		data: List[Dict[str, Any]] = r.json()
		if not data:
			return None
		first = data[0]
		lat = float(first.get("lat"))
		lon = float(first.get("lon"))
		name = str(first.get("name") or city)
		return lat, lon, name

	def current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
		params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": self.units}
		r = requests.get(CURRENT_URL, params=params, timeout=20)
		r.raise_for_status()
		return r.json()

	def forecast_3h(self, lat: float, lon: float) -> Dict[str, Any]:
		params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": self.units}
		r = requests.get(FORECAST_URL, params=params, timeout=30)
		r.raise_for_status()
		return r.json()
