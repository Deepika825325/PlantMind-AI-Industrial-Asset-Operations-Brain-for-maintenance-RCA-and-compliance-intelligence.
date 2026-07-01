from pathlib import Path
import csv
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

REQUIRED_FILES = [
    "documents/manuals_sops/SOP-P101-001_Pump_Lubrication_and_Bearing_Check.md",
    "documents/manuals_sops/SOP-P101-002_Pump_Vibration_Inspection.md",
    "documents/manuals_sops/SOP-C201-001_Compressor_Safe_Shutdown.md",
    "documents/manuals_sops/SOP-HX301-001_Heat_Exchanger_Cleaning_and_Fouling_Check.md",
    "documents/manuals_sops/SOP-GEN-001_Work_Permit_and_LOTO.md",

    "documents/inspection_reports/IR-P101-001_Pump_Vibration_Inspection.md",
    "documents/inspection_reports/IR-P101-002_Pump_Bearing_Temperature_Check.md",
    "documents/inspection_reports/IR-C201-001_Compressor_Monthly_Inspection.md",
    "documents/inspection_reports/IR-HX301-001_Heat_Exchanger_Performance_Inspection.md",
    "documents/inspection_reports/IR-GEN-001_Safety_Evidence_Audit.md",

    "documents/incident_reports/INC-P101-001_High_Vibration_Event.md",
    "documents/incident_reports/INC-HX301-001_Low_Heat_Transfer_Efficiency.md",

    "documents/compliance/COMP-001_Compliance_Checklist.md",

    "documents/drawings/PID-001_Demo_Process_Line.png",
    "documents/drawings/PID-001_Demo_Process_Line.metadata.json",

    "structured/work_orders.csv",
    "structured/sensor_readings.csv",
    "structured/benchmark_questions.csv",
    "structured/ground_truth_compliance_gaps.csv",

    "public_sources/README_sources.md",
]


def validate_required_files():
    missing_files = []

    for relative_path in REQUIRED_FILES:
        file_path = RAW_DIR / relative_path

        if not file_path.exists():
            missing_files.append(relative_path)

    return missing_files


def validate_csv_file(relative_path):
    file_path = RAW_DIR / relative_path

    if not file_path.exists():
        return False, f"Missing CSV file: {relative_path}"

    try:
        with file_path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        if not rows:
            return False, f"CSV has no rows: {relative_path}"

        return True, f"CSV valid: {relative_path} | rows: {len(rows)}"

    except Exception as error:
        return False, f"CSV error in {relative_path}: {str(error)}"


def validate_json_file(relative_path):
    file_path = RAW_DIR / relative_path

    if not file_path.exists():
        return False, f"Missing JSON file: {relative_path}"

    try:
        with file_path.open("r", encoding="utf-8") as file:
            json.load(file)

        return True, f"JSON valid: {relative_path}"

    except Exception as error:
        return False, f"JSON error in {relative_path}: {str(error)}"


def main():
    print("PlantMind AI - Raw Data Validation")
    print("=" * 50)

    missing_files = validate_required_files()

    if missing_files:
        print("\nMissing files:")
        for file in missing_files:
            print(f" - {file}")
    else:
        print("\nAll required raw files are present.")

    print("\nValidating CSV files:")

    csv_files = [
        "structured/work_orders.csv",
        "structured/sensor_readings.csv",
        "structured/benchmark_questions.csv",
        "structured/ground_truth_compliance_gaps.csv",
    ]

    for csv_file in csv_files:
        is_valid, message = validate_csv_file(csv_file)
        print(("PASS: " if is_valid else "FAIL: ") + message)

    print("\nValidating JSON files:")

    json_files = [
        "documents/drawings/PID-001_Demo_Process_Line.metadata.json",
    ]

    for json_file in json_files:
        is_valid, message = validate_json_file(json_file)
        print(("PASS: " if is_valid else "FAIL: ") + message)

    if not missing_files:
        print("\nDay 2 raw dataset validation passed.")
    else:
        print("\nDay 2 raw dataset validation failed. Fix missing files first.")


if __name__ == "__main__":
    main()