from fastapi import APIRouter, HTTPException

from app.ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from app.schemas import (
    DocumentRequest,
    GenerateResponse,
)


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.post(
    "/generate",
    response_model=GenerateResponse,
    tags=["documents"]
)
def generate_document(
    request: DocumentRequest
):

    try:

        document, model, demo_mode = (
            generator.generate_document(
                document_type=request.document_type,
                parties=request.parties,
                terms=request.terms,
                dates=request.dates,
            )
        )

        return GenerateResponse(
            document=document,
            model=model,
            demo_mode=demo_mode,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI document generation failed: {exc}",
        ) from exc