import hashlib
import json

def compute_document_hash(content_bytes: bytes) -> str:

    return hashlib.sha256(content_bytes).hexdigest()

def compute_result_hash(data: dict) -> str:

    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

def build_extraction_metadata(pages: list, processing_time_ms: int) -> dict:
    return {
        "overall_confidence": pages,
        "processing_time_ms": processing_time_ms
    }
