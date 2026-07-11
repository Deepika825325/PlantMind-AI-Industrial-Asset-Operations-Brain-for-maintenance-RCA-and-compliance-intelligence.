from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.auth.dependencies import require_permission
from apps.api.failure_classification.schemas import (
    FailureClassificationHistoryResponse,
    FailureClassificationModelCard,
    FailureClassificationRequest,
    FailureClassificationResponse,
)
from apps.api.failure_classification.service import FailureModeClassifier


router = APIRouter(
    prefix="/failure-classification",
    tags=["failure-classification"],
)

failure_classifier = FailureModeClassifier()


@router.get(
    "/model",
    response_model=FailureClassificationModelCard,
)
def get_failure_classification_model(
    user=Depends(require_permission("document.read")),
) -> FailureClassificationModelCard:
    return failure_classifier.model_card()


@router.post(
    "/classify",
    response_model=FailureClassificationResponse,
)
def classify_failure_mode(
    request: FailureClassificationRequest,
    user=Depends(require_permission("evidence.write")),
) -> FailureClassificationResponse:
    return failure_classifier.classify(
        request
    )


@router.get(
    "/assets/{asset_id}/history",
    response_model=FailureClassificationHistoryResponse,
)
def get_failure_classification_history(
    asset_id: str,
    user=Depends(require_permission("document.read")),
) -> FailureClassificationHistoryResponse:
    return failure_classifier.history(
        asset_id
    )