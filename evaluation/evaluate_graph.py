from __future__ import annotations

from typing import Any

from common import EVALUATION_DIR, PROJECT_ROOT, load_json, normalize_text, round_metrics, safe_divide


def _collect_lists(data: Any, keys: list[str]) -> list[Any]:
    if not isinstance(data, dict):
        return []
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
    for value in data.values():
        if isinstance(value, dict):
            nested = _collect_lists(value, keys)
            if nested:
                return nested
    return []


def _node_id(node: Any) -> str | None:
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return None
    for key in ("id", "node_id", "key", "asset_id", "document_id", "work_order_id", "case_id", "gap_id"):
        if node.get(key):
            return str(node[key])
    return None


def _edge_endpoint(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return _node_id(value)
    return None


def _edge_pair(edge: Any) -> tuple[str, str] | None:
    if not isinstance(edge, dict):
        return None
    source = _edge_endpoint(
        edge.get("source")
        or edge.get("from")
        or edge.get("source_id")
        or edge.get("start")
    )
    target = _edge_endpoint(
        edge.get("target")
        or edge.get("to")
        or edge.get("target_id")
        or edge.get("end")
    )
    if source and target:
        return source, target
    return None


def evaluate_graph() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    graph_path = PROJECT_ROOT / "data" / "demo" / "knowledge_graph.json"
    truth = load_json(EVALUATION_DIR / "ground_truth_graph.json")
    rows: list[dict[str, Any]] = []

    if not graph_path.exists():
        metrics = {
            "node_coverage": 0.0,
            "edge_coverage": 0.0,
            "graph_link_completeness": 0.0,
            "asset_document_linkage_accuracy": 0.0,
            "broken_link_count": 0,
            "actual_node_count": 0,
            "actual_edge_count": 0,
            "error": "data/demo/knowledge_graph.json not found",
        }
        return metrics, rows

    data = load_json(graph_path)
    nodes = _collect_lists(data, ["nodes", "vertices", "entities"])
    edges = _collect_lists(data, ["edges", "links", "relationships"])

    actual_nodes = {normalize_text(node_id) for node in nodes if (node_id := _node_id(node))}
    actual_edges = {
        (normalize_text(pair[0]), normalize_text(pair[1]))
        for edge in edges
        if (pair := _edge_pair(edge))
    }
    undirected_edges = actual_edges | {(target, source) for source, target in actual_edges}

    expected_nodes = {normalize_text(item) for item in truth.get("expected_nodes", [])}
    expected_edges = {
        (normalize_text(item[0]), normalize_text(item[1]))
        for item in truth.get("expected_edges", [])
        if isinstance(item, list) and len(item) >= 2
    }

    node_coverage = safe_divide(len(expected_nodes & actual_nodes), len(expected_nodes))
    edge_coverage = safe_divide(len(expected_edges & undirected_edges), len(expected_edges))
    asset_document_edges = {
        edge
        for edge in expected_edges
        if (
            edge[0] in {"p-101", "c-201", "hx-301"}
            and any(token in edge[1] for token in ("sop", "ir-", "inc-", "comp-"))
        )
        or (
            edge[1] in {"p-101", "c-201", "hx-301"}
            and any(token in edge[0] for token in ("sop", "ir-", "inc-", "comp-"))
        )
    }
    asset_document_linkage_accuracy = safe_divide(
        len(asset_document_edges & undirected_edges),
        len(asset_document_edges),
    )
    broken_edges = [
        (source, target)
        for source, target in actual_edges
        if source not in actual_nodes or target not in actual_nodes
    ]

    for node in sorted(expected_nodes):
        rows.append(
            {
                "module": "knowledge_graph",
                "item_id": node,
                "category": "node",
                "metric": "coverage",
                "expected": "present",
                "actual": "present" if node in actual_nodes else "missing",
                "pass": node in actual_nodes,
                "notes": "",
            }
        )
    for source, target in sorted(expected_edges):
        present = (source, target) in undirected_edges
        rows.append(
            {
                "module": "knowledge_graph",
                "item_id": f"{source}->{target}",
                "category": "edge",
                "metric": "coverage",
                "expected": "present",
                "actual": "present" if present else "missing",
                "pass": present,
                "notes": "",
            }
        )

    metrics = {
        "node_coverage": node_coverage,
        "edge_coverage": edge_coverage,
        "graph_link_completeness": edge_coverage,
        "asset_document_linkage_accuracy": asset_document_linkage_accuracy,
        "broken_link_count": len(broken_edges),
        "actual_node_count": len(actual_nodes),
        "actual_edge_count": len(actual_edges),
    }
    return round_metrics(metrics), rows


if __name__ == "__main__":
    metrics, _ = evaluate_graph()
    print(metrics)
