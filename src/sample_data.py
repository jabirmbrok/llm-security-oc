import pandas as pd


def load_sample_alerts(path: str = "data/processed/llm_eval_subset.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)

        if "alert_text" not in df.columns:
            raise ValueError("CSV must contain alert_text column.")

        if "label" not in df.columns:
            df["label"] = "Unknown"

        return df

    except Exception:
        demo_data = [
            {
                "Id": "demo-001",
                "alert_text": "Category: CredentialAccess | MitreTechniques: T1110;T1078 | EntityType: User | EvidenceRole: Impacted | DetectorId: 468 | AlertTitle: 24 | SuspicionLevel: Suspicious | LastVerdict: Unknown | CountryCode: 242 | State: 1445 | City: 10630 | OSFamily: 5 | OSVersion: 66",
                "label": "TruePositive"
            },
            {
                "Id": "demo-002",
                "alert_text": "Category: Discovery | MitreTechniques: unknown | EntityType: Machine | EvidenceRole: Related | DetectorId: 122 | AlertTitle: 88 | SuspicionLevel: Low | LastVerdict: BenignPositive | CountryCode: 100 | State: 300 | City: 5000 | OSFamily: 5 | OSVersion: 70",
                "label": "BenignPositive"
            },
            {
                "Id": "demo-003",
                "alert_text": "Category: InitialAccess | MitreTechniques: T1566 | EntityType: Mailbox | EvidenceRole: Impacted | DetectorId: 712 | AlertTitle: 19 | SuspicionLevel: Unknown | LastVerdict: FalsePositive | CountryCode: 80 | State: 10 | City: 700 | OSFamily: unknown | OSVersion: unknown",
                "label": "FalsePositive"
            }
        ]

        return pd.DataFrame(demo_data)