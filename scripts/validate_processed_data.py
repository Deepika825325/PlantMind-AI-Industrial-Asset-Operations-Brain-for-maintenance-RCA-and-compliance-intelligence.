from pathlib import Path
import csv
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REQUIRED_FILES = [
    "documents_index.csv",
    "document_chunks.json",
    "asset_metadata.json",
    "compliance_matrix.json",
    "sensor_summary.json",
    "work_orders_processed.json",
    "benchmark_questions.json",
    "knowledge_graph_seed.json",
]


def read_json(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_csv_rows(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def validate_required_files():
    missing_files = []

    for file_name in REQUIRED_FILES:
        file_path = PROCESSED_DIR / file_name

        if not file_path.exists():
            missing_files.append(file_name)

    return missing_files


def validate_documents_index():
    file_path = PROCESSED_DIR / "documents_index.csv"
    rows = read_csv_rows(file_path)

    required_columns = [
        "document_id",
        "title",
        "file_name",
        "relative_path",
        "document_type",
        "asset_ids",
        "tags",
        "summary",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in rows[0]
    ]

    return {
        "file": "documents_index.csv",
        "status": "PASS" if rows and not missing_columns else "FAIL",
        "records": len(rows),
        "missing_columns": missing_columns,
    }


def validate_document_chunks():
    data = read_json(PROCESSED_DIR / "document_chunks.json")
    chunks = data.get("chunks", [])

    valid_chunk_count = len([
        chunk for chunk in chunks
        if chunk.get("chunk_id") and chunk.get("chunk_text")
    ])

    return {
        "file": "document_chunks.json",
        "status": "PASS" if valid_chunk_count == len(chunks) and len(chunks) > 0 else "FAIL",
        "total_chunks": len(chunks),
        "valid_chunks": valid_chunk_count,
    }


def validate_asset_metadata():
    data = read_json(PROCESSED_DIR / "asset_metadata.json")
    assets = data.get("assets", [])

    expected_assets = {"P-101", "C-201", "HX-301"}
    found_assets = {asset.get("asset_id") for asset in assets}

    return {
        "file": "asset_metadata.json",
        "status": "PASS" if expected_assets.issubset(found_assets) else "FAIL",
        "total_assets": len(assets),
        "found_assets": sorted(found_assets),
    }


def validate_compliance_matrix():
    data = read_json(PROCESSED_DIR / "compliance_matrix.json")
    gaps = data.get("gaps", [])

    expected_gaps = {"GAP-001", "GAP-002", "GAP-003", "GAP-004", "GAP-005"}
    found_gaps = {gap.get("gap_id") for gap in gaps}

    return {
        "file": "compliance_matrix.json",
        "status": "PASS" if expected_gaps.issubset(found_gaps) else "FAIL",
        "total_gaps": len(gaps),
        "found_gaps": sorted(found_gaps),
    }


def validate_sensor_summary():
    data = read_json(PROCESSED_DIR / "sensor_summary.json")
    asset_level = data.get("asset_level_summary", [])
    sensor_level = data.get("sensor_level_summary", [])

    expected_assets = {"P-101", "C-201", "HX-301"}
    found_assets = {item.get("asset_id") for item in asset_level}

    return {
        "file": "sensor_summary.json",
        "status": "PASS" if expected_assets.issubset(found_assets) and len(sensor_level) > 0 else "FAIL",
        "asset_summary_count": len(asset_level),
        "sensor_summary_count": len(sensor_level),
        "found_assets": sorted(found_assets),
    }


def validate_work_orders():
    data = read_json(PROCESSED_DIR / "work_orders_processed.json")
    work_orders = data.get("work_orders", [])

    return {
        "file": "work_orders_processed.json",
        "status": "PASS" if len(work_orders) >= 6 else "FAIL",
        "total_work_orders": len(work_orders),
    }


def validate_benchmark_questions():
    data = read_json(PROCESSED_DIR / "benchmark_questions.json")
    questions = data.get("questions", [])

    return {
        "file": "benchmark_questions.json",
        "status": "PASS" if len(questions) >= 20 else "FAIL",
        "total_questions": len(questions),
    }


def validate_knowledge_graph():
    data = read_json(PROCESSED_DIR / "knowledge_graph_seed.json")
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    expected_nodes = {"P-101", "C-201", "HX-301"}
    found_nodes = {node.get("id") for node in nodes}

    return {
        "file": "knowledge_graph_seed.json",
        "status": "PASS" if expected_nodes.issubset(found_nodes) and len(edges) > 0 else "FAIL",
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def main():
    print("PlantMind AI - Processed Data Validation")
    print("=" * 50)

    missing_files = validate_required_files()

    if missing_files:
        print("\nMissing processed files:")
        for file_name in missing_files:
            print(f" - {file_name}")
        print("\nProcessed validation failed.")
        return

    print("\nAll required processed files are present.")

    validations = [
        validate_documents_index(),
        validate_document_chunks(),
        validate_asset_metadata(),
        validate_compliance_matrix(),
        validate_sensor_summary(),
        validate_work_orders(),
        validate_benchmark_questions(),
        validate_knowledge_graph(),
    ]

    print("\nValidation results:")

    failed = []

    for result in validations:
        status = result["status"]
        file_name = result["file"]

        print(f"{status}: {file_name}")

        for key, value in result.items():
            if key not in ["status", "file"]:
                print(f"  - {key}: {value}")

        if status != "PASS":
            failed.append(file_name)

    if failed:
        print("\nProcessed data validation failed.")
        print("Fix these files:")
        for file_name in failed:
            print(f" - {file_name}")
    else:
        print("\nDay 3 processed data validation passed.")


if __name__ == "__main__":
    main()