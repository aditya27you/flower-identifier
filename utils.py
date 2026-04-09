import requests
import base64
import re
import streamlit as st

API_KEY = st.secrets["API_KEY"]


def analyze_flower(image_bytes: bytes) -> dict:
    """
    Sends image bytes to Gemini Vision API and returns parsed flower info.
    Returns a dict with keys: name, scientific_name, predictions, soil, uses, care_tips, explanation, raw
    """

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={API_KEY}"
    )

    prompt = """
You are an expert botanist and plant identification AI.
Carefully analyze the image and identify the flower.

Respond STRICTLY in this exact format (do not skip any field):

Name: <common name>
Scientific Name: <scientific name>
Top 3 Predictions:
1. <flower name> - <confidence>%
2. <flower name> - <confidence>%
3. <flower name> - <confidence>%
Soil: <soil type and requirements>
Uses: <medicinal, decorative, culinary uses>
Care Tips: <watering, sunlight, pruning tips>
Explanation: <2-3 sentence AI explanation about this flower>

If no flower is detected, respond with:
Name: Unknown
Scientific Name: N/A
Top 3 Predictions:
1. Not a flower - 100%
2. N/A - 0%
3. N/A - 0%
Soil: N/A
Uses: N/A
Care Tips: N/A
Explanation: No flower was detected in the provided image. Please try again with a clear flower photo.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode("utf-8"),
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
        },
    }

    try:
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

    except requests.exceptions.Timeout:
        return error_result("Request timed out. Please try again.")
    except requests.exceptions.HTTPError as e:
        return error_result(f"API error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        return error_result(f"Unexpected error: {str(e)}")


def parse_response(text: str) -> dict:
    """Parse the structured Gemini response into a clean dict."""

    def extract(label):
        pattern = rf"{label}:\s*(.+?)(?=\n[A-Z]|\Z)"
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

    return {
        "name": extract("Name"),
        "scientific_name": extract("Scientific Name"),
        "predictions": predictions,
        "soil": extract("Soil"),
        "uses": extract("Uses"),
        "care_tips": extract("Care Tips"),
        "explanation": extract("Explanation"),
        "raw": text,
        "error": None,
    }


def error_result(message: str) -> dict:
    return {
        "name": "Error",
        "scientific_name": "N/A",
        "predictions": [],
        "soil": "N/A",
        "uses": "N/A",
        "care_tips": "N/A",
        "explanation": message,
        "raw": message,
        "error": message,
    }
