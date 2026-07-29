"""The AI Decision Structure: given a new import, decide how it fits into the
existing course library and write the resulting structure to the DB.

Pipeline (see app/service.py for the orchestrating entry point, run_import):
  1. Embed the new material (app/embeddings.py) - used only for candidate retrieval.
  2. Shortlist top-K existing courses above a similarity threshold.
  3. One Claude call (structured output) decides the action AND produces the
     content (new course structure, or a targeted addition) in a single response.
  4. Apply the decision to the DB in one transaction.

Design note (flagged per the project plan): steps 3 does classification and content
generation in a single LLM call. This keeps latency/cost reasonable for a prototype,
at the cost of being harder to unit-test in isolation. Mitigation: get_decision() is
the single seam to mock, so apply_decision() (the DB-writing half) is fully
unit-testable against hand-built ImportDecision objects without ever calling the API.
"""

import json

from app.claude_client import EFFORT, MAX_TOKENS, MODEL, get_client
from app.decision_schema import ImportDecision
from app.models import Concept, Course, Module, SourceMaterial
from app.embeddings import compute_course_representative_embedding


class ImportDecisionError(Exception):
    """Raised when Claude's decision can't be safely applied (refusal, truncation,
    or a hallucinated target_course_id that wasn't actually offered as a candidate)."""


SYSTEM_PROMPT = """\
You are the content-organization engine for an AI course-builder. Given a piece of \
imported learning material (title + text) and, optionally, a shortlist of existing \
courses that might be related, decide exactly one of: create a brand-new course, add \
this material as new content to an existing course, or add it as a single new concept \
within an existing course's structure. Then produce the structured content for that \
decision.

Rules:
- If no candidate courses are provided, or none are a good conceptual fit, choose \
new_course.
- target_course_id must exactly match one of the candidate course IDs provided - never \
invent an ID.
- Concept `content` fields must be synthesized, organized prose derived from the source \
material - not a verbatim copy-paste and not a one-line stub. Write it as real course \
content a learner would read.
- Course and module `description` fields must be concise (1-3 sentences) and \
semantically representative, since they are also used for future similarity matching \
against this course.
- Only set updated_course_description if the new content meaningfully changes what the \
course as a whole covers; otherwise leave it null.
"""


def _format_candidate(course: Course, score: float) -> str:
    lines = [
        f"### Candidate course_id={course.id} (similarity={score:.2f})",
        f"Title: {course.title}",
        f"Description: {course.description}",
        "Modules:",
    ]
    if course.modules:
        for module in course.modules:
            concept_titles = ", ".join(c.title for c in module.concepts) or "(no concepts yet)"
            lines.append(f"  - {module.title}: {concept_titles}")
    else:
        lines.append("  (no modules yet)")
    return "\n".join(lines)


def build_user_content(title: str, raw_text: str, candidates: list[tuple[Course, float]]) -> str:
    parts = [
        "## New material to import",
        f"Title: {title}",
        "",
        "Text:",
        raw_text,
        "",
        "## Candidate existing courses (may be empty)",
    ]
    if candidates:
        parts.extend(_format_candidate(course, score) for course, score in candidates)
    else:
        parts.append("(none - there are no existing courses, or none are a plausible fit)")
    parts.append("\nDecide the action and produce the structured output per the schema.")
    return "\n".join(parts)


def get_decision(title: str, raw_text: str, candidates: list[tuple[Course, float]]) -> ImportDecision:
    client = get_client()
    user_content = build_user_content(title, raw_text, candidates)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        output_config={
            "format": {
                "type": "json_schema",
                "schema": ImportDecision.model_json_schema(),
            },
            "effort": EFFORT,
        },
        messages=[{"role": "user", "content": user_content}],
    )

    if response.stop_reason == "refusal":
        raise ImportDecisionError(f"Claude refused the request: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise ImportDecisionError(
            "Claude's response was truncated at max_tokens before completing the "
            "structured output; consider raising MAX_TOKENS or lowering CLAUDE_EFFORT."
        )

    text = next((block.text for block in response.content if block.type == "text"), None)
    if text is None:
        raise ImportDecisionError("Claude's response contained no text content to parse.")

    return ImportDecision.model_validate_json(text)


def _renumber(items: list, key) -> list:
    """Sort by the model-supplied `order` hint, but return items ready to be
    assigned fresh sequential integers by the caller - we never trust the AI's raw
    order values as literal, unique DB values."""
    return sorted(items, key=key)


def apply_decision(
    db,
    source_material: SourceMaterial,
    decision: ImportDecision,
    candidate_ids: set[int],
) -> Course:
    if decision.action == "new_course":
        if decision.new_course is None:
            raise ImportDecisionError("action=new_course but no new_course proposal was provided")

        proposal = decision.new_course
        course = Course(
            title=proposal.title,
            description=proposal.description,
        )
        course.embedding = None  # set after flush, once we're sure title/description are final
        db.add(course)
        db.flush()  # assign course.id

        for module_order, module_proposal in enumerate(_renumber(proposal.modules, lambda m: m.order)):
            module = Module(
                course_id=course.id,
                title=module_proposal.title,
                description=module_proposal.description,
                order=module_order,
            )
            db.add(module)
            db.flush()  # assign module.id

            for concept_order, concept_proposal in enumerate(
                _renumber(module_proposal.concepts, lambda c: c.order)
            ):
                db.add(
                    Concept(
                        module_id=module.id,
                        title=concept_proposal.title,
                        content=concept_proposal.content,
                        order=concept_order,
                        source_material_id=source_material.id,
                    )
                )

        course.embedding = json.dumps(
            compute_course_representative_embedding(course.title, course.description)
        )

    else:
        if decision.target_course_id is None or decision.target_course_id not in candidate_ids:
            raise ImportDecisionError(
                f"target_course_id={decision.target_course_id!r} was not among the "
                f"candidate course IDs actually offered ({sorted(candidate_ids)}); "
                "refusing to write to an unverified course."
            )
        course = db.get(Course, decision.target_course_id)
        if course is None:
            raise ImportDecisionError(f"target course {decision.target_course_id} no longer exists")

        addition = decision.addition
        if addition is None:
            raise ImportDecisionError(f"action={decision.action} but no addition proposal was provided")

        target = addition.module_target
        if target.existing_module_id is not None:
            module = db.get(Module, target.existing_module_id)
            if module is None or module.course_id != course.id:
                raise ImportDecisionError(
                    f"existing_module_id={target.existing_module_id} is not a module of "
                    f"course {course.id}"
                )
        elif target.new_module_title:
            max_module_order = max((m.order for m in course.modules), default=-1)
            module = Module(
                course_id=course.id,
                title=target.new_module_title,
                description=target.new_module_description or "",
                order=max_module_order + 1,
            )
            db.add(module)
            db.flush()
        else:
            raise ImportDecisionError(
                "module_target has neither existing_module_id nor new_module_title set"
            )

        max_concept_order = max((c.order for c in module.concepts), default=-1)
        for offset, concept_proposal in enumerate(_renumber(addition.concepts, lambda c: c.order)):
            db.add(
                Concept(
                    module_id=module.id,
                    title=concept_proposal.title,
                    content=concept_proposal.content,
                    order=max_concept_order + 1 + offset,
                    source_material_id=source_material.id,
                )
            )

        if addition.updated_course_description:
            course.description = addition.updated_course_description
            course.embedding = json.dumps(
                compute_course_representative_embedding(course.title, course.description)
            )

    db.flush()

    source_material.decision_action = decision.action
    source_material.decision_reasoning = decision.reasoning
    source_material.target_course_id = course.id

    return course
