import os
from typing import Optional
from pathlib import Path

try:
	from dotenv import load_dotenv  # type: ignore
except Exception:
	load_dotenv = None  # type: ignore


_BOM = "\ufeff"


def _manual_parse_env(env_path: Path) -> None:
	try:
		if not env_path.exists():
			return
		# Use utf-8-sig to seamlessly handle BOM-prefixed files
		text = env_path.read_text(encoding="utf-8-sig")
		for raw_line in text.splitlines():
			line = raw_line.strip()
			if not line or line.startswith("#"):
				continue
			if "=" not in line:
				continue
			key, value = line.split("=", 1)
			key = key.strip().lstrip(_BOM)
			value = value.strip().strip('"').strip("'").lstrip(_BOM)
			if key and os.getenv(key) in (None, ""):
				os.environ[key] = value
	except Exception:
		# Silent fallback; avoid crashing on weird encodings
		pass


def _load_env_files() -> None:
	# 1) Try project root .env (two levels up from this file: src/config.py -> repo/.env)
	project_root = Path(__file__).resolve().parents[1]
	project_env = project_root / ".env"
	if load_dotenv and project_env.exists():
		load_dotenv(dotenv_path=str(project_env), override=False)
	# Always manually parse as a safety net (won't override existing env)
	_manual_parse_env(project_env)

	# 2) Also try standard search from current working directory
	if load_dotenv:
		load_dotenv(override=False)

	# 3) Also manually parse CWD .env (safety net)
	cwd_env = Path.cwd() / ".env"
	_manual_parse_env(cwd_env)


# Load on import
_load_env_files()


def reload_env() -> None:
	"""Force reloading environment variables from .env files."""
	_load_env_files()


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
	value = os.getenv(name)
	if value is not None and value != "":
		return value
	return default


class AppConfig:
	def __init__(self) -> None:
		self.openweather_api_key: Optional[str] = get_env("OPENWEATHER_API_KEY")
		self.windy_api_key: Optional[str] = get_env("WINDY_API_KEY")
		self.default_city: str = get_env("DEFAULT_CITY", "Chennai") or "Chennai"
		self.units: str = get_env("UNITS", "metric") or "metric"

		if self.units not in ("metric", "imperial"):
			self.units = "metric"

	def require_api_key(self) -> str:
		# Keep backward compatibility with OPENWEATHER_API_KEY path
		key = self.openweather_api_key or self.windy_api_key
		if not key:
			raise RuntimeError("No API key set. Set WINDY_API_KEY or OPENWEATHER_API_KEY in .env.")
		return key

	# expose helper for reuse
	def get_env(self, name: str, default: Optional[str] = None) -> Optional[str]:
		return get_env(name, default)
