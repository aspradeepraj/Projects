import json
import math
from pathlib import Path

from ollama import Client
from jsonschema import Draft7Validator, validate
from jsonschema.exceptions import ValidationError

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ==================================================
# STEP 1: PROJECT SETTINGS
# ==================================================

MODEL_NAME = "qwen2.5:3b"
MAX_ATTEMPTS = 3

# Edit these to change the trip
TOTAL_DAYS = 2
TRIP_DESCRIPTION = ("a 2-day motorcycle trip: Day 1 Chennai to Pondicherry, "
                    "Day 2 Pondicherry to Chennai")
VIDEO_SECONDS = 10  # total video length, split evenly across the days

# num_ctx must cover prompt + schema + full output (Ollama default is only 2048-4096)
OLLAMA_OPTIONS = {"temperature": 0.1, "num_ctx": 6144, "num_predict": 3072}

BASE_DIR = Path(__file__).resolve().parent
PROMPT_FILE = BASE_DIR / "master_prompt.txt"
SCHEMA_FILE = BASE_DIR / "schema.json"
BIKE_IMAGE_FILE = BASE_DIR / "bike.png"  # Optional: place your bike PNG here

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ==================================================
# STEP 2: LOAD MASTER PROMPT & SCHEMA
# ==================================================

def load_prompt():
    if not PROMPT_FILE.exists():
        raise FileNotFoundError("master_prompt.txt not found in " + str(BASE_DIR))
    with open(PROMPT_FILE, "r", encoding="utf-8") as file:
        return file.read()


def load_schema():
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError("schema.json not found in " + str(BASE_DIR))
    with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ==================================================
# STEP 3: GENERATE ITINERARY USING OLLAMA
# ==================================================

# timeout=None -> never give up while a slow local model is still generating
client = Client(host="http://localhost:11434", timeout=None)


def stream_chat(messages, schema):
    """Stream the reply so progress is visible, return (raw_text, done_reason)."""
    parts = []
    done_reason = None
    tokens = 0
    for chunk in client.chat(
        model=MODEL_NAME,
        messages=messages,
        format=schema,
        options=OLLAMA_OPTIONS,
        stream=True,
    ):
        piece = chunk.message.content or ""
        parts.append(piece)
        tokens += 1
        if tokens % 50 == 0:
            print(f"  ...received ~{tokens} chunks", end="\r", flush=True)
        if getattr(chunk, "done", False):
            done_reason = getattr(chunk, "done_reason", None)
    print()
    return "".join(parts), done_reason


def parse_response(raw, done_reason):
    (OUTPUT_DIR / "raw_response.txt").write_text(raw, encoding="utf-8")
    print(f"Model stopped because: {done_reason} | output length: {len(raw)} chars")
    if done_reason == "length":
        print("WARNING: output was cut off (token limit). JSON is incomplete.")
    return json.loads(raw)


def generate_itinerary(prompt, schema):
    print("\nGenerating India motorcycle expedition itinerary...")

    raw, done_reason = stream_chat(
        [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    f"Generate the complete itinerary for {TRIP_DESCRIPTION}. "
                    "Return only valid JSON. "
                    f"IMPORTANT: total_days must be {TOTAL_DAYS} and the itinerary must have exactly {TOTAL_DAYS} day(s). "
                    "Keep every text field short (one brief sentence)."
                )
            }
        ],
        schema,
    )

    data = parse_response(raw, done_reason)
    print("Itinerary generation completed!")
    return data


def correct_itinerary(prompt, schema, data, errors):
    correction_message = (
        "Your previous itinerary failed validation:\n"
        + "\n".join(errors)
        + "\n\nPlease fix these errors and return the complete JSON only."
    )
    raw, done_reason = stream_chat(
        [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    "Previous JSON:\n"
                    + json.dumps(data, indent=2)
                    + "\n\n"
                    + correction_message
                )
            }
        ],
        schema,
    )
    return parse_response(raw, done_reason)


# ==================================================
# STEP 4: VALIDATE JSON SCHEMA & BUSINESS RULES
# ==================================================

def validate_schema(data, schema):
    print("\nChecking JSON schema...")
    Draft7Validator.check_schema(schema)
    validate(instance=data, schema=schema)
    print("JSON schema validation successful!")
    return True


