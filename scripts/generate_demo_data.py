from pathlib import Path
import csv
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEMO_DIR = PROJECT_ROOT / "data" / "demo"

ASSET_METADATA_FILE = PROCESSED_DIR / "asset_metadata.json"
DOCUMENTS_INDEX_FILE = PROCESSED_DIR / "documents_index.csv"
SENSOR_SUMMARY_FILE = PROCESSED_DIR / "sensor_summary.json"
COMPLIANCE_MATRIX_FILE = PROCESSED_DIR / "compliance_matrix.json"
WORK_ORDERS_FILE = PROCESSED_DIR / "work_orders_processed.json"
BENCHMARK_QUESTIONS_FILE = PROCESSED_DIR / "benchmark_questions.json"
KNOWLEDGE_GRAPH_FILE = PROCESSED_DIR / "knowledge_graph_seed.json"


def read_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_csv_rows(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def write_json(file_name, data):
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    output_file = DEMO_DIR / file_name

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_file


def generate_assets_demo(asset_metadata):
    assets = []

    for asset in asset_metadata.get("assets", []):
        risk_score = int(asset["risk_score"])
        health_score = max(0, 100 - risk_score)

        assets.append({
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "risk_score": risk_score,
            "health_score": health_score,
            "risk_level": asset["risk_level"],
            "sensor_status": asset["sensor_status"],
            "compliance_status": asset["compliance_status"],
            "total_compliance_gaps": asset["total_compliance_gaps"],
            "open_or_delayed_work_orders": asset["open_or_delayed_work_orders"],
            "connected_sensors": asset["connected_sensors"],
            "critical_story": asset["critical_story"],
            "source_documents": asset["source_documents"],
            "pid_reference": asset["pid_reference"]
        })

    return {
        "artifact": "demo_assets",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_assets": len(assets),
        "assets": assets
    }


def generate_documents_demo(documents):
    demo_documents = []

    for document in documents:
        demo_documents.append({
            "document_id": document["document_id"],
            "title": document["title"],
            "document_type": document["document_type"],
            "source_group": document["source_group"],
            "asset_ids": document["asset_ids"].split(";") if document["asset_ids"] else [],
            "tags": document["tags"].split(";") if document["tags"] else [],
            "summary": document["summary"],
            "relative_path": document["relative_path"],
            "word_count": int(document["word_count"]) if document["word_count"] else 0
        })

    return {
        "artifact": "demo_documents",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_documents": len(demo_documents),
        "documents": demo_documents
    }


def generate_health_scores(asset_metadata, sensor_summary):
    sensor_level = sensor_summary.get("sensor_level_summary", [])

    sensor_by_asset = {}

    for sensor in sensor_level:
        asset_id = sensor["asset_id"]

        if asset_id not in sensor_by_asset:
            sensor_by_asset[asset_id] = []

        sensor_by_asset[asset_id].append({
            "sensor_name": sensor["sensor_name"],
            "latest_value": sensor["latest_value"],
            "unit": sensor["unit"],
            "latest_status": sensor["latest_status"],
            "trend_direction": sensor["trend_direction"]
        })

    health_scores = []

    for asset in asset_metadata.get("assets", []):
        risk_score = int(asset["risk_score"])
        health_score = max(0, 100 - risk_score)

        if health_score >= 70:
            health_label = "Healthy"
        elif health_score >= 40:
            health_label = "Needs Attention"
        else:
            health_label = "Critical Attention Needed"

        health_scores.append({
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            "asset_type": asset["asset_type"],
            "risk_score": risk_score,
            "health_score": health_score,
            "health_label": health_label,
            "risk_level": asset["risk_level"],
            "sensor_status": asset["sensor_status"],
            "sensor_signals": sensor_by_asset.get(asset["asset_id"], []),
            "summary": asset["critical_story"]
        })

    return {
        "artifact": "demo_health_scores",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "health_scores": health_scores
    }


def generate_maintenance_events(work_orders_processed):
    events = []

    for work_order in work_orders_processed.get("work_orders", []):
        events.append({
            "event_id": work_order["work_order_id"],
            "asset_id": work_order["asset_id"],
            "asset_name": work_order["asset_name"],
            "event_type": work_order["work_order_type"],
            "priority": work_order["priority"],
            "status": work_order["status"],
            "created_date": work_order["created_date"],
            "due_date": work_order["due_date"],
            "description": work_order["description"],
            "linked_document": work_order["linked_document"],
            "compliance_related": work_order["compliance_related"]
        })

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    events = sorted(
        events,
        key=lambda event: (
            priority_order.get(event["priority"], 99),
            event["due_date"]
        )
    )

    return {
        "artifact": "demo_maintenance_events",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_events": len(events),
        "events": events
    }


def generate_compliance_demo(compliance_matrix):
    return {
        "artifact": "demo_compliance_matrix",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "asset_compliance_summary": compliance_matrix.get("asset_compliance_summary", []),
        "gaps": compliance_matrix.get("gaps", [])
    }


def generate_knowledge_graph_demo(knowledge_graph):
    nodes = knowledge_graph.get("nodes", [])
    edges = knowledge_graph.get("edges", [])

    important_node_types = {
        "Project",
        "Asset",
        "Document",
        "SensorSignal",
        "ComplianceGap",
        "WorkOrder",
        "Instrument",
        "Valve",
        "RiskClass",
        "ProcessNode"
    }

    filtered_nodes = [
        node for node in nodes
        if node.get("type") in important_node_types
    ]

    allowed_node_ids = {node["id"] for node in filtered_nodes}

    filtered_edges = [
        edge for edge in edges
        if edge.get("source") in allowed_node_ids and edge.get("target") in allowed_node_ids
    ]

    return {
        "artifact": "demo_knowledge_graph",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "node_count": len(filtered_nodes),
        "edge_count": len(filtered_edges),
        "nodes": filtered_nodes,
        "edges": filtered_edges
    }


def generate_rag_seed_questions(benchmark_questions):
    questions = []

    for question in benchmark_questions.get("questions", []):
        questions.append({
            "question_id": question["question_id"],
            "question": question["question"],
            "expected_answer_type": question["expected_answer_type"],
            "expected_assets": question["expected_assets"],
            "expected_sources": question["expected_sources"]
        })

    return {
        "artifact": "demo_rag_seed_questions",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_questions": len(questions),
        "questions": questions
    }


def generate_demo_answers():
    answers = [
        {
            "question": "Why is P-101 high risk?",
            "asset_id": "P-101",
            "answer": "P-101 is high risk because vibration reached a critical level, bearing temperature is in warning range, abnormal bearing noise was reported, and lubrication evidence is missing.",
            "supporting_sources": [
                "IR-P101-001",
                "IR-P101-002",
                "INC-P101-001",
                "COMP-001"
            ]
        },
        {
            "question": "What is the likely root cause of P-101 vibration?",
            "asset_id": "P-101",
            "answer": "The likely root causes are bearing wear, lubrication degradation, shaft misalignment, loose mounting, or mechanical imbalance. Missing lubrication evidence increases confidence in lubrication-related bearing risk.",
            "supporting_sources": [
                "INC-P101-001",
                "IR-P101-001",
                "IR-P101-002",
                "SOP-P101-001"
            ]
        },
        {
            "question": "Why is C-201 medium risk?",
            "asset_id": "C-201",
            "answer": "C-201 is medium risk because estimated RUL is decreasing, outlet temperature is above normal range, pressure ratio is unstable, and filter replacement verification is delayed.",
            "supporting_sources": [
                "IR-C201-001",
                "SOP-C201-001",
                "sensor_summary.json",
                "work_orders_processed.json"
            ]
        },
        {
            "question": "Why is HX-301 suspected to be fouled?",
            "asset_id": "HX-301",
            "answer": "HX-301 is suspected to be fouled because outlet temperature dropped below normal, pressure drop increased, efficiency index decreased, and cleaning/fouling inspection evidence is overdue.",
            "supporting_sources": [
                "IR-HX301-001",
                "INC-HX301-001",
                "SOP-HX301-001",
                "sensor_summary.json"
            ]
        },
        {
            "question": "Which assets are non-compliant?",
            "asset_id": "ALL",
            "answer": "P-101, C-201, and HX-301 all have compliance gaps. P-101 has missing lubrication and work permit evidence, C-201 has delayed filter replacement verification, and HX-301 has overdue cleaning evidence and missing work permit evidence.",
            "supporting_sources": [
                "COMP-001",
                "IR-GEN-001",
                "ground_truth_compliance_gaps.csv",
                "compliance_matrix.json"
            ]
        }
    ]

    return {
        "artifact": "demo_answers",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "answers": answers
    }


def generate_dashboard_summary(asset_metadata, compliance_matrix, work_orders_processed, documents, knowledge_graph):
    assets = asset_metadata.get("assets", [])
    gaps = compliance_matrix.get("gaps", [])
    work_orders = work_orders_processed.get("work_orders", [])

    high_risk_assets = [
        asset["asset_id"] for asset in assets
        if asset["risk_level"] == "High"
    ]

    medium_risk_assets = [
        asset["asset_id"] for asset in assets
        if asset["risk_level"] == "Medium"
    ]

    open_or_delayed_work_orders = [
        work_order["work_order_id"] for work_order in work_orders
        if work_order["status"] in ["Open", "Delayed"]
    ]

    high_severity_gaps = [
        gap["gap_id"] for gap in gaps
        if gap["gap_severity"] == "High"
    ]

    return {
        "artifact": "demo_dashboard_summary",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_assets": len(assets),
        "high_risk_assets": high_risk_assets,
        "medium_risk_assets": medium_risk_assets,
        "total_documents": len(documents),
        "total_compliance_gaps": len(gaps),
        "high_severity_gaps": high_severity_gaps,
        "total_work_orders": len(work_orders),
        "open_or_delayed_work_orders": open_or_delayed_work_orders,
        "knowledge_graph_nodes": knowledge_graph.get("node_count"),
        "knowledge_graph_edges": knowledge_graph.get("edge_count"),
        "demo_story": "P-101 is the highest-priority risk asset; C-201 needs compressor maintenance planning; HX-301 needs fouling inspection and cleaning evidence."
    }


def main():
    print("PlantMind AI - Demo Data Generator")
    print("=" * 50)

    asset_metadata = read_json(ASSET_METADATA_FILE)
    documents = read_csv_rows(DOCUMENTS_INDEX_FILE)
    sensor_summary = read_json(SENSOR_SUMMARY_FILE)
    compliance_matrix = read_json(COMPLIANCE_MATRIX_FILE)
    work_orders_processed = read_json(WORK_ORDERS_FILE)
    benchmark_questions = read_json(BENCHMARK_QUESTIONS_FILE)
    knowledge_graph = read_json(KNOWLEDGE_GRAPH_FILE)

    outputs = []

    outputs.append(write_json("assets.json", generate_assets_demo(asset_metadata)))
    outputs.append(write_json("documents.json", generate_documents_demo(documents)))
    outputs.append(write_json("health_scores.json", generate_health_scores(asset_metadata, sensor_summary)))
    outputs.append(write_json("maintenance_events.json", generate_maintenance_events(work_orders_processed)))
    outputs.append(write_json("compliance_matrix.json", generate_compliance_demo(compliance_matrix)))
    outputs.append(write_json("knowledge_graph.json", generate_knowledge_graph_demo(knowledge_graph)))
    outputs.append(write_json("rag_seed_questions.json", generate_rag_seed_questions(benchmark_questions)))
    outputs.append(write_json("demo_answers.json", generate_demo_answers()))
    outputs.append(write_json(
        "dashboard_summary.json",
        generate_dashboard_summary(
            asset_metadata=asset_metadata,
            compliance_matrix=compliance_matrix,
            work_orders_processed=work_orders_processed,
            documents=documents,
            knowledge_graph=knowledge_graph
        )
    ))

    print("Demo files created:")

    for output in outputs:
        print(f" - {output}")

    print("\nDay 3 demo data generation completed.")


if __name__ == "__main__":
    main()