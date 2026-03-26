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
