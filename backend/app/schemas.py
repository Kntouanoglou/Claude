"""Pydantic DTOs for the public JSON API. Deliberately separate from
decision_schema.py (Claude's structured-output contract) - these two schemas serve
different consumers and will evolve independently.
"""

from datetime import datetime

from pydantic import BaseModel


class ConceptOut(BaseModel):
    id: int
    title: str
    summary: str
    key_points: list[str]
    content: str
    order: int
    source_material_id: int
    created_at: datetime


class ConceptWithSourceOut(ConceptOut):
    source_material_title: str


class ModuleOut(BaseModel):
    id: int
    title: str
    description: str
    order: int
    concepts: list[ConceptWithSourceOut]


class CourseListItemOut(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    module_count: int
    concept_count: int


class CourseDetailOut(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    modules: list[ModuleOut]


class SourceMaterialOut(BaseModel):
    id: int
    title: str
    raw_text: str
    decision_action: str | None
    decision_reasoning: str | None
    target_course_id: int | None
    created_at: datetime
    concepts: list[ConceptOut]


class ImportResultOut(BaseModel):
    action: str
    reasoning: str
    course_id: int
    course_title: str
    source_material_id: int
