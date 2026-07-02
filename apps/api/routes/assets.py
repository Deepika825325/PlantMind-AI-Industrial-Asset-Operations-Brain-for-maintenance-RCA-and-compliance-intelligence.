from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import (
    get_asset_by_id,
    get_assets,
    get_compliance_matrix,
    get_documents,
    get_health_scores,
    get_knowledge_graph,
    get_maintenance_events,
    get_rag_seed_questions,
)


router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("")
def list_assets(
    risk_level: str | None = Query(default=None),
    asset_type: str | None = Query(default=None)
):
    assets = get_assets()

    if risk_level:
        assets = [
            asset for asset in assets
            if asset.get("risk_level", "").lower() == risk_level.lower()
        ]

    if asset_type:
        assets = [
            asset for asset in assets
            if asset.get("asset_type", "").lower() == asset_type.lower()
        ]

    return {
        "total": len(assets),
        "assets": assets
    }


@router.get("/health-scores")
def list_health_scores():
    health_scores = get_health_scores()

    return {
        "total": len(health_scores),
        "health_scores": health_scores
    }


@router.get("/{asset_id}")
def get_asset(asset_id: str):
    asset = get_asset_by_id(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")

    return asset


@router.get("/{asset_id}/health")
def get_asset_health(asset_id: str):
    asset_id = asset_id.upper()
    health_scores = get_health_scores()

    for health in health_scores:
        if health.get("asset_id") == asset_id:
            return health

    raise HTTPException(status_code=404, detail=f"Health score not found for asset: {asset_id}")


@router.get("/{asset_id}/evidence")
def get_asset_evidence(asset_id: str):
    asset_id = asset_id.upper()

    asset = get_asset_by_id(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")

    health = None

    for item in get_health_scores():
        if item.get("asset_id") == asset_id:
            health = item
            break

    compliance_data = get_compliance_matrix()

    asset_compliance_summary = None

    for summary in compliance_data.get("asset_compliance_summary", []):
        if summary.get("asset_id") == asset_id:
            asset_compliance_summary = summary
            break

    compliance_gaps = [
        gap for gap in compliance_data.get("gaps", [])
        if gap.get("asset_id") == asset_id
    ]

    work_orders = [
        event for event in get_maintenance_events()
        if event.get("asset_id") == asset_id
    ]

    documents = [
        document for document in get_documents()
        if asset_id in document.get("asset_ids", [])
    ]

    graph = get_knowledge_graph()
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])

    connected_edges = [
        edge for edge in graph_edges
        if edge.get("source") == asset_id or edge.get("target") == asset_id
    ]

    connected_node_ids = {asset_id}

    for edge in connected_edges:
        connected_node_ids.add(edge.get("source"))
        connected_node_ids.add(edge.get("target"))

    connected_nodes = [
        node for node in graph_nodes
        if node.get("id") in connected_node_ids
    ]

    suggested_questions = []

    for question in get_rag_seed_questions():
        expected_assets = question.get("expected_assets", [])

        if asset_id in expected_assets:
            suggested_questions.append(question)

    return {
        "asset_id": asset_id,
        "asset": asset,
        "health": health,
        "compliance": {
            "summary": asset_compliance_summary,
            "gaps": compliance_gaps
        },
        "work_orders": work_orders,
        "documents": documents,
        "graph_subgraph": {
            "node_count": len(connected_nodes),
            "edge_count": len(connected_edges),
            "nodes": connected_nodes,
            "edges": connected_edges
        },
        "suggested_questions": suggested_questions
    }