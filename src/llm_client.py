import time
import requests
import streamlit as st

from src.prompt_templates import build_soc_prompt, build_hybrid_explanation_prompt
from src.json_parser import extract_json_from_text, validate_llm_result


def mock_llm_response(alert_text: str, ml_prediction: str | None = None):
    label = ml_prediction if ml_prediction else "BenignPositive"

    parsed = {
        "predicted_label": label,
        "confidence": 0.76,
        "reasoning_summary": "This is a mock SOC explanation. Replace mock mode with the real Qwen LoRA API when the VM endpoint is ready.",
        "recommended_actions": [
            "Review related alerts from the same IncidentId or AlertId.",
            "Check affected entity and evidence role.",
            "Escalate if similar activity is observed across multiple assets."
        ],
        "containment_priority": "Medium"
    }

    return {
        "ok": True,
        "source": "mock",
        "latency_seconds": 0.15,
        "raw_response": parsed,
        "valid_json": True,
        "parsed": parsed
    }


def call_qwen_api(
    alert_text: str,
    ml_prediction: str | None = None,
    mode: str = "hybrid"
):
    use_mock = st.secrets.get("USE_MOCK_LLM", True)

    if use_mock:
        return mock_llm_response(alert_text, ml_prediction)

    api_url = st.secrets.get("SOC_API_URL", "")
    api_key = st.secrets.get("SOC_API_KEY", "")

    if not api_url:
        return {
            "ok": False,
            "source": "api",
            "error": "SOC_API_URL is not configured.",
            "latency_seconds": 0
        }

    if mode == "hybrid" and ml_prediction:
        prompt = build_hybrid_explanation_prompt(alert_text, ml_prediction)
    else:
        prompt = build_soc_prompt(alert_text, ml_prediction)

    payload = {
        "alert_text": alert_text,
        "ml_prediction": ml_prediction,
        "prompt": prompt,
        "mode": mode
    }

    headers = {
        "X-API-Key": api_key
    }

    start = time.time()

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=180
        )
        response.raise_for_status()

        data = response.json()
        latency = round(time.time() - start, 3)

        raw_output = data.get("response", data)

        if isinstance(raw_output, dict):
            parsed = raw_output
            valid_json = True
            error = None
        else:
            extracted = extract_json_from_text(str(raw_output))
            valid_json = extracted["valid_json"]
            parsed = extracted["parsed"]
            error = extracted["error"]

        clean_result = validate_llm_result(parsed)

        return {
            "ok": True,
            "source": "api",
            "latency_seconds": data.get("latency_seconds", latency),
            "raw_response": raw_output,
            "valid_json": valid_json,
            "json_error": error,
            "parsed": clean_result
        }

    except Exception as e:
        return {
            "ok": False,
            "source": "api",
            "error": str(e),
            "latency_seconds": round(time.time() - start, 3)
        }