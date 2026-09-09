"""Small persistence helpers shared by routers. Kept intentionally thin -
no repository/service-layer abstraction.
"""

from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app import models
from app.seed_sources import lookup


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def get_or_create_source(db: Session, domain: str) -> models.Source:
    source = db.query(models.Source).filter(models.Source.domain == domain).one_or_none()
    if source:
        return source
    info = lookup(domain)
    source = models.Source(
        name=info["name"],
        domain=domain,
        reliability_score=info["reliability_score"],
        bias_score=info["bias_score"],
    )
    db.add(source)
    db.flush()
    return source