def validate_business_rules(data):
    print("\nChecking business rules...")
    errors = []

    expedition = data["expedition_info"]
    itinerary = data["itinerary"]
    total_days = expedition["total_days"]

    if total_days != TOTAL_DAYS:
        errors.append(f"total_days must be {TOTAL_DAYS}, but found {total_days}.")

    if len(itinerary) != total_days:
        errors.append(f"Expected {total_days} itinerary days, but generated {len(itinerary)} days.")

    for index, day in enumerate(itinerary, start=1):
        if day["day"] != index:
            errors.append(f"Expected Day {index} but found Day {day['day']}.")

    if itinerary:
        # FIX: was itinerary["from"] (list indexed by string) -> first day
        if itinerary[0]["from"].strip().casefold() != expedition["start_location"].strip().casefold():
            errors.append("First day's starting location does not match start_location.")

    for index in range(len(itinerary) - 1):
        if itinerary[index]["to"].strip().casefold() != itinerary[index + 1]["from"].strip().casefold():
            errors.append(f"Route mismatch between Day {index + 1} and Day {index + 2}.")

    if itinerary:
        if itinerary[-1]["to"].strip().casefold() != expedition["end_location"].strip().casefold():
            errors.append("Final day's destination does not match end_location.")

    budget = expedition["budget"]
    if budget["minimum"] > budget["maximum"]:
        errors.append("Minimum budget cannot be greater than maximum budget.")
    if not budget["minimum"] <= budget["estimated_total_inr"] <= budget["maximum"]:
        errors.append("Estimated total cost is outside the specified budget.")

    if errors:
        print("\nBusiness rule validation failed!")
        for error in errors:
            print("-", error)
        return errors

    print("Business rule validation successful!")
    return []


# ==================================================
# STEP 5: AUTOMATIC GENERATION AND RETRY
# ==================================================

def generate_valid_itinerary(prompt, schema):
    data = None
    errors = []

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print("\n========================================")
        print("GENERATION ATTEMPT:", attempt)
        print("========================================")

        try:
            # FIX: regenerate from scratch if there is no usable previous JSON
            if data is None:
                data = generate_itinerary(prompt, schema)
            else:
                print("\nAsking Qwen to correct the itinerary...")
                data = correct_itinerary(prompt, schema, data, errors)

            validate_schema(data, schema)
            errors = validate_business_rules(data)

            if not errors:
                print("\nAll validations passed!")
                return data

        except ValidationError as error:
            errors = [f"JSON schema validation error: {error.message}"]
            print("\nSchema validation failed:", error.message)
        except json.JSONDecodeError as error:
            errors = [f"Invalid JSON: {str(error)}"]
            data = None  # nothing usable to correct
            print("\nInvalid JSON returned by the model:", error)
            print("Raw output saved to:", OUTPUT_DIR / "raw_response.txt")

    print("\nMaximum retry attempts reached.")
    return None


# ==================================================
# STEP 6: SAVE JSON OUTPUT
# ==================================================

def save_output(data, filename):
    output_file = OUTPUT_DIR / filename
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"\nJSON file saved successfully! Location: {output_file}")


# ==================================================
# STEP 7: CONTINUOUS BIKE-DRIVING VIDEO GENERATOR
# ==================================================

INDIA_CITY_COORDS = {
    "chennai": (13.08, 80.27),
    "karimnagar": (18.43, 79.12),
    "sagar": (23.83, 78.73),
    "gwalior": (26.21, 78.18),
    "delhi": (28.61, 77.20),
    "amritsar": (31.63, 74.87),
    "srinagar": (34.08, 74.79),
    "kargil": (34.55, 76.13),
    "leh": (34.15, 77.57),
    "nubra": (34.68, 77.56),
    "pangong": (33.75, 78.66),
    "koyal": (32.96, 79.13),
    "koyul": (32.96, 79.13),
    "tso moriri": (32.91, 78.31),
    "sarchu": (32.90, 77.58),
    "manali": (32.24, 77.18),
    "panipat": (29.39, 76.96),
    "rajura": (19.78, 79.36),
    "ongole": (15.50, 80.04),
    "pondicherry": (11.93, 79.83),
    "puducherry": (11.93, 79.83),
    "mahabalipuram": (12.62, 80.19),
}

