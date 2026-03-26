from onlycuts.app.config.settings import settings
from onlycuts.app.domain.enums.statuses import ApprovalStatus
from onlycuts.app.domain.errors.exceptions import AuthorizationError
from onlycuts.app.repositories.approvals import ApprovalRepository


ACTION_TO_STATUS = {
    "post": ApprovalStatus.APPROVED.value,
    "queue": ApprovalStatus.DEFERRED.value,
    "reject": ApprovalStatus.REJECTED.value,
    "regen": ApprovalStatus.REWRITE_REQUESTED.value,
    "shorter": ApprovalStatus.REWRITE_REQUESTED.value,
    "stronger": ApprovalStatus.REWRITE_REQUESTED.value,
    "help": ApprovalStatus.PENDING.value,
}


class ApprovalService:
    def __init__(self, approvals: ApprovalRepository):
        self.approvals = approvals

    def record_action(self, actor_user_id: int, draft_id: str, action: str) -> str:
        if actor_user_id != settings.telegram_approver_user_id:
            raise AuthorizationError("only configured approver may take actions")
        status = ACTION_TO_STATUS.get(action)
        if status is None:
            raise ValueError("unsupported action")
        approval = self.approvals.create(draft_id=draft_id, actor_telegram_user_id=actor_user_id, action=action, status=status)
        return approval.status
