from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB


class Event(UUIDAuditBase):
    __tablename__ = "events"

    typ: Mapped[str | None] = mapped_column(String(63))
    log_index: Mapped[str] = mapped_column(String(255))
    transaction_hash: Mapped[str] = mapped_column(String(64))
    block_number: Mapped[int] = mapped_column(Integer)
    raw_data: Mapped[dict] = mapped_column(JSONB)
    data: Mapped[dict] = mapped_column(JSONB)
    from_address: Mapped[str] = mapped_column(String(42))
    to_address: Mapped[str] = mapped_column(String(42))

    __table_args__ = (
        UniqueConstraint(
            "transaction_hash", "log_index", "block_number",
            name="uq_transaction_log_block"
        ),
    )