INDIA_OUTLINE_LATLON = [
    (35.5, 76.8), (34.8, 78.5), (33.0, 79.3), (31.5, 78.8), (30.2, 80.5),
    (28.5, 81.5), (27.5, 85.0), (27.2, 88.5), (28.0, 95.0), (26.0, 95.2),
    (23.5, 93.0), (22.0, 88.8), (20.2, 86.5), (17.7, 83.3), (15.5, 80.2),
    (13.0, 80.3), (10.3, 79.8), (8.1, 77.5), (10.0, 76.2), (13.0, 74.8),
    (15.5, 73.8), (19.0, 72.8), (21.5, 72.6), (20.8, 70.4), (22.5, 69.0),
    (23.8, 68.5), (24.5, 71.0), (27.0, 70.5), (30.0, 73.8), (32.5, 74.5),
    (34.5, 74.0), (35.5, 76.8)
]


def load_video_font(size, bold=False):
    # FIX: added Linux/macOS fallbacks (was Windows-only)
    candidates = (
        ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/System/Library/Fonts/Supplemental/Arial.ttf"]
    )
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def latlon_to_map_xy(lat, lon, box_x, box_y, box_w, box_h):
    min_lat, max_lat = 7.5, 36.5
    min_lon, max_lon = 68.0, 96.5
    nx = (lon - min_lon) / (max_lon - min_lon)
    ny = 1.0 - ((lat - min_lat) / (max_lat - min_lat))
    return int(box_x + nx * box_w), int(box_y + ny * box_h)


def get_city_latlon(city_name):
    key = city_name.strip().casefold()
    for known, coords in INDIA_CITY_COORDS.items():
        if known in key or key in known:
            return coords
    return (22.5, 78.9)


def draw_rider_and_bike(img, draw, cx, cy, frame_idx, custom_bike_img=None):
    bounce = int(math.sin(frame_idx * 0.7) * 2.5)
    wheel_angle = (frame_idx * 24) % 360

    if custom_bike_img is not None:
        bx = cx - custom_bike_img.width // 2
        by = cy - custom_bike_img.height + bounce
        img.paste(custom_bike_img, (bx, by), custom_bike_img)
        return

    by = cy + bounce  # FIX: 'by' was undefined in the built-in bike branch

    # Exhaust puff particles
    for p in range(3):
        puff_x = cx - 95 - ((frame_idx * 6 + p * 18) % 55)
        puff_y = cy - 22 + int(math.sin((frame_idx + p) * 0.5) * 4)
        puff_r = 4 + p * 2
        draw.ellipse((puff_x - puff_r, puff_y - puff_r, puff_x + puff_r, puff_y + puff_r), fill=(190, 200, 215))

    # Wheels (Rear & Front)
    wheel_r = 26
    for wx in (cx - 65, cx + 68):
        wy = by - wheel_r
        draw.ellipse((wx - wheel_r, wy - wheel_r, wx + wheel_r, wy + wheel_r), fill=(22, 24, 28), outline=(90, 95, 105), width=4)
        draw.ellipse((wx - 15, wy - 15, wx + 15, wy + 15), outline=(210, 215, 225), width=2)
        for s in range(4):
            ang = math.radians(wheel_angle + s * 45)
            x1 = wx + int(math.cos(ang) * 14)
            y1 = wy + int(math.sin(ang) * 14)
            x2 = wx - int(math.cos(ang) * 14)
            y2 = wy - int(math.sin(ang) * 14)
            draw.line((x1, y1, x2, y2), fill=(220, 225, 235), width=2)

    # Frame / forks
    draw.line((cx - 65, by - 26, cx - 15, by - 34), fill=(160, 170, 185), width=5)
    draw.line((cx + 68, by - 26, cx + 38, by - 78), fill=(190, 200, 215), width=5)
    # Engine block & Exhaust pipe
    draw.rounded_rectangle((cx - 28, by - 55, cx + 22, by - 24), radius=6, fill=(75, 82, 95), outline=(140, 150, 165), width=2)
    draw.line((cx - 10, by - 26, cx - 88, by - 20), fill=(180, 185, 195), width=6)
    # Fuel tank & Adventure Fairing
    draw.polygon([
        (cx - 18, by - 56), (cx + 18, by - 74), (cx + 46, by - 68),
        (cx + 62, by - 58), (cx + 32, by - 48), (cx - 15, by - 48)
    ], fill=(235, 95, 35))
    # Tail rack & Pannier box
    draw.rectangle((cx - 75, by - 66, cx - 44, by - 42), fill=(45, 52, 65), outline=(130, 140, 155), width=2)
    draw.line((cx - 50, by - 54, cx - 15, by - 54), fill=(30, 32, 38), width=7)
    # Windshield & Headlight beam
    draw.line((cx + 38, by - 74, cx + 48, by - 96), fill=(160, 230, 255), width=3)
    draw.polygon([(cx + 55, by - 64), (cx + 210, by - 88), (cx + 210, by - 32)], fill=(255, 245, 180))
    # Rider
    draw.line((cx - 18, by - 56, cx - 8, by - 32), fill=(35, 45, 65), width=9)
    draw.line((cx - 8, by - 32, cx + 4, by - 26), fill=(25, 25, 28), width=7)
    draw.line((cx - 22, by - 58, cx - 6, by - 98), fill=(25, 140, 130), width=16)
    draw.line((cx - 6, by - 94, cx + 30, by - 78), fill=(25, 140, 130), width=8)
    hx, hy = cx - 2, by - 114
    draw.ellipse((hx - 14, hy - 14, hx + 14, hy + 14), fill=(245, 245, 250), outline=(30, 35, 45), width=2)
    draw.pieslice((hx - 13, hy - 12, hx + 15, hy + 12), start=-25, end=25, fill=(30, 40, 55))


