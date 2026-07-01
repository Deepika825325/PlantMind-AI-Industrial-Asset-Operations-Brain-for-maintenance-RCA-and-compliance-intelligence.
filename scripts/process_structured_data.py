from pathlib import Path
import json
import pandas as pd
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

STRUCTURED_DIR = RAW_DIR / "structured"
DRAWING_METADATA_FILE = RAW_DIR / "documents" / "drawings" / "PID-001_Demo_Process_Line.metadata.json"

WORK_ORDERS_FILE = STRUCTURED_DIR / "work_orders.csv"
SENSOR_READINGS_FILE = STRUCTURED_DIR / "sensor_readings.csv"
BENCHMARK_QUESTIONS_FILE = STRUCTURED_DIR / "benchmark_questions.csv"
COMPLIANCE_GAPS_FILE = STRUCTURED_DIR / "ground_truth_compliance_gaps.csv"

ASSET_MASTER = {
    "P-101": {
        "asset_id": "P-101",
        "asset_name": "Cooling Water Circulation Pump",
        "asset_type": "Pump",
        "critical_story": "High vibration, bearing temperature warning, abnormal noise, and missing lubrication evidence."
    },
    "C-201": {
        "asset_id": "C-201",
        "asset_name": "Process Air Compressor",
        "asset_type": "Compressor",
        "critical_story": "Decreasing RUL, outlet temperature warning, pressure ratio instability, and delayed filter verification."
    },
    "HX-301": {
        "asset_id": "HX-301",
        "asset_name": "Feed Preheater Heat Exchanger",
        "asset_type": "Heat Exchanger",
        "critical_story": "Low outlet temperature, high pressure drop, reduced efficiency, suspected fouling, and overdue cleaning evidence."
    },
}


