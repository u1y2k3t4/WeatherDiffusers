from __future__ import annotations

from typing import Optional, Tuple, Any, List, Dict
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_city_osm(city: str) -> Optional[Tuple[float, float, str]]:
	params = {
		"q": city,
		"format": "json",
		"limit": 1,
		"addressdetails": 0,
		"accept-language": "en",
	}
	headers = {"User-Agent": "WeatherDiffusers/1.0 (educational)"}
	r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=20)
	r.raise_for_status()
	data: List[Dict[str, Any]] = r.json()
	if not data:
		return None
	first = data[0]
	lat = float(first.get("lat"))
	lon = float(first.get("lon"))
	display_name = str(first.get("display_name") or city)
	return lat, lon, display_name
