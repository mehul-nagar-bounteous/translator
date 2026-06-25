from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, field_validator

from languages import SOURCE_LANGUAGE, SUPPORTED_LANGUAGES, is_valid_target
from translator import TranslationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.translator = TranslationService()
    yield
    del app.state.translator


app = FastAPI(
    title="IndicTrans2 Translation API",
    description="Translate English text into any of the 22 Indian languages using ai4bharat/indictrans2-en-indic-1B.",
    version="1.0.0",
    lifespan=lifespan,
)


class TranslateRequest(BaseModel):
    text: str
    target_language: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v.strip()

    @field_validator("target_language")
    @classmethod
    def language_must_be_supported(cls, v: str) -> str:
        if not is_valid_target(v):
            raise ValueError(
                f"'{v}' is not a supported target language. "
                f"Call GET /languages for the full list."
            )
        return v


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class TranslateResponse(BaseModel):
    source_language: str
    translated_text: str
    time_taken_ms: float
    token_usage: TokenUsage


@app.get("/health", tags=["Meta"])
def health():
    return {"status": "ready"}


@app.get("/languages", tags=["Meta"])
def list_languages():
    return {
        "source_language": {SOURCE_LANGUAGE: "English"},
        "target_languages": SUPPORTED_LANGUAGES,
    }


@app.post("/translate", response_model=TranslateResponse, tags=["Translation"])
def translate(body: TranslateRequest, request: Request):
    service: TranslationService = request.app.state.translator
    try:
        result = service.translate(body.text, body.target_language)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TranslateResponse(
        source_language=SOURCE_LANGUAGE,
        translated_text=result.translated_text,
        time_taken_ms=result.time_taken_ms,
        token_usage=TokenUsage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            total_tokens=result.input_tokens + result.output_tokens,
        ),
    )
