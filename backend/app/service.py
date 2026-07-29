"""Business-logic seam between the routers and the AI decision pipeline / DB.

This is the one place routers/api.py calls into. Keeping it here (rather than in the
router functions themselves) means the core logic has no dependency on FastAPI and is
easy to exercise directly in tests or a REPL.
"""

import json

from sqlalchemy.orm import Session

from app import embeddings, import_pipeline, schemas
from app.config import SIMILARITY_THRESHOLD, SIMILARITY_TOP_K
from app.models import Course, SourceMaterial


def run_import(db: Session, title: str, raw_text: str) -> schemas.ImportResultOut:
    new_embedding = embeddings.embed_text(title, raw_text)
    courses = db.query(Course).all()
    candidates = embeddings.top_k_candidate_courses(
        new_embedding, courses, k=SIMILARITY_TOP_K, threshold=SIMILARITY_THRESHOLD
    )
    candidate_ids = {course.id for course, _ in candidates}

    # Calls the Anthropic API; may raise import_pipeline.ImportDecisionError. No DB
    # writes have happened yet at this point, so nothing to roll back on failure.
    decision = import_pipeline.get_decision(title, raw_text, candidates)

    try:
        source_material = SourceMaterial(
            title=title,
            raw_text=raw_text,
            embedding=json.dumps(new_embedding),
        )
        db.add(source_material)
        db.flush()  # assign source_material.id before apply_decision needs it

        course = import_pipeline.apply_decision(db, source_material, decision, candidate_ids)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(course)
    db.refresh(source_material)

    return schemas.ImportResultOut(
        action=decision.action,
        reasoning=decision.reasoning,
        course_id=course.id,
        course_title=course.title,
        source_material_id=source_material.id,
    )


def list_courses(db: Session) -> list[schemas.CourseListItemOut]:
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return [
        schemas.CourseListItemOut(
            id=course.id,
            title=course.title,
            description=course.description,
            created_at=course.created_at,
            module_count=len(course.modules),
            concept_count=sum(len(module.concepts) for module in course.modules),
        )
        for course in courses
    ]


def get_course_detail(db: Session, course_id: int) -> schemas.CourseDetailOut | None:
    course = db.get(Course, course_id)
    if course is None:
        return None

    modules_out = [
        schemas.ModuleOut(
            id=module.id,
            title=module.title,
            description=module.description,
            order=module.order,
            concepts=[
                schemas.ConceptWithSourceOut(
                    id=concept.id,
                    title=concept.title,
                    content=concept.content,
                    order=concept.order,
                    source_material_id=concept.source_material_id,
                    created_at=concept.created_at,
                    source_material_title=concept.source_material.title,
                )
                for concept in module.concepts
            ],
        )
        for module in course.modules
    ]

    return schemas.CourseDetailOut(
        id=course.id,
        title=course.title,
        description=course.description,
        created_at=course.created_at,
        updated_at=course.updated_at,
        modules=modules_out,
    )


def get_source_material(db: Session, source_material_id: int) -> schemas.SourceMaterialOut | None:
    sm = db.get(SourceMaterial, source_material_id)
    if sm is None:
        return None

    return schemas.SourceMaterialOut(
        id=sm.id,
        title=sm.title,
        raw_text=sm.raw_text,
        decision_action=sm.decision_action,
        decision_reasoning=sm.decision_reasoning,
        target_course_id=sm.target_course_id,
        created_at=sm.created_at,
        concepts=[
            schemas.ConceptOut(
                id=concept.id,
                title=concept.title,
                content=concept.content,
                order=concept.order,
                source_material_id=concept.source_material_id,
                created_at=concept.created_at,
            )
            for concept in sm.concepts
        ],
    )