def create_expedition_video(data):
    print("\nCreating continuous bike-driving expedition video...")

    width, height = 1280, 720
    fps = 24
    expedition = data["expedition_info"]
    itinerary = data["itinerary"]
    frames_per_day = max(1, int(fps * VIDEO_SECONDS / len(itinerary)))

    output_file = OUTPUT_DIR / "expedition_video.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(str(output_file), fourcc, fps, (width, height))
    if not video.isOpened():
        video.release()
        raise RuntimeError("Unable to create MP4 video. Check OpenCV installation.")

    custom_bike_img = None
    if BIKE_IMAGE_FILE.exists():
        try:
            loaded = Image.open(BIKE_IMAGE_FILE).convert("RGBA")
            aspect = loaded.width / loaded.height
            new_h = 135
            custom_bike_img = loaded.resize((int(new_h * aspect), new_h), Image.Resampling.LANCZOS)
            print("Loaded custom bike image:", BIKE_IMAGE_FILE)
        except Exception as e:
            print("Could not load custom bike.png, using built-in bike animation:", e)

    title_font = load_video_font(30, True)
    heading_font = load_video_font(24, True)
    normal_font = load_video_font(19, False)
    bold_small = load_video_font(17, True)
    tiny_font = load_video_font(14, False)

    map_box = (850, 95, 400, 540)
    india_poly = [latlon_to_map_xy(lat, lon, *map_box) for lat, lon in INDIA_OUTLINE_LATLON]

    leg_points = []
    for day in itinerary:
        p1 = latlon_to_map_xy(*get_city_latlon(day["from"]), *map_box)
        p2 = latlon_to_map_xy(*get_city_latlon(day["to"]), *map_box)
        leg_points.append((p1, p2))

    total_km_all = sum(d["distance_km"] for d in itinerary)
    cumulative_km = 0.0
    global_frame = 0

    try:
        for day_idx, day in enumerate(itinerary):
            terrains = " ".join(day["terrain_type"]).lower()
            altitude = day.get("altitude_m") or 0
            is_himalaya = any(k in terrains for k in ["mountain", "off road", "gravel"]) or altitude > 2000

            if is_himalaya:
                sky_color = (32, 68, 118)
                mountain_far = (165, 185, 210)
                mountain_near = (110, 95, 82)
                ground_color = (128, 112, 92)
            else:
                sky_color = (42, 115, 175)
                mountain_far = (75, 130, 120)
                mountain_near = (52, 112, 72)
                ground_color = (58, 128, 68)

            p_start, p_end = leg_points[day_idx]

            for f in range(frames_per_day):
                t = f / frames_per_day
                img = Image.new("RGB", (width, height), sky_color)
                draw = ImageDraw.Draw(img)

                scene_w = 830
                horizon_y = 430

                # Sun
                draw.ellipse((680, 110, 740, 170), fill=(255, 230, 130))

                # Far Mountains
                for m in range(-1, 5):
                    mx = m * 240 - int((global_frame * 2.5) % 240)
                    peak_y = 210 if is_himalaya else 310
                    draw.polygon([(mx, horizon_y), (mx + 120, peak_y), (mx + 240, horizon_y)], fill=mountain_far)
                    if is_himalaya:
                        draw.polygon([(mx + 82, peak_y + 70), (mx + 120, peak_y), (mx + 158, peak_y + 70)], fill=(248, 250, 255))

                # Near Hills
                for m in range(-1, 6):
                    mx = m * 190 - int((global_frame * 5.0) % 190)
                    peak_y = 290 if is_himalaya else 355
                    draw.polygon([(mx, horizon_y), (mx + 95, peak_y), (mx + 190, horizon_y)], fill=mountain_near)

                # Ground & Highway Asphalt
                draw.rectangle((0, horizon_y, scene_w, height), fill=ground_color)
                road_top, road_bot = 505, 645
                draw.rectangle((0, road_top, scene_w, road_bot), fill=(48, 52, 60))
                draw.line((0, road_top, scene_w, road_top), fill=(235, 235, 235), width=4)
                draw.line((0, road_bot, scene_w, road_bot), fill=(235, 235, 235), width=4)

                # Moving Highway Dashed Lines
                dash_spacing = 110
                dash_offset = int((global_frame * 18) % dash_spacing)
                for dx in range(-dash_spacing, scene_w + dash_spacing, dash_spacing):
                    x1 = dx - dash_offset
                    draw.rectangle((x1, 571, x1 + 55, 579), fill=(250, 210, 60))

                # Scrolling Roadside Props
                prop_spacing = 260
                prop_offset = int((global_frame * 14) % prop_spacing)
                for px in range(-prop_spacing, scene_w + prop_spacing, prop_spacing):
                    rx = px - prop_offset
                    if is_himalaya:
                        draw.rounded_rectangle((rx, 468, rx + 26, 502), radius=5, fill=(255, 195, 0), outline=(30, 30, 30), width=2)
                        draw.rectangle((rx, 482, rx + 26, 502), fill=(245, 245, 245))
                    else:
                        draw.rectangle((rx + 10, 465, rx + 18, 503), fill=(95, 62, 38))
                        draw.ellipse((rx - 8, 425, rx + 36, 472), fill=(34, 110, 48))

                # Draw Moving Motorcycle & Rider
                draw_rider_and_bike(img, draw, 280, 588, global_frame, custom_bike_img)

                # Top Banner
                draw.rectangle((0, 0, width, 78), fill=(16, 26, 46))
                draw.text((25, 14), f"INDIA EXPEDITION  |  DAY {day['day']} OF {expedition['total_days']}:  {day['from'].upper()}  ->  {day['to'].upper()}", font=title_font, fill=(255, 255, 255))
                draw.text((25, 50), f"{expedition['title']}   •   Vehicle: {expedition['primary_rider']['vehicle']}", font=tiny_font, fill=(95, 215, 195))

                # HUD Overlay Card
                draw.rounded_rectangle((20, 95, 520, 285), radius=14, fill=(18, 30, 52), outline=(80, 200, 180), width=2)
                live_day_km = int(day["distance_km"] * t)
                live_total_km = int(cumulative_km + day["distance_km"] * t)
                draw.text((38, 108), f"Leg Distance: {live_day_km} / {day['distance_km']} KM   ({day['riding_hours']} hrs)", font=heading_font, fill=(80, 220, 195))
                draw.text((38, 142), f"Total Odometer: {live_total_km} / {int(total_km_all)} KM", font=normal_font, fill=(240, 245, 255))
                draw.text((38, 172), f"Terrain: {', '.join(day['terrain_type'])}   |   Alt: {day.get('altitude_m', 'N/A')} m", font=normal_font, fill=(215, 225, 240))
                highlights_str = ", ".join(day["highlights"][:2])
                draw.text((38, 204), f"Highlights: {highlights_str[:46]}", font=bold_small, fill=(255, 215, 105))
                draw.text((38, 234), f"Day Type: {day['day_type']}   |   Month: {expedition['travel_month']}", font=tiny_font, fill=(185, 195, 210))

                # Right Panel: Live India GPS Route Map
                draw.rectangle((scene_w, 78, width, height), fill=(18, 28, 48))
                draw.line((scene_w, 78, scene_w, height), fill=(80, 200, 180), width=3)
                draw.text((855, 86), "LIVE INDIA ROUTE TRACKER", font=bold_small, fill=(80, 220, 195))
                draw.polygon(india_poly, fill=(32, 48, 76), outline=(105, 145, 195))

                # All legs (dim), completed legs (bright)
                for p1, p2 in leg_points:
                    draw.line((p1, p2), fill=(85, 100, 125), width=2)
                for prev_idx in range(day_idx):
                    prev_p1, prev_p2 = leg_points[prev_idx]
                    draw.line((prev_p1, prev_p2), fill=(80, 220, 195), width=4)

                # FIX: x and y must be interpolated separately (tuples were used as scalars)
                curr_x = int(p_start[0] + (p_end[0] - p_start[0]) * t)
                curr_y = int(p_start[1] + (p_end[1] - p_start[1]) * t)
                draw.line((p_start, (curr_x, curr_y)), fill=(255, 195, 45), width=4)

                # FIX: city dots/labels used tuples in arithmetic
                for p1, _ in leg_points:
                    draw.ellipse((p1[0] - 3, p1[1] - 3, p1[0] + 3, p1[1] + 3), fill=(210, 220, 235))
                draw.text((p_start[0] + 6, p_start[1] - 10), day["from"], font=tiny_font, fill=(255, 255, 255))
                draw.text((p_end[0] + 6, p_end[1] - 10), day["to"], font=tiny_font, fill=(255, 215, 105))

                pulse = 6 + int(abs(math.sin(global_frame * 0.3)) * 5)
                draw.ellipse((curr_x - pulse, curr_y - pulse, curr_x + pulse, curr_y + pulse), outline=(255, 95, 50), width=2)
                draw.ellipse((curr_x - 5, curr_y - 5, curr_x + 5, curr_y + 5), fill=(255, 95, 50))

                # Bottom Progress Bar
                draw.rectangle((0, 665, width, height), fill=(14, 22, 38))
                overall_progress = (day_idx + t) / len(itinerary)
                draw.rectangle((25, 678, 1255, 692), fill=(50, 62, 82))
                draw.rectangle((25, 678, 25 + int(1230 * overall_progress), 692), fill=(80, 220, 195))
                draw.text((25, 697), f"Route Progress: {int(overall_progress * 100)}%   |   Est. Budget: INR {expedition['budget']['estimated_total_inr']:,}", font=tiny_font, fill=(195, 205, 220))

                frame_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                video.write(frame_bgr)
                global_frame += 1

            # FIX: update after each day's frames (was inside the frame loop)
            cumulative_km += day["distance_km"]
    finally:
        video.release()

    print("\nContinuous bike-driving video created successfully!")
    print("Video location:", output_file)


# ==================================================
# STEP 8: MAIN PROGRAM
# ==================================================

def main():
    print("========================================")
    print(" INDIA MOTORCYCLE EXPEDITION PLANNER")
    print("========================================")

    try:
        prompt = load_prompt()
        schema = load_schema()
        data = generate_valid_itinerary(prompt, schema)

        if data is not None:
            save_output(data, "itinerary.json")
            create_expedition_video(data)
            print("\n========================================")
            print(" SUCCESS! JSON and VIDEO generated.")
            print("========================================")
        else:
            print("\nAll generation attempts failed. Review master_prompt.txt and retry.")
    except Exception as error:
        print("\nERROR:", error)


if __name__ == "__main__":
    main()