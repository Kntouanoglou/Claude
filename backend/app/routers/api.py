import anthropic
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import schemas, service
from app.db import get_db
from app.import_pipeline import ImportDecisionError

router = APIRouter(prefix="/api")


@router.post("/import", response_model=schemas.ImportResultOut)
async def import_material(
    title: str = Form(...),
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    file_text = None
    if file is not None:
        file_bytes = await file.read()
        file_text = file_bytes.decode("utf-8", errors="replace")

    resolved_text = (text or "").strip() or (file_text or "").strip()
    if not resolved_text:
        raise HTTPException(
            status_code=400, detail="Provide either pasted text or a .txt file upload."
        )
    if not title or not title.strip():
        raise HTTPException(status_code=400, detail="Title is required.")

    try:
        return service.run_import(db, title.strip(), resolved_text)
    except ImportDecisionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        # Raised by claude_client.get_client() when ANTHROPIC_API_KEY is unset —
        # a config problem, not a bad request, so surface it as 503 with a clear
        # message rather than a generic 500.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except anthropic.APIStatusError as exc:
        # The Anthropic API itself rejected the request (bad API key, no credit
        # balance, rate limit, overload, etc.). exc.message is the whole raw
        # "Error code: 400 - {...}" string; pull out the clean nested message
        # the API actually sent, falling back to the raw string if the body
        # isn't shaped as expected.
        error_body = exc.body.get("error") if isinstance(exc.body, dict) else None
        clean_message = error_body.get("message") if isinstance(error_body, dict) else None
        raise HTTPException(
            status_code=502, detail=f"Anthropic API error: {clean_message or exc.message}"
        ) from exc
    except anthropic.APIConnectionError as exc:
        raise HTTPException(
            status_code=502, detail="Could not reach the Anthropic API — check your network connection."
        ) from exc


@router.get("/courses", response_model=list[schemas.CourseListItemOut])
def list_courses(db: Session = Depends(get_db)):
    return service.list_courses(db)


@router.get("/courses/{course_id}", response_model=schemas.CourseDetailOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = service.get_course_detail(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/source-materials/{source_material_id}", response_model=schemas.SourceMaterialOut)
def get_source_material(source_material_id: int, db: Session = Depends(get_db)):
    source_material = service.get_source_material(db, source_material_id)
    if source_material is None:
        raise HTTPException(status_code=404, detail="Source material not found")
    return source_material
