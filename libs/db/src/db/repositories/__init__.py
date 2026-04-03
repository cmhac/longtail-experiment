"""Repository exports for shared DB package."""

from .conflict_repository import InMemoryConflictRepository, StoredConflict
from .dataset_discovery_repository import InMemoryDatasetDiscoveryRepository
from .auth_management_repository import PostgresAuthManagementRepository
from .interfaces import (
    AuthManagementRepository,
    DatasetDiscoveryReadRepository,
    HierarchyRepository,
    ObservationRepository,
    ProvenanceRepository,
    TrendLifecycleRepository,
)
from .postgres_trend_repository import PostgresTrendRepository
from .run_repository import InMemoryRunRepository, StoredRunOutcome

__all__ = [
    "AuthManagementRepository",
    "DatasetDiscoveryReadRepository",
    "HierarchyRepository",
    "InMemoryConflictRepository",
    "InMemoryDatasetDiscoveryRepository",
    "InMemoryRunRepository",
    "ObservationRepository",
    "PostgresAuthManagementRepository",
    "PostgresTrendRepository",
    "ProvenanceRepository",
    "StoredConflict",
    "StoredRunOutcome",
    "TrendLifecycleRepository",
]
