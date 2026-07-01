from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import get_knowledge_graph


router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


@router.get("")
def get_full_knowledge_graph():
    return get_knowledge_graph()


@router.get("/nodes")
def list_nodes(node_type: str | None = Query(default=None)):
    graph = get_knowledge_graph()
    nodes = graph.get("nodes", [])

    if node_type:
        nodes = [
            node for node in nodes
            if node.get("type", "").lower() == node_type.lower()
        ]

    return {
        "total": len(nodes),
        "nodes": nodes
    }


@router.get("/edges")
def list_edges(relationship: str | None = Query(default=None)):
    graph = get_knowledge_graph()
    edges = graph.get("edges", [])

    if relationship:
        edges = [
            edge for edge in edges
            if edge.get("relationship", "").lower() == relationship.lower()
        ]

    return {
        "total": len(edges),
        "edges": edges
    }


@router.get("/assets/{asset_id}/subgraph")
def get_asset_subgraph(asset_id: str):
    asset_id = asset_id.upper()
    graph = get_knowledge_graph()

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    connected_edges = [
        edge for edge in edges
        if edge.get("source") == asset_id or edge.get("target") == asset_id
    ]

    if not connected_edges:
        raise HTTPException(status_code=404, detail=f"No graph edges found for asset: {asset_id}")

    connected_node_ids = {asset_id}

    for edge in connected_edges:
        connected_node_ids.add(edge.get("source"))
        connected_node_ids.add(edge.get("target"))

    connected_nodes = [
        node for node in nodes
        if node.get("id") in connected_node_ids
    ]

    return {
        "asset_id": asset_id,
        "node_count": len(connected_nodes),
        "edge_count": len(connected_edges),
        "nodes": connected_nodes,
        "edges": connected_edges
    }