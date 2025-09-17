from __future__ import annotations

from typing import Optional, Tuple

from src.config import AppConfig, get_env as cfg_get_env
from src.geocode import geocode_city_osm
from src.windy import WindyClient
from src.detect import detect_from_windy_precip, detect_imminent_precipitation
from src.prompt import build_prompt
from src.image_gen import generate_alert_image

try:
	from src.openweather import OpenWeatherClient
except Exception:
	OpenWeatherClient = None  # type: ignore


def generate_weather_image_for_city(city: str, window_min: int = 180, step_min: int = 60, force_image: bool = False) -> Tuple[str, str]:
	config = AppConfig()
	geo = geocode_city_osm(city)
	if not geo:
		raise RuntimeError(f"Could not geocode city: {city}")
	lat, lon, city_name = geo

	windy_key = cfg_get_env("WINDY_API_KEY")
	alert = None
	if windy_key:
		try:
			windy = WindyClient(api_key=windy_key)
			wd = windy.point_forecast(lat, lon, parameters=["precip", "prate"])
			alert = detect_from_windy_precip(wd, step_minutes=int(step_min), window_minutes=int(window_min))
		except Exception:
			pass

	if not alert:
		owm_key = cfg_get_env("OPENWEATHER_API_KEY")
		units = cfg_get_env("UNITS", "metric") or "metric"
		if owm_key and OpenWeatherClient is not None:
			try:
				client = OpenWeatherClient(api_key=owm_key, units=units)
				current = client.current_weather(lat, lon)
				forecast = client.forecast_3h(lat, lon)
				alert = detect_imminent_precipitation(current, forecast)
			except Exception:
				pass

	if not alert and not force_image:
		condition, eta = "none", 0.0
		prompt = build_prompt(city_name, condition, eta)
		path = generate_alert_image(city_name, condition, eta, prompt)
		msg = f"No imminent precipitation detected for {city_name} soon."
		return path, msg

	condition, eta = alert if alert else ("none", 0.0)
	prompt = build_prompt(city_name, condition, eta)
	path = generate_alert_image(city_name, condition, eta, prompt)
	if condition == "precipitation":
		msg = f"{city_name}: precipitation expected in ~{int(eta)} minutes."
	else:
		msg = f"{city_name}: no immediate precipitation detected."
	return path, msg
