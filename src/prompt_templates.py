def build_soc_prompt(alert_text: str, ml_prediction: str | None = None) -> str:
    return f"""
You are a Security Operations Center analyst.

Your task is to analyze a structured security alert and generate triage guidance.

Allowed IncidentGrade labels:
- TruePositive: the alert likely represents a real malicious or suspicious security incident.
- FalsePositive: the alert is likely an incorrect detection or non-issue.
- BenignPositive: the alert is valid but likely caused by benign activity.

ML prediction:
{ml_prediction if ml_prediction else "Not provided"}

Return only valid JSON using this exact schema:
{{
  "predicted_label": "TruePositive or FalsePositive or BenignPositive",
  "confidence": 0.0,
  "reasoning_summary": "brief analyst explanation",
  "recommended_actions": ["action 1", "action 2", "action 3"],
  "containment_priority": "Low, Medium, or High"
}}

Security alert:
{alert_text}
""".strip()


def build_hybrid_explanation_prompt(alert_text: str, ml_prediction: str) -> str:
    return f"""
You are a SOC copilot.

A machine learning classifier has already predicted the incident label.
Do not change the ML prediction. Use it as the fixed triage label.

ML prediction:
{ml_prediction}

Generate analyst-friendly explanation and response guidance.

Return only valid JSON using this exact schema:
{{
  "predicted_label": "{ml_prediction}",
  "confidence": 0.0,
  "reasoning_summary": "brief explanation of why this alert may have this label",
  "recommended_actions": ["action 1", "action 2", "action 3"],
  "containment_priority": "Low, Medium, or High"
}}

Security alert:
{alert_text}
""".strip()