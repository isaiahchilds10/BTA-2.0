"""Source result contract. No fake sports observations or live status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class FeedStatus(str, Enum):
    CURRENT = "CURRENT"
    DELAYED = "DELAYED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class SourceResult(Generic[T]):
    """A result with explicit freshness; no last-known datum is marked live by default.

    The adapter, not this contract, must implement measured freshness rules.
    """

    status: FeedStatus
    provider: str
    retrieved_at: Optional[datetime] = None
    provider_updated_at: Optional[datetime] = None
    value: Optional[T] = None
    limitation: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("provider must be specified")
        for field_name in ("retrieved_at", "provider_updated_at"):
            value = getattr(self, field_name)
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"{field_name} must be timezone-aware")
        if self.status == FeedStatus.CURRENT:
            if self.retrieved_at is None or self.provider_updated_at is None or self.value is None:
                raise ValueError("CURRENT requires observed data and both timestamps")
        if self.status == FeedStatus.DELAYED:
            if self.value is None or self.retrieved_at is None:
                raise ValueError("DELAYED requires last-known observed data and retrieval time")
        if self.status == FeedStatus.UNAVAILABLE and self.value is not None:
            raise ValueError("UNAVAILABLE cannot contain fabricated data")
