from fastapi import APIRouter, HTTPException, Query

from apps.api.services.data_loader import (
    get_chunks_by_document_id,
    get_document_by_id,
    get_documents,
)


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("")
def list_documents(
    asset_id: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    tag: str | None = Query(default=None)
):
    documents = get_documents()

    if asset_id:
        asset_id = asset_id.upper()
        documents = [
            document for document in documents
            if asset_id in document.get("asset_ids", [])
        ]

    if document_type:
        documents = [
            document for document in documents
            if document_type.lower() in document.get("document_type", "").lower()
        ]

    if tag:
        tag = tag.upper()
        documents = [
            document for document in documents
            if tag in [item.upper() for item in document.get("tags", [])]
        ]

    return {
        "total": len(documents),
        "documents": documents
    }


@router.get("/{document_id}")
def get_document(document_id: str):
    document = get_document_by_id(document_id)

    if not document:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

    return document


@router.get("/{document_id}/chunks")
def get_document_chunks(document_id: str):
    chunks = get_chunks_by_document_id(document_id)

    if not chunks:
        raise HTTPException(status_code=404, detail=f"No chunks found for document: {document_id}")

    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": chunks
    }