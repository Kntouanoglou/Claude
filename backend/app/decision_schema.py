"""The structured-output contract Claude must fill in for every import decision.

Kept deliberately separate from schemas.py (the public JSON API contract): this
schema is tuned for what the model needs to reliably produce (flat-ish, every
object closed with additionalProperties=false per the structured-outputs
constraints), while schemas.py is tuned for what the frontend needs to render.
They will drift independently as we tune prompts vs. as we tune the UI.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    # extra="forbid" makes pydantic emit "additionalProperties": false on every
    # generated JSON Schema object, which Claude's structured-outputs feature
    # requires for every object in the schema.
    model_config = ConfigDict(extra="forbid")


class ConceptProposal(StrictModel):
    title: str
    content: str  # synthesized/organized learning content, not a copy-paste of the source
    order: int  # relative ordering hint only — the app renumbers sequentially on write


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
