from __future__ import annotations

import json
import requests
from typing import Any, Dict, List, Optional

WINDY_POINT_URL = "https://api.windy.com/api/point-forecast/v2"


class WindyClient:
	def __init__(self, api_key: str, model: str = "gfs") -> None:
		self.api_key = api_key
		self.model = model

	def point_forecast(self, lat: float, lon: float, parameters: List[str]) -> Dict[str, Any]:
		headers = {"Content-Type": "application/json"}
		body = {
			"lat": lat,
			"lon": lon,
			"model": self.model,
			"parameters": parameters,
			"key": self.api_key,
		}
		r = requests.post(WINDY_POINT_URL, headers=headers, data=json.dumps(body), timeout=30)
		r.raise_for_status()
		return r.json()