def read_csv(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    return pd.read_csv(file_path)


def read_json(file_path):
    if not file_path.exists():
        return {}

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(file_name, data):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / file_name

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_file


def calculate_sensor_summary(sensor_df):
    sensor_df["timestamp"] = pd.to_datetime(sensor_df["timestamp"])

    summaries = []

    for (asset_id, sensor_name), group in sensor_df.groupby(["asset_id", "sensor_name"]):
        group = group.sort_values("timestamp")

        latest = group.iloc[-1]
        first = group.iloc[0]

        values = pd.to_numeric(group["value"], errors="coerce")

        trend_direction = "Stable"

        if len(values.dropna()) >= 2:
            if latest["value"] > first["value"]:
                trend_direction = "Increasing"
            elif latest["value"] < first["value"]:
                trend_direction = "Decreasing"

        summaries.append({
            "asset_id": asset_id,
            "sensor_name": sensor_name,
            "unit": str(latest["unit"]),
            "first_value": float(first["value"]),
            "latest_value": float(latest["value"]),
            "min_value": float(values.min()),
            "max_value": float(values.max()),
            "average_value": round(float(values.mean()), 3),
            "latest_status": str(latest["status"]),
            "trend_direction": trend_direction,
            "reading_count": int(len(group)),
            "first_timestamp": first["timestamp"].isoformat(),
            "latest_timestamp": latest["timestamp"].isoformat(),
            "source_dataset": str(latest["source_dataset"])
        })

    asset_level = []

    for asset_id, group in sensor_df.groupby("asset_id"):
        statuses = group["status"].value_counts().to_dict()

        if "Critical" in statuses:
            overall_status = "Critical"
        elif "Warning" in statuses:
            overall_status = "Warning"
        else:
            overall_status = "Normal"

        asset_level.append({
            "asset_id": asset_id,
            "overall_sensor_status": overall_status,
            "total_readings": int(len(group)),
            "status_counts": {str(k): int(v) for k, v in statuses.items()},
            "sensors": sorted(group["sensor_name"].unique().tolist())
        })

    return {
        "artifact": "sensor_summary",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "asset_level_summary": asset_level,
        "sensor_level_summary": summaries
    }


def calculate_compliance_matrix(compliance_df):
    gaps = []

    for _, row in compliance_df.iterrows():
        gaps.append({
            "gap_id": row["gap_id"],
            "asset_id": row["asset_id"],
            "requirement": row["requirement"],
            "expected_evidence": row["expected_evidence"],
            "current_status": row["current_status"],
            "evidence_file": "" if pd.isna(row.get("evidence_file")) else row.get("evidence_file"),
            "gap_severity": row["gap_severity"],
            "recommended_action": row["recommended_action"],
            "source_document": row["source_document"]
        })

    asset_summary = []

    for asset_id, group in compliance_df.groupby("asset_id"):
        high_count = int((group["gap_severity"] == "High").sum())
        medium_count = int((group["gap_severity"] == "Medium").sum())
        total_gaps = int(len(group))

        if high_count > 0:
            compliance_status = "High Risk Non-Compliant"
        elif medium_count > 0:
            compliance_status = "Medium Risk Non-Compliant"
        else:
            compliance_status = "Compliant"

        asset_summary.append({
            "asset_id": asset_id,
            "total_gaps": total_gaps,
            "high_severity_gaps": high_count,
            "medium_severity_gaps": medium_count,
            "compliance_status": compliance_status,
            "gap_ids": group["gap_id"].tolist()
        })

    return {
        "artifact": "compliance_matrix",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "asset_compliance_summary": asset_summary,
        "gaps": gaps
    }


def process_work_orders(work_orders_df):
    work_orders = []

    for _, row in work_orders_df.iterrows():
        work_orders.append({
            "work_order_id": row["work_order_id"],
            "asset_id": row["asset_id"],
            "asset_name": row["asset_name"],
            "work_order_type": row["work_order_type"],
            "priority": row["priority"],
            "status": row["status"],
            "created_date": row["created_date"],
            "due_date": row["due_date"],
            "description": row["description"],
            "linked_document": row["linked_document"],
            "compliance_related": row["compliance_related"]
        })

    asset_summary = []

    for asset_id, group in work_orders_df.groupby("asset_id"):
        status_counts = group["status"].value_counts().to_dict()
        priority_counts = group["priority"].value_counts().to_dict()

        asset_summary.append({
            "asset_id": asset_id,
            "total_work_orders": int(len(group)),
            "status_counts": {str(k): int(v) for k, v in status_counts.items()},
            "priority_counts": {str(k): int(v) for k, v in priority_counts.items()},
            "open_or_delayed_work_orders": group[group["status"].isin(["Open", "Delayed"])]["work_order_id"].tolist()
        })

    return {
        "artifact": "work_orders_processed",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "asset_work_order_summary": asset_summary,
        "work_orders": work_orders
    }


def process_benchmark_questions(benchmark_df):
    questions = []

    for _, row in benchmark_df.iterrows():
        questions.append({
            "question_id": row["question_id"],
            "question": row["question"],
            "expected_answer_type": row["expected_answer_type"],
            "expected_assets": str(row["expected_assets"]).split(";"),
            "expected_sources": str(row["expected_sources"]).split(";")
        })

    return {
        "artifact": "benchmark_questions",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_questions": len(questions),
        "questions": questions
    }


def calculate_asset_metadata(sensor_summary, compliance_matrix, work_orders_processed, drawing_metadata):
    sensor_by_asset = {
        item["asset_id"]: item
        for item in sensor_summary["asset_level_summary"]
    }

    compliance_by_asset = {
        item["asset_id"]: item
        for item in compliance_matrix["asset_compliance_summary"]
    }

    work_orders_by_asset = {
        item["asset_id"]: item
        for item in work_orders_processed["asset_work_order_summary"]
    }

    assets = []

    for asset_id, master in ASSET_MASTER.items():
        sensor_info = sensor_by_asset.get(asset_id, {})
        compliance_info = compliance_by_asset.get(asset_id, {})
        wo_info = work_orders_by_asset.get(asset_id, {})

        risk_score = 20

        sensor_status = sensor_info.get("overall_sensor_status", "Unknown")

        if sensor_status == "Critical":
            risk_score += 35
        elif sensor_status == "Warning":
            risk_score += 20

        risk_score += compliance_info.get("high_severity_gaps", 0) * 15
        risk_score += compliance_info.get("medium_severity_gaps", 0) * 8

        status_counts = wo_info.get("status_counts", {})
        priority_counts = wo_info.get("priority_counts", {})

        risk_score += status_counts.get("Delayed", 0) * 8
        risk_score += priority_counts.get("High", 0) * 6

        risk_score = min(risk_score, 100)

        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 45:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        assets.append({
            "asset_id": master["asset_id"],
            "asset_name": master["asset_name"],
            "asset_type": master["asset_type"],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "sensor_status": sensor_status,
            "compliance_status": compliance_info.get("compliance_status", "Unknown"),
            "total_compliance_gaps": compliance_info.get("total_gaps", 0),
            "open_or_delayed_work_orders": wo_info.get("open_or_delayed_work_orders", []),
            "connected_sensors": sensor_info.get("sensors", []),
            "critical_story": master["critical_story"],
            "source_documents": get_asset_source_documents(asset_id),
            "pid_reference": drawing_metadata.get("document_id", "PID-001")
        })

    return {
        "artifact": "asset_metadata",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_assets": len(assets),
        "assets": assets
    }


def get_asset_source_documents(asset_id):
    mapping = {
        "P-101": [
            "SOP-P101-001",
            "SOP-P101-002",
            "IR-P101-001",
            "IR-P101-002",
            "INC-P101-001",
            "COMP-001",
            "PID-001"
        ],
        "C-201": [
            "SOP-C201-001",
            "IR-C201-001",
            "COMP-001",
            "PID-001"
        ],
        "HX-301": [
            "SOP-HX301-001",
            "IR-HX301-001",
            "INC-HX301-001",
            "COMP-001",
            "PID-001"
        ],
    }

    return mapping.get(asset_id, [])


def main():
    print("PlantMind AI - Structured Data Processor")
    print("=" * 50)

    work_orders_df = read_csv(WORK_ORDERS_FILE)
    sensor_df = read_csv(SENSOR_READINGS_FILE)
    benchmark_df = read_csv(BENCHMARK_QUESTIONS_FILE)
    compliance_df = read_csv(COMPLIANCE_GAPS_FILE)
    drawing_metadata = read_json(DRAWING_METADATA_FILE)

    sensor_summary = calculate_sensor_summary(sensor_df)
    compliance_matrix = calculate_compliance_matrix(compliance_df)
    work_orders_processed = process_work_orders(work_orders_df)
    benchmark_questions = process_benchmark_questions(benchmark_df)

    asset_metadata = calculate_asset_metadata(
        sensor_summary=sensor_summary,
        compliance_matrix=compliance_matrix,
        work_orders_processed=work_orders_processed,
        drawing_metadata=drawing_metadata
    )

    output_files = []
    output_files.append(write_json("sensor_summary.json", sensor_summary))
    output_files.append(write_json("compliance_matrix.json", compliance_matrix))
    output_files.append(write_json("work_orders_processed.json", work_orders_processed))
    output_files.append(write_json("benchmark_questions.json", benchmark_questions))
    output_files.append(write_json("asset_metadata.json", asset_metadata))

    print("Structured outputs created:")

    for output_file in output_files:
        print(f" - {output_file}")

    print("\nDay 3 structured processing completed.")


if __name__ == "__main__":
    main()