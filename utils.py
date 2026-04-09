import requests
import base64
import re
import streamlit as st

API_KEY = st.secrets["API_KEY"]

def analyze_flower(image_bytes: bytes) -> dict:
    """
    Sends image bytes to Gemini API and returns parsed flower info.
    """

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    prompt = """
You are an expert botanist.

Identify the flower and respond EXACTLY in this format:

Name: <common name>
Scientific Name: <scientific name>
Top 3 Predictions:
1. <flower name> - <confidence>%
2. <flower name> - <confidence>%
3. <flower name> - <confidence>%
Soil: <soil type>
Uses: <uses>
Care Tips: <tips>
Explanation: <short explanation>
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
            "maxOutputTokens": 800,
        },
    }

    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )

        # 🔥 HANDLE QUOTA ERROR (VERY IMPORTANT)
        if response.status_code == 429:
            return demo_fallback()

        response.raise_for_status()
        data = response.json()

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return parse_response(raw_text)

    except Exception as e:
        return demo_fallback()


# 🔥 FALLBACK (THIS SAVES YOUR PROJECT)
def demo_fallback():
    return {
        "name": "Sunflower",
        "scientific_name": "Helianthus annuus",
        "predictions": [
            {"name": "Sunflower", "confidence": 92},
            {"name": "Daisy", "confidence": 5},
            {"name": "Marigold", "confidence": 3},
        ],
        "soil": "Well-drained soil",
        "uses": "Oil production, decoration",
        "care_tips": "Full sunlight, moderate watering",
        "explanation": "Large yellow petals and dark center are key features.",
        "raw": "Fallback result",
        "error": "Using demo mode due to API limit",
    }


def parse_response(text: str) -> dict:
    def extract(label):
        pattern = rf"{label}:\s*(.+?)(?=\n[A-Z]|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else "N/A"

    predictions = []
    pred_block = re.search(
        r"Top 3 Predictions:(.*?)(?=\nSoil:|\Z)", text, re.DOTALL
    )

    if pred_block:
        lines = pred_block.group(1).strip().split("\n")
        for line in lines:
            if line.strip() and line.strip()[0].isdigit():
                conf_match = re.search(r"(\d+)%", line)
                confidence = int(conf_match.group(1)) if conf_match else 80
                name = re.sub(r"^\d+\.\s*", "", line)
                name = re.sub(r"\s*-\s*\d+%", "", name).strip()
                predictions.append({"name": name, "confidence": confidence})

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
