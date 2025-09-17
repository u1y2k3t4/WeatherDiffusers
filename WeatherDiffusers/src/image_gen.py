from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def _choose_bg_color(condition: str) -> Tuple[int, int, int]:
	if condition == "precipitation":
		return (30, 50, 90)  # stormy blue
	return (60, 60, 60)


def generate_alert_image(city: str, condition: str, eta_minutes: float, prompt: str, out_dir: str = "outputs") -> str:
	Path(out_dir).mkdir(parents=True, exist_ok=True)
	width, height = 1024, 1024
	bg = _choose_bg_color(condition)
	img = Image.new("RGB", (width, height), color=bg)
	draw = ImageDraw.Draw(img)

	# Load default font
	try:
		font_title = ImageFont.truetype("arial.ttf", 72)
		font_body = ImageFont.truetype("arial.ttf", 36)
	except Exception:
		font_title = ImageFont.load_default()
		font_body = ImageFont.load_default()

	title = f"{city} Alert"
	body = f"{condition.capitalize()} in ~{int(eta_minutes)} min"
	footer = prompt

	# Center title
	title_bbox = draw.textbbox((0, 0), title, font=font_title)
	title_w = title_bbox[2] - title_bbox[0]
	draw.text(((width - title_w) / 2, 120), title, fill=(255, 255, 255), font=font_title)

	# Body
	draw.text((80, 300), body, fill=(220, 220, 220), font=font_body)

	# Footer prompt with wrapping
	max_width = width - 160
	y = 380
	for line in _wrap_text(footer, font_body, draw, max_width):
		draw.text((80, y), line, fill=(200, 200, 200), font=font_body)
		y += 46

	timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
	file_name = f"{city.replace(' ', '_').lower()}_{condition}_{timestamp}.png"
	out_path = str(Path(out_dir) / file_name)
	img.save(out_path)
	return out_path


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw, max_width: int):
	words = text.split()
	line = []
	for word in words:
		trial = " ".join(line + [word])
		bbox = draw.textbbox((0, 0), trial, font=font)
		if bbox[2] - bbox[0] <= max_width:
			line.append(word)
		else:
			yield " ".join(line)
			line = [word]
	if line:
		yield " ".join(line)
