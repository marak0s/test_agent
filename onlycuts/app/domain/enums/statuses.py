from enum import Enum


class TopicStatus(str, Enum):
    NEW = "new"
    SHORTLISTED = "shortlisted"
    PLANNED = "planned"
    DRAFTED = "drafted"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ContentStatus(str, Enum):
    PLANNED = "planned"
    DRAFTING = "drafting"
    REVIEW = "review"
    APPROVED = "approved"
    QUEUED = "queued"
    PUBLISHED = "published"
    REJECTED = "rejected"


class DraftReviewStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    PASSED = "passed"
    FAILED = "failed"
    SUPERSEDED = "superseded"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REWRITE_REQUESTED = "rewrite_requested"
    DEFERRED = "deferred"


class PublicationStatus(str, Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
