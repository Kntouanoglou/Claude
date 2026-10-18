from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SourceMaterial(Base):
    """One user import (title + raw text) and the AI's decision about it.

    Kept as a permanent audit trail: every concept in the system traces back to
    exactly one row here, and the decision/reasoning fields let us inspect why the
    AI organized things the way it did (useful for tuning the pipeline later).
    """

    __tablename__ = "source_material"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    raw_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[str | None] = mapped_column(Text)  # JSON-serialized list[float]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    decision_action: Mapped[str | None] = mapped_column(String(30))
    decision_reasoning: Mapped[str | None] = mapped_column(Text)
    target_course_id: Mapped[int | None] = mapped_column(ForeignKey("course.id"))

    target_course: Mapped["Course | None"] = relationship(
        back_populates="source_materials", foreign_keys=[target_course_id]
    )
    concepts: Mapped[list["Concept"]] = relationship(back_populates="source_material")

    __table_args__ = (Index("ix_source_material_created_at", "created_at"),)


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    description: Mapped[str] = mapped_column(Text)  # AI-generated
    embedding: Mapped[str | None] = mapped_column(Text)  # JSON list[float] — representative embedding
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    modules: Mapped[list["Module"]] = relationship(
        back_populates="course", order_by="Module.order", cascade="all, delete-orphan"
    )
    source_materials: Mapped[list["SourceMaterial"]] = relationship(
        back_populates="target_course", foreign_keys="SourceMaterial.target_course_id"
    )


class Module(Base):
    __tablename__ = "module"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)  # AI-generated
    order: Mapped[int] = mapped_column(Integer)

    course: Mapped["Course"] = relationship(back_populates="modules")
    concepts: Mapped[list["Concept"]] = relationship(
        back_populates="module", order_by="Concept.order", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("course_id", "order", name="uq_module_course_order"),)


class Concept(Base):
    __tablename__ = "concept"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("module.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text)  # one-sentence takeaway, shown as the lead-in
    key_points: Mapped[str] = mapped_column(Text)  # JSON-serialized list[str]
    content: Mapped[str] = mapped_column(Text)  # synthesized explanation, expands on the key points
    order: Mapped[int] = mapped_column(Integer)
    source_material_id: Mapped[int] = mapped_column(ForeignKey("source_material.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    module: Mapped["Module"] = relationship(back_populates="concepts")
    source_material: Mapped["SourceMaterial"] = relationship(back_populates="concepts")

    __table_args__ = (UniqueConstraint("module_id", "order", name="uq_concept_module_order"),)
