from __future__ import annotations

import argparse
import sys

from src.config import AppConfig
from src.geocode import geocode_city_osm
from src.windy import WindyClient
from src.detect import detect_from_windy_precip, detect_imminent_precipitation
from src.prompt import build_prompt
from src.image_gen import generate_alert_image

# Optional fallback
try:
	from src.openweather import OpenWeatherClient
except Exception:
	OpenWeatherClient = None  # type: ignore


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Generate weather alert image if imminent precipitation is detected.")
	parser.add_argument("--city", type=str, default=None, help="City name (falls back to DEFAULT_CITY from env)")
	parser.add_argument("--window-min", type=int, default=180, help="Detection window in minutes (Windy)")
	parser.add_argument("--step-min", type=int, default=60, help="Step size of Windy series in minutes")
	parser.add_argument("--force-image", action="store_true", help="Always generate image even if no precip detected")
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	config = AppConfig()
	city = args.city or config.default_city

	geo = geocode_city_osm(city)
	if not geo:
		print(f"Could not geocode city: {city}")
		return 1
	lat, lon, city_name = geo

	windy_key = config.get_env("WINDY_API_KEY") if hasattr(config, "get_env") else None
	if windy_key is None:
		import os
		windy_key = os.getenv("WINDY_API_KEY")

	alert = None
	if windy_key:
		try:
			windy = WindyClient(api_key=windy_key)
			wd = windy.point_forecast(lat, lon, parameters=["precip", "prate"])
			alert = detect_from_windy_precip(wd, step_minutes=int(args.step_min), window_minutes=int(args.window_min))
		except Exception as e:
			print(f"Windy API failed: {e}")

	if not alert:
		# Fallback to OpenWeather if configured
		try:
			from src.config import get_env as cfg_get_env
			owm_key = cfg_get_env("OPENWEATHER_API_KEY")
			units = cfg_get_env("UNITS", "metric") or "metric"
			if owm_key and OpenWeatherClient is not None:
				client = OpenWeatherClient(api_key=owm_key, units=units)
				current = client.current_weather(lat, lon)
				forecast = client.forecast_3h(lat, lon)
				alert = detect_imminent_precipitation(current, forecast)
		except Exception as e:
			print(f"OpenWeather fallback failed: {e}")

	if not alert:
		msg = f"No imminent precipitation detected for {city_name} soon."
		print(msg)
		if not args.force_image:
			return 0
		# Force a generic image
		condition, eta = "none", 0.0
		prompt = build_prompt(city_name, condition, eta)
		out_path = generate_alert_image(city_name, condition, eta, prompt)
		print(f"Forced image saved to: {out_path}")
		return 0

	condition, eta = alert
	prompt = build_prompt(city_name, condition, eta)
	out_path = generate_alert_image(city_name, condition, eta, prompt)
	print(f"Alert image saved to: {out_path}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
