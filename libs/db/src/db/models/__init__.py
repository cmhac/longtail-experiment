"""SQLAlchemy model exports for the shared contract database."""

from .base import Base
from .data_series import DataSeries
from .lineage import ProvenanceRecord, RevisionRecord
from .ingestion_runtime import (
    ConflictRecord,
    IngestionRun,
    SourceEligibilitySnapshot,
    SourceRunLock,
    SourceRunOutcome,
    SeriesRunOutcome,
    SourceSchedulePolicy,
)
from .observation import Observation
from .source_profile import SourceProfile
from .taxonomy import CategoryNode, GeographyNode
from .trends import (
    TrendCanonicalDescriptor,
    TrendChangeEvent,
    TrendLookbackEvaluation,
    TrendLookbackSnapshot,
    TrendRecord,
    TrendTransitionEvent,
    UserDatasetSubscription,
    UserTrendNotification,
)
from .topic_tag import DataSeriesTopicTag, TopicTag

try:
    from .auth_management import (
        AccountAuditEvent,
        AuthSession,
        CredentialRecord,
        RoleAssignment,
        UserAccount,
    )
except ModuleNotFoundError:
    # The auth_management module is introduced in a later foundational task.
    pass

__all__ = [
    "AccountAuditEvent",
    "AuthSession",
    "Base",
    "CategoryNode",
    "ConflictRecord",
    "CredentialRecord",
    "DataSeries",
    "DataSeriesTopicTag",
    "GeographyNode",
    "IngestionRun",
    "Observation",
    "ProvenanceRecord",
    "RevisionRecord",
    "RoleAssignment",
    "SourceEligibilitySnapshot",
    "SourceRunLock",
    "SourceRunOutcome",
    "SeriesRunOutcome",
    "SourceSchedulePolicy",
    "SourceProfile",
    "TrendCanonicalDescriptor",
    "TrendChangeEvent",
    "TrendLookbackEvaluation",
    "TrendLookbackSnapshot",
    "TrendRecord",
    "TrendTransitionEvent",
    "TopicTag",
    "UserDatasetSubscription",
    "UserTrendNotification",
    "UserAccount",
]
