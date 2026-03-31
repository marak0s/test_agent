from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import Artifact


class ArtifactRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, kind: str, ref_id: str, payload: dict) -> Artifact:
        artifact = Artifact(kind=kind, ref_id=ref_id, payload=payload)
        self.session.add(artifact)
        self.session.flush()
        return artifact

    def exists(self, kind: str, ref_id: str) -> bool:
        return self.session.scalar(select(Artifact.id).where(Artifact.kind == kind, Artifact.ref_id == ref_id)) is not None

    def latest(self, kind: str, ref_id: str) -> Artifact | None:
        return self.session.scalar(
            select(Artifact).where(Artifact.kind == kind, Artifact.ref_id == ref_id).order_by(Artifact.created_at.desc())
        )
