import requests
import base64
import re
import time
import streamlit as st

API_KEY = st.secrets["GEMINI_API_KEY"]

# Models to try in order
MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b",
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
Native Regions: <comma separated list of countries or continents>
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
Explanation: No flower was detected. Please try again with a clear flower photo.
"""


def call_model(model: str, image_b64: str) -> dict:
    """Call a single Gemini model."""
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
    return parse_response(raw_text), model


def analyze_flower(image_bytes: bytes) -> dict:
    """
    Try multiple Gemini models with smart retry and fallback.
    Automatically switches model if quota is exceeded.
    """
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    for model in MODELS:
        try:
            result, used_model = call_model(model, image_b64)
            result["model_used"] = used_model
            return result

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code

            if code == 429:
                # Quota exceeded — wait a bit then try next model
                try:
                    retry_after = int(
                        re.search(
                            r"retry in (\d+)",
                            e.response.text,
                            re.IGNORECASE
                        ).group(1)
                    )
                    wait = min(retry_after, 5)
                except Exception:
                    wait = 3
                time.sleep(wait)
                continue  # try next model

            elif code == 404:
                # Model not found — try next
                continue

            else:
                return error_result(f"API error {code}. Please check your API key.")

        except requests.exceptions.Timeout:
            continue

        except Exception as e:
            continue

    # All models failed
    return error_result(
        "All Gemini models are currently quota-limited on your account.\n\n"
        "Please:\n"
        "1. Wait 1 minute and try again\n"
        "2. Or get a new API key from aistudio.google.com\n"
        "3. Update GEMINI_API_KEY in Streamlit Secrets"
    )


def parse_response(text: str) -> dict:
    """Parse Gemini response into clean dict."""

    def extract(label):
        pattern = rf"{label}:\s*(.+?)(?=\n[A-Za-z ]{{1,25}}:|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else "N/A"

    # Parse predictions
    predictions = []
    pred_block = re.search(
        r"Top 3 Predictions:(.*?)(?=\nSoil:|\Z)", text, re.DOTALL | re.IGNORECASE
    )
    if pred_block:
        for line in pred_block.group(1).strip().split("\n"):
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
    native_regions = (
        [r.strip() for r in native_raw.split(",")]
        if native_raw != "N/A" else []
    )

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
