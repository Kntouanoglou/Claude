"""The structured-output contract Claude must fill in for every import decision.

Kept deliberately separate from schemas.py (the public JSON API contract): this
schema is tuned for what the model needs to reliably produce (flat-ish, every
object closed with additionalProperties=false per the structured-outputs
constraints), while schemas.py is tuned for what the frontend needs to render.
They will drift independently as we tune prompts vs. as we tune the UI.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

# Minimum length (after stripping whitespace) for a concept's synthesized content.
# Not a quality bar, just a floor that catches empty/placeholder output outright —
# real synthesized prose is expected to run to many hundreds of characters.
_MIN_CONCEPT_CONTENT_CHARS = 40


class StrictModel(BaseModel):
    # extra="forbid" makes pydantic emit "additionalProperties": false on every
    # generated JSON Schema object, which Claude's structured-outputs feature
    # requires for every object in the schema.
    model_config = ConfigDict(extra="forbid")


class ConceptProposal(StrictModel):
    title: str
    summary: str  # one plain-English sentence: the single takeaway of this concept
    key_points: list[str]  # 3-6 short, scannable, self-contained points
    content: str  # a short explanation paragraph that expands on the key points
    order: int  # relative ordering hint only — the app renumbers sequentially on write

    @field_validator("title")
    @classmethod
    def title_must_be_non_trivial(cls, v: str) -> str:
        if len(v.strip()) < 3 or v.strip().lower() in {"placeholder", "todo", "tbd", "n/a"}:
            raise ValueError(f"concept title {v!r} looks like a placeholder, not a real concept title")
        return v

    @field_validator("summary")
    @classmethod
    def summary_must_be_non_trivial(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("concept summary is missing or too short to be a real takeaway")
        return v

    @field_validator("key_points")
    @classmethod
    def key_points_must_be_substantive(cls, v: list[str]) -> list[str]:
        # NOTE: intentionally plain @field_validators, not Field(min_length=...) —
        # a min_length constraint would get baked into model_json_schema() and sent
        # to Claude as part of output_config.format.schema, where it's an
        # unsupported JSON Schema feature for structured outputs. A validator runs
        # client-side only and never touches the schema we send.
        cleaned = [p.strip() for p in v if p.strip()]
        if len(cleaned) < 2:
            raise ValueError("concept needs at least 2 real key_points, not a placeholder list")
        if any(len(p) < 10 for p in cleaned):
            raise ValueError("a key_point is too short to be a real, self-contained point")
        return cleaned

    @field_validator("content")
    @classmethod
    def content_must_be_substantive(cls, v: str) -> str:
        if len(v.strip()) < _MIN_CONCEPT_CONTENT_CHARS:
            raise ValueError(
                "concept content is empty or too short to be real synthesized "
                f"prose (min {_MIN_CONCEPT_CONTENT_CHARS} chars) — looks like a placeholder"
            )
        return v


class ModuleProposal(StrictModel):
    title: str
    description: str  # also used as embedding input if this becomes part of a new course
    order: int
    concepts: list[ConceptProposal]


class NewCourseProposal(StrictModel):
    title: str
    description: str  # embedded as the course's representative embedding
    modules: list[ModuleProposal]


class ModuleTarget(StrictModel):
    # Exactly one of these should be set by the model:
    existing_module_id: Optional[int] = None
    new_module_title: Optional[str] = None
    new_module_description: Optional[str] = None


class AdditionProposal(StrictModel):
    module_target: ModuleTarget
    concepts: list[ConceptProposal]
    # Only set when the new content meaningfully shifts what the course as a whole
    # covers; if set, the app refreshes Course.description and recomputes its
    # representative embedding.
    updated_course_description: Optional[str] = None


class ImportDecision(StrictModel):
    action: Literal["new_course", "add_to_course", "new_concept_in_course"]
    reasoning: str
    # Required (non-null) whenever action != "new_course"; must match one of the
    # candidate course IDs actually offered in the prompt — validated in
    # import_pipeline.apply_decision before any DB write.
    target_course_id: Optional[int] = None
    new_course: Optional[NewCourseProposal] = None
    addition: Optional[AdditionProposal] = None
