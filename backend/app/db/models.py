from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    row_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    fields: Mapped[list["DatasetField"]] = relationship(
        "DatasetField",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    records: Mapped[list["Record"]] = relationship(
        "Record",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )


class DatasetField(Base):
    __tablename__ = "dataset_fields"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dataset_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    null_frac: Mapped[float] = mapped_column(nullable=False)
    distinct_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    example_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    dataset: Mapped[Dataset] = relationship("Dataset", back_populates="fields")

    __table_args__ = (
        UniqueConstraint("dataset_id", "name", name="uix_dataset_field_name"),
    )


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dataset_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    dataset: Mapped[Dataset] = relationship("Dataset", back_populates="records")
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        "Bookmark",
        back_populates="record",
        cascade="all, delete-orphan",
    )


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("records.id", ondelete="CASCADE"),
        nullable=False,
    )
    note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    record: Mapped[Record] = relationship("Record", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("user_id", "record_id", name="uix_user_record_bookmark"),
    )
