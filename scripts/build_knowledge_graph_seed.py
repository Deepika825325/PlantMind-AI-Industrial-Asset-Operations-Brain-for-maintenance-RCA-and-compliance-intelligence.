from pathlib import Path
import csv
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DOCUMENTS_INDEX_FILE = PROCESSED_DIR / "documents_index.csv"
ASSET_METADATA_FILE = PROCESSED_DIR / "asset_metadata.json"
SENSOR_SUMMARY_FILE = PROCESSED_DIR / "sensor_summary.json"
COMPLIANCE_MATRIX_FILE = PROCESSED_DIR / "compliance_matrix.json"
WORK_ORDERS_FILE = PROCESSED_DIR / "work_orders_processed.json"
PID_METADATA_FILE = RAW_DIR / "documents" / "drawings" / "PID-001_Demo_Process_Line.metadata.json"

OUTPUT_FILE = PROCESSED_DIR / "knowledge_graph_seed.json"


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


def add_node(nodes, node_id, label, node_type, properties=None):
    if node_id in nodes:
        return

    nodes[node_id] = {
        "id": node_id,
        "label": label,
        "type": node_type,
        "properties": properties or {}
    }


def add_edge(edges, source, target, relationship, properties=None):
    edge_id = f"{source}__{relationship}__{target}"

    if edge_id in edges:
        return

    edges[edge_id] = {
        "id": edge_id,
        "source": source,
        "target": target,
        "relationship": relationship,
        "properties": properties or {}
    }


def build_asset_nodes(nodes, asset_metadata):
    for asset in asset_metadata.get("assets", []):
        add_node(
            nodes=nodes,
            node_id=asset["asset_id"],
            label=f'{asset["asset_id"]} - {asset["asset_name"]}',
            node_type="Asset",
            properties={
                "asset_name": asset["asset_name"],
                "asset_type": asset["asset_type"],
                "risk_score": asset["risk_score"],
                "risk_level": asset["risk_level"],
                "sensor_status": asset["sensor_status"],
                "compliance_status": asset["compliance_status"],
                "total_compliance_gaps": asset["total_compliance_gaps"],
                "critical_story": asset["critical_story"]
            }
        )


def build_document_nodes_and_edges(nodes, edges, documents):
    for document in documents:
        document_id = document["document_id"]

        add_node(
            nodes=nodes,
            node_id=document_id,
            label=document.get("title") or document_id,
            node_type="Document",
            properties={
                "document_type": document.get("document_type", ""),
                "source_group": document.get("source_group", ""),
                "relative_path": document.get("relative_path", ""),
                "summary": document.get("summary", "")
            }
        )

        asset_ids = document.get("asset_ids", "")

        if asset_ids:
            for asset_id in asset_ids.split(";"):
                asset_id = asset_id.strip()

                if asset_id:
                    add_edge(
                        edges=edges,
                        source=asset_id,
                        target=document_id,
                        relationship="MENTIONED_IN",
                        properties={
                            "source": "documents_index.csv"
                        }
                    )


def build_sensor_nodes_and_edges(nodes, edges, sensor_summary):
    for sensor in sensor_summary.get("sensor_level_summary", []):
        asset_id = sensor["asset_id"]
        sensor_name = sensor["sensor_name"]
        sensor_id = f"{asset_id}_{sensor_name}"

        add_node(
            nodes=nodes,
            node_id=sensor_id,
            label=f"{asset_id} {sensor_name}",
            node_type="SensorSignal",
            properties={
                "asset_id": asset_id,
                "sensor_name": sensor_name,
                "unit": sensor["unit"],
                "latest_value": sensor["latest_value"],
                "latest_status": sensor["latest_status"],
                "trend_direction": sensor["trend_direction"],
                "source_dataset": sensor["source_dataset"]
            }
        )

        add_edge(
            edges=edges,
            source=asset_id,
            target=sensor_id,
            relationship="HAS_SENSOR_SIGNAL",
            properties={
                "latest_status": sensor["latest_status"],
                "trend_direction": sensor["trend_direction"]
            }
        )


def build_compliance_nodes_and_edges(nodes, edges, compliance_matrix):
    for gap in compliance_matrix.get("gaps", []):
        gap_id = gap["gap_id"]
        asset_id = gap["asset_id"]

        add_node(
            nodes=nodes,
            node_id=gap_id,
            label=f'{gap_id} - {gap["requirement"]}',
            node_type="ComplianceGap",
            properties={
                "asset_id": asset_id,
                "requirement": gap["requirement"],
                "expected_evidence": gap["expected_evidence"],
                "current_status": gap["current_status"],
                "gap_severity": gap["gap_severity"],
                "recommended_action": gap["recommended_action"],
                "source_document": gap["source_document"]
            }
        )

        add_edge(
            edges=edges,
            source=asset_id,
            target=gap_id,
            relationship="HAS_COMPLIANCE_GAP",
            properties={
                "severity": gap["gap_severity"],
                "status": gap["current_status"]
            }
        )

        source_document = gap.get("source_document")

        if source_document:
            add_edge(
                edges=edges,
                source=gap_id,
                target=source_document,
                relationship="SUPPORTED_BY",
                properties={
                    "source": "compliance_matrix.json"
                }
            )


