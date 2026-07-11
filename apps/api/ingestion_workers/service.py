from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from apps.api.ingestion.service import DocumentIngestionService
from apps.api.ingestion_workers.schemas import (
    ExtractedHeading,
    ExtractedTable,
    ExtractionError,
    ExtractionWorkerJob,
    PageAwareChunk,
    ParserMetadata,
)


PARSER_NAME = "plantmind_page_aware_extraction_worker"
PARSER_VERSION = "1.0.0"

ASSET_TAG_PATTERN = re.compile(
    r"\b(?:P-\d{3}|C-\d{3}|HX-\d{3})\b"
)


@dataclass(frozen=True)
class ExtractionWorkerConfig:
    jobs_dir: Path = Path("data/ingestion/worker_jobs")
    extracted_dir: Path = Path("data/ingestion/extracted")
    failure_log_path: Path = Path("data/ingestion/worker_failures.jsonl")
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 150


class DocumentExtractionWorkerService:
    def __init__(
        self,
        ingestion_service: DocumentIngestionService,
        config: ExtractionWorkerConfig | None = None,
    ) -> None:
        self.ingestion_service = ingestion_service
        self.config = config or ExtractionWorkerConfig()

        self.config.jobs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config.extracted_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config.failure_log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def run_extraction_job(
        self,
        document_id: str,
    ) -> ExtractionWorkerJob:
        job = self._new_job(
            document_id=document_id,
        )

        return self._execute_job(
            job,
        )

    def retry_job(
        self,
        job_id: str,
    ) -> ExtractionWorkerJob:
        job_path = self.config.jobs_dir / f"{job_id}.json"

        if not job_path.exists():
            raise FileNotFoundError(
                f"Extraction worker job not found: {job_id}"
            )

        existing_job = ExtractionWorkerJob.model_validate_json(
            job_path.read_text(
                encoding="utf-8",
            )
        )

        retry_job = existing_job.model_copy(
            update={
                "status": "queued",
                "errors": [],
                "updated_at": self._now(),
            }
        )

        return self._execute_job(
            retry_job,
        )

    def load_job(
        self,
        job_id: str,
    ) -> ExtractionWorkerJob:
        job_path = self.config.jobs_dir / f"{job_id}.json"

        if not job_path.exists():
            raise FileNotFoundError(
                f"Extraction worker job not found: {job_id}"
            )

        return ExtractionWorkerJob.model_validate_json(
            job_path.read_text(
                encoding="utf-8",
            )
        )

    def _execute_job(
        self,
        job: ExtractionWorkerJob,
    ) -> ExtractionWorkerJob:
        started_job = job.model_copy(
            update={
                "status": "running",
                "attempts": job.attempts + 1,
                "updated_at": self._now(),
            }
        )
        self._write_job(started_job)

        try:
            manifest = self.ingestion_service.load_manifest(
                started_job.document_id
            )

            source_path = Path(
                manifest.stored_raw_path
            )

            raw_text = self._read_source_text(
                source_path=source_path,
                extension=manifest.extension,
            )

            pages = self._split_pages(
                raw_text,
            )

            headings = self._detect_headings(
                pages,
            )

            tables = self._extract_tables(
                pages,
            )

            detected_asset_ids = self._detect_asset_ids(
                raw_text=raw_text,
                manifest_asset_ids=manifest.asset_ids,
            )

            chunks = self._chunk_pages(
                document_id=manifest.document_id,
                pages=pages,
                headings=headings,
                asset_ids=detected_asset_ids,
            )

            completed_job = started_job.model_copy(
                update={
                    "status": "completed",
                    "total_pages": len(pages),
                    "total_chunks": len(chunks),
                    "detected_asset_ids": detected_asset_ids,
                    "headings": headings,
                    "tables": tables,
                    "chunks": chunks,
                    "errors": [],
                    "updated_at": self._now(),
                }
            )

            self._write_job(completed_job)
            self._write_extracted_artifact(completed_job)

            return completed_job
        except Exception as exc:
            failed_job = started_job.model_copy(
                update={
                    "status": "failed",
                    "errors": [
                        ExtractionError(
                            code=exc.__class__.__name__,
                            message=str(exc),
                            retryable=True,
                        )
                    ],
                    "updated_at": self._now(),
                }
            )

            self._write_job(failed_job)
            self._append_failure_log(failed_job)

            return failed_job

    def _read_source_text(
        self,
        source_path: Path,
        extension: str,
    ) -> str:
        if not source_path.exists():
            raise FileNotFoundError(
                f"Stored document not found: {source_path}"
            )

        if extension == ".pdf":
            return self._read_pdf_like_text(
                source_path,
            )

        return source_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    def _read_pdf_like_text(
        self,
        source_path: Path,
    ) -> str:
        try:
            import pypdf  # type: ignore

            reader = pypdf.PdfReader(
                str(source_path)
            )

            pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]

            return "\f".join(pages)
        except Exception:
            return source_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

    def _split_pages(
        self,
        text: str,
    ) -> list[str]:
        if "\f" in text:
            pages = text.split("\f")
        else:
            pages = re.split(
                r"\n\s*(?:===\s*Page\s+\d+\s*===|Page\s+\d+\s*:)\s*\n",
                text,
                flags=re.IGNORECASE,
            )

        cleaned_pages = [
            page.strip()
            for page in pages
            if page.strip()
        ]

        return cleaned_pages or [text.strip()]

    def _detect_headings(
        self,
        pages: list[str],
    ) -> list[ExtractedHeading]:
        headings: list[ExtractedHeading] = []

        for page_index, page in enumerate(
            pages,
            start=1,
        ):
            for line_index, line in enumerate(
                page.splitlines(),
                start=1,
            ):
                stripped = line.strip()

                if not stripped:
                    continue

                is_markdown_heading = stripped.startswith("#")
                is_section_heading = stripped.endswith(":")
                is_upper_heading = (
                    stripped.upper() == stripped
                    and len(stripped.split()) <= 8
                    and any(char.isalpha() for char in stripped)
                )

                if (
                    is_markdown_heading
                    or is_section_heading
                    or is_upper_heading
                ):
                    headings.append(
                        ExtractedHeading(
                            page_number=page_index,
                            heading_text=stripped.lstrip("#").strip(": "),
                            line_number=line_index,
                        )
                    )

        return headings

    def _extract_tables(
        self,
        pages: list[str],
    ) -> list[ExtractedTable]:
        tables: list[ExtractedTable] = []

        for page_index, page in enumerate(
            pages,
            start=1,
        ):
            table_rows: list[list[str]] = []

            for line in page.splitlines():
                if "|" not in line:
                    continue

                cells = [
                    cell.strip()
                    for cell in line.strip("|").split("|")
                ]

                if len(cells) >= 2:
                    table_rows.append(cells)

            if table_rows:
                tables.append(
                    ExtractedTable(
                        page_number=page_index,
                        table_index=len(tables),
                        rows=table_rows,
                    )
                )

        return tables

    def _detect_asset_ids(
        self,
        raw_text: str,
        manifest_asset_ids: list[str],
    ) -> list[str]:
        detected = set(
            ASSET_TAG_PATTERN.findall(
                raw_text
            )
        )

        detected.update(
            manifest_asset_ids
        )

        return sorted(detected)

    def _chunk_pages(
        self,
        document_id: str,
        pages: list[str],
        headings: list[ExtractedHeading],
        asset_ids: list[str],
    ) -> list[PageAwareChunk]:
        chunks: list[PageAwareChunk] = []
        chunk_size = max(
            1,
            self.config.chunk_size_chars,
        )
        overlap = max(
            0,
            self.config.chunk_overlap_chars,
        )

        headings_by_page = {
            heading.page_number: heading.heading_text
            for heading in headings
        }

        for page_number, page in enumerate(
            pages,
            start=1,
        ):
            start = 0
            page_length = len(page)

            while start < page_length:
                end = min(
                    start + chunk_size,
                    page_length,
                )
                chunk_text = page[start:end].strip()

                if chunk_text:
                    chunk_index = len(chunks)
                    chunks.append(
                        PageAwareChunk(
                            document_id=document_id,
                            chunk_id=(
                                f"{document_id}-PAGE-{page_number:04d}-"
                                f"CHUNK-{chunk_index + 1:04d}"
                            ),
                            chunk_index=chunk_index,
                            page_number=page_number,
                            section_heading=headings_by_page.get(
                                page_number,
                            ),
                            text=chunk_text,
                            character_start=start,
                            character_end=end,
                            token_estimate=max(
                                1,
                                len(chunk_text) // 4,
                            ),
                            asset_ids=[
                                asset
                                for asset in asset_ids
                                if asset in chunk_text
                            ]
                            or asset_ids,
                        )
                    )

                if end >= page_length:
                    break

                next_start = end - overlap
                if next_start <= start:
                    next_start = end

                start = next_start

        return chunks

    def _new_job(
        self,
        document_id: str,
    ) -> ExtractionWorkerJob:
        now = self._now()
        job_id = f"EXT-JOB-{document_id}-{now.replace(':', '').replace('.', '')}"

        return ExtractionWorkerJob(
            job_id=job_id,
            document_id=document_id,
            status="queued",
            parser=ParserMetadata(
                parser_name=PARSER_NAME,
                parser_version=PARSER_VERSION,
                parser_mode="page_aware_local_worker",
            ),
            created_at=now,
            updated_at=now,
        )

    def _write_job(
        self,
        job: ExtractionWorkerJob,
    ) -> None:
        job_path = self.config.jobs_dir / f"{job.job_id}.json"
        job_path.write_text(
            job.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def _write_extracted_artifact(
        self,
        job: ExtractionWorkerJob,
    ) -> None:
        artifact_path = self.config.extracted_dir / f"{job.document_id}.json"
        artifact_path.write_text(
            job.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def _append_failure_log(
        self,
        job: ExtractionWorkerJob,
    ) -> None:
        with self.config.failure_log_path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(
                    {
                        "job_id": job.job_id,
                        "document_id": job.document_id,
                        "attempts": job.attempts,
                        "errors": [
                            error.model_dump()
                            for error in job.errors
                        ],
                        "updated_at": job.updated_at,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    def _now(
        self,
    ) -> str:
        return datetime.now(
            timezone.utc,
        ).isoformat()