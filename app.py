import streamlit as st
import plotly.express as px

from src.sample_data import load_sample_alerts
from src.llm_client import call_qwen_api


st.set_page_config(
    page_title="LLM-SOC Alert Triage",
    page_icon="🛡️",
    layout="wide"
)


LABEL_OPTIONS = [
    "TruePositive",
    "FalsePositive",
    "BenignPositive"
]


def show_label_badge(label: str):
    if label == "TruePositive":
        st.error(f"IncidentGrade: {label}")
    elif label == "FalsePositive":
        st.warning(f"IncidentGrade: {label}")
    elif label == "BenignPositive":
        st.success(f"IncidentGrade: {label}")
    else:
        st.info(f"IncidentGrade: {label}")


st.sidebar.title("LLM-SOC")
st.sidebar.caption("Hybrid Alert Triage and Response Guidance")

mode = st.sidebar.selectbox(
    "Analysis Mode",
    [
        "Hybrid ML + Qwen Explanation",
        "Direct Qwen Classification"
    ]
)

use_manual_input = st.sidebar.checkbox(
    "Manual alert input",
    value=False
)

st.sidebar.divider()

use_mock = st.secrets.get("USE_MOCK_LLM", True)

if use_mock:
    st.sidebar.warning("Mock LLM mode is ON")
else:
    st.sidebar.success("Connected to external Qwen API")

st.title("LLM-SOC Hybrid Alert Triage Dashboard")

tab1, tab2, tab3 = st.tabs([
    "Single Alert Triage",
    "Dataset Explorer",
    "API Debug"
])


with tab1:
    st.subheader("Single Alert Triage")

    df = load_sample_alerts()

    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        if use_manual_input:
            alert_text = st.text_area(
                "Paste alert_text",
                height=260,
                placeholder="Category: CredentialAccess | MitreTechniques: T1110..."
            )
            true_label = "Unknown"

        else:
            selected_idx = st.selectbox(
                "Select sample alert",
                options=list(range(len(df))),
                format_func=lambda i: f"Row {i} | Label: {df.iloc[i].get('label', 'Unknown')}"
            )

            selected_row = df.iloc[selected_idx]
            alert_text = selected_row["alert_text"]
            true_label = selected_row.get("label", "Unknown")

            st.text_area(
                "Selected alert_text",
                value=alert_text,
                height=260
            )

        st.caption(f"Ground-truth label: {true_label}")

    with col_right:
        st.markdown("### ML Prediction")

        ml_prediction = st.selectbox(
            "Select ML prediction",
            LABEL_OPTIONS,
            index=0
        )

        st.caption(
            "For now this is manual. Later, connect this to Logistic Regression output."
        )

        show_label_badge(ml_prediction)

        run_button = st.button(
            "Run LLM SOC Analysis",
            type="primary",
            use_container_width=True
        )

    if run_button:
        if not alert_text.strip():
            st.error("Alert text is empty.")
        else:
            selected_mode = "hybrid" if mode == "Hybrid ML + Qwen Explanation" else "direct"

            with st.spinner("Calling Qwen SOC analyst..."):
                result = call_qwen_api(
                    alert_text=alert_text,
                    ml_prediction=ml_prediction,
                    mode=selected_mode
                )

            st.divider()

            if not result["ok"]:
                st.error("LLM service failed.")
                st.code(result.get("error", "Unknown error"))
            else:
                parsed = result.get("parsed", {})

                st.markdown("## SOC Analysis Result")

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric("LLM Label", parsed.get("predicted_label", "Unknown"))

                with c2:
                    st.metric("Confidence", parsed.get("confidence", 0.0))

                with c3:
                    st.metric("Latency", f"{result.get('latency_seconds', 0)}s")

                with c4:
                    st.metric("Valid JSON", str(result.get("valid_json", False)))

                st.markdown("### Analyst Explanation")
                st.write(parsed.get("reasoning_summary", "No explanation provided."))

                st.markdown("### Recommended Actions")

                actions = parsed.get("recommended_actions", [])

                if actions:
                    for action in actions:
                        st.write(f"- {action}")
                else:
                    st.write("No actions provided.")

                st.markdown("### Containment Priority")
                st.info(parsed.get("containment_priority", "Unknown"))

                with st.expander("Raw LLM Response"):
                    st.write(result.get("raw_response"))

                with st.expander("Full Parsed Result"):
                    st.json(parsed)


with tab2:
    st.subheader("Dataset Explorer")

    df = load_sample_alerts()

    st.write("Loaded samples:", len(df))

    st.dataframe(df.head(100), use_container_width=True)

    if "label" in df.columns:
        label_counts = df["label"].value_counts().reset_index()
        label_counts.columns = ["label", "count"]

        fig = px.bar(
            label_counts,
            x="label",
            y="count",
            title="Label Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Sample alert_text")

    sample_idx = st.slider(
        "Sample row",
        min_value=0,
        max_value=max(len(df) - 1, 0),
        value=0
    )

    st.code(df.iloc[sample_idx]["alert_text"])


with tab3:
    st.subheader("API Debug")

    st.write("Use this tab to test whether Streamlit can reach the Qwen API.")

    debug_alert = st.text_area(
        "Debug alert_text",
        value="Category: CredentialAccess | MitreTechniques: T1110 | EntityType: User | EvidenceRole: Impacted | SuspicionLevel: Suspicious",
        height=160
    )

    debug_prediction = st.selectbox(
        "Debug ML prediction",
        LABEL_OPTIONS,
        key="debug_prediction"
    )

    if st.button("Test API Connection"):
        with st.spinner("Testing API..."):
            result = call_qwen_api(
                alert_text=debug_alert,
                ml_prediction=debug_prediction,
                mode="hybrid"
            )

        if result["ok"]:
            st.success("API call successful.")
            st.json(result)
        else:
            st.error("API call failed.")
            st.code(result.get("error", "Unknown error"))