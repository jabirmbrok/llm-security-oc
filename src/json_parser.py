import json
import re
from typing import Any, Dict


def extract_json_from_text(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "valid_json": False,
            "parsed": None,
            "error": "Empty response"
        }

    try:
        parsed = json.loads(text)
        return {
            "valid_json": True,
            "parsed": parsed,
            "error": None
        }
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return {
            "valid_json": False,
            "parsed": None,
            "error": "No JSON object found"
        }

    try:
        parsed = json.loads(match.group())
        return {
            "valid_json": True,
            "parsed": parsed,
            "error": None
        }
    except Exception as e:
        return {
            "valid_json": False,
            "parsed": None,
            "error": str(e)
        }


def normalize_label(label: str) -> str:
    if not label:
        return "Unknown"

    clean = label.strip().lower().replace(" ", "").replace("_", "")

    mapping = {
        "truepositive": "TruePositive",
        "tp": "TruePositive",
        "malicious": "TruePositive",
        "attack": "TruePositive",

        "falsepositive": "FalsePositive",
        "fp": "FalsePositive",

        "benignpositive": "BenignPositive",
        "bp": "BenignPositive",
        "benign": "BenignPositive",
        "safe": "BenignPositive",
    }

    return mapping.get(clean, "Unknown")


def validate_llm_result(parsed: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(parsed, dict):
        return {
            "predicted_label": "Unknown",
            "confidence": 0.0,
            "reasoning_summary": "Invalid LLM response format.",
            "recommended_actions": [],
            "containment_priority": "Unknown"
        }

    label = normalize_label(parsed.get("predicted_label", ""))

    try:
        confidence = float(parsed.get("confidence", 0.0))
    except Exception:
        confidence = 0.0

    confidence = max(0.0, min(confidence, 1.0))

    actions = parsed.get("recommended_actions", [])
    if isinstance(actions, str):
        actions = [actions]
    if not isinstance(actions, list):
        actions = []

    return {
        "predicted_label": label,
        "confidence": confidence,
        "reasoning_summary": parsed.get("reasoning_summary", "No explanation provided."),
        "recommended_actions": actions,
        "containment_priority": parsed.get("containment_priority", "Unknown")
    }