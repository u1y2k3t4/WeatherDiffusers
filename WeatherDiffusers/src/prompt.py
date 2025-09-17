from __future__ import annotations

from typing import Tuple


def build_prompt(city_name: str, condition: str, eta_minutes: float) -> str:
	if condition == "precipitation":
		base = f"Weather alert for {city_name}: precipitation expected in ~{int(eta_minutes)} minutes."
		style = "dark stormy sky, dramatic clouds, approaching rain, city skyline"
	elif condition == "none":
		base = f"Weather snapshot for {city_name}: no immediate precipitation detected."
		style = "calm city skyline, partly cloudy sky, soft lighting"
	else:
		base = f"Weather update for {city_name}: {condition} in ~{int(eta_minutes)} minutes."
		style = "weather scene"
	return f"{base} Visualize: {style}."
