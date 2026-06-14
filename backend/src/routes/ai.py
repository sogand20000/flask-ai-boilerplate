import asyncio
import sys
from typing import Optional

from backend.src.services.rag_service import retrieve_relevant_context
from backend.src.services.supabase_service import (
    get_chat_by_id,
    insert_document,
    insert_new_chat_history,
    supabase,
    update_chat_history,
)
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

ai_router = APIRouter(prefix="/api", tags=["AI  Chat"])


class ChatBody(BaseModel):
    message: str = Field(
        ..., min_length=1, description="The user message cannot be empty"
    )
    chat_id: Optional[int] = Field(
        None, description="The chat ID to continue the conversation"
    )


try:
    ai_client = genai.Client()
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize Gemini Client in blueprint: {e}")
    ai_client = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(errors.APIError),
    reraise=True,
)
async def call_gemini_with_retry_content(client, history):
    return await client.aio.models.generate_content(
        model="gemini-2.5-flash", contents=history
    )


async def call_gemini_with_retry_content_stream(client, history):
    return await client.aio.models.generate_content_stream(
        model="gemini-2.5-flash", contents=history
    )


@ai_router.post("/chat/stream")
async def chat_stream(body: ChatBody):
    if not ai_client:
        raise HTTPException(status_code=503, detail="AI Service unavailable")
    user_message = body.message
    chat_id = body.chat_id
    chat_history = []
    current_chat_id = None

    if chat_id is not None:
        db_response = await asyncio.to_thread(get_chat_by_id, chat_id)
        if db_response and db_response.data and len(db_response.data) > 0:
            db_record = db_response.data[0]
            chat_history = db_record.get("history", [])
            current_chat_id = chat_id
        else:
            raise HTTPException(status_code=404, detail="Chat ID not found")

    context = await asyncio.to_thread(retrieve_relevant_context, user_message)
    if context:
        enhanced_message = (
            f"[INSTRUCTION]\n"
            f"You are a helpful assistant. Prioritize the ongoing conversation history for personal questions (like the user's name, greetings, or past interactions). "
            f"Use the provided [CONTEXT] below ONLY to answer specific questions about company rules, documents, or technical guidelines. "
            f"If the user asks about something not in the context AND not in the history, state that it wasn't found in the documents.\n\n"
            f"[CONTEXT]\n{context}\n\n"
            f"[USER QUESTION]\n{user_message}"
        )
    else:
        enhanced_message = user_message

    contents = []
    for msg in chat_history:
        role = msg.get("role")
        if role == "assistant":
            role = "model"

        raw_parts = msg.get("parts", [])

        text_content = ""
        if raw_parts:
            first_part = raw_parts[0]
            if isinstance(first_part, dict):
                text_content = first_part.get("text", "")
            else:
                text_content = str(first_part)

        if text_content:
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=text_content)],
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=enhanced_message)],
        )
    )
    chat_history.append({"role": "user", "parts": [user_message]})

    if current_chat_id is None:
        insert_response = await asyncio.to_thread(insert_new_chat_history, chat_history)
        if insert_response and insert_response.data:
            current_chat_id = insert_response.data[0]["id"]
        else:
            raise HTTPException(status_code=500, detail="Database insert failed")

    async def event_generator():
        full_response = ""
        try:
            response_stream = await call_gemini_with_retry_content_stream(
                ai_client, contents
            )

            async for chunk in response_stream:
                if chunk.text:
                    text_chunk = chunk.text
                    full_response += text_chunk
                    yield f"data: {text_chunk}\n\n"

        except Exception as stream_err:
            sys.stdout.write(f"❌ Error during streaming: {stream_err}")
            sys.stdout.flush()
            yield "data: [An error occurred while streaming response]\n\n"

        finally:
            if full_response:
                chat_history.append({"role": "model", "parts": [full_response]})
                await asyncio.to_thread(
                    update_chat_history, current_chat_id, chat_history
                )
                sys.stdout.write("✅ DB updated successfully!\n")
                sys.stdout.flush()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Chat-ID": str(current_chat_id),
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@ai_router.get("/chat/{chat_id}/history")
async def get_chat_history(chat_id: int):
    try:
        db_response = await asyncio.to_thread(
            lambda: (
                supabase.table("chats").select("history").eq("id", chat_id).execute()
            )
        )
        if db_response.data and len(db_response.data) > 0:
            raw_history = db_response.data[0].get("history", [])

            formatted_messages = [
                {
                    "sender": "user" if msg["role"] == "user" else "ai",
                    "text": msg["parts"][0]
                    if isinstance(msg["parts"], list)
                    else msg["parts"],
                }
                for msg in raw_history
            ]

            return {"status": "success", "messages": formatted_messages}
        else:
            raise HTTPException(status_code=404, detail="Chat not found")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch history: {str(e)}"
        )


class KnowledgeBody(BaseModel):
    content: str = Field(
        ..., min_length=10, description="The text content of the knowledge base"
    )
    category: Optional[str] = "General"


@ai_router.post("/knowledge/add")
async def add_knowledge(body: KnowledgeBody):
    success = await asyncio.to_thread(
        insert_document, content=body.content, metadata={"category": body.category}
    )
    if success:
        return {
            "status": "success",
            "message": "Knowledge successfully vectorized and stored.",
        }
    raise HTTPException(status_code=500, detail="Internal server error during storage")
