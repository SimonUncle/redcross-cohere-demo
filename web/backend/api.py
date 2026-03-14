"""FastAPI backend wrapping the existing agent/vision/translate modules with SSE streaming."""

import sys
import os
import json
import asyncio
from typing import Optional

# Add project root to sys.path so we can import from backend.*
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from backend.agent import run_agent, run_agent_stream
from backend.classifier import classify_query, MODEL_FAST, MODEL_REASONING
from backend.vision import analyze_prescription, translate_to_korean, translate_to_english

app = FastAPI(title="Red Cross Blood Donation Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str
    model: Optional[str] = None
    lang: Optional[str] = "ko"


class CompareRequest(BaseModel):
    query: str
    lang: Optional[str] = "ko"


class TranslateRequest(BaseModel):
    text: str
    direction: str  # "en_to_kr" | "kr_to_en"


class TranslatePipelineRequest(BaseModel):
    query_en: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sse_event(event: str, data: dict) -> dict:
    """Format an SSE event dict for EventSourceResponse."""
    return {"event": event, "data": json.dumps(data, ensure_ascii=False)}


def _sse_error(message: str) -> dict:
    return {"event": "error", "data": json.dumps({"error": message}, ensure_ascii=False)}


# ---------------------------------------------------------------------------
# POST /api/chat  (SSE streaming)
# ---------------------------------------------------------------------------

@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        try:
            loop = asyncio.get_event_loop()
            queue: asyncio.Queue = asyncio.Queue()

            def _produce():
                for evt in _collect_stream_events(req.query, req.model, req.lang):
                    loop.call_soon_threadsafe(queue.put_nowait, evt)
                loop.call_soon_threadsafe(queue.put_nowait, None)

            loop.run_in_executor(None, _produce)

            while True:
                evt = await queue.get()
                if evt is None:
                    break
                yield evt
        except Exception as exc:
            yield _sse_error(str(exc))

    return EventSourceResponse(
        event_generator(),
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _collect_stream_events(query: str, model: Optional[str], lang: Optional[str] = "ko"):
    """Consume run_agent_stream and yield SSE-formatted dicts."""
    try:
        stream = run_agent_stream(query, model=model, lang=lang or "ko")
        for event in stream:
            etype = event.get("type")

            if etype == "classification":
                yield _sse_event("classification", event["classification"])

            elif etype == "tool_start":
                yield _sse_event("tool_call", {
                    "step": event["step"],
                    "tool": event["tool"],
                    "args": event["args"],
                    "status": "running",
                })

            elif etype == "tool_done":
                yield _sse_event("tool_call", {
                    "step": event["step"],
                    "tool": event["tool"],
                    "args": event["args"],
                    "result": event.get("result", ""),
                    "result_preview": event.get("result_preview", ""),
                    "status": "done",
                })

            elif etype == "sources":
                yield _sse_event("sources", {"data": event.get("data", [])})

            elif etype == "tool_plan":
                yield _sse_event("tool_plan", {"text": event.get("text", "")})

            elif etype == "content_delta":
                yield _sse_event("text_delta", {"text": event.get("text", "")})

            elif etype == "thinking":
                yield _sse_event("thinking", {"text": event.get("text", "")})

            elif etype == "judgment":
                yield _sse_event("judgment", event.get("judgment", {}))
                if event.get("timing"):
                    yield _sse_event("timing", event["timing"])

            elif etype == "answer":
                yield _sse_event("answer", {"text": event.get("text", "")})

            elif etype == "result":
                yield _sse_event("done", {
                    "total_tokens": event.get("total_tokens"),
                    "rate_limits": event.get("rate_limits"),
                })

    except Exception as exc:
        yield _sse_error(str(exc))


# ---------------------------------------------------------------------------
# POST /api/chat/compare  (JSON)
# ---------------------------------------------------------------------------

@app.post("/api/chat/compare")
async def chat_compare(req: CompareRequest):
    loop = asyncio.get_event_loop()
    lang = req.lang or "ko"
    fast_future = loop.run_in_executor(
        None,
        lambda: run_agent(req.query, thinking_enabled=False, model=MODEL_FAST, lang=lang),
    )
    reasoning_future = loop.run_in_executor(
        None,
        lambda: run_agent(req.query, thinking_enabled=True, model=MODEL_REASONING, lang=lang),
    )

    # Run both models; if one fails, return partial result with error for the failed one
    fast_result = None
    reasoning_result = None
    errors = {}

    try:
        fast_result = await fast_future
    except Exception as exc:
        errors["command_a"] = str(exc)
        fast_result = {"error": str(exc), "answer": f"Error: {exc}", "judgment": {}, "tool_calls": []}

    try:
        reasoning_result = await reasoning_future
    except Exception as exc:
        errors["reasoning"] = str(exc)
        reasoning_result = {"error": str(exc), "answer": f"Error: {exc}", "judgment": {}, "tool_calls": []}

    if len(errors) == 2:
        raise HTTPException(status_code=500, detail=f"Both models failed: {errors}")

    return {"command_a": fast_result, "reasoning": reasoning_result}


# ---------------------------------------------------------------------------
# POST /api/vision  (JSON)
# ---------------------------------------------------------------------------

@app.post("/api/vision")
async def vision(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        loop = asyncio.get_event_loop()
        ocr_text = await loop.run_in_executor(None, analyze_prescription, image_bytes)

        # OCR 결과를 에이전트 파이프라인에 전달하여 판정
        agent_query = f"다음 처방전 OCR 결과를 바탕으로 각 약물별 헌혈 가능 여부를 판정해주세요:\n\n{ocr_text}"
        agent_result = await loop.run_in_executor(
            None, lambda: run_agent(agent_query)
        )

        return {
            "ocr_text": ocr_text,
            "pipeline_result": {
                "judgment": agent_result.get("judgment"),
                "answer": agent_result.get("answer"),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# POST /api/translate  (JSON)
# ---------------------------------------------------------------------------

@app.post("/api/translate")
async def translate(req: TranslateRequest):
    try:
        loop = asyncio.get_event_loop()
        if req.direction == "en_to_kr":
            translated = await loop.run_in_executor(None, translate_to_korean, req.text)
        elif req.direction == "kr_to_en":
            translated = await loop.run_in_executor(None, translate_to_english, req.text)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid direction '{req.direction}'. Use 'en_to_kr' or 'kr_to_en'.",
            )
        return {"translated": translated}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# POST /api/translate/pipeline  (SSE streaming)
# ---------------------------------------------------------------------------

@app.post("/api/translate/pipeline")
async def translate_pipeline(req: TranslatePipelineRequest):
    async def event_generator():
        try:
            loop = asyncio.get_event_loop()

            # Step 1: Translate EN → KR
            query_kr = await loop.run_in_executor(None, translate_to_korean, req.query_en)
            yield _sse_event("translate_input", {"text": query_kr})

            # Step 2: Run agent stream on Korean query
            events = await loop.run_in_executor(
                None,
                lambda: list(_collect_stream_events(query_kr, model=None)),
            )

            # Collect answer text for final translation
            answer_parts = []
            for evt in events:
                yield evt
                # Collect answer (new) or text_delta (legacy) to build full answer
                evt_name = evt.get("event")
                if evt_name in ("answer", "text_delta"):
                    data = json.loads(evt["data"])
                    answer_parts.append(data.get("text", ""))

            # Step 3: Translate full answer KR → EN
            full_answer_kr = "".join(answer_parts)
            if full_answer_kr:
                answer_en = await loop.run_in_executor(
                    None, translate_to_english, full_answer_kr
                )
                yield _sse_event("translate_output", {"text": answer_en})

        except Exception as exc:
            yield _sse_error(str(exc))

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7070)
