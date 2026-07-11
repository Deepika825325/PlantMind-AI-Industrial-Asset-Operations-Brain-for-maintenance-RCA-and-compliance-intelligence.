from __future__ import annotations

import csv
import hashlib
import json
import mimetypes
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.api.ingestion.schemas import (
    DocumentIngestionRequest,
    DocumentIngestionResult,
    IngestionChunk,
    IngestionChunkManifest,
    IngestionManifest,
    IngestionValidationError,
)


SUPPORTED_TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".csv",
    ".json",
    ".log",
}

STORED_ONLY_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".xlsx",
    ".xls",
    ".docx",
}


@dataclass(frozen=True)
class IngestionConfig:
    raw_dir: Path = Path("data/ingestion/raw")
    normalized_dir: Path = Path("data/ingestion/normalized")
    manifest_dir: Path = Path("data/ingestion/manifests")
    chunks_dir: Path | None = None
    max_preview_chars: int = 500
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 150
    max_file_size_bytes: int = 25 * 1024 * 1024


class IngestionValidationException(ValueError):
    def __init__(
        self,
        errors: list[IngestionValidationError],
    ) -> None:
        self.errors = errors

        super().__init__(
            "; ".join(
                error.message
                for error in errors
            )
        )


class DocumentIngestionService:
    def __init__(
        self,
        config: IngestionConfig | None = None,
    ) -> None:
        self.config = config or IngestionConfig()
        self.chunks_dir = (
            self.config.chunks_dir
            or self.config.raw_dir.parent / "chunks"
        )

        self.config.raw_dir.mkdir(parents=True, exist_ok=True)
        self.config.normalized_dir.mkdir(parents=True, exist_ok=True)
        self.config.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

    def ingest_document(
        self,
        request: DocumentIngestionRequest,
    ) -> DocumentIngestionResult:
        source_path = Path(request.source_path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Document source file not found: {source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                f"Document source path is not a file: {source_path}"
            )

        extension = source_path.suffix.lower()
        file_size_bytes = source_path.stat().st_size
        detected_mime_type = self._detect_mime_type(source_path)

        validation_errors = self._validate_file(
            source_path=source_path,
            extension=extension,
            file_size_bytes=file_size_bytes,
            detected_mime_type=detected_mime_type,
        )

        if validation_errors:
            raise IngestionValidationException(
                validation_errors
            )

        checksum = self._sha256(source_path)
        document_id = self._document_id(checksum)
        safe_filename = self._safe_filename(source_path.name)

        stored_raw_path = (
            self.config.raw_dir
            / f"{document_id}__{safe_filename}"
        )

        manifest_path = (
            self.config.manifest_dir
            / f"{document_id}.json"
        )

        normalized_text_path = (
            self.config.normalized_dir
            / f"{document_id}.txt"
        )

        chunk_manifest_path = (
            self.chunks_dir
            / f"{document_id}.json"
        )

        duplicate_of_document_id = (
            document_id
            if manifest_path.exists()
            else None
        )

        status = "duplicate" if duplicate_of_document_id else "ingested"

        revision_group_id = self._revision_group_id(
            source_path.name
        )

        revision_number = self._next_revision_number(
            revision_group_id=revision_group_id,
            document_id=document_id,
            is_duplicate=bool(duplicate_of_document_id),
        )

        shutil.copy2(
            source_path,
            stored_raw_path,
        )

        text_extract_status = "unsupported"
        text_preview: str | None = None
        normalized_path_value: str | None = None
        chunk_manifest_value: str | None = None
        chunk_count = 0

        if extension in SUPPORTED_TEXT_EXTENSIONS:
            extracted_text = self._extract_text(
                source_path=source_path,
                extension=extension,
            )
            normalized_text_path.write_text(
                extracted_text,
                encoding="utf-8",
            )
            normalized_path_value = str(normalized_text_path)
            text_extract_status = "extracted"
            text_preview = extracted_text[
                : self.config.max_preview_chars
            ]

            chunks = self._chunk_text(
                document_id=document_id,
                text=extracted_text,
                asset_ids=request.asset_ids,
                document_type=request.document_type,
                source_filename=source_path.name,
            )

            chunk_count = len(chunks)

            if chunks:
                self._write_chunk_manifest(
                    chunk_manifest_path,
                    IngestionChunkManifest(
                        document_id=document_id,
                        total_chunks=chunk_count,
                        chunks=chunks,
                    ),
                )
                chunk_manifest_value = str(chunk_manifest_path)

        elif extension in STORED_ONLY_EXTENSIONS:
            text_extract_status = "stored_only"
        else:
            text_extract_status = "unsupported"

        processing_status = (
            "ready"
            if text_extract_status == "extracted"
            else "stored_only"
            if text_extract_status == "stored_only"
            else "failed"
        )

        lifecycle_status = (
            "ready"
            if processing_status in {"ready", "stored_only"}
            else "failed"
        )

        manifest = IngestionManifest(
            document_id=document_id,
            source_filename=source_path.name,
            source_path=str(source_path),
            stored_raw_path=str(stored_raw_path),
            object_storage_path=str(stored_raw_path),
            storage_backend="local_object_store",
            normalized_text_path=normalized_path_value,
            chunk_manifest_path=chunk_manifest_value,
            checksum_sha256=checksum,
            detected_mime_type=detected_mime_type,
            file_size_bytes=file_size_bytes,
            max_file_size_bytes=self.config.max_file_size_bytes,
            extension=extension,
            document_type=request.document_type,
            asset_ids=request.asset_ids,
            source_system=request.source_system,
            uploaded_by=request.uploaded_by,
            lifecycle_status=lifecycle_status,
            upload_status="uploaded",
            processing_status=processing_status,
            text_extract_status=text_extract_status,
            text_preview=text_preview,
            chunk_count=chunk_count,
            revision_group_id=revision_group_id,
            revision_number=revision_number,
            is_latest_revision=True,
            is_duplicate=bool(duplicate_of_document_id),
            duplicate_of_document_id=duplicate_of_document_id,
            validation_errors=[],
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        self._write_manifest(
            manifest_path,
            manifest,
        )

        return DocumentIngestionResult(
            document_id=document_id,
            status=status,
            source_filename=source_path.name,
            source_path=str(source_path),
            stored_raw_path=str(stored_raw_path),
            object_storage_path=str(stored_raw_path),
            storage_backend="local_object_store",
            normalized_text_path=normalized_path_value,
            chunk_manifest_path=chunk_manifest_value,
            manifest_path=str(manifest_path),
            checksum_sha256=checksum,
            detected_mime_type=detected_mime_type,
            file_size_bytes=file_size_bytes,
            max_file_size_bytes=self.config.max_file_size_bytes,
            extension=extension,
            document_type=request.document_type,
            asset_ids=request.asset_ids,
            source_system=request.source_system,
            uploaded_by=request.uploaded_by,
            lifecycle_status=lifecycle_status,
            upload_status="uploaded",
            processing_status=processing_status,
            text_extract_status=text_extract_status,
            text_preview=text_preview,
            chunk_count=chunk_count,
            revision_group_id=revision_group_id,
            revision_number=revision_number,
            is_latest_revision=True,
            is_duplicate=bool(duplicate_of_document_id),
            duplicate_of_document_id=duplicate_of_document_id,
            validation_errors=[],
            message=self._message(
                status=status,
                text_extract_status=text_extract_status,
            ),
        )

    def list_manifests(
        self,
    ) -> list[IngestionManifest]:
        manifests: list[IngestionManifest] = []

        for manifest_path in sorted(
            self.config.manifest_dir.glob("*.json")
        ):
            manifests.append(
                self.load_manifest(
                    manifest_path.stem
                )
            )

        return manifests

    def load_manifest(
        self,
        document_id: str,
    ) -> IngestionManifest:
        manifest_path = (
            self.config.manifest_dir
            / f"{document_id}.json"
        )

        if not manifest_path.exists():
            raise FileNotFoundError(
                f"Ingestion manifest not found: {document_id}"
            )

        return IngestionManifest.model_validate_json(
            manifest_path.read_text(
                encoding="utf-8",
            )
        )

    def load_chunk_manifest(
        self,
        document_id: str,
    ) -> IngestionChunkManifest:
        chunk_manifest_path = (
            self.chunks_dir
            / f"{document_id}.json"
        )

        if not chunk_manifest_path.exists():
            raise FileNotFoundError(
                f"Ingestion chunk manifest not found: {document_id}"
            )

        return IngestionChunkManifest.model_validate_json(
            chunk_manifest_path.read_text(
                encoding="utf-8",
            )
        )

    def _detect_mime_type(
        self,
        source_path: Path,
    ) -> str:
        detected, _ = mimetypes.guess_type(
            source_path.name
        )

        return detected or "application/octet-stream"

    def _validate_file(
        self,
        source_path: Path,
        extension: str,
        file_size_bytes: int,
        detected_mime_type: str,
    ) -> list[IngestionValidationError]:
        errors: list[IngestionValidationError] = []

        supported_extensions = (
            SUPPORTED_TEXT_EXTENSIONS
            | STORED_ONLY_EXTENSIONS
        )

        if extension not in supported_extensions:
            errors.append(
                IngestionValidationError(
                    code="unsupported_file_extension",
                    field="source_path",
                    message=(
                        f"Unsupported file extension '{extension}' "
                        f"for document {source_path.name}."
                    ),
                )
            )

        if file_size_bytes <= 0:
            errors.append(
                IngestionValidationError(
                    code="empty_file",
                    field="source_path",
                    message="Document file is empty.",
                )
            )

        if file_size_bytes > self.config.max_file_size_bytes:
            errors.append(
                IngestionValidationError(
                    code="file_too_large",
                    field="source_path",
                    message=(
                        "Document exceeds maximum allowed size "
                        f"of {self.config.max_file_size_bytes} bytes."
                    ),
                )
            )

        if not detected_mime_type:
            errors.append(
                IngestionValidationError(
                    code="mime_type_not_detected",
                    field="source_path",
                    message="Could not detect MIME type.",
                )
            )

        return errors

    def _revision_group_id(
        self,
        filename: str,
    ) -> str:
        safe = self._safe_filename(
            Path(filename).stem
        ).upper()

        return f"DOC-REV-{safe}"

    def _next_revision_number(
        self,
        revision_group_id: str,
        document_id: str,
        is_duplicate: bool,
    ) -> int:
        existing = [
            manifest
            for manifest in self.list_manifests()
            if manifest.revision_group_id == revision_group_id
        ]

        if is_duplicate:
            for manifest in existing:
                if manifest.document_id == document_id:
                    return manifest.revision_number

        if not existing:
            return 1

        return (
            max(
                manifest.revision_number
                for manifest in existing
            )
            + 1
        )

    def _extract_text(
        self,
        source_path: Path,
        extension: str,
    ) -> str:
        if extension in {
            ".txt",
            ".md",
            ".markdown",
            ".log",
        }:
            return source_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

        if extension == ".json":
            data: Any = json.loads(
                source_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            )
            return json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )

        if extension == ".csv":
            rows: list[str] = []
            with source_path.open(
                "r",
                encoding="utf-8",
                errors="replace",
                newline="",
            ) as file:
                reader = csv.reader(file)
                for row in reader:
                    rows.append(
                        " | ".join(row)
                    )
            return "\n".join(rows)

        return ""

    def _chunk_text(
        self,
        document_id: str,
        text: str,
        asset_ids: list[str],
        document_type: str,
        source_filename: str,
    ) -> list[IngestionChunk]:
        if not text.strip():
            return []

        chunks: list[IngestionChunk] = []
        start = 0
        text_length = len(text)
        chunk_size = max(1, self.config.chunk_size_chars)
        overlap = max(0, self.config.chunk_overlap_chars)

        while start < text_length:
            end = min(
                start + chunk_size,
                text_length,
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_index = len(chunks)
                chunks.append(
                    IngestionChunk(
                        document_id=document_id,
                        chunk_id=(
                            f"{document_id}-CHUNK-"
                            f"{chunk_index + 1:04d}"
                        ),
                        chunk_index=chunk_index,
                        text=chunk_text,
                        character_start=start,
                        character_end=end,
                        token_estimate=max(
                            1,
                            len(chunk_text) // 4,
                        ),
                        asset_ids=asset_ids,
                        document_type=document_type,
                        source_filename=source_filename,
                    )
                )

            if end >= text_length:
                break

            next_start = end - overlap
            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    def _sha256(
        self,
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    def _document_id(
        self,
        checksum: str,
    ) -> str:
        return f"DOC-ING-{checksum[:16].upper()}"

    def _safe_filename(
        self,
        filename: str,
    ) -> str:
        cleaned = re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            filename,
        )
        return cleaned.strip("_") or "document"

    def _write_manifest(
        self,
        manifest_path: Path,
        manifest: IngestionManifest,
    ) -> None:
        manifest_path.write_text(
            manifest.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def _write_chunk_manifest(
        self,
        chunk_manifest_path: Path,
        chunk_manifest: IngestionChunkManifest,
    ) -> None:
        chunk_manifest_path.write_text(
            chunk_manifest.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def _message(
        self,
        status: str,
        text_extract_status: str,
    ) -> str:
        if status == "duplicate":
            return "Document already existed; manifest was refreshed."

        if text_extract_status == "extracted":
            return "Document ingested, text extracted, and chunks prepared."

        if text_extract_status == "stored_only":
            return "Document stored; text extraction will be handled by a specialized parser later."

        return "Document stored but extension is not supported for text extraction yet."
