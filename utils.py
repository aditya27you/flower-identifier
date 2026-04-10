import requests
import base64
import time
import streamlit as st

HF_TOKEN = st.secrets["HF_TOKEN"]

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# ── Step 1: Use BLIP to caption the image ──────────────────────────────────
BLIP_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

# ── Step 2: Use Mistral to generate flower details ─────────────────────────
MISTRAL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"


def caption_image(image_bytes: bytes) -> str:
    """Use BLIP to get a text caption of the flower image."""
    for attempt in range(3):
        try:
            response = requests.post(
                BLIP_URL,
                headers=HEADERS,
                data=image_bytes,
                timeout=30,
            )
            if response.status_code == 503:
                # Model is loading — wait and retry
                wait = response.json().get("estimated_time", 20)
                time.sleep(min(wait, 20))
                continue
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "a flower")
            return "a flower"
        except Exception:
            time.sleep(5)
    return "a flower"


def get_flower_details(caption: str) -> str:
    """Use Mistral to generate detailed flower info from caption."""

    prompt = f"""<s>[INST]
You are an expert botanist. Based on this image description: "{caption}"

Identify the flower and respond STRICTLY in this exact format:

Name: <common name>
Scientific Name: <scientific name>
Family: <plant family>
Origin: <country or region>
Top 3 Predictions:
1. <flower name> - <confidence>%
2. <flower name> - <confidence>%
3. <flower name> - <confidence>%
Soil: <soil type>
Sunlight: <sunlight needs>
Watering: <watering needs>
Uses: <medicinal, decorative, culinary uses>
Care Tips: <care tips>
Fun Fact: <interesting fact>
Native Regions: <comma separated countries or continents>
Bloom Season: <season>
Explanation: <2-3 sentences about this flower>
[/INST]"""

    for attempt in range(3):
        try:
            response = requests.post(
                MISTRAL_URL,
                headers=HEADERS,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 600,
                        "temperature": 0.3,
                        "return_full_text": False,
                    }
                },
                timeout=60,
            )
            if response.status_code == 503:
                wait = response.json().get("estimated_time", 20)
                time.sleep(min(wait, 25))
                continue
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "")
            return ""
        except Exception:
            time.sleep(5)
    return ""


def analyze_flower(image_bytes: bytes) -> dict:
    """
    Full pipeline: image → BLIP caption → Mistral details → parsed result
    """
    try:
        # Step 1: Caption the image
        caption = caption_image(image_bytes)

        # Step 2: Get flower details from caption
        raw_text = get_flower_details(caption)

        if not raw_text.strip():
            return error_result("Could not generate flower details. Please try again.")

        result = parse_response(raw_text)
        result["caption"] = caption
        return result

    except Exception as e:
        return error_result(f"Unexpected error: {str(e)}")


def parse_response(text: str) -> dict:
    """Parse structured response into a clean dict."""
    import re

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
        "caption": "",
        "raw": text,
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
        "caption": "",
        "raw": message,
        "error": message,
    }
