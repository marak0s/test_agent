from onlycuts.app.repositories.artifacts import ArtifactRepository


class ArtifactStore:
    def __init__(self, repo: ArtifactRepository):
        self.repo = repo

    def save(self, kind: str, ref_id: str, payload: dict) -> None:
        self.repo.create(kind=kind, ref_id=ref_id, payload=payload)
