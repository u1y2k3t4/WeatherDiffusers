from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List


RAIN_CODES_PREFIX = (2, 3, 5)  
SNOW_CODE_PREFIX = 6


def _code_indicates_precip(code: int) -> bool:
	prefix = code // 100
	return prefix in RAIN_CODES_PREFIX or prefix == SNOW_CODE_PREFIX


def detect_from_current(current: Dict[str, Any]) -> Optional[Tuple[str, float]]:
	weather = current.get("weather") or []
	if not weather:
		return None
	code = int((weather[0] or {}).get("id", 0))
	if _code_indicates_precip(code):
		return ("precipitation", 0.0)
	return None


def detect_from_forecast_3h(forecast: Dict[str, Any]) -> Optional[Tuple[str, float]]:
	lst = forecast.get("list") or []
	if not isinstance(lst, list) or not lst:
		return None
	for idx, block in enumerate(lst[:2]):
		weather = block.get("weather") or []
		if not weather:
			continue
		code = int((weather[0] or {}).get("id", 0))
		if _code_indicates_precip(code):
			eta_minutes = 180.0 * (idx + 1)
			return ("precipitation", eta_minutes)
	return None


def detect_imminent_precipitation(current: Dict[str, Any], forecast: Dict[str, Any]) -> Optional[Tuple[str, float]]:
	now = detect_from_current(current)
	if now:
		return now
	return detect_from_forecast_3h(forecast)


def detect_from_windy_precip(series: Dict[str, List[float]], step_minutes: int = 60, window_minutes: int = 180) -> Optional[Tuple[str, float]]:
	# Windy parameters commonly include "precip", "prate" or similar arrays at regular step
	arr = series.get("precip") or series.get("prate") or []
	if not arr:
		return None
	for idx, value in enumerate(arr):
		try:
			v = float(value)
		except (TypeError, ValueError):
			continue
		if v > 0:
			eta = (idx) * step_minutes
			if eta <= window_minutes:
				return ("precipitation", float(max(0, eta)))
			else:
				break
	return None