def build_work_order_nodes_and_edges(nodes, edges, work_orders_processed):
    for work_order in work_orders_processed.get("work_orders", []):
        work_order_id = work_order["work_order_id"]
        asset_id = work_order["asset_id"]

        add_node(
            nodes=nodes,
            node_id=work_order_id,
            label=f'{work_order_id} - {work_order["work_order_type"]}',
            node_type="WorkOrder",
            properties={
                "asset_id": asset_id,
                "asset_name": work_order["asset_name"],
                "work_order_type": work_order["work_order_type"],
                "priority": work_order["priority"],
                "status": work_order["status"],
                "created_date": work_order["created_date"],
                "due_date": work_order["due_date"],
                "description": work_order["description"],
                "compliance_related": work_order["compliance_related"]
            }
        )

        add_edge(
            edges=edges,
            source=asset_id,
            target=work_order_id,
            relationship="HAS_WORK_ORDER",
            properties={
                "priority": work_order["priority"],
                "status": work_order["status"]
            }
        )

        linked_document = work_order.get("linked_document")

        if linked_document:
            add_edge(
                edges=edges,
                source=work_order_id,
                target=linked_document,
                relationship="LINKED_TO_DOCUMENT",
                properties={
                    "source": "work_orders_processed.json"
                }
            )


def build_pid_nodes_and_edges(nodes, edges, pid_metadata):
    for graph_node in pid_metadata.get("graph_nodes", []):
        add_node(
            nodes=nodes,
            node_id=graph_node["id"],
            label=graph_node["label"],
            node_type=graph_node["type"],
            properties={
                "source": "PID-001 metadata"
            }
        )

    for graph_edge in pid_metadata.get("graph_edges", []):
        source = graph_edge["source"]
        target = graph_edge["target"]

        if source not in nodes:
            add_node(
                nodes=nodes,
                node_id=source,
                label=source,
                node_type="ProcessNode",
                properties={
                    "source": "PID-001 metadata"
                }
            )

        if target not in nodes:
            add_node(
                nodes=nodes,
                node_id=target,
                label=target,
                node_type="ProcessNode",
                properties={
                    "source": "PID-001 metadata"
                }
            )

        add_edge(
            edges=edges,
            source=source,
            target=target,
            relationship=graph_edge["relationship"],
            properties={
                "source": "PID-001 metadata"
            }
        )


def build_risk_edges(edges, asset_metadata):
    for asset in asset_metadata.get("assets", []):
        asset_id = asset["asset_id"]

        if asset["risk_level"] == "High":
            add_edge(
                edges=edges,
                source=asset_id,
                target="High_Risk_Assets",
                relationship="CLASSIFIED_AS",
                properties={
                    "risk_score": asset["risk_score"]
                }
            )

        elif asset["risk_level"] == "Medium":
            add_edge(
                edges=edges,
                source=asset_id,
                target="Medium_Risk_Assets",
                relationship="CLASSIFIED_AS",
                properties={
                    "risk_score": asset["risk_score"]
                }
            )


def main():
    print("PlantMind AI - Knowledge Graph Seed Builder")
    print("=" * 50)

    documents = read_csv_rows(DOCUMENTS_INDEX_FILE)
    asset_metadata = read_json(ASSET_METADATA_FILE)
    sensor_summary = read_json(SENSOR_SUMMARY_FILE)
    compliance_matrix = read_json(COMPLIANCE_MATRIX_FILE)
    work_orders_processed = read_json(WORK_ORDERS_FILE)
    pid_metadata = read_json(PID_METADATA_FILE)

    nodes = {}
    edges = {}

    add_node(
        nodes=nodes,
        node_id="PlantMind_AI",
        label="PlantMind AI",
        node_type="Project",
        properties={
            "description": "Industrial Asset and Operations Brain for maintenance, RCA, compliance, and knowledge intelligence."
        }
    )

    add_node(
        nodes=nodes,
        node_id="High_Risk_Assets",
        label="High Risk Assets",
        node_type="RiskClass",
        properties={}
    )

    add_node(
        nodes=nodes,
        node_id="Medium_Risk_Assets",
        label="Medium Risk Assets",
        node_type="RiskClass",
        properties={}
    )

    build_asset_nodes(nodes, asset_metadata)
    build_document_nodes_and_edges(nodes, edges, documents)
    build_sensor_nodes_and_edges(nodes, edges, sensor_summary)
    build_compliance_nodes_and_edges(nodes, edges, compliance_matrix)
    build_work_order_nodes_and_edges(nodes, edges, work_orders_processed)
    build_pid_nodes_and_edges(nodes, edges, pid_metadata)
    build_risk_edges(edges, asset_metadata)

    for asset in asset_metadata.get("assets", []):
        add_edge(
            edges=edges,
            source="PlantMind_AI",
            target=asset["asset_id"],
            relationship="TRACKS_ASSET",
            properties={}
        )

    output = {
        "project": "PlantMind AI",
        "artifact": "knowledge_graph_seed",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": list(edges.values())
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"Nodes created: {len(nodes)}")
    print(f"Edges created: {len(edges)}")
    print(f"Output created: {OUTPUT_FILE}")
    print("\nKnowledge graph seed completed.")


if __name__ == "__main__":
    main()