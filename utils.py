import requests
import base64
import re
import time
import streamlit as st

API_KEY = st.secrets["API_KEY"]

# Try multiple models in order if one fails
MODELS = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
    "gemini-2.0-flash",
    "gemini-1.0-pro-vision-latest",
]

PROMPT = """
You are an expert botanist and plant identification AI.
Carefully analyze the image and identify the flower.

Respond STRICTLY in this exact format (do not skip any field):

Name: <common name>
Scientific Name: <scientific name>
Family: <plant family name>
Origin: <country or region of origin>
Top 3 Predictions:
1. <flower name> - <confidence>%
2. <flower name> - <confidence>%
3. <flower name> - <confidence>%
Soil: <soil type and requirements>
Sunlight: <full sun / partial shade / full shade>
Watering: <watering frequency and amount>
Uses: <medicinal, decorative, culinary uses>
Care Tips: <pruning, fertilizing, seasonal tips>
Fun Fact: <one interesting fact about this flower>
Native Regions: <comma separated list of countries/continents where this flower naturally grows>
Bloom Season: <Spring / Summer / Autumn / Winter / Year-round>
Explanation: <2-3 sentence AI explanation about this flower>

If no flower is detected, respond with:
Name: Unknown
Scientific Name: N/A
Family: N/A
Origin: N/A
Top 3 Predictions:
1. Not a flower - 100%
2. N/A - 0%
3. N/A - 0%
Soil: N/A
Sunlight: N/A
Watering: N/A
Uses: N/A
Care Tips: N/A
Fun Fact: N/A
Native Regions: N/A
Bloom Season: N/A
Explanation: No flower was detected in the provided image. Please try again with a clear flower photo.
"""


def call_gemini(model: str, image_b64: str) -> dict:
    """Call a specific Gemini model."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={API_KEY}"
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_b64,
                }}
            ]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1500,
        },
    }
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    return parse_response(raw_text)


def analyze_flower(image_bytes: bytes) -> dict:
    """
    Try multiple Gemini models with automatic fallback.
    Returns parsed flower info dict.
    """
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    last_error = None

    for model in MODELS:
        try:
            result = call_gemini(model, image_b64)
            result["model_used"] = model
            return result

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            # 429 = quota exceeded → try next model
            # 404 = model not found → try next model
            if status in [429, 404]:
                last_error = f"Model `{model}` unavailable (code {status}), trying next..."
                time.sleep(1)
                continue
            else:
                return error_result(f"API error {status}: {e.response.text}")

        except requests.exceptions.Timeout:
            last_error = f"Model `{model}` timed out, trying next..."
            continue

        except Exception as e:
            last_error = str(e)
            continue

    # All models failed
    return error_result(
        "⚠️ All Gemini models are currently quota-limited. "
        "Please wait 1 minute and try again, or update your API key in Streamlit secrets."
    )


def parse_response(text: str) -> dict:
    """Parse structured Gemini response into a clean dict."""

    def extract(label):
        pattern = rf"{label}:\s*(.+?)(?=\n[A-Za-z ]{{1,25}}:|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else "N/A"

    predictions = []
    pred_block = re.search(
        r"Top 3 Predictions:(.*?)(?=\nSoil:|\Z)", text, re.DOTALL | re.IGNORECASE
    )
    if pred_block:
        lines = pred_block.group(1).strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit():
                conf_match = re.search(r"(\d+)%", line)
                confidence = int(conf_match.group(1)) if conf_match else 80
                name_part = re.sub(r"^\d+\.\s*", "", line)
                name_part = re.sub(r"\s*-\s*\d+%", "", name_part).strip()
                predictions.append({"name": name_part, "confidence": confidence})

    if not predictions:
        predictions = [
            {"name": extract("Name"), "confidence": 85},
            {"name": "Similar species", "confidence": 10},
            {"name": "Unknown variety", "confidence": 5},
        ]

    native_raw = extract("Native Regions")
    native_regions = [r.strip() for r in native_raw.split(",")] if native_raw != "N/A" else []

    return {
        "name": extract("Name"),
        "scientific_name": extract("Scientific Name"),
        "family": extract("Family"),
        "origin": extract("Origin"),
        "predictions": predictions,
        "soil": extract("Soil"),
        "sunlight": extract("Sunlight"),
        "watering": extract("Watering"),
        "uses": extract("Uses"),
        "care_tips": extract("Care Tips"),
        "fun_fact": extract("Fun Fact"),
        "native_regions": native_regions,
        "bloom_season": extract("Bloom Season"),
        "explanation": extract("Explanation"),
        "raw": text,
        "model_used": "unknown",
        "error": None,
    }


def error_result(message: str) -> dict:
    return {
        "name": "Error",
        "scientific_name": "N/A",
        "family": "N/A",
        "origin": "N/A",
        "predictions": [],
        "soil": "N/A",
        "sunlight": "N/A",
        "watering": "N/A",
        "uses": "N/A",
        "care_tips": "N/A",
        "fun_fact": "N/A",
        "native_regions": [],
        "bloom_season": "N/A",
        "explanation": message,
        "raw": message,
        "model_used": "none",
        "error": message,
    }
